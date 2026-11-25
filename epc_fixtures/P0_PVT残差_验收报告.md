# EPC P0 验收报告 — PVT 残差覆盖增量

| 项 | 内容 |
|---|---|
| 结论 | **PASS** |
| 验收角色 | EDA 测试验证（独立复跑，不盲信开发自报） |
| 验收对象 | `residual_gbdt` 默认 `apply_on: all_extrapolated`（新几何 / 新 PVT / 双新均加 residual） |
| 需求 | `/workspace/EPC_算法升级_PVT残差_需求_v0.md` |
| 日期 | 2026-10-21 22:57 CST（Asia/Shanghai） |
| 数据性质 | **合成 DEMO，非真实 PDK / foundry** |
| 编排来源 | EDA开发任务编排协调器(Top)「请正式验收 · PVT 残差覆盖增量」 |
| 关联 | `algo_holdout_report.md`（本轮重训刷新）；`P0_算法升级_验收报告.md`；门禁复验报告 |

---

## 0. 一页结论

| 维度 | 结果 |
|---|---|
| **F1–F5 功能门禁** | **PASS** |
| **F4 `idw_nn` 可切**（绿+红） | **PASS** |
| **P-LOP / P-LOI-base / P-LOI-reg** | **ALL PASS** |
| 阻塞缺陷 | **无** |

| 关键数字（本轮独立实测） | 值 |
|---|---|
| 绿 sample EXIT / COUNT | **0** / **4950**；distinct (9,11,50)；不完整组 0 |
| 红 upper_bound EXIT / B.db | **1** / **不落盘**（verify_only，cells_clipped=0） |
| P-LOP p95 residual vs idw_nn | **5.22059e-05 < 5.2333e-05**（严格） |
| P-LOI p95 residual vs idw_nn | **0.102257 < 0.31168** |
| P-LOI-reg vs prev×1.05 | **0.102257 ≤ 0.107448**（prev=0.102331）；且 **P-LOI-reg+**（≤prev） |
| 本轮模型 sha256[:16] | **`bd6ecde2f27e622b`** |
| 开发自报 sha16 | `0806067a841e77fd`（**与本轮重训不一致**；精度数字一致，见 §5） |

---

## 1. 复现命令（本验收亲自执行）

```bash
pip install --break-system-packages scikit-learn joblib pyyaml   # 已装 sklearn 1.9.1
cd /workspace && python3 -m epc_engine.train \
  --source-db /workspace/epc_fixtures/A_ref.db \
  --model-out /workspace/epc_engine/models/residual_gbdt.joblib \
  --report-out /workspace/epc_fixtures/algo_holdout_report.md --seed 42
python3 -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
bash /workspace/epc_fixtures/run_red_upper_bound.sh
# F4：临时 YAML 仅改 construct.backend=idw_nn → 绿(/tmp/epc_B_idw.db) + 红(bound=1000)
```

Train 控制台摘录：

```
[train] LOI p95 baseline=0.31168 residual=0.102257 better=True
[train] LOP p95 baseline=5.2333e-05 residual=5.22059e-05 better=True
[train] gate P-LOP=PASS / P-LOI-base=PASS / P-LOI-reg=PASS
[train] model → ... residual_gbdt.joblib keys=48 sha16=bd6ecde2f27e622b
```

---

## 2. F 功能门禁

### 2.1 F1–F3 · sample + `residual_gbdt`

| # | 项 | 期望 | 实测 |
|---|---|---|---|
| **F1** | EXIT / COUNT | 0 / 4950 | **EXIT=0**；COUNT=**4950**；distinct instance/pvt/key=**(9,11,50)**；每组 50 key 齐全 |
| **F2** | 既有约束 | 两条 PASS | `#0 table_upper_bound`：verify_only；before_max=after_max=**1387.9** ≤1500；cells_clipped=**0/25**；`#1 relative_delta`：δ=−4 → **×0.9600**；max_rel_err=0 |
| **F3** | 红上界 | EXIT≠0；不写 B.db | `run_red_upper_bound.sh`：**EXIT=1**；bound=1000 vs max=1387.9；`/tmp/epc_B_red.db` **absent**；FAIL audit；stderr 含 gate fail；脚本自检 “RED regression PASS” |

样本 yaml 仍为 `apply_on: all_extrapolated`；job 日志：`backend_used=residual_gbdt fallback=False model_sha16=bd6ecde2f27e622b`。

### 2.2 F4 · 可切 `idw_nn`

临时 YAML（不改 sample 文件）：`construct.backend: idw_nn`。

| 路径 | EXIT | 结果 |
|---|---|---|
| 绿 | **0** | COUNT=**4950**；两条约束 PASS；`backend_used=idw_nn`；model_sha16=None |
| 红 bound=1000 | **1** | 预先植入 stale B.db → **removed**；正式库 **不存在**；FAIL audit `gates_ok: False` |

→ **F4 PASS**。

### 2.3 F5 · audit：新 PVT / both 可见 `residual_applied=true`

来源：`/workspace/epc_fixtures/B_out.sample_audit.md`（绿 residual 跑后）。

