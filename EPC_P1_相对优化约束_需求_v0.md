# EPC P1《相对优化约束》需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 开 P1；交编排器 → 代码工程师；**本侧不扇出**） |
| 日期 | 2026-10-21（Asia/Shanghai） |
| 范围锚点 | `/workspace/SRAM_Char_AI_范围说明书_T0.md` §1.3 / §2；`/workspace/EPC_项目IO与规则骨架_v0.md` §6 / §8–9 |
| T1 / 夹具 | T1 **v1.1**；`/workspace/epc_fixtures/`（A **40000** / B 满表 **4950**） |
| P0 已绿（勿重造） | 点级 `relative_delta_vs_source`（−4%→×0.96）；笼统 `relative_improve_vs_source` **拒载**；`fail_job`+verify-only+失败不落盘；`residual_gbdt` + `apply_on: all_extrapolated` |

> P1 = **相对优化约束层**（分 PVT 组 speed%/power% 糖衣 → 展开为四元组+`delta_pct`）+ **更严可信度门禁 / 抽检回写 / 对照点可审计**。  
> **不在本轮**：P2 边角算子产品化；真工艺标定；改 `char_data` schema。

---

## 1. 目标

1. 合法支持「按 PVT 组声明 speed%/power%」的 **糖衣** YAML，加载期 **确定性展开** 为多条 `relative_delta_vs_source`（每条仍是 instance×pvt×key×cell + 有符号 `delta_pct`）。  
2. **钉死 S2 对照点**（B∉A 时相对谁）并写入 audit。  
3. **钉死 S5 生产默认**（与 sample 对齐）。  
4. 落地 ≤3 条 **可量化** 可信度硬门禁（含抽检回写）。  
5. 功能/精度类验收 + 绿/红 fixtures 增量；约束仍 **优先于** 风格/残差。

---

## 2. YAML 形态

### 2.1 原子类型（已有，P1 继续为唯一执行形态）

```yaml
- type: relative_delta_vs_source
  instances: ["..."]
  pvts: ["..."]
  keys: ["tcq"]
  table_cells: "all_cells"   # 或 scalar / 显式索引（S6 本轮不扩方言）
  target:
    mode: delta_pct
    delta_pct: -4            # 已冻结：目标 = baseline × (1 + delta_pct/100)
    baseline: source_aligned
```

### 2.2 糖衣类型（P1 新增：允许加载，但必须可展开）

```yaml
- type: relative_improve_vs_source
  instances: ["HINP3TCAM64X8SWISDC", "HINP3TCAM512X100SWISDC"]  # 必填；可列表
  pvts: ["SSGNP_0P99V_0P99V_125C", "TT_0P80V_0P80V_25C"]         # 即 pvt_group
  table_cells: "all_cells"
  speed_keys: *default_speed_keys          # 或内联列表；缺省用 §3 默认表
  power_keys: *default_power_keys
  speed_improve_pct: 4                     # 「优化 4%」→ 对 speed_keys：delta_pct = -4
  power_improve_pct: 5                     # 「优化 5%」→ 对 power_keys：delta_pct = -5
  baseline: source_aligned
  # 可选覆盖：
  # allow_proxy_baseline: true|false       # 见 §4 S2
```

**展开规则（硬）：**

| 输入 | 展开为 |
|---|---|
| `speed_improve_pct: X` | 每个 `(inst,pvt,key∈speed_keys)` → 一条 `relative_delta_vs_source`，`delta_pct = -X` |
| `power_improve_pct: Y` | 同上，`key∈power_keys`，`delta_pct = -Y` |
| 两族 key 交集 | **拒载**（配置错误） |
| 缺 `instances` / `pvts` / `table_cells`(或 scalar) / 两 pct 皆缺 | **拒载**（保持「笼统 PPA 拒绝」精神；pct=0 不算声明） |

展开后与手写原子约束 **AND** 合并；冲突同一 locator 多条相对约束 → **拒载**或后写覆盖策略须在实现选一并写进 audit（**建议拒载**）。

> 与 Kai 已冻结语义对齐：「speed 优化 4%」= delay 类 **数值 ×0.96** = `delta_pct: -4`；power 同理「越小越好」。

---

## 3. speed / power key 默认分组表（DEMO · 可被 YAML 覆盖）

> 来源：A_ref 50 key；轴 key 永不入组。未列入者 **不**被糖衣触及。

### 3.1 `default_speed_keys`（越小越好 → improve X% ⇒ `delta_pct=-X`）

