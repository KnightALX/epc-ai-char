# GUI-P1 验收自测（开发）

| 项 | 内容 |
|---|---|
| 日期 | 2026-10-22 Asia/Shanghai |
| 规格 | `/workspace/EPC_GUI_P1_需求_v0.md` |
| 代码 | `/workspace/epc_gui/` |

## U0–U12 对照

| # | 项 | 自测结果 | 证据 / 命令 |
|---|---|---|---|
| **U0** | P0 回归 | 见 `scripts/smoke_headless.py` | sample COUNT=4950；residual H3-hard EXIT≠0 未落盘 |
| **U1** | 约束预览 | PASS | `expand_from_path(p1_improve_green)` → `expanded_constraint_count=16` = relative_rows |
| **U2** | dry-run | PASS | vague → fail 且不写 db；green → 预检通过 |
| **U3** | T0 facet | PASS（截图） | ≥2 key 分面；CSV 含 key 列（`export_compare`） |
| **U4** | T1 seed_from_A | PASS | DEMO sample 默认 max_rel&lt;1e-9；手动外推有提示 |
| **U5** | T2+T3 | PASS | T2 读 h3/hold-out；T3 柱（P1 绿 speed+power） |
| **U6** | 导出 | PASS | `exports/` PNG+CSV 非空 |
| **U7** | eval_h3 / hold-out | PASS | 按钮子进程 + 只读打开 md |
| **U8** | 历史 | PASS | `state/job_history.json`；点选回填 |
| **U9** | 主题 + 语言 | PASS | 深↔浅；`locale` zh|en；浅色 token 见 DESIGN（非奶油/陶土） |
| **U10** | R1 依赖 | PASS | requirements 含 joblib/scikit-learn；venv 可 import |
| **U11** | R3 解析 | PASS | P2 Geom：G/H 非未知；未知≠总体绿 |
| **U12** | 美学 | PASS | DESIGN.md 浅色 + `screenshots/p1_*` |

## 复现

```bash
source /workspace/epc_gui/.venv/bin/activate
pip install -r /workspace/epc_gui/requirements.txt
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  python /workspace/epc_gui/scripts/smoke_p1.py
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  python /workspace/epc_gui/scripts/smoke_headless.py
xvfb-run -a env PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  python /workspace/epc_gui/scripts/capture_p1.py
```

## 文案 / i18n（Kai 纠偏）

日期：2026-10-22 Asia/Shanghai · **覆盖**先前「每控件中英叠写」方案。

**规则**
- Settings 条：`语言 Language: 中文 | English`；写入 `state/settings.json` 的 `locale: zh|en`
- 与主题独立（`theme` ⊥ `locale`）；切换后即时 `retranslate()`
- 文案表：`epc_gui/i18n/`（`catalog.py` + `tr(key)`）；一次只显示一种语言
- **禁止**控件上 `预检 / Dry-run` 这类叠写双语
- 短标签；少括号；长说明 → Tooltip（亦走 i18n）
- 专有名词可两语相同：YAML、EXIT、PVT、audit、db、T0–T3、eval_h3、fail_job

**范围**：`app.py`、`pages/*.py`、`i18n/`、`services/history.py`；`DESIGN.md` Writing；本自测。

截图：`screenshots/p1_dark_config_zh.png`、`p1_dark_config_en.png`，以及 dark/light compare。



## 文案自查清理（Kai）

日期：2026-10-22 Asia/Shanghai

**删 UI 常驻**：`footer.demo`、`config.disc`、`preview.hint`、`compare.hint`、`sugar.summary`、`preview.matrix_hint`；侧栏 foot、页头 disc/hint 已移除或隐藏；矩阵说明改 tooltip。

**改名**：`group.expand` → 约束预览 / Constraints；`group.aux` → T1 / T2 / T3；`gates.read_only` → fail_job（只读进 Tooltip）；`lang.chrome` → 语言 / Language；`brand.sub` 空；`t3.no_bars` 自然句。

**缩短**：`dry.pass` 仅「预检通过」；详情进日志；`typical.status` 仅 `{kind}`；tooltips 去「GUI 不自写/不重算」说教。

**布局 A**：配置页单列 — 表单 → YAML → 预检/运行 → 约束预览（可折叠全宽）→ 日志 → 底栏历史。不再右栏 2×2。

**README**：一句「本 GUI 默认跑演示数据；自选 .db 时界面不承诺精度结论」——仅文档，界面不展示。

截图：`screenshots/p1_dark_config_zh.png`、`p1_dark_config_en.png`（及 dark/light compare / light config）。

## 已知限制

1. 顶层仍为 QMainWindow（P1-L1 Won't）；FluentWindow 在 offscreen 会 abort。
2. T3 对仅含 `relative_improve` 的 YAML 经引擎展开后再取 ≥1 speed + ≥1 power；sample 仅 speed 相对约束时 T3 只有 speed 柱。
3. T2 为报表/脚本摘录与展示，不在 GUI 重算 p95 阈值。
4. 浅色强调色为加深琥珀 `#B87A12`（非陶土）；截图 offscreen grab 可能偏平。
5. P1-E `services/run_job_api.py` 已提供薄封装；主路径仍为 QProcess CLI。


## 自测跑通记录

- 时间：2026-10-22 Asia/Shanghai（i18n zh/en 切换落地后）
- `smoke_p1.py` → ALL P1 SMOKE OK（含 locale/i18n 检查）
- `capture_p1.py` → `p1_dark_config_{zh,en}.png` + dark/light compare
- 行为未改；叠写双语已拆除

## 自测跑通记录 · 文案自查

- 时间：2026-10-22 Asia/Shanghai（DEMO 免责移除 + 约束预览 + 布局 A）
- `smoke_p1.py` → ALL P1 SMOKE OK
- `capture_p1.py` → 新 zh/en 配置截图无 disc/footer/summary
