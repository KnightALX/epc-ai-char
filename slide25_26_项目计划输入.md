# AI-Assisted SRAM Compiler Characterization — 项目计划输入研究报告

> **用途**：编排协调器 / 需求拆解 / 开发 / 测试的统一技术输入  
> **来源锚点**：TSMC Jonathan Chang, 2026 IEEE VLSI SC2-2《AI for accelerating memory design》（Slide 24–26）  
> **调研范围**：公开文献方法族、Foundry/IP 行业实践、主流 EDA 厂商公开能力（不编造未公开的内部数字或论文标题）  
> **日期**：2026-10-21（Asia/Shanghai）  
> **状态**：可直接作为项目计划输入；末尾含待业务确认清单

---

## 0. 一页纸摘要（给决策者）

| 维度 | 结论 |
|------|------|
| **在做什么** | 用少量「真仿真」PVT 点 + 历史/同源参考数据，预测 SRAM Compiler 全 PVT 表征表（timing/power/约束等），替代「每个 corner 全量 SPICE」或失败的线性 Transfer Ratio。 |
| **为什么难** | PVT 维数高（工艺角×电压×温度×可选模式可达数百）；电路行为在低压/近阈值区强非线性；跨工艺版本（如 N3E→N3P）相关也是非线性；极值 corner 仿真易失败。 |
| **成熟做法谱系** | 传统：全仿 / 多项式 compiler 模型 / 线性 scaling / RSM；现代：corner reduction + Surrogate（GPR/GBDT/MLP）+ Active Learning 选点 + Transfer / Multi-fidelity；商业侧：Cadence Liberate ML、Synopsys PrimeLib SmartScaling/ML、Siemens Solido Generator/Characterizer。 |
| **与 Slide 对应** | App-1≈同设计内稀疏仿真+填表；App-2≈旧设计/旧工艺全表作 Ref + 新侧少量 seed；Slide 26≈跨工艺 Transfer Learning 取代单点 Transfer Ratio；Slide 24≈用 >99% 已有点预测 <1% missing，解卡交付。 |
| **建议我们怎么做** | MVP：同工艺内 GPR/GBDT + 固定 hold-out 校验门禁；增强：Active Learning + 跨版本 Transfer；签核级仍保留关键 corner 真仿真。 |
| **最大风险** | 外推到未覆盖的极值区；过拟合「中间区」；把预测值当签核真值；Foundry/客户数据合规与模型可解释性不足。 |

---

## 1. 问题本质：工程语言说清「在做什么」

### 1.1 业务语境（来自讲稿）

TSMC 讲稿将表征放在 memory IP 交付关键路径上：先进节点下 **PVT × 配置 × 指标** 的仿真量是交付瓶颈；部分极值条件还会仿真失败，拖住整条 IP 流水线。

- **Slide 24（相邻）**：仿真失败导致 **<1% missing points**；用已有 **>99%** 数据 AI 预测补齐，让 IP 团队先往下走，EDA 工具问题并行修，最后再回仿校验并交付。
- **Slide 25**：AI-Assisted **SRAM Compiler Characterization** 两条应用。
- **Slide 26**：跨工艺版本（示例 **N3E → N3P**）的 **Transfer Learning**，取代失败的线性 Transfer Ratio 脚本。

### 1.2 输入 / 输出（系统视角）

```
输入（典型）
├── 设计侧：SRAM leaf / critical-path netlist、compiler 配置空间（words×bits×mux、bank、Vt 选项…）
├── 工艺侧：PDK/SPICE model、process corner 定义、可选 aging/EM
├── 条件侧：PVT 表（P×V×T，可能再乘 mode：read/write/retention、半选等）
├── 参考侧（App-2 / Transfer）：旧设计或旧工艺的「全量」表征数据库
└── 稀疏仿真：已跑通的 seed / partial PVT 结果 + 失败点清单

输出（典型）
├── 完整或近完整 PVT 表征表（预测填洞 / 预测填表）
├── 不确定性 / 置信度（哪些点必须回仿）
├── 可选：Liberty(.lib) / datasheet 数值 / compiler 多项式系数
└── 校验报告：相对真仿真误差、outlier、门禁通过与否
```

