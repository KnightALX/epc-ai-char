# EPC GUI-P2.1 正式验收报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS**（阻塞缺陷：无） |
| 日期 | 2026-10-22 14:14 Asia/Shanghai |
| 规格 | `/workspace/EPC_GUI_P2_1_需求_v0.md` **v0**（U0–U4；Kai 两问全按推荐） |
| 代码 | `/workspace/epc_gui/`（验收**未改**产品代码；仅写入本报告） |
| 验收方 | 独立复跑 smoke + 手算 PASS/FAIL 与 mean(δ) + Qt 空态/边界 + 截图目视（非盲签开发自测） |
| 开发自测 | `/workspace/epc_gui/GUI_P2_1_验收自测.md`（仅参考） |
| 基线 | GUI-P2 PASS（`/workspace/epc_gui/GUI_P2_验收报告.md`） |

---

## 1. 冒烟复跑（独立）

```bash
cd /workspace
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/smoke_p1.py
# → ALL P1 SMOKE OK ；EXIT 0

PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/smoke_p2.py
# → ALL P2 / P2.1 SMOKE OK ；EXIT 0

PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/capture_p2.py
# → EXIT 0 ；截图已刷新
```

| 脚本 | 结果 |
|---|---|
| `smoke_p1.py` | **ALL P1 SMOKE OK**（EXIT **0**） |
| `smoke_p2.py` | **ALL P2 / P2.1 SMOKE OK**（EXIT **0**） |
| `capture_p2.py` | EXIT **0**（本轮独立重抓） |

`smoke_p2` 关键打印（摘录）：

- U2 chart1：`views=['rel_bars','bound_cells','constraint_list']` default=`rel_bars`
- U3/U4/U5 free：`cover=6/23` Δmed=`0.0` **Δmean=`0.0`**（默认 PVT×`tcq`）
- P21-M1：`sat parseable=True n/m=17/17`；UI `约束 达标 17/17`
- P21-M2：UI `均值差 +0.0%`
- polish：`overall='通过'`；ComparePage visibility + P2.1 OK

---

## 2. U0–U4 证据表

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| **U0** | 回归 + 门禁只读 | **PASS** | 独立复跑 `smoke_p1`+`smoke_p2` 均 EXIT 0。门禁灯行为与 P2 一致：坏/缺失 audit → `lbl_overall='未知'`（**≠绿**）；`exit_code=0` + 可解析 audit →「通过」。灯条仍只读 `parse_audit` + EXIT；`lbl_gates_ok` 空隐藏。达标/Δmean **不**参与判决 |
| **U1** | 达标有约束 | **PASS** | audit=`/workspace/epc_fixtures/p1/B_out.p1_green_audit.md`。**独立**正则手算 `## Constraints` 下 `### [PASS]`/`[FAIL]`：**PASS=17 FAIL=0 m=17**。`parse_constraint_sat_rate` → `17/17`；Qt `lbl_sat='约束 达标 17/17'`（有约束可见）。切图一视图不改口径（同源 audit）。截图浅/深/en 均见 `17/17` 或 `Constraints 17/17` |
| **U2** | 达标空态 | **PASS** | 无约束（yaml `constraints=[]`）：`chart1_box` 隐藏且 `lbl_sat` 隐藏/清空。有约束但 audit=`out_geom_audit.md`（Constraints 段无 `[PASS]`/`[FAIL]` 标记）：`lbl_sat='约束 —'`；门禁文案不含「达标」，灯不因该 Text 变绿/变红。截图 `p2_dark_compare_no_constraints.png` 见「无约束」、图一/达标区隐藏 |
| **U3** | Δmean | **PASS** | 默认 `FFGNP_…×tcq`：`both=6`，gui `delta_mean_pct=0.0`，手算 `mean(δ)×100=0.0`，\|gui−hand\|=`0`（&lt;1e-9）。非零抽检：`SSGNP_0P99V_0P99V_125C×tcq` → gui=`-1.3333333333333313`，手算同值，**相对误差=0**；UI 改 PVT/key 后 `lbl_delta_mean='均值差 -1.3%'`。右侧三行：对齐 · 中位差 · 均值差；**不当门禁** |
| **U4** | 美学 / 边界 | **PASS** | 深/浅×有约束截图齐；en 见 `Constraints 17/17` + `Mean Δ`。少文案；门禁区判决文案（overall / EXIT / 短摘录 / G1–G3）**无**「达标」「均值差」「Mean Δ」。i18n 门禁相关键无混入 sat/Δmean（sat/Δmean 仅 `chart1.sat_*` / `free.delta_mean*`）。浅色对比页图区可见大量 `#FFFFFF` |

