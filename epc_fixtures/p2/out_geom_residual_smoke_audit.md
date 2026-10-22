# EPC Audit Report — DEMO_P2_geom_residual_smoke — **PASS**

- Generated: **2026-10-21 23:46:00 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `corner_fill_geom`
- Job YAML: `/tmp/epc_geom_res.yaml` (sha256[:16]=2a072be1c7251062)
- Source DB: `/workspace/epc_fixtures/A_ref.db` (sha256[:16]=0b1e643c4e951cbb)
- Target process: `DEMO_A` ← `DEMO_A`
- **construct.backend**: `residual_gbdt` (cfg `residual_gbdt`)
- **construct.prior**: `idw_nn`
- **construct.apply_on**: `all_extrapolated`
- **fallback_used**: `False`
- **model**: `/workspace/epc_engine/models/residual_gbdt.joblib` (sha256[:16]=bd6ecde2f27e622b)
- Hold-out report (offline): `/workspace/epc_fixtures/algo_holdout_report.md`
- **gates_ok: `True`** — H1 PASS: COUNT=2000 axes ok; H2 PASS: 1600 seed cells unchanged (max_rel=0.000e+00) | no constraints
- B.db written: **yes**

## P1 credibility gates (G1–G3)

- **G3 expanded_constraint_count**: `0` (sugar_declared=False)
- **G1 baseline mix**: A_exact=0, style_proxy=0, relative_evals=0
- **G2 spot-check**: PASS — G2 n/a (P2 mode)

## I/O summary

| Axis | Count |
|---|---|
| B instances | 5 |
| B pvts | 8 |
| field_keys | 50 |
| rows written | **2000** |
| table N | 5 |
| groups extrapolated | 8 / 40 |

### B instances ∉ A

- (none)

### B pvts ∉ A

- (none)

## Constraints (AND; constraint > style)

## Gates

- require_constraint_satisfaction: `True`
- on_violation: `fail_job`
- Result: **PASS** — H1 PASS: COUNT=2000 axes ok; H2 PASS: 1600 seed cells unchanged (max_rel=0.000e+00) | no constraints

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P90V_0P90V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM256X32SWISDC` | `TT_0P90V_0P90V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib); operator=corner_fill_geom |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `TT_0P80V_0P80V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X100SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `TT_0P80V_0P80V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM512X8SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `TT_0P80V_0P80V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X100SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_125C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |
| `HINP3TCAM64X8SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=corner_fill_geom exact seed copy |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.

## P2 operator

- **mode / operator**: `corner_fill_geom`
- **seeds**: `HINP3TCAM64X8SWISDC`, `HINP3TCAM64X100SWISDC`, `HINP3TCAM512X8SWISDC`, `HINP3TCAM512X100SWISDC`
- **targets**: `HINP3TCAM256X32SWISDC`
- **backend**: `residual_gbdt`
- **H1**: H1 PASS: COUNT=2000 axes ok
- **H2**: H2 PASS: 1600 seed cells unchanged (max_rel=0.000e+00)

