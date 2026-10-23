# EPC Desktop GUI (P0 + P1 + P2)

Fluent 本地壳：配置 job → 内嵌跑 `epc_engine` → 预览 `char_data` → 对比页：**门禁 → 约束举证 → 自由对比**。

**门禁只读引擎 audit.md + EXIT；GUI 不重算、不改写 FAIL→PASS。**

本 GUI 默认跑演示数据；自选 .db 时界面不承诺精度结论。

壳为 DESIGN「探针台」**QMainWindow**（`FluentWindow` = Won't：offscreen 下不可用；ThemeColor 仍覆盖）。

视觉规范见 [`DESIGN.md`](DESIGN.md)（深/浅色板）；流程依据 [`FRONTEND_DESIGN.md`](FRONTEND_DESIGN.md)。

## 安装

依赖栈：**PyQt5≥5.15** + `PyQt-Fluent-Widgets`（PyQt5 版，`import qfluentwidgets`）+ pyqtgraph（建议 `PYQTGRAPH_QT_LIB=PyQt5`）。

在**仓库根**（含 `epc_gui/`、`epc_engine/`、`epc_fixtures/`）执行：

```bash
python3 -m venv epc_gui/.venv
source epc_gui/.venv/bin/activate
pip install -r epc_gui/requirements.txt
# residual 路径需要 joblib + scikit-learn（已写入 requirements）
# 若环境同时装了 PyQt6，启动前设：
#   export PYQTGRAPH_QT_LIB=PyQt5
```

## 启动

```bash
cd /path/to/epc-ai-char   # 仓库根
source epc_gui/.venv/bin/activate
export PYTHONPATH=.
export PYQTGRAPH_QT_LIB=PyQt5
# 可选：夹具不在默认 <repo>/epc_fixtures 时
# export EPC_FIXTURES_ROOT=/path/to/epc_fixtures
python -m epc_gui
# 无显示器：
xvfb-run -a env PYTHONPATH=. PYQTGRAPH_QT_LIB=PyQt5 QT_QPA_PLATFORM=offscreen \
  python -m epc_gui
```

运行期路径（**不依赖 `/workspace`**）：
- `state/`、`exports/` → 包相对（`epc_gui/state`、`epc_gui/exports`）
- DEMO 夹具 → `EPC_FIXTURES_ROOT`，否则相对仓库根的 `epc_fixtures/`

## P2 对比页（v0.3）

| 区 | 说明 |
|---|---|
| 门禁 | 只读灯条 + audit 摘录 + 打开全文；未知≠绿 |
| 图一 | 有约束才绘；视图 rel_bars / bound_cells / constraint_list；无约束整区隐藏 |
| 图二 | 参考 vs 构造；PVT/key 交集；容量×typical 双折线；右侧默认「覆盖 n/m」+「Δmed %」 |

糖衣展开仍只走引擎 `load_job`。详见 `GUI_P2_验收自测.md` 与仓库根 `EPC_GUI_P2_需求_v0.md`。

## P1 能力摘要

| 项 | 说明 |
|---|---|
| 约束预览 | 配置页只读表：引擎 `load_job` 展开后的相对约束（instance/pvt/key/δ） |
| 预检 | 「预检」只 `load_job`，不写 B.db；失败展示引擎异常原文 |
| T0 facet | ≥2 key 分面图；仍支持单 key×多 PVT |
| T1 | 默认 `seed_from_A`（max_rel&lt;1e-9）；手动外推点明示「可能≠seed」 |
| T2 / T3 | 报表摘录 / baseline·B·target 柱；不内算门禁 |
| 导出 | 「导出对比」→ `exports/` PNG+CSV |
| eval_h3 / hold-out | 子进程跑 `epc_fixtures/p2/eval_h3.py`；打开 `algo_holdout_report.md` |
| 历史 | `state/job_history.json`；点选回填 YAML / 打开 audit·db |
| 主题 | 顶栏深↔浅；`state/settings.json`；浅色为冷钢纸，禁奶油+陶土 |

## T0 典型值（Kai 钉死）

| 值形态 | 规则 | UI 标注 |
|---|---|---|
| 标量（1 token） | 直接用 | `typical=scalar` |
| N×N 表 | **表中位 cell**：`mid = n//2` | **`typical=median_cell`** |
| 轴向量 / AXIS_KEYS | 不作为趋势 Y | skip |

横轴：`capacity = depth × width`，升序。

## 联调 YAML

路径相对仓库根 `epc_fixtures/`（或 `EPC_FIXTURES_ROOT`）：

| 场景 | 路径 |
|---|---|
| sample | `epc_fixtures/epc_job.sample.yaml` |
| P1 糖衣绿 | `epc_fixtures/p1/epc_job.p1_improve_green.yaml` |
| P1 糖衣拒载 | `epc_fixtures/p1/epc_job.p1_r1_vague.yaml` |
| P2 Geom 绿 | `epc_fixtures/p2/job_corner_fill_green.yaml` |
| residual H3-hard 红 | `epc_fixtures/p2/job_corner_fill_residual_h3hard.yaml` |

## 截图

| 文件 | 内容 |
|---|---|
| `screenshots/p1_dark_config_zh.png` / `_en.png` | 深色配置 zh/en（约束预览 + 底栏历史） |
| `screenshots/p1_dark_compare.png` | 深色对比（P2 IA） |
| `screenshots/p2_dark_compare_chart1_constraints.png` | P2 有约束：门禁+图一+图二 |
| `screenshots/p2_dark_compare_no_constraints.png` | P2 无约束：图一隐藏 |
| `screenshots/p1_light_config.png` | 浅色配置 |
| `screenshots/p1_light_compare.png` | 浅色对比 |
| `screenshots/page_a_*.png` 等 | P0 基线 |

## Headless 自测

在仓库根：

```bash
source epc_gui/.venv/bin/activate
pip install -r epc_gui/requirements.txt
export PYTHONPATH=.
export PYQTGRAPH_QT_LIB=PyQt5
QT_QPA_PLATFORM=offscreen python -m epc_gui.scripts.smoke_p1
QT_QPA_PLATFORM=offscreen python -m epc_gui.scripts.smoke_p2
QT_QPA_PLATFORM=offscreen python -m epc_gui.scripts.smoke_headless
```

详见 `GUI_P2_验收自测.md` / `GUI_P1_验收自测.md` / `GUI_P0_验收报告.md`。
