# AB-hard（epc_ab / algo_holdout 硬门禁）自测

| 项 | 内容 |
|---|---|
| 需求 | `/workspace/EPC_加固_epc_ab_holdout硬门禁_需求_v0.md` v0 |
| Kai 拍板 | Q1=A（离线硬 + 在线只读 stamp）；Q2=比较符 `≤` |
| 日期 | 2026-10-22（Asia/Shanghai） |
| 状态 | **开发自测**（验收另派，本页勿当签收） |

## 钉死行为

- 离线：非 idw → `AB-hard-LOI` / `AB-hard-LOP` 均 `p95_sel ≤ p95_idw_nn`；FAIL → EXIT≠0，**不晋升**生产 `residual_gbdt.joblib`
- 在线 `epc_ab`：**不**重跑 LOI/LOP；读 `*.ab_hard.json`（或 bundle `ab_hard_stamp`）；缺/stale/FAIL → EXIT≠0、**不写 B.db**
- `idw_nn` → `ab_hard: SKIP`
- 与 P2 `modes/h3_hard.py` / `run_p2_suite` / `eval_h3.py` **解耦**
- 禁止因精度劣于 idw 而静默 fallback 掩盖 FAIL（模型缺失 fallback 仍允许并 audit）

## 一键 suite

```bash
bash /workspace/epc_fixtures/run_ab_hard_suite.sh
```

建议验收报告路径：`/workspace/epc_fixtures/加固_epc_ab_holdout硬门禁_验收报告.md`（由独立验收写，开发不自签）。

## 绿 / 红复现

### 离线门禁逻辑（快；不跑全量 fold）

```bash
PYTHONPATH=/workspace python3 - <<'PY'
from epc_engine.ab_hard import evaluate_ab_hard_gates
# U3 equality → PASS
ok, g, _ = evaluate_ab_hard_gates(0.1, 0.1, 0.05, 0.05)
assert ok
# U2 sel > idw → FAIL
ok, g, _ = evaluate_ab_hard_gates(0.2, 0.1, 0.05, 0.05)
assert not ok and not g["AB-hard-LOI"]
print("offline gate logic OK")
PY
```

### 离线全量 holdout（慢；可选）

```bash
PYTHONPATH=/workspace python3 -m epc_engine.train \
  --source-db /workspace/epc_fixtures/A_ref.db \
  --skip-train \
  --report-out /workspace/epc_fixtures/algo_holdout_report.md
# 期望：AB-hard-LOI/LOP PASS，EXIT 0；写出 stamp
```

FAIL 时（mock / 真劣化）：EXIT 3，且 `--require-ab-hard`（默认）不覆盖生产 joblib。

### 在线绿

```bash
# 确保 stamp 与模型 sha 一致（suite 会自动 seed）
PYTHONPATH=/workspace python3 -m epc_engine \
  /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_green.yaml
# EXIT 0；B.db 存在；audit `ab_hard: PASS`
```

### 在线红（坏 stamp）

```bash
# 将 residual_gbdt.joblib.ab_hard.json 改为 ab_hard=FAIL 或 p95_sel>p95_idw 后：
rm -f /workspace/epc_fixtures/ab_hard/B_out.ab_hard_red.db
PYTHONPATH=/workspace python3 -m epc_engine \
  /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_red.yaml
# EXIT≠0；无 B.db；audit `ab_hard: FAIL`
```

### idw 跳过

```bash
PYTHONPATH=/workspace python3 -m epc_engine \
  /workspace/epc_fixtures/ab_hard/epc_job.ab_hard_idw.yaml
# EXIT 0；audit `ab_hard: SKIP`
```

## 改动文件（开发）

- `epc_engine/ab_hard.py`（新）
- `epc_engine/train_lib.py`（≤ 门禁、报表 AB-hard 列）
- `epc_engine/train.py`（拒绝晋升、写 stamp、`--require-ab-hard`）
- `epc_engine/cli.py`（`run_epc_ab` stamp 门）
- `epc_engine/audit.py`（AB-hard 段）
- `epc_fixtures/run_ab_hard_suite.sh`
- `epc_fixtures/ab_hard/*`
- `epc_engine/models/residual_gbdt.joblib.ab_hard.json`（sidecar stamp）

**未改**：`modes/h3_hard.py`、`p2/eval_h3.py`、`p2/run_p2_suite.sh`、GUI。

## 比较符说明（AB-S3）

原算法升级「严格 `<`」本轮改为 **`≤`**，与 H3-hard 统一；现 DEMO residual 仍绿。旧门禁 ID `P-LOP` / `P-LOI-base` 保留为 **AB-hard-*** 别名行。
