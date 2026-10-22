# EPC GUI-P0 正式验收报告

| 项 | 内容 |
|---|---|
| 日期 | 2026-10-22（Asia/Shanghai） |
| 验收方 | EDA 测试验证（独立 · 无桌面/浏览器 · headless/文件/CLI） |
| 范围 | `/workspace/EPC_GUI_范围说明书_v0.md` v0.2（含 §6 U6） |
| 开发自测 | `/workspace/epc_gui/GUI_P0_验收自测.md`（核验，非橡皮图章） |
| **结论** | **PASS**（阻塞缺陷：**无**） |

> 本机无交互式 GUI/桌面。功能与联调以代码路径 + `smoke_headless.py` + 独立 `epc_engine` CLI + offscreen 启动/截图文件为准。  
> **建议父代理/Kai 做一次 live GUI 目视**（三页点通、Run 按钮手感、Fluent 控件细节）；不阻塞本结论。

---

## 1. 结论摘要

| 门 | 结果 | 证据要点 |
|---|---|---|
| U1 sample 闭环 | PASS | CLI EXIT0 COUNT=4950；audit PASS；smoke 同 |
| U2 红路径 | PASS | residual H3-hard EXIT1；B.db 未落盘；总体 FAIL + H3-hard=FAIL；T0 文案「不可绘」 |
| U3 门禁只读 | PASS | `audit_parse` 只解析 md；无 GUI 内 evaluate；未知→MuteFog 非绿 |
| U4 T0 | PASS | `typical=median_cell` mid×mid；≥3 容量×≥2 PVT；spot rel_err=0 |
| U4b T1 | PASS* | 有数值展示；外推 locator 可 >1e-9（已知限制，非阻塞） |
| U5 三页 | PASS | `config`/`preview`/`compare` + 导航；offscreen start OK；截图齐全 |
| U6 美学 | PASS† | `DESIGN.md` + 4 张截图；文本对照 FRONTEND_DESIGN 反模式未命中 |
| 联调 sample/P1/P2/红 | PASS | 独立 CLI 全绿/红符合预期 |

\* T1 对相对约束 locator 可能是外推点，UI 已标注「注意：外推点可能≠seed」。  
† 像素级美学由截图描述 + DESIGN 文本评审；live 观感留给父代理。

---

## 2. 环境与复现

```bash
source /workspace/epc_gui/.venv/bin/activate
export PYTHONPATH=/workspace
# 验收时补装（GUI requirements.txt 未列引擎依赖）：
#   pip install joblib scikit-learn
python /workspace/epc_gui/scripts/smoke_headless.py   # → ALL SMOKE OK
QT_QPA_PLATFORM=offscreen python /workspace/epc_gui/scripts/brief_start_quit.py  # → started OK
python -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
python -m epc_engine /workspace/epc_fixtures/p1/epc_job.p1_improve_green.yaml
python -m epc_engine /workspace/epc_fixtures/p2/job_corner_fill_green.yaml
python -m epc_engine /workspace/epc_fixtures/p2/job_corner_fill_residual_h3hard.yaml
```

**注意（非阻塞残留 R1）：** 初验时 GUI venv **缺 `joblib`**，导致 `python -m epc_engine` 在 residual 路径上 `ModuleNotFoundError`。`smoke_headless` 对 sample **复用已有 db**、对红路径若 audit 未刷新可能误读旧 FAIL audit。已在本会话 venv 安装 `joblib`+`scikit-learn` 后 **强制复跑四条 job** 通过。建议把引擎依赖写入 GUI README/`requirements.txt` 或文档化「先装 epc_engine 依赖」。

---

## 3. 功能核对（代码 + smoke）

### 3.1 三页存在

| 页 | 模块 | 导航文案 |
|---|---|---|
| A 输入配置 | `pages/config_page.py` | 输入配置 |
| B 输出预览 | `pages/preview_page.py` | 输出预览 |
| C 数据对比 | `pages/compare_page.py` | 数据对比 |

壳：`app.py` `MainWindow(QMainWindow)` + `QStackedWidget`（非 `FluentWindow`）。

### 3.2 内嵌跑引擎

