#!/usr/bin/env bash
# P1 green/red + sample regression suite
set -u
cd /workspace
PASS=0
FAIL=0

run_expect() {
  local name="$1" expect_exit="$2" yaml="$3" expect_db="$4"  # expect_db: yes|no
  echo "=== $name (expect EXIT=$expect_exit db=$expect_db) ==="
  set +e
  python3 -m epc_engine "$yaml"
  local rc=$?
  set -e
  if [[ "$rc" -ne "$expect_exit" ]]; then
    echo "FAIL $name: exit=$rc want=$expect_exit"
    FAIL=$((FAIL+1))
    return
  fi
  local db
  db=$(python3 - <<PY
import yaml
print(yaml.safe_load(open("$yaml"))["output"]["db_path"])
PY
)
  if [[ "$expect_db" == "yes" ]]; then
    if [[ ! -f "$db" ]]; then
      echo "FAIL $name: expected B.db at $db"
      FAIL=$((FAIL+1)); return
    fi
    cnt=$(python3 - <<PY
import sqlite3
print(sqlite3.connect("$db").execute("select count(*) from char_data").fetchone()[0])
PY
)
    if [[ "$cnt" != "4950" ]]; then
      echo "FAIL $name: COUNT=$cnt want=4950"
      FAIL=$((FAIL+1)); return
    fi
  else
    if [[ -f "$db" ]]; then
      echo "FAIL $name: B.db should not exist: $db"
      FAIL=$((FAIL+1)); return
    fi
  fi
  echo "OK $name"
  PASS=$((PASS+1))
}

# R1: load-time reject → exception → non-zero (cli re-raises). Capture exit.
echo "=== R1 vague (expect non-zero, no db) ==="
set +e
python3 -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_r1_vague.yaml
rc=$?
set -e
if [[ "$rc" -eq 0 ]]; then
  echo "FAIL R1: expected non-zero"
  FAIL=$((FAIL+1))
else
  if [[ -f /workspace/epc_fixtures/p1/B_out.p1_r1.db ]]; then
    echo "FAIL R1: B.db exists"
    FAIL=$((FAIL+1))
  else
    echo "OK R1 exit=$rc"
    PASS=$((PASS+1))
  fi
fi

run_expect R2 1 /workspace/epc_fixtures/p1/epc_job.p1_r2_proxy_forbid.yaml no
run_expect GREEN_residual 0 /workspace/epc_fixtures/p1/epc_job.p1_improve_green.yaml yes
run_expect GREEN_idw 0 /workspace/epc_fixtures/p1/epc_job.p1_improve_green_idw.yaml yes
run_expect SAMPLE 0 /workspace/epc_fixtures/epc_job.sample.yaml yes

echo "=== red upper bound (existing) ==="
bash /workspace/epc_fixtures/run_red_upper_bound.sh
rc=$?
if [[ "$rc" -eq 0 ]]; then
  # script itself should exit 0 if red behaved correctly
  echo "OK red_upper_bound harness"
  PASS=$((PASS+1))
else
  echo "FAIL red_upper_bound harness rc=$rc"
  FAIL=$((FAIL+1))
fi

echo "=== SUMMARY pass=$PASS fail=$FAIL ==="
[[ "$FAIL" -eq 0 ]]
