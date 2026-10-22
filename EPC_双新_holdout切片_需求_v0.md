# EPC《双新 (geom+PVT) hold-out 切片》需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0.1**（编排器称 Kai 对 Q1–Q3 全按推荐已开开发；本侧不扇出） |
| 日期 | 2026-10-22（Asia/Shanghai） |
| 触发 | 构造已覆盖双新（`instance∉A ∧ pvt∉A`），但 hold-out **仅有 LOI / LOP**，缺「同时新几何+新 PVT」独立切片 |
| 锚点 | `/workspace/EPC_算法升级_需求_v0.md` §2/§5；`/workspace/EPC_算法升级_PVT残差_需求_v0.md`；`/workspace/EPC_加固_epc_ab_holdout硬门禁_需求_v0.md`；`algo_holdout_report.md`；`epc_engine/train_lib.py`（`LOI_INSTANCES` / `LOP_PVTS`） |
| 非目标 | slide25/26 迁移、接真库、暂停、GUI、重训架构、与 Op-Geom H3 / AB stamp **缠死** |

> 本轮 = **评估切片 + 门禁口径**（可复现协议 + 报表；硬 EXIT 见推荐）。  
> **禁止**用四角 Geom hold-out / LOI-only / LOP-only **冒充**双新。

---

## 1. 一页结论

| 问 | 答（本稿推荐） |
|---|---|
| 切片名 | **LON**（Leave-one-(instance,pvt) / 双新 leave-pair） |
| 测什么 | 相对训练集，test 点同时为 **新几何 ∧ 新 PVT** |
| 指标 | cell 相对误差 **p95**；与同协议 **`idw_nn` prior** 并列；比较符默认 **`≤`**（对齐 AB-hard / H3-hard） |
| 交付 | 离线报表增量（独立小节或旁路 md）+ **可选**硬 EXIT；**本轮不要**新 stamp、不要改 AB stamp |
| 边界 | 只定评估/门禁口径；不改在线构造公式、不接真库、不做 GUI |

---

## 2. 协议钉死（A_ref 上）

### 2.1 为什么 LOI/LOP 不够

| 协议 | 训练集相对 test | 模拟 |
|---|---|---|
| LOI | 新 instance，**pvt 仍在训练中** | 纯新几何 |
| LOP | 新 pvt，**instance 仍在训练中** | 纯新 PVT |
| **LON（本轮）** | instance **与** pvt **都不在**训练可见集 | **双新** |

### 2.2 Leave-pair 定义

对每一折 `(I_h, P_h)`：

| 集合 | 规则 |
|---|---|
| **Train 可见** | A_ref 中 **去掉**所有 `instance = I_h` 的行，且 **去掉**所有 `pvt = P_h` 的列 → 剩余约为 `19 × 39` 组（及全部 key） |
| **Test** | **仅** `(I_h, P_h, key)` 上的 cell（核心 8 key；轴 key 不参与） |
| **禁止计入本切片** | `I_h × (pvt≠P_h)`（属 LOI 态）、`(instance≠I_h) × P_h`（属 LOP 态）——可另附旁注，**不得**并入 LON p95 |

先验与残差路径须与在线双新一致：

- **prior（idw_nn）**：IDW @ NN-pvt + 既有 delay/power 经验缩放（算法升级 §2.4）  
- **selected（residual_gbdt）**：`apply_on: all_extrapolated` / 双头合成；audit 语义上等价 `residual_reason=both`  
- 误差：`e = |hat−truth| / max(|truth|, ε)`，ε=`1e-12`，**cell 级**；折间合并后再报全局 p50/p95/max

### 2.3 折集合（推荐默认）

| 项 | 推荐 |
|---|---|
| 候选 | 现成 **`LOI_INSTANCES` × `LOP_PVTS`** = **5 × 6 = 30** 折（复用列表，零新抽样歧义） |
| seed | `42`（仅当实现需打乱/子采样时；全笛卡尔则 seed 只作报表头） |
| 子采样备选 | 若 30 折过慢：固定 seed 抽 **K=12** 对（须在报表写死名单）——见 §8 Q1 |
| 核心 key | 与现报表相同 8 key |

### 2.4 比较符

| 项 | 钉死建议 |
|---|---|
| 主判定 | `p95_selected ≤ p95_idw_nn`（允许 =） |
| 报表 | 并列两路 p95、`delta`、`n_cells`、折数、协议 id=`lon_v0` |
| 若选严格 `<` | 仅当 Kai 拍板 Q2；本稿 **不**默认 |

---

## 3. 交付形态（薄）

