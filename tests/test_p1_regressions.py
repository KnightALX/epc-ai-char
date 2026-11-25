"""P1 regression suite: every reviewer P1 fix must have a failing-before test.

Each test builds a per-test copy of a fixture YAML (repo tree stays read-only)
and asserts the fixed behavior. Expected exit codes follow cli.main:
ValueError/FileNotFoundError/KeyError -> 2; gate failures -> 1; sqlite/other
exceptions propagate (traceback -> 1).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from conftest import FIXTURES, db_count, load_list, make_tmp_job, run_engine

SAMPLE = FIXTURES / "epc_job.sample.yaml"
TRANSFER_RTL = FIXTURES / "transfer" / "epc_job.transfer_rtl.yaml"


def _copy_and_edit(src_yaml: Path, tmp_path: Path, mutate) -> Path:
    job = make_tmp_job(src_yaml, tmp_path)
    data = yaml.safe_load(job.yaml.read_text(encoding="utf-8"))
    mutate(data)
    job.yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return job.yaml


# ---- P1 ① empty locator must not silently skip a constraint ----------------


def test_p1_empty_instances_rejected(tmp_path: Path):
    y = _copy_and_edit(SAMPLE, tmp_path, lambda d: d["constraints"][0].__setitem__("instances", []))
    cp = run_engine(y)
    assert cp.returncode == 2
    assert "empty locator" in cp.stderr
    assert not Path(tmp_path / "B_out.sample.db").exists()


def test_p1_empty_keys_rejected(tmp_path: Path):
    y = _copy_and_edit(SAMPLE, tmp_path, lambda d: d["constraints"][0].__setitem__("keys", []))
    cp = run_engine(y)
    assert cp.returncode == 2
    assert "empty locator" in cp.stderr
    assert not Path(tmp_path / "B_out.sample.db").exists()


# ---- P1 ② value_range op whitelist ------------------------------------------


def test_p1_invalid_op_rejected(tmp_path: Path):
    def bad(d):
        d["constraints"][0]["target"]["op"] = "=="

    y = _copy_and_edit(SAMPLE, tmp_path, bad)
    cp = run_engine(y)
    assert cp.returncode == 2
    # table_upper_bound has its own pre-existing "only supports <=" guard;
    # the new whitelist guards the value_range path with "op=" message.
    assert ("only supports <=" in cp.stderr) or ("op=" in cp.stderr)
    assert not Path(tmp_path / "B_out.sample.db").exists()


# ---- P1 ③ on_violation must be an exact enum value --------------------------


@pytest.mark.parametrize("typo", ["Fail_Job", "fail job"])
def test_p1_on_violation_bad_value_rejected(tmp_path: Path, typo: str):
    def bad(d):
        d["gates"]["on_violation"] = typo

    y = _copy_and_edit(SAMPLE, tmp_path, bad)
    cp = run_engine(y)
    assert cp.returncode == 2
    assert "on_violation" in cp.stderr
    assert not Path(tmp_path / "B_out.sample.db").exists()


@pytest.mark.parametrize("padded", ["fail_job ", " fail_job", "fail_job\n"])
def test_p1_on_violation_whitespace_accepted(tmp_path: Path, padded: str):
    # strip() then validate: trailing/leading whitespace is tolerated, never
    # silently clipped into a soft-clip pass.
    def pad(d):
        d["gates"]["on_violation"] = padded

    job = make_tmp_job(SAMPLE, tmp_path)
    data = yaml.safe_load(job.yaml.read_text(encoding="utf-8"))
    pad(data)
    job.yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    cp = run_engine(job.yaml)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert job.db.is_file()
    assert db_count(job.db) == 4950


# ---- P1 ⑤ atomic write: a failed write leaves the previous B.db intact -----


def test_p1_atomic_write_preserves_old_db(tmp_path: Path):
    from epc_engine.construct_types import ConstructResult
    from epc_engine.write_db import write_b_db

    db = tmp_path / "B.db"
    good = ConstructResult(data={("I", "P", "K"): "1.0 1.0 1.0"}, field_keys=["K"])
    assert write_b_db(db, good, ["I"], ["P"]) == 1
    before = db.read_bytes()

    bad = ConstructResult(data={("I", "P", "K"): "1.0 nan 1.0"}, field_keys=["K"])
    with pytest.raises(ValueError, match="non-finite"):
        write_b_db(db, bad, ["I"], ["P"])

    # previous library byte-identical, no .tmp residue anywhere
    assert db.read_bytes() == before
    assert not Path(str(db) + ".tmp").exists()


# ---- P1 ④ a failed run must not leave a stale B.db that looks current ------


def test_p1_failed_run_removes_stale_db(tmp_path: Path):
    job = make_tmp_job(SAMPLE, tmp_path)
    cp = run_engine(job.yaml)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert job.db.is_file()

    # duplicate instance -> construct size mismatch -> exit 2 + stale db dropped
    dup_list = tmp_path / "dup_instances.txt"
    originals = load_list(FIXTURES / "B_instance_list.txt")
    dup_list.write_text("\n".join(originals + [originals[0]]) + "\n", encoding="utf-8")
    data = yaml.safe_load(job.yaml.read_text(encoding="utf-8"))
    data["target"]["instance_list_path"] = str(dup_list)
    job.yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    cp2 = run_engine(job.yaml)
    assert cp2.returncode == 2
    assert not job.db.exists()
    assert not Path(str(job.db) + ".tmp").exists()


# ---- P1 ⑥ G2 spot-check must honor constrained cells, not always cell 0 -----


def test_p1_g2_cell_subset_no_false_kill(tmp_path: Path):
    def subset(d):
        # relative constraint on tcq now covers only cells [1,2]; cell 0 is
        # unconstrained, so the old fixed toks[0] check used to mis-kill.
        d["constraints"][1]["table_cells"] = [1, 2]

    job = make_tmp_job(SAMPLE, tmp_path)
    data = yaml.safe_load(job.yaml.read_text(encoding="utf-8"))
    subset(data)
    job.yaml.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    cp = run_engine(job.yaml)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert job.db.is_file()
    assert db_count(job.db) == 4950
    audit = job.audit.read_text(encoding="utf-8")
    assert "G2 PASS" in audit
    assert "**PASS**" in audit


# ---- P1 ⑦ transfer must raise on unpredicted non-axis cells -----------------


def test_p1_transfer_missing_raises(tmp_path: Path, monkeypatch):
    from epc_engine.job import load_job
    from epc_engine.modes import transfer_ab
    from epc_engine.source import load_source_db

    job_yaml = make_tmp_job(TRANSFER_RTL, tmp_path).yaml
    job = load_job(str(job_yaml))
    src = load_source_db(job.source_db)
    from epc_engine.construct_types import AXIS_KEYS

    non_axis = next(k for k in src.field_keys if k not in AXIS_KEYS)

    monkeypatch.setattr(transfer_ab, "predict_group_value", lambda *a, **k: None)
    with pytest.raises(ValueError, match="could not predict"):
        transfer_ab.construct_transfer(
            job, b_instances=["NO_SUCH_INST"], b_pvts=["NO_SUCH_PVT"],
            field_keys=[non_axis],
        )
