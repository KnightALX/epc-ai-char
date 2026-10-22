# LON（双新 leave-pair）自测

| 项 | 内容 |
|---|---|
| 需求 | `/workspace/EPC_双新_holdout切片_需求_v0.md` v0 |
| Kai 拍板 | Q1=A（30 折笛卡尔）；Q2=A（报表 Must + 硬 EXIT Should，默认可关；**无 stamp**）；Q3=`≤` |
| 日期 | 2026-10-22（Asia/Shanghai） |
| 状态 | **开发自测**（验收另派，本页勿当签收） |

## 钉死行为

- 折 `(I_h, P_h)`：train 去掉整行 `instance=I_h` + 整列 `pvt=P_h`；**只评**交叉点 `(I_h,P_h,*)`
- 禁止把 LOI / LOP 点并入 LON p95
- 指标：cell 相对误差；prior=`idw_nn`（双新 NN-pvt+scale）；selected=`residual_gbdt` geom head（`residual_reason=both`）
- 比较：`p95_sel ≤ p95_idw`；协议 id=`lon_v0`
- 硬 EXIT：默认开（`--require-lon-hard`）；`--no-require-lon-hard` 可关
- **本轮不要** `*.lon_hard.json` / 不改 AB stamp；不调 `eval_h3` / `h3_hard`

## 一键 suite

```bash
bash /workspace/epc_fixtures/run_lon_holdout_suite.sh
```

建议验收报告路径：`/workspace/epc_fixtures/双新_holdout切片_验收报告.md`（独立验收写，开发不自签）。

## 绿 / 红复现

### 门禁逻辑（快）

```bash
PYTHONPATH=/workspace python3 - <<'PY'
from epc_engine.lon_holdout import evaluate_lon_hard_gates
ok, g, _ = evaluate_lon_hard_gates(0.1, 0.1)   # equality → PASS
assert ok
ok, g, _ = evaluate_lon_hard_gates(0.2, 0.1)   # sel > idw → FAIL
assert not ok
print("LON gate logic OK")
PY
```

### 全量 LON（~1–2 min；30 折）

```bash
PYTHONPATH=/workspace python3 -m epc_engine.lon_holdout \
  --source-db /workspace/epc_fixtures/A_ref.db \
  --report-out /workspace/epc_fixtures/algo_holdout_dual_new_report.md \
  --require-lon-hard
# 期望：EXIT 0；LON-hard PASS；报表含两路 p95
```

开发侧绿路径（2026-10-22）：

| 路 | p95 |
|---|---|
| **selected** (`residual_gbdt`) | **0.104781** |
| **idw_nn** prior | **0.311677** |
| n_cells / folds | 3120 / 30 |

### 红（mock）

`evaluate_lon_hard_gates(0.99, 0.10)` → FAIL；CLI 在 `--require-lon-hard` 下 EXIT 3。

### 关硬门

```bash
PYTHONPATH=/workspace python3 -m epc_engine.lon_holdout --no-require-lon-hard
# 即使 LON-hard FAIL 也 EXIT 0（仍写报表）
```

## 改动文件（开发）

- `epc_engine/lon_holdout.py`（新：协议 / 门禁 / 报表 / CLI）
- `epc_fixtures/run_lon_holdout_suite.sh`（新）
- `epc_fixtures/algo_holdout_dual_new_report.md`（旁路报表）
- `epc_fixtures/algo_holdout_report.md`（互链 Dual-new 节）
- `epc_fixtures/LON_自测.md`（本页）

**未改**：`ab_hard.py` stamp 语义、`modes/h3_hard.py`、`p2/eval_h3.py`、`run_p2_suite.sh`、`run_ab_hard_suite.sh`、GUI、在线 job 内重跑 30 折。

## 与 AB / H3 关系

```text
LOI / LOP  → AB-hard（已有 stamp）
LON       → 本切片（报表 + 可选硬 EXIT；无 stamp）
Op-Geom H3 → 另一条线，互不冒充
```
