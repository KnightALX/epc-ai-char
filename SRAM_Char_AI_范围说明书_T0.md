# 《范围说明书》T0 — EPC：跨工艺表征库构造（A.db → B.db）

| 项 | 内容 |
|---|---|
| 文档状态 | **v1 冻结版**（补丁 **v1.0.1**：DEMO 规模脚注 20×40×50）；开放项见 §5，不阻挡开发交接 |
| 产出角色 | EDA需求拆解专家（T0） |
| 编排 | EDA开发任务编排协调器(Top) |
| 主输入 | `/workspace/EPC_项目IO与规则骨架_v0.md`（含 **§8 约束语义冻结**） |
| 数据契约 | `/workspace/SRAM_Char_AI_数据契约_db_v0.md`（逻辑行 / Instance 正则 / 表轴） |
| 方法参考 | Slide 26 TL ≈ 主路径方法核；Slide 24–25、同工艺边角插值 = **引擎算子** |
| 日期 | 2026-10-21（Asia/Shanghai） |
| 纪律 | 不把示例工艺名（N5P/N3P 等）当我方已有数据承诺；不编造误差阈值；未知标「待 Kai 确认」 |
| **官方 DEMO 夹具** | `/workspace/epc_fixtures/`（**合成非 PDK / 非 Foundry 真值**） |
| **DEMO 规模（脚注）** | A_ref：**20×40×50 = 40_000** 行；option=`SWISDC`；表轴 **N=5**；B 列表 9×11 满表验收 **9×11×50=4_950**。详见 T1 v1.1。 |

---

## 0. 一页结论

| 决策项 | 本草案推荐 | 需拍板？ |
|---|---|---|
| **产品一句话** | 用 **A 工艺 `.db`** 的历史风格/趋势 +（可选）**YAML 约束**，为 **B 工艺**按 `instance_list`×`pvt_list` 构造完整 **B.db**（列表可超出 A 的集合） | 知悉 |
| **P0** | **EPC 跨工艺库构造（YAML 驱动）**：I/O 齐全、继承 A 趋势、绝对值表约束 AND、审计报告；列表外延时内嵌调用配置维/PVT 维算子 | 是 |
| **P1** | 分 PVT 组 **相对 A 的 speed%/power%** 约束；更强可信度门禁 / 回写校验 | 是 |
| **P2 / 算子包** | 同工艺边角插值、纯 PVT 缺数解卡 — **同一引擎可复用算子**（可单独产品化） | 是 |
| **硬规则保留** | Instance 正则拆解；表值与 `tran_index`/`load_index` **轴对齐**，禁止打乱 N×N | 知悉 |
| **约束优先级** | **已冻结：用户约束 > 继承 A 风格/趋势**（骨架 §8） | 已拍板 |
| **约束定位** | **已冻结：** 每条约束必须落到 instance + pvt + key + value 内点；目标为范围或 ±X% | 已拍板 |
| **±% 乘法语义（S1）** | **已冻结：** delay/min_period 类 `-4%` = 数值×0.96；功耗类默认同样有符号乘法（`-5%`→×0.95），除非单 key 覆盖 | 已拍板 |
| **开放语义（仍须问卷）** | 对照点（S2）；B field 全集是否=A（S4）；违规 fail vs clip（S5）；表内点寻址（S6） | 是 |

### 相对 v0.2 的纠偏理由

v0.2 把「同工艺边角→内点」当作默认 P0，贴近 compiler 出库子能力，但 **不是 Kai 给出的 EPC 真实主交付**。EPC 主交付是 **跨工艺 A→B 构库**，且 B 的 instance/pvt **可以不被 A 包含**——因此配置维/PVT 维是主路径上的 **子问题/算子**，不应再占据 P0 产品定义（除非 A≡B 的退化特例）。

---

## 1. P0 / P1 / P2 范围

### 1.1 总览（对齐骨架 §6）

| 层级 | 名称 | 交付 | 不在范围 |
|---|---|---|---|
| **P0** | EPC 主路径 | YAML 作业：读 A.db + B 列表 +（可选）绝对值约束 → 写 B.db + 审计；继承 A 风格/趋势；支持列表外延 | 不承诺未钉死的 speed% 语义；无 A.db 空转；不扇出他 bot |
| **P1** | 相对优化约束层 | `relative_improve_vs_source`（分 PVT 组 speed%/power%）；更严门禁与对照点策略落地 | 无对照点定义时的虚假达标 |
| **P2** | 算子产品化 | 同工艺边角插值；PVT 缺数/少仿 — 挂同一引擎，可独立调用 | 替代 P0 成为唯一故事 |