### 1.3 PVT 空间长什么样

工程上「一个 PVT」通常是离散点：

| 轴 | 常见内容 | 备注 |
|----|----------|------|
| **P（Process）** | TT/FF/SS/SF/FS，或 foundry 定义的更多 corner（含全局+局部变异相关定义） | 先进节点 corner 名与数量因 PDK 而异 |
| **V（Voltage）** | VDD 档位、可选 VCS/VDDP、多电源域 | 近阈值区非线性强 |
| **T（Temperature）** | −40 / 25 / 85 / 125℃ 等 | 漏电/时序温度系数可反向 |
| **模式 / 操作** | read、write、RMW、retention、bypass… | 不同 arc 不同指标 |
| **Compiler 配置** | 容量、列复用、bank、IO 位数 | Compiler 常对「实例族」建 surrogate，而非每个实例全仿 |

讲稿中 **PVT 1…300** 是数量级示意：同一 compiler / 同一宏在「全角 × 全压 × 全温 × 多模式」下，表征点可达数百量级；再乘实例配置则更大。

### 1.4 典型被表征 / 被预测的指标

按用途分组（项目需明确哪些进 Liberty、哪些只进 datasheet / 内部 QC）：

| 类别 | 指标示例 | 下游用途 |
|------|----------|----------|
| **Timing / 约束** | access time、cycle time、setup/hold、clock-to-Q、recovery/removal | STA、综合约束 |
| **Power** | dynamic energy（read/write）、leakage、待机电流 | 功耗分析、IR |
| **稳定性 / 功能裕度** | SNM（read）、write margin、retention SNM、Vmin | 良率与低压可行性（常不直接进 .lib） |
| **电流波形类** | CCS/ECSM 相关电流、AVM/IR 电流剖面 | 先进 STA、电源完整性 |
| **统计类（可选）** | LVF/POCV sigma、high-sigma 失效概率 | 签核变异建模 |

**本质一句话**：在「昂贵的晶体管级仿真」与「必须交付的稠密 PVT 表」之间，建一个 **有物理一致性约束的、可校验的回归/迁移模型**，把仿真预算花在最有信息量的点上。

### 1.5 与「标准单元库表征」的同构与差异

| | Standard Cell Library | SRAM Compiler Characterization |
|--|----------------------|--------------------------------|
| 同构 | 都是 PVT×arc 上的查表；都可做 sparse char + ML 填表 | — |
| 差异 | 单元小、arc 规则清晰、工具链极成熟 | 宏大、常 critical-path / 分区仿真；compiler 还要跨配置泛化 |
| 商业工具 | Liberate / PrimeLib / Solido 主战场 | Liberate MX 等 memory char；compiler 内部常自建 surrogate |

我们的项目若对标讲稿，**主目标更接近「compiler / memory IP 的多 PVT 表」**，可借鉴 stdcell 的 ML 表征方法，但不能假设直接套用 stdcell 黑盒工具即覆盖 SRAM 全部指标（尤其 SNM/Vmin）。

---

## 2. 怎么做：从传统到现代的方法论栈

自上而下是「成熟度 / 可解释性」谱系；项目选型应明确落在哪一层、签核边界在哪。

### 2.1 L0 — 暴力全仿真（Baseline）

- **做法**：每个目标 PVT（及必要配置）跑 SPICE / FastSPICE（memory 常用分区 + critical path）。
- **优点**：金标准；可解释。
- **缺点**：TAT 与机器成本爆炸；极值点失败会堵交付（Slide 24 痛点）。

### 2.2 L1 — 解析 / 经验缩放（传统工业脚本）

- **单点 Transfer Ratio + 线性映射**（讲稿点名失败案例）：  
  `metric_N3P(PVT_i) ≈ TransferRatio × metric_N3E(PVT_i)` 或对 V/T 做线性插值。
