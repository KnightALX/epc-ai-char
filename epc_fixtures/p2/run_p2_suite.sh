#!/usr/bin/env bash
# P2 operator suite: green/red + H3-hard + P0/P1 regression samples
set -u
cd /workspace
PASS=0
FAIL=0

expect_exit() {
  local name="$1" want="$2"
  shift 2
  echo "=== $name (expect EXIT=$want) ==="
  set +e
  "$@" >/tmp/epc_p2_out.txt 2>&1
  local rc=$?
  set -e
  if [[ "$rc" -ne "$want" ]]; then
    echo "FAIL $name: exit=$rc want=$want"
    tail -20 /tmp/epc_p2_out.txt
    FAIL=$((FAIL+1))
    return
  fi
  echo "OK $name exit=$rc"
  PASS=$((PASS+1))
}

expect_db() {
  local name="$1" db="$2" want_exist="$3" want_count="${4:-}"
  if [[ "$want_exist" == "yes" ]]; then
    if [[ ! -f "$db" ]]; then
      echo "FAIL $name: missing db $db"; FAIL=$((FAIL+1)); return
    fi
    if [[ -n "$want_count" ]]; then
      cnt=$(python3 -c "import sqlite3; print(sqlite3.connect('$db').execute('select count(*) from char_data').fetchone()[0])")
      if [[ "$cnt" != "$want_count" ]]; then
        echo "FAIL $name: COUNT=$cnt want=$want_count"; FAIL=$((FAIL+1)); return
      fi
    fi
  else
    if [[ -f "$db" ]]; then
      echo "FAIL $name: db should not exist: $db"; FAIL=$((FAIL+1)); return
    fi
  fi
  echo "OK $name db-check"
  PASS=$((PASS+1))
}

# Rebuild punched/sparse if missing
python3 /workspace/epc_fixtures/p2/build_p2_fixtures.py >/tmp/epc_p2_build.txt

# --- Greens ---
expect_exit GEOM_GREEN 0 python3 -m epc_engine /workspace/epc_fixtures/p2/job_corner_fill_green.yaml
expect_db GEOM_COUNT /workspace/epc_fixtures/p2/out_geom.db yes 2000

expect_exit MISS_GREEN 0 python3 -m epc_engine /workspace/epc_fixtures/p2/job_missing_fill_green.yaml
expect_db MISS_COUNT /workspace/epc_fixtures/p2/out_missing.db yes 800

expect_exit SPARSE_GREEN 0 python3 -m epc_engine /workspace/epc_fixtures/p2/job_sparse_fill_green.yaml
expect_db SPARSE_COUNT /workspace/epc_fixtures/p2/out_sparse.db yes 800

# --- Reds (no db) ---
rm -f /workspace/epc_fixtures/p2/out_geom_red.db \
      /workspace/epc_fixtures/p2/out_missing_red.db \
      /workspace/epc_fixtures/p2/out_sparse_red.db \
      /workspace/epc_fixtures/p2/out_geom_residual_h3hard.db

expect_exit GEOM_RED 2 python3 -m epc_engine /workspace/epc_fixtures/p2/job_corner_fill_red.yaml
expect_db GEOM_RED_DB /workspace/epc_fixtures/p2/out_geom_red.db no

expect_exit MISS_RED 2 python3 -m epc_engine /workspace/epc_fixtures/p2/job_missing_fill_red.yaml
expect_db MISS_RED_DB /workspace/epc_fixtures/p2/out_missing_red.db no

expect_exit SPARSE_RED 2 python3 -m epc_engine /workspace/epc_fixtures/p2/job_sparse_fill_red.yaml
expect_db SPARSE_RED_DB /workspace/epc_fixtures/p2/out_sparse_red.db no

