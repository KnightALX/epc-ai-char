# EPC 项目 I/O 与规则骨架 v0（Kai 2026-10-21）

> 纠偏：相对「同工艺边角 instance 插值」与「同库 PVT 缺数」，**EPC 主交付是跨工艺平台表征库构造**：A → B。

## 1. 输入

| # | 输入 | 说明 |
|---|---|---|
| 1 | **A 工艺平台 `.db`** | 现成参考（例：N5P）；含大量 instance × pvt × field_key |
| 2 | **B 的 `instance_list`** | 目标颗粒列表；**可不被 A.db 的 instance 集合包含** |
| 3 | **B 的 `pvt_list`** | 目标 PVT 列表；**可不被 A.db 的 pvt 集合包含** |
| 4 | **\*可缺省：B 数据构造约束** | 多条约束为 **AND**；见下 |

### 约束类型（Kai 示例，AND）

1. **点/表上界（绝对值）**  
   - 例：`ssgnp_0p99v_125c` 下 `tselr1_min_period` 的 3×3 各点 **≤ 800ps**  
   - 例：同 PVT `tcq` 的 3×3 **≤ 600ps**  
   - 例：`ssgnp_0p675v_125c` 下 `tcq` 的 3×3 **≤ 1000ps**
2. **相对 A 的整体优化目标（按 PVT 分组）**  
   - 例：某些 PVT 上，相对 A：speed 相关 key **整体优化 4%**，power **优化 5%**  
   - 另一些 PVT：speed **3%**，power **2%**  
   - 「整体」「speed/power 相关 key 集合」需在 YAML 中显式声明分组

## 2. 输出

**B 工艺平台 `.db`**

- instance 数 = `instance_list` 长度  
- pvt 数 = `pvt_list` 长度  
- 每个 `(instance, pvt)` 覆盖 **全部 key|value**（与 A 侧字段全集对齐策略：**待确认**——B 是否必须与 A 同 C 个 field_key）

## 3. 要求

1. **构造过程规则可配置**：优先 **YAML** 输入；规则清晰，便于用户执行/复现。  
2. **继承 A 的历史数据经验与风格**：每项 key 的趋势与数据特征可信。  
3. 构造过程可附加特殊要求，同时保持可信度（与约束 AND、门禁、审计日志一致）。

## 4. 与讲稿 / 前序理解的关系

| 能力 | 角色 |
|---|---|
| 跨工艺 A→B 迁移 + 约束满足 | **EPC 主路径（应对齐 P0）** ≈ Slide 26 TL + 工程约束层 |
| 配置维：B.instance 不在 A 内时的几何外推/插值 | 主路径子问题（与跨工艺叠加） |
| PVT：B.pvt 不在 A 内，或缺数 | 主路径子问题 / 可与 Slide 24–25 方法复用 |
| 同工艺纯边角插值出库 | 降为特例（A≡B 工艺时）或工具能力之一 |

## 5. YAML 规则骨架（草案，待拍板后细化）

```yaml
# epc_job.example.yaml
version: "0.1"
job_name: "N5P_to_N3P_example"   # 名称待 Kai 确认，勿当作真实工艺承诺

source:
  process: "N5P"                   # A
  db_path: "/path/to/A.db"

target:
  process: "TARGET_B"              # B
  instance_list_path: "/path/to/B_instances.txt"
  pvt_list_path: "/path/to/B_pvts.txt"
  # 或 inline:
  # instances: ["HINP3TCAM64X8SWISDC", ...]
  # pvts: ["SSGNP_0P675V_0P675V_M40C", ...]

field_policy:
  # 与 A 对齐：all_from_source | explicit_list
  keys: all_from_source
  table_axes: ["tran_index", "load_index"]
  # 表值插值必须保持轴对齐，禁止打乱 N×N 结构

style_from_source:
  enabled: true
  # 趋势/特征：按 family+geometry 邻域 + 同名 key 从 A 迁移后再施加约束
  notes: "继承 A 的数据风格与趋势可信度"

constraints:                       # 全部 AND
  - type: table_upper_bound
    pvt: "ssgnp_0p99v_125c"
    key: "tselr1_min_period"
    unit: "ps"
    max: 800
    apply_to: each_table_cell     # 3x3/5x5 每个点

  - type: table_upper_bound
    pvt: "ssgnp_0p99v_125c"
    key: "tcq"
    unit: "ps"
    max: 600
    apply_to: each_table_cell

  - type: table_upper_bound
    pvt: "ssgnp_0p675v_125c"
    key: "tcq"
    unit: "ps"
    max: 1000
    apply_to: each_table_cell

  - type: relative_improve_vs_source
    pvt_group: ["ssgnp_0p99v_125c", "..."]
    speed_keys: ["tselr1_min_period", "tcq", "..."]   # 待业务定义
    power_keys: ["write_power_vddc", "leakage_vddc", "..."]
    speed_improve_pct: 4          # 更快 = 时序类数值更小？语义待钉死
    power_improve_pct: 5          # 更省电 = 功耗更小

  - type: relative_improve_vs_source
    pvt_group: ["..."]
    speed_keys: ["..."]
    power_keys: ["..."]
    speed_improve_pct: 3
    power_improve_pct: 2

output:
  db_path: "/path/to/B_out.db"
  audit_report_path: "/path/to/B_out_audit.md"

gates:
  require_constraint_satisfaction: true
  on_violation: fail_job          # 或 soft_clip + flag —— 待 Kai 确认
```

