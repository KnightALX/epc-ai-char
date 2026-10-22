# EPC Desktop GUI — Design plan (P0 + P1 + P2)

Subject: local **SRAM / TCAM characterization** job console — configure EPC jobs, run `epc_engine`, inspect `char_data`, prove gates from audit, read capacity×typical timing/power trends across PVT. Audience: Kai / EDA char engineers. Job of the UI: dense, trustworthy instrument — not a marketing dashboard.

Reviewed against FRONTEND_DESIGN: deliberately avoids cream+terracotta, acid-green-on-black, SaaS identical rounded-card stacks, tracked ALL-CAPS eyebrows, and button trailing "→".

---

## Color — dark (default)

| Token | Hex | Role |
|---|---|---|
| **InkWell** | `#0E1419` | App canvas / window background (fab-floor ink, cool not pure black) |
| **PanelSteel** | `#1C252E` | Nav rail, sticky job strip, elevated field groups |
| **RuleLine** | `#2A3540` | Hairline separators, table grid, plot axes |
| **Chalk** | `#D8DEE6` | Primary readable text |
| **MuteFog** | `#8B96A3` | Secondary labels, tooltips |
| **TraceAmber** | `#E8A838` | Single accent: Run, selected nav, focus ring, primary series highlight |
| **PvtCyan** | `#3DB8C5` | Secondary data: PVT series 2+, links, optional A.db overlay |
| **PassTeal** | `#4A9B7A` | Gate PASS only (status, never chrome fill) |
| **FailRose** | `#C45B6A` | Gate FAIL / 未落盘 only |
| **PlotCanvas** | `#0E1419` | pyqtgraph drawing area (= InkWell on dark) |

Extended PVT line cycle (pyqtgraph): TraceAmber, PvtCyan, `#C084FC` (VioletProbe), `#F0A06A` (Copper), `#6B9BD1` (SkySteel), `#9BC47A` (Moss). Max 6 simultaneous series before recycling.

Plot canvas (**PlotCanvas**) = InkWell on dark; axis/grid = RuleLine; legend text = MuteFog.

---

## Color — light (P1 theme toggle)

Cool steel / ink light — **not** cream `#F4F1EA` / terracotta `#D97757`.

| Token | Hex | Role |
|---|---|---|
| **InkWell** | `#EEF1F5` | Cool paper canvas (blue-grey, not warm cream) |
| **PanelSteel** | `#FFFFFF` | Rail / bands / sticky strip |
| **RuleLine** | `#C5CED8` | Hairlines, grid |
| **Chalk** | `#1A2330` | Primary ink text |
| **MuteFog** | `#5A6675` | Secondary labels |
| **TraceAmber** | `#B87A12` | Accent on light (darker amber for WCAG) |
| **PvtCyan** | `#1A8A96` | PVT series / links |
| **PassTeal** | `#2D7A5A` | PASS lamps |
| **FailRose** | `#B04050` | FAIL lamps |
| **PlotCanvas** | `#FFFFFF` | **pyqtgraph drawing area only** — pure white for screenshots; page InkWell stays `#EEF1F5` |

Same PVT cycle hues, slightly deepened for light plots. Light **plot canvas** = `#FFFFFF` (not InkWell grey-blue); axes = RuleLine.

**Forbidden for light:** cream base, terracotta/clay accent, pastel peach fills, warm beige cards.

---

## Type

Qt system stack (no web font download required):

| Role | Stack | Use |
|---|---|---|
| **UI** | `"Noto Sans"`, `"Source Sans 3"`, `"Segoe UI"`, `"PingFang SC"`, `"Noto Sans CJK SC"`, `sans-serif` | Page titles, forms, buttons — **sentence case**, medium weight for titles |
| **Data** | `"IBM Plex Mono"`, `"Cascadia Mono"`, `"DejaVu Sans Mono"`, `"Noto Sans Mono"`, `monospace` | instance / pvt / EXIT / COUNT / YAML paths / cell values |
| **Scale** | Title 18–20px · Section 13px MuteFog · Body 13px Chalk · Data 12px mono · Micro 11px MuteFog | Tight leading (~1.25) |

