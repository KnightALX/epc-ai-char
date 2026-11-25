# GUI-P2.1 验收自测（开发侧 · 不自签）

日期：2026-10-22（Asia/Shanghai）  
规格：`/workspace/EPC_GUI_P2_1_需求_v0.md` v0 · Kai 两问全按推荐  
基线：GUI-P2 PASS

## 交付摘要

| ID | 项 | 实现 |
|---|---|---|
| **P21-M1** | 图一旁 `约束 达标 n/m` | `audit_parse.parse_constraint_sat_rate` 只读 `### [PASS]`/`[FAIL]`；有约束才显；缺段/`—`；**不改灯** |
| **P21-M2** | 图二右侧 `均值差 ±x.x%` | `FreeCompareModel.delta_mean_pct`；与 cover/Δmed 同 `both`；不当门禁 |
| **P21-M3** | smoke + 截图 + DESIGN/自测/i18n | 见下 |

Won't：真库、导出、eval_h3、改灯判决。

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

## U 表（开发侧自测）

| # | 项 | 标准 | 开发侧 |
|---|---|---|---|
| **U0** | 回归 | `smoke_p1` + `smoke_p2` EXIT 0；门禁灯行为与 P2 一致（未知≠绿） | 见 smoke 输出 |
| **U1** | 达标有约束 | `p1_green`：图一旁 `n/m` 与独立解析同份 audit 的 `[PASS]`/`[FAIL]` 一致 | smoke 内 hand-count |
| **U2** | 达标空态 | 无约束：无达标 Text；有约束但 Constraints 无标记：`约束 —`，灯不因此变 | smoke（empty yaml + `out_geom_audit.md`） |
| **U3** | Δmean | 图二右侧见均值差；与手算 `mean(δ)` 相对误差 &lt; 1e-9；改 key 后更新 | smoke hand-mean |
| **U4** | 美学 / 边界 | 截图深或浅×有约束；无长说明书；Δmean/达标**不**出现在门禁判决文案 | 截图路径见下 |

## 截图

| 文件 | 内容 |
|---|---|
| `screenshots/p2_light_compare.png` | 浅色有约束：图一旁达标 + 图二均值差（优先） |
| `screenshots/p2_light_compare_chart1_constraints.png` | 同浅色有约束 |
| `screenshots/p2_dark_compare_chart1_constraints.png` | 深色有约束 |
| `screenshots/p2_dark_compare_no_constraints.png` | 无约束：图一/达标隐藏 |
| `screenshots/p2_dark_compare_en.png` | English：`Constraints n/m` · `Mean Δ` |

## 改动文件（开发）

- `services/audit_parse.py` — `ConstraintSatRate` / `parse_constraint_sat_rate`
- `services/compare_views.py` — `FreeCompareModel.delta_mean_pct`
- `pages/compare_page.py` — `lbl_sat` / `lbl_delta_mean`
- `i18n/catalog.py` — sat / Δmean 文案
- `scripts/smoke_p2.py` — P2.1 断言
- `DESIGN.md` — P2.1 一句
- `GUI_P2_1_验收自测.md` — 本文

**验收另派，本文不自签 PASS。**
