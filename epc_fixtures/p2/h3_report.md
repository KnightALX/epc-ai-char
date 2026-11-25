# P2 H3 DEMO accuracy report

Synthetic fixtures only — not foundry/PDK truth.

H3-hard: when backend ≠ idw_nn, require `p95_selected ≤ p95_idw_nn` (equality allowed).
Geom certified on idw_nn; residual hard status reported separately as `h3_hard_residual`.

| operator | ok | p95_selected | p95_idw_nn | delta | h3_hard | extra |
|---|---|---|---|---|---|---|
| `corner_fill_geom` | **PASS** | 0.0076663859962657925 | 0.0076663859962657925 | 0.0 | `SKIP` | h3_hard_residual=FAIL, p95_residual=0.02631870555117344, delta_residual=0.018652319554907648, n_err=832, detail=holdout=HINP3TCAM256X32SWISDC pvts=8 keys=8, backend_certified=idw_nn |
| `pvt_missing_fill` | **PASS** | 1.7652830908536708e-05 | 1.7652830908536708e-05 | 0.0 | `SKIP` | p95_holes=1.7652830908536708e-05, n_err=105, n_holes=9, threshold=0.15, backend_certified=idw_nn |
| `pvt_sparse_fill` | **PASS** | 0.13928002125398511 | 0.13928002125398511 | 0.0 | `PASS` | p95_residual=0.13928002125398511, hold_pvt=FFGNP_0P675V_0P675V_M40C, n_err=104, backend_certified=residual_gbdt |

**Overall H3: PASS**

