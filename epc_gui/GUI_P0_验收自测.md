# GUI-P0 验收自测

日期：2026-10-22（Asia/Shanghai）

## 设计

- 计划：`/workspace/epc_gui/DESIGN.md`
- 色板摘要：InkWell `#0E1419` · PanelSteel `#1C252E` · TraceAmber `#E8A838` · PvtCyan `#3DB8C5` · PassTeal `#4A9B7A` · FailRose `#C45B6A`
- 壳：自定义 QMainWindow「探针台」导航（`FluentWindow` 在 offscreen/xvfb 下 frameless abort，P0 用同色板自绘壳；仍 `setTheme(DARK)` + `ThemeColor=TraceAmber`）

## T0

- 标注：`typical=median_cell`（N×N 取 `mid=n//2` 交叉格；非全表 median）
- 自测：`scripts/smoke_headless.py` 单元断言 index 12→42.0；sample `tcq` 双 PVT 各 9 点、capacity 升序、spot rel_err=0

## 命令与结果

```bash
source /workspace/epc_gui/.venv/bin/activate
export PYTHONPATH=/workspace

# 1) 依赖
python -c "from PyQt6.QtWidgets import QApplication; import pyqtgraph,yaml; print('OK')"

# 2) brief start/quit
QT_QPA_PLATFORM=offscreen python /workspace/epc_gui/scripts/brief_start_quit.py
# → started OK

# 3) headless smoke
python /workspace/epc_gui/scripts/smoke_headless.py
# → sample COUNT=4950 audit PASS
# → red residual H3-hard EXIT=1 未落盘 audit FAIL H3-hard=FAIL
# → ALL SMOKE OK

# 4) screenshots
QT_QPA_PLATFORM=offscreen python /workspace/epc_gui/scripts/capture_screenshots.py
```

| 检查 | 结果 |
|---|---|
| Deps | OK（venv + libegl1） |
| `python -m epc_gui` offscreen start/quit | started OK |
| sample COUNT | 4950 |
| sample audit | PASS / gates_ok True |
| T0 median_cell unit | OK |
| T0 series ≥3 caps × ≥2 PVT | 9×2，rel_err 0 |
| red H3-hard | EXIT=1，无 db，audit FAIL，H3-hard=FAIL |
| 截图 | `screenshots/page_{a_config,b_preview,c_compare,c_fail_h3hard}.png` |

## 联调 YAML

- sample：`/workspace/epc_fixtures/epc_job.sample.yaml`
- P1 绿：`/workspace/epc_fixtures/p1/epc_job.p1_improve_green.yaml`
- P2 Geom 绿：`/workspace/epc_fixtures/p2/job_corner_fill_green.yaml`
- residual H3-hard 红：`/workspace/epc_fixtures/p2/job_corner_fill_residual_h3hard.yaml`

## 已知限制

1. `qfluentwidgets.FluentWindow` 在 `QT_QPA_PLATFORM=offscreen` 下构造即 abort → P0 用 DESIGN 色板自绘壳。
2. 辅证 T1 对「相对约束 locator」可能是外推点，max_rel_err 不一定 &lt;1e-9；seed 点需选 seed_from_A。
3. GUI 不重写引擎门禁；解析失败显示「未知」。
