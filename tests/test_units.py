"""Unit-level contract tests: gate logic, parser defaults, fixture honesty,
transfer decoupling, and the transfer hold-out subprocess green report."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ENV, FIXTURES, REPO

from epc_engine.ab_hard import (
    GATE_AB_LOI,
    GATE_AB_LOP,
    GATE_ALIAS_LOI,
    GATE_ALIAS_LOP,
    evaluate_ab_hard_gates,
)
from epc_engine.transfer_holdout import build_parser as transfer_build_parser
from epc_engine.transfer_lib import (
    GATE_TRANSFER,
    evaluate_transfer_hard_gates,
)


# ---------------------------------------------------------------- AB-hard gates
def test_ab_hard_equality_passes():
    ok, gates, detail = evaluate_ab_hard_gates(0.100, 0.100, 0.010, 0.010)
    assert ok
    assert gates[GATE_AB_LOI] and gates[GATE_AB_LOP]
    assert gates[GATE_ALIAS_LOI] == gates[GATE_AB_LOI]
    assert gates[GATE_ALIAS_LOP] == gates[GATE_AB_LOP]
    assert detail["protocol"] == "loi_v0+lop_v0"
    assert detail["compare"] == "<="


def test_ab_hard_selected_worse_fails():
    ok, gates, _ = evaluate_ab_hard_gates(0.20, 0.10, 0.02, 0.01)
    assert not ok
    assert gates[GATE_AB_LOI] is False
    assert gates[GATE_ALIAS_LOI] is False


def test_ab_hard_non_finite_fails():
    ok, _, _ = evaluate_ab_hard_gates(float("nan"), 0.1, 0.01, 0.01)
    assert not ok


# ------------------------------------------------------------- TRANSFER gates
def test_transfer_gate_equality_passes():
    ok, gates, detail = evaluate_transfer_hard_gates(0.1, 0.1)
    assert ok
    assert gates[GATE_TRANSFER]
    assert detail["compare"] == "<="
    assert detail["protocol"] == "transfer_holdout_v0"


def test_transfer_gate_rtl_worse_fails():
    ok, gates, _ = evaluate_transfer_hard_gates(0.2, 0.1)
    assert not ok
    assert gates[GATE_TRANSFER] is False


def test_transfer_gate_rtl_better_passes():
    ok, _, _ = evaluate_transfer_hard_gates(0.05, 0.1)
    assert ok


# ------------------------------------------------------------- parser defaults
def test_transfer_parser_default_require_hard_off():
    args = transfer_build_parser().parse_args([])
    assert args.require_transfer_hard is False


# ------------------------------------------------------------- fixture honesty
def _col(db: Path, key: str, limit: int) -> list[str]:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT value FROM char_data WHERE field_key=? ORDER BY rowid LIMIT ?",
            (key, limit),
        ).fetchall()
    finally:
        con.close()
    return [r[0] for r in rows]


def test_transfer_fixture_honesty_leakage_differs():
    src = _col(FIXTURES / "transfer" / "A_src.db", "leakage_vddc", 5)
    tgt = _col(FIXTURES / "transfer" / "A_tgt_full.db", "leakage_vddc", 5)
    assert len(src) == 5 and len(tgt) == 5, "leakage_vddc samples missing"
    assert src != tgt, "target domain must not leak source truth on leakage_vddc"


def test_transfer_fixture_axes_preserved():
    src = _col(FIXTURES / "transfer" / "A_src.db", "tran_index", 5)
    tgt = _col(FIXTURES / "transfer" / "A_tgt_full.db", "tran_index", 5)
    assert src == tgt, "tran_index axes must be preserved across domains"


def test_warp_meta_contract():
    wm = json.loads((FIXTURES / "transfer" / "warp_meta.json").read_text(encoding="utf-8"))
    assert wm["warp_id"] == "warp_nl_v0"
    assert wm["n_groups_seed"] == 120
    assert wm["forced_boundary_groups"] == 30


def test_seed_manifest_contract():
    sm = json.loads((FIXTURES / "transfer" / "seed_manifest.json").read_text(encoding="utf-8"))
    assert sm["n"] == 120
    assert len(sm["seed_groups"]) == 120
    assert len(sm["forced_boundary"]) == 30


# ------------------------------------------------------------- decoupling scan
FORBIDDEN = ["eval_h3", "h3_hard", "modes.h3", "write_ab_hard", "lon_hard"]


def _code_without_comments(path: Path) -> str:
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("#")
    ]
    return "\n".join(lines)


@pytest.mark.parametrize(
    "rel",
    [
        "epc_engine/transfer_lib.py",
        "epc_engine/transfer_holdout.py",
        "epc_engine/modes/transfer_ab.py",
    ],
)
def test_transfer_decoupled_from_other_protocols(rel):
    text = _code_without_comments(REPO / rel)
    for tok in FORBIDDEN:
        assert tok not in text, f"{rel} references forbidden token {tok!r}"


def test_no_transfer_hard_sidecar():
    assert not (REPO / "epc_engine" / "models" / "transfer_hard.json").exists()


# ------------------------------------------------------------- holdout subprocess
def test_transfer_holdout_subprocess_green(tmp_path):
    report = tmp_path / "transfer_holdout_report.md"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "epc_engine.transfer_holdout",
            "--src-db",
            str(FIXTURES / "transfer" / "A_src.db"),
            "--seed-db",
            str(FIXTURES / "transfer" / "A_tgt_seed.db"),
            "--tgt-full-db",
            str(FIXTURES / "transfer" / "A_tgt_full.db"),
            "--report-out",
            str(report),
            "--require-transfer-hard",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENV,
        timeout=1800,
    )
    assert proc.returncode == 0, (
        f"stdout tail:\n{proc.stdout[-2000:]}\nstderr tail:\n{proc.stderr[-2000:]}"
    )
    text = report.read_text(encoding="utf-8")
    assert "transfer_holdout_v0" in text
    assert "TRANSFER-hard" in text
    assert "**PASS**" in text
    assert "warp_nl_v0" in text
    assert "120" in text