**P0 引擎内部（非独立产品里程碑，但是实现必需）：**

| 算子 | 何时触发 |
|---|---|
| 跨工艺迁移 / 风格继承 | 始终（A→B） |
| 配置维插值/外推 | B.instance ∉ A.instance 集合时 |
| PVT 维插值/外推或缺数补 | B.pvt ∉ A.pvt，或中间态缺字段时 |
| 约束投影 / 校验 | YAML 含 constraints 时（AND） |

### 1.2 P0 — EPC 跨工艺库构造（YAML 驱动）

#### 输入

| # | 输入 | 说明 |
|---|---|---|
| 1 | **A 工艺平台 `.db`** | 参考库（骨架例：N5P — **仅为示例**） |
| 2 | **B `instance_list`** | 目标颗粒；**可不被 A 包含** |
| 3 | **B `pvt_list`** | 目标 PVT；**可不被 A 包含** |
| 4 | **\*可缺省：约束 YAML** | 多条 **AND**；见 §2 |

#### 输出

| 输出 | 要求 |
|---|---|
| **B.db** | instance 数 = 列表长；pvt 数 = 列表长；每个 `(instance,pvt)` 覆盖约定 field 全集的 `key|value` |
| **审计报告** | 规则版本、对照点、约束逐条结果、外推标记、模型/作业指纹 |

#### 要求（Kai）

1. 构造过程 **规则可配置**（优先 YAML），可执行、可复现。  
2. **继承 A** 的历史经验与风格；各 key 趋势与数据特征可信。  
3. 可附加特殊约束，同时保持可信度（与门禁、审计一致）。

#### P0 建议纳入的约束子集

- ✅ 满足 §2.2 的 **绝对值/范围** 约束（`value_range` / `table_upper_bound`），强制带 instance/pvt/key/cell  
- ✅ 基础 `style_from_source`（**永远低于约束**）  
- ⏳ 相对 ±%（`relative_delta_vs_source`）→ **默认 P1**；升 P0 见 Q1b；同样必须四元组+点，禁止笼统 PPA

### 1.3 P1 — 相对 A 的分 PVT 组优化 + 强门禁

- YAML：展开后的 `relative_delta_vs_source`（逐 instance/pvt/key/cell + `delta_pct`）  
- 对照点（S2）、违规策略（S5）必须已拍板；**优先级已冻结为约束优先**  
- 增强：可信度门禁、抽检回写、与出库工具链兼容性（**bit-compatible：待确认**）

### 1.4 P2 — 可复用算子包

- **配置维：** 同工艺（或 A≡B 退化）边角→内点全 PVT×全字段  
- **PVT 维：** Slide 24 缺数解卡；Slide 25 少 PVT 填表  
- 与 P0 共用：Instance 解析、表轴对齐、状态枚举、审计

### 1.5 Instance 解析规则（保留，供 T1/开发共用）

| 段 | 含义 | 示例 |
|---|---|---|
| Vendor | 厂商前缀 | `HI` |
| Process | 工艺平台 | `NP3`（B 列表中的 Process 段应与目标工艺策略一致 — **待确认是否改写 Process 子串**） |
| Family | 数字前产品族 | `TCAM` / `SRAMHCSPEB` / … |
| Geometry | `(\d+)X(\d+)(M\d+)?` | `64X8`、`64X8M2` |
| Options | 其余 | `SWISDC` |

解析失败 → 拒收该 instance。跨工艺时：A/B 的 Vendor+Family+Geometry+Options 对齐规则、Process 段是否重写 → **待 Kai 确认（Q5）**。

### 1.6 表轴对齐硬规则（保留）

1. 表值展平长度 = N×N；与 `tran_index`/`load_index` 长度一致，否则门禁失败。  
2. 跨 instance/工艺比较或迁移时必须 **轴对齐**；默认禁止静默错位插值。  
3. 写回 B.db 保持与契约一致的展平格式。  
4. 范围类约束必须声明 `table_cells`（如 `all_cells`）或 `scalar`；不得默认猜测作用点。

