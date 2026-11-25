"""Shared pytest fixtures: engine subprocess runner + tmp YAML materializer.

Design: every job runs as `python -m epc_engine <yaml>` (the same entry the
GUI/CLI use), with the YAML copied into a per-test tmp dir and its
output db/audit paths redirected there. Source/model paths stay as shipped
(legacy /workspace forms are rebased by epc_engine.paths.portable), so tests
read the real A_ref fixtures but never write into the repo tree.
"""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "epc_fixtures"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@dataclass
class MaterializedJob:
    yaml: Path
    db: Path
    audit: Path


def run_engine(yaml_path: Path, timeout: int = 1200):
    """Run `python -m epc_engine <yaml>` from repo root; return CompletedProcess."""
    return subprocess.run(
        [sys.executable, "-m", "epc_engine", str(yaml_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=ENV,
    )


def db_count(db_path: Path) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        return conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]


def db_distinct_keys(db_path: Path) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        return conn.execute("SELECT COUNT(DISTINCT field_key) FROM char_data").fetchone()[0]


def make_tmp_job(src_yaml: Path, tmp_path: Path) -> MaterializedJob:
    """Copy a fixture YAML into tmp, redirecting output db/audit to tmp."""
    data = yaml.safe_load(src_yaml.read_text(encoding="utf-8"))
    out = data["output"]
    out_db = tmp_path / Path(str(out["db_path"])).name
    out_audit = tmp_path / Path(str(out["audit_report_path"])).name
    out["db_path"] = str(out_db)
    out["audit_report_path"] = str(out_audit)
    job = tmp_path / src_yaml.name
    job.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return MaterializedJob(yaml=job, db=out_db, audit=out_audit)


def load_list(path: Path) -> list[str]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO
