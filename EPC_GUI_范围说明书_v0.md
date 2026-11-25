# EPC GUI 范围说明书 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0.2**（§8 冻结 + T0；Kai 追加美学 **严格按 frontend-design**；**本侧不扇出**） |
| 日期 | 2026-10-22（Asia/Shanghai）；补丁同日 |
| 引擎 | `/workspace/epc_engine/`：`python -m epc_engine <job.yaml>`；mode=`epc_ab`\|`corner_fill_geom`\|`pvt_missing_fill`\|`pvt_sparse_fill` |
| DEMO | `/workspace/epc_fixtures/`（sample / P1 / P2 / 加固）；合成数据，**非**真工艺 |
| 对齐能力 | 代码工程师侧已具备 **PyQt-Fluent-Widgets**；本 GUI **只编排与可视化**，不重写构造/门禁算法 |

> 目标：效仿 Fluent 桌面壳，给当前 EPC 一条「配 job → 跑引擎 → 看库 → 对照门禁与趋势」的本地闭环。  
> **门禁证明只读引擎 audit / G / H 结果**；GUI **禁止**另造门禁逻辑或改写 FAIL→PASS。

---

## 1. 结论（一页）

| 问 | 答 |
|---|---|
| 能否做？ | **能**。桌面本地 + 调现有 CLI/库 API 即可，与算法解耦。 |
| 技术栈默认 | **PyQt6 + PyQt-Fluent-Widgets**；图表 **pyqtgraph**（已冻结） |
| 三页 | ① 输入件配置 ② 输出 db 预览 ③ 数据对比（门禁证明 + 趋势可信） |
| P0 必做 | 三页骨架 + 加载/保存 YAML + 内嵌跑 job + audit 门禁灯 + **主趋势 T0**（容量×典型值多 PVT 折线）+ 辅证 T1/T2/T3 |
| 非目标 | Web、云端真 PDK、多用户、重训模型 UI、替代 CLI |

---

## 2. 技术栈与集成边界

### 2.1 推荐默认（建议钉死）

| 层 | 选择 |
|---|---|
| UI | PyQt6 + [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)（导航/卡片/主题） |
| 进程 | 桌面单机；工作目录默认指向 `/workspace/epc_fixtures`（可改） |
| 跑 job | **子进程**调用 `python -m epc_engine <yaml>`（捕获 EXIT、stdout/stderr）；P1 可再包一层薄 Python API，但门禁仍以引擎为准 |
| 读库 | `sqlite3` 只读打开 `char_data`（与 T1 一致）；大表分页/按 key 懒加载 |
| 写配置 | GUI 编辑 → 落盘 YAML（schema 与现 `epc_job.sample.yaml` / P2 job 对齐）；**不**在内存里偷偷改引擎行为 |

### 2.2 硬边界

- GUI **不得**实现、放宽或绕过：`fail_job`、G1–G3、H1–H3、H3-hard、约束 evaluate。  
- 展示用的「门禁灯」只能解析引擎写出的 **audit.md**（及 EXIT code）；解析失败 → UI 标「未知」，不得默认绿。  
- 不内嵌重训；不改 `char_data` schema；不扇出第二套 backend。

---

## 3. 信息架构（三页）

```text
┌─────────────────────────────────────────────────────────┐
│  EPC Desktop (Fluent)     [打开YAML] [另存] [运行] [停止] │
├──────────┬──────────────────────────────────────────────┤
│ 输入配置  │  Page A: Job / mode / paths / constraints     │
│ 输出预览  │  Page B: B.db（或 out_*.db）表浏览             │
│ 数据对比  │  Page C: 门禁证明 + 趋势对照                   │
└──────────┴──────────────────────────────────────────────┘
```

### 3.1 Page A — 输入件配置

| 区块 | 控件要点 | 绑定 YAML |
|---|---|---|
| 作业头 | job_name、version | 顶层 |
| Mode | 下拉：`epc_ab` / `corner_fill_geom` / `pvt_missing_fill` / `pvt_sparse_fill`；与 `operator` 同步，冲突拒载提示 | `mode` / `operator` |
| Source | 文件选择 A.db / source.db；只读展示 process、instance/pvt 计数 | `source.*` |
| Target · epc_ab | instance_list / pvt_list 路径 + 行数预览 | `target.*` |
| Target · P2 | seed/target instances、pvt_list、角覆盖开关、Miss/Sparse 专有项 | 各 mode 段 |
| Construct | backend=`idw_nn`\|`residual_gbdt`；model_path；apply_on | `construct.*` |
| Constraints | 列表编辑器：type、instances/pvts/keys、target；糖衣展开只读预览（调用引擎已有展开结果或保存后跑一次 dry——P1） | `constraints` |
| Output / Gates | db_path、audit_path；`on_violation=fail_job`（只读强调，不可在 DEMO 默认改 soft） | `output` / `gates` |
| 快捷 | 「加载 sample」「加载 P1 绿」「加载 P2 Geom 绿」一键填路径 | fixtures 路径常量 |

