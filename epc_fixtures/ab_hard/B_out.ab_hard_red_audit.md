# EPC Audit Report — AB_hard_online_red — **FAIL**

- Generated: **2026-10-22 22:28:50 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `epc_ab`
- Job YAML: `/workspace/epc_fixtures/ab_hard/epc_job.ab_hard_red.yaml` (sha256[:16]=55501a0711b102b4)
- Source DB: `/workspace/epc_fixtures/A_ref.db` (sha256[:16]=0b1e643c4e951cbb)
- Target process: `DEMO_B` ← `DEMO_A`
- **construct.backend**: `residual_gbdt` (cfg `residual_gbdt`)
- **construct.prior**: `idw_nn`
- **construct.apply_on**: `all_extrapolated`
- **fallback_used**: `False`
- **model**: `/workspace/epc_engine/models/residual_gbdt.joblib` (sha256[:16]=bd6ecde2f27e622b)
- Hold-out report (offline): `/workspace/epc_fixtures/algo_holdout_report.md`
- **gates_ok: `False`** — ab_hard: FAIL (missing_stamp) — non-idw backend requires sidecar /workspace/epc_engine/models/residual_gbdt.joblib.ab_hard.json or bundle ab_hard_stamp
- B.db written: **no (FAIL / skipped)**

## P1 credibility gates (G1–G3)

- **G3 expanded_constraint_count**: `0` (sugar_declared=False)
- **G1 baseline mix**: A_exact=0, style_proxy=0, relative_evals=0
- **G2 spot-check**: FAIL — G2 skipped (ab_hard FAIL, no B.db)

## I/O summary

| Axis | Count |
|---|---|
| B instances | 9 |
| B pvts | 11 |
| field_keys | 50 |
| rows written | **0** |
| table N | 5 |
| groups extrapolated | 51 / 99 |

### B instances ∉ A

- `HINP3TCAM128X64SWISDC`
- `HINP3TCAM256X48SWISDC`
- `HINP3TCAM384X100SWISDC`

### B pvts ∉ A

- `SSGNP_1P05V_1P05V_M40C`
- `FFGNP_0P75V_0P75V_85C`
- `TT_1P05V_1P05V_M40C`

## Constraints (AND; constraint > style)

## AB-hard (epc_ab hold-out stamp)

- **ab_hard**: `FAIL`
- **ab_hard_protocol**: `loi_v0+lop_v0`
- **backend**: `residual_gbdt`
- **p95_selected_loi**: `None`
- **p95_idw_loi**: `None`
- **p95_selected_lop**: `None`
- **p95_idw_lop**: `None`
- **stamp_sha16**: `None`
- **stamp_generated**: `None`
- **reason**: `missing_stamp`

## Gates

- require_constraint_satisfaction: `True`
- on_violation: `fail_job`
- Result: **FAIL** — ab_hard: FAIL (missing_stamp) — non-idw backend requires sidecar /workspace/epc_engine/models/residual_gbdt.joblib.ab_hard.json or bundle ab_hard_stamp

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `TT_0P675V_0P675V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `TT_0P90V_0P90V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `TT_1P05V_1P05V_M40C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=TT_0P90V_0P90V_M40C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `TT_0P675V_0P675V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `TT_0P90V_0P90V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM256X48SWISDC` | `TT_1P05V_1P05V_M40C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=TT_0P90V_0P90V_M40C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `TT_0P675V_0P675V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `TT_0P90V_0P90V_125C` | config_extrapolated | True | True | geom | instance∉A; geometry IDW at target pvt; residual_applied=true reason=geom head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `TT_1P05V_1P05V_M40C` | config_extrapolated | True | True | both | instance∉A and pvt∉A; geom IDW @ NN pvt=TT_0P90V_0P90V_M40C; residual_applied=true reason=both head=geom(+residual_gbdt.joblib) |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.
- AB-hard: non-idw epc_ab requires offline LOI/LOP stamp (`≤` idw); missing/stale/FAIL → no B.db (decoupled from P2 H3-hard).