- **Voltage/Temperature derating、corner scaling**。
- **优点**：实现快、零训练数据门槛。
- **失败模式**：低压、跨 Vt、跨工艺微缩后 **非线性相关** 主导 → 趋势都对不上（Slide 26）。

### 2.3 L2 — Compiler 多项式 / 响应面（RSM）

- 对少量「锚点实例 × 锚点 PVT」拟合多项式（或分段多项式），compiler 生成任意配置时插值。
- **行业现实**（公开白皮书常见叙述）：对 NLDM 尚可「加 margin 凑合」；对 **CCS/ECSM** 与先进节点精度压力大，常被迫做 **instance-specific re-char**。
- **优点**：部署进 compiler 简单。  
- **缺点**：强非线性区与跨工艺迁移差。

### 2.4 L3 — 统计实验设计 / Corner Reduction（不换模型，先减点）

- 用工程经验或聚类选出「必须真仿」的 critical corners，其余用缩放或后处理生成。
- 与商业工具的 「prediction out / SmartScaling」叙事同构：先仿锚点库，再生成中间 PVT。

### 2.5 L4 — 同域 Surrogate（Slide 25 App-1）

**设定**：同一设计（或同一 compiler 版本 / 同一工艺），已仿 1–50 个 PVT，预测 51–300。

推荐管线：

1. 特征：`[process_onehot / continuous process params, V, T, mode, …]`；可选设计描述符（mux、words、bits）。
2. 标签：各 metric（可 log 变换 leakage 等）。
3. 模型：GPR（小样本+UQ）或 GBDT（表格强基线）或浅层 MLP。
4. 校验：固定 hold-out 真仿点；分区域（高 V / 低 V）报误差。
5. 门禁：高不确定或超出训练凸包 → 强制回仿。

### 2.6 L5 — 跨域 / 少样本（Slide 25 App-2 + Slide 26）

**设定 A（App-2）**：旧设计/旧工艺有完整 Ref；新设计/新工艺只仿少量 seed → 预测其余。  
**设定 B（Transfer）**：源工艺全 PVT + 目标工艺少量 PVT → 学非线性跨工艺映射，并利用源域内部 PVT 相关。

方法族：

- **Fine-tune / 特征复用**：源域预训练 DNN/GBDT，目标域冻层或小学习率微调（学术常见「PVT-aware transfer」方向）。
- **Domain adaptation**：对齐源/目标特征分布后再回归。
- **Multi-fidelity**：把「旧工艺全表」当低保真、把「新工艺稀疏真仿」当高保真，学校正项（Δ-learning）。
- **Residual transfer**：先用线性 Transfer Ratio 作弱先验，再学非线性残差（工程上可解释性较好）。

### 2.7 L6 — Active Learning / 序贯选点

模型给出不确定性或期望误差下降 → 下一轮仿真预算打在最有价值的 PVT → 再训练。  
与「固定先仿 50 点」相比，同样预算通常更能压住最差点误差（学术上 GPR+AL 做 CCS / setup-hold 多角表征是常见方向）。

### 2.8 L7 — 交付闭环（Slide 24 运营层）

```
全量任务排队 → 大部分成功 → 失败点 AI 填洞（标 provisional）
→ IP 下游继续 → 工具修复 / 资源空闲后回仿 missing
→ 对比预测 vs 真值 → 更新模型 / 放行或撤回 provisional
```

这是 **工程交付策略**，不是纯算法：必须有「provisional vs golden」状态机与责任边界。

---

## 3. EDA 领域成熟方案

### 3.1 Foundry / IP / 行业常见实践（公开叙述可核对）

1. **Memory Compiler 路径**  
   - 叶单元 + critical-path netlist 表征 → 拟合 compiler 时序/功耗模型 → 生成任意实例的 .lib / datasheet / AVM。  
   - 精度不足时：对关键实例做 **instance-specific characterization**（Cadence 等公开材料明确讨论 compiler 多项式局限与再表征需求）。

2. **Memory 表征工具路径**  
   - 分区（static / dynamic partitioning）+ FastSPICE 全块探路 + SPICE 精表征子块 → 产出 Liberty timing/power/noise。  
   - 代表公开产品能力：**Cadence Liberate MX**（memory/macro characterization）。

