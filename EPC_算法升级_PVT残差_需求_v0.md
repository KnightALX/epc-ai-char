# EPC 算法升级增量 · PVT 残差覆盖 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 选定：增强 residual 覆盖新 PVT，改善 LOP） |
| 日期 | 2026-10-21（Asia/Shanghai） |
| 父需求 | `/workspace/EPC_算法升级_需求_v0.md` |
| 已验收现状 | `/workspace/epc_fixtures/P0_算法升级_验收报告.md`、`algo_holdout_report.md` |
| 现状策略 | `v_hat = prior(idw_nn) + HistGBDT`，但 **残差仅用于新几何（LOI）**；纯新 PVT → prior-only → LOP p95 **EQUAL** 基线 |
| 锚点数字（已验收报表） | LOI：idw_nn **0.31168** → residual **0.102331**；LOP：二者均为 **5.2333e-05**（prior-only） |

> **纪律**：不改 I/O / YAML 约束门禁 / `char_data` schema；**不**扇出开发（编排器交接）。DEMO 合成 only。

---

## 1. 目标

对新 PVT（`pvt∉A`）以及双新（`instance∉A ∧ pvt∉A`）也施加 residual，使：

| 协议 | 目标 |
|---|---|
| **LOP** | hold-out **p95 严格优于** `idw_nn`（结束 EQUAL） |
| **LOI** | **不得明显回退**（可测口径见 §5）；且仍须严格优于 `idw_nn` |

公式不变：\(\hat{v} = \mathrm{prior}(idw\_nn) + \mathrm{residual}(x)\)；变化在 **何时加 residual** 与 **训练是否覆盖 PVT 外推残差**。

---

## 2. 训练（A_ref only）

1. 继续仅用 A_ref；在线 job 仍只读 A.db + YAML + 预训模型。  
2. 训练集须同时覆盖：  
   - **几何外推残差**：leave-instance 风格（held instance 上 prior=IDW，残差 = 真值 − prior）  
   - **PVT 外推残差**：leave-pvt 风格（held pvt 上 prior=NN(+经验缩放)，残差 = 真值 − prior）  
3. 特征：沿用现有 geom(`log2 d/w`) + PVT(`corner`/`corner_rank`, `V`, `T`) + `prior_hat` + cell 轴；**可加强** PVT 相关项（例：`ΔV`/`ΔT` vs NN pvt、`1/V`、corner one-hot 全量、`V×T`），**禁止**打乱 tran/load。  
4. 模型形态可维持逐 key HistGBDT；允许单模型或 `geom_residual` / `pvt_residual` 双头，但在线合成规则须文档化。  
5. Hold-out 协议与折集合：**默认复用**现报表 LOI 5 折 + LOP 6 折 + 核心 8 key + ε=`1e-12` + seed=`42`，便于与锚点对比；扩折须在新报表声明。

---

## 3. 在线策略（须钉死并写进 audit）

**推荐默认（本增量硬需求）：**

| `(instance,pvt)` 相对 A | 行为 |
|---|---|
| 二者皆在且有组 | `seed_from_A`：**不加** residual（拷贝真值） |
| 其余任一外推 | **一律** `prior + residual`（含纯新 PVT、纯新几何、双新） |

可选配置（实现可保留，默认如下）：

```yaml
construct:
  backend: residual_gbdt
  residual_gbdt:
    apply_on: all_extrapolated   # 推荐默认；曾用 geom_only 即现状
    # 兼容开关（若保留）：
    # apply_geom_residual: true
    # apply_pvt_residual: true
```

Audit 每组须能区分：`residual_applied=true|false` 与原因（`seed_from_A` / `geom` / `pvt` / `both` / `fallback`）。  
**禁止**再出现「pvt-only → residual skipped」作为默认生产路径（除非显式 `apply_on: geom_only` 做对照实验）。

---

## 4. 验收 F（功能回归）

与父需求 F1–F6 同口径；本增量至少：

| # | 项 | 通过标准 |
|---|---|---|
| F1 | sample + `residual_gbdt` | EXIT **0**，`COUNT(*)=4950` |
| F2 | 既有约束 | PASS（upper bound / relative −4%） |
| F3 | 红用例 | EXIT≠0，目标 B.db **不落盘** |
| F4 | 可切 `idw_nn` | 同上绿+红仍过 |
| F5 | 审计 | 纯新 PVT / 双新组可见 **residual_applied=true**（非 seed） |

---

## 5. 验收 P（精度 · 可测口径）

同一报表路径更新：`/workspace/epc_fixtures/algo_holdout_report.md`（并刷新或附注 `P0_算法升级_验收报告.md` / 增量验收页）。

记：

- \(p95^{LOI}_{base}\)、\(p95^{LOP}_{base}\) = 同协议下 **idw_nn**  
- \(p95^{LOI}_{new}\)、\(p95^{LOP}_{new}\) = 本增量 residual（`apply_on: all_extrapolated`）  
- \(p95^{LOI}_{prev} = 0.102331\) = **已验收** residual（geom-only）锚点  

| ID | 门禁 | 通过标准（钉死） |
|---|---|---|
| **P-LOP** | 硬 | \(p95^{LOP}_{new} < p95^{LOP}_{base}\)（严格；结束 EQUAL） |
| **P-LOI-base** | 硬 | \(p95^{LOI}_{new} < p95^{LOI}_{base}\)（仍须显著优于 idw_nn；对应当前 base≈0.31168） |
| **P-LOI-reg** | 硬（回退） | \(p95^{LOI}_{new} \le p95^{LOI}_{prev} \times 1.05\) 即 **≤ 0.107448**（相对已验收 residual 恶化不超过 **5%**） |

说明：

- 「不得明显回退」= **P-LOI-reg**；不是「允许掉回只优于基线」。若实现无法同时满足 P-LOP 与 P-LOI-reg，**优先保 P-LOI-reg 与 P-LOI-base**，并在报表标 FAIL 原因，由编排器/Kai 再裁；默认交付目标是 **三项全绿**。  
- 更优：\(p95^{LOI}_{new} \le p95^{LOI}_{prev}\)（不差于当前）记为 **P-LOI-reg+**（加分，非硬门禁）。  
- 核心 8 key 须在报表按 key 列出 LOP Δ；允许个别 key LOP 持平，但 **全局聚合 p95** 必须严格下降。  
- LOP 基线绝对值很小（delay 类近 0、leakage 较大）；实现时勿改误差定义刷过门禁；协议/ε/聚合方式须与现报表一致。

---

## 6. 非目标

- 跨真实工艺 / PDK 标定  
- 换大模型 / 改 schema / 放宽约束 `fail_job`  
- 强制扩满 20/40 折（可后做；本轮复用现折即可）

---

## 7. 交付物（经编排器 → 代码工程师）

1. 训练覆盖 PVT 外推残差；默认在线 `apply_on: all_extrapolated`  
2. 更新模型文件 + README / 复现命令  
3. 新 hold-out 报表：P-LOP / P-LOI-base / P-LOI-reg 判定行  
4. F1–F5 绿  

---

## 8. 一页结论

- **改什么**：残差从「仅新几何」扩到「一切非 seed 外推（含新 PVT / 双新）」；训练补 PVT leave-out 残差。  
- **LOP**：p95 必须 **严格 < idw_nn**。  
- **LOI**：仍 **严格 < idw_nn**，且相对已验收 **0.102331** 恶化 **≤5%**（≤**0.107448**）。  
- **不**扇出；本文路径交编排器。

**本文路径**：`/workspace/EPC_算法升级_PVT残差_需求_v0.md`
