"""DB-layer tests: db_meta provenance table, user_version, index hygiene."""
from __future__ import annotations

import re
import sqlite3

from conftest import FIXTURES, make_tmp_job, run_engine
from epc_engine.write_db import read_db_meta, sha16


def test_sample_job_embeds_db_meta(tmp_path):
    job = make_tmp_job(FIXTURES / "epc_job.sample.yaml", tmp_path)
    proc = run_engine(job.yaml)
    assert proc.returncode == 0, (proc.stdout + proc.stderr)[-3000:]
    assert job.db.exists()

    conn = sqlite3.connect(str(job.db))
    try:
        uv = conn.execute("PRAGMA user_version").fetchone()[0]
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        n = conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]
        idx_names = {r[1] for r in conn.execute(
            "PRAGMA index_list(char_data)").fetchall()}
    finally:
        conn.close()

    assert uv == 1
    assert "db_meta" in tables
    assert n == 4950
    # PK leftmost prefix covers instance lookups: no redundant idx_inst
    assert "idx_inst" not in idx_names
    assert "idx_pvt" in idx_names
    assert "idx_key" in idx_names

    meta = read_db_meta(job.db)
    assert meta["backend"] == "residual_gbdt"
    assert meta["fallback_used"] == "false"
    assert meta["rows_written"] == "4950"
    assert meta["b_instances"] == "9"
    assert meta["b_pvts"] == "11"
    assert meta["gates"] == "PASS"
    assert meta["ab_hard"] == "PASS"
    assert meta["g2"] == "PASS"
    assert meta["finalized"] == "true"
    assert meta["yaml_sha16"] == sha16(job.yaml)
    assert re.fullmatch(r"[0-9a-f]{16}", meta["source_sha16"])
    assert meta["source_sha16"] != meta["yaml_sha16"]
    assert re.fullmatch(r"[0-9a-f]{16}", meta["model_sha16"])


def test_read_db_meta_missing_table_is_empty(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "bare.db"))
    conn.execute("CREATE TABLE char_data(x TEXT)")
    conn.commit()
    conn.close()
    assert read_db_meta(tmp_path / "bare.db") == {}