**关键交互**

1. 改 mode → 显示/隐藏对应字段；非法组合即时红字（与引擎拒载文案对齐）。  
2. **运行**：写临时或用户选定 YAML → 子进程跑引擎 → 进度条/日志面板 → 结束后跳转 Page B（若 PASS 且有 db）或停在 A 并打开 audit 摘要（FAIL）。  
3. FAIL 时 **确认输出 db 不存在或已删除**（读文件系统，与 S5 一致），UI 明示「未落盘」。

### 3.2 Page B — 输出件 db 预览

| 能力 | P0 | P1 |
|---|---|---|
| 打开最近一次输出 db / 任选 db | ✓ | ✓ |
| 按 instance × pvt 过滤；key 下拉 | ✓ | ✓ |
| 表值网格（N×N token 解析为矩阵） | ✓ | ✓ |
| 状态列 / provisional（若库或 audit 有） | 有则显 | 筛选 |
| 导出当前切片 CSV | — | ✓ |
| 与 A 同 locator 并排（只读） | — | ✓ |

不做：就地编辑 cell 写回库（非目标）；巨型全表一次载入（须分页）。

### 3.3 Page C — 数据对比（门禁证明 + 趋势可信）

分两栏，**同一 hold-out / 约束 locator 上下文**。

#### C-1 门禁证明（只读引擎产物）

| 证明什么 | GUI 怎么做 | 数据源（唯一） |
|---|---|---|
| ① 若设门禁则满足 | 解析 audit：总状态 PASS/FAIL、`gates_ok`、G1/G2/G3、H1/H2/H3、H3-hard（若有）、约束逐条结果 | `*_audit.md` + EXIT |
| fail_job 语义 | FAIL 时检查 output db **未写出**；PASS 时 COUNT 与 YAML 声明一致（只读 SQL） | 文件系统 + sqlite |
| 禁止 | GUI 内重新 evaluate 约束并覆盖 audit | — |

验收口径（可测）：对 fixtures 绿路径，UI 显示的 PASS/FAIL 与独立 CLI 跑出的 audit **逐字段一致**；对红路径，UI 不得显示「已写出 B.db」。

#### C-2 趋势可信

##### 主视图 **T0 · 容量–典型值折线**（Kai 冻结 · 趋势可信主定义）

| 项 | 钉死 |
|---|---|
| 横轴 | instance **容量**，默认 `capacity = depth × width`（T1 解析自 instance 名）；按容量 **升序** 排列；同容量多 instance 时次键用 instance 名 |
| 纵轴 | 用户关心的时序 / 功耗 **典型值**（见下「典型值」）随容量的变化 |
| 系列 | **多条 PVT 折线**可同时绘制；**PVT 与 field_key 均由用户多选**（key 多选时：同图分色按「key×pvt」或分 facet——P0 允许「单 key + 多 PVT」为默认交互，多 key 为 P0 增强开关） |
| 数据源 | 优先 **输出库**（B / out_*）；可叠 **源库 A** 同 key×pvt 虚线作对照（同一容量轴） |
| 库 | **pyqtgraph** 折线；图例可开关单条 PVT |

**典型值（可验收默认，避免空泛）：**

| 优先级 | 规则 |
|---|---|
| 1 | 若该 `(instance,pvt,key)` 值为标量 → 直接用 |
| 2 | 若为 N×N 表 → 取表中位** cell（`tran_index`/`load_index` 中位）；UI 标注 `typical=median_cell` |
| 3 | 用户可改「典型」为 min / max / 指定 (tran,load)（P1）；P0 固定中位 cell |

**T0 验收（P0）：**

1. 选 ≥3 个不同容量 instance、≥2 条 PVT、1 个 delay 类 key：折线点数 = instance 数，横轴单调不降。  
2. 与只读 SQL 算出的同协议典型值 **逐点相对误差 &lt; 1e-9**（证明 GUI 未另造数）。  
3. 换 key / 增删 PVT 多选后图例与曲线同步更新。

