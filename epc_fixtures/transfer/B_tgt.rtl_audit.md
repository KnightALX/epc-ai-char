# EPC Audit Report — DEMO_transfer_ab_residual_tl_v0 — **PASS**

- Generated: **2026-10-22 22:28:19 CST** (Asia/Shanghai)
- Engine: `epc_engine`
- **mode / operator**: `transfer_ab`
- Job YAML: `/workspace/epc_fixtures/transfer/epc_job.transfer_rtl.yaml` (sha256[:16]=afb8266891b2f35f)
- Source DB: `/workspace/epc_fixtures/transfer/A_src.db` (sha256[:16]=0b1e643c4e951cbb)
- Target process: `DEMO_TGT` ← `DEMO_SRC`
- **construct.backend**: `residual_tl` (cfg `residual_tl`)
- **construct.prior**: `linear_tr`
- **construct.apply_on**: `transfer_seed_fit`
- **fallback_used**: `False`
- **model**: n/a
- Hold-out report (offline): `/workspace/epc_fixtures/algo_holdout_report.md`
- **gates_ok: `True`** — no constraints | transfer backend=residual_tl protocol=transfer_holdout_v0
- B.db written: **yes**

## P1 credibility gates (G1–G3)

- **G3 expanded_constraint_count**: `0` (sugar_declared=False)
- **G1 baseline mix**: A_exact=0, style_proxy=0, relative_evals=0
- **G2 spot-check**: PASS — G2 SKIP: transfer_ab (no relative sugar required)

## I/O summary

| Axis | Count |
|---|---|
| B instances | 8 |
| B pvts | 12 |
| field_keys | 50 |
| rows written | **4800** |
| table N | 5 |
| groups extrapolated | 58 / 96 |

### B instances ∉ A

- (none)

### B pvts ∉ A

- (none)

## Constraints (AND; constraint > style)

## AB-hard (epc_ab hold-out stamp)

- **ab_hard**: `None`
- **ab_hard_protocol**: `None`
- **backend**: `residual_tl`
- **p95_selected_loi**: `None`
- **p95_idw_loi**: `None`
- **p95_selected_lop**: `None`
- **p95_idw_lop**: `None`
- **stamp_sha16**: `None`
- **stamp_generated**: `None`
- **reason**: `transfer_ab: no AB/LON/transfer stamp this round`

## Gates

- require_constraint_satisfaction: `False`
- on_violation: `fail_job`
- Result: **PASS** — no constraints | transfer backend=residual_tl protocol=transfer_holdout_v0

## Group status sample

| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |
|---|---|---|---|---|---|---|
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P80V_0P80V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `TT_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X32SWISDC` | `TT_0P90V_0P90V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P675V_0P675V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P80V_0P80V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `FFGNP_1P05V_1P05V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `SSGNP_0P675V_0P675V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `SSGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `TT_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X72SWISDC` | `TT_0P90V_0P90V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P675V_0P675V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P80V_0P80V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `FFGNP_1P05V_1P05V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `SSGNP_0P675V_0P675V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `TT_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM128X8SWISDC` | `TT_0P90V_0P90V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P80V_0P80V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM256X32SWISDC` | `TT_0P90V_0P90V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P80V_0P80V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X100SWISDC` | `TT_0P90V_0P90V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P675V_0P675V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P80V_0P80V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM512X8SWISDC` | `TT_0P90V_0P90V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P80V_0P80V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P80V_0P80V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_0P99V_0P99V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X100SWISDC` | `TT_0P90V_0P90V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P675V_0P675V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P675V_0P675V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P80V_0P80V_125C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P80V_0P80V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P80V_0P80V_M40C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P90V_0P90V_25C` | transfer_pred | True | True | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_0P99V_0P99V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `FFGNP_1P05V_1P05V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P675V_0P675V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `SSGNP_0P99V_0P99V_125C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `TT_0P80V_0P80V_25C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |
| `HINP3TCAM64X8SWISDC` | `TT_0P90V_0P90V_M40C` | seed_from_tgt | False | False | transfer_rtl | backend=residual_tl; protocol=transfer_holdout_v0 |

## Notes

- Synthetic DEMO fixtures are not foundry/PDK truth.
- P1: `relative_improve_vs_source` expands to atomic `relative_delta_vs_source` (improve X% → delta_pct=-X).
- S2 baseline: A_exact else style_proxy (pre-constraint construct); `allow_proxy_baseline:false` fails the job if proxy needed.
- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.
- G1 auditability / G2 rewrite spot-check / G3 expansion count.
- AB-hard: non-idw epc_ab requires offline LOI/LOP stamp (`≤` idw); missing/stale/FAIL → no B.db (decoupled from P2 H3-hard).
