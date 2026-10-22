# EPC Algorithm Hold-out Report — residual_gbdt vs idw_nn

- Generated: **2026-10-21 22:56:59 CST** (Asia/Shanghai)
- Protocol: LOI (5 folds) + LOP (6 folds)
- Core keys: `tselr1_min_period, tcq, tcd, taccess, leakage_vddc, read_power_vddc, write_power_vddc, dynamic_energy_read`
- ε = `1e-12`; random_seed = `42`
- Relative error: `|hat-true|/max(|true|,ε)` at cell level
- **apply_on**: `all_extrapolated` (heads=`models_geom+models_pvt`)
- **DEMO synthetic only** — not foundry/PDK calibration

> **Policy (PVT residual v0):** residual on every non-`seed_from_A` extrapolation (geom / pvt / both). Dual-head: geom←leave-instance, pvt←leave-pvt.

- Production model: `/workspace/epc_engine/models/residual_gbdt.joblib` (sha256[:16]=bd6ecde2f27e622b)

## Acceptance gates (AB-hard / PVT residual)

| ID | Criterion | p95_selected | p95_idw_nn | delta | backend | protocol | Result |
|---|---|---|---|---|---|---|---|
| **AB-hard-LOP** | p95_sel ≤ p95_idw | 5.22059e-05 | 5.2333e-05 | -1.271e-07 | `residual_gbdt` | `lop_v0` | **PASS** |
| **AB-hard-LOI** | p95_sel ≤ p95_idw | 0.102257 | 0.31168 | -0.209423 | `residual_gbdt` | `loi_v0` | **PASS** |
| **P-LOI-reg** | p95_residual ≤ prev×1.05 | 0.102257 | (reg) | — | `residual_gbdt` | `loi_v0` | **PASS** |
| P-LOI-reg+ (bonus) | p95_residual ≤ prev | 0.102257 | (prev=0.102331) | — | `residual_gbdt` | `loi_v0` | **PASS** |
| alias P-LOP | = AB-hard-LOP (legacy strict-< → ≤) | 5.22059e-05 | 5.2333e-05 | -1.271e-07 | `residual_gbdt` | `lop_v0` | **PASS** |
| alias P-LOI-base | = AB-hard-LOI (legacy strict-< → ≤) | 0.102257 | 0.31168 | -0.209423 | `residual_gbdt` | `loi_v0` | **PASS** |

**Hard gates overall: ALL PASS** (AB-hard-LOI ∧ AB-hard-LOP ∧ P-LOI-reg; compare `≤`)

> Compare unified with H3-hard (`≤`). Online `epc_ab` reads stamp `residual_gbdt.joblib.ab_hard.json` (no per-job LOI recompute).

## Summary table

| Protocol | baseline idw_nn p95 | residual_gbdt p95 | n | ≤ idw? |
|---|---|---|---|---|
| **LOI** (`loi_v0`) | 0.31168 | 0.102257 | 20800 | YES |
| **LOP** (`lop_v0`) | 5.2333e-05 | 5.22059e-05 | 12480 | YES |

- LOI p50 baseline=0.0737119 residual=0.0705802
- LOI max baseline=0.462857 residual=0.191105
- LOP p50 baseline=0 residual=0
- LOP max baseline=0.320382 residual=0.20851

### LOI folds

- `HINP3TCAM64X8SWISDC`
- `HINP3TCAM512X100SWISDC`
- `HINP3TCAM64X100SWISDC`
- `HINP3TCAM512X8SWISDC`
- `HINP3TCAM256X32SWISDC`

### LOP folds

- `TT_0P80V_0P80V_25C`
- `SSGNP_0P99V_0P99V_125C`
- `FFGNP_0P675V_0P675V_M40C`
- `SSGNP_0P675V_0P675V_125C`
- `FFGNP_1P05V_1P05V_25C`
- `TT_0P90V_0P90V_M40C`

## Per-key LOI (p95)

| key | baseline p95 | residual p95 | Δ |
|---|---|---|---|
| `tselr1_min_period` | 0.311674 | 0.102668 | -0.209007 |
| `tcq` | 0.311679 | 0.102458 | -0.209221 |
| `tcd` | 0.311682 | 0.102212 | -0.20947 |
| `taccess` | 0.311677 | 0.102102 | -0.209574 |
| `leakage_vddc` | 0.457378 | 0.153255 | -0.304123 |
| `read_power_vddc` | 0.364467 | 0.0709403 | -0.293527 |
| `write_power_vddc` | 0.364475 | 0.0718404 | -0.292635 |
| `dynamic_energy_read` | 0.364616 | 0.0721703 | -0.292445 |

## Per-key LOP (p95)

| key | baseline p95 | residual p95 | Δ |
|---|---|---|---|
| `tselr1_min_period` | 3.91017e-05 | 3.91017e-05 | 0 |
| `tcq` | 4.28694e-05 | 4.28694e-05 | 0 |
| `tcd` | 5.12464e-05 | 5.12464e-05 | 0 |
| `taccess` | 3.7033e-05 | 3.7033e-05 | 0 |
| `leakage_vddc` | 0.319971 | 0.119731 | -0.20024 |
| `read_power_vddc` | 9.40216e-05 | 9.40216e-05 | 0 |
| `write_power_vddc` | 8.25287e-05 | 8.25287e-05 | 0 |
| `dynamic_energy_read` | 0.000247158 | 0.00026591 | 1.87526e-05 |


## Dual-new / LON

Leave-pair protocol (`lon_v0`) is reported separately (not merged into LOI/LOP p95):

- Sidecar: [`algo_holdout_dual_new_report.md`](/workspace/epc_fixtures/algo_holdout_dual_new_report.md)
- Suite: `bash /workspace/epc_fixtures/run_lon_holdout_suite.sh`
- Compare: `p95_sel ≤ p95_idw` (LON-hard); **no stamp** this round

## Notes

- Prior = existing IDW+NN (leave-one-instance / leave-one-pvt).
- Residual = sklearn `HistGradientBoostingRegressor` per key × head; `prior_hat` + ΔV/ΔT/1/V/V×T/corner-onehot are features.
- Hard gates: **AB-hard-LOI**, **AB-hard-LOP** (≤ idw; aliases P-LOI-base / P-LOP), **P-LOI-reg** (parallel).
