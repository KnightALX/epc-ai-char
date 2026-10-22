# EPC Dual-new / LON Hold-out Report — residual_gbdt vs idw_nn

- Generated: **2026-10-22 22:30:07 CST** (Asia/Shanghai)
- Protocol: **LON** (`lon_v0`) — leave-one-(instance,pvt) / leave-pair
- Folds: **30** (= LOI_INSTANCES × LOP_PVTS cartesian)
- Core keys: `tselr1_min_period, tcq, tcd, taccess, leakage_vddc, read_power_vddc, write_power_vddc, dynamic_energy_read`
- ε = `1e-12`; random_seed = `42`
- Relative error: `|hat-true|/max(|true|,ε)` at cell level
- **apply_on**: `all_extrapolated` (models_geom (both → geom head; mirrors online residual_reason=both))
- **DEMO synthetic only** — not foundry/PDK calibration
- **No LON stamp** this round (decoupled from AB-hard stamp / Op-Geom H3)

> **Policy:** train removes row `I_h` and column `P_h`; evaluate **only** cross points `(I_h, P_h, *)`. LOI/LOP cells must not be merged into LON p95.

- Sibling LOI/LOP report: [`algo_holdout_report.md`](/workspace/epc_fixtures/algo_holdout_report.md)
- Production model: `/workspace/epc_engine/models/residual_gbdt.joblib` (sha256[:16]=bd6ecde2f27e622b)

## Acceptance gate (LON-hard)

| ID | Criterion | p95_selected | p95_idw_nn | delta | n_cells | n_folds | backend | protocol | Result |
|---|---|---|---|---|---|---|---|---|---|
| **LON-hard** | p95_sel ≤ p95_idw | 0.104781 | 0.311677 | -0.206896 | 3120 | 30 | `residual_gbdt` | `lon_v0` | **PASS** |

**LON-hard: PASS** (compare `≤`; equality OK)

## Summary

| Protocol | baseline idw_nn p95 | residual_gbdt p95 | p50_idw | p50_sel | max_idw | max_sel | n | ≤ idw? |
|---|---|---|---|---|---|---|---|---|
| **LON** (`lon_v0`) | 0.311677 | 0.104781 | 0.073711 | 0.0690432 | 0.560031 | 0.578972 | 3120 | YES |

- Note: LOI-state cells I_h×(pvt≠P_h) and LOP-state (instance≠I_h)×P_h are NOT counted in LON p95.

### Fold list (I_h, P_h)

- `HINP3TCAM64X8SWISDC` × `TT_0P80V_0P80V_25C`
- `HINP3TCAM64X8SWISDC` × `SSGNP_0P99V_0P99V_125C`
- `HINP3TCAM64X8SWISDC` × `FFGNP_0P675V_0P675V_M40C`
- `HINP3TCAM64X8SWISDC` × `SSGNP_0P675V_0P675V_125C`
- `HINP3TCAM64X8SWISDC` × `FFGNP_1P05V_1P05V_25C`
- `HINP3TCAM64X8SWISDC` × `TT_0P90V_0P90V_M40C`
- `HINP3TCAM512X100SWISDC` × `TT_0P80V_0P80V_25C`
- `HINP3TCAM512X100SWISDC` × `SSGNP_0P99V_0P99V_125C`
- `HINP3TCAM512X100SWISDC` × `FFGNP_0P675V_0P675V_M40C`
- `HINP3TCAM512X100SWISDC` × `SSGNP_0P675V_0P675V_125C`
- `HINP3TCAM512X100SWISDC` × `FFGNP_1P05V_1P05V_25C`
- `HINP3TCAM512X100SWISDC` × `TT_0P90V_0P90V_M40C`
- `HINP3TCAM64X100SWISDC` × `TT_0P80V_0P80V_25C`
- `HINP3TCAM64X100SWISDC` × `SSGNP_0P99V_0P99V_125C`
- `HINP3TCAM64X100SWISDC` × `FFGNP_0P675V_0P675V_M40C`
- `HINP3TCAM64X100SWISDC` × `SSGNP_0P675V_0P675V_125C`
- `HINP3TCAM64X100SWISDC` × `FFGNP_1P05V_1P05V_25C`
- `HINP3TCAM64X100SWISDC` × `TT_0P90V_0P90V_M40C`
- `HINP3TCAM512X8SWISDC` × `TT_0P80V_0P80V_25C`
- `HINP3TCAM512X8SWISDC` × `SSGNP_0P99V_0P99V_125C`
- `HINP3TCAM512X8SWISDC` × `FFGNP_0P675V_0P675V_M40C`
- `HINP3TCAM512X8SWISDC` × `SSGNP_0P675V_0P675V_125C`
- `HINP3TCAM512X8SWISDC` × `FFGNP_1P05V_1P05V_25C`
- `HINP3TCAM512X8SWISDC` × `TT_0P90V_0P90V_M40C`
- `HINP3TCAM256X32SWISDC` × `TT_0P80V_0P80V_25C`
- `HINP3TCAM256X32SWISDC` × `SSGNP_0P99V_0P99V_125C`
- `HINP3TCAM256X32SWISDC` × `FFGNP_0P675V_0P675V_M40C`
- `HINP3TCAM256X32SWISDC` × `SSGNP_0P675V_0P675V_125C`
- `HINP3TCAM256X32SWISDC` × `FFGNP_1P05V_1P05V_25C`
- `HINP3TCAM256X32SWISDC` × `TT_0P90V_0P90V_M40C`

## Per-key LON (p95)

| key | baseline p95 | residual p95 | Δ |
|---|---|---|---|
| `tselr1_min_period` | 0.311671 | 0.103215 | -0.208457 |
| `tcq` | 0.311673 | 0.103157 | -0.208516 |
| `tcd` | 0.311677 | 0.103172 | -0.208505 |
| `taccess` | 0.311674 | 0.103821 | -0.207853 |
| `leakage_vddc` | 0.524646 | 0.322747 | -0.201899 |
| `read_power_vddc` | 0.36439 | 0.0996063 | -0.264783 |
| `write_power_vddc` | 0.364433 | 0.0984031 | -0.26603 |
| `dynamic_energy_read` | 0.364562 | 0.105295 | -0.259266 |

## Protocol purity (first fold sample)

- held: `HINP3TCAM64X8SWISDC` × `TT_0P80V_0P80V_25C`
- train_n_instances=19 (has_held_inst=False)
- train_n_pvts=39 (has_held_pvt=False)
- n_test_locators=8 (expected = n_keys; all `(I_h,P_h,*)`)

## Notes

- Prior = IDW @ NN-pvt among remaining pvts + delay/power scale (dual-new; not LOI-only / LOP-only).
- Selected = prior + geom-head residual (online `residual_reason=both`).
- Hard gate: **LON-hard** (`p95_sel ≤ p95_idw`). Flag `--require-lon-hard` (default on) / `--no-require-lon-hard`.
- **Not** Op-Geom corner / Miss / Sparse hold-out. **Not** AB stamp.