##### 辅证（门禁页 / 子页；保留，不替代 T0）

| ID | 定义 | 可视化 | 通过标准 |
|---|---|---|---|
| **T1 Seed 不变** | 选 1 个 seed（instance,pvt,key）：输入 vs 输出 | 叠线（tran 切片或 1D） | max 相对误差 &lt; **1e-9**（同 H2） |
| **T2 构造 vs 真值** | hold-out / A_exact 对齐点 | Δ **热力** | 展示 p95（可读 `eval_h3` / hold-out 报表；**不**在 GUI 重算门禁阈值） |
| **T3 相对约束方向** | 有 relative / 糖衣时 | 柱：baseline vs B vs 目标 | \|B/baseline − (1+δ/100)\| &lt; **1e-6**（同 G2） |

P0：**必须 T0**；辅证至少 **T1**，并按 job 自动亮 **T2 或 T3 之一**。P1：T0 多 key facet + T1–T3 全开。

---

## 4. 与 fixtures 联调路径

| 场景 | 一键入口 | 期望 UI |
|---|---|---|
| P0 sample | `epc_job.sample.yaml` | EXIT0；B COUNT=4950；audit PASS；T3 可抽相对约束 |
| P1 绿/红 | `epc_fixtures/p1/` 既有 job | 绿：G1–G3 灯绿；红：FAIL 不落盘 |
| P2 Geom/Miss/Sparse 绿 | `p2/job_*_green.yaml` | mode 正确；H1–H3 摘要；T1 seed 不变 |
| P2 / 加固红 | residual H3-hard 红等 | FAIL；H3-hard 红灯；无 out db |
| 只读对比 | 不跑 job，直接打开已有 `B_out.sample.db` + audit | Page B/C 可用 |

联调命令（开发自测，非 GUI 内逻辑）：

```bash
python -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
# 及 p1 / p2 suite；GUI 应用同一 YAML 路径应得到一致 audit
```

---

## 5. 里程碑：P0 必做 vs P1 增强

### 5.1 GUI-P0（本范围「能演示闭环」）

1. Fluent 壳 + 三页导航。  
2. 加载/编辑/保存 YAML（覆盖 sample + 至少一种 P2 mode 字段）。  
3. 子进程运行引擎 + 日志 + EXIT。  
4. Page B：按 instance/pvt/key 预览表矩阵。  
5. Page C：audit 门禁灯 + **主趋势 T0**（容量×典型值，多 PVT）+ 辅证 **T1** +（T2|T3）。  
6. 一键加载 sample；文档说明 DEMO-only。  
7. **美学**：先写 `DESIGN.md` token 计划，再实现；交付截图对照 `/workspace/epc_gui/FRONTEND_DESIGN.md`（见 §6）。

### 5.2 GUI-P1（增强，非本 v0 阻塞）

- 约束糖衣可视化展开；dry-run 拒载预检。  
- T0 多 key facet；T1+T2+T3 全开；导出对比 PNG/CSV。  
- 内嵌选跑 `eval_h3.py` / 打开 `algo_holdout_report.md`。  
- job 历史列表；主题深浅色。  
- 薄 API：`from epc_engine... import run_job`（若开发抽出），仍以 audit 为门禁源。

---

## 6. 美学硬约束（frontend-design）

Kai 追加：**GUI 美学严格按 frontend-design**，与功能范围同级，**不可跳过**。

| 项 | 要求 |
|---|---|
| 规范源 | `/workspace/epc_gui/FRONTEND_DESIGN.md`（frontend-design 技能全文；以该文件为准） |
| 设计计划 | 交付必须含 **`/workspace/epc_gui/DESIGN.md`**：4–6 色 token（具名 hex）、字体与角色、布局概念（含简短 ASCII）、本产品差异化原则；**写码前**完成，并相对「任意类似页都会长成这样」的默认稿自检修订 |
| 验收附件 | 三页（配置 / 预览 / 对比含 T0）各 ≥1 张截图，建议落 `epc_gui/screenshots/`；评审对照 FRONTEND_DESIGN 的原则与反模式 |
| 栈关系 | 仍用 PyQt6 + Fluent **控件能力**；视觉身份（色、字、疏密、主记忆点）由 DESIGN.md 定义，**禁止**停在 Fluent / 模板默认皮 |

**禁止（AI 默认美学清单，见 FRONTEND_DESIGN 校准段；出现即美学 FAIL）：**

