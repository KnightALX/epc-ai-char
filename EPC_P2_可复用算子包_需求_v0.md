# EPC P2《可复用算子包》需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 开 P2；拍板项转 Kai 后由编排器交接开发；**本侧不扇出**） |
| 日期 | 2026-10-21（Asia/Shanghai） |
| 范围锚点 | `/workspace/SRAM_Char_AI_范围说明书_T0.md` **§1.4**；`/workspace/EPC_项目IO与规则骨架_v0.md` §6 |
| 方法参考 | `/workspace/slide25_26_项目计划输入.md`（Slide 24 缺数 / Slide 25 少 PVT 填表意图；**勿与本文 EPC 里程碑 P0/P1/P2 编号混淆**） |
| 引擎现状 | `/workspace/epc_engine/`：单一 `python -m epc_engine <job.yaml>`；P0 A→B + 外推后端；P1 糖衣相对约束 + G1–G3；S2=A / S5=`fail_job` **已拍板** |
| DEMO | `/workspace/epc_fixtures/` A_ref **20×40×50**；T1 **v1.1** |

> P2 = 把「同工艺边角→内点」「PVT 缺数/少角填表」收成 **可独立调用** 的算子/作业模式，挂同一引擎。  
> **不**替代 P0 成为唯一产品故事；**不**重开 P0/P1；**不**改 `char_data` schema；**不**做真工艺标定。

---

## 1. 目标

| ID | 算子 | 一句话 |
|---|---|---|
| **Op-Geom** | 配置维 · 边角→内点 | 同工艺（或 A≡B 退化）：给定 seed 边角 instance 的稠密表征，生成目标内点 instance 的 **全 PVT × 全字段** |
| **Op-Miss** | PVT 维 · 缺数解卡 | 库中已有 `(instance,pvt)` 组，但部分 `field_key`（或 token）缺失 → 填洞并标 provisional |
| **Op-Sparse** | PVT 维 · 少 PVT 填表 | 某 instance（或全集）仅有稀疏 seed PVT → 填满目标 `pvt_list` 全字段 |

三者共用：T1 Instance/PVT 解析、表轴对齐、状态枚举、审计、`fail_job` 不落盘、可选约束层（P0/P1 类型可挂，非必须）。

构造内核 **复用** 现有 `idw_nn` / `residual_gbdt`（及后续 backend），P2 交付的是 **作业模式 + 触发/种子契约 + 门禁 + fixtures**，不是再发明一套插值。

---

## 2. 与 P0 job 的关系（入口形态）

### 2.1 推荐默认（建议钉死）

**同一 CLI 入口 + YAML `mode` 分派**（降低分叉）：

```bash
python -m epc_engine /path/to/job.yaml
# 或显式：
python -m epc_engine --mode corner_fill_geom job.yaml
```

| `mode` | 含义 | 典型 I/O |
|---|---|---|
| `epc_ab`（**默认**，现 P0） | 跨工艺/列表驱动 A→B | 现 sample 不变 |
| `corner_fill_geom` | Op-Geom | `source.db` + `seed_instances` + `target_instances` + `pvt_list`(或 all_from_source) |
| `pvt_missing_fill` | Op-Miss | 单库 path（in-place 写出到 `output.db_path`，**禁止静默覆盖无备份**） |
| `pvt_sparse_fill` | Op-Sparse | `source.db`（含稀疏 PVT）+ `target.pvt_list` + instance 范围 |

可选等价糖：顶层 `operator: corner_fill_geom` 与 `mode` 同义；二者都写且冲突 → **拒载**。

### 2.2 备选（须 Kai 拍板）

| 方案 | 内容 |
|---|---|
| **A（推荐）** | 上表：`mode` 子模式，共用 `python -m epc_engine` |
| **B** | 独立 subcommand：`python -m epc_engine geom …` / `missing …` / `sparse …`（YAML 仍可传） |
| **C** | A+B 双入口（subcommand 只是 mode 的薄封装） |

**本需求默认写 A**；若 Kai 选 B/C，实现跟拍板，验收命令随之改文档。

### 2.3 硬边界

- `mode=epc_ab` 行为与现 P0/P1 **回归绿**（不得因 P2 引入破坏）。  
- P2 模式 **不得** 假装成「跨工艺主故事」：audit 标题须含算子名；README 标明附属能力。  
- P2 默认可不跑相对糖衣；若 YAML 含 constraints，语义与 P0/P1 相同（S2=A、S5=`fail_job`）。

---

## 3. Op-Geom · 边角落点定义

### 3.1 Seed / 内点（DEMO 可测）