---

## 2. I/O 与 YAML 约束类型（写入范围）

### 2.1 逻辑数据模型

```
A.db / B.db 行：instance_name | pvt | field_key | value
规模语义：行数 ≈ |instances| × |pvts| × C
```

### 2.2 约束语义冻结（Kai 拍板 · 对齐骨架 §8）

| 规则 | 内容 |
|---|---|
| **优先级** | **用户约束 > 继承 A 风格/趋势**。风格迁移不得覆盖或稀释已声明约束。 |
| **合法约束** | 每条 **必须** 显式指定：**instance**、**pvt**、**key**、**value 中的点**；目标为 **范围**（如 `<=800ps`、`[a,b]`）或 **±X%**（相对可解析的 A 侧对照/显式基线）。 |
| **展开规则** | instance 可用列表/通配，但执行前必须展开到具体 instance；表值必须指明表内位置（`(i,j)` / `all_cells` / index 子集）；标量 = 唯一点。 |
| **禁止** | 与 `.db` 无关的自然语言约束；未指明 instance/pvt/key/表内点的笼统 PPA 口号。笼统「speed/power 优化」必须展开为对具体 key（及表内点策略）的 ±%。 |

### 2.3 约束类型（AND；均须满足 §2.2 定位字段）

| type | 含义 | 强制字段 | 建议层级 |
|---|---|---|---|
| `value_range` / `table_upper_bound` | 绝对值范围或上/下界 | `instances`, `pvts`, `keys`, `table_cells`\|`scalar`, `op`+`bound`（或 interval）, 可选 `unit` | **P0** |
| `relative_delta_vs_source` | 相对 A（或显式基线）的有符号 ±% | `instances`, `pvts`, `keys`, `table_cells`\|`scalar`, `delta_pct`, `baseline: source_aligned` | **P1**（默认；若 Kai 要求可升 P0） |

> 旧名 `relative_improve_vs_source` + 笼统 `speed_keys`/`power_keys` **不得**再作为唯一合法写法；若 YAML 仍写分组名，预处理器必须展开成逐条「四元组+点」约束，否则 **拒收作业**。

### 2.4 YAML 作业必备块与约束 schema

作业级块（沿用骨架 §5）：`source` / `target` / `field_policy` / `style_from_source` / `constraints[]` / `output` / `gates`。

**每条 `constraints[]` 元素强制字段（缺一拒载）：**

```yaml
constraints:
  - type: value_range          # 或 relative_delta_vs_source
    instances: ["HINP3TCAM64X8SWISDC"]   # 或 pattern，展开后具体化
    pvts: ["SSGNP_0P99V_0P99V_125C"]
    keys: ["tselr1_min_period"]
    # 表值必填其一：
    table_cells: "all_cells"   # 或 [[0,0],[0,1],...] / flat indices
    # 标量则：
    # cell: scalar
    target:
      mode: range              # range | delta_pct
      op: "<="                 # range 时
      value: 800
      unit: "ps"
      # delta_pct 时改用：
      # delta_pct: -4          # 有符号；已冻结：数值×(1+delta_pct/100)，如 -4→×0.96
      # baseline: source_aligned
```

### 2.5 仍开放的语义（已去掉「约束 vs 风格」）

| ID | 问题 | 状态 |
|---|---|---|
| ~~S1~~ | delay/min_period `-X%`；功耗类同理 | **已冻结：** 数值 × (1 + delta_pct/100)，如 −4%→×0.96、−5%→×0.95；单 key 可覆盖 |
| S2 | B 点不在 A 时，相对约束的对照点如何选 | 待拍板 |
| ~~S3~~ | ~~约束 vs 风格优先级~~ | **已冻结：约束优先** |
| S4 | B 的 field 全集是否必须 = A | 待拍板 |
| S5 | 违规 `fail_job` vs `soft_clip+flag` | 待拍板 |
| S6 | 表内点寻址正式语法（`(r,c)` / 展平下标 / `all_cells`） | 待拍板（三者可并存，须在 schema 枚举） |

## 3. 签核 / 可信度策略（结构）