1. 暖奶油底 + 高对比衬线 + 陶土/粘土强调色（近 #F4F1EA / #D97757 一类）  
2. 近黑底 + 单一酸绿或朱红强调  
3. 大报式细线、零圆角、密栏排版套用在本工具上而无内容理由  
4. SaaS 卡片套件：同圆角同灰影切块、装饰渐变洗  
5. 模板铬：tracked ALL-CAPS eyebrow、中点拼接元数据、`WORD — fragment`、近黑假黑、小数据滥用等宽字、按钮尾缀「→」等与主题无关的套话  

另：不为装饰堆编号徽章；非用户触发的 fade/slide 进场不散落每张卡片。文案用界面语气、主动作名一致（见 FRONTEND_DESIGN「writing」）。

**美学验收条（并入 §8）：** 无 `DESIGN.md` 或截图缺失，或评审认定落入上列反模式且无书面设计理由 → **GUI 美学门禁 FAIL**（功能 U1–U5 过也不能算完整交付）。

---

## 7. 非目标

- Web / 远程多用户 / 权限体系  
- 真 PDK / 代工厂标定云  
- GUI 内训练 residual、改 schema、手改 cell 写库  
- 替代 CLI 或绕过 `fail_job`  
- 像素级复刻某商业 Liberate/SiliconSmart GUI  
- 以 Fluent 默认皮或 AI 模板美学交差（见 §6 反模式）  

---

## 8. 验收建议（GUI 本身）

| # | 项 | 标准 |
|---|---|---|
| U1 | sample 闭环 | UI 跑 sample → 与 CLI 同 COUNT、同 audit 状态 |
| U2 | 红路径 | 任选一红 job → UI 显示 FAIL 且输出 db 不存在 |
| U3 | 门禁只读 | 故意改 audit 文件后重载，UI 跟随文件（证明不内算门禁）※可选开发自测 |
| U4 | T0 主趋势 | ≥3 容量点、≥2 PVT、1 key；横轴升序；与 SQL 典型值逐点一致 |
| U4b | T1 辅证 | DEMO seed 叠线误差 &lt; 1e-9 有数值展示 |
| U5 | 三页可达 | 不跑完整 suite 也可手动点通 A→B→C |
| **U6** | **美学** | 存在 `epc_gui/DESIGN.md` + 三页截图；对照 `FRONTEND_DESIGN.md`；未落入 §6 反模式清单 |

---

## 9. Kai 拍板结果（已冻结）

Kai **未改**原五问推荐 → 编排器冻结如下；并追加 **T0 主趋势**（见 §3.3 C-2）。

| # | 决议 |
|---|---|
| **Q1** | **DEMO 一等公民 + 允许自选 db**（自选不承诺精度门禁文案） |
| **Q2** | **内嵌跑 job**（子进程调 `epc_engine`） |
| **Q3** | **主视图 = T0**（容量横轴 × 典型值纵轴，多 PVT 折线；key/PVT 用户多选）。原 T1 / T2 / T3 **保留为辅证**（门禁页/子页） |
| **Q4** | **pyqtgraph** |
| **Q5** | 入口 **`python -m epc_gui`**（包 `/workspace/epc_gui/`） |

另冻结：**美学严格按 frontend-design**（§6）。无其余开放拍板项；开发交接由编排器发出。

---

## 10. 交付物（开发阶段预期，非本需求文档本身）

| 产物 | 说明 |
|---|---|
| `/workspace/epc_gui/` | 应用包 + README（安装 Fluent、启动命令） |
| **`epc_gui/DESIGN.md`** | **必交**：色/字/布局/原则 token 计划（先于或并行于实现，验收硬项） |
| **`epc_gui/FRONTEND_DESIGN.md`** | 美学规范源（已存在）；实现与评审依此 |
| 截图 | 三页各 ≥1，建议 `epc_gui/screenshots/` |
| 联调说明 | 指向 sample/P1/P2 YAML |

---

## 11. 一页结论

- **做**：PyQt6 + Fluent 本地 GUI，三页配置 / 预览 / 对比；**内嵌**子进程调 `epc_engine`。  
- **门禁**：只可视化 audit 与 EXIT；不另造逻辑。  
- **趋势可信主视图 T0**：横轴容量（depth×width 升序），纵轴典型时序/功耗，多 PVT 折线；key/PVT 多选。T1/T2/T3 为辅。  
- **§9 已冻结**；美学依 §6 / `FRONTEND_DESIGN.md`，须交 `DESIGN.md` + 截图；编排器交开发。  

**本文路径**：`/workspace/EPC_GUI_范围说明书_v0.md`
