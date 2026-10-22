"""Dual-new LON hold-out (leave-one-(instance,pvt) / leave-pair).

Protocol id: lon_v0
- Fold (I_h, P_h): train removes all instance=I_h rows AND all pvt=P_h cols
- Evaluate ONLY cross points (I_h, P_h, *) on core keys
- Never merge LOI/LOP cells into LON p95
- Compare: p95_selected ≤ p95_idw_nn (equality OK)
- No stamp this round; decoupled from AB-hard stamp and Op-Geom corner hold-out
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .backends.idw_nn import lookup_or_idw, optional_pvt_scale
from .construct_types import AXIS_KEYS
from .parse import parse_instance, parse_pvt
from .source import SourceDB, load_source_db
from .train_lib import (
    CORE_KEYS,
    EPS,
    LOI_INSTANCES,
    LOP_PVTS,
    RANDOM_SEED,
    ErrAgg,
    _rel_err,
    build_xy_geom,
    fit_models,
    nearest_pvt_excluding,
    predict_residual_tokens,
    sha16,
)
from .values import parse_tokens

SHANGHAI = ZoneInfo("Asia/Shanghai")
PROTOCOL_ID = "lon_v0"
GATE_LON = "LON-hard"


def _finite(x: float) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _delta(sel: float, idw: float) -> float:
    if not (_finite(sel) and _finite(idw)):
        return float("nan")
    return float(sel) - float(idw)


def evaluate_lon_hard_gates(
    p95_selected: float,
    p95_idw: float,
) -> tuple[bool, dict[str, bool], dict[str, Any]]:
    """LON-hard: p95_sel ≤ p95_idw (equality OK)."""
    ok = (
        _finite(p95_selected)
        and _finite(p95_idw)
        and float(p95_selected) <= float(p95_idw)
    )
    gates = {GATE_LON: ok}
    detail = {
        "protocol": PROTOCOL_ID,
        "p95_selected": p95_selected,
        "p95_idw_nn": p95_idw,
        "delta": _delta(p95_selected, p95_idw),
        "pass": ok,
        "compare": "<=",
        "note": "LON-hard uses ≤ (unify with AB-hard / H3-hard). No stamp.",
    }
    return ok, gates, detail


def _prior_leave_pair(
    source: SourceDB,
    inst: str,
    held_pvt: str,
    key: str,
    held_instances: set[str],
    held_pvts: set[str],
) -> tuple[list[float], Any]:
    """Dual-new prior: geom IDW excluding held instances @ NN among remaining pvts + scale.

    Returns (prior_tokens, nn_pp) for residual feature ΔV/ΔT.
    """
    b_pp = (
        source.pvt_parts[held_pvt]
        if held_pvt in source.pvt_parts
        else parse_pvt(held_pvt)
    )
    nn_name = nearest_pvt_excluding(held_pvt, source, held_pvts)
    nn_pp = source.pvt_parts[nn_name]
    ip = parse_instance(inst)
    val = lookup_or_idw(
        source, inst, ip, nn_name, key, exclude_instances=held_instances
    )
    val = optional_pvt_scale(source, val, key, b_pp, nn_name)
    return parse_tokens(val), nn_pp


def eval_lon_fold(
    source: SourceDB,
    *,
    held_inst: str,
    held_pvt: str,
    keys: list[str],
    seed: int = RANDOM_SEED,
) -> tuple[ErrAgg, ErrAgg, dict[str, ErrAgg], dict[str, ErrAgg], dict[str, Any]]:
    """One leave-pair fold. Test cells are ONLY (held_inst, held_pvt, key).

    Train: exclude all rows instance=held_inst and all cols pvt=held_pvt.
    Selected path mirrors online residual_reason=both → geom head + dual-new prior.
    """
    held_instances = {held_inst}
    held_pvts = {held_pvt}
    remaining_pvts = set(source.pvts) - held_pvts
    remaining_insts = [i for i in source.instances if i not in held_instances]

    # Protocol purity metadata (for U1)
    purity = {
        "held_inst": held_inst,
        "held_pvt": held_pvt,
        "train_n_instances": len(remaining_insts),
        "train_n_pvts": len(remaining_pvts),
        "train_has_held_inst": held_inst in remaining_insts,
        "train_has_held_pvt": held_pvt in remaining_pvts,
        "test_locators": [],  # filled below
    }

    xy = build_xy_geom(
        source,
        keys,
        exclude_instances=held_instances,
        pvt_filter=remaining_pvts,
    )
    models = fit_models(xy, seed=seed, head="geom")

    base_agg, res_agg = ErrAgg(), ErrAgg()
    base_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    res_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}

    if not source.has_group(held_inst, held_pvt):
        purity["test_locators"] = []
        return base_agg, res_agg, base_by, res_by, purity

    for key in keys:
        true_toks = parse_tokens(source.get(held_inst, held_pvt, key))  # type: ignore[arg-type]
        prior_toks, nn_pp = _prior_leave_pair(
            source,
            held_inst,
            held_pvt,
            key,
            held_instances,
            held_pvts,
        )
        for t, p in zip(true_toks, prior_toks):
            e = _rel_err(p, t)
            base_agg.add(e)
            base_by[key].add(e)

        model = models.get(key)
        if model is None:
            hat_toks = prior_toks
        else:
            hat_toks = predict_residual_tokens(
                model,
                source,
                held_inst,
                held_pvt,
                key,
                prior_toks,
                nn_pp=nn_pp,
            )
        for t, h in zip(true_toks, hat_toks):
            e = _rel_err(h, t)
            res_agg.add(e)
            res_by[key].add(e)
        purity["test_locators"].append((held_inst, held_pvt, key))

    return base_agg, res_agg, base_by, res_by, purity


def lon_fold_list(
    source: SourceDB,
    *,
    instances: list[str] | None = None,
    pvts: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Full cartesian LOI_INSTANCES × LOP_PVTS (default 30), filtered to A_ref."""
    insts = [i for i in (instances or LOI_INSTANCES) if i in source.instances]
    ps = [p for p in (pvts or LOP_PVTS) if p in source.pvts]
    return [(i, p) for i in insts for p in ps]


