# EPC Audit Report — DEMO_P2_missing_green — **PASS**

- Generated: **2026-10-22 00:06:46 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `pvt_missing_fill`
- Job YAML: `/workspace/epc_fixtures/p2/job_missing_fill_green.yaml` (sha256[:16]=53553bbd7191c5ea)
- Source DB: `/workspace/epc_fixtures/p2/A_missing_punched.db` (sha256[:16]=939b78bdef3cbd7f)
- Target process: `DEMO_A` ← `DEMO_A`
- **construct.backend**: `idw_nn` (cfg `idw_nn`)
- **construct.prior**: `idw_nn`
- **construct.apply_on**: `all_extrapolated`
- **fallback_used**: `False`
- **model**: n/a
- Hold-out report (offline): `/workspace/epc_fixtures/algo_holdout_report.md`
- **gates_ok: `True`** — H1 PASS: COUNT=800 axes ok; H2 PASS: 791 seed cells unchanged (max_rel=0.000e+00); H3-hard SKIP (backend=idw_nn) | no constraints
- B.db written: **yes**

## P1 credibility gates (G1–G3)

- **G3 expanded_constraint_count**: `0` (sugar_declared=False)
- **G1 baseline mix**: A_exact=0, style_proxy=0, relative_evals=0
- **G2 spot-check**: PASS — G2 n/a (P2 mode)

## I/O summary

| Axis | Count |
|---|---|
| B instances | 2 |
| B pvts | 8 |
| field_keys | 50 |
| rows written | **800** |
| table N | 5 |
| groups extrapolated | 6 / 16 |

### B instances ∉ A

- (none)

### B pvts ∉ A

- (none)

## Constraints (AND; constraint > style)

## Gates

- require_constraint_satisfaction: `True`
- on_violation: `fail_job`
- Result: **PASS** — H1 PASS: COUNT=800 axes ok; H2 PASS: 791 seed cells unchanged (max_rel=0.000e+00); H3-hard SKIP (backend=idw_nn) | no constraints

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM128X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P90V_0P90V_25C` | missing_filled | True | False | - | operator=pvt_missing_fill provisional=true |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_125C` | missing_filled | True | False | - | operator=pvt_missing_fill provisional=true |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM128X32SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM256X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | missing_filled | True | False | - | operator=pvt_missing_fill provisional=true |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=pvt_missing_fill intact group |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_125C` | missing_filled | True | False | - | operator=pvt_missing_fill provisional=true |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_25C` | missing_filled | True | False | - | operator=pvt_missing_fill provisional=true |
| `HINP3TCAM256X32SWISDC` | `TT_0P90V_0P90V_25C` | missing_filled | True | False | - | operator=pvt_missing_fill provisional=true |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.

## P2 operator

- **mode / operator**: `pvt_missing_fill`
- **create_missing_groups**: `False`
- **holes filled**: 9
- **intact (H2)**: 791
- **H1**: H1 PASS: COUNT=800 axes ok
- **H2**: H2 PASS: 791 seed cells unchanged (max_rel=0.000e+00)
- **H3-hard**: H3-hard SKIP (backend=idw_nn)

### Missing list (sample ≤40)

- `HINP3TCAM128X32SWISDC×SSGNP_0P90V_0P90V_25C×retention_leakage`
- `HINP3TCAM128X32SWISDC×TT_0P80V_0P80V_125C×hold_time_a_scalar`
- `HINP3TCAM128X32SWISDC×TT_0P80V_0P80V_125C×ir_drop_est`
- `HINP3TCAM128X32SWISDC×TT_0P80V_0P80V_125C×taccess`
- `HINP3TCAM256X32SWISDC×FFGNP_1P05V_1P05V_25C×dynamic_energy_write`
- `HINP3TCAM256X32SWISDC×TT_0P80V_0P80V_125C×temp_coeff_delay`
- `HINP3TCAM256X32SWISDC×TT_0P80V_0P80V_25C×tcd`
- `HINP3TCAM256X32SWISDC×TT_0P90V_0P90V_25C×tpd_clk_q`
- `HINP3TCAM256X32SWISDC×TT_0P90V_0P90V_25C×twen_hold`

## H3-hard

- **h3_hard**: `SKIP`
- **backend**: `idw_nn`
- **protocol**: `miss_punched_holes:A_missing_punched.db`
- **p95_selected**: `nan`
- **p95_idw_nn**: `nan`
- **delta**: `None`