Should（P21-S1/S2）未做者不挡 PASS；Won't（P21-W1–W4）未当缺陷。DEMO fixture ≠ 真 PDK。

---

## 3. 独立手算数字（摘要）

| 项 | 值 |
|---|---|
| audit | `epc_fixtures/p1/B_out.p1_green_audit.md` |
| 达标 n/m（手算） | **17/17**（17×`[PASS]`，0×`[FAIL]`） |
| 默认 Δmean（`FFGNP_0P80V_0P80V_25C`×`tcq`，both=6） | **+0.0%**（gui=hand，err=0） |
| 非零 Δmean（`SSGNP_0P99V_0P99V_125C`×`tcq`，both=6） | **−1.333…%**（相对误差 **0**）；UI 显示 `均值差 -1.3%` |

---

## 4. 截图清单

| 文件 | 用途 |
|---|---|
| `/workspace/epc_gui/screenshots/p2_light_compare.png` | 浅色 · 有约束：图一旁 **约束 达标 17/17** + 图二右侧 **均值差 +0.0%** |
| `/workspace/epc_gui/screenshots/p2_light_compare_chart1_constraints.png` | 浅色 · 同有约束（图一焦点） |
| `/workspace/epc_gui/screenshots/p2_dark_compare_chart1_constraints.png` | 深色 · 有约束：达标 + 均值差 |
| `/workspace/epc_gui/screenshots/p2_dark_compare.png` | 深色 · 对比总览（同有约束） |
| `/workspace/epc_gui/screenshots/p2_dark_compare_en.png` | 深色 · English：`Constraints 17/17` · `Mean Δ +0.0%` |
| `/workspace/epc_gui/screenshots/p2_dark_compare_no_constraints.png` | 深色 · 无约束：图一/达标隐藏 +「无约束」；图二均值差仍在 |
| `/workspace/epc_gui/screenshots/p2_light_compare_no_constraints.png` | 浅色 · 无约束空态 |
| `/workspace/epc_gui/screenshots/p2_dark_config.png` | 深色 · 配置（回归观感） |
| `/workspace/epc_gui/screenshots/p2_light_config.png` | 浅色 · 配置 |

---

## 5. 已知限制（非阻塞）

1. Should P21-S1（hover 提示「来自 audit 逐条」）、P21-S2（相对目标误差中位）未做，不挡 PASS。
2. Won't：真库/真 PDK、导出 PNG·CSV、`eval_h3`/hold-out 回灌、GUI 自算改灯、重开图一玩具/FluentWindow。
3. 默认 DEMO PVT×key 上构造≈参考 → Δmean 常为 `+0.0%`；非零需换 PVT（如 SSGNP…）——公式与刷新已独立验证。
4. offscreen grab 偏平；live 下建议点一次：有约束切视图、无约束空态、改 PVT/key 看均值差、深↔浅/中↔英（非阻塞）。
5. 本轮 DEMO fixture（`p1_green`）≠ 真 PDK。

---

## 6. Live GUI 建议（非必须阻塞）

1. 对比页有约束：确认图一旁「约束 达标 17/17」，切 `rel_bars`/`bound_cells`/`constraint_list` 后 n/m 不变。
2. 无约束 YAML：图一+达标隐藏，仅「无约束」；灯条不变。
3. 改 PVT 至 `SSGNP_0P99V_0P99V_125C`、key=`tcq`：右侧「均值差」应变为约 `−1.3%`，门禁不变。
4. 深↔浅、中↔英：无叠写；en 为 `Constraints n/m` / `Mean Δ`。

---

## 7. 结论

**GUI-P2.1 正式验收：PASS。** U0–U4 均无阻塞失败；回归冒烟绿；图一旁达标只读 audit 逐条计数（17/17）；空态「约束 —」/无约束隐藏正确；图二 Δmean 与手算 mean(δ) 一致（含非零用例相对误差 0）；达标与均值差未进入门禁判决文案。

报告路径：`/workspace/epc_gui/GUI_P2_1_验收报告.md`
