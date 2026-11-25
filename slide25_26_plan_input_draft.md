# Slide 25/26 深刻理解 — 项目计划输入（草稿，待成熟方案调研补齐）

来源：TSMC Jonathan Chang, *AI for Accelerating Memory Development*, 2026 IEEE VLSI Symposium SC2-2

---

## 一句话定位

这两页都在解决 **SRAM/Memory IP 表征（Characterization）算力与 TAT 爆炸**：用已有仿真大数据 + AI，少跑真 SPICE，补全或迁移大量 PVT 点上的性能指标；核心不是“生成电路”，而是 **数值型 surrogate / transfer 预测 + 校验门禁**。

上游上下文：Slide 23 进入 Characterization 专章；Slide 24 是同章的「缺数补点」（仿真失败 <1% missing）；25/26 是 compiler 全量表征加速与跨工艺迁移两条产品化应用。

---

## Slide 25 — AI-Assisted SRAM Compiler Characterization

### 在做什么（What）

| 项 | 内容 |
|---|---|
| 对象 | SRAM Compiler 表征：在大量 PVT corner 上得到 timing/power 等库表可用指标 |
| 痛点 | 先进节点下 PVT 组合可达数百（图示到 PVT 300），全量 SPICE 表征成本极高 |
| 输出 | 未仿真（或极少仿真）corner 上的指标预测值，用于推进后续 IP 流程；最终仍需对关键点回仿真校验 |
| App-1 | **同设计内补全**：已仿真部分 PVT（如 1–50）→ 预测其余（51–300） |
| App-2 | **跨设计/跨工艺少样本**：Ref 库有全 PVT；新设计/新工艺只仿真少量 seed → 预测大量其余 PVT |

价值主张（片上原文要点）：用历史大数据训练；建模型预测额外 PVT；相对传统插值/外推，在 **非线性电路行为** 上更准。

### 怎么做（How，从片面可还原的流程）

1. **建训练库**：历史表征结果（多工艺、多 compiler 配置、多 PVT → 指标向量）作为 big data。
2. **选点仿真（真值）**：App-1 仿真子集；App-2 对新目标仿真少量 seed（图示约到 PVT10 量级，具体比例需业务定）。
3. **学映射**：输入为 PVT 参数（及可选：设计/工艺特征向量、结构参数），输出为表征指标；强调非线性拟合能力。
4. **批量预测** 未仿真 corner。
5. **（隐含，工程必备）门禁**：对高风险/高不确定/关键 signoff corner 回灌仿真；与 Slide 24「先预测推进、后补真值校验」一致。

---

## Slide 26 — AI Transfer Learning for Characterization

### 在做什么（What）

跨 **工艺版本**（示例 N3E → N3P）迁移表征知识：旧版全 PVT 已知，新版只有极少点（示例仅 PVT1）有真值，要预测新版其余 PVT。

对比两种策略：

| | 传统 Linear Mapping by script | Transfer Learning by AI/ML |
|---|---|---|
| 做法 | 用单点算 Transfer Ratio，再线性映射到其余 PVT | ML 学跨版本关系 + 利用旧版 **PVT 内部相关结构** |
| 失败点 | 真实相关非线性（片上 `taah_clk_0_int` Offset–Temperature 曲线） | 目标：拟合非线性，并借助旧数据 PVT 间相关提高精度 |

### 怎么做（How）

可还原的方法骨架：

1. **源域** N3E：全 PVT 表征向量（及 PVT 间相关结构）。
2. **目标域** N3P：极少 seed 真值（片上 PVT1）。
3. **禁止**：仅用单点 ratio 做全局线性缩放。
4. **采用**：跨域非线性映射（transfer / domain adaptation）；显式利用源域 PVT–PVT 相关，把「曲面形状」迁到目标域，再用 seed 做校准。
5. **校验**：关键 corner / 高不确定区域必须回仿真（与 24/25 同一交付纪律）。

与 Slide 25 App-2 的关系：25 是「有 Ref 全表 + 新目标少仿真」的产品叙事；26 把「跨工艺版本」的难点（非线性、不能线性 mapping）和方法名（Transfer Learning）钉死，是 25 的关键技术特写。

---

## 与 Slide 24 的关系（同一能力的不同入口）

- 24：**缺测补点**（工具挂了 / 极端条件失败）→ 用 >99% 已有点预测 <1%，解卡交付。
- 25：**主动少仿** → 从未打算全仿完再交付。
- 26：**跨版本迁移** → Ref 与目标不在同一分布，必须 transfer，而非同分布插值。

项目上可做成 **同一预测与门禁平台**，三种工况：missing-fill / within-design sparse char / cross-process transfer。

---

## 问题本质（工程抽象）

**多维 PVT（及设计/工艺特征）→ 电路性能指标** 的昂贵黑盒函数 \(f\)，用 surrogate \(̂f\) 在约束误差与风险下近似：

- 同分布稀疏观测（25 App-1、24）
- 近邻分布 + 极少目标域标签（25 App-2、26）

成功标准不是「模型好看」，而是：**TAT/CPU 下降 + 关键指标误差可控 + 可审计的回仿真门禁 + 能进 Liberty/签核流程**。
