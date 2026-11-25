# EPC GUI-P1 正式验收报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS**（阻塞缺陷：无） |
| 日期 | 2026-10-22 10:29 Asia/Shanghai |
| 规格 | `/workspace/EPC_GUI_P1_需求_v0.md`（U0–U12） |
| 代码 | `/workspace/epc_gui/`（验收未改产品代码） |
| 验收方 | 独立复跑 + 截图/代码抽检（非盲签开发自测） |

---

## 1. 冒烟复跑（独立）

```bash
source /workspace/epc_gui/.venv/bin/activate
export PYTHONPATH=/workspace
QT_QPA_PLATFORM=offscreen python /workspace/epc_gui/scripts/smoke_p1.py
QT_QPA_PLATFORM=offscreen python /workspace/epc_gui/scripts/smoke_headless.py
```

| 脚本 | 结果 |
|---|---|
| `smoke_p1.py` | **ALL P1 SMOKE OK**（EXIT 0） |
| `smoke_headless.py` | **ALL SMOKE OK**（EXIT 0；sample COUNT=4950；H3-hard 红 EXIT=1 未落盘） |

`smoke_p1` 关键打印（摘录）：

- U10：`joblib`+`sklearn` importable；`requirements.txt` 含二者
- U1：`expanded_constraint_count=16` = `relative_rows=16`
- U2：vague dry-run fail 且不写 db；green dry-run ok expanded=16
- U4：`seed_from_A` max_rel=`0.000e+00`
- U11：geom lights H1/H2=PASS、H3-hard=SKIP；display=PASS；unk=False
- i18n / copy hygiene：OK（空键 + 无叠写双语禁词）

另：独立 CLI `python -m` 路径外，`eval_h3.py` 子进程实测 **EXIT 0**（约 3.2s）。

---

## 2. U0–U12 证据表

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| **U0** | P0 回归 | **PASS** | `smoke_headless`：sample 复用 B_out COUNT=**4950**、audit PASS；H3-hard 红 EXIT=1、**未落盘**；门禁仍只读 audit/EXIT（compare 页「打开 audit」+ 灯条，无 GUI 自算 PASS） |
| **U1** | 糖衣展开 | **PASS** | 独立：`load_job` 与 `expand_from_path(p1_improve_green)` 均为 **16**；GUI 表列 instance/pvt/key/delta_pct/sugar_origin（截图 zh/en 配置页「约束预览 / Constraints」） |
| **U2** | dry-run | **PASS** | vague → `ok=False`，目标 `B_out.p1_r1.db` **不存在**；green → 预检通过；实现为 `load_job` only（`services/sugar.py`） |
| **U3** | T0 facet | **PASS** | 截图 compare：≥2 key（tcq + tselr1）选中，图例 `facet · tcq`；导出 CSV 列含 **`key`**，实测 36 行、keys=`{tcq,tselr1_min_period}` |
| **U4** | T1 seed_from_A | **PASS** | smoke：DEMO max_rel=0 &lt; 1e-9，`st=seed_from_A`；compare 有手动 locator + 外推提示路径（`t1.manual`） |
| **U5** | T2+T3 | **PASS** | T2：compare 内嵌 `h3_report`/`hold-out` 摘录（截图可见 p95 表）；T3：GUI 先引擎展开糖衣再 `t3_bars`，独立复现 **speed/tcq + power/leakage_vddc** 各一柱（baseline/B/target 对齐 δ）；sample 仅 speed 柱为已知限制 |
| **U6** | 导出 | **PASS** | `exports/t0_compare_20261022_092531.csv`（2650B）+ `.png`（39141B）非空；CSV 字段 `capacity,instance,pvt,key,typical` |
| **U7** | eval_h3 / hold-out | **PASS** | 按钮绑定 `eval_h3.py` 子进程 + 打开 `algo_holdout_report.md`；独立跑 eval_h3 **EXIT 0**；路径均存在 |
| **U8** | 历史 | **PASS** | `state/job_history.json` **≥3** 条（含 sample/P1 run，EXIT=0）；点击 → `load_yaml_path` + 打开 audit/db 上下文（`config_page._on_history_click` / `app._on_history`） |
| **U9** | 主题 | **PASS** | 深↔浅截图齐全；`theme.LIGHT.InkWell=#EEF1F5`、`TraceAmber=#B87A12`；**非** cream `#F4F1EA` / terracotta `#D97757`；settings 持久化 `theme`+`locale` |
| **U10** | R1 依赖 | **PASS** | `requirements.txt` 含 `joblib`/`scikit-learn`；当前 venv 可 import；smoke U10 绿。**未**另起全空 venv 重装（非阻塞：见 §4） |
| **U11** | R3 解析 | **PASS** | P2 geom audit：H1/H2 PASS、H3-hard SKIP、G 灯非「未知」；P1 green audit G1–G3=PASS；未知≠总体绿逻辑在 smoke 有合成护栏 |
| **U12** | 美学 | **PASS** | `DESIGN.md` 已补浅色 token + P1 布局/文案；`FRONTEND_DESIGN` 反模式自检表存在；截图深浅×配置/对比；无叠写双语、无常驻 DEMO/disc/`sugar.summary` |

