# EPC P1 fixtures — relative_improve_vs_source

## Green

```bash
cd /workspace
python3 -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_improve_green.yaml
# backend=idw_nn:
python3 -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_improve_green_idw.yaml
```

Expect: EXIT0, COUNT=4950, G3 `expanded_constraint_count=16`
(= 2 inst × 2 pvt × (2 speed + 2 power)), G1/G2 PASS, speed ×0.96 / power ×0.95.

## Red

| Case | YAML | Expect |
|---|---|---|
| R1 vague | `epc_job.p1_r1_vague.yaml` | load reject EXIT≠0, no B.db |
| R2 proxy forbid | `epc_job.p1_r2_proxy_forbid.yaml` | EXIT1, no B.db |

```bash
bash /workspace/epc_fixtures/p1/run_p1_suite.sh
```