| residual_reason | 组数 | residual_applied |
|---|---|---|
| `seed_from_A` | 48 | **False**（正确：不加 residual） |
| `geom` | 24 | **True** |
| `pvt` | **18** | **True**（纯新 PVT） |
| `both` | **9** | **True**（双新） |

合计：99 组 = 9×11；`residual_applied=True` **51** 组。  
抽检行例：

- `HINP3TCAM128X32SWISDC × FFGNP_0P75V_0P75V_85C` → reason=**pvt**，applied=**True**
- `HINP3TCAM128X64SWISDC × FFGNP_0P75V_0P75V_85C` → reason=**both**，applied=**True**

→ **F5 PASS**（默认路径已不再出现「pvt-only → residual skipped」）。

---

## 3. P 精度（硬门禁）

报表：`/workspace/epc_fixtures/algo_holdout_report.md`（本轮 train 于 **2026-10-21 22:56:59 CST** 刷新）。  
协议：LOI 5 折 + LOP 6 折；核心 8 key；ε=`1e-12`；seed=`42`；相对误差 `|hat-true|/max(|true|,ε)`。

| ID | 准则 | 实测 | 门限 | 结果 |
|---|---|---|---|---|
| **P-LOP** | p95_new < p95_idw_nn | **5.22059e-05 < 5.2333e-05** | 严格 | **PASS** |
| **P-LOI-base** | p95_new < p95_idw_nn | **0.102257 < 0.31168** | 严格（base≈0.31168） | **PASS** |
| **P-LOI-reg** | p95_new ≤ prev×1.05 | **0.102257 ≤ 0.107448** | prev=0.102331 | **PASS** |
| P-LOI-reg+（加分） | p95_new ≤ prev | **0.102257 ≤ 0.102331** | 非硬 | **PASS** |

汇总：

| Protocol | idw_nn p95 | residual p95 | n | better? |
|---|---|---|---|---|
| LOI | 0.31168 | **0.102257** | 20800 | YES |
| LOP | 5.2333e-05 | **5.22059e-05** | 12480 | YES |

相对父需求已验收 geom-only 锚点：LOP 已从 **EQUAL** 变为 **严格更优**；LOI 相对 0.102331 略优（reg+）。

### 3.1 与开发自报对照

| 项 | 开发自报 | 本轮独立实测 | 一致？ |
|---|---|---|---|
| P-LOP | 5.22059e-05 < 5.2333e-05 | **同** | YES |
| P-LOI | 0.102257 | **同** | YES |
| model sha16 | `0806067a841e77fd` | **`bd6ecde2f27e622b`** | **NO**（见 §5） |

---

## 4. 缺陷列表

| 级别 | 项 | 说明 |
|---|---|---|
| 阻塞 | — | **无** |
| 非阻塞 | 模型 sha 漂移 | 同命令/seed=42 全量重训后 sha16 与开发交付包不一致；hold-out 聚合数字可复现一致。生产若需字节级可复现，应钉死 sklearn/joblib 版本与 fit 确定性选项，或把 hold-out 与全量 fit 的 artifact 一并签收。 |
| 非阻塞 / 观察 | LOP 分 key | 报表 per-key LOP：多数 delay 类 Δ=0；`leakage_vddc` 大降；`dynamic_energy_read` 单 key 略升。**全局聚合 p95** 仍严格下降，符合需求「允许个别 key 持平/波动、全局须严格下降」。 |
| 非阻塞 | LOP 绝对改进幅度小 | Δ ≈ 1.27e-07（相对基线约 0.024%）。门禁为严格不等式，已满足；DEMO 上 LOP 基线本就极小。 |

---

## 5. 残留风险

1. **Artifact 字节不可复现**：本轮 `sha16=bd6ecde2f27e622b` ≠ 开发自报 `0806067a841e77fd`。验收以 **hold-out 数字与 F 门禁** 为准判定 PASS；若下游要 pin 模型哈希，请以**本轮重训产物**或开发重新导出并附 train 日志为准。  
2. **DEMO only**：精度结论不可外推真实 PDK。  
3. **双头合成**：`both` 路径 audit 显示 `head=geom`（geom 头 + IDW@NN pvt）；与需求「在线合成规则须文档化」一致，但仍依赖 README/代码注释；建议在引擎 README 钉死 both 时用哪一头。

---

## 6. 签收

| 检查项 | 结论 |
|---|---|
| F1 sample + residual_gbdt | **PASS** |
| F2 约束 | **PASS** |
| F3 红上界不落盘 | **PASS** |
| F4 可切 idw_nn | **PASS** |
| F5 新 PVT / both → residual_applied=true | **PASS** |
| P-LOP / P-LOI-base / P-LOI-reg | **PASS / PASS / PASS** |
| **总体** | **PASS**（阻塞缺陷：无） |

**报告路径**：`/workspace/epc_fixtures/P0_PVT残差_验收报告.md`  
**Hold-out**：`/workspace/epc_fixtures/algo_holdout_report.md`  
**本轮模型**：`/workspace/epc_engine/models/residual_gbdt.joblib`（sha16=`bd6ecde2f27e622b`）
