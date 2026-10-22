# EPC《slide25/26 迁移增强》需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 在 LON PASS 后选定；**待编排器转 Kai 拍板**；**本侧不扇出**） |
| 日期 | 2026-10-22（Asia/Shanghai） |
| 触发 | 按 slide25/26 开 **跨域 Transfer** 最小可验收切片（非接真库、非 GUI、非暂停、非 Active Learning） |
| 技术输入 | `/workspace/slide25_26_项目计划输入.md`（Slide 26 TL、§2.6 L5、§4.7 Residual transfer、§6 E3；**必须击败线性 Transfer Ratio**） |
| 已收口（回归不动） | 同工艺 residual GBDT；AB-hard LOI/LOP；LON 双新；H3-hard；GUI P0–P2.1 |
| 引擎落点建议 | 新 `mode`（推荐 `transfer_ab`）**或** `construct.backend: residual_tl`；复用 job/YAML/audit/`fail_job` 语义 |

> 本轮 = DEMO 上 **源域全表 + 目标域少量 seed → 预测目标稠密/hold-out**，主方法 **Residual TL**，对照 **纯线性 TR**。  
> **并列能力**：不得冒充或削弱同工艺 LOI/LOP/LON / AB-hard / Geom H3。夹具 = **伪双工艺**（从 A_ref 派生），**≠ 真 PDK / 真 N3E→N3P**。

---

## 1. 一页结论

| 问 | 答（本稿推荐） |
|---|---|
| 设定 | 源域 `A_src` 全表 Ref + 目标域稀疏 `A_tgt_seed` → 预测目标 hold-out / 稠密 `B_tgt` |
| 方法 | **Residual TL** = 线性 Transfer Ratio 弱先验 + GBDT 非线性残差；**必须**保留纯线性 TR 对照 |
| 门禁 | 同协议 hold-out：`p95_residual_tl ≤ p95_linear_tr`（允许 =；对齐现网）；报表并列 TR / residual-TL（可选同工艺 idw，无则标 n/a） |
| 夹具 | 由 `A_ref` **可复现派生**伪双工艺（§4）；禁止「同库改名假装迁移」而无数值域偏移 |
| 薄边界 | 无 AL、无 GUI、无真库、无 stamp（本轮）；同工艺门禁回归绿 |

---

## 2. I/O 与配置草图

### 2.1 数据角色

| 角色 | 含义 | DEMO 来源 |
|---|---|---|
| **A_src** | 源域全表（旧工艺/旧版本伪节点） | 派生自 A_ref（§4） |
| **A_tgt_full** | 目标域全表真值（**仅离线评估**；在线 job **不可读** hold-out 真值） | 同派生流水线产出 |
| **A_tgt_seed** | 目标域可见 seed 子集 | 从 A_tgt_full 按 §5 比例/边界规则切出 |
| **B_tgt** | 预测输出 db | job 写出；红路径不落盘 |

### 2.2 YAML 草图（实现可微调键名）

```yaml
version: "0.1"
job_name: "DEMO_transfer_ab_v0"
mode: transfer_ab          # 推荐新 mode；若坚持复用 epc_ab 则须显式 transfer 段且文档钉死
source:
  db: "/workspace/epc_fixtures/transfer/A_src.db"
target:
  seed_db: "/workspace/epc_fixtures/transfer/A_tgt_seed.db"
  # 稠密预测范围：列表或「与 src 对齐的 instance×pvt 网格」
  instance_list: "..."
  pvt_list: "..."
output:
  db: "/tmp/B_tgt_transfer.db"
construct:
  backend: residual_tl     # residual_tl | linear_tr（对照）
  residual_tl:
    prior: linear_tr       # 弱先验
    model_path: "..."      # 离线训好；可缺省则 job 内仅用 seed 拟合（DEMO 允许）
    fallback: linear_tr
gates:
  on_violation: fail_job
  # 精度硬门见 §6（离线 suite 为主）
```

Audit 须记：`mode`、`backend`、`prior`、seed 覆盖摘要、是否 fallback、模型 sha（若有）。

### 2.3 与现 `epc_ab` 关系

| 项 | 规则 |
|---|---|
| 同工艺构造 | **不动**；既有 backend / AB-hard / LON 回归必须绿 |
| 迁移 | **并列**新 mode（或显式 transfer 段）；禁止用迁移报表数字改贴 LOI/LOP/LON |
| 约束 | 若本轮 YAML 带约束：仍先构造后约束；`fail_job` 不落盘语义与 S5 一致。无约束 job 亦允许（迁移精度门禁走 suite） |

