# EPC Audit Report — DEMO_A_scale20x_to_DEMO_B — **PASS**

- Generated: **2026-11-24 23:03:03 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `epc_ab`
- Job YAML: `D:\SramDbEpc\epc-ai-char-main\epc-ai-char-main\epc_fixtures\scale\epc_job.scale_20x.yaml` (sha256[:16]=aed37b424e02b592)
- Source DB: `D:\SramDbEpc\epc-ai-char-main\epc-ai-char-main\epc_fixtures\scale\A_scale_20x.db` (sha256[:16]=385757c34af78afc)
- Target process: `DEMO_B` ← `DEMO_A`
- **construct.backend**: `residual_gbdt` (cfg `residual_gbdt`)
- **construct.prior**: `idw_nn`
- **construct.apply_on**: `all_extrapolated`
- **fallback_used**: `False`
- **model**: `D:\SramDbEpc\epc-ai-char-main\epc-ai-char-main\epc_engine\models\residual_gbdt.joblib` (sha256[:16]=bd6ecde2f27e622b)
- Hold-out report (offline): `D:\SramDbEpc\epc-ai-char-main\epc-ai-char-main\epc_fixtures\algo_holdout_report.md`
- **gates_ok: `True`** — all constraints PASS | G1 PASS: all relative baselines auditable | G2 PASS: B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16
- B.db written: **yes**

## P1 credibility gates (G1–G3)

- **G3 expanded_constraint_count**: `0` (sugar_declared=False)
- **G1 baseline mix**: A_exact=1, style_proxy=0, relative_evals=1
- **G2 spot-check**: PASS — G2 PASS: B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16

| family | instance | pvt | key | δ% | baseline_source | detail | ok |
|---|---|---|---|---|---|---|---|
| - | `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | `tcq` | -4.0 | A_exact | B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16 | True |

## I/O summary

| Axis | Count |
|---|---|
| B instances | 50 |
| B pvts | 11 |
| field_keys | 50 |
| rows written | **27500** |
| table N | 5 |
| groups extrapolated | 150 / 550 |

### B instances ∉ A

- (none)

### B pvts ∉ A

- `SSGNP_1P05V_1P05V_M40C`
- `FFGNP_0P75V_0P75V_85C`
- `TT_1P05V_1P05V_M40C`

## Constraints (AND; constraint > style)

### [PASS] #0 `table_upper_bound`

- Locator: `HINP3TCAM512X100SWISDC × SSGNP_0P99V_0P99V_125C × tselr1_min_period`
- Applied: True
- Detail: op<= 1500.0; mode=verify_only; before_max=1387.9; after_max=1387.9; cells_clipped=0/25
- Metrics: `{'bound': 1500.0, 'before_max': 1387.9, 'after_max': 1387.9, 'cells_clipped': 0, 'n_cells': 25, 'mode': 'verify_only'}`

### [PASS] #1 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × TT_0P80V_0P80V_25C × tcq`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=140 → 134.4
- baseline_source: `A_exact` baseline0=`140.0` proxy_ref=`` family=`None`

## AB-hard (epc_ab hold-out stamp)

- **ab_hard**: `PASS`
- **ab_hard_protocol**: `loi_v0+lop_v0`
- **backend**: `residual_gbdt`
- **p95_selected_loi**: `0.102257`
- **p95_idw_loi**: `0.31168`
- **p95_selected_lop**: `5.22059e-05`
- **p95_idw_lop**: `5.2333e-05`
- **stamp_sha16**: `bd6ecde2f27e622b`
- **stamp_generated**: `2026-10-22T14:32:34+08:00`

## Gates

- require_constraint_satisfaction: `True`
- on_violation: `fail_job`
- Result: **PASS** — all constraints PASS | G1 PASS: all relative baselines auditable | G2 PASS: B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM128X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X4SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X4SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X4SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X4SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM128X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM128X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM160X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM160X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM192X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM192X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X4SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X4SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X4SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X4SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM256X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM256X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM320X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM320X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM384X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM384X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM448X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM448X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
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
| `HINP3TCAM512X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X4SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X4SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X4SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X4SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM512X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM512X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM64X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM64X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
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
| `HINP3TCAM96X16SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X16SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X16SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X16SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X48SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X48SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X64SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X64SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X80SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=FFGNP_0P80V_0P80V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X80SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |
| `HINP3TCAM96X80SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | seed_from_A | exact (instance,pvt) in A; residual_applied=false (seed_from_A) |
| `HINP3TCAM96X80SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_M40C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib) |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.
- AB-hard: non-idw epc_ab requires offline LOI/LOP stamp (`≤` idw); missing/stale/FAIL → no B.db (decoupled from P2 H3-hard).