1. A.db 真值 = 参考种子；**不**在作业中被 ML 覆写。  
2. B.db 默认带生成标记与审计；是否直接进正式出库 .lib → **Q3**。  
3. 外推（instance 或 pvt 超出 A 覆盖）必须 `extrapolated_flag`。  
4. 约束满足：`require_constraint_satisfaction` 为 true 时，按 S5 策略；与风格冲突时 **以约束为准**。

---

## 4. 成功标准结构（阈值留空）

| 类 | 结构 |
|---|---|
| I/O 完备 | \|B.inst\|=列表；\|B.pvt\|=列表；白名单 field 无静默空洞 |
| 风格/趋势 | 相对 A 的趋势一致性度量（定义 **待填**）；抽检 key 曲线形态 |
| 绝对值约束 | 逐条 constraint pass rate；P0 建议 100% 或按 S5 |
| 相对 %（P1） | 按 pvt_group×key_group 达标；对照点可审计 |
| 轴完整性 | 表轴对齐检查 100% |
| 基线 | 朴素「拷贝 A 近邻再缩放」必须可被 EPC 主模型对比（定义待填） |
| 复现 | 同 YAML + 同 A.db → B.db 比特级或数值容差内可复现（**待确认**） |
| 审计 | 每 job 必出报告 |

---

## 5. 给 Kai 的决策问卷

**Q0. 样例资产** — **DEMO 已满足（冻结）**  
- [x] A.db：`/workspace/epc_fixtures/A_ref.db`（合成，**20×40×50=40000** 行，option=`SWISDC`，N=5）  
- [x] B lists：9 instance（3∉A）× 11 pvt（3∉A）；满表验收 **4950** 行  
- [x] 合法约束 YAML：`epc_job.sample.yaml`  
- 生产真库替换 DEMO 时另开变更，不自动解除「合成非 PDK」标注  

**Q1. P0 主线确认**  
- [ ] **A. 采纳：P0=EPC 跨工艺 YAML 构库（推荐）**  
- [ ] B. 仍坚持 P0=同工艺边角插值（EPC 降级）  
- [ ] C. 双 P0：EPC + 同工艺边角必须同里程碑  

**Q1b. 相对 ±% 约束（必须已能展开到 instance/pvt/key/cell）**  
- [ ] 进 P0 必达  
- [ ] **留 P1（推荐）**  

**Q2. field 全集（S4）**  
- [ ] B 必须 `all_from_source` 与 A 同 key 集  
- [ ] `explicit_list`（附列表）  
- [ ] 待 .db introspection 后定  

**Q3. B.db 与出库**  
- [ ] 仅内部  
- [ ] 可进正式 .lib（责任人____）  
- [ ] 进 .lib 前必须抽检真仿门禁  
- [ ] 是否需与现有出库工具 **bit-compatible**：[ ] 是 [ ] 否 [ ] 待查  

**Q4. 开放语义拍板（优先级已冻结：约束 > 风格，不必再选）**  
- ~~S1~~：**已冻结** delay/min_period 与功耗类默认 `×(1+delta_pct/100)`（单 key 可覆盖）
- S2 对照点策略：________  
- S5 违规： [ ] fail_job [ ] soft_clip+flag  
- S6 表内点寻址： [ ] 允许 `(r,c)` + `all_cells` + 展平下标 三选（推荐） [ ] 仅一种：________  

**Q5. 跨工艺 Instance 命名**  
- B 列表里 Process 段是否改为 B 工艺名： [ ] 是 [ ] 否 [ ] 混合  
- Options/Family 必须与 A 可对齐的规则：________  

**Q6. 相对约束的 key 清单**  
- 提供将「speed/power」展开后的 **具体 field_key 列表**（及默认 `table_cells`），或 [ ] 委托按样例 key 起草后你再改  

**Q7. 精度 / 可信度门禁**  
- 内插 vs 外推区分阈值：________（可待定）  

**Q8. 表轴**  
- [ ] 沿用「族内黄金轴 / 从 A 对齐轴」（推荐方向）  
- [ ] 其他：________  

**Q9. 工具策略**  
- [ ] 全自研引擎 [ ] 外购+薄自研 [ ] 先自研 MVP  

**Q10. 合规**  
- air-gapped： [ ] 是 [ ] 否；A/B .db 跨客户混用： [ ] 禁止（推荐） [ ] 允许  

---

## 6. 下游接口预告

### 6.1 T1 schema / 作业对象必钉