### YAML 中必须尽早钉死的语义（开放问题）

1. 「speed 优化 4%」对 delay/min_period：是否 **数值 ×0.96**（即 `-4%`）？**建议默认采纳，待 Kai 一句确认。**  
2. 相对 A 时，若 B 的 instance/pvt 在 A 中不存在，**对照点**如何选（最近邻几何？同名？family 内插值后再比）？  
3. ~~约束 vs 风格优先级~~ → **已冻结：约束优先**（见 §8）。  
4. B 的 field_key 全集是否必须等于 A？  
5. 表内点寻址语法：`(row,col)` / 展平下标 / `all_cells` 选用哪套？

## 6. 建议的范围重切（给需求拆解）

| 层级 | 建议 |
|---|---|
| **P0** | EPC 主路径：YAML 驱动的 A→B `.db` 构造；支持 instance/pvt 列表外延；绝对值表约束 AND；基础「继承 A 趋势」；审计报告 |
| **P1** | 相对 A 的分 PVT 组 PPA% 约束；更强的可信度门禁 / 回写校验 |
| **P2** | 同工艺边角插值、纯 PVT 缺数解卡等作为 **可复用算子** 挂进同一引擎 |

## 7. 待 Kai 确认 / 提供

- [ ] A 样例 `.db` + B 的 instance_list / pvt_list 样例  
- [ ] 约束样例是否写成正式 YAML  
- [ ] speed/power key 分组表  
- [ ] 违规时 fail vs clip  
- [ ] 输出 `.db` 是否需与现有出库工具链 bit-compatible

---

## 8. 约束语义冻结（Kai 2026-10-21 22:09）

### 优先级
**用户约束 > 继承 A 风格/趋势。** 风格迁移不得覆盖或稀释已声明约束。

### 合法约束必须可定位到 db 元素
每条约束 **必须显式** 指定：

| 维度 | 要求 |
|---|---|
| **instance** | 哪个 instance（可列表/通配规则，但展开后必须落到具体 instance） |
| **pvt** | 哪个 pvt |
| **key** | 哪个 `field_key` |
| **value 中的点** | 标量：唯一点；表值：必须指明表内位置（如 `(i,j)` / `all_cells` / 指定 index 子集） |
| **目标** | **范围**（如 `<= 800ps`、`[a,b]`）或 **相对变化**（`-X%` / `+X%`，相对对象必须是可解析的 A 侧对照值或显式基线） |

### 禁止
- 与 `.db` 无关的自然语言约束（如「整体更好看」「大概快一点」且不落到 key/点）
- 未指明 instance / pvt / key / 表内点的笼统 PPA 口号（若保留「相对 A 的 %」，必须展开为对 **具体 key（及表内点策略）** 的 ±%）

### 对 YAML 的含义
- `relative_improve_vs_source` 若保留，必须带：`instances`、`pvts`、`keys`、`table_cells`（或 `scalar`）、`delta_pct`（有符号）、`baseline: source_aligned`
- speed 优化：对 delay/min_period 类 key，**`-4%` = 数值 × 0.96** 是否采纳：**建议默认是，仍待 Kai 一句确认**

## 9. 百分比语义冻结（Kai 2026-10-21）

对 **delay / min_period 等「越小越好」的时序类 key**：

- 约束写作 `-4%`（或 `delta_pct: -4`）表示目标值 = **基线数值 × 0.96**
- 对称地，`+4%` = 基线 × 1.04（变慢/变差方向，若业务使用）

对 **power / leakage 等「越小越好」的功耗类 key**：同样默认 **有符号百分比作用于数值乘法**（`-5%` → ×0.95），除非 YAML 对某 key 显式覆盖。

（若本文档已有冲突表述，以本节为准。）