3. **多 PVT 减负**  
   - 锚点 corner 真表征 + scaling / ML 生成中间 PVT。  
   - 统计库：LVF 与 nominal 统一 flow（减少后期 merge）。

4. **QC**  
   - .lib 一致性、单调性、outlier、与 SPICE 抽检相关；Siemens Solido Analytics 等公开强调 ML outlier + 规则检查。

### 3.2 学术界代表性路线（方法族，不编造具体标题数字）

下列均为 **常见研究方向**（可在 DAC/ICCAD/DATE/TCAD/TODAES/MLCAD 检索到同主题工作；具体论文以你们内部文献库为准）：

| 方向 | 在解决什么 | 常见技术 |
|------|------------|----------|
| **Stdcell CCS/NLDM 加速表征** | 波形/查表点太多 | GPR + Active Learning；插值+偏置校正 |
| **多 PVT Liberty 推断** | 从参考库 + PVT 特征生成目标角 .lib | MLP/Mixer 类表格模型（如公开报告的 LIBMixer 类工作） |
| **统计 timing char** | LVF/相关与寄生 | 图网络 + AL；寄生 RC 压缩 |
| **SRAM 时序/良率** | access path、read yield、Vmin | ML 辅助 netlist 提取；失效边界建模；Monte Carlo 加速 |
| **跨节点 Transfer** | 源节点模型 → 目标节点少样本 | DNN transfer / domain equalization（TODAES 等可见 PVT-aware transfer、embedded memory PPA transfer 类工作） |
| **波形/图学习仿真代理** | 替代部分 SPICE 波形 | GNN 波形传播（加速仿真本身，与「PVT 表回归」互补） |

**与讲稿对齐的学术表述**：

- App-1 ↔ **same-domain sparse regression / AL**  
- App-2 ↔ **few-shot + reference library conditioning**  
- Slide 26 ↔ **cross-technology transfer learning / multi-fidelity correction**

### 3.3 商业 EDA 公开能力对应（有公开依据才写）

> 下列为厂商官网/新闻/产品页公开表述的能力映射；**内部算法细节与可复现精度未公开处标「不确定」**。营销数字（如「Nx faster」）仅作存在性参考，**不作为我们项目的验收承诺**。

| 厂商 / 产品 | 与讲稿问题的对应 | 公开依据要点 | 不确定点 |
|-------------|------------------|--------------|----------|
| **Cadence Liberate Trio + ML option** | App-1 类：中间 PVT prediction out；缩短 TAT 的 prediction in；critical corner clustering | 官网：ML 预测 critical corners；prediction out 从已全表征库推导 intermediate PVT；prediction in 加速表征 | SRAM compiler 内部指标（SNM 等）是否覆盖；跨工艺 transfer 是否一等公民 |
| **Cadence Liberate MX** | Memory/macro 真表征基础设施（分区、分布式仿真、.lib） | 产品页/白皮书：memory characterization、dynamic partitioning | 本身不是「AI 填 PVT 表」；AI 需自建或与 Trio ML 组合（组合方式项目需确认） |
| **Synopsys PrimeLib** | 多 PVT：SmartScaling；ML：high-sigma char、更快 LVF、PDK 更新的 ML sensitivity DB | 产品页明确列出 SmartScaling、ML-based high-sigma、ML LVF、ML augmented sensitivity database | SmartScaling 与「非线性 ML transfer」是否同一机制：**不确定**；更像工业 scaling + ML 加速，而非讲稿式跨 N3E→N3P TL |
| **Siemens Solido Characterization Suite** | Generator：锚点 .lib → 生成更多 PVT 视图；Characterizer：AI 加速 SPICE 表征；Analytics：QA | 新闻稿/资料：Characterizer AI 引擎、LibSPICE；Generator 用 baseline .lib 训练以生成额外视图（公开称可不跑额外 SPICE） | 对 SRAM compiler 全指标栈的覆盖；跨工艺 TL 细节 |
| **开源/学术原型** | 小规模 stdcell NLDM/CCS 流水线 | 如社区工具链可做 ngspice→.lib；研究代码做 GPR+AL | 不具备生产级 memory 分区与签核 QA |

