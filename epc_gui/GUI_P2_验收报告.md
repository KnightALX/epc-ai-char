# EPC GUI-P2 正式验收报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS**（阻塞缺陷：无） |
| 日期 | 2026-10-22 11:44 Asia/Shanghai |
| 规格 | `/workspace/EPC_GUI_P2_需求_v0.md` **v0.3**（U0–U6；Kai 四问全按推荐） |
| 代码 | `/workspace/epc_gui/`（验收**未改**产品代码） |
| 验收方 | 独立复跑 smoke + 服务层抽检 + 截图目视（非盲签开发自测） |
| 开发自测 | `/workspace/epc_gui/GUI_P2_验收自测.md`（仅参考） |

---

## 1. 冒烟复跑（独立）

```bash
cd /workspace
PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/smoke_p1.py
# → ALL P1 SMOKE OK ；EXIT 0

PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/smoke_p2.py
# → ALL P2 SMOKE OK ；EXIT 0

PYTHONPATH=/workspace QT_QPA_PLATFORM=offscreen \
  /workspace/epc_gui/.venv/bin/python /workspace/epc_gui/scripts/capture_p2.py
# → EXIT 0 ；截图已刷新
```

| 脚本 | 结果 |
|---|---|
| `smoke_p1.py` | **ALL P1 SMOKE OK**（EXIT **0**） |
| `smoke_p2.py` | **ALL P2 SMOKE OK**（EXIT **0**） |
| `capture_p2.py` | EXIT **0**（本轮独立重抓） |

`smoke_p2` 关键打印（摘录）：

- U2：`views=['rel_bars','bound_cells','constraint_list']` default=`rel_bars`；rel=16 bound=1 list=17
- U1：empty constraints `has=False` views=`[]`
- U3/U4/U5：`empty=None` pvt=`FFGNP_…` key=`tcq` cover=`6/23` Δmed=`0.0` n_pts=`23`
- polish：`overall='通过'` db=`'已落盘'` hover_tips=`16`；ComparePage visibility OK

---

## 2. U0–U6 证据表

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| **U0** | 回归 + 门禁只读 | **PASS** | 独立复跑 `smoke_p1`+`smoke_p2` 均 EXIT 0。门禁：`parse_audit` → `_apply_summary`；灯条/短摘录/打开全文；`lbl_gates_ok` 隐藏且无 `gates_ok` 裸奔。坏 audit：`parse_ok=False` → 总体「未知」MuteFog，**≠绿**（独立合成护栏）。EXIT 来自上下文子进程码，GUI 不自算 PASS/FAIL |
| **U1** | 图一无约束 | **PASS** | `build_chart1` 空 constraints → `has_constraints=False`、`views=[]`。Qt：`chart1_box` 隐藏 + `lbl_chart1_empty` 显示「无约束」。截图 `p2_dark_compare_no_constraints.png` / `p2_light_compare_no_constraints.png` |
| **U2** | 图一有约束 | **PASS** | p1_green：三视图可下拉；默认 `rel_bars`。i18n 标题「结果约束反标」/ Constraint markup。横轴①②③…；`_c1_hover_tips` 非空（细则 type/instance/pvt/key）。截图 `p2_*_compare_chart1_constraints.png`、`p2_dark_compare_en.png` |
| **U3** | 图二交集 | **PASS** | `build_free_compare`：`pvt_opts = pa & pb`；key 优先当前 PVT 下两库交集，否则全局 `ka & kb`。独立：两库 PVT 40∩11=**8**，单边项不在 `pvt_options`；缺构造库 → `empty_reason=need_dbs`、选项空 |
| **U4** | 图二曲线 | **PASS** | cover_m=`23`≥3；双值点 `both=6`；容量升序。图例参考虚线 MuteFog / 构造实线 TraceAmber（`compare_page`）。截图门禁下方图二可见双折线 + capacity 横轴 |
| **U5** | 右侧 Text | **PASS** | 文案「对齐 n/m」「中位差 ±x%」（zh）/ Aligned · Median Δ（en）；改 key 后 `build_free_compare` 重算。只读描述，**不写 audit、不改灯条**（右侧与 `_apply_summary` 无耦合） |
| **U6** | 美学 | **PASS** | 布局门禁→图一→图二；少文案；深/浅×有/无约束截图齐。`LIGHT.PlotCanvas=#FFFFFF`（InkWell 仍 `#EEF1F5`）；浅色截图图区像素抽检大量精确 `#FFFFFF`。无 `gates_ok`/路径裸奔；无长说明书。单语 zh/en 截图无叠写 |

Should（P2-S1–S5）未做者不挡 PASS；Won't（P2-W1–W4）未当缺陷。

---

## 3. 截图清单

| 文件 | 用途 |
|---|---|
| `/workspace/epc_gui/screenshots/p2_dark_compare_chart1_constraints.png` | 深色 · 有约束：门禁+图一①②③+图二双线+右侧对齐/中位差 |
| `/workspace/epc_gui/screenshots/p2_dark_compare.png` | 深色 · 对比总览（同有约束） |
| `/workspace/epc_gui/screenshots/p2_dark_compare_no_constraints.png` | 深色 · 无约束：图一隐藏 +「无约束」；图二仍可用 |
| `/workspace/epc_gui/screenshots/p2_dark_compare_en.png` | 深色 · English（Constraint markup / Free compare / Aligned） |
| `/workspace/epc_gui/screenshots/p2_light_compare.png` | 浅色 · 有约束；PlotCanvas 纯白 |
| `/workspace/epc_gui/screenshots/p2_light_compare_chart1_constraints.png` | 浅色 · 图一有约束 |
| `/workspace/epc_gui/screenshots/p2_light_compare_no_constraints.png` | 浅色 · 无约束空态 |
| `/workspace/epc_gui/screenshots/p2_dark_config.png` | 深色 · 配置（回归观感） |
| `/workspace/epc_gui/screenshots/p2_light_config.png` | 浅色 · 配置 |

---

## 4. 已知限制（非阻塞）

1. 图一 `rel_bars` 最多绘约 16 条相对 locator；完整清单看 `constraint_list`（开发自测已声明）。
2. 图二 Δmean、typical 改 min/max/指定 cell、导出 PNG·CSV、eval_h3/hold-out 回灌为 **Should**，未做不挡 PASS。
3. T0 多 key 分面主视图已降出 Must（规格 Q3）。
4. 顶层仍为 **QMainWindow**（FluentWindow Won't / offscreen 风险）。
5. offscreen grab 对比图偏平；live 下 hover 细则、下拉切换观感建议人工点一次（非阻塞）。
6. 本轮 DEMO fixture（`p1_green` / sample 路径）≠ 真 PDK；未接真库（Won't P2-W2）。

---

## 5. Live GUI 建议（非必须阻塞）

1. 对比页：有约束时切换 `rel_bars` / `bound_cells` / `constraint_list`；hover ①②③ 看细则。
2. 无约束 YAML：确认图一整区隐藏 + 一句「无约束」，图二仍可选 PVT/key。
3. 改 PVT/key 看右侧「对齐 / 中位差」即时更新，灯条不变。
4. 深↔浅、中↔英：无叠写、浅色图区仍为纯白。

---

## 6. 结论

**GUI-P2 正式验收：PASS。** U0–U6 均无阻塞失败；门禁只读 audit/EXIT（未知≠绿）；图一有约束才绘并对准 locator；图二为两库交集自由对比 + 右侧描述性 Text（不当门禁）；美学与浅色 PlotCanvas `#FFFFFF` 符合 Kai 已确认口径。

报告路径：`/workspace/epc_gui/GUI_P2_验收报告.md`
