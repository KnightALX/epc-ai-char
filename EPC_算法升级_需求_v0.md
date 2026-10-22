# EPC 算法升级需求 v0 — 构造后端：击败 IDW+NN 基线

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 选定下一步；交编排器 → 代码工程师实现） |
| 日期 | 2026-10-21（Asia/Shanghai） |
| 范围说明书 | `/workspace/SRAM_Char_AI_范围说明书_T0.md` **v1 / v1.0.1** |
| T1 数据字典 | `/workspace/EPC_T1_数据字典.md` **v1.1** |
| 基线引擎 | `/workspace/epc_engine/construct.py`（几何 IDW k=4,p=2 + PVT NN + 经验 V/T/corner 缩放） |
| DEMO 夹具 | `/workspace/epc_fixtures/`（A_ref **20×40×50=40000**；B 满表 **9×11×50=4950**） |
| 技术背景 | `/workspace/slide25_26_项目计划输入.md` §4；`/workspace/EPC_项目IO与规则骨架_v0.md` |

> **纪律**：本文件只定目标 / 方案推荐 / 特征 / 训练评估 / 验收。**不**改 char_data schema；**不**扇出开发（由编排器交接）。在线 job 契约与约束门禁不变。

---

## 1. 目标

在 **相同 I/O、YAML、约束门禁、审计与 EXIT 语义** 下，升级 B∉A（新几何 / 新 PVT / 双新）构造可信度，**须击败当前 IDW+NN 基线**。

| 维度 | 要求 |
|---|---|
| 功能兼容 | sample YAML 仍 EXIT0；`COUNT(*)=4950`；既有约束 PASS；红用例仍 FAIL 且 **不落盘** B.db |
| 精度 | 在 DEMO 上定义可复现的 **hold-out** 指标；相对基线 **p95 相对误差严格更优**（阈值先「优于基线」+ 报表；具体数字待 DEMO 标定后可升 v0.1） |
| 可切换 | 配置项 `construct.backend: idw_nn \| residual_gbdt`（YAML 或引擎配置；默认可保留 `idw_nn` 直至新后端验收绿） |
| 在线契约 | job 运行时 **只读** A.db + YAML（+ 可选离线训好的模型文件路径）；**禁止**在线扫 B 真值或改 schema |

---

## 2. 基线（必须保留可切换）

当前 `construct.py` 行为（验收对照）：

1. `(instance,pvt)` ∈ A → `seed_from_A` 原样拷贝  
2. instance∉A、pvt∈A → 同 pvt 上几何 **IDW**（`log2(depth), log2(width)`，k=4，p=2）  
3. pvt∉A → **PVT NN** +（delay/power 类 key）经验 V/T/corner 缩放  
4. 双新 → IDW @ NN pvt + 同上缩放  
5. `tran_index` / `load_index` **始终**从 A 参考组拷贝；**禁止**打乱或重排表轴  

新后端必须覆盖相同状态标签语义（或等价审计字段），并仍先构造、后施加约束（用户约束 > 风格先验）。

---

## 3. 推荐方案（可微调）

$$
\hat{v} = \mathrm{prior}(\mathrm{IDW/NN\ 或\ 线性}) + \mathrm{residual\_model}(x)
$$

| 层级 | 建议 | 说明 |
|---|---|---|
| Prior | 复用现有 IDW+NN（或同特征线性回归） | 保证冷启动与可解释；残差学「几何/PVT 非线性」 |
| 主残差模型 | **GBDT**（LightGBM / XGBoost / sklearn HistGBDT 均可） | 表格强基线；多输出或 **逐 key**；DEMO 优先逐 key 或按 key 族（delay / power / cap / other） |
| 小样本关键 key | 可选 **GPR**（仅标量或低维） | 若某 key 在 A 上有效样本极少或需 UQ；非本轮硬性 |
| 表值处理 | 每 cell 一行，或共享几何/PVT 特征 + 多输出 N² | **必须**保持 tran/load 轴对齐；特征可含 `tran_i`, `load_j`, `i`, `j`，**不得**打乱行主序写回 |