| key |
|---|
| `tselr1_min_period` |
| `tselw1_min_period` |
| `tcq` |
| `tcd` |
| `taccess` |
| `tpd_clk_q` |
| `taddr_setup` |
| `taddr_hold` |
| `twen_setup` |
| `twen_hold` |
| `tcen_setup` |
| `tcen_hold` |
| `tdata_setup` |
| `tdata_hold` |
| `setup_time_a_scalar` |
| `hold_time_a_scalar` |
| `clk_to_q_scalar` |
| `min_pulse_width_clk` |
| `min_period_scalar` |
| `search_latency_scalar` |
| `slew_out_est` |

**默认不入 speed：** `temp_coeff_delay`（系数，非时序绝对值）。若业务要纳入 → YAML 显式列入 `speed_keys`。

### 3.2 `default_power_keys`（越小越好 → improve Y% ⇒ `delta_pct=-Y`）

| key |
|---|
| `leakage_vddc` |
| `leakage_vddp` |
| `retention_leakage` |
| `write_power_vddc` |
| `write_power_vddp` |
| `read_power_vddc` |
| `read_power_vddp` |
| `standby_power_vddc` |
| `search_power_vddc` |
| `dynamic_energy_read` |
| `dynamic_energy_write` |
| `dynamic_energy_search` |

### 3.3 不自动展开（示例）

`area_um2`、各类 `*_cap*`、`noise_margin_snm`、`vdd_min_func`、`em_margin`、`ir_drop_est`、`tran_index`、`load_index`、`fanout_load_nom` 等。

---

## 4. 开放语义：建议钉死 vs 须 Kai 拍板

### 4.1 S2 对照点（B 的 instance/pvt ∉ A）

| 方案 | 含义 |
|---|---|
| **A（推荐默认 · 与现 P0 `style_proxy` 对齐）** | `baseline: source_aligned`：若 A 有精确 `(inst,pvt,key)` → **A_exact**；否则基线 = **施加相对约束前** 的构造值（prior/residual 结果），audit 记 `baseline_source=style_proxy`，并记录用于构造的参考（如 NN pvt / IDW 邻居摘要） |
| B | 仅允许 A_exact；∉A 的相对约束 **拒载或 gate FAIL**（最严，无代理达标） |
| C | YAML 强制 `reference_instance` + `reference_pvt`（须 ∈A），用该对照点同 key 表对齐后比 |

**本需求默认采纳 A**，并加开关：

- `allow_proxy_baseline: true`（**糖衣默认 true**，与现引擎行为连续）  
- 若作业写 `allow_proxy_baseline: false`，则任一 locator 需 proxy → **整作业 FAIL**（贴近方案 B）

| 状态 | |
|---|---|
| **须 Kai 拍板** | 默认 A 是否可冻结；若改 B/C，P1 实现跟拍板结果 |
| 审计硬要求（无论拍哪案） | 每条相对约束 eval 必须可审计：`baseline_source`、`baseline0`、可选 `reference_*` |

### 4.2 S5 违规策略

| 建议钉死 | 内容 |
|---|---|
| **生产唯一默认** | 与 sample 一致：`gates.on_violation: fail_job`；绝对值约束 **verify-only**（不 clip-then-pass）；失败 **不落盘** B.db |
| soft_clip | 仅当 YAML **显式** `on_violation: soft_clip`（或等价）时启用；**不作为 P1 验收绿路径**；audit 必须大红旗 |

| 状态 | |
|---|---|
| **建议钉死** | sample/`fail_job` 即为 P1 生产唯一策略 |
| **须 Kai 拍板** | 是否永久禁止 soft_clip 进入主线（或仅保留实验开关） |

### 4.3 百分比符号（已冻结 · 重申）

- speed/power「优化 X%」→ `delta_pct = -X` → ×`(1 - X/100)`  
- 与骨架 §9 / 说明书 S1 一致；单 key 可被原子约束覆盖。

---

## 5. 「更严可信度门禁」本轮最小可测集（≤3 条硬门禁）

| ID | 门禁 | 可测量通过标准 |
|---|---|---|
| **G1 对照可审计** | 每条已应用的相对约束（含糖衣展开）在 audit 中有 `baseline_source∈{A_exact,style_proxy}`；proxy 时须有非空参考摘要字段 | 缺字段或非法枚举 → **FAIL**（EXIT≠0，不落盘） |
| **G2 抽检回写** | 作业成功写 B.db 后，对相对约束覆盖的 locator **再读库** ≥1 组（建议：糖衣样例中固定 1 speed + 1 power cell），验证 \|B/baseline − (1+δ/100)\| < **1e-6**（相对） | 任一抽检失败 → **FAIL**（若已写入则删除 B.db，与 fail_job 一致） |
| **G3 展开完整性** | 糖衣展开后原子条数 = \|instances\|×\|pvts\|×(\|speed_keys\|·𝟙_speed + \|power_keys\|·𝟙_power)；加载期打印/审计 `expanded_constraint_count` | 计数为 0、或与声明 pct 不一致、或与手写 locator 冲突 → **拒载/FAIL** |

