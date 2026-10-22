#!/usr/bin/env python3
"""P2 H3 DEMO accuracy reports (geom / miss / sparse) with H3-hard columns."""
from __future__ import annotations

import math
import sqlite3
from pathlib import Path

from epc_engine.backends import idw_nn, residual_gbdt
from epc_engine.job import ConstructConfig
from epc_engine.modes.gates_h import p95, relative_err
from epc_engine.modes.h3_hard import check_h3_hard
from epc_engine.modes.source_util import subset_source
from epc_engine.source import load_source_db
from epc_engine.train_lib import CORE_KEYS
from epc_engine.values import parse_tokens

ROOT = Path("/workspace/epc_fixtures/p2")
A_REF = Path("/workspace/epc_fixtures/A_ref.db")
MODEL = Path("/workspace/epc_engine/models/residual_gbdt.joblib")

CORNERS = [
    "HINP3TCAM64X8SWISDC",
    "HINP3TCAM64X100SWISDC",
    "HINP3TCAM512X8SWISDC",
    "HINP3TCAM512X100SWISDC",
]
HOLD_INST = "HINP3TCAM256X32SWISDC"
PVT8 = [l.strip() for l in (ROOT / "pvt8.txt").read_text().splitlines() if l.strip()]


def cell_rels(pred: str, truth: str) -> list[float]:
    pt = parse_tokens(pred)
    tt = parse_tokens(truth)
    if len(pt) != len(tt):
        return [1.0]
    return [relative_err(a, b) for a, b in zip(pt, tt)]


def h3_geom() -> dict:
    """Geom certified on idw_nn (green default); residual reported as h3_hard_residual."""
    source = load_source_db(A_REF)
    seed_src = subset_source(source, instances=CORNERS)
    keys = list(CORE_KEYS)
    cfg_res = ConstructConfig(
        backend="residual_gbdt",
        model_path=MODEL,
        prior="idw_nn",
        fallback="idw_nn",
        apply_on="all_extrapolated",
    )
    r_idw = idw_nn.construct(seed_src, [HOLD_INST], PVT8, keys)
    r_res = residual_gbdt.construct(seed_src, [HOLD_INST], PVT8, keys, cfg_res)

    errs_idw: list[float] = []
    errs_res: list[float] = []
    for pvt in PVT8:
        for key in keys:
            truth = source.get(HOLD_INST, pvt, key)
            if truth is None:
                continue
            errs_idw.extend(cell_rels(r_idw.data[(HOLD_INST, pvt, key)], truth))
            errs_res.extend(cell_rels(r_res.data[(HOLD_INST, pvt, key)], truth))
    p95_idw = p95(errs_idw)
    p95_res = p95(errs_res)
    delta = (
        (p95_res - p95_idw)
        if (not math.isnan(p95_res) and not math.isnan(p95_idw))
        else float("nan")
    )

    # Certified path = idw_nn (green default). H3-base + hard skip for idw.
    backend_certified = "idw_nn"
    ok_base = (not math.isnan(p95_idw)) and (p95_idw < 0.2)
    # §2.2 ok formula with certified backend = idw_nn:
    # ok = finite(p95_idw) ∧ (p95_idw < 0.2) ∧ (backend==idw ∨ selected≤idw)
    ok = ok_base and True  # certified idw → hard clause trivial

    _, _, hard_res = check_h3_hard(
        backend="residual_gbdt",
        p95_selected=p95_res,
        p95_idw=p95_idw,
        protocol_id=f"geom_4corner_holdout:{HOLD_INST}",
    )
    return {
        "operator": "corner_fill_geom",
        "backend_certified": backend_certified,
        "p95_selected": p95_idw,  # certified selected = idw
        "p95_idw_nn": p95_idw,
        "p95_residual": p95_res,
        "delta": 0.0,
        "delta_residual": delta,
        "h3_hard": "SKIP",
        "h3_hard_residual": hard_res.get("h3_hard"),
        "n_err": len(errs_idw),
        "ok": ok,
        "detail": f"holdout={HOLD_INST} pvts={len(PVT8)} keys={len(keys)}",
    }


def h3_miss() -> dict:
    # Use punched list + filled out_missing.db
    punch_path = ROOT / "A_missing_punched.db.punched.txt"
    out_db = ROOT / "out_missing.db"
    lines = [l for l in punch_path.read_text().splitlines() if l.strip()]
    punched = []
    for l in lines:
        parts = l.split("\t")
        if len(parts) >= 4:
            punched.append((parts[0], parts[1], parts[2], parts[3]))
    conn = sqlite3.connect(str(out_db))
    errs = []
    try:
        for inst, pvt, key, truth in punched:
            row = conn.execute(
                "SELECT value FROM char_data WHERE instance=? AND pvt=? AND field_key=?",
                (inst, pvt, key),
            ).fetchone()
            if row is None:
                errs.append(1.0)
                continue
            errs.extend(cell_rels(row[0], truth))
    finally:
        conn.close()
    p95_v = p95(errs)
    ok = p95_v < 0.15
    return {
        "operator": "pvt_missing_fill",
        "backend_certified": "idw_nn",
        "p95_selected": p95_v,
        "p95_idw_nn": p95_v,
        "p95_holes": p95_v,
        "delta": 0.0,
        "h3_hard": "SKIP",
        "n_holes": len(punched),
        "n_err": len(errs),
        "ok": ok,
        "threshold": 0.15,
    }