**映射结论（给计划用）**：

- 讲稿 App-1 / missing-point ≈ 与 **Liberate ML prediction**、**Solido Generator**、**PrimeLib SmartScaling** 同一问题族。  
- 讲稿 Slide 26 跨工艺 **非线性 Transfer Learning** ≈ 学术/自研色彩更重；**三大厂是否提供「N3E→N3P SRAM 全表 TL」一键能力：公开材料不足以断言，应标不确定，倾向「需自研或深度定制」**。

---

## 4. 常用算法族（按场景、优劣、何时用）

### 4.1 插值 / 外推

| | |
|--|--|
| **适用** | 网格规则、行为近似线性/可分（高 V、中间温区）；快速填洞原型 |
| **优点** | 零训练、可解释、实现一天级 |
| **缺点** | 外推危险；低压/跨角非线性差（讲稿明确不如 AI） |
| **何时用** | MVP 对照基线；禁止作为唯一签核手段 |

### 4.2 响应面 / RSM / 多项式

| | |
|--|--|
| **适用** | Compiler 配置空间平滑区；与历史 compiler 模型兼容 |
| **优点** | 嵌入 compiler 容易；系数可审计 |
| **缺点** | 阶数爆炸；CCS/强非线性吃力 |
| **何时用** | 需与现有 compiler 交付格式兼容时作主干或残差载体 |

### 4.3 高斯过程 GPR

| | |
|--|--|
| **适用** | **小样本** App-1；需要 **不确定性** 驱动 AL / 回仿门禁 |
| **优点** | UQ 天然；数据少时往往稳健 |
| **缺点** | O(n³) 难扩到极大表；高维特征需核/稀疏近似精心设计 |
| **何时用** | MVP 首选之一；AL 循环的标配 surrogate |

### 4.4 随机森林 / GBDT（XGBoost/LightGBM 等）

| | |
|--|--|
| **适用** | 中等样本量的表格 PVT→metric；多输出可分模型 |
| **优点** | 强基线、特征重要度、训练快、对尺度不敏感 |
| **缺点** | 外推弱于带平滑先验的模型；UQ 需额外校准（分位数/jackknife） |
| **何时用** | App-1 生产基线；与 GPR 做 ensemble |

### 4.5 MLP / DNN

| | |
|--|--|
| **适用** | 大数据 Ref（App-2）；跨域 pretrain→finetune（Slide 26） |
| **优点** | 表达非线性强；易做多任务（同时预测 timing+power） |
| **缺点** | 小样本过拟合；需强正则与物理约束；UQ 需 ensemble/MC-dropout 等 |
| **何时用** | 有完整旧库时；Transfer Learning 主干 |

### 4.6 物理先验 / Hybrid

| | |
|--|--|
| **做法** | 先物理/经验公式或线性 ratio，再学残差；或对 leakage 用 Arrhenius/指数特征，对 delay 用饱和速度相关特征 |
| **优点** | 小样本泛化与可解释性更好；易过门禁审计 |
| **缺点** | 先验错了会系统性偏置 |
| **何时用** | **强烈推荐**作为工程默认结构（残差学习） |

### 4.7 Transfer / Domain Adaptation / Multi-fidelity / Few-shot

| 子类 | 场景 | 要点 |
|------|------|------|
| **Fine-tune TL** | 旧工艺 DNN → 新工艺 | 源域要够全；目标 seed 要覆盖凸包边界 |
| **Domain adaptation** | 特征分布偏移大 | 需无监督对齐或少量标签 |
| **Multi-fidelity** | 粗模型/旧节点 vs 精仿真 | 学 Δ；预算分配到高保真点 |
| **Few-shot / meta** | 频繁新 compiler 版本 | 学术可见；工程落地成本高，增强阶段再议 |