---

## 3. 方法（可微调，推荐钉死）

### 3.1 线性 Transfer Ratio（对照基线 · Must 实现）

对每个 `field_key`（及可选 pvt/几何分箱）：

\[
\hat{v}_{\mathrm{TR}} = r(k)\, v_{\mathrm{src}}(i,p,k)
\]

- \(r\) 由目标 **seed** 上相对源同对齐 locator 的比值估计（全局 per-key，或 per-key×corner 粗箱——实现选一种并在报表写死）。  
- **禁止**在 hold-out 真值上估 \(r\)。

### 3.2 Residual TL（主方法 · Must）

\[
\hat{v}_{\mathrm{RTL}} = \hat{v}_{\mathrm{TR}} + \mathrm{GBDT}\bigl(x,\, \hat{v}_{\mathrm{TR}}\bigr)
\]

| 项 | 建议 |
|---|---|
| 特征 \(x\) | 几何 `log2(d/w)`、PVT（corner/V/T）、key、cell 轴、`prior_tr`；**可加**源域同点邻域统计（可选 Should） |
| 标签 | seed 上 `truth_tgt − prior_tr` |
| 轴 | tran/load **禁止打乱**（同现引擎） |
| 可切换 | `backend: linear_tr` 纯先验对照；`residual_tl` 主路径 |

讲稿两点落地：① 非线性相关（残差）② 可利用源域内部 PVT 相关（特征/多任务，本轮允许薄实现，不强制 DNN fine-tune）。

---

## 4. 伪双工艺夹具（从 A_ref 派生 · 防假迁移）

### 4.1 禁止

- 仅把 instance 名改 `NP3→NP3X` 而 **value 逐位相同**（零域偏移 = 假迁移）。  
- 用同工艺 LOI/LON 数字充当 Transfer 验收。  
- 覆盖或污染现 `A_ref.db` 生产路径。

### 4.2 推荐派生（可复现脚本）

目录建议：`/workspace/epc_fixtures/transfer/`。

1. **A_src** ← `A_ref` 拷贝（或硬链 + 只读），标签 `domain=src`。  
2. **A_tgt_full** ← 对每个 cell 施加 **已知非线性 warp**（写死公式与 seed）：

\[
v_{\mathrm{tgt}} = g(V,T,\mathrm{corner},\mathrm{key\_family})\cdot v_{\mathrm{src}} + h(\cdots)
\]

   要求：存在区域使 **全局线性 \(r\) 系统性偏**（低压/漏电族等），从而 Residual TL **有空间**优于 TR。  
3. **A_tgt_seed** ← 按 §5 从 A_tgt_full 切出；其余作 hold-out 真值（仅评估脚本可读）。  
4. 脚本：`epc_fixtures/transfer/build_pseudo_domains.py`（或等价）；报表头打印 warp id / git 可复现命令。

**迁移轴语义（拍板 Q1）**：默认叙事 = **跨工艺伪节点**（Slide 26）；备选 = 跨 option/版本（同 value warp + option 改名）。二者都须满足 §4.1。

---

## 5. Hold-out 协议（目标域）

| 项 | 推荐默认 |
|---|---|
| 对齐 | 源/目标 **同一** instance×pvt×key 网格（DEMO）；「同一 PVT」= 同名字符串 |
| Seed 比例 | 目标格子的 **15%**（或等价：固定边界角全集 + 随机补足到 15%）；**必须含**边界角（SS 类低压高温等——用现 LOP 列表中的极端 pvt ∪ LOI 边角 instance） |
| 评估集 | 目标域 **非 seed** 格子；核心 8 key；cell 相对误差；ε=`1e-12` |
| 主指标 | 全局 **p95**；报表另给 p50/max；建议低压区旁注一行（Should） |
| 对照 | **linear_tr** 同 seed/同评估集；可选：同工艺 `idw_nn` 在目标域（无源域时）标 n/a |
| 比较符 | **`p95_residual_tl ≤ p95_linear_tr`**（允许 =） |
| 协议 id | `transfer_holdout_v0` |

---

## 6. 门禁与交付形态

| 层 | 本轮推荐 |
|---|---|
| **离线报表** | **Must** — `/workspace/epc_fixtures/transfer/transfer_holdout_report.md`（并列 TR / RTL p95、seed 比例、warp id） |
| **硬 EXIT** | **Should** — suite / train 旗标 `--require-transfer-hard`；FAIL → EXIT≠0（可关） |
| **在线 stamp** | **Won't（本轮）** — 不扩 AB/LON stamp；迁移失败不 internally 改写同工艺 stamp |
| **在线 job** | Must 能跑通绿路径写出 B_tgt；精度硬门以 **离线 suite** 为主（与 AB 早期「报表+可选硬」同薄） |

