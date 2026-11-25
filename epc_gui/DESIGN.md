# EPC Desktop GUI — Design plan (P0 + P1 + P2)

Subject: local **SRAM / TCAM characterization** job console — configure EPC jobs, run `epc_engine`, inspect `char_data`, prove gates from audit, read capacity×typical timing/power trends across PVT. Audience: Kai / EDA char engineers. Job of the UI: dense, trustworthy instrument — not a marketing dashboard.

**Aesthetic baseline:** Virtuoso-like cool gray + blue (mainstream EDA calm). Reviewed against FRONTEND_DESIGN: deliberately avoids cream+terracotta, acid-green-on-black, SaaS identical rounded-card stacks, tracked ALL-CAPS eyebrows, and button trailing "→".

---

## Color — dark (default)

| Token | Hex | Role |
|---|---|---|
| **InkWell** | `#1E1E1E` | App canvas / window background (Virtuoso CIW cool near-black) |
| **PanelSteel** | `#2D2D30` | Nav rail, sticky job strip, elevated field groups |
| **RuleLine** | `#3E3E42` | Hairline separators, table grid, plot axes |
| **Chalk** | `#D4D4D4` | Primary readable text |
| **MuteFog** | `#9A9A9A` | Secondary labels, tooltips, EXIT / 已落盘 / side readouts |
| **AccentBlue** | `#4A90D9` | **Sole** accent: Run, selected nav bar, focus ring, primary series, constructed curve |
| **TraceAmber** | `#4A90D9` | Legacy alias → same as AccentBlue (no amber) |
| **PvtCyan** | `#6B7C8A` | Cool gray-blue secondary series (not high-sat cyan) |
| **PassTeal** | `#6A9F6A` | Gate PASS **lamp / overall status only** (never chrome fill, never auxiliary copy) |
| **FailRose** | `#C75B5B` | Gate FAIL lamp / overall / true error text only |
| **PlotCanvas** | `#1E1E1E` | pyqtgraph drawing area (= InkWell on dark) |

Extended PVT line cycle (pyqtgraph, blue-gray family): AccentBlue, SteelGray, SlateBlue, MistSteel, DeepSky, SilverFog. Max 6 simultaneous series before recycling. No high-sat purple / copper.

Plot canvas (**PlotCanvas**) = InkWell on dark; axis/grid = RuleLine; legend text = MuteFog.

**Auxiliary text rule:** Mute / section notes / side `对齐`·`中位差`·`均值差` / `约束达标 n/m` / audit snippet body → **MuteFog or Chalk only**. Never AccentBlue / PassTeal / FailRose on ordinary helper copy. Audit box does not color-highlight PASS/FAIL words (weight OK); color stays on left lamp + one overall status line.

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
| **AccentBlue** | `#2E6BB0` | Accent on light (deepened for WCAG) |
| **TraceAmber** | `#2E6BB0` | Legacy alias → AccentBlue |
| **PvtCyan** | `#5A6B7A` | Secondary series |
| **PassTeal** | `#3D7A3D` | PASS lamps |
| **FailRose** | `#B04040` | FAIL lamps |
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

**Concept:** *Virtuoso / probe-station rack* — cool steel rail left; continuous work surface right with sticky job strip (name · mode · EXIT · theme). Content is **field bands** + hairlines, not soft card stacks.

**P1 additions**

| Control | Placement |
|---|---|
| Constraint preview | Page A full-width collapsible under YAML/run; table only, no metadata bar |
| Dry-run「预检」 | Beside 运行; success = MuteFog short line; fail = FailRose (true error); no B.db write |
| Job history | Page A bottom strip; click → reload YAML / audit; `state/job_history.json` |
| Theme + language | Sticky strip; `theme` + `locale` in `state/settings.json` (independent) |
| T0 multi-key facet | Page C stacked plots when ≥2 keys |
| Export PNG/CSV | Page C → `exports/` |
| eval_h3 / hold-out | Page C aux buttons |

**Density:** 8–12px padding; 1px RuleLine; radius **≤2px** on controls only.

---

## Principles

1. **Instrument, not SaaS** — hairlines; no decorative card grids; radius ≤2.
2. **One blue signal** — AccentBlue for Run / nav bar / focus / constructed series only.
3. **Neutral EXIT / disk** — mono MuteFog; no green/red fill blocks on EXIT or 已落盘. True pass/fail = lamp + short overall word.
4. **Compare IA (P2 / P2.1)** — Gates (read-only) → Chart 1 constraint markup + audit `达标 n/m` (hidden if none) → Chart 2 free A/B capacity×`typical=median_cell` with 对齐 + Δmed + Δmean (descriptive, not a gate).
5. **Mono for locators** — instance×pvt×key and EXIT in Data face.
6. **Honest gates** — never invent PASS/FAIL in the UI; no persistent DEMO disclaimer microcopy.
7. **Theme parity** — light = same instrument on cool steel paper; never cream+terracotta.

