#!/usr/bin/env bash
# Red regression: tighten table_upper_bound to 1000 (max≈1387) → must FAIL, no usable B.db.
# Does NOT modify epc_job.sample.yaml.
set -euo pipefail
OUT_DB=/tmp/epc_B_red.db
OUT_AUDIT=/tmp/epc_B_red_audit.md
JOB=/tmp/epc_job_red.yaml
rm -f "$OUT_DB" "$OUT_AUDIT" "$JOB"
python3 - <<PY
from pathlib import Path
import yaml
src = Path("/workspace/epc_fixtures/epc_job.sample.yaml")
raw = yaml.safe_load(src.read_text())
raw["constraints"][0]["target"]["value"] = 1000
raw["output"]["db_path"] = "/tmp/epc_B_red.db"
raw["output"]["audit_report_path"] = "/tmp/epc_B_red_audit.md"
Path("/tmp/epc_job_red.yaml").write_text(yaml.dump(raw, sort_keys=False))
print("wrote /tmp/epc_job_red.yaml (bound=1000)")
PY
set +e
cd /workspace && python3 -m epc_engine "$JOB" 2>/tmp/epc_red_stderr.txt
EC=$?
set -e
echo "EXIT=$EC"
if [[ -f "$OUT_DB" ]]; then
  echo "BAD: B.db exists at $OUT_DB"
  exit 2
fi
echo "OK: no B.db at $OUT_DB"
if ! grep -q "FAIL: constraint gate failed" /tmp/epc_red_stderr.txt; then
  echo "BAD: stderr missing gate fail"
  cat /tmp/epc_red_stderr.txt
  exit 3
fi
echo "OK: stderr has gate fail"
if [[ -f "$OUT_AUDIT" ]] && grep -q "gates_ok: \`False\`" "$OUT_AUDIT"; then
  echo "OK: FAIL audit present"
elif [[ -f "$OUT_AUDIT" ]] && grep -qi "FAIL" "$OUT_AUDIT"; then
  echo "OK: FAIL audit present (title)"
else
  echo "WARN: audit missing or not clearly FAIL"
fi
test "$EC" -ne 0
echo "RED regression PASS"
