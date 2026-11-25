#!/usr/bin/env bash
# Transfer (Residual TL) suite — parallel to run_ab_hard_suite / run_lon_holdout_suite
# Does NOT call Geom H3 / AB stamp / LON protocols.
set -u
cd /workspace
export PYTHONPATH=/workspace
PASS=0
FAIL=0
REPORT=/workspace/epc_fixtures/transfer/transfer_holdout_report.md
ACCEPT=/workspace/epc_fixtures/transfer/迁移增强_验收报告.md

ok() { echo "OK $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL $1: $2"; FAIL=$((FAIL+1)); }

echo "======== Transfer hold-out suite ========"

# --- U3 gate logic (≤, equality PASS; > FAIL) ---
echo "=== U3 TRANSFER-hard gate logic ==="
python3 - <<'PY'
from epc_engine.transfer_lib import evaluate_transfer_hard_gates, GATE_TRANSFER, PROTOCOL_ID
ok, g, d = evaluate_transfer_hard_gates(0.1, 0.1)
assert ok and g[GATE_TRANSFER], (ok, g)
ok2, g2, _ = evaluate_transfer_hard_gates(0.2, 0.1)
assert (not ok2) and (not g2[GATE_TRANSFER]), g2
ok3, g3, _ = evaluate_transfer_hard_gates(0.05, 0.1)
assert ok3 and g3[GATE_TRANSFER], g3
assert d["compare"] == "<=" and d["protocol"] == PROTOCOL_ID
print("transfer_gate_logic PASS")
PY
if [[ $? -eq 0 ]]; then ok "U3_gate_logic"; else bad "U3_gate_logic" "assert"; fi

# --- U5 mock red: hard EXIT path ---
echo "=== U5 mock red (hard EXIT) ==="
python3 - <<'PY'
from epc_engine.transfer_lib import evaluate_transfer_hard_gates
ok, g, _ = evaluate_transfer_hard_gates(0.99, 0.10)
assert not ok
rc = 0 if ok else 3
assert rc == 3
print("mock_red EXIT", rc)
PY
if [[ $? -eq 0 ]]; then ok "U5_mock_red"; else bad "U5_mock_red" "assert"; fi

# --- U1 fixture honesty ---
echo "=== U1 fixture honesty (non-identity warp) ==="
python3 - <<'PY'
import sqlite3
from pathlib import Path
import json
src = Path("/workspace/epc_fixtures/transfer/A_src.db")
tgt = Path("/workspace/epc_fixtures/transfer/A_tgt_full.db")
seed = Path("/workspace/epc_fixtures/transfer/A_tgt_seed.db")
aref = Path("/workspace/epc_fixtures/A_ref.db")
assert src.is_file() and tgt.is_file() and seed.is_file()
assert aref.is_file()
# A_ref not overwritten: mtime/size still a real file and builder only copies
c1 = sqlite3.connect(str(src))
c2 = sqlite3.connect(str(tgt))
r1 = c1.execute("SELECT value FROM char_data WHERE field_key='leakage_vddc' LIMIT 5").fetchall()
r2 = c2.execute("SELECT value FROM char_data WHERE field_key='leakage_vddc' LIMIT 5").fetchall()
assert r1 != r2, "src/tgt leakage identical — fake transfer"
# axes unchanged
a1 = c1.execute("SELECT value FROM char_data WHERE field_key='tran_index' LIMIT 1").fetchone()[0]
a2 = c2.execute("SELECT value FROM char_data WHERE field_key='tran_index' LIMIT 1").fetchone()[0]
assert a1 == a2
c1.close(); c2.close()
meta = json.loads(Path("/workspace/epc_fixtures/transfer/warp_meta.json").read_text())
assert meta["warp_id"] == "warp_nl_v0"
assert meta["n_groups_seed"] == 120
assert meta["forced_boundary_groups"] == 30
man = json.loads(Path("/workspace/epc_fixtures/transfer/seed_manifest.json").read_text())
assert len(man["forced_boundary"]) == 30
print("fixture honesty PASS", meta["warp_id"], "seed", meta["n_groups_seed"])
PY
if [[ $? -eq 0 ]]; then ok "U1_fixture_honesty"; else bad "U1_fixture_honesty" "assert"; fi

# --- U2/U3 green report ---
echo "=== U2/U3 green transfer report ==="
set +e
python3 -m epc_engine.transfer_holdout \
  --src-db /workspace/epc_fixtures/transfer/A_src.db \
  --seed-db /workspace/epc_fixtures/transfer/A_tgt_seed.db \
  --tgt-full-db /workspace/epc_fixtures/transfer/A_tgt_full.db \
  --report-out "$REPORT" \
  --require-transfer-hard