讲稿两点机制必须落地到实现：

1. 学 **跨工艺非线性相关**（不是单 ratio）。  
2. 利用 **旧工艺内部 PVT 间相关** 提升新工艺预测（可做成源域协方差 / 联合模型 / 多任务）。

### 4.8 Active Learning / 实验设计

| 策略 | 思想 | 注意 |
|------|------|------|
| Uncertainty sampling | 采预测方差大的点 | 易采噪声点，需与「工程关键角」先验混合 |
| Space-filling（LHS 等） | 先铺满空间 | 作初始设计好；后期不如模型驱动 |
| Expected improvement / 批量化 AL | 平衡探索利用 | 实现复杂，增强版再上 |
| Critical-corner 先验 | 强制包含 SS+低压+高温等 | **必须**，避免纯数据驱动漏掉签核角 |

### 4.9 不确定性量化（UQ）与回仿门禁

**建议门禁逻辑（项目可直接写成需求）**：

1. **训练凸包外**（V/T/process 外推）→ 禁止只靠预测交付。  
2. **预测 σ 或 ensemble 分歧 > 阈值** → 回仿。  
3. **物理规则破坏**（如 delay 随 V 升高而变差超过容差、查表非单调）→ 回仿或人工审。  
4. **签核集合**（客户合同/ STA signoff corners）→ **永远真仿真**，ML 只用于非签核中间角或 provisional。  
5. **Slide 24 missing**：provisional 入库必须带 flag；回仿后误差超阈 → 触发模型重训与下游通知。

---

## 5. 推荐技术选型（若我们做项目）

### 5.1 目标分层（避免一口吃签核）

| 层级 | 目标 | 成功标准（建议） |
|------|------|------------------|
| **P0 交付解卡** | Slide 24：missing <1% 填洞 | 回仿后相对误差达标；不阻断 IP 流水线 |
| **P1 同工艺加速** | Slide 25 App-1 | 真仿比例降到约定值（例：20–30% 量级，**待标定**），关键角误差达标 |
| **P2 跨版本迁移** | App-2 + Slide 26 | 新工艺 seed 比例显著低于 P1；优于线性 Transfer Ratio 基线 |

### 5.2 MVP（6–10 周量级，示意）

**范围**：单工艺、单一 SRAM 家族、指标先做 **access/cycle + read/write energy + leakage**（SNM/Vmin 第二期）。

**技术**：

1. 基线：网格插值 + 线性 Transfer Ratio（必须有，作对照）。  
2. 主模型：**GBDT 或 GPR（残差 = 真值 − 线性先验）**。  
3. 数据：历史已跑 PVT 表清洗 → 统一 schema。  
4. 校验：分层 hold-out（按 V 分段）；报告 p50/p95/max \|相对误差\|。  
5. 门禁：凸包 + σ 阈值 + 签核角强制仿真。  
6. 产出：预测表 + QC 报告，**不直接宣称替代签核**。

**数据需求（量级，需用你们真实表校准）**：

- 启动：至少 **一个** 完整或近完整 PVT 表作离线评估；  
- 在线：App-1 建议初始 seed **覆盖边界角**（不是随机中部 50 点）。

### 5.3 增强版路径

| 阶段 | 增强 | 依赖 |
|------|------|------|
| E1 | Batch Active Learning 选下一轮仿真 | MVP 的 UQ 可用 |
| E2 | 多任务网络（timing+power 共享表征） | 更多干净标签 |
| E3 | 跨工艺 Transfer / multi-fidelity Δ 模型 | 成对 N3E↔N3P（或等价）对齐 PVT 表 |
| E4 | 接入 Liberate MX / 现有 char 流水线自动回仿 | 工具与 license |
| E5 | SNM/Vmin/统计 LVF | 专门仿真 deck；指标定义与业务对齐 |

### 5.4 验收指标建议（写入测试专家用例）

> 具体阈值必须由业务/签核负责人拍板；下列是 **结构建议**，不是承诺数字。