- `services/job_runner.py`：`QProcess` → `python -m epc_engine <yaml>`；`run_blocking` 供 smoke。
- `config_page.run_job`：同步表单→YAML→落盘→`runner.start`；日志面板接 stdout/stderr。
- 快捷：`加载 sample` / `P1 绿` / `P2 Geom 绿` / `residual H3-hard 红`（`yaml_io.FIXTURE_SHORTCUTS`）。

### 3.3 门禁只读 audit + EXIT

- `services/audit_parse.py` 文档与实现：**NEVER re-evaluate gates**。
- Page C：`总体`/`gates_ok`/逐灯来自 audit 文本；`EXIT` 来自子进程码。
- `parse_ok=False` → 强制「总体 **未知**」（MuteFog），**不默认绿**（已单测缺文件/空文件）。
- 代码扫描：GUI 页内无 `evaluate_constraint` / 自造 PASS。

### 3.4 T0 = capacity × typical(median_cell) + 多 PVT

- `services/trend.py`：`TYPICAL_LABEL = "typical=median_cell"`；N×N 取 `mid=n//2` 交叉格（非全表 median）。
- 横轴 `depth×width` 升序；多 PVT → 多 `TrendSeries`。
- Smoke：unit 索引 12→42.0；sample `tcq`×2 PVT 各 9 点，capacity 升序，spot `rel_err=0`。

### 3.5 FAIL 未落盘 → T0 不可绘 + 门禁红

| 层 | 行为 |
|---|---|
| Config `_on_finished` | `code!=0` → EXIT FailRose；无 db →「未落盘」；**不** `request_preview` |
| Compare `set_context` | `b_db` 不存在 → `plot.clear()` +「无输出库（FAIL 未落盘或不存在）— T0 不可绘」 |
| Compare `_apply_summary` | `overall=FAIL` → FailRose |
| 截图 | `page_c_fail_h3hard.png`：总体 FAIL、B.db 未落盘、T0 空白+不可绘文案 |
| Smoke | red EXIT=1；无 db；audit FAIL；H3-hard=FAIL |

---

## 4. 联调（独立 CLI，与 GUI 同一 YAML）

| 场景 | YAML | EXIT | 产物 | audit（GUI parser） |
|---|---|---|---|---|
| sample | `epc_job.sample.yaml` | 0 | COUNT=**4950** | PASS / gates_ok True |
| P1 绿 | `p1/epc_job.p1_improve_green.yaml` | 0 | COUNT=**4950** | PASS |
| P2 Geom 绿 | `p2/job_corner_fill_green.yaml` | 0 | COUNT=**2000** | PASS；H1/H2=PASS；H3-hard=SKIP |
| residual H3-hard 红 | `p2/job_corner_fill_residual_h3hard.yaml` | **1** | **无** out db | FAIL；H3-hard=FAIL；db_written no |

GUI smoke 覆盖 sample 解析/T0 + 红路径；P1/P2 绿由 CLI + 快捷键路径常量对齐（未在 smoke 内再跑一遍 GUI 子进程，因与 CLI 同 `job_runner`/`epc_engine`）。

---

## 5. U6 美学

### 5.1 交付物

| 要求 | 状态 |
|---|---|
| `/workspace/epc_gui/DESIGN.md` | 有（色/字/布局/原则 + FRONTEND 自检表） |
| `/workspace/epc_gui/FRONTEND_DESIGN.md` | 有 |
| 三页截图 | 有，见下 |

**截图路径（请父代理 live 目视）：**

- `/workspace/epc_gui/screenshots/page_a_config.png`
- `/workspace/epc_gui/screenshots/page_b_preview.png`
- `/workspace/epc_gui/screenshots/page_c_compare.png`
- `/workspace/epc_gui/screenshots/page_c_fail_h3hard.png`（红路径附加）

### 5.2 反模式文本对照（FRONTEND_DESIGN / 范围 §6）

| 反模式 | 本交付 | 判定 |
|---|---|---|
| 暖奶油 + 陶土强调 | InkWell `#0E1419` + TraceAmber `#E8A838` | 避开 |
| 近黑 + 单一酸绿/朱红 chrome | PassTeal/FailRose **仅状态灯** | 避开 |
| SaaS 同圆角同灰影卡片堆 | field band + hairline；radius≤4 | 避开 |
| ALL-CAPS eyebrow / 按钮「→」 | 句子式「运行/停止/保存」 | 避开 |
| 模板中点装饰元数据 | sticky 用 mono job·mode·EXIT（工具语义） | 可接受 |