| 项 | 规则 |
|---|---|
| 几何坐标 | T1：`(log2(depth), log2(width))`；同 `family`/`options`（DEMO=`TCAM`/`SWISDC`） |
| **边角 seed（默认）** | 在 seed 池的 depth×width 矩形四角：`(d_min,w_min),(d_min,w_max),(d_max,w_min),(d_max,w_max)` 对应 instance；YAML 也可 **显式** `seed_instances: [...]`（优先显式） |
| **内点 target** | `target_instances` 中非 seed 者；须与 seed 同族/同 option，否则 **拒载** |
| 覆盖 | 每个 target instance × 目标 pvt 全集 × `field_keys`（默认 `all_from_source`） |
| 轴 | `tran_index`/`load_index` 从 seed 参考组拷贝；**禁止**打乱 |

### 3.2 算法

- Prior：现有几何 IDW（仅在 seed 集合上）；PVT∈source 则同 pvt IDW，否则走现 PVT NN+缩放 / residual 策略（与 `construct.backend` 配置一致）。  
- Seed 行：**原样拷贝**，状态 `seed_from_source`；内点：`config_extrapolated`（或保留现枚举并 audit 注明 `operator=corner_fill_geom`）。

### 3.3 须 Kai 拍板（边角）

| 问 | 推荐默认 |
|---|---|
| 边角是否必须恰好 4 个矩形角？ | **默认是**；显式 `seed_instances` 可 ≥4，但须覆盖矩形角或 Kai 声明放弃角覆盖检查 |
| 无 mux / 多 option 混跑？ | DEMO **禁止**混 option；生产混 option → 拒载或分桶（本轮 DEMO 钉死禁止） |

---

## 4. Op-Miss / Op-Sparse · 缺数与少角

### 4.1 缺数触发（Op-Miss）

对指定 `instances`×`pvts`（默认=库内出现过的组）：

| 条件 | 视为 missing |
|---|---|
| M1 | 该组缺少某 `field_key`（相对约定全集，默认=库内该组已出现过的 key 并集或 YAML `field_keys`） |
| M2 | key 存在但 `value` 空 / 非数值 token / 表值长度 ≠ N²（轴键长度 ≠ N） |

**不触发**：整组 `(instance,pvt)` 完全不存在 → 归 **Op-Sparse**（或显式 `create_missing_groups: true` 才由 Miss 创建组；**默认 false**，须 Kai 若要合并）。

填洞后：`status=missing_filled`（或 `pvt_extrapolated`+note）；audit 列表逐 key；建议标记 `provisional=true`（DEMO 字段可放 audit，不改 schema）。

### 4.2 少 PVT 填表（Op-Sparse）

| 项 | 规则 |
|---|---|
| Seed PVT | 库中该 instance 已有完整组的 pvt |
| Target PVT | YAML `target.pvt_list`（可含 seed） |
| 动作 | 对缺失 pvt：用现 PVT 维构造（NN+scale / residual）从 seed PVT 生成全字段 |
| 最少 seed | **≥1** 完整 pvt；推荐 DEMO ≥3 且覆盖 ≥2 corner 名（SS/TT/FF 类）— 不足则 **WARN 或 FAIL**（见拍板） |

### 4.3 须 Kai 拍板（PVT）

| 问 | 推荐默认 |
|---|---|
| Op-Miss 是否允许创建「整组不存在」？ | **否**（默认 false） |
| Sparse seed＜3 时 | **FAIL**（硬），除非 `allow_weak_seed: true` |
| 与 Slide 24「<1% missing」比例 | DEMO **不**锁 1% 阈值；只锁功能+门禁；比例作报表指标 |

---

## 5. 硬门禁（≤3 条，可量化）

三算子共用框架；报表写清 `operator`。

| ID | 门禁 | 通过标准 |
|---|---|---|
| **H1 轴/行数完整** | 输出 DB：目标 `(instance,pvt)` 每组含轴键；表值 token=N²；`COUNT(*)` = \|inst\|×\|pvt\|×\|keys\|（与 YAML 声明一致） | 任一不满足 → **FAIL**，不落盘 |
| **H2 Seed 不变** | 所有 seed（边角 instance 或 seed PVT 组，或 Miss 中非 missing 的已有 cell）写回后与输入相对误差 **max\|Δ/ max(\|v\|,ε)\| < 1e-9**（或 bit 级字符串相等，表值建议数值） | 破坏 seed → **FAIL** |
| **H3 可测精度（DEMO）** | 见下分算子；不通过 → **FAIL** | 必须出 `/workspace/epc_fixtures/p2/*_report.md` |

**H3 分算子口径：**

