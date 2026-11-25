"""Red-path end-to-end: shipped red jobs fail with the right exit code and
leave no B.db behind. AB-hard red is exercised against a tmp model copy with
a tampered (or missing) sidecar so the repo stamp is never mutated."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from conftest import FIXTURES, MaterializedJob, REPO, make_tmp_job, run_engine

RED_CASES = [
    ("p1_r1_vague", "p1/epc_job.p1_r1_vague.yaml", 2),
    ("p1_r2_proxy_forbid", "p1/epc_job.p1_r2_proxy_forbid.yaml", 1),
    ("p2_geom_red", "p2/job_corner_fill_red.yaml", 2),
    ("p2_missing_red", "p2/job_missing_fill_red.yaml", 2),
    ("p2_sparse_red", "p2/job_sparse_fill_red.yaml", 2),
    ("p2_geom_residual_h3hard", "p2/job_corner_fill_residual_h3hard.yaml", 1),
]


@pytest.mark.parametrize(
    "name, rel, exit_code",
    [(n, r, e) for n, r, e in RED_CASES],
    ids=[c[0] for c in RED_CASES],
)
def test_red_job(name, rel, exit_code, tmp_path):
    job = make_tmp_job(FIXTURES / rel, tmp_path)
    proc = run_engine(job.yaml)
    assert proc.returncode == exit_code, (
        f"{name}: exit={proc.returncode} want={exit_code}\n"
        f"stdout tail:\n{proc.stdout[-800:]}\nstderr tail:\n{proc.stderr[-800:]}"
    )
    assert not job.db.exists(), f"{name}: B.db must not exist after FAIL"


def test_red_upper_bound_regression(tmp_path):
    """run_red_upper_bound.sh contract: table_upper_bound 1500→1000 must FAIL,
    no B.db, stderr carries the gate fail marker."""
    data = yaml.safe_load(
        (FIXTURES / "epc_job.sample.yaml").read_text(encoding="utf-8")
    )
    assert data["constraints"][0]["type"] == "table_upper_bound"
    data["constraints"][0]["target"]["value"] = 1000
    out = data["output"]
    db = tmp_path / Path(str(out["db_path"])).name
    audit = tmp_path / Path(str(out["audit_report_path"])).name
    out["db_path"] = str(db)
    out["audit_report_path"] = str(audit)
    job_yaml = tmp_path / "epc_job_red_upper_bound.yaml"
    job_yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    proc = run_engine(job_yaml)
    assert proc.returncode == 1, proc.stderr[-2000:]  # gates FAIL → cli run_epc_ab returns 1
    assert not db.exists(), "B.db must not exist after constraint gate FAIL"
    assert "FAIL: constraint gate failed" in proc.stderr
    assert audit.is_file()
    assert "FAIL" in audit.read_text(encoding="utf-8")


def test_h3hard_red_audit_marks(tmp_path):
    job = make_tmp_job(
        FIXTURES / "p2" / "job_corner_fill_residual_h3hard.yaml", tmp_path
    )
    proc = run_engine(job.yaml)
    assert proc.returncode == 1, proc.stderr[-2000:]
    text = job.audit.read_text(encoding="utf-8")
    assert "h3_hard" in text and "FAIL" in text
    assert "p95_selected" in text


def _job_with_model_redirect(rel: str, tmp_path: Path, sidecar_text: str | None):
    """Materialize a job whose construct.model_path points at a tmp copy of
    the shipped model, optionally with a sidecar written (None = no sidecar)."""
    src_yaml = FIXTURES / rel
    data = yaml.safe_load(src_yaml.read_text(encoding="utf-8"))
    out = data["output"]
    db = tmp_path / Path(str(out["db_path"])).name
    audit = tmp_path / Path(str(out["audit_report_path"])).name
    out["db_path"] = str(db)
    out["audit_report_path"] = str(audit)

    src_model = REPO / "epc_engine" / "models" / "residual_gbdt.joblib"
    dst = tmp_path / "residual_gbdt.joblib"
    shutil.copyfile(src_model, dst)
    if sidecar_text is not None:
        (tmp_path / "residual_gbdt.joblib.ab_hard.json").write_text(
            sidecar_text, encoding="utf-8"
        )

    def walk(d):
        if isinstance(d, dict):
            for k, v in list(d.items()):
                if k == "model_path":
                    d[k] = str(dst)
                else:
                    walk(v)

    walk(data.get("construct") or {})
    job_yaml = tmp_path / src_yaml.name
    job_yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return MaterializedJob(yaml=job_yaml, db=db, audit=audit)


def test_ab_hard_red_poisoned_stamp(tmp_path):
    from epc_engine.train_lib import sha16

    src_model = REPO / "epc_engine" / "models" / "residual_gbdt.joblib"
    dst = tmp_path / "residual_gbdt.joblib"
    shutil.copyfile(src_model, dst)
    st = json.loads(
        (REPO / "epc_engine" / "models" / "residual_gbdt.joblib.ab_hard.json").read_text()
    )
    st["ab_hard"] = "FAIL"
    st["p95_selected_loi"] = 0.99
    st["p95_idw_loi"] = 0.10
    st["model_sha16"] = sha16(dst)
    st["stamp_sha16"] = st["model_sha16"]
    sidecar = json.dumps(st, indent=2) + "\n"

    job = _job_with_model_redirect("ab_hard/epc_job.ab_hard_red.yaml", tmp_path, sidecar)
    proc = run_engine(job.yaml)
    assert proc.returncode != 0, proc.stderr[-2000:]
    assert not job.db.exists(), "B.db must not exist after AB-hard FAIL"
    text = job.audit.read_text(encoding="utf-8")
    assert "ab_hard" in text and "FAIL" in text


def test_ab_hard_red_missing_stamp(tmp_path):
    job = _job_with_model_redirect(
        "ab_hard/epc_job.ab_hard_red.yaml", tmp_path, sidecar_text=None
    )
    proc = run_engine(job.yaml)
    assert proc.returncode != 0, proc.stderr[-2000:]
    assert not job.db.exists(), "B.db must not exist after missing-stamp FAIL"
    text = job.audit.read_text(encoding="utf-8")
    assert ("missing_stamp" in text) or ("FAIL" in text and "ab_hard" in text)