| 层 | 本轮推荐 | 说明 |
|---|---|---|
| **离线报表** | **Must** | 扩 `/workspace/epc_fixtures/algo_holdout_report.md` 增 **「Dual-new / LON」** 节，**或**旁路 `/workspace/epc_fixtures/algo_holdout_dual_new_report.md`（二选一，报表头互链） |
| **硬 EXIT** | **Should（推荐先做报表，硬门可同 PR 加开关）** | 默认：`python -m epc_engine.train` / suite 在 LON FAIL 时 **EXIT≠0**（`--require-lon-hard` 或并入 AB suite 旁路）；若 Kai 要更薄 → 本轮仅报表、硬门下次（Q2） |
| **在线 stamp** | **Won't（本轮）** | **不**扩 `*.ab_hard.json`、不新增 `*.lon_hard.json`；避免与 AB-hard 缠死 |
| **Op-Geom H3** | **不动** | 禁止 `eval_h3` / 四角协议冒充 LON |

Suite 建议路径：

```text
/workspace/epc_fixtures/run_lon_holdout_suite.sh
→ 报告：/workspace/epc_fixtures/双新_holdout切片_验收报告.md（或并入 algo 报表自测）
```

与 `run_ab_hard_suite.sh` / `run_p2_suite.sh` **并列**，可互调但不共享协议实现。

---

## 4. Must / Should / Won't

### 4.1 Must

| ID | 项 |
|---|---|
| **LON-M1** | 实现 leave-pair 协议 §2.2；test **仅**双新交叉点 |
| **LON-M2** | 报表：LON p95_selected / p95_idw / delta / n / 折列表；协议 id |
| **LON-M3** | 与 LOI/LOP **分列**；不得把 LOI/LOP 数字改贴为双新 |
| **LON-M4** | U0：现 AB-hard LOI/LOP、sample 约束绿红、P2 idw 绿 **回归仍过** |

### 4.2 Should

| ID | 项 |
|---|---|
| **LON-S1** | 硬门：`p95_sel ≤ p95_idw` FAIL → EXIT≠0（旗标可关） |
| **LON-S2** | 按 key 的 LON p95 表；旁注「非双新交叉点未计入」 |
| **LON-S3** | 红夹具：mock `p95_sel > p95_idw` → suite 红 |

### 4.3 Won't

| ID | 项 |
|---|---|
| **LON-W1** | 接真库 / 真 PDK；slide 迁移；GUI |
| **LON-W2** | 重训架构（换模型族、改 schema、打乱轴） |
| **LON-W3** | 本轮 LON stamp / 改 AB stamp 语义 |
| **LON-W4** | 四角 Geom / Miss / Sparse hold-out 冒充双新 |
| **LON-W5** | 每个在线 `epc_ab` job 内重跑 30 折 LON |

---

## 5. 验收 U 表

| # | 项 | 标准 |
|---|---|---|
| **U0** | 回归 | AB-hard suite / sample 绿红 / P2 idw 绿仍过；Geom H3 行为不变 |
| **U1** | 协议纯度 | 单折抽检：train 无 `I_h`、无 `P_h`；计入误差的 locator **仅** `(I_h,P_h,*)` |
| **U2** | 绿报表 | 现行 residual 模型跑出 LON 节；两路 p95 有限；折数与名单符合 §2.3 拍板结果 |
| **U3** | 比较 | 若启用硬门：`p95_sel ≤ p95_idw` → PASS；`>` → EXIT≠0；`=` → PASS |
| **U4** | 反冒充 | suite/文档断言：**未**调用 `eval_h3` / 四角协议作为 LON 证据 |
| **U5** | 红（若 S3） | mock 劣化 → 硬门红或报表明确 FAIL |

---

## 6. 请 Kai 拍板（编排器转）

| # | 问 | 本稿推荐 |
|---|---|---|
| **Q1** | 折怎么抽？ | **A：全笛卡尔 `LOI_INSTANCES×LOP_PVTS`（30 折）**。备选 B：seed=42 固定 **12** 对（写死名单） |
| **Q2** | 本轮门禁多重？ | **A：报表 Must + 硬 EXIT Should（默认开、可旗标关）**；**不要 stamp**。备选 B：仅报表（硬门下次）。备选 C：报表+硬 EXIT 均为 Must 且无关闭旗标 |
| **Q3** | 比较符？ | **`≤`**（与 AB-hard/H3-hard 一致）。备选：严格 `<` |

（协议纯度「只评交叉点」、与 Geom/AB stamp 解耦、非真库/非 GUI — **已钉死**。）

**请 Kai 拍板后再开开发。** 不写「可直接开开发」。

---

## 7. 与既有门禁关系

```text
LOI  ──纯新几何──┐
LOP  ──纯新 PVT──┼── AB-hard（已 PASS）+ 报表
LON  ──双新交叉──┘── 本需求新增切片（薄；stamp 不绑）

Op-Geom/Miss/Sparse H3-hard ── 另一条线，互不冒充
```

**本文路径**：`/workspace/EPC_双新_holdout切片_需求_v0.md`（**v0**）