rc=$?
set -e
if [[ "$rc" -eq 0 && -f "$REPORT" ]]; then
  python3 - <<'PY'
from pathlib import Path
import re
t = Path("/workspace/epc_fixtures/transfer/transfer_holdout_report.md").read_text()
assert "transfer_holdout_v0" in t and "TRANSFER-hard" in t
assert "warp_nl_v0" in t
assert "**PASS**" in t
# Summary rows
m_tr = re.search(r"\|\s*\*\*linear_tr\*\*\s*\|\s*([0-9.eE+-]+)", t)
m_rtl = re.search(r"\|\s*\*\*residual_tl\*\*\s*\|\s*([0-9.eE+-]+)", t)
assert m_tr and m_rtl, (m_tr, m_rtl)
tr, rtl = float(m_tr.group(1)), float(m_rtl.group(1))
assert rtl <= tr, (rtl, tr)
assert "120" in t  # seed groups
print(f"green TRANSFER p95_RTL={rtl:.6g} p95_TR={tr:.6g}")
PY
  if [[ $? -eq 0 ]]; then ok "U2_green_report"; else bad "U2_green_report" "p95 parse/assert"; fi
else
  bad "U2_green_report" "exit=$rc or missing report"
fi

# --- hard flag default-off contract ---
echo "=== hard flag default off (EXIT 0 even if we force fail via unit) ==="
python3 - <<'PY'
from epc_engine.transfer_holdout import build_parser
args = build_parser().parse_args([])
assert args.require_transfer_hard is False
print("default require_transfer_hard=False PASS")
PY
if [[ $? -eq 0 ]]; then ok "hard_flag_default_off"; else bad "hard_flag_default_off" "assert"; fi

# --- U4 anti-impersonation / decoupling ---
echo "=== U4 decoupling ==="
python3 - <<'PY'
from pathlib import Path
import re
for rel in ("transfer_lib.py", "transfer_holdout.py", "modes/transfer_ab.py"):
    src = Path("/workspace/epc_engine") / rel
    text = src.read_text()
    code_only = re.sub(r'""".*?"""', "", text, flags=re.S)
    code_only = re.sub(r"'''.*?'''", "", code_only, flags=re.S)
    code_only = re.sub(r"#.*", "", code_only)
    bad_hits = [t for t in ("eval_h3", "h3_hard", "modes.h3", "write_ab_hard", "lon_hard") if t in code_only]
    # allow comments mentioning LON/AB in docs strings already stripped
    assert not bad_hits, (rel, bad_hits)
# AB stamp untouched; no transfer stamp
assert Path("/workspace/epc_engine/models/residual_gbdt.joblib.ab_hard.json").is_file()
assert not Path("/workspace/epc_engine/models/residual_gbdt.joblib.transfer_hard.json").exists()
print("U4 decoupling PASS")
PY
if [[ $? -eq 0 ]]; then ok "U4_decoupling"; else bad "U4_decoupling" "forbidden refs"; fi

# --- U5 online green writes B_tgt ---
echo "=== online transfer_ab residual_tl ==="
set +e
python3 -m epc_engine /workspace/epc_fixtures/transfer/epc_job.transfer_rtl.yaml
rc=$?
set -e
if [[ "$rc" -eq 0 && -f /workspace/epc_fixtures/transfer/B_tgt.rtl.db ]]; then
  ok "online_rtl_job"
else
  bad "online_rtl_job" "exit=$rc"
fi

echo "=== online transfer_ab linear_tr (Should one-click) ==="
set +e
python3 -m epc_engine /workspace/epc_fixtures/transfer/epc_job.transfer_tr.yaml
rc=$?
set -e
if [[ "$rc" -eq 0 && -f /workspace/epc_fixtures/transfer/B_tgt.tr.db ]]; then
  ok "online_tr_job"
else
  bad "online_tr_job" "exit=$rc"
fi

# --- U0 light: sample residual still green ---
echo "=== U0 sample residual ==="
set +e
python3 -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
rc=$?
set -e
if [[ "$rc" -eq 0 && -f /workspace/epc_fixtures/B_out.sample.db ]]; then
  ok "U0_sample"
else
  bad "U0_sample" "exit=$rc"
fi

# --- write accept report stub for orchestrator ---
{
  echo "# 迁移增强 验收报告（开发侧 suite）"
  echo ""
  echo "- Suite pass=$PASS fail=$FAIL"
  echo "- Report: \`$REPORT\`"
  echo "- Protocol: \`transfer_holdout_v0\` / warp \`warp_nl_v0\`"
  echo "- **开发侧绿；正式验收另派，勿自签**"
} > "$ACCEPT"

echo "======== SUMMARY pass=$PASS fail=$FAIL ========"
if [[ "$FAIL" -gt 0 ]]; then exit 1; fi
exit 0
