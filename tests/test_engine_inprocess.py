"""In-process engine runs: the same jobs as the subprocess suites, but through
epc_engine.cli.run() inside THIS process, so pytest-cov attributes engine
coverage (cli/source/backends/construct/constraints/write_db/audit) to the
report instead of losing it to subprocess isolation.
"""
from __future__ import annotations

import pytest
import yaml

from tests.conftest import FIXTURES, db_count, make_tmp_job

from epc_engine.cli import run


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_inprocess_sample_green(tmp_path):
    m = make_tmp_job(FIXTURES / "epc_job.sample.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert db_count(m.db) == 4950
    text = m.audit.read_text(encoding="utf-8")
    assert "G2 PASS" in text and "**PASS**" in text


def test_inprocess_p1_green_idw(tmp_path):
    m = make_tmp_job(FIXTURES / "p1" / "epc_job.p1_improve_green_idw.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert db_count(m.db) == 4950


def test_inprocess_ab_hard_green(tmp_path):
    m = make_tmp_job(FIXTURES / "ab_hard" / "epc_job.ab_hard_green.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert db_count(m.db) == 4950
    text = m.audit.read_text(encoding="utf-8")
    assert "**PASS**" in text and "**ab_hard**: `PASS`" in text and "loi_v0+lop_v0" in text


def test_inprocess_upper_bound_red(tmp_path):
    m = make_tmp_job(FIXTURES / "epc_job.sample.yaml", tmp_path)
    data = _load(m.yaml)
    data["constraints"][0]["target"]["value"] = 1000
    m.yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    rc = run(m.yaml)
    assert rc != 0
    assert not m.db.exists()


def test_inprocess_p2_red(tmp_path):
    m = make_tmp_job(FIXTURES / "p2" / "job_corner_fill_red.yaml", tmp_path)
    # In-process run() raises where CLI main() would convert to exit 2.
    with pytest.raises(ValueError, match="corner"):
        run(m.yaml)
    assert not m.db.exists()


def test_inprocess_corner_fill_green(tmp_path):
    m = make_tmp_job(FIXTURES / "p2" / "job_corner_fill_green.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert db_count(m.db) == 2000


def test_inprocess_missing_fill_green(tmp_path):
    m = make_tmp_job(FIXTURES / "p2" / "job_missing_fill_green.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert db_count(m.db) == 800


def test_inprocess_sparse_fill_green(tmp_path):
    m = make_tmp_job(FIXTURES / "p2" / "job_sparse_fill_green.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert db_count(m.db) == 800


def test_inprocess_h3hard_red(tmp_path):
    m = make_tmp_job(FIXTURES / "p2" / "job_corner_fill_residual_h3hard.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc != 0
    assert not m.db.exists()
    text = m.audit.read_text(encoding="utf-8")
    assert "H3-hard" in text and "FAIL" in text


def test_inprocess_transfer_rtl_green(tmp_path):
    m = make_tmp_job(FIXTURES / "transfer" / "epc_job.transfer_rtl.yaml", tmp_path)
    rc = run(m.yaml)
    assert rc == 0
    assert m.db.exists() and db_count(m.db) > 0
