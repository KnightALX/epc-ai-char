"""Green-path end-to-end: every shipped green job exits 0 and writes the
expected row count into a tmp output db (source fixtures stay read-only)."""
from __future__ import annotations

import pytest

from conftest import (
    FIXTURES,
    db_count,
    db_distinct_keys,
    load_list,
    make_tmp_job,
    run_engine,
)


def _transfer_expected_rows() -> int:
    inst = load_list(FIXTURES / "transfer" / "B_instance_list.txt")
    pvt = load_list(FIXTURES / "transfer" / "B_pvt_list.txt")
    keys = db_distinct_keys(FIXTURES / "transfer" / "A_src.db")
    return len(inst) * len(pvt) * keys


GREEN_CASES = [
    ("sample", "epc_job.sample.yaml", 4950),
    ("p1_improve_green", "p1/epc_job.p1_improve_green.yaml", 4950),
    ("p1_improve_green_idw", "p1/epc_job.p1_improve_green_idw.yaml", 4950),
    ("ab_hard_green", "ab_hard/epc_job.ab_hard_green.yaml", 4950),
    ("ab_hard_idw", "ab_hard/epc_job.ab_hard_idw.yaml", 4950),
    ("p2_geom_green", "p2/job_corner_fill_green.yaml", 2000),
    ("p2_missing_green", "p2/job_missing_fill_green.yaml", 800),
    ("p2_sparse_green", "p2/job_sparse_fill_green.yaml", 800),
    ("transfer_rtl", "transfer/epc_job.transfer_rtl.yaml", None),
    ("transfer_tr", "transfer/epc_job.transfer_tr.yaml", None),
]


@pytest.mark.parametrize(
    "name, rel, expected",
    [(n, r, e if e is not None else _transfer_expected_rows())
     for n, r, e in GREEN_CASES],
    ids=[c[0] for c in GREEN_CASES],
)
def test_green_job(name, rel, expected, tmp_path):
    job = make_tmp_job(FIXTURES / rel, tmp_path)
    proc = run_engine(job.yaml)
    assert proc.returncode == 0, f"{name} stderr tail:\n{proc.stderr[-2000:]}"
    assert job.db.is_file(), f"{name}: B.db missing at {job.db}"
    assert db_count(job.db) == expected, f"{name}: COUNT != {expected}"
    assert job.audit.is_file(), f"{name}: audit missing at {job.audit}"


def test_sample_audit_content(tmp_path):
    job = make_tmp_job(FIXTURES / "epc_job.sample.yaml", tmp_path)
    proc = run_engine(job.yaml)
    assert proc.returncode == 0, proc.stderr[-2000:]
    text = job.audit.read_text(encoding="utf-8")
    assert "**PASS**" in text
    assert "G2 PASS" in text
    assert "| rows written | **4950** |" in text
    assert "baseline_source" in text  # G1 auditability section present


def test_ab_hard_green_audit_mark(tmp_path):
    job = make_tmp_job(FIXTURES / "ab_hard" / "epc_job.ab_hard_green.yaml", tmp_path)
    proc = run_engine(job.yaml)
    assert proc.returncode == 0, proc.stderr[-2000:]
    text = job.audit.read_text(encoding="utf-8")
    assert "ab_hard" in text and "PASS" in text


def test_ab_hard_idw_audit_skip(tmp_path):
    job = make_tmp_job(FIXTURES / "ab_hard" / "epc_job.ab_hard_idw.yaml", tmp_path)
    proc = run_engine(job.yaml)
    assert proc.returncode == 0, proc.stderr[-2000:]
    text = job.audit.read_text(encoding="utf-8")
    assert "ab_hard" in text and "SKIP" in text
