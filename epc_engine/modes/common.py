"""Shared P2 run helpers: write/fail paths, audit stub, list resolution."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from ..audit import write_audit
from ..paths import portable
from ..constraints import ConstraintEval, apply_constraints, evaluate_gates
from ..construct_types import ConstructResult
from ..job import Job, read_list_file
from ..source import SourceDB
from ..write_db import write_b_db


def _remove_output_db(path: Path) -> None:
    path = Path(path)
    if path.is_file():
        path.unlink()
        print(f"[epc] removed prior/stale B.db → {path}")


def resolve_pvt_list(spec: Any, source: SourceDB, base: Path) -> list[str]:
    if spec is None or spec == "all_from_source":
        return list(source.pvts)
    if isinstance(spec, str):
        p = portable(spec)
        if not p.is_absolute():
            p = (base / p).resolve()
        if p.is_file():
            return read_list_file(p)
        raise ValueError(f"pvt_list path not found: {p}")
    if isinstance(spec, list):
        return list(spec)
    raise ValueError(f"bad pvt_list: {spec!r}")


def resolve_instance_list(spec: Any, source: SourceDB, base: Path) -> list[str]:
    if spec is None or spec == "all_in_source" or spec == "all_from_source":
        return list(source.instances)
    if isinstance(spec, str):
        p = portable(spec)
        if not p.is_absolute():
            p = (base / p).resolve()
        if p.is_file():
            return read_list_file(p)
        raise ValueError(f"instance list path not found: {p}")
    if isinstance(spec, list):
        return list(spec)
    raise ValueError(f"bad instances: {spec!r}")


def resolve_field_keys(policy: str, source: SourceDB) -> list[str]:
    if policy == "all_from_source":
        return list(source.field_keys)
    raise ValueError(f"unsupported field_policy.keys: {policy}")


def finish_job(
    job: Job,
    source: SourceDB,
    instances: list[str],
    pvts: list[str],
    result: ConstructResult,
    *,
    h_ok: bool,
    h_msg: str,
    extra_audit_lines: list[str] | None = None,
) -> int:
    """Apply optional constraints, H gates, write or fail_job."""
    evals: list[ConstraintEval] = []
    if job.constraints:
        print("[epc] applying constraints…")
        evals = apply_constraints(job, source, result)
        n_fail = sum(1 for e in evals if not e.passed)
        print(
            f"[epc] constraint evals: PASS={sum(1 for e in evals if e.passed)} "
            f"FAIL={n_fail}"
        )
    gates_ok, gates_msg = evaluate_gates(job, evals)
    if job.constraints:
        print(f"[epc] constraint gates: {'PASS' if gates_ok else 'FAIL'} — {gates_msg}")
    else:
        gates_ok, gates_msg = True, "no constraints"

    all_ok = bool(h_ok and gates_ok)
    combined = f"{h_msg} | {gates_msg}"

    fail_job = (not all_ok) and job.on_violation == "fail_job"
    if fail_job or not all_ok:
        _remove_output_db(job.output_db)
        write_audit(
            job.audit_path,
            job,
            source,
            instances,
            pvts,
            result,
            evals,
            0,
            False,
            combined,
            g2_ok=True,
            g2_msg="G2 n/a (P2 mode)",
            g2_results=[],
        )
        if extra_audit_lines:
            _append_audit(job.audit_path, extra_audit_lines)
        print(f"[epc] audit (FAIL) → {job.audit_path}")
        print(f"[epc] FAIL: {combined}", file=sys.stderr)
        return 1

    print(f"[epc] writing B.db → {job.output_db}")
    n = write_b_db(job.output_db, result, instances, pvts)
    print(f"[epc] wrote {n} rows")
    write_audit(
        job.audit_path,
        job,
        source,
        instances,
        pvts,
        result,
        evals,
        n,
        True,
        combined,
        g2_ok=True,
        g2_msg="G2 n/a (P2 mode)",
        g2_results=[],
    )
    if extra_audit_lines:
        _append_audit(job.audit_path, extra_audit_lines)
    print(f"[epc] audit → {job.audit_path}")
    print("[epc] OK")
    return 0


def _append_audit(path: Path, lines: list[str]) -> None:
    path = Path(path)
    with path.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write("\n".join(lines))
        f.write("\n")
