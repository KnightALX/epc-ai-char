# EPC Audit Report — AB_hard_idw_skip — **PASS**

- Generated: **2026-10-22 22:28:51 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `epc_ab`
- Job YAML: `/workspace/epc_fixtures/ab_hard/epc_job.ab_hard_idw.yaml` (sha256[:16]=cc998e45dd952822)
- Source DB: `/workspace/epc_fixtures/A_ref.db` (sha256[:16]=0b1e643c4e951cbb)
- Target process: `DEMO_B` ← `DEMO_A`
- **construct.backend**: `idw_nn` (cfg `idw_nn`)
- **construct.prior**: `idw_nn`
- **construct.apply_on**: `all_extrapolated`
- **fallback_used**: `False`
- **model**: n/a
- Hold-out report (offline): `/workspace/epc_fixtures/algo_holdout_report.md`
- **gates_ok: `True`** — all constraints PASS | G3 PASS: expanded_constraint_count=16 | G1 PASS: all relative baselines auditable | G2 PASS: B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16; B0=0.0095 baseline0=0.01 factor=0.950000 |B/base-factor|=0.000e+00
- B.db written: **yes**

## P1 credibility gates (G1–G3)

- **G3 expanded_constraint_count**: `16` (sugar_declared=True)
- **G1 baseline mix**: A_exact=16, style_proxy=0, relative_evals=16
- **G2 spot-check**: PASS — G2 PASS: B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16; B0=0.0095 baseline0=0.01 factor=0.950000 |B/base-factor|=0.000e+00

| family | instance | pvt | key | δ% | baseline_source | detail | ok |
|---|---|---|---|---|---|---|---|
| speed | `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | `tcq` | -4.0 | A_exact | B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16 | True |
| power | `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | `leakage_vddc` | -5.0 | A_exact | B0=0.0095 baseline0=0.01 factor=0.950000 |B/base-factor|=0.000e+00 | True |

## I/O summary

| Axis | Count |
|---|---|
| B instances | 9 |
| B pvts | 11 |
| field_keys | 50 |
| rows written | **4950** |
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

### [PASS] #0 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × TT_0P80V_0P80V_25C × tcq`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=140 → 134.4
- baseline_source: `A_exact` baseline0=`140.0` proxy_ref=`` family=`speed`

### [PASS] #0 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × SSGNP_0P99V_0P99V_125C × tcq`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=167.27 → 160.579
- baseline_source: `A_exact` baseline0=`167.27` proxy_ref=`` family=`speed`

### [PASS] #0 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × TT_0P80V_0P80V_25C × tcq`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=324.23 → 311.261
- baseline_source: `A_exact` baseline0=`324.23` proxy_ref=`` family=`speed`

### [PASS] #0 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × SSGNP_0P99V_0P99V_125C × tcq`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=387.37 → 371.875
- baseline_source: `A_exact` baseline0=`387.37` proxy_ref=`` family=`speed`

### [PASS] #1 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × TT_0P80V_0P80V_25C × taccess`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=180 → 172.8
- baseline_source: `A_exact` baseline0=`180.0` proxy_ref=`` family=`speed`

### [PASS] #1 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × SSGNP_0P99V_0P99V_125C × taccess`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=215.06 → 206.458
- baseline_source: `A_exact` baseline0=`215.06` proxy_ref=`` family=`speed`

### [PASS] #1 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × TT_0P80V_0P80V_25C × taccess`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=416.86 → 400.186
- baseline_source: `A_exact` baseline0=`416.86` proxy_ref=`` family=`speed`

### [PASS] #1 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × SSGNP_0P99V_0P99V_125C × taccess`
- Applied: True
- Detail: delta_pct=-4.0 → ×0.9600; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=498.05 → 478.128
- baseline_source: `A_exact` baseline0=`498.05` proxy_ref=`` family=`speed`

### [PASS] #2 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × TT_0P80V_0P80V_25C × leakage_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=0.01 → 0.0095
- baseline_source: `A_exact` baseline0=`0.01` proxy_ref=`` family=`power`

### [PASS] #2 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × SSGNP_0P99V_0P99V_125C × leakage_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=0.08575 → 0.0814625
- baseline_source: `A_exact` baseline0=`0.08575` proxy_ref=`` family=`power`

### [PASS] #2 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × TT_0P80V_0P80V_25C × leakage_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=0.08424 → 0.080028
- baseline_source: `A_exact` baseline0=`0.08424` proxy_ref=`` family=`power`

### [PASS] #2 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × SSGNP_0P99V_0P99V_125C × leakage_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=0.72244 → 0.686318
- baseline_source: `A_exact` baseline0=`0.72244` proxy_ref=`` family=`power`

### [PASS] #3 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × TT_0P80V_0P80V_25C × read_power_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=0.5 → 0.475
- baseline_source: `A_exact` baseline0=`0.5` proxy_ref=`` family=`power`

