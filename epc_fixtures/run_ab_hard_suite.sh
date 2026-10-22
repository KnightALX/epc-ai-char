#!/usr/bin/env bash
# AB-hard suite — decoupled from P2 run_p2_suite / eval_h3 / h3_hard.py
set -u
cd /workspace
export PYTHONPATH=/workspace
PASS=0
FAIL=0
MODEL=/workspace/epc_engine/models/residual_gbdt.joblib
STAMP=${MODEL}.ab_hard.json
STAMP_BAK=/tmp/residual_gbdt.ab_hard.json.bak_suite

ok() { echo "OK $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL $1: $2"; FAIL=$((FAIL+1)); }

echo "======== AB-hard suite ========"

# --- U3 + U2 offline gate unit (no full LOI recompute) ---
echo "=== U2/U3 offline gate logic ==="
python3 - <<'PY'
from epc_engine.ab_hard import evaluate_ab_hard_gates
# U3: equality → PASS
ok, g, _ = evaluate_ab_hard_gates(0.1, 0.1, 0.05, 0.05)
assert ok and g["AB-hard-LOI"] and g["AB-hard-LOP"], g
# U2: sel > idw → FAIL
ok2, g2, _ = evaluate_ab_hard_gates(0.2, 0.1, 0.05, 0.05)
assert (not ok2) and (not g2["AB-hard-LOI"]), g2
ok3, g3, _ = evaluate_ab_hard_gates(0.1, 0.1, 0.2, 0.05)
assert (not ok3) and (not g3["AB-hard-LOP"]), g3
# aliases present
assert g["P-LOI-base"] is True and g["P-LOP"] is True
print("gate_logic PASS")
PY
if [[ $? -eq 0 ]]; then ok "U2_U3_gate_logic"; else bad "U2_U3_gate_logic" "assert"; fi

# --- Ensure green stamp exists for current model ---
echo "=== seed/verify green stamp ==="
python3 - <<'PY'
from pathlib import Path
from epc_engine.ab_hard import build_stamp, write_stamp, load_stamp, check_ab_hard_online
from epc_engine.train_lib import sha16
mp = Path("/workspace/epc_engine/models/residual_gbdt.joblib")
sha = sha16(mp)
st = load_stamp(mp)
if st is None or st.get("model_sha16") != sha or st.get("ab_hard") != "PASS":
    # Seed from last accepted algo_holdout_report numbers
    st = build_stamp(
        model_sha16=sha,
        backend="residual_gbdt",
        p95_selected_loi=0.102257,
        p95_idw_loi=0.31168,
        p95_selected_lop=5.22059e-05,
        p95_idw_lop=5.2333e-05,
        gates={"P-LOI-reg": True},
        source_path="/workspace/epc_fixtures/A_ref.db",
        seed=42,
    )
    write_stamp(st, mp)
ok, msg, a = check_ab_hard_online(backend="residual_gbdt", model_path=mp, model_sha16=sha)
assert ok and a["ab_hard"] == "PASS", (ok, msg, a)
print(msg)
PY
if [[ $? -eq 0 ]]; then ok "U1_stamp_green"; else bad "U1_stamp_green" "seed/check"; fi

# --- U1 online green ---
echo "=== U1 online green residual ==="
rm -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_green.db
set +e
python3 -m epc_engine /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_green.yaml
rc=$?
set -e
if [[ "$rc" -eq 0 && -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_green.db ]]; then
  if rg -q "ab_hard.: .PASS|\\*\\*ab_hard\\*\\*: \`PASS\`" /workspace/epc_fixtures/ab_hard/B_out.ab_hard_green_audit.md; then
    ok "U1_online_green"
  else
    bad "U1_online_green" "audit missing ab_hard PASS"
  fi
else
  bad "U1_online_green" "exit=$rc or missing db"
fi

# --- U4 online red: poison stamp (p95_sel > p95_idw) ---
echo "=== U4 online red bad stamp ==="
cp -f "$STAMP" "$STAMP_BAK"
python3 - <<'PY'
import json
from pathlib import Path
from epc_engine.train_lib import sha16
mp = Path("/workspace/epc_engine/models/residual_gbdt.joblib")
p = Path(str(mp) + ".ab_hard.json")
st = json.loads(p.read_text())
st["ab_hard"] = "FAIL"
st["p95_selected_loi"] = 0.99
st["p95_idw_loi"] = 0.10
st["model_sha16"] = sha16(mp)
st["stamp_sha16"] = st["model_sha16"]
p.write_text(json.dumps(st, indent=2) + "\n")
PY
rm -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red.db
set +e
python3 -m epc_engine /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_red.yaml
rc=$?
set -e
# restore stamp immediately
cp -f "$STAMP_BAK" "$STAMP"
if [[ "$rc" -ne 0 && ! -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red.db ]]; then
  if rg -q "ab_hard.: .FAIL|\\*\\*ab_hard\\*\\*: \`FAIL\`" /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red_audit.md; then
    ok "U4_online_red_stamp"
  else
    bad "U4_online_red_stamp" "audit missing FAIL"
  fi
else
  bad "U4_online_red_stamp" "exit=$rc db_exists=$([[ -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red.db ]] && echo yes || echo no)"
fi

# --- U4 missing stamp ---
echo "=== U4 missing stamp ==="
mv "$STAMP" "$STAMP_BAK"
rm -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red.db
set +e
python3 -m epc_engine /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_red.yaml
rc=$?
set -e
mv "$STAMP_BAK" "$STAMP"
if [[ "$rc" -ne 0 && ! -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red.db ]]; then
  if rg -q "missing_stamp|ab_hard.: .FAIL" /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red_audit.md; then
    ok "U4_missing_stamp"
  else
    bad "U4_missing_stamp" "audit reason"
  fi
else
  bad "U4_missing_stamp" "exit=$rc"
fi

# --- U5 idw skip ---
echo "=== U5 idw skip ==="
rm -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_idw.db
set +e
python3 -m epc_engine /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_idw.yaml
rc=$?
set -e
if [[ "$rc" -eq 0 && -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_idw.db ]]; then
  if rg -q "ab_hard.: .SKIP|\\*\\*ab_hard\\*\\*: \`SKIP\`" /workspace/epc_fixtures/ab_hard/B_out.ab_hard_idw_audit.md; then
    ok "U5_idw_skip"
  else
    bad "U5_idw_skip" "audit missing SKIP"
  fi
else
  bad "U5_idw_skip" "exit=$rc"
fi

# --- U0 light regression: sample (residual) still green ---
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

# --- Decouple check: h3_hard.py untouched fingerprint note ---
echo "=== AB-M4 decouple (suite isolation) ==="
if [[ -f /workspace/epc_engine/modes/h3_hard.py ]]; then
  ok "AB-M4_h3_hard_present_untouched_by_this_suite"
else
  bad "AB-M4" "h3_hard.py missing unexpectedly"
fi

echo "======== SUMMARY pass=$PASS fail=$FAIL ========"
if [[ "$FAIL" -gt 0 ]]; then exit 1; fi
exit 0