| 组 | 字段/对象 |
|---|---|
| Job | `job_id`, YAML 原文指纹, `source_db_id`, `target_process` |
| 列表 | `instance_list[]`, `pvt_list[]`（含 ∈A / ∉A 标记） |
| 行 | 四元组 + `value_kind` + 表轴还原 |
| Instance 解析 | vendor/process/family/depth/width/mux/options |
| 约束 | 规范化记录：强制 `instances/pvts/keys/table_cells|scalar` + target；展开日志；逐条 evaluate |
| 对照点 | `reference_instance`, `reference_pvt`, `reference_mode`（S2） |
| 状态 | seed_from_A / migrated / config_extrapolated / pvt_extrapolated / constraint_clipped / … |
| 输出 | B.db 路径、audit 路径 |

### 6.2 开发钉死

- P0：YAML 加载 → 校验约束强制字段 → 解析列表 → 继承 A →（必要时）配置/PVT 算子 → **约束投影（优先于风格）** → 写 B.db + audit  
- 相对 ±% 默认特征开关，P1 打开；加载时拒绝笼统 PPA  
- 禁止：无审计出库；打乱表结构；未解析 instance；缺 instance/pvt/key/cell 的约束

### 6.3 测试钉死

- 黄金 job：小 A.db 子集 + 显式列表 + 上界约束  
- ∉A 的 instance/pvt 外延用例  
- 约束 AND、违规 fail/clip  
- 轴对齐负面用例  
- 复现性  

### 6.4 编排（不扇出）

```
EPC 骨架 + 说明书 v0.3.2 → Kai 答卷（Q0/Q1/Q4：S2/S4/S5/S6）
  → 冻 v1 → T1 → 开发/测试
```

---

## 7. 开放问题汇总

见 §2.5（S1/S3 已冻结）与 §5；另：Family 枚举、样例 .db、出库 bit-compat、单位制。

---

## 8.1 v1 冻结说明（2026-10-21）

| 已冻结 | 内容 |
|---|---|
| 产品主线 | EPC：A.db → B.db，YAML 驱动；列表可外延 |
| 约束 | 约束 > 风格；强制 instance/pvt/key/cell；±% = ×(1+δ/100) |
| DEMO 夹具 | `/workspace/epc_fixtures/`；**20×40×50=40000**；**合成非 PDK** |
| T1 入口 | 物理表 `char_data(instance,pvt,field_key,value)` 见 `/workspace/EPC_T1_数据字典.md` |

| 仍开放（不挡 T1） | S2 对照点细化、S4 生产 C 全集、S5 若偏离 sample 的 fail_job、S6 寻址方言扩展、真 PDK 替换 |

## 8. 修订记录

| 版本 | 说明 |
|---|---|
| v0–v0.1 | Slide24 / field_key 白名单 |
| v0.2 | P0=同工艺配置维边角插值 |
| v0.3 | P0=EPC 跨工艺 YAML 构库 A→B；相对%默认 P1；边角/PVT=引擎算子或 P2 |
| v0.3.1 | 约束语义冻结：约束>风格；强制 instance/pvt/key/cell；禁笼统 PPA |
| v0.3.2 | 关闭 S1：±% = 数值×(1+delta_pct/100) |
| v1 | 冻结版：挂接 epc_fixtures；Q0 DEMO 已满足；启动 T1 |
| **v1.0.1** | **补 DEMO 规模脚注：20×40×50=40000；B 满表 4950；对齐 T1 v1.1（不改产品范围）** |

---

## 9. 给编排器的变更摘要

### v1 → v1.0.1（夹具扩容后）
1. 范围说明书仅补 **DEMO 规模脚注**（20×40×50 / B=4950），产品范围不变。  
2. T1 升 **v1.1**：`/workspace/EPC_T1_数据字典.md`。  
3. **仍不扇出开发**——由编排器交接代码工程师做 P0 MVP。

### v0.3.2 → v1（历史）
1. 范围 v1 冻结 + 官方 DEMO 夹具。  
2. Q0 DEMO 已满足。  
3. T1 首版数据字典。  

---

*路径：`/workspace/SRAM_Char_AI_范围说明书_T0.md`（**v1.0.1**）*  
*夹具：`/workspace/epc_fixtures/`*  
*T1：`/workspace/EPC_T1_数据字典.md`（**v1.1**）*