### [PASS] #3 `relative_delta_vs_source`

- Locator: `HINP3TCAM64X8SWISDC × SSGNP_0P99V_0P99V_125C × read_power_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=0.8806 → 0.83657
- baseline_source: `A_exact` baseline0=`0.8806` proxy_ref=`` family=`power`

### [PASS] #3 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × TT_0P80V_0P80V_25C × read_power_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=3.1076 → 2.95222
- baseline_source: `A_exact` baseline0=`3.1076` proxy_ref=`` family=`power`

### [PASS] #3 `relative_delta_vs_source`

- Locator: `HINP3TCAM512X100SWISDC × SSGNP_0P99V_0P99V_125C × read_power_vddc`
- Applied: True
- Detail: delta_pct=-5.0 → ×0.9500; baseline_source=A_exact; max_rel_err=0.000e+00; sample baseline0=5.4728 → 5.19916
- baseline_source: `A_exact` baseline0=`5.4728` proxy_ref=`` family=`power`

## AB-hard (epc_ab hold-out stamp)

- **ab_hard**: `SKIP`
- **ab_hard_protocol**: `loi_v0+lop_v0`
- **backend**: `idw_nn`
- **p95_selected_loi**: `None`
- **p95_idw_loi**: `None`
- **p95_selected_lop**: `None`
- **p95_idw_lop**: `None`
- **stamp_sha16**: `None`
- **stamp_generated**: `None`
- **reason**: `backend_idw_nn`

## Gates

- require_constraint_satisfaction: `True`
- on_violation: `fail_job`
- Result: **PASS** — all constraints PASS | G3 PASS: expanded_constraint_count=16 | G1 PASS: all relative baselines auditable | G2 PASS: B0=134.4 baseline0=140 factor=0.960000 |B/base-factor|=1.110e-16; B0=0.0095 baseline0=0.01 factor=0.950000 |B/base-factor|=0.000e+00

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | False | - | pvt∉A; NN=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM128X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM128X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=TT_0P90V_0P90V_M40C |
| `HINP3TCAM128X64SWISDC` | `FFGNP_0P75V_0P75V_85C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM128X64SWISDC` | `FFGNP_0P80V_0P80V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `FFGNP_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P675V_0P675V_M40C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P75V_0P75V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `SSGNP_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM128X64SWISDC` | `TT_0P675V_0P675V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `TT_0P90V_0P90V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM128X64SWISDC` | `TT_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=TT_0P90V_0P90V_M40C |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | False | - | pvt∉A; NN=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM256X32SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM256X32SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=TT_0P90V_0P90V_M40C |
| `HINP3TCAM256X48SWISDC` | `FFGNP_0P75V_0P75V_85C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM256X48SWISDC` | `FFGNP_0P80V_0P80V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `FFGNP_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `SSGNP_0P675V_0P675V_M40C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `SSGNP_0P75V_0P75V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `SSGNP_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM256X48SWISDC` | `TT_0P675V_0P675V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `TT_0P90V_0P90V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM256X48SWISDC` | `TT_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=TT_0P90V_0P90V_M40C |
| `HINP3TCAM384X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM384X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM384X100SWISDC` | `TT_0P675V_0P675V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `TT_0P80V_0P80V_25C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `TT_0P90V_0P90V_125C` | config_extrapolated | True | False | - | instance∉A; geometry IDW at target pvt |
| `HINP3TCAM384X100SWISDC` | `TT_1P05V_1P05V_M40C` | config_extrapolated | True | False | - | instance∉A and pvt∉A; geom IDW @ NN pvt=TT_0P90V_0P90V_M40C |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | False | - | pvt∉A; NN=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM512X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=TT_0P90V_0P90V_M40C |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | False | - | pvt∉A; NN=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM512X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM512X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=TT_0P90V_0P90V_M40C |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | False | - | pvt∉A; NN=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM64X100SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X100SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=TT_0P90V_0P90V_M40C |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P75V_0P75V_85C` | pvt_extrapolated | True | False | - | pvt∉A; NN=FFGNP_0P80V_0P80V_125C |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `FFGNP_1P05V_1P05V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P675V_0P675V_M40C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P75V_0P75V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `SSGNP_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=SSGNP_0P99V_0P99V_M40C |
| `HINP3TCAM64X8SWISDC` | `TT_0P675V_0P675V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `TT_0P90V_0P90V_125C` | seed_from_A | False | False | - | exact (instance,pvt) in A |
| `HINP3TCAM64X8SWISDC` | `TT_1P05V_1P05V_M40C` | pvt_extrapolated | True | False | - | pvt∉A; NN=TT_0P90V_0P90V_M40C |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.
- AB-hard: non-idw epc_ab requires offline LOI/LOP stamp (`≤` idw); missing/stale/FAIL → no B.db (decoupled from P2 H3-hard).
