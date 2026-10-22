# EPC Audit Report — DEMO_P2_sparse_green — **PASS**

- Generated: **2026-10-22 00:10:18 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `pvt_sparse_fill`
- Job YAML: `/workspace/epc_fixtures/p2/job_sparse_fill_green.yaml` (sha256[:16]=d7b2f91251983bae)
- Source DB: `/workspace/epc_fixtures/p2/A_sparse.db` (sha256[:16]=50d108410138937d)
- Target process: `DEMO_A` ← `DEMO_A`
- **construct.backend**: `residual_gbdt` (cfg `residual_gbdt`)
- **construct.prior**: `idw_nn`
- **construct.apply_on**: `all_extrapolated`
- **fallback_used**: `False`
- **model**: `/workspace/epc_engine/models/residual_gbdt.joblib` (sha256[:16]=bd6ecde2f27e622b)
- Hold-out report (offline): `/workspace/epc_fixtures/algo_holdout_report.md`
- **gates_ok: `True`** — H1 PASS: COUNT=800 axes ok; H2 PASS: 400 seed cells unchanged (max_rel=0.000e+00); H3-hard PASS: p95_selected=0.122253 ≤ p95_idw_nn=0.122253 (delta=0) protocol=sparse_lop:HINP3TCAM128X32SWISDC:FFGNP_0P675V_0P675V_M40C | no constraints
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
| groups extrapolated | 8 / 16 |

### B instances ∉ A

- (none)

### B pvts ∉ A

- `SSGNP_0P675V_0P675V_125C`
- `FFGNP_1P05V_1P05V_25C`
- `TT_0P80V_0P80V_125C`
- `SSGNP_0P90V_0P90V_25C`

## Constraints (AND; constraint > style)

## Gates

- require_constraint_satisfaction: `True`
- on_violation: `fail_job`
- Result: **PASS** — H1 PASS: COUNT=800 axes ok; H2 PASS: 400 seed cells unchanged (max_rel=0.000e+00); H3-hard PASS: p95_selected=0.122253 ≤ p95_idw_nn=0.122253 (delta=0) protocol=sparse_lop:HINP3TCAM128X32SWISDC:FFGNP_0P675V_0P675V_M40C | no constraints

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM128X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_25C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P90V_0P90V_25C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_125C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P80V_0P80V_25C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM128X32SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM256X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P90V_0P90V_25C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P90V_0P90V_25C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=SSGNP_0P99V_0P99V_125C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_125C` | pvt_extrapolated | True | True | pvt | pvt∉A; NN=TT_0P80V_0P80V_25C; residual_applied=true reason=pvt head=pvt(+residual_gbdt.joblib); operator=pvt_sparse_fill |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |
| `HINP3TCAM256X32SWISDC` | `TT_0P90V_0P90V_25C` | seed_from_source | False | False | - | operator=pvt_sparse_fill seed pvt copy |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.

## P2 operator

- **mode / operator**: `pvt_sparse_fill`
- **allow_weak_seed**: `False`
- **min_seed_pvts**: `3`
- **H1**: H1 PASS: COUNT=800 axes ok
- **H2**: H2 PASS: 400 seed cells unchanged (max_rel=0.000e+00)
- **H3-hard**: H3-hard PASS: p95_selected=0.122253 ≤ p95_idw_nn=0.122253 (delta=0) protocol=sparse_lop:HINP3TCAM128X32SWISDC:FFGNP_0P675V_0P675V_M40C

### Seed PVT counts

- `HINP3TCAM128X32SWISDC`: 4 seeds
- `HINP3TCAM256X32SWISDC`: 4 seeds

## H3-hard

- **h3_hard**: `PASS`
- **backend**: `residual_gbdt`
- **protocol**: `sparse_lop:HINP3TCAM128X32SWISDC:FFGNP_0P675V_0P675V_M40C`
- **p95_selected**: `0.12225266717192328`
- **p95_idw_nn**: `0.12225266717192328`
- **delta**: `0.0`

