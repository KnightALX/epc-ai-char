"""Scale evaluation test: build a 10x synthetic source DB, run the engine end-to-end.

This is the "large-scale generation" gate the user asked for: 200 instances x
40 PVTs x 50 keys = 400,000 source rows -> 50 x 11 x 50 = 27,500 output rows.

Marked `slow`: the fixture build is O(400k) SQL inserts. Run the full suite
once for the acceptance evidence; iterate with `pytest -m "not slow"`.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ENV, FIXTURES, REPO, run_engine

pytestmark = pytest.mark.slow

SCALE_YAML = FIXTURES / "scale" / "epc_job.scale_10x.yaml"


def _rewrite_yaml(tmp_path: Path) -> Path:
    """Point the scale YAML's scale-local paths into tmp; keep /workspace
    entries for shipped B_pvt_list and the model so the portable() rebase
    path is exercised by this test."""
    text = SCALE_YAML.read_text(encoding="utf-8")
    subs = {
        "/workspace/epc_fixtures/scale/A_scale.db": str(
            tmp_path / "A_scale.db"
        ).replace("\\", "/"),
        "/workspace/epc_fixtures/scale/B_scale_instance_list.txt": str(
            tmp_path / "B_scale_instance_list.txt"
        ).replace("\\", "/"),
        "/workspace/epc_fixtures/scale/B_out_scale_10x.db": str(
            tmp_path / "B_out_scale_10x.db"
        ).replace("\\", "/"),
        "/workspace/epc_fixtures/scale/B_out_scale_10x_audit.md": str(
            tmp_path / "B_out_scale_10x_audit.md"
        ).replace("\\", "/"),
    }
    for old, new in subs.items():
        assert old in text, f"scale yaml no longer contains {old}"
        text = text.replace(old, new)
    job = tmp_path / "epc_job.scale_10x.yaml"
    job.write_text(text, encoding="utf-8")
    return job


def test_scale_10x_build_and_run(tmp_path):
    build = subprocess.run(
        [
            sys.executable,
            str(FIXTURES / "scale" / "build_scale_fixture.py"),
            "--instances",
            "200",
            "--out",
            str(tmp_path / "A_scale.db"),
            "--b-list",
            str(tmp_path / "B_scale_instance_list.txt"),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,
        env=ENV,
    )
    assert build.returncode == 0, (build.stdout + build.stderr)[-2000:]

    with sqlite3.connect(str(tmp_path / "A_scale.db")) as conn:
        n_src = conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]
    assert n_src == 400_000

    job = _rewrite_yaml(tmp_path)
    proc = run_engine(job, timeout=1800)
    assert proc.returncode == 0, (proc.stdout + proc.stderr)[-3000:]

    b_db = tmp_path / "B_out_scale_10x.db"
    assert b_db.exists()
    with sqlite3.connect(str(b_db)) as conn:
        n_b = conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]
        uv = conn.execute("PRAGMA user_version").fetchone()[0]
        meta = dict(
            conn.execute("SELECT key, value FROM db_meta").fetchall()
        )
    assert n_b == 27_500  # 50 instances x 11 PVTs x 50 keys
    assert uv == 1
    assert meta["rows_written"] == "27500"
    assert meta["b_instances"] == "50"

    audit = (tmp_path / "B_out_scale_10x_audit.md").read_text(encoding="utf-8")
    assert "G2 PASS" in audit
    assert "**PASS**" in audit