Avoid: ALL-CAPS eyebrows, single-word italic accents in titles, button trailing "→".

---

## Layout

**Concept:** *Probe-station rack* — cool steel rail left; continuous work surface right with sticky job strip (name · mode · EXIT · theme). Content is **field bands** + hairlines, not soft card stacks.

**P1 additions**

| Control | Placement |
|---|---|
| Constraint preview | Page A full-width collapsible under YAML/run; table only, no metadata bar |
| Dry-run「预检」 | Beside 运行; short PassTeal / FailRose (no B.db write) |
| Job history | Page A bottom strip; click → reload YAML / audit; `state/job_history.json` |
| Theme + language | Sticky strip; `theme` + `locale` in `state/settings.json` (independent) |
| T0 multi-key facet | Page C stacked plots when ≥2 keys |
| Export PNG/CSV | Page C → `exports/` |
| eval_h3 / hold-out | Page C aux buttons |

**Density:** 8–12px padding; 1px RuleLine; radius ≤4px on controls only.

---

## Principles

1. **Instrument, not SaaS** — hairlines; no decorative card grids.
2. **One amber signal** — TraceAmber for Run / selection only.
3. **Compare IA (P2 / P2.1)** — Gates (read-only) → Chart 1 constraint markup + audit `达标 n/m` (hidden if none) → Chart 2 free A/B capacity×`typical=median_cell` with 对齐 + Δmed + Δmean (descriptive, not a gate).
4. **Mono for locators** — instance×pvt×key and EXIT in Data face.
5. **Honest gates** — never invent PASS/FAIL in the UI; no persistent DEMO disclaimer microcopy.
6. **Theme parity** — light = same instrument on cool steel paper; never cream+terracotta.

---

---

## Writing (P1 copy)

**Language switch (not stacked bilingual):** Settings strip label is locale-local (`语言` / `Language`); combo lists 中文 | English. Persists `locale: zh|en` in `state/settings.json` (independent of theme). Visible UI shows **one** locale at a time via `epc_gui/i18n` (`tr(key)`). Do **not** put `中文 / EN` on every control.

Keep labels short; put implementation constraints in **Tooltip** or one MuteFog secondary line — avoid long parenthetical titles. Proper nouns may stay English in both locales: YAML, EXIT, PVT, audit, db, T0–T3, eval_h3, fail_job. Theme button text is locale-aware (`深色`/`浅色` or `Dark`/`Light`).

## Self-check (FRONTEND_DESIGN)

| Risk default | Our choice |
|---|---|
| Cream + terracotta | Dark InkWell+TraceAmber; light `#EEF1F5`/`#B87A12` — never `#F4F1EA`/`#D97757` |
| Acid green dark | PassTeal only on PASS lamps |
| Identical rounded cards | Field bands + hairlines, radius ≤4 |
| ALL-CAPS / → buttons | Sentence case; one locale at a time (`运行` / `Run` via switch) |
| Generic Fluent grey | ThemeColor + QSS from this token set |

**Copy hygiene:** No persistent DEMO / accuracy-disclaimer footers or page-header hints. Empty i18n keys (`footer.demo`, `config.disc`, `preview.hint`, `compare.hint`, `sugar.summary`, `preview.matrix_hint`) stay empty; widgets are removed or hidden. Constraint panel title = 约束预览 / Constraints. `lang.chrome` is locale-local (语言 / Language), never stacked bilingual.


## P2 Compare page

