# EPC 加固《epc_ab / algo_holdout 硬门禁》需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0.1**（编排器称 Kai 对 Q1/Q2 全按推荐已开开发；本侧不扇出） |
| 日期 | 2026-10-22（Asia/Shanghai） |
| 触发 | Kai 选定：`mode=epc_ab` 主路径 hold-out 上，非 `idw` backend 须 **`p95_selected ≤ p95_idw`**（允许 =）；失败 `fail_job`、不落盘 |
| 锚点 | `/workspace/EPC_加固_残差硬门禁_需求_v0.md` §3/§5（`epc_ab` **下次**）；`/workspace/EPC_算法升级_需求_v0.md` §5 LOI/LOP；`/workspace/epc_fixtures/algo_holdout_report.md`；P0 算法升级 / PVT 残差验收 |
| 引擎 | `/workspace/epc_engine/`（`train` / `train_lib` / `backends` / `cli.run_epc_ab`）；**勿改** Op-Geom/Miss/Sparse 的 `modes/h3_hard.py` 协议 |

> 本轮 = **把「selected ≤ idw」锁进 epc_ab 精度主路径**，与 P2 算子 H3-hard **并列、不缠死**。  
> **非目标**：重训冲榜、改 schema、真 PDK、放宽约束 `fail_job`、重开 Geom 四角协议。

---

## 1. 一页结论

| 问 | 答（本稿推荐） |
|---|---|
| 比什么 | 同协议 hold-out 上 **`p95_selected ≤ p95_idw_nn`**（允许 =；对齐 H3-hard，**放宽**原算法升级「严格 `<`」） |
| 谁触发 | `construct.backend ∉ {idw_nn}`（含 `residual_gbdt` 及未来非 idw）；**`idw_nn` 跳过** |
| 主协议 | **LOI p95**（与算法升级 A1 / 报表主指标一致）；**LOP p95 同规则硬断言**（并列，不二选一） |
| 落点 | **Must：离线 `algo_holdout` 硬断言** + **Must：在线 epc_ab 只读 stamp**（缺/FAIL → `fail_job` 不落盘）；**不**在每个 job 内重跑全量 LOI 折 |
| 与 P2 | **独立 suite**；禁止复用四角 Geom hold-out 冒充 AB |

---

## 2. 适用范围（钉清：在线 vs 离线）

| 层 | 本轮 | 行为 |
|---|---|---|
| **离线 `algo_holdout` / `python -m epc_engine.train`** | **Must** | 报表硬门：`AB-hard-LOI`、`AB-hard-LOP`；任一 FAIL → 进程 **EXIT≠0**；禁止把 FAIL 报表当绿交付 |
| **在线 `mode=epc_ab` job** | **Must（轻）** | **不**内嵌全量 fold 重算。读模型/报表 **AB-hard stamp**（最近一次离线 ALL PASS + 模型 sha）；`backend≠idw_nn` 且 stamp 缺/过期/FAIL → **`fail_job`、不写 B.db**；`backend=idw_nn` → 跳过本门 |
| **Op-Geom / Miss / Sparse** | **不动** | 继续既有 H3-hard；本需求 **零改** 其协议与夹具 |

**不推荐本轮**：每个 `epc_ab` job 现场跑 5+6 折 hold-out（慢、与 train 职责重叠、易与 A.db≠A_ref 缠死）。若 Kai 坚持「job 内重算」，降为 Should 且须另钉 A_ref 路径与超时——见 §8 Q1。

---

## 3. 协议（与现 LOI/LOP 对齐）

| 项 | 钉死 |
|---|---|
| 误差 | `e = \|hat − truth\| / max(\|truth\|, ε)`，ε=`1e-12`；**cell 级**；同 `algo_holdout_report.md` |
| 核心 key | 报表写死的 8 key（`tselr1_min_period, tcq, tcd, taccess, leakage_vddc, read_power_vddc, write_power_vddc, dynamic_energy_read`）；轴 key 不参与 |
| **LOI** | 现 5 折 instance 列表（或同 seed 可复现集合）；聚合全局 p95 |
| **LOP** | 现 6 折 pvt 列表；聚合全局 p95 |
| seed | 默认 `42`（与现报表一致）；变更须刷报表并升版说明 |
| 比较符 | **`p95_selected ≤ p95_idw_nn`**（允许 =） |
| 相对旧门 | 原 **P-LOI-base / P-LOP** 的「严格 `<`」**本轮改为 `≤`**，门禁 ID 建议更名为 **`AB-hard-LOI` / `AB-hard-LOP`**（报表可保留旧名别名一行，避免历史链接断裂） |
| 回归门 | 既有 **P-LOI-reg**（≤ prev×1.05）**保留**，与 AB-hard **并行**；本轮不改 reg 公式 |
| 并列报表 | 必须写出：`p95_selected`、`p95_idw_nn`、`delta`、`pass`、`backend`、协议 id（`loi_v0` / `lop_v0`） |

---

## 4. 失败策略（对齐 S5）

| 场景 | 规则 |
|---|---|
| 离线 AB-hard FAIL | train/holdout **EXIT≠0**；报表标 FAIL；**不得**静默晋升/覆盖生产 `residual_gbdt.joblib` 为「绿」 |
| 在线 stamp FAIL/缺 | `epc_ab`：**`on_violation=fail_job` 语义** → EXIT≠0，**B.db 不落盘**；audit 含 `ab_hard: FAIL` + 原因（missing_stamp / stale / offline_fail） |
| `idw_nn` | 跳过 AB-hard（audit：`ab_hard: SKIP`） |
| 禁止 | 因精度劣于 idw 而静默 `fallback→idw_nn` 后当绿；精度差 **≠**「模型缺失」（模型缺失仍可走既有 fallback，且 audit 注明） |

