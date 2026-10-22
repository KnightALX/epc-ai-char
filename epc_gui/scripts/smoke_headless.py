#!/usr/bin/env python3
"""Headless GUI-P0 smoke: services + engine run + audit parse + T0 median_cell."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "/workspace")
os.environ.setdefault("PYTHONPATH", "/workspace")

from epc_gui.services.audit_parse import parse_audit
from epc_gui.services.job_runner import run_blocking
from epc_gui.services import trend as trend_svc
from epc_gui.services.yaml_io import load_yaml, FIXTURE_SHORTCUTS


def main() -> int:
    errors: list[str] = []
    print("=== GUI-P0 headless smoke ===")
    print(f"T0 typical rule: {trend_svc.TYPICAL_LABEL}")

    # median_cell unit
    n = 5
    # flat row-major; mid=(2,2) index 12
    toks = [float(i) for i in range(25)]
    toks[12] = 42.0
    val = " ".join(str(x) for x in toks)
    tv = trend_svc.typical_value(val, n)
    assert tv.kind == "median_cell" and tv.value == 42.0, tv
    assert tv.tran_i == 2 and tv.load_i == 2 and tv.cell_index == 12
    print(f"OK median_cell → {tv.value} @ ({tv.tran_i},{tv.load_i})")

    # sample green
    y = FIXTURE_SHORTCUTS["sample"]
    data = load_yaml(y)
    print(f"load YAML {y}: job={data.get('job_name')}")
    # Prefer existing sample db if present and COUNT matches; else run
    out_db = Path(data["output"]["db_path"])
    audit = Path(data["output"]["audit_report_path"])
    need_run = not out_db.is_file()
    if need_run:
        print("running sample job…")
        rr = run_blocking(y, timeout=300)
        print(f"EXIT={rr.exit_code}")
        if rr.exit_code != 0:
            errors.append(f"sample EXIT={rr.exit_code}")
            print(rr.stderr[-2000:])
    else:
        print(f"reuse existing {out_db}")

    if out_db.is_file():
        from epc_gui.services.db_reader import CharDb

        with CharDb(out_db) as db:
            cnt = db.count()
        print(f"COUNT={cnt}")
        if cnt != 4950:
            errors.append(f"COUNT={cnt} want 4950")
    else:
        errors.append("sample db missing after run")

    s = parse_audit(audit)
    print(f"audit overall={s.overall} gates_ok={s.gates_ok} parse_ok={s.parse_ok}")
    if s.overall != "PASS" or not s.parse_ok:
        errors.append(f"audit parse {s.overall}")

    # T0 series
    if out_db.is_file():
        series = trend_svc.build_series(
            out_db,
            key="tcq",
            pvts=["TT_0P80V_0P80V_25C", "SSGNP_0P99V_0P99V_125C"],
        )
        for ser in series:
            caps = [p.capacity for p in ser.points]
            print(f"T0 {ser.key}×{ser.pvt}: n={len(ser.points)} caps={caps[:5]}… kind={ser.typical_kind}")
            if len(ser.points) < 3:
                errors.append(f"need ≥3 capacity points for {ser.pvt}")
            if caps != sorted(caps):
                errors.append(f"capacity not ascending for {ser.pvt}")
            # SQL spot-check first point
            if ser.points:
                p0 = ser.points[0]
                with CharDb(out_db) as db:
                    raw = db.get_value(p0.instance, ser.pvt, ser.key)
                tv = trend_svc.typical_value(raw, 5)
                rel = trend_svc.max_rel_err(p0.value, tv.value)
                print(f"  spot {p0.instance} rel_err={rel:.3e}")
                if rel >= 1e-9:
                    errors.append(f"T0 rel_err {rel}")

    # red residual h3hard
    red = FIXTURE_SHORTCUTS["p2_geom_residual_h3hard_red"]
    print(f"red YAML {red}")
    rr = run_blocking(red, timeout=300)
    print(f"red EXIT={rr.exit_code}")
    red_data = load_yaml(red)
    red_db = Path(red_data["output"]["db_path"])
    red_audit = Path(red_data["output"]["audit_report_path"])
    if rr.exit_code == 0:
        errors.append("red expected non-zero EXIT")
    if red_db.is_file():
        errors.append(f"red should not write db but found {red_db}")
    else:
        print("red: 未落盘 OK")
    rs = parse_audit(red_audit)
    print(f"red audit overall={rs.overall} gates_ok={rs.gates_ok}")
    lights = {g.name: g.status for g in rs.gates}
    print(f"  lights={lights}")
    if rs.overall != "FAIL":
        errors.append(f"red audit overall={rs.overall}")
    if lights.get("H3-hard") != "FAIL":
        errors.append(f"H3-hard light={lights.get('H3-hard')}")

    if errors:
        print("FAIL:", errors)
        return 1
    print("ALL SMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