headless 截图目视摘要：深色探针台轨 + 琥珀选中/Run；Page C 门禁条 + T0 折线主视图；红路径门禁红且图空——与 DESIGN「Instrument, not SaaS」一致。

---

## 6. 已知限制 · 阻塞判定

| # | 限制 | 判定 | 理由 |
|---|---|---|---|
| L1 | 自定义 `QMainWindow`，非 `FluentWindow` | **非阻塞** | 自测与 README 已写明 offscreen/frameless abort；仍 `setTheme(DARK)`+ThemeColor；DESIGN 色板落地。范围要求 Fluent **控件能力** + DESIGN 视觉身份，未强制顶层必须 FluentWindow。 |
| L2 | T1 对外推点 max_rel_err 可能 ≥1e-9 | **非阻塞** | UI 明示外推提示；真 seed 应用 seed_from_A。不构成门禁造假。 |
| L3 | 未知不默认绿 | **符合需求**（非缺陷） | 范围 §2.2 / U3；代码与截图（G3=未知 等）证实。 |

---

## 7. Headless 范围 vs 仍需 live GUI

**本验收已覆盖：**

- 依赖导入、offscreen 启停、三页类存在、YAML 快捷、子进程引擎契约  
- audit 解析、未知态、T0 median_cell 与 SQL 一致、FAIL 不落盘与 T0 门禁  
- 四条联调 YAML 的引擎侧结果与 GUI parser 一致  
- DESIGN/FRONTEND 文本评审 + 截图文件存在性与内容描述  

**建议父代理 live 补做（非本结论阻塞）：**

1. 真实 DISPLAY 下点通 A→B→C、点「运行」看进度与跳转  
2. 确认 Fluent 控件在非 offscreen 下的观感（若未来改回 FluentWindow）  
3. 人眼确认 U6 无遗漏反模式（验收机仅能描述截图）  
4. 确认 GUI venv 在干净机上安装 `joblib`/`sklearn` 后内嵌 Run 不炸（见 R1）

---

## 8. 残留风险（非阻塞）

| ID | 项 | 建议 |
|---|---|---|
| R1 | GUI `requirements.txt` 未列引擎 `joblib`/`scikit-learn` | 文档或依赖钉死 |
| R2 | smoke sample 复用已有 db，不强制重跑 | 可选加 `--force-run` |
| R3 | audit 对 P2 的 G1/G3 常显示「未知」（文案格式未匹配） | 增强 parser 或引擎 audit 短语；**未知≠绿**，可接受 |
| R4 | T1 默认捡 relative 约束 locator → 演示上易现 4e-2 | P1 改默认 seed_from_A |
| R5 | 截图红路径 sticky 仍可能显示 sample job 名（捕获时序） | 捕获脚本在红跑后刷新 strip |

---

## 9. 最终判定

**GUI-P0：PASS**

- 阻塞缺陷：无  
- 已知限制 L1/L2：非阻塞；L3：需求满足  
- 美学 U6：文档+截图+反模式文本评审通过；live 目视建议父代理跟进  

**报告路径：** `/workspace/epc_gui/GUI_P0_验收报告.md`

---

## 附注 · 父代理截图目视（2026-10-22 00:33 CST）

独立查看 `epc_gui/screenshots/` 四张图后确认：

1. **三页结构**：输入配置 / 输出预览 / 数据对比侧栏齐全，深色+橙强调，与 DESIGN 一致。
2. **PASS 对比页**：门禁只读区显示「总体 PASS / EXIT 0」；T0 为 capacity×typical，多 PVT 曲线可绘。
3. **H3-hard FAIL 页**：红字「总体 FAIL / EXIT 1 / B.db 未落盘」；T0 明示「无法出库…T0 不可绘」，图区无数据点——与功能门禁一致。
4. **U6**：未见明显拥挤表单/默认绿误导；底部 DEMO 精度免责声明可见。

未再开 live 桌面点通；截图+冒烟足够支撑本轮 PASS。已知限制 L1/L2 维持非阻塞。