def run_lon_holdout(
    source: SourceDB,
    keys: list[str] | None = None,
    seed: int = RANDOM_SEED,
    folds: list[tuple[str, str]] | None = None,
) -> dict:
    keys = list(keys or CORE_KEYS)
    keys = [k for k in keys if k in source.field_keys and k not in AXIS_KEYS]
    fold_list = folds if folds is not None else lon_fold_list(source)

    lon_base, lon_res = ErrAgg(), ErrAgg()
    lon_base_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    lon_res_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    fold_summaries: list[dict[str, Any]] = []
    purity_samples: list[dict[str, Any]] = []

    for idx, (inst, pvt) in enumerate(fold_list):
        b, r, bb, rb, purity = eval_lon_fold(
            source,
            held_inst=inst,
            held_pvt=pvt,
            keys=keys,
            seed=seed,
        )
        lon_base.extend(b)
        lon_res.extend(r)
        for k in keys:
            lon_base_by[k].extend(bb[k])
            lon_res_by[k].extend(rb[k])
        bs, rs = b.summary(), r.summary()
        fold_summaries.append(
            {
                "inst": inst,
                "pvt": pvt,
                "n": rs["n"],
                "p95_idw": bs["p95"],
                "p95_sel": rs["p95"],
            }
        )
        if idx == 0:
            purity_samples.append(purity)

    lb, lr = lon_base.summary(), lon_res.summary()
    ok, gates, detail = evaluate_lon_hard_gates(float(lr["p95"]), float(lb["p95"]))

    return {
        "protocol": PROTOCOL_ID,
        "keys": keys,
        "folds": fold_list,
        "n_folds": len(fold_list),
        "lon_baseline": lb,
        "lon_residual": lr,
        "lon_by_key": {
            k: {
                "baseline": lon_base_by[k].summary(),
                "residual": lon_res_by[k].summary(),
            }
            for k in keys
        },
        "fold_summaries": fold_summaries,
        "gates": gates,
        "lon_hard_ok": ok,
        "lon_hard_detail": detail,
        "purity_sample": purity_samples[0] if purity_samples else None,
        "eps": EPS,
        "seed": seed,
        "apply_on": "all_extrapolated",
        "heads": "models_geom (both → geom head; mirrors online residual_reason=both)",
        "backend": "residual_gbdt",
        "prior": "idw_nn",
        "note_excluded": (
            "LOI-state cells I_h×(pvt≠P_h) and LOP-state (instance≠I_h)×P_h "
            "are NOT counted in LON p95."
        ),
    }


