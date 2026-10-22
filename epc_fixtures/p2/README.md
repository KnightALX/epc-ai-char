# EPC P2 fixtures — reusable operators

Synthetic DEMO only. Modes on the same CLI:

```bash
python3 -m epc_engine /workspace/epc_fixtures/p2/job_corner_fill_green.yaml
python3 -m epc_engine --mode pvt_sparse_fill /workspace/epc_fixtures/p2/job_sparse_fill_green.yaml
```

## One-shot suite

```bash
bash /workspace/epc_fixtures/p2/run_p2_suite.sh
```

Covers: Op-Geom / Op-Miss / Op-Sparse green+red, mode/operator conflict, H3, sample + P1 green regression.

## Expected green COUNTs

| job | COUNT |
|---|---|
| `job_corner_fill_green.yaml` | 2000 = 5×8×50 |
| `job_missing_fill_green.yaml` | 800 = 2×8×50 |
| `job_sparse_fill_green.yaml` | 800 = 2×8×50 |

## H3

```bash
PYTHONPATH=/workspace python3 /workspace/epc_fixtures/p2/eval_h3.py
```

Report: `h3_report.md`