1. **精度**：按指标分组的相对误差分布（p50/p90/p95/max）；低压区单独报表。  
2. **基线对比**：必须击败「最近邻插值」与「线性 Transfer Ratio」。  
3. **校准**：高置信预测的实际命中率（reliability diagram）。  
4. **覆盖**：签核角 0 预测替代；provisional 点 100% 可追溯。  
5. **效率**：真仿点数 / 总点数；端到端 TAT；失败点解卡时间（对照 Slide 24）。  
6. **回归**：模型版本变更时，对黄金集的误差不得无故变差。  
7. **下游抽样**：抽若干预测 .lib 进 STA，关键 path 与真 .lib 差异在约定 bound 内（增强阶段）。

### 5.5 与三 bot 流水线的接口（给编排器用）

```
需求拆解专家
  → 明确：指标清单、PVT 字典、签核角、provisional 策略、数据合规

代码开发工程师
  → 数据 schema、训练/推理服务、与仿真队列/回仿 API、QC 报告

测试验证专家
  → 黄金集、分层误差、门禁单测、对抗用例（极值/缺失/工艺跳变）
```

---

## 6. 风险与坑

| 风险 | 表现 | 缓解 |
|------|------|------|
| **过拟合中间区** | 平均误差好看，SS+低压崩 | 分层报表；强制边界 seed；物理残差 |
| **外推失效** | 训练从未见过的 V/T | 凸包检测；禁止静默外推 |
| **Corner 极值 / 仿真失败相关** | 失败点恰是最难预测的点 | Slide 24 流程 + 失败点优先回仿；不要用失败点邻近瞎插 |
| **工艺跳变过大** | N3E→差一代以上或 DTCO 大改 | 降低 TL 权重；增加目标 seed；分 metric 决定能否迁移 |
| **指标异构** | timing 可迁、SNM 不可迁 | 分模型；禁止一刀切 |
| **把预测当黄金** | 错误 .lib 进签核 | 状态机：predicted / validated / signoff |
| **数据泄漏** | 同仿真重复进 train/test | 按 PVT 组分割，不按行随机 |
| **配置空间混淆** | 不同 mux/bank 当同分布 | 特征加配置；或分配置建模 |
| **Legal / 合规** | PDK、客户 .lib、跨厂数据不能混训 | 数据分级；模型按工艺/客户隔离；训练日志审计 |
| **工具链漂移** | 换 SPICE 版本导致标签偏移 | 标签带 tool fingerprint；重训触发器 |
| **可解释性不足** | 客户/Foundry 拒收黑盒 | 残差模型 + 敏感性报告 + 抽检 SPICE |

---

## 7. 与讲稿三条应用的直接对照表

| 讲稿 | 问题形式 | 推荐方法核 | 商业近似 | 我们 MVP |
|------|----------|------------|----------|----------|
| Slide 24 Missing | 已知 >99%，补 <1% | 局部 GPR/GBDT + 强制回仿队列 | 库 QA/填洞脚本 | **优先做**：解卡价值高、数据已在 |
| Slide 25 App-1 | 同设计稀疏→稠密 | Surrogate + 边界 seed + UQ 门禁 | Liberate ML prediction、Solido Generator、PrimeLib SmartScaling | MVP 主路径 |
| Slide 25 App-2 | Ref 全表 + 新侧少 seed | Conditioning / multi-fidelity / fine-tune | 部分 Generator「参考库」叙事；细节不确定 | MVP+ |
| Slide 26 TL | N3E→N3P 非线性 | Residual TL + 源域 PVT 相关 | **公开一键能力不确定** → 自研重点 | 增强版 E3 |

---

## 8. 参考与公开来源（可核对，非完整文献综述）

**讲稿**  
- TSMC Jonathan Chang, 2026 IEEE VLSI SC2-2, *AI for accelerating memory design*（用户提供 PDF；Slide 24–26 文本已核对）。