Suite 建议：

```text
/workspace/epc_fixtures/transfer/run_transfer_suite.sh
→ /workspace/epc_fixtures/transfer/迁移增强_验收报告.md
```

与 `run_ab_hard_suite` / `run_lon_holdout_suite` / `run_p2_suite` **并列**。

---

## 7. Must / Should / Won't

### 7.1 Must

| ID | 项 |
|---|---|
| **TR-M1** | 伪双工艺夹具可复现；有数值域偏移（§4） |
| **TR-M2** | 实现 `linear_tr` 与 `residual_tl`；同协议 hold-out 报表并列 |
| **TR-M3** | 主判定：`p95_RTL ≤ p95_TR`（若启用硬门）/ 报表明确 pass 行 |
| **TR-M4** | U0：同工艺 sample/AB-hard/LON/P2-idw **回归仍过** |
| **TR-M5** | 在线 job：seed→预测；audit 可追溯；红路径（若启用精度硬或约束）不落盘 |

### 7.2 Should

| ID | 项 |
|---|---|
| **TR-S1** | `--require-transfer-hard` 硬 EXIT + mock 红夹具 |
| **TR-S2** | 低压区分层 p95 旁注；源域邻域特征 |
| **TR-S3** | `backend: linear_tr` 一键对照 YAML |

### 7.3 Won't

| ID | 项 |
|---|---|
| **TR-W1** | 接真 PDK / 真 N3E↔N3P 库 |
| **TR-W2** | Active Learning 选点；GUI；签核角「预测替代真仿」宣称 |
| **TR-W3** | 本轮迁移 stamp；削弱或改口径同工艺 AB/LON/H3 |
| **TR-W4** | 零偏移改名假迁移；用 LOI/LON 冒充 Transfer |

---

## 8. 验收 U 表

| # | 项 | 标准 |
|---|---|---|
| **U0** | 回归 | AB-hard / LON / sample 绿红 / P2 idw 绿仍过 |
| **U1** | 夹具诚实 | warp 后存在 seed 外区域使线性 TR p95 **可见劣于** RTL（或文档证明 warp 非恒等）；src/tgt value **非**逐位恒等 |
| **U2** | 绿报表 | 现行默认 seed 比例下 RTL 与 TR 两路 p95 有限；协议 id；seed 含边界角 |
| **U3** | 优于 TR | `p95_RTL ≤ p95_TR`（硬门开则 EXIT 0；关则报表 PASS 行） |
| **U4** | 解耦 | suite **未**调用 eval_h3 / 未改 AB stamp；迁移报告路径独立 |
| **U5** | 红（若 S1） | mock RTL 劣于 TR → 硬 EXIT≠0 |

---

## 9. 请 Kai 拍板（编排器转）

| # | 问 | 本稿推荐 |
|---|---|---|
| **Q1** | 迁移轴？ | **A：跨工艺伪节点**（A_ref + 非线性 warp，Slide 26 叙事）。备选 B：跨 option/版本（改名 + 同 warp） |
| **Q2** | Seed 比例？ | **A：目标格子 ~15% + 强制边界角**。备选 B：10%。备选 C：仅固定边界角集合（不补随机） |
| **Q3** | 门禁多重？ | **A：报表 Must + 硬 EXIT Should（可旗标）+ 本轮无 stamp**。备选 B：仅报表。备选 C：硬 EXIT 必开无关旗标 |
| **Q4** | 比较符？ | **`≤`**（与 AB/H3/LON 一致）。备选：严格 `<` |

（Residual TL 结构、必须有线性 TR 对照、伪夹具禁止零偏移、同工艺回归不动 — **已钉死**。）

**请 Kai 拍板后再开开发。** 不写「可直接开开发」。

---

## 10. 与讲稿映射

| 讲稿 | 本薄页 |
|---|---|
| Slide 25 App-2 | 源全表 + 目标少 seed |
| Slide 26 / E3 | Residual TL 击败线性 TR |
| §4.7 | 非线性相关 +（薄）源域 PVT 信息 |
| Active Learning / 真库 | **Won't** |

**本文路径**：`/workspace/EPC_迁移增强_需求_v0.md`（**v0**）