实现落点建议（非强制目录名）：`epc_engine/construct.py` 抽 backend 接口；`backends/idw_nn.py` / `backends/residual_gbdt.py`；离线脚本 `tools/train_residual.py` + `tools/eval_holdout.py`。

依赖：允许增加 `lightgbm` 或 `sklearn`（写明 README）；无 GPU 要求。

---

## 4. 特征（x）

| 组 | 特征 | 规则 |
|---|---|---|
| 几何 | `log2(depth)`, `log2(width)`；可选 `mux`（DEMO 可缺省）、`family` one-hot / 常数 | 与 T1 解析一致 |
| PVT | `corner` one-hot **或** `corner_rank`；`V`, `Vddp`, `T` | 与 `parse.PvtParts` 一致 |
| Key | `key_id` / 分 key 独立模型 / key 族 one-hot | 禁止把无关 key 混成单一无条件输出而不声明 |
| 表 cell | `tran_index[i]`, `load_index[j]`, 可选 `i`,`j` | **轴顺序冻结**；标量 key 无 cell 维 |
| 禁止 | 目标 value 本身；随机打乱 cell；用 B∉A 的「真值」当训练标签（DEMO 合成真值仅用于 **离线** hold-out 评估） | |

Prior 输出可作为一维特征 `prior_hat` 喂给残差模型（推荐）。

---

## 5. 训练数据与离线评估协议

### 5.1 数据边界

| 场景 | 允许 |
|---|---|
| 离线训练 / hold-out | **仅** A_ref（及由其派生的 leave-one 折） |
| 在线 `epc_engine` job | 只读 job 指定的 A.db + YAML；可加载 **预先**训好的模型文件（路径由配置给出） |
| B 列表中 ∉A 点 | **不可**作训练标签；可作为「无真值构造」冒烟，不计入精度验收 |

### 5.2 Hold-out 定义（DEMO 可算）

在 A_ref（20 instance × 40 pvt）上定义两套协议，**均须报**；主验收取二者加权或取更严者（实现时在报表中并列，默认 **主指标 = leave-one-instance 的 p95**）：

1. **Leave-one-instance（LOI）**  
   - 每次留出 1 个 instance 的全部 pvt×key 作 test；用其余 19 个训练 prior+残差。  
   - 模拟 B 新几何。  
   - 建议至少跑满 20 折，或固定种子抽 ≥5 个边角几何（含 `64X8` / `512X100` 等）。

2. **Leave-one-pvt（LOP）**  
   - 每次留出 1 个 pvt 的全部 instance×key；其余 39 训练。  
   - 模拟 B 新 PVT。  
   - 建议全 40 折或分层抽 corner×V×T 各若干。

**指标（每个 key 或按 key 族聚合后再全局聚合）：**

- 相对误差：\( e = \| \hat{v} - v \| / \max(\|v\|, \epsilon) \)（表值按 cell；可报 cell 级与表级 max）  
- 汇总：p50 / **p95** / max；相对 **同一 hold-out 上的 IDW+NN 基线**  
- **验收阈值（v0）**：全局（或 delay+power 核心 key 集合）**p95(e_new) < p95(e_baseline)**，且报表落盘  

核心 key 建议集（可微调，须在报表写死列表）：  
`tselr1_min_period`, `tcq`, `tcd`, `taccess`, `leakage_vddc`, `read_power_vddc`, `write_power_vddc`, `dynamic_energy_read` 等 delay/power 代表；轴 key 不参与精度。

ε：建议 `1e-12` 或按 key 族的绝对地板（报表注明）。

### 5.3 与 sample job 的关系

Hold-out **不替代** sample YAML 功能验收。精度绿 ≠ 可关掉约束门禁。