| 算子 | H3 |
|---|---|
| Op-Geom | 在 A_ref 上：取 4 角为 seed，留 ≥1 内点 instance 全 pvt×核心 8 key 作 hold-out；`p95` 相对误差 **≤ idw_nn 同协议**（允许 =；推荐 residual 时 **严格 <** 若 backend=residual_gbdt） |
| Op-Miss | 人工打孔：随机（seed=42）挖掉已有库 **约 0.5%–2%** 的非轴 key cell；填回后这些孔的 cell 级 p95 相对误差 **< 0.15**（DEMO 合成阈值，可标定后升 v0.1）；且未打孔 cell 满足 H2 |
| Op-Sparse | Leave-one-pvt：对抽检 instance，藏 1 个 pvt 再填回；该 pvt 上核心 8 key 的 p95 **≤** 同点 `idw_nn`/`residual` 基线（与现 hold-out 工具对齐） |

ε=`1e-12`；核心 8 key 同算法升级报表。

---

## 6. 验收 F / Fixtures

### 6.1 F 清单

| # | 项 | 标准 |
|---|---|---|
| F0 | P0/P1 回归 | 现 sample / P1 绿红路径仍过 |
| F1 | Op-Geom 绿 | EXIT0 + H1–H3 |
| F2 | Op-Miss 绿 | EXIT0 + H1–H3 |
| F3 | Op-Sparse 绿 | EXIT0 + H1–H3 |
| F4 | 红用例 | 各算子 ≥1 红：EXIT≠0、输出 db **不落盘** |
| F5 | Audit | 含 `mode`/`operator`、seed 列表、missing 列表、backend、gates |

### 6.2 Fixtures 建议（`/workspace/epc_fixtures/p2/`）

| 文件 | 角色 |
|---|---|
| `job_corner_fill_green.yaml` | Seed= A_ref 四角几何；target=1–2 内点；pvt=全 40 或子集 ≥8；期望满表 COUNT |
| `job_corner_fill_red.yaml` | 混 option / 内点当 seed 缺失角覆盖 → FAIL |
| `job_missing_fill_green.yaml` | 从 A_ref 拷贝小库并打孔；填回 |
| `job_missing_fill_red.yaml` | 要求填「整组不存在」且未开 create → FAIL |
| `job_sparse_fill_green.yaml` | 每 instance 只留 3–5 个 pvt；target 扩到 11 或 40 |
| `job_sparse_fill_red.yaml` | seed pvt=0 或 1 且未 `allow_weak_seed` → FAIL |
| `P2_算子包_验收报告.md` | 汇总 F/H |

绿路径输出 db 放 `p2/out_*.db`，勿覆盖 `A_ref.db`。

---

## 7. YAML 草图（实现可微调键名）

```yaml
version: "0.1"
mode: corner_fill_geom    # epc_ab | corner_fill_geom | pvt_missing_fill | pvt_sparse_fill
job_name: DEMO_P2_geom

source:
  db_path: "/workspace/epc_fixtures/A_ref.db"

geom_fill:                 # mode=corner_fill_geom
  seed_instances:          # 显式优先；否则按矩形四角从 pool 推断
    - HINP3TCAM64X8SWISDC
    - HINP3TCAM64X100SWISDC
    - HINP3TCAM512X8SWISDC
    - HINP3TCAM512X100SWISDC
  target_instances:
    - HINP3TCAM256X32SWISDC
  pvt_list: all_from_source

# missing_fill: ...
# sparse_fill:
#   instances: all_in_source
#   seed_pvts: auto
#   target_pvt_list_path: "..."

construct:
  backend: residual_gbdt   # 或 idw_nn
  apply_on: all_extrapolated

output:
  db_path: "/workspace/epc_fixtures/p2/out_geom.db"
  audit_report_path: "/workspace/epc_fixtures/p2/out_geom_audit.md"

gates:
  require_constraint_satisfaction: true
  on_violation: fail_job
```

---

## 8. 非目标

- 真 PDK / 跨真实工艺标定；Active Learning 选点产品化  
- 改 schema；把 P2 升成唯一主路径  
- 重开 P0 I/O 或 P1 糖衣/G1–G3  
- soft_clip 默认；无审计的静默填洞  

---

## 9. 给编排器 → Kai 的拍板清单

1. **入口**：A=`mode` 子模式（推荐） / B=独立 subcommand / C=两者？  
2. **边角**：默认矩形四角 + 显式 seed 覆盖检查 — 是否同意？  
3. **Miss**：默认不创建整组；Sparse seed＜3 → FAIL — 是否同意？  

未回前可按推荐默认设计；Kai 确认后冻结再交开发。

---

## 10. 一页结论

- P2 三算子：**边角→内点 / 缺数填洞 / 少 PVT 填表**；复用现 backend，产品化的是 **mode 契约 + 门禁 + fixtures**。  
- 推荐 **同一 CLI + `mode`**；H1 完整、H2 seed 不变、H3 DEMO 精度。  
- 不扇出；拍板后由编排器交接代码工程师。

**本文路径**：`/workspace/EPC_P2_可复用算子包_需求_v0.md`