def h3_sparse() -> dict:
    """Leave-one-pvt on A_sparse instance: hide 1 seed pvt, refill, compare to idw/residual."""
    sparse = load_source_db(ROOT / "A_sparse.db")
    full = load_source_db(A_REF)
    inst = HOLD_INST
    seed_pvts = [p for p in sparse.pvts if sparse.has_group(inst, p)]
    assert len(seed_pvts) >= 3
    hold_pvt = seed_pvts[0]
    keys = list(CORE_KEYS)
    from epc_engine.modes.h3_hard import drop_instance_pvt

    src2 = drop_instance_pvt(sparse, inst, hold_pvt)
    cfg_res = ConstructConfig(
        backend="residual_gbdt",
        model_path=MODEL,
        prior="idw_nn",
        fallback="idw_nn",
        apply_on="all_extrapolated",
    )
    r_idw = idw_nn.construct(src2, [inst], [hold_pvt], keys)
    r_res = residual_gbdt.construct(src2, [inst], [hold_pvt], keys, cfg_res)
    errs_idw, errs_res = [], []
    for key in keys:
        truth = full.get(inst, hold_pvt, key) or sparse.get(inst, hold_pvt, key)
        if truth is None:
            continue
        errs_idw.extend(cell_rels(r_idw.data[(inst, hold_pvt, key)], truth))
        errs_res.extend(cell_rels(r_res.data[(inst, hold_pvt, key)], truth))
    p95_idw = p95(errs_idw)
    p95_res = p95(errs_res)
    delta = (
        (p95_res - p95_idw)
        if (not math.isnan(p95_res) and not math.isnan(p95_idw))
        else float("nan")
    )
    # Sparse green uses residual → H3-hard applies: selected ≤ idw
    ok_hard, _, hard_audit = check_h3_hard(
        backend="residual_gbdt",
        p95_selected=p95_res,
        p95_idw=p95_idw,
        protocol_id=f"sparse_lop:{inst}:{hold_pvt}",
    )
    ok = ok_hard
    return {
        "operator": "pvt_sparse_fill",
        "backend_certified": "residual_gbdt",
        "hold_pvt": hold_pvt,
        "p95_selected": p95_res,
        "p95_idw_nn": p95_idw,
        "p95_residual": p95_res,
        "delta": delta,
        "h3_hard": hard_audit.get("h3_hard"),
        "n_err": len(errs_res),
        "ok": ok,
    }


def write_report(path: Path, results: list[dict]) -> None:
    lines = [
        "# P2 H3 DEMO accuracy report",
        "",
        "Synthetic fixtures only — not foundry/PDK truth.",
        "",
        "H3-hard: when backend ≠ idw_nn, require `p95_selected ≤ p95_idw_nn` (equality allowed).",
        "Geom certified on idw_nn; residual hard status reported separately as `h3_hard_residual`.",
        "",
        "| operator | ok | p95_selected | p95_idw_nn | delta | h3_hard | extra |",
        "|---|---|---|---|---|---|---|",
    ]
    all_ok = True
    for r in results:
        ok = r.get("ok", False)
        all_ok = all_ok and ok
        extra_bits = []
        for k in (
            "h3_hard_residual",
            "p95_residual",
            "delta_residual",
            "p95_holes",
            "hold_pvt",
            "n_err",
            "n_holes",
            "threshold",
            "detail",
            "backend_certified",
        ):
            if k in r and k not in (
                "operator",
                "ok",
                "p95_selected",
                "p95_idw_nn",
                "delta",
                "h3_hard",
            ):
                extra_bits.append(f"{k}={r[k]}")
        extra = ", ".join(extra_bits)
        lines.append(
            f"| `{r['operator']}` | **{'PASS' if ok else 'FAIL'}** | "
            f"{r.get('p95_selected')} | {r.get('p95_idw_nn')} | {r.get('delta')} | "
            f"`{r.get('h3_hard')}` | {extra} |"
        )
    lines += ["", f"**Overall H3: {'PASS' if all_ok else 'FAIL'}**", ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(path)
    for r in results:
        print(r)
    if not all_ok:
        raise SystemExit(1)


def main() -> None:
    results = [h3_geom(), h3_miss(), h3_sparse()]
    write_report(ROOT / "h3_report.md", results)
    # also per-operator stubs
    for r in results:
        (ROOT / f"h3_{r['operator']}_report.md").write_text(
            f"# H3 `{r['operator']}`\n\n`{r}`\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