---

## 6. 验收清单

### 6.1 功能（回归，两 backend 都要）

| # | 项 | 通过标准 |
|---|---|---|
| F1 | sample YAML | `python3 -m epc_engine .../epc_job.sample.yaml` → **EXIT 0** |
| F2 | 满表行数 | `COUNT(*)=4950`（9×11×50） |
| F3 | 约束 | 既有 `table_upper_bound` / `relative_delta_vs_source` **PASS**（与 P0 MVP 门禁复验一致） |
| F4 | 红用例 | 收紧 upper bound → **EXIT≠0**，目标 B.db **不存在**；FAIL audit 可写 |
| F5 | 轴完整 | 每组含 `tran_index`/`load_index`；表值 token 数 = N²（N=5） |
| F6 | 切换 | `construct.backend: idw_nn` 与 `residual_gbdt` 均可跑通 F1–F5 |

### 6.2 精度（仅 residual 后端 + 离线报表）

| # | 项 | 通过标准 |
|---|---|---|
| P1 | 报表路径 | 如 `/workspace/epc_fixtures/algo_holdout_report.md`（或 `algo_eval/`）含 LOI/LOP、基线对比、按 key 族 p50/p95 |
| P2 | 优于基线 | 主指标 **p95 相对误差严格小于** 同协议 IDW+NN |
| P3 | 可复现 | 固定随机种子；依赖与命令写入引擎 README 或报表头 |

数字阈值（如「p95≤X%」）**本 v0 不锁定**；标定后由需求侧升 v0.1。

### 6.3 非目标（本轮不做）

- 跨真实工艺 / 真 PDK 标定  
- 深度学习大模型、GNN、波形级代理  
- 修改 `char_data` schema 或 T1 主键语义  
- Active Learning 选点、在线重训  
- 替换约束引擎或放宽 `fail_job` 语义  

---

## 7. 配置草图（实现时可微调键名）

```yaml
# 可置于 job YAML 顶层或 style_from_source 下
construct:
  backend: residual_gbdt   # idw_nn | residual_gbdt
  residual_gbdt:
    model_path: "/workspace/epc_fixtures/models/residual_gbdt.joblib"  # 预训
    prior: idw_nn          # idw_nn | linear | none
    fallback: idw_nn       # 模型缺失或特征失败时回退，且 audit 注明
```

Audit 须记录：`backend`、`prior`、是否 fallback、模型路径哈希/版本。

---

## 8. 交付物（代码工程师，经编排器交接）

1. 可切换构造后端 + 文档（README 增补）  
2. 离线 train / hold-out eval 脚本与 **一键复现命令**  
3. DEMO 上 P1–P3 报表；F1–F6 绿  
4. **不**要求本轮改范围说明书正文；若需脚注「构造后端可插拔」，另开范围补丁（编排器决定）  

---

## 9. 开放项（不挡开工）

| ID | 项 | 默认 |
|---|---|---|
| A1 | 主指标用 LOI 还是 LOI∩LOP | 报表并列；门禁默认 LOI p95 |
| A2 | 逐 key vs 多输出 GBDT | 先逐 key / 按族；性能不够再合并 |
| A3 | 模型文件格式 | joblib / lightgbm txt，README 钉死一种 |
| A4 | p95 数值门槛 | DEMO 标定后写入 v0.1 |

---

## 10. 一页结论

- **升什么**：构造算法，不是 I/O/约束。  
- **怎么升**：`prior(IDW/NN) + GBDT 残差`；特征 = 几何 log2 + PVT + key/cell；轴不打乱。  
- **怎么验**：功能回归照旧；精度用 A_ref leave-one-instance/pvt **击败 IDW+NN p95**。  
- **怎么交**：配置可切换；编排器交接代码工程师；需求侧本文件路径如下。  

**本文路径**：`/workspace/EPC_算法升级_需求_v0.md`