> 不做本轮：全库趋势一致性大模型评分、bit-compatible 出库工具链（待确认项保持开放）。

---

## 6. 验收

### 6.1 F 功能

| # | 项 | 通过标准 |
|---|---|---|
| F1 | 原子相对（回归） | 现 sample 中 `relative_delta_vs_source` 行为不变：EXIT0、COUNT=4950 |
| F2 | 糖衣绿用例 | 见 §7 绿 fixture：EXIT0、COUNT=4950、展开条数符合 G3、约束 PASS |
| F3 | 红用例 | 见 §7：EXIT≠0、B.db 不落盘 |
| F4 | 笼统拒载 | 无 instances/pvts/table_cells 的 `relative_improve_vs_source` 仍 **拒载** |
| F5 | `idw_nn` / `residual_gbdt` | 两 backend 均可跑通绿路径（约束层与 backend 正交） |
| F6 | G1–G3 | 绿路径全过；故意缺 audit / 破坏回写的注入测试至少各 1（可脚本化） |

### 6.2 P 行为 / 精度口径（约束层）

| # | 项 | 通过标准 |
|---|---|---|
| P1 | 符号 | speed_improve 4 → 抽检 cell == baseline×**0.96**；power_improve 5 → ×**0.95** |
| P2 | 优先级 | 风格/残差不得稀释：约束作用点最终值 = 强制目标（与 P0 相对约束相同） |
| P3 | Proxy 透明 | ∉A locator 在 `allow_proxy_baseline:true` 下可 PASS，但 audit 标 `style_proxy`；`false` 时 FAIL |

---

## 7. Fixtures 增量建议

路径建议：`/workspace/epc_fixtures/p1/`（或同级新 yaml）。

### 7.1 绿 · `epc_job.p1_improve_green.yaml`

- 基于 sample：保留一条 `table_upper_bound`（可选）  
- 增加一条糖衣，例如：  
  - `instances`: 2 个 **∈A** 的 B instance（如 `64X8`、`512X100`）  
  - `pvts`: 2 个 **∈A**（如 `TT_0P80V…`、`SSGNP_0P99V…`）  
  - `speed_improve_pct: 4`，`power_improve_pct: 5`  
  - `speed_keys`/`power_keys` 可缩到各 2 个代表 key 以控展开量（验收仍须用默认表跑一轮「全默认 key」或文档声明子集）  
- 期望：EXIT0，COUNT=4950，G1–G3 PASS，抽检 ×0.96/×0.95  

### 7.2 红 · 至少 1（建议 2）

| 红用例 | 期望 |
|---|---|
| **R1 笼统糖衣** | 仅有 `speed_improve_pct`、无 instances/pvts → **拒载/EXIT≠0**，无 B.db |
| **R2 proxy 禁止** | locator 含 B∉A instance，且 `allow_proxy_baseline: false` → **FAIL**，无 B.db |

（可选 R3：与 upper_bound 冲突的相对目标 → fail_job 不落盘。）

### 7.3 报告

`/workspace/epc_fixtures/P1_相对优化约束_验收报告.md`：展开条数、G1–G3、绿/红 EXIT、抽检表。

---

## 8. 非目标

- P2 边角/缺数算子产品化  
- 真 PDK / 跨真实工艺标定  
- 修改 schema；放开「无定位 PPA」  
- 将 soft_clip 定为默认  

---

## 9. 给编排器的拍板清单（转 Kai）

请 Kai 一句确认（否则按本文 **推荐默认** 开工）：

1. **S2**：默认 **A（A_exact / 否则 style_proxy + 可审计）**？还是 B/C？  
2. **S5**：生产是否 **唯一 fail_job**（soft_clip 仅显式实验）？  
3. **§3 默认 speed/power 表** 是否可直接用，或要增删 key？  

---

## 10. 一页结论

- P1 核心：糖衣 `relative_improve_vs_source` → 展开为原子 `relative_delta_vs_source`；**−improve% = delta_pct**。  
- S2 推荐 A + `allow_proxy_baseline`；S5 推荐唯一 `fail_job`。  
- 硬门禁仅 G1 审计 / G2 回写抽检 / G3 展开计数。  
- 绿/红 fixtures 各至少 1；**不扇出开发**。

**本文路径**：`/workspace/EPC_P1_相对优化约束_需求_v0.md`
