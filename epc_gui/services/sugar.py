"""Sugar expand + dry-run via engine load_job only (no construct / no B.db)."""
from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from epc_engine.job import Job, load_job


@dataclass
class SugarRow:
    instance: str
    pvt: str
    key: str
    delta_pct: float | None
    sugar_origin: str | None
    key_family: str | None = None


@dataclass
class SugarExpandResult:
    ok: bool
    error: str = ""
    expanded_constraint_count: int = 0
    sugar_declared: bool = False
    mode: str = ""
    backend: str = ""
    constraint_count: int = 0
    relative_rows: list[SugarRow] | None = None
    job: Job | None = None


def _flatten_relative(job: Job) -> list[SugarRow]:
    rows: list[SugarRow] = []
    for c in job.constraints:
        if c.type != "relative_delta_vs_source":
            continue
        tgt = c.target or {}
        delta = tgt.get("delta_pct")
        try:
            delta_f = float(delta) if delta is not None else None
        except (TypeError, ValueError):
            delta_f = None
        for inst in c.instances:
            for pvt in c.pvts:
                for key in c.keys:
                    rows.append(
                        SugarRow(
                            instance=str(inst),
                            pvt=str(pvt),
                            key=str(key),
                            delta_pct=delta_f,
                            sugar_origin=c.sugar_origin,
                            key_family=c.key_family,
                        )
                    )
    return rows


def expand_from_path(path: str | Path) -> SugarExpandResult:
    """Call engine load_job; never invent expand rules."""
    try:
        job = load_job(path)
    except Exception as e:
        return SugarExpandResult(ok=False, error=f"{type(e).__name__}: {e}")
    rows = _flatten_relative(job)
    return SugarExpandResult(
        ok=True,
        expanded_constraint_count=int(job.expanded_constraint_count),
        sugar_declared=bool(job.sugar_declared),
        mode=str(job.mode),
        backend=str(job.construct.backend),
        constraint_count=len(job.constraints),
        relative_rows=rows,
        job=job,
    )


def expand_from_yaml_text(text: str, *, hint_name: str = "gui_dry_run.yaml") -> SugarExpandResult:
    """Write temp YAML then load_job (engine path API)."""
    with tempfile.TemporaryDirectory(prefix="epc_gui_dry_") as td:
        p = Path(td) / hint_name
        p.write_text(text, encoding="utf-8")
        return expand_from_path(p)


def dry_run_precheck(
    yaml_text: str | None = None,
    path: str | Path | None = None,
) -> SugarExpandResult:
    """P1-A dry-run: load_job only — no construct, no write_b_db."""
    if path is not None and yaml_text is None:
        return expand_from_path(path)
    if yaml_text is None:
        return SugarExpandResult(ok=False, error="no yaml provided")
    return expand_from_yaml_text(yaml_text)
