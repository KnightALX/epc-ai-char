#!/usr/bin/env bash
# LON (dual-new leave-pair) suite — parallel to run_ab_hard_suite / run_p2_suite
# Does NOT call Geom corner protocol or AB stamp writers.
set -u
cd /workspace
export PYTHONPATH=/workspace
PASS=0
FAIL=0
REPORT=/workspace/epc_fixtures/algo_holdout_dual_new_report.md

ok() { echo "OK $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL $1: $2"; FAIL=$((FAIL+1)); }

echo "======== LON hold-out suite ========"

# --- U3 gate logic (≤, equality PASS; > FAIL) ---
echo "=== U3 LON-hard gate logic ==="
python3 - <<'PY'
from epc_engine.lon_holdout import evaluate_lon_hard_gates, GATE_LON
ok, g, d = evaluate_lon_hard_gates(0.1, 0.1)
assert ok and g[GATE_LON], (ok, g)
ok2, g2, _ = evaluate_lon_hard_gates(0.2, 0.1)
assert (not ok2) and (not g2[GATE_LON]), g2
ok3, g3, _ = evaluate_lon_hard_gates(0.05, 0.1)
assert ok3 and g3[GATE_LON], g3
assert d["compare"] == "<=" and d["protocol"] == "lon_v0"
print("lon_gate_logic PASS")
PY
if [[ $? -eq 0 ]]; then ok "U3_gate_logic"; else bad "U3_gate_logic" "assert"; fi

# --- U5 mock red: hard EXIT path ---
echo "=== U5 mock red (hard EXIT) ==="
python3 - <<'PY'
from epc_engine.lon_holdout import evaluate_lon_hard_gates
ok, g, _ = evaluate_lon_hard_gates(0.99, 0.10)
assert not ok
rc = 0 if ok else 3
assert rc == 3
print("mock_red EXIT", rc)
PY
if [[ $? -eq 0 ]]; then ok "U5_mock_red"; else bad "U5_mock_red" "assert"; fi

# --- U1 protocol purity (single fold) ---
echo "=== U1 protocol purity (1 fold) ==="
python3 - <<'PY'
from pathlib import Path
from epc_engine.source import load_source_db
from epc_engine.train_lib import LOI_INSTANCES, LOP_PVTS, CORE_KEYS
from epc_engine.lon_holdout import eval_lon_fold
from epc_engine.construct_types import AXIS_KEYS

s = load_source_db(Path("/workspace/epc_fixtures/A_ref.db"))
keys = [k for k in CORE_KEYS if k in s.field_keys and k not in AXIS_KEYS]
I_h, P_h = LOI_INSTANCES[0], LOP_PVTS[0]
b, r, bb, rb, purity = eval_lon_fold(
    s, held_inst=I_h, held_pvt=P_h, keys=keys, seed=42
)
assert purity["train_has_held_inst"] is False
assert purity["train_has_held_pvt"] is False
assert purity["train_n_instances"] == len(s.instances) - 1
assert purity["train_n_pvts"] == len(s.pvts) - 1
locs = purity["test_locators"]
assert len(locs) == len(keys)
assert all(i == I_h and p == P_h for i, p, k in locs)
assert b.summary()["n"] == r.summary()["n"]
assert b.summary()["n"] > 0
print("purity PASS", I_h, P_h, "n_cells", r.summary()["n"])
PY
if [[ $? -eq 0 ]]; then ok "U1_protocol_purity"; else bad "U1_protocol_purity" "assert"; fi

# --- U2 green report (full 30-fold; ~1–2 min) ---
echo "=== U2 green LON report (30 folds) ==="
set +e
python3 -m epc_engine.lon_holdout \
  --source-db /workspace/epc_fixtures/A_ref.db \
  --report-out "$REPORT" \
  --require-lon-hard
rc=$?
set -e
if [[ "$rc" -eq 0 && -f "$REPORT" ]]; then
  python3 - <<'PY'
from pathlib import Path
import re
t = Path("/workspace/epc_fixtures/algo_holdout_dual_new_report.md").read_text()
assert "lon_v0" in t and "LON-hard" in t and "Dual-new" in t
assert "**PASS**" in t
# Summary row: | **LON** (`lon_v0`) | idw_p95 | sel_p95 | ...
m = re.search(
    r"\*\*LON\*\*\s*\(`lon_v0`\)\s*\|\s*([0-9.eE+-]+)\s*\|\s*([0-9.eE+-]+)",
    t,
)
assert m, "missing LON summary p95 row"
idw, sel = float(m.group(1)), float(m.group(2))
assert sel <= idw, (sel, idw)
assert "30" in t
print(f"green LON p95_selected={sel:.6g} p95_idw={idw:.6g}")
PY
  if [[ $? -eq 0 ]]; then ok "U2_green_report"; else bad "U2_green_report" "p95 parse/assert"; fi
else
  bad "U2_green_report" "exit=$rc or missing report"
fi

# --- U4 anti-impersonation ---
echo "=== U4 anti-impersonation ==="
python3 - <<'PY'
from pathlib import Path
import re
src = Path("/workspace/epc_engine/lon_holdout.py").read_text()
code_only = re.sub(r'""".*?"""', "", src, flags=re.S)
code_only = re.sub(r"'''.*?'''", "", code_only, flags=re.S)
code_only = re.sub(r"#.*", "", code_only)
bad_hits = [t for t in ("eval_h3", "h3_hard", "modes.h3") if t in code_only]
assert not bad_hits, bad_hits
print("U4 no corner/H3 evidence in lon_holdout code PASS")
PY
if [[ $? -eq 0 ]]; then ok "U4_no_eval_h3"; else bad "U4_no_eval_h3" "forbidden refs"; fi

# --- Mutual link with LOI/LOP report ---
echo "=== report mutual links ==="
if rg -q "algo_holdout_dual_new_report|Dual-new / LON" /workspace/epc_fixtures/algo_holdout_report.md \
  && rg -q "algo_holdout_report" "$REPORT"; then
  ok "mutual_report_links"
else
  bad "mutual_report_links" "missing cross-link"
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

# --- no LON stamp ---
echo "=== no LON stamp contract ==="
if [[ -f /workspace/epc_engine/models/residual_gbdt.joblib.ab_hard.json ]] \
  && [[ ! -f /workspace/epc_engine/models/residual_gbdt.joblib.lon_hard.json ]]; then
  ok "no_lon_stamp"
else
  bad "no_lon_stamp" "missing ab stamp or unexpected lon stamp"
fi

echo "======== SUMMARY pass=$PASS fail=$FAIL ========"
if [[ "$FAIL" -gt 0 ]]; then exit 1; fi
exit 0