Audit 字段（在线，建议）：

```text
ab_hard: PASS|FAIL|SKIP
ab_hard_protocol: loi_v0+lop_v0
p95_selected_loi / p95_idw_loi / …
p95_selected_lop / p95_idw_lop / …
stamp_sha16 / stamp_generated
backend
```

（数值可引用离线报表摘录，不必在 job 内重算。）

---

## 5. 绿 / 红夹具与 suite（与 Op-Geom 隔离）

| 角色 | 建议 | 期望 |
|---|---|---|
| **绿** | 现 `residual_gbdt` + 现行 A_ref 协议（报表已 YES） | AB-hard-LOI/LOP **PASS**（`≤`）；train EXIT 0 |
| **红** | 人为劣化：fixture 注入 `p95_selected > p95_idw`（mock 或损毁模型头），或临时开关强制 FAIL | 离线 EXIT≠0；若跑在线 stamp 红 → **不落盘** |
| **idw 跳过** | sample/`epc_ab` 临时 `backend: idw_nn` | `ab_hard: SKIP`；功能绿红仍受约束门禁 |
| Suite | 增量脚本建议：`epc_fixtures/run_ab_hard_suite.sh`（或 train 旗标 `--require-ab-hard`）；报告：`加固_epc_ab_holdout硬门禁_验收报告.md` | **禁止**塞进 `p2/eval_h3.py` / `run_p2_suite` |

禁止覆盖 `A_ref.db`；红路径不得留下「伪绿」B.db。

---

## 6. Must / Should / Won't

### 6.1 Must

| ID | 项 |
|---|---|
| **AB-M1** | 离线：非 idw → `AB-hard-LOI` 与 `AB-hard-LOP` 均 `p95_sel ≤ p95_idw`；FAIL → EXIT≠0 |
| **AB-M2** | 报表并列两路 p95 + pass；比较符与 H3-hard 一致（允许 =） |
| **AB-M3** | 在线 `epc_ab`：非 idw 须有效 AB-hard stamp；否则 `fail_job` 不落盘；idw 跳过 |
| **AB-M4** | 与 P2 H3-hard **解耦**（独立代码路径/suite/报告） |
| **AB-M5** | 回归：现 sample / P1 约束绿红、P2 算子绿（idw）**仍过**；`idw_nn` 可切 |

### 6.2 Should

| ID | 项 |
|---|---|
| **AB-S1** | stamp 写入模型 joblib meta 或旁路 `*.ab_hard.json`（sha + 两路 p95 + 时间） |
| **AB-S2** | CI/suite 一键红夹具（mock p95） |
| **AB-S3** | 文档注明：由算法升级「严格 `<`」→ 本轮「`≤`」的动机（与 H3-hard 统一） |

### 6.3 Won't

| ID | 项 |
|---|---|
| **AB-W1** | 每个 epc_ab job 内重跑全量 LOI/LOP（除非 Kai 改拍 Q1） |
| **AB-W2** | 与 Op-Geom 四角 hold-out / `eval_h3` 合并口径 |
| **AB-W3** | 重训冲过门、真 PDK、改 `char_data` schema |
| **AB-W4** | 静默降级 backend 掩盖 AB-hard FAIL |

---

## 7. 验收 U 表（≤6）

| # | 项 | 标准 |
|---|---|---|
| **U0** | 回归 | sample + 约束绿红 + P2 idw 绿仍过；P2 residual Geom 红行为**不变** |
| **U1** | 离线绿 | 现行 residual 模型：`AB-hard-LOI/LOP` PASS；报表两路 p95；EXIT 0 |
| **U2** | 离线红 | 强制 `p95_sel > p95_idw` → EXIT≠0；报表 FAIL |
| **U3** | 比较符 | `p95_sel == p95_idw` → **PASS**（允许 =）；严格 `<` 不再作为唯一绿条件 |
| **U4** | 在线 stamp | 非 idw + 无/坏 stamp → EXIT≠0、无 B.db；audit `ab_hard: FAIL` |
| **U5** | idw 跳过 | `backend=idw_nn` → `ab_hard: SKIP`；不挡功能门禁 |

---

## 8. 请 Kai 拍板（编排器转 · 1–2 问）

| # | 问 | 本稿推荐 |
|---|---|---|
| **Q1** | 在线 `epc_ab` 要多重？ | **A：离线硬断言 + 在线只读 stamp（缺/FAIL→fail_job）** — 见 §2。备选 B：仅离线（在线不拦）。备选 C：每 job 重算 LOI（不推荐） |
| **Q2** | 原「严格 `<`」是否改为 `≤`？ | **改 `≤`**（与 H3-hard 统一）；现 DEMO 仍绿 |

（触发 backend、LOI+LOP 双硬、fail_job 不落盘、与 Geom 解耦 — **已钉死，不再开放**。）

**请 Kai 拍板后再开开发。** 不写「可直接开开发」。

---

## 9. 与「下次」锚点对照

| H3-hard 文档原文 | 本需求 |
|---|---|
| `epc_ab` 主路径 hold-out **下次** | **本轮落地** |
| 可选并入 `algo_holdout` 硬断言 | **Must（离线）** |
| 比较符 ≤ | **一致** |
| fail_job 不落盘 | **在线 stamp 失败时一致** |

**本文路径**：`/workspace/EPC_加固_epc_ab_holdout硬门禁_需求_v0.md`（**v0**）