---

## 3. 观感 / 文案（非单独硬门禁，已核对）

| 声称 | 核验 |
|---|---|
| Settings zh\|en，控件无叠写双语 | 截图 `p1_dark_config_zh.png` / `_en.png`：侧栏与按钮分别为纯中文或纯英文；i18n 禁词扫描通过 |
| 删 DEMO 免责 / 页头 hint / sugar.summary 常驻小字 | 截图无 footer/disc；i18n 对应键为空；源码无 `tr("footer.demo")` 等常驻调用 |
| 「约束预览」通栏；配置竖排非右栏 2×2 | `config_page` Layout A 单列；截图确认全宽约束表 |
| 门禁只读 audit/EXIT | compare 灯条 + 打开 audit；gates 表单只读展示 `fail_job` |

---

## 4. 截图清单

| 文件 | 用途 |
|---|---|
| `/workspace/epc_gui/screenshots/p1_dark_config_zh.png` | 深色 · 配置 · 中文 |
| `/workspace/epc_gui/screenshots/p1_dark_config_en.png` | 深色 · 配置 · English |
| `/workspace/epc_gui/screenshots/p1_dark_config.png` | 深色 · 配置（与 zh 同代） |
| `/workspace/epc_gui/screenshots/p1_light_config.png` | 浅色 · 配置 |
| `/workspace/epc_gui/screenshots/p1_dark_compare.png` | 深色 · 对比（门禁+T0 facet+T1/T2/T3 区） |
| `/workspace/epc_gui/screenshots/p1_light_compare.png` | 浅色 · 对比 |

---

## 5. 已知限制（非阻塞）

1. 顶层仍为 **QMainWindow**（P1-L1 Won't）；FluentWindow offscreen abort 风险仍在。
2. **sample** YAML 仅 speed 相对约束时 T3 只有 speed 柱；P1 绿经展开后可同时出 speed+power。
3. T2 为报表/脚本摘录展示，**GUI 不重算** p95 门禁。
4. offscreen grab 对比图偏平；T3 柱图可能落在滚动区外，需 live 下滚确认像素。
5. P1-E `services/run_job_api.py` 薄封装已在；主路径仍 QProcess CLI（Should，不阻塞）。
6. U10 未在「全新空 venv」上从零 `pip install -r` 重装（现有 `.venv` + requirements + import 已过）。

---

## 6. Live GUI 建议（给父代理 / Kai）

下列 headless/截图已覆盖大部分 U，**建议**（非必须阻塞）在有显示的环境点一次：

1. 配置页：预检 vague → 失败文案；运行 P1 绿 → 历史新增一条并点选回填。
2. 对比页：多选 ≥2 key 看 facet 刷新；点「导出对比」确认新文件；点 eval_h3 / hold-out。
3. 切换 深↔浅、中↔英，确认无闪退、无叠写。
4. 下滚确认 T3 柱状图在 P1 绿上可见。

---

## 7. 结论

**GUI-P1 正式验收：PASS。** U0–U12 均无阻塞失败；引擎门禁语义未见 GUI 侧改写；观感清理（i18n、布局 A、免责移除）与规格一致。

报告路径：`/workspace/epc_gui/GUI_P1_验收报告.md`

---

## 附注 · 父代理截图目视（2026-10-22 10:30 CST）

独立查看 `screenshots/p1_*`：

1. **zh/en 配置**：顶栏语言切换后控件为单语，无叠写；约束预览通栏；配置竖排；未见 DEMO 免责/页头 hint 常驻小字。
2. **对比页**：门禁只读 PASS/EXIT；T0 facet（多 key）；T1 max_rel=0；T2/T3 区可见；有「导出对比」。
3. **深/浅**：`p1_light_*` 与 `p1_dark_*` 均在；浅色未见奶油底/陶土强调类反模式。

未再开 live 桌面点通；冒烟+截图足够支撑本轮 PASS。建议非阻塞 live：历史点选、导出落盘、深浅/中英切换。