# F2: Geom + residual_gbdt must H3-hard FAIL (finish_job → EXIT=1), no db
expect_exit GEOM_RESIDUAL_H3HARD 1 python3 -m epc_engine /workspace/epc_fixtures/p2/job_corner_fill_residual_h3hard.yaml
expect_db GEOM_RESIDUAL_H3HARD_DB /workspace/epc_fixtures/p2/out_geom_residual_h3hard.db no
# Audit must record h3_hard FAIL + both p95s
echo "=== GEOM_RESIDUAL_H3HARD_AUDIT ==="
if rg -q "h3_hard.*FAIL|h3_hard: FAIL|\*\*h3_hard\*\*: \`FAIL\`" /workspace/epc_fixtures/p2/out_geom_residual_h3hard_audit.md \
   && rg -q "p95_selected" /workspace/epc_fixtures/p2/out_geom_residual_h3hard_audit.md \
   && rg -q "p95_idw_nn" /workspace/epc_fixtures/p2/out_geom_residual_h3hard_audit.md; then
  echo "OK GEOM_RESIDUAL_H3HARD_AUDIT"
  PASS=$((PASS+1))
else
  echo "FAIL GEOM_RESIDUAL_H3HARD_AUDIT"
  rg -n "h3_hard|p95_" /workspace/epc_fixtures/p2/out_geom_residual_h3hard_audit.md || true
  FAIL=$((FAIL+1))
fi

# R1: green Geom YAML keeps require_corner_coverage: true
echo "=== R1_CORNER_COVERAGE ==="
if rg -q "require_corner_coverage:\s*true" /workspace/epc_fixtures/p2/job_corner_fill_green.yaml; then
  echo "OK R1_CORNER_COVERAGE"
  PASS=$((PASS+1))
else
  echo "FAIL R1_CORNER_COVERAGE: green geom missing require_corner_coverage: true"
  FAIL=$((FAIL+1))
fi

# R2 / F_mode_conflict: mode/operator conflict
cat > /tmp/epc_conflict.yaml <<'Y'
version: "0.1"
mode: corner_fill_geom
operator: pvt_sparse_fill
source: {db_path: "/workspace/epc_fixtures/A_ref.db"}
geom_fill: {target_instances: [HINP3TCAM256X32SWISDC]}
output:
  db_path: "/tmp/no.db"
  audit_report_path: "/tmp/no_audit.md"
gates: {on_violation: fail_job}
Y
expect_exit F_mode_conflict 2 python3 -m epc_engine /tmp/epc_conflict.yaml

# --- H3 ---
echo "=== H3 ==="
set +e
PYTHONPATH=/workspace python3 /workspace/epc_fixtures/p2/eval_h3.py >/tmp/epc_p2_h3.txt 2>&1
rc=$?
set -e
if [[ "$rc" -ne 0 ]]; then
  echo "FAIL H3"; cat /tmp/epc_p2_h3.txt; FAIL=$((FAIL+1))
else
  echo "OK H3"; PASS=$((PASS+1))
fi

# --- P0/P1 regression (sample + p1 green) ---
expect_exit SAMPLE 0 python3 -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
expect_db SAMPLE_COUNT /workspace/epc_fixtures/B_out.sample.db yes 4950

expect_exit P1_GREEN 0 python3 -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_improve_green.yaml
expect_db P1_COUNT /workspace/epc_fixtures/p1/B_out.p1_green.db yes 4950

# idw_nn geom still works
cat > /tmp/epc_geom_idw.yaml <<'Y'
version: "0.1"
mode: corner_fill_geom
job_name: DEMO_P2_geom_idw
source:
  process: DEMO_A
  db_path: "/workspace/epc_fixtures/A_ref.db"
geom_fill:
  seed_instances:
    - HINP3TCAM64X8SWISDC
    - HINP3TCAM64X100SWISDC
    - HINP3TCAM512X8SWISDC
    - HINP3TCAM512X100SWISDC
  target_instances: [HINP3TCAM256X32SWISDC]
  pvt_list: "/workspace/epc_fixtures/p2/pvt8.txt"
construct: {backend: idw_nn}
field_policy: {keys: all_from_source}
output:
  db_path: "/workspace/epc_fixtures/p2/out_geom_idw.db"
  audit_report_path: "/workspace/epc_fixtures/p2/out_geom_idw_audit.md"
gates: {require_constraint_satisfaction: true, on_violation: fail_job}
Y
expect_exit GEOM_IDW 0 python3 -m epc_engine /tmp/epc_geom_idw.yaml

echo "=== SUMMARY pass=$PASS fail=$FAIL ==="
[[ "$FAIL" -eq 0 ]]