---

## Writing (P1 copy)

**Language switch (not stacked bilingual):** Settings strip label is locale-local (`语言` / `Language`); combo lists 中文 | English. Persists `locale: zh|en` in `state/settings.json` (independent of theme). Visible UI shows **one** locale at a time via `epc_gui/i18n` (`tr(key)`). Do **not** put `中文 / EN` on every control.

Keep labels short; put implementation constraints in **Tooltip** or one MuteFog secondary line — avoid long parenthetical titles. Proper nouns may stay English in both locales: YAML, EXIT, PVT, audit, db, T0–T3, eval_h3, fail_job. Theme button text is locale-aware (`深色`/`浅色` or `Dark`/`Light`).

## Self-check (FRONTEND_DESIGN)

| Risk default | Our choice |
|---|---|
| Cream + terracotta | Dark InkWell+AccentBlue; light `#EEF1F5`/`#2E6BB0` — never `#F4F1EA`/`#D97757` |
| Acid green dark | PassTeal only on PASS lamps / overall |
| Identical rounded cards | Field bands + hairlines, radius ≤2 |
| ALL-CAPS / → buttons | Sentence case; one locale at a time (`运行` / `Run` via switch) |
| Generic Fluent grey | ThemeColor = AccentBlue + QSS from this token set |
| Amber marketing accent | Replaced by AccentBlue (Virtuoso-like) |

**Copy hygiene:** No persistent DEMO / accuracy-disclaimer footers or page-header hints. Empty i18n keys (`footer.demo`, `config.disc`, `preview.hint`, `compare.hint`, `sugar.summary`, `preview.matrix_hint`) stay empty; widgets are removed or hidden. Constraint panel title = 约束预览 / Constraints. `lang.chrome` is locale-local (语言 / Language), never stacked bilingual.


## P2 Compare page

| Band | Role |
|---|---|
| Gate zone | Read-only lamps + short audit excerpt + open full; unknown ≠ green; EXIT / 已落盘 MuteFog mono |
| Chart 1 | Constraint markup; views `rel_bars` / `bound_cells` / `constraint_list`; sugar via engine `load_job`; **hide entire band** when no constraints + one empty-state line; **P2.1**旁侧 `约束 达标 n/m`（只读 audit，中性字） |
| Chart 2 | Free compare: reference vs constructed; PVT/key = intersection; dual polylines (ref dashed MuteFog, constructed solid AccentBlue); right Text `对齐 n/m` · `中位差` · **`均值差`（P2.1）** — all MuteFog/Chalk |

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
|      |   双折线 (ref 虚线 MuteFog | 构造 实线 AccentBlue) | 对齐 |
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
| Chart1 bars | baseline MuteFog · B AccentBlue · target RuleLine (deeper gray) |
| Chart1 bound line | MuteFog dashed (not FailRose) |
| Chart1 axis | ①②③… ordinals; long locators in hover only |
| Chart2 ref | dashed MuteFog, symbol 5 |
| Chart2 constructed | solid AccentBlue width 2, symbol 6 |
| Side readout | mono Data MuteFog/Chalk; cover + Δmed + Δmean; typical=median_cell in tooltip |
| Chart1 sat_rate | Readout beside view combo; audit-only counts; `约束 —` if unparseable |

---

## Visual polish self-check (this round)

| Check | Pass when |
|---|---|
| Virtuoso / probe-station, not SaaS | Field bands + hairlines; radius ≤2 on controls; no soft grey shadow stacks |
| One memorable focus | AccentBlue on Run / selected nav bar / constructed series only |
| Gate accents | PassTeal / FailRose on lamps & overall — no large teal/rose fill panels; EXIT/disk neutral |
| Aux copy | No amber/cyan/teal/rose on Mute / side Δ / sat_rate / audit body |
| Chart contrast | Ref dashed muted vs constructed solid blue readable on dark **and** light |
| Type hierarchy | Title 18 · Section MuteFog 13 · Body 13 · Data mono 12 · Micro 11 |
| Anti-patterns | No cream+terracotta, acid green chrome, ALL-CAPS eyebrows, button「→」, amber marketing |
| Three pages one skin | Same margins / GroupBox / button / table QSS on config · preview · compare |
| Breathing density | Not a manual wall; empty microcopy removed; gate excerpt short |

---

## P2.1 thin enhancements

| Item | Rule |
|---|---|
| Chart1 `sat_rate` | Parse current job `*_audit.md` `## Constraints` → count `### [PASS]` / `### [FAIL]` → `约束 达标 n/m`; hide with chart1 when no constraints; unparseable → `约束 —`; **never** recompute from db or change gate lamps; text = MuteFog |
| Chart2 `Δmean` | Same δ as Δmed on `both` points; `mean(δ)×100` as `均值差 ±x.x%` / `Mean Δ`; empty both → `均值差 —`; not a gate |