| Band | Role |
|---|---|
| Gate zone | Read-only lamps + short audit excerpt + open full; unknown ≠ green |
| Chart 1 | Constraint markup; views `rel_bars` / `bound_cells` / `constraint_list`; sugar via engine `load_job`; **hide entire band** when no constraints + one empty-state line; **P2.1**旁侧 `约束 达标 n/m`（只读 audit `[PASS]`/`[FAIL]`，不改灯） |
| Chart 2 | Free compare: reference vs constructed; PVT/key = intersection; dual polylines (ref dashed MuteFog, constructed solid TraceAmber); right Text `对齐 n/m` · `中位差` · **`均值差`（P2.1）** |

T0 multi-key facet as main view is **out of Must**. eval_h3 / hold-out remain thin Should controls.

### Compare layout (probe-station bands)

```
+------+----------------------------------------------------------+
| EPC  | sticky: job · mode · EXIT · 语言 · 主题                    |
| 配置 |----------------------------------------------------------|
| 预览 | [门禁]  灯条 · 通过/未通过/未知 · EXIT · 已落盘 · 摘录     |
| 对比*|----------------------------------------------------------|
|      | [结果约束反标]  视图▾ · 图一 ①②③… + hover · 达标 n/m     |
|      |   (无约束 → 整区隐藏，一行空态)                            |
|      |----------------------------------------------------------|
|      | [自由对比]  参考/构造 · PVT · key · 刷新                   |
|      |   双折线 (ref 虚线 MuteFog | 构造 实线 TraceAmber) | 对齐 |
|      |                                                   | Δmed |
|      |                                                   | Δmean|
|      |----------------------------------------------------------|
|      | eval_h3 · hold-out · 薄日志                               |
+------+----------------------------------------------------------+
```

**Rhythm:** gate band compact (lamp accents only) → chart1 medium (bars + ordinal axis) → chart2 expands. Hairlines between bands; no stacked soft-shadow cards. Page margins 14/10; band gap 10–12px.

### Chart chrome

| Element | Token / rule |
|---|---|
| Plot bg | PlotCanvas (dark=InkWell; light=`#FFFFFF`) |
| Grid / axes | RuleLine, alpha ≈0.22 |
| Axis / legend text | MuteFog Data face |
| Chart1 bars | baseline MuteFog · B TraceAmber · target PvtCyan |
| Chart1 axis | ①②③… ordinals; long locators in hover only |
| Chart2 ref | dashed MuteFog, symbol 5 |
| Chart2 constructed | solid TraceAmber width 2, symbol 6 |
| Side readout | mono Data; cover + Δmed + Δmean; typical=median_cell in tooltip |
| Chart1 sat_rate | Readout beside view combo; audit-only counts; `约束 —` if unparseable |

---

## Visual polish self-check (this round)

| Check | Pass when |
|---|---|
| Probe-station, not SaaS | Field bands + hairlines; radius ≤4 on controls; no soft grey shadow stacks |
| One memorable focus | TraceAmber on Run / selected nav / constructed series only |
| Gate accents | PassTeal / FailRose on lamps & status text — no large teal/rose fill panels |
| Chart contrast | Ref dashed muted vs constructed solid amber readable on dark **and** light |
| Type hierarchy | Title 18 · Section MuteFog 13 · Body 13 · Data mono 12 · Micro 11 |
| Anti-patterns | No cream+terracotta, acid green chrome, ALL-CAPS eyebrows, button「→」 |
| Three pages one skin | Same margins / GroupBox / button / table QSS on config · preview · compare |
| Breathing density | Not a manual wall; empty microcopy removed; gate excerpt short |

---

## P2.1 thin enhancements

| Item | Rule |
|---|---|
| Chart1 `sat_rate` | Parse current job `*_audit.md` `## Constraints` → count `### [PASS]` / `### [FAIL]` → `约束 达标 n/m`; hide with chart1 when no constraints; unparseable → `约束 —`; **never** recompute from db or change gate lamps |
| Chart2 `Δmean` | Same δ as Δmed on `both` points; `mean(δ)×100` as `均值差 ±x.x%` / `Mean Δ`; empty both → `均值差 —`; not a gate |