def write_lon_report(
    report: dict,
    path: Path,
    *,
    model_path: Path | None = None,
    main_report_link: str | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(tz=SHANGHAI).strftime("%Y-%m-%d %H:%M:%S %Z")
    lb, lr = report["lon_baseline"], report["lon_residual"]
    gates = report.get("gates") or {}
    lon_ok = gates.get(GATE_LON, report.get("lon_hard_ok", False))
    d = float(lr["p95"]) - float(lb["p95"])
    backend = report.get("backend", "residual_gbdt")

    def gmark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = [
        "# EPC Dual-new / LON Hold-out Report — residual_gbdt vs idw_nn",
        "",
        f"- Generated: **{now}** (Asia/Shanghai)",
        f"- Protocol: **LON** (`{PROTOCOL_ID}`) — leave-one-(instance,pvt) / leave-pair",
        f"- Folds: **{report['n_folds']}** (= LOI_INSTANCES × LOP_PVTS cartesian)",
        f"- Core keys: `{', '.join(report['keys'])}`",
        f"- ε = `{report['eps']}`; random_seed = `{report['seed']}`",
        f"- Relative error: `|hat-true|/max(|true|,ε)` at cell level",
        f"- **apply_on**: `{report.get('apply_on')}` ({report.get('heads')})",
        f"- **DEMO synthetic only** — not foundry/PDK calibration",
        f"- **No LON stamp** this round (decoupled from AB-hard stamp / Op-Geom H3)",
        "",
        "> **Policy:** train removes row `I_h` and column `P_h`; evaluate **only** "
        "cross points `(I_h, P_h, *)`. LOI/LOP cells must not be merged into LON p95.",
        "",
    ]
    if main_report_link:
        lines.append(
            f"- Sibling LOI/LOP report: [`algo_holdout_report.md`]({main_report_link})"
        )
    if model_path and Path(model_path).is_file():
        lines.append(
            f"- Production model: `{model_path}` (sha256[:16]={sha16(Path(model_path))})"
        )

    lines += [
        "",
        "## Acceptance gate (LON-hard)",
        "",
        "| ID | Criterion | p95_selected | p95_idw_nn | delta | n_cells | n_folds | backend | protocol | Result |",
        "|---|---|---|---|---|---|---|---|---|---|",
        f"| **{GATE_LON}** | p95_sel ≤ p95_idw | "
        f"{lr['p95']:.6g} | {lb['p95']:.6g} | {d:.6g} | {lr['n']} | "
        f"{report['n_folds']} | `{backend}` | `{PROTOCOL_ID}` | "
        f"**{gmark(bool(lon_ok))}** |",
        "",
        f"**LON-hard: {'PASS' if lon_ok else 'FAIL'}** (compare `≤`; equality OK)",
        "",
        "## Summary",
        "",
        "| Protocol | baseline idw_nn p95 | residual_gbdt p95 | p50_idw | p50_sel | max_idw | max_sel | n | ≤ idw? |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| **LON** (`{PROTOCOL_ID}`) | {lb['p95']:.6g} | {lr['p95']:.6g} | "
        f"{lb['p50']:.6g} | {lr['p50']:.6g} | {lb['max']:.6g} | {lr['max']:.6g} | "
        f"{lr['n']} | {'YES' if lr['p95'] <= lb['p95'] else 'NO'} |",
        "",
        f"- Note: {report.get('note_excluded', '')}",
        "",
        "### Fold list (I_h, P_h)",
        "",
    ]
    for inst, pvt in report["folds"]:
        lines.append(f"- `{inst}` × `{pvt}`")

    lines += [
        "",
        "## Per-key LON (p95)",
        "",
        "| key | baseline p95 | residual p95 | Δ |",
        "|---|---|---|---|",
    ]
    for k in report["keys"]:
        b = report["lon_by_key"][k]["baseline"]["p95"]
        r = report["lon_by_key"][k]["residual"]["p95"]
        lines.append(f"| `{k}` | {b:.6g} | {r:.6g} | {r - b:.6g} |")

    purity = report.get("purity_sample")
    if purity:
        lines += [
            "",
            "## Protocol purity (first fold sample)",
            "",
            f"- held: `{purity['held_inst']}` × `{purity['held_pvt']}`",
            f"- train_n_instances={purity['train_n_instances']} "
            f"(has_held_inst={purity['train_has_held_inst']})",
            f"- train_n_pvts={purity['train_n_pvts']} "
            f"(has_held_pvt={purity['train_has_held_pvt']})",
            f"- n_test_locators={len(purity.get('test_locators') or [])} "
            f"(expected = n_keys; all `(I_h,P_h,*)`)",
            "",
        ]

    lines += [
        "## Notes",
        "",
        "- Prior = IDW @ NN-pvt among remaining pvts + delay/power scale "
        "(dual-new; not LOI-only / LOP-only).",
        "- Selected = prior + geom-head residual (online `residual_reason=both`).",
        f"- Hard gate: **{GATE_LON}** (`p95_sel ≤ p95_idw`). Flag `--require-lon-hard` "
        "(default on) / `--no-require-lon-hard`.",
        "- **Not** Op-Geom corner / Miss / Sparse hold-out. **Not** AB stamp.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epc_engine.lon_holdout",
        description="Dual-new LON hold-out eval (leave-pair); no stamp",
    )
    p.add_argument(
        "--source-db",
        default="/workspace/epc_fixtures/A_ref.db",
    )
    p.add_argument(
        "--report-out",
        default="/workspace/epc_fixtures/algo_holdout_dual_new_report.md",
    )
    p.add_argument(
        "--model-path",
        default="/workspace/epc_engine/models/residual_gbdt.joblib",
        help="Optional; only for report sha line (LON does not write stamp)",
    )
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    p.add_argument(
        "--require-lon-hard",
        action="store_true",
        default=True,
        help="EXIT≠0 when LON-hard FAIL (default on)",
    )
    p.add_argument(
        "--no-require-lon-hard",
        action="store_false",
        dest="require_lon_hard",
        help="Allow EXIT 0 even if LON-hard FAIL (debug)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = load_source_db(Path(args.source_db))
    folds = lon_fold_list(source)
    print(
        f"[lon] A={source.path} instances={len(source.instances)} "
        f"pvts={len(source.pvts)} folds={len(folds)} protocol={PROTOCOL_ID}"
    )
    report = run_lon_holdout(source, seed=args.seed, folds=folds)
    report["source_path"] = str(source.path)
    lb, lr = report["lon_baseline"], report["lon_residual"]
    print(
        f"[lon] LON p95 baseline(idw)={lb['p95']:.6g} "
        f"selected={lr['p95']:.6g} n={lr['n']} "
        f"le_idw={lr['p95'] <= lb['p95']}"
    )
    ok = bool(report.get("lon_hard_ok"))
    print(f"[lon] gate {GATE_LON}={'PASS' if ok else 'FAIL'}")

    mp = Path(args.model_path) if args.model_path else None
    write_lon_report(
        report,
        Path(args.report_out),
        model_path=mp if mp and mp.is_file() else None,
        main_report_link="/workspace/epc_fixtures/algo_holdout_report.md",
    )
    print(f"[lon] report → {args.report_out}")

    if args.require_lon_hard and not ok:
        print(f"[lon] FAIL: {GATE_LON} — EXIT 3", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