**行业 / 产品公开页（能力存在性）**  
- Cadence Liberate Trio Characterization Suite（含 ML prediction in/out、multi-PVT）。  
- Cadence Liberate MX Memory Characterization；memory compiler vs instance-specific char 相关白皮书叙述。  
- Synopsys PrimeLib（SmartScaling、ML high-sigma、ML LVF、ML sensitivity DB）。  
- Siemens Solido Characterizer / Characterization Suite / Generator / Analytics（2026 新闻稿等）。

**学术方法族入口（示例方向，检索用）**  
- Transfer learning for PVT-aware circuit performance（TODAES 等）。  
- Embedded memory PPA models with transfer across compiler/tech（低数据饮食类工作）。  
- GPR + Active Learning for CCS library characterization。  
- ML-assisted multi-PVT / Liberty inference（如 ASP-DAC 公开的 LIBMixer 类报告）。  
- SRAM variation-aware timing / yield estimation 类 TCAD/DAC 方向。

> **纪律**：上文避免写入未经你们核对的「精确加速比 / 误差百分比」作为项目承诺；厂商营销数字与单篇论文数字需单独引用评审后再进 KPI。

---

## 9. 待向业务确认的问题清单

### 9.1 范围与成功定义

1. 第一期要对齐的是 **Compiler 出库 .lib**、**内部 datasheet**，还是 **两者都要**？  
2. 指标白名单：是否包含 SNM / write margin / Vmin / LVF，还是仅 timing+power？  
3. 「签核角」完整列表是什么？哪些角 **绝对禁止** ML 替代？  
4. P0 是否就是 Slide 24 解卡？还是必须同时交出 App-1 加速？

### 9.2 数据与工艺

5. 可用的历史全 PVT 表有几套？覆盖哪些工艺（是否已有类似 N3E/N3P 成对数据）？  
6. PVT 字典与命名是否跨版本对齐？Transfer 时如何定义「同一 PVT」？  
7. 仿真金标准工具链（Spectre/HSPICE/FineSim/XA…）与版本钉扎策略？  
8. Critical-path 与 full-instance 表征各占哪些指标？

### 9.3 精度与流程

9. 各指标可接受的 p95 相对误差 / 绝对误差分别是多少？低压区是否更严？  
10. Provisional 预测结果是否允许进入下游 STA 试跑？责任人是谁？  
11. 回仿后发现超差，下游撤回流程是否已有？

### 9.4 工具与组织

12. 是否已有 Cadence Liberate（Trio/MX）/ Synopsys PrimeLib / Siemens Solido 许可证与专家？倾向 **外购能力 + 薄自研** 还是 **全自研 surrogate**？  
13. 与 [@EDA需求拆解专家] / [@EDA代码开发工程师] / [@EDA测试验证专家] 的接口物（schema、报告格式）是否沿用现有模板？  
14. 数据能否出网训练？是否必须 air-gapped？跨客户数据能否隔离训练？

### 9.5 合规

15. PDK / .lib 再分发与衍生模型的法律与客户合同限制？  
16. 模型与训练日志的保留周期、审计要求？

---

## 10. 编排协调器可直接拆的第一轮任务包（建议）

| ID | 任务 | 建议负责人 | 依赖 | 产出 |
|----|------|------------|------|------|
| T0 | 确认 §9 问题中的 P0 范围与签核角 | 业务 + 需求拆解 | — | 范围说明书 |
| T1 | 盘点现有 PVT 表与仿真队列，定义统一 schema | 需求拆解 + 开发 | T0 | 数据字典 + 样例 |
| T2 | 实现线性 ratio + 插值基线与误差报表 | 开发 | T1 | 基线报告 |
| T3 | 实现 GPR/GBDT 残差 MVP + 凸包门禁 | 开发 | T1–T2 | 可运行流水线 |
| T4 | 黄金集与分层验收用例 | 测试验证 | T0–T1 | 测试计划与门禁 |
| T5 | Slide 24 missing 状态机（provisional/validate） | 开发 + 测试 | T3–T4 | 解卡流程 |
| T6 | （增强）跨版本 TL 可行性评估 | 需求拆解 | 成对工艺数据 | Go/No-Go |

---

*文档结束。路径：`/workspace/eda_char_ai_research.md`*
