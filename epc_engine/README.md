# epc_engine — EPC A→B characterization construction

YAML-driven **A.db → B.db** library construction for Kai's EPC project.

**Synthetic DEMO only** when used with `/workspace/epc_fixtures/` (not foundry/PDK truth).

## Install deps

```bash
pip install --break-system-packages scikit-learn joblib pyyaml
```

## Reproduce — sample job (residual_gbdt)

```bash
cd /workspace
python3 -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
```

Expected:

- Exit code `0`
- `/workspace/epc_fixtures/B_out.sample.db` with `COUNT(*) = 4950` (9×11×50)
- Audit: `/workspace/epc_fixtures/B_out.sample_audit.md` (records backend / model sha)

### Switch back to baseline

Set in job YAML:

```yaml
construct:
  backend: idw_nn
```

## Offline train + hold-out

```bash
cd /workspace
python3 -m epc_engine.train \
  --source-db /workspace/epc_fixtures/A_ref.db \
  --model-out /workspace/epc_engine/models/residual_gbdt.joblib \
  --report-out /workspace/epc_fixtures/algo_holdout_report.md \
  --seed 42
```

- Trains **only on A_ref**:
  - `models_geom`: leave-one-instance residual labels
  - `models_pvt`: leave-one-pvt residual labels (gated online to keys with prior p95≥1e-4)
- Writes production model (joblib) and LOI/LOP report.
- Online jobs **only read** A.db + YAML + model (no on-the-fly training).
- Default `construct.residual_gbdt.apply_on: all_extrapolated` (residual on every non-seed group).

Hold-out report: `/workspace/epc_fixtures/algo_holdout_report.md`

Hard gates: **P-LOP**, **P-LOI-base**, **P-LOI-reg** (see report).

## Package layout

```
epc_engine/
  __init__.py / __main__.py
  cli.py              # online job orchestration
  job.py              # YAML (+ construct.backend)
  parse.py / source.py / values.py
  construct.py        # facade → backends
  construct_types.py  # ConstructResult / CellMeta
  backends/
    idw_nn.py         # baseline IDW+NN
    residual_gbdt.py  # prior + HistGBDT residual
    features.py
  constraints.py / write_db.py / audit.py
  train.py / train_lib.py
  models/residual_gbdt.joblib
  README.md
```

## Construct backends

| backend | Formula | Notes |
|---|---|---|
| `idw_nn` | geometry IDW (k=4,p=2) + PVT NN + V/T/corner scale | always available |
| `residual_gbdt` | `v_hat = prior(idw_nn) + residual_GBDT(x)` | dual-head geom/pvt; `apply_on: all_extrapolated` (default) or `geom_only`; needs `model_path`; fallback→idw_nn |

Features `x`: `log2(depth/width)`, corner_rank, V/Vddp/T, cell i/j + axis values, **prior_hat**.

Per-key `sklearn.ensemble.HistGradientBoostingRegressor`. Axis keys (`tran_index`/`load_index`) copied from A; never shuffled.

**Online residual policy:** residual is applied for **new geometry** (`instance∉A`). Exact A groups stay `seed_from_A`. Pure PVT-only extrapolation keeps prior (DEMO generative scale already matches baseline).

### Job YAML sketch

```yaml
construct:
  backend: residual_gbdt   # idw_nn | residual_gbdt
  residual_gbdt:
    model_path: "/workspace/epc_engine/models/residual_gbdt.joblib"
    prior: idw_nn
    fallback: idw_nn
```

## Constraints / gates (unchanged)

1. Style/construct first, then constraints (**constraint > style**).
2. `table_upper_bound` under `fail_job`: **verify only** (no clip-then-pass).
3. `relative_delta_vs_source`: force `baseline × (1 + δ/100)`.
4. Gate FAIL + `fail_job` → **do not write B.db** (delete prior at path); FAIL audit; exit `1`.

### Red regression

```bash
bash /workspace/epc_fixtures/run_red_upper_bound.sh
```

Expect `EXIT≠0`, no usable B.db.

## Known limitations

- DEMO synthetic data; **not** physical/PDK calibration.
- Residual helps **geometry** leave-one (LOI); PVT-only leave-out uses prior by policy.
- Only `all_from_source` field policy.
- Hold-out uses core key subset for speed; production model covers all non-axis keys.


## P1 — `relative_improve_vs_source` sugar

Load-time expansion to atomic `relative_delta_vs_source` (improve X% → `delta_pct=-X`).

Default speed/power key tables: `epc_engine/defaults.py` (§3 of the P1 req).

### Reproduce

```bash
cd /workspace
# green residual_gbdt
python3 -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_improve_green.yaml
# green idw_nn
python3 -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_improve_green_idw.yaml
# full suite (green/red + sample + upper-bound red)
bash /workspace/epc_fixtures/p1/run_p1_suite.sh
```

Gates: **G1** baseline auditability · **G2** rewrite spot-check · **G3** `expanded_constraint_count`.

S2: `A_exact` else `style_proxy`; `allow_proxy_baseline:false` → FAIL + no B.db.

## Write precision

`fmt_scalar` uses 12 significant digits (`.12g`) so relative-constraint cells re-read with relative error ≪ `1e-6` (legacy magnitude-tier `:.2f` could hit ~`1e-5`). G2 threshold unchanged.


## P2 modes (reusable operators)

Same CLI; set YAML `mode` (or `operator`) / optional `--mode`:

| mode | Operator |
|---|---|
| `epc_ab` (default) | P0/P1 A→B |
| `corner_fill_geom` | Op-Geom: rectangle corners → interiors |
| `pvt_missing_fill` | Op-Miss: fill missing keys in existing groups |
| `pvt_sparse_fill` | Op-Sparse: sparse PVTs → target list |

```bash
bash /workspace/epc_fixtures/p2/run_p2_suite.sh
```

Hard gates H1 (completeness) / H2 (seed unchanged) / H3 (DEMO accuracy report).
`fail_job` still refuses to leave a usable output DB.
