"""Offline Transfer hold-out: linear_tr vs residual_tl on pseudo dual-process.

Protocol id: transfer_holdout_v0
- Seed from A_tgt_seed only (never hold-out truth for training/r)
- Eval on A_tgt_full \\ seed groups; core 8 keys; cell relative error
- Gate: p95_RTL ≤ p95_TR (equality OK)
- No stamp; decoupled from AB/LON/H3
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .construct_types import AXIS_KEYS
from .parse import parse_pvt
from .paths import repo_root
from .source import SourceDB, load_source_db
from .train_lib import CORE_KEYS, EPS, RANDOM_SEED, ErrAgg, _rel_err
from .transfer_lib import (
    GATE_TRANSFER,
    PROTOCOL_ID,
    WARP_ID_DEFAULT,
    estimate_transfer_ratios,
    evaluate_transfer_hard_gates,
    fit_transfer_models,
    build_xy_transfer,
    prior_tr_tokens,
    predict_rtl_tokens,
    train_transfer_bundle,
)
from .values import parse_tokens

SHANGHAI = ZoneInfo("Asia/Shanghai")


def _seed_group_set(seed: SourceDB) -> set[tuple[str, str]]:
    return set(seed.groups.keys())


def run_transfer_holdout(
    src: SourceDB,
    seed: SourceDB,
    tgt_full: SourceDB,
    keys: list[str] | None = None,
    *,
    rng_seed: int = RANDOM_SEED,
    low_v_thr: float = 0.75,
) -> dict[str, Any]:
    keys = list(keys or CORE_KEYS)
    keys = [k for k in keys if k in src.field_keys and k not in AXIS_KEYS]
    seed_set = _seed_group_set(seed)

    # Ratios + RTL models from seed ONLY
    ratios = estimate_transfer_ratios(src, seed, keys)
    xy = build_xy_transfer(src, seed, keys, ratios)
    models = fit_transfer_models(xy, seed=rng_seed)

    tr_agg, rtl_agg = ErrAgg(), ErrAgg()
    tr_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    rtl_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    # low-V stratified
    tr_low, rtl_low = ErrAgg(), ErrAgg()

    n_eval_groups = 0
    n_seed_skipped = 0
    leaked_seed = 0

    for (inst, pvt), g in tgt_full.groups.items():
        if (inst, pvt) in seed_set:
            n_seed_skipped += 1
            continue
        if not src.has_group(inst, pvt):
            continue
        n_eval_groups += 1
        pp = tgt_full.pvt_parts.get(pvt) or parse_pvt(pvt)
        is_low = float(pp.vdd) < low_v_thr
        for key in keys:
            true_s = g.get(key)
            if true_s is None:
                continue
            # Guard: must not use seed truth — already skipped seed groups
            if (inst, pvt) in seed_set:
                leaked_seed += 1
                continue
            true_toks = parse_tokens(true_s)
            prior = prior_tr_tokens(src, inst, pvt, key, ratios)
            if prior is None or len(prior) != len(true_toks):
                continue
            for t, p in zip(true_toks, prior):
                e = _rel_err(p, t)
                tr_agg.add(e)
                tr_by[key].add(e)
                if is_low:
                    tr_low.add(e)
            model = models.get(key)
            hat = predict_rtl_tokens(model, src, inst, pvt, key, prior)
            for t, h in zip(true_toks, hat):
                e = _rel_err(h, t)
                rtl_agg.add(e)
                rtl_by[key].add(e)
                if is_low:
                    rtl_low.add(e)

    tr_s, rtl_s = tr_agg.summary(), rtl_agg.summary()
    ok, gates, detail = evaluate_transfer_hard_gates(
        float(rtl_s["p95"]), float(tr_s["p95"])
    )
    return {
        "protocol": PROTOCOL_ID,
        "keys": keys,
        "ratios": ratios,
        "n_seed_groups": len(seed_set),
        "n_eval_groups": n_eval_groups,
        "n_seed_skipped": n_seed_skipped,
        "leaked_seed_guard": leaked_seed,
        "tr": tr_s,
        "rtl": rtl_s,
        "tr_by_key": {k: tr_by[k].summary() for k in keys},
        "rtl_by_key": {k: rtl_by[k].summary() for k in keys},
        "tr_low_v": tr_low.summary(),
        "rtl_low_v": rtl_low.summary(),
        "low_v_thr": low_v_thr,
        "gates": gates,
        "transfer_hard_ok": ok,
        "transfer_hard_detail": detail,
        "eps": EPS,
        "seed": rng_seed,
        "n_models": len(models),
        "backend_rtl": "residual_tl",
        "backend_tr": "linear_tr",
        "ratio_policy": "global_per_key_median_on_seed",
    }


def write_transfer_report(
    report: dict,
    path: Path,
    *,
    warp_id: str = WARP_ID_DEFAULT,
    src_path: str | None = None,
    seed_path: str | None = None,
    tgt_path: str | None = None,
    reproduce_cmd: str | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(tz=SHANGHAI).strftime("%Y-%m-%d %H:%M:%S %Z")
    tr, rtl = report["tr"], report["rtl"]
    gates = report.get("gates") or {}
    ok = gates.get(GATE_TRANSFER, report.get("transfer_hard_ok", False))
    d = float(rtl["p95"]) - float(tr["p95"])

    def gmark(v: bool) -> str:
        return "PASS" if v else "FAIL"

    lines = [
        "# EPC Transfer Hold-out Report — residual_tl vs linear_tr",
        "",
        f"- Generated: **{now}** (Asia/Shanghai)",
        f"- Protocol: **Transfer** (`{PROTOCOL_ID}`)",
        f"- Warp id: **`{warp_id}`** (pseudo dual-process; ≠ true PDK)",
        f"- Seed groups: **{report['n_seed_groups']}**; eval (non-seed) groups: **{report['n_eval_groups']}**",
        f"- Core keys: `{', '.join(report['keys'])}`",
        f"- ε = `{report['eps']}`; random_seed = `{report['seed']}`",
        f"- Ratio policy: `{report.get('ratio_policy')}` (seed only — hold-out truth never used for r)",
        f"- Relative error: `|hat-true|/max(|true|,ε)` at cell level",
        f"- **No transfer stamp** this round (decoupled from AB-hard / LON / H3)",
        f"- **DEMO synthetic only** — not foundry calibration",
        "",
    ]
    if src_path:
        lines.append(f"- A_src: `{src_path}`")
    if seed_path:
        lines.append(f"- A_tgt_seed: `{seed_path}`")
    if tgt_path:
        lines.append(f"- A_tgt_full (eval only): `{tgt_path}`")
    if reproduce_cmd:
        lines.append(f"- Reproduce: `{reproduce_cmd}`")

    lines += [
        "",
        "## Acceptance gate (TRANSFER-hard)",
        "",
        "| ID | Criterion | p95_RTL | p95_TR | delta | n_cells | n_eval_groups | protocol | Result |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| **{GATE_TRANSFER}** | p95_RTL ≤ p95_TR | "
        f"{rtl['p95']:.6g} | {tr['p95']:.6g} | {d:.6g} | {rtl['n']} | "
        f"{report['n_eval_groups']} | `{PROTOCOL_ID}` | **{gmark(bool(ok))}** |",
        "",
        f"**TRANSFER-hard: {'PASS' if ok else 'FAIL'}** (compare `≤`; equality OK)",
        "",
        "## Summary",
        "",
        "| Method | p95 | p50 | max | n | ≤ TR? |",
        "|---|---|---|---|---|---|",
        f"| **linear_tr** | {tr['p95']:.6g} | {tr['p50']:.6g} | {tr['max']:.6g} | {tr['n']} | — |",
        f"| **residual_tl** | {rtl['p95']:.6g} | {rtl['p50']:.6g} | {rtl['max']:.6g} | {rtl['n']} | "
        f"{'YES' if rtl['p95'] <= tr['p95'] else 'NO'} |",
        "",
        "### Low-V stratified (Should)",
        "",
        f"- Threshold: VDD < `{report['low_v_thr']}`",
        f"- linear_tr p95_lowV = `{report['tr_low_v']['p95']:.6g}` (n={report['tr_low_v']['n']})",
        f"- residual_tl p95_lowV = `{report['rtl_low_v']['p95']:.6g}` (n={report['rtl_low_v']['n']})",
        "",
        "## Per-key p95",
        "",
        "| key | linear_tr p95 | residual_tl p95 | Δ | r (seed median) |",
        "|---|---|---|---|---|",
    ]
    for k in report["keys"]:
        b = report["tr_by_key"][k]["p95"]
        r = report["rtl_by_key"][k]["p95"]
        ratio = report["ratios"].get(k, float("nan"))
        lines.append(
            f"| `{k}` | {b:.6g} | {r:.6g} | {r - b:.6g} | {ratio:.6g} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- Prior = linear Transfer Ratio on aligned src locator; residual = GBDT(x, prior_tr).",
        "- Features: log2(d/w), PVT, cell axes, prior_tr (tran/load axes never shuffled).",
        f"- Hard gate: **{GATE_TRANSFER}** (`p95_RTL ≤ p95_TR`). "
        "Flag `--require-transfer-hard` / `--no-require-transfer-hard` (default off).",
        "- **Not** same-process LOI/LOP/LON evidence. **Not** AB stamp / Op-Geom H3.",
        f"- leaked_seed_guard={report.get('leaked_seed_guard', 0)} (must be 0)",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epc_engine.transfer_holdout",
        description="Transfer hold-out eval (linear_tr vs residual_tl); no stamp",
    )
    p.add_argument(
        "--src-db",
        default=str(repo_root() / "epc_fixtures" / "transfer" / "A_src.db"),
    )
    p.add_argument(
        "--seed-db",
        default=str(repo_root() / "epc_fixtures" / "transfer" / "A_tgt_seed.db"),
    )
    p.add_argument(
        "--tgt-full-db",
        default=str(repo_root() / "epc_fixtures" / "transfer" / "A_tgt_full.db"),
    )
    p.add_argument(
        "--report-out",
        default=str(repo_root() / "epc_fixtures" / "transfer" / "transfer_holdout_report.md"),
    )
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    p.add_argument(
        "--warp-id",
        default=WARP_ID_DEFAULT,
    )
    p.add_argument(
        "--require-transfer-hard",
        action="store_true",
        default=False,
        help="EXIT≠0 when TRANSFER-hard FAIL (default off; Should)",
    )
    p.add_argument(
        "--no-require-transfer-hard",
        action="store_false",
        dest="require_transfer_hard",
        help="Allow EXIT 0 even if TRANSFER-hard FAIL (default)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    src = load_source_db(Path(args.src_db))
    seed = load_source_db(Path(args.seed_db))
    tgt = load_source_db(Path(args.tgt_full_db))
    print(
        f"[transfer] src={src.path} seed_groups={len(seed.groups)} "
        f"tgt_groups={len(tgt.groups)} protocol={PROTOCOL_ID}"
    )
    # Integrity: seed must be subset of tgt_full locators
    seed_set = set(seed.groups.keys())
    tgt_set = set(tgt.groups.keys())
    if not seed_set.issubset(tgt_set):
        print("[transfer] ERROR: seed not subset of tgt_full", file=sys.stderr)
        return 2

    report = run_transfer_holdout(src, seed, tgt, rng_seed=args.seed)
    tr, rtl = report["tr"], report["rtl"]
    print(
        f"[transfer] p95 linear_tr={tr['p95']:.6g} residual_tl={rtl['p95']:.6g} "
        f"n={rtl['n']} le_tr={rtl['p95'] <= tr['p95']}"
    )
    ok = bool(report.get("transfer_hard_ok"))
    print(f"[transfer] gate {GATE_TRANSFER}={'PASS' if ok else 'FAIL'}")

    # warp meta if present
    warp_id = args.warp_id
    meta_path = Path(args.src_db).parent / "warp_meta.json"
    reproduce = None
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        warp_id = meta.get("warp_id", warp_id)
        reproduce = meta.get("reproduce")

    write_transfer_report(
        report,
        Path(args.report_out),
        warp_id=warp_id,
        src_path=str(src.path),
        seed_path=str(seed.path),
        tgt_path=str(tgt.path),
        reproduce_cmd=reproduce,
    )
    print(f"[transfer] report → {args.report_out}")

    if args.require_transfer_hard and not ok:
        print(f"[transfer] FAIL: {GATE_TRANSFER} — EXIT 3", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
