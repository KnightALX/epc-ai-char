"""CLI entry for EPC engine (P1 G2 spot-check included)."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from .ab_hard import check_ab_hard_online
from .audit import write_audit
from .constraints import apply_constraints, evaluate_gates
from .construct import construct_b
from .job import load_job, load_target_lists
from .source import load_source_db
from .values import parse_tokens
from .write_db import write_b_db


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epc_engine",
        description="EPC: construct B.db from A.db + YAML job (modes: epc_ab|corner_fill_geom|pvt_missing_fill|pvt_sparse_fill)",
    )
    p.add_argument(
        "--mode",
        default=None,
        help="Override YAML mode/operator (epc_ab|corner_fill_geom|pvt_missing_fill|pvt_sparse_fill)",
    )
    p.add_argument(
        "job_yaml",
        nargs="?",
        default="/workspace/epc_fixtures/epc_job.sample.yaml",
        help="Path to EPC job YAML (default: sample fixture)",
    )
    return p


def _remove_output_db(path: Path) -> None:
    """Delete a leftover / prior B.db so FAIL cannot leave a usable library."""
    path = Path(path)
    if path.is_file():
        path.unlink()
        print(f"[epc] removed prior/stale B.db → {path}")


def _pick_g2_samples(evals) -> list[dict]:
    """Pick ≥1 speed + ≥1 power sugar cell when available; else any relative."""
    speed = None
    power = None
    any_rel = None
    for e in evals:
        if e.type != "relative_delta_vs_source" or not e.passed or not e.applied:
            continue
        m = e.metrics or {}
        if "instance" not in m or "key" not in m:
            continue
        sample = {
            "instance": m["instance"],
            "pvt": m["pvt"],
            "key": m["key"],
            "delta_pct": float(m["delta_pct"]),
            "baseline0": float(m["baseline0"]),
            "factor": float(m["factor"]),
            "baseline_source": m.get("baseline_source"),
            "key_family": m.get("key_family"),
            "locator": e.locator,
        }
        if any_rel is None:
            any_rel = sample
        fam = m.get("key_family")
        if fam == "speed" and speed is None:
            speed = sample
        elif fam == "power" and power is None:
            power = sample
        if speed and power:
            break
    out = []
    if speed:
        out.append(speed)
    if power:
        out.append(power)
    if not out and any_rel:
        out.append(any_rel)
    return out


def g2_spot_check(db_path: Path, samples: list[dict]) -> tuple[bool, str, list[dict]]:
    """Re-read B.db; verify |B0/baseline0 − (1+δ/100)| < 1e-6."""
    if not samples:
        return True, "G2 SKIP: no relative samples to check", []
    if not Path(db_path).is_file():
        return False, "G2 FAIL: B.db missing for spot-check", []
    conn = sqlite3.connect(str(db_path))
    results = []
    try:
        for s in samples:
            row = conn.execute(
                "SELECT value FROM char_data WHERE instance=? AND pvt=? AND field_key=?",
                (s["instance"], s["pvt"], s["key"]),
            ).fetchone()
            if row is None:
                results.append({**s, "ok": False, "detail": "row missing in B.db"})
                continue
            toks = parse_tokens(row[0])
            got0 = toks[0]
            base0 = s["baseline0"]
            factor = s["factor"]
            if abs(base0) < 1e-15:
                rel = abs(got0 - base0 * factor)
            else:
                rel = abs(got0 / base0 - factor)
            ok = rel < 1e-6
            results.append(
                {
                    **s,
                    "ok": ok,
                    "b0": got0,
                    "rel_err_vs_factor": rel,
                    "detail": (
                        f"B0={got0:.8g} baseline0={base0:.8g} "
                        f"factor={factor:.6f} |B/base-factor|={rel:.3e}"
                    ),
                }
            )
    finally:
        conn.close()
    failed = [r for r in results if not r.get("ok")]
    if failed:
        msg = "G2 FAIL: " + "; ".join(r["detail"] for r in failed)
        return False, msg, results
    msg = "G2 PASS: " + "; ".join(r["detail"] for r in results)
    return True, msg, results


def run_epc_ab(job) -> int:
    print(f"[epc] mode=epc_ab job={job.job_name} yaml={job.path}")
    print(f"[epc] source={job.source_db}")
    if job.sugar_declared:
        print(f"[epc] G3 expanded_constraint_count={job.expanded_constraint_count}")
    cfg = job.construct
    print(
        f"[epc] construct.backend={cfg.backend} prior={cfg.prior} "
        f"apply_on={cfg.apply_on} model={cfg.model_path}"
    )

    source = load_source_db(job.source_db)
    print(
        f"[epc] A loaded: instances={len(source.instances)} "
        f"pvts={len(source.pvts)} keys={len(source.field_keys)} "
        f"rows={len(source.rows)}"
    )

    b_instances, b_pvts = load_target_lists(job)
    print(f"[epc] B lists: instances={len(b_instances)} pvts={len(b_pvts)}")

    if job.field_keys_policy == "all_from_source":
        field_keys = list(source.field_keys)
    else:
        raise ValueError(f"unsupported field_policy.keys: {job.field_keys_policy}")

    from .parse import parse_instance, parse_pvt

    for name in b_instances:
        parse_instance(name)
    for name in b_pvts:
        parse_pvt(name)

    print("[epc] constructing…")
    result = construct_b(source, b_instances, b_pvts, field_keys, cfg)
    print(
        f"[epc] backend_used={result.backend} fallback={result.fallback_used} "
        f"model_sha16={result.model_sha16}"
    )
    expected = len(b_instances) * len(b_pvts) * len(field_keys)
    if len(result.data) != expected:
        print(
            f"[epc] ERROR: constructed {len(result.data)} cells, expected {expected}",
            file=sys.stderr,
        )
        return 2

    # AB-hard (epc_ab): read-only stamp — no per-job LOI recompute.
    # Configured backend drives the gate; model-missing→idw fallback is SKIP.
    ab_ok, ab_msg, ab_audit = check_ab_hard_online(
        backend=cfg.backend,
        model_path=cfg.model_path,
        model_sha16=result.model_sha16,
        fallback_used=bool(result.fallback_used),
    )
    print(f"[epc] {ab_msg}")
    if not ab_ok:
        _remove_output_db(job.output_db)
        write_audit(
            job.audit_path,
            job,
            source,
            b_instances,
            b_pvts,
            result,
            [],
            0,
            False,
            ab_msg,
            g2_ok=False,
            g2_msg="G2 skipped (ab_hard FAIL, no B.db)",
            g2_results=[],
            ab_hard_audit=ab_audit,
        )
        print(f"[epc] audit (AB-hard FAIL) → {job.audit_path}")
        print(
            "[epc] FAIL: AB-hard stamp gate failed (on_violation=fail_job semantics)",
            file=sys.stderr,
        )
        return 1

    print("[epc] applying constraints (priority over style)…")
    evals = apply_constraints(job, source, result)
    for e in evals:
        mark = "PASS" if e.passed else "FAIL"
        # Keep stdout readable: only print FAIL + first few PASS for sugar floods
        if (not e.passed) or e.type != "relative_delta_vs_source" or e.index < 3:
            print(f"[epc]   [{mark}] #{e.index} {e.type}: {e.detail}")
    n_fail = sum(1 for e in evals if not e.passed)
    n_pass = sum(1 for e in evals if e.passed)
    print(f"[epc] constraint evals: PASS={n_pass} FAIL={n_fail} total={len(evals)}")

    gates_ok, gates_msg = evaluate_gates(job, evals)
    print(f"[epc] gates: {'PASS' if gates_ok else 'FAIL'} — {gates_msg}")

    g2_ok, g2_msg, g2_results = True, "G2 pending write", []
    fail_job = (not gates_ok) and job.on_violation == "fail_job"

    if fail_job:
        _remove_output_db(job.output_db)
        n = 0
        print("[epc] skipped write of B.db (gates FAIL, on_violation=fail_job)")
        write_audit(
            job.audit_path,
            job,
            source,
            b_instances,
            b_pvts,
            result,
            evals,
            n,
            gates_ok,
            gates_msg,
            g2_ok=False,
            g2_msg="G2 skipped (gates FAIL, no B.db)",
            g2_results=[],
            ab_hard_audit=ab_audit,
        )
        print(f"[epc] audit (FAIL) → {job.audit_path}")
        print(
            "[epc] FAIL: constraint gate failed (on_violation=fail_job)",
            file=sys.stderr,
        )
        return 1

    print(f"[epc] writing B.db → {job.output_db}")
    n = write_b_db(job.output_db, result, b_instances, b_pvts)
    print(f"[epc] wrote {n} rows")

    # G2: spot-check rewrite against baselines
    samples = _pick_g2_samples(evals)
    g2_ok, g2_msg, g2_results = g2_spot_check(job.output_db, samples)
    print(f"[epc] {g2_msg}")
    if not g2_ok:
        _remove_output_db(job.output_db)
        write_audit(
            job.audit_path,
            job,
            source,
            b_instances,
            b_pvts,
            result,
            evals,
            0,
            False,
            gates_msg + " | " + g2_msg,
            g2_ok=False,
            g2_msg=g2_msg,
            g2_results=g2_results,
            ab_hard_audit=ab_audit,
        )
        print(f"[epc] audit (G2 FAIL) → {job.audit_path}")
        print("[epc] FAIL: G2 spot-check failed; B.db removed", file=sys.stderr)
        return 1

    write_audit(
        job.audit_path,
        job,
        source,
        b_instances,
        b_pvts,
        result,
        evals,
        n,
        gates_ok and g2_ok,
        gates_msg + " | " + g2_msg,
        g2_ok=g2_ok,
        g2_msg=g2_msg,
        g2_results=g2_results,
        ab_hard_audit=ab_audit,
    )
    print(f"[epc] audit → {job.audit_path}")

    if n != expected:
        print(f"[epc] FAIL: row count {n} != {expected}", file=sys.stderr)
        _remove_output_db(job.output_db)
        return 2
    print("[epc] OK")
    return 0


def run(job_yaml: str | Path, mode_override: str | None = None) -> int:
    job = load_job(job_yaml, mode_override=mode_override)
    print(f"[epc] job={job.job_name} mode={job.mode} yaml={job.path}")
    if job.mode != "epc_ab":
        from .modes import run_mode

        return run_mode(job)
    return run_epc_ab(job)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args.job_yaml, mode_override=args.mode)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        print(f"[epc] ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[epc] ERROR: {exc}", file=sys.stderr)
        raise
