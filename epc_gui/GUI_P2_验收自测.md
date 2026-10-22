# GUI-P2 验收自测（开发侧）

日期：2026-10-22（Asia/Shanghai）  
规格：`/workspace/EPC_GUI_P2_需求_v0.md` v0.3 · Kai 四问全按推荐

## 交付摘要

- **P2-G0** 门禁区：只读灯条 + audit 短摘录 + 打开全文；未知≠绿（复用 `audit_parse.display_overall`）
- **P2-G1–G4** 图一：有约束才绘；下拉 `rel_bars` / `bound_cells` / `constraint_list`；糖衣仅 `load_job`；无约束整区隐藏 + 一句空态
- **P2-F1** 图二：参考 vs 构造；PVT/key = 两库交集；容量升序双折线（参考虚线 MuteFog，构造实线 TraceAmber）
- **P2-F2** 右侧默认仅 `覆盖 n/m` + `Δmed %`（无默认 Δmean）；不当门禁
- **P2-F3** 布局门禁→图一→图二；少文案；P1 smoke 回归；DESIGN + 截图

## 命令

```bash
cd /workspace
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/smoke_p1.py
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/smoke_p2.py
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/capture_p2.py
```

## 截图

| 文件 | 内容 |
|---|---|
| `screenshots/p2_dark_compare_chart1_constraints.png` | 有约束：门禁+图一+图二 |
| `screenshots/p2_dark_compare_no_constraints.png` | 无约束：图一隐藏 + 空态句 |
| `screenshots/p2_dark_compare.png` | 总览（同有约束） |
| `screenshots/p2_dark_compare_en.png` | English locale |

## 已知限制

- 图一 `rel_bars` 最多绘 16 条相对 locator；完整清单看 `constraint_list`
- 图二 Δmean / typical 改 min·max·指定 cell 为 Should，未做
- T0 多 key 分面主视图已降出 Must；eval_h3 / hold-out 仅底栏 Should
- FluentWindow 仍不做（offscreen 限制）

## 文案与图一交互修订（验收前）

日期：2026-10-22（Asia/Shanghai）

| 项 | 改动 |
|---|---|
| 门禁区 | 去掉 `gates_ok …` 裸字段；B.db 仅「已落盘/未落盘」，路径进 Tooltip；总体「通过/未通过/未知」；灯条 `G1-PASS` 短码 |
| 图一标题 | **结果约束反标** / Constraint markup；空态 **无约束** |
| 图一横轴 | ①②③… 序号刻度；hover 显示约束细则（type/instance/pvt/key/目标·δ） |
| 图二右侧 | 「对齐 n/m」「中位差 ±x%」；`typical=median_cell` 仅 Tooltip |

截图：`p2_dark_compare_chart1_constraints.png`（序号轴）、`p2_dark_compare_no_constraints.png`（空态）、`p2_dark_compare.png`（门禁区）、`p2_dark_compare_en.png`。

## 视觉抛光（frontend-design + DESIGN）

- DESIGN.md：补 Compare 布局 ASCII、图表 chrome、本轮自检表
- QSS：FieldBand 圆角 2px、ReadoutBand、Lamp/GateLights/AuditSnippet、焦点 TraceAmber、Tooltip
- 对比页：门禁 ● 灯点、读出条、页边 14/10、图一①②③ / 图二虚实对比度不变语义
- 截图：`screenshots/p2_dark_compare*.png`、`p2_light_compare*.png`、可选 `p2_*_config.png`
- 功能 / 门禁语义 / 图一图二数据逻辑未改

## 浅色图区纯白

Light **PlotCanvas** = `#FFFFFF`（页面 InkWell 仍 `#EEF1F5`）；`theme.configure_plot` 用 `PlotCanvas`，深色不变。截图：`p2_light_compare.png`。
