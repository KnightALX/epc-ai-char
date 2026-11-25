# Fluent redesign — acceptance evidence

Date: 2026-11-25. Scope: replace the hand-written Fusion+QSS skin with
PyQt-Fluent-Widgets (default FluentWindow shell + Fluent widgets on all pages),
keeping `epc_gui/services` and `epc_engine` logic untouched.

Plan: `docs/superpowers/plans/2026-11-24-gui-fluent-redesign.md`
Spec: `docs/superpowers/specs/2026-11-24-gui-fluent-redesign-design.md`

## 0. What changed

| File | Before | After |
| --- | --- | --- |
| `epc_gui/theme.py` | 423-line Fusion+QSS generator | 129-line Fluent adapter (`apply_theme`, `current_tokens`, `configure_plot`, `set_label_state`) |
| `epc_gui/app.py` | 359-line QMainWindow + rail + QSS | 294-line `FluentWindow` + `NavigationInterface` (config/preview/compare/settings) |
| `epc_gui/pages/settings_page.py` | — | 83-line `ScrollArea` page: dark `SwitchSettingCard`, language `SettingCard`+`ComboBox` |
| `epc_gui/i18n/catalog.py` | 311 lines | 321 lines (+5 settings keys ×2 locales) |
| `epc_gui/pages/config_page.py` | 506 lines | 508 lines, Fluent widgets + `HeaderCardWidget` bands |
| `epc_gui/pages/preview_page.py` | 210 lines | 220 lines, Fluent combo/table |
| `epc_gui/pages/compare_page.py` | 772 lines | 770 lines, Fluent cards/table + hover guard |
| `epc_gui/services/history.py` | default `theme="dark"` | default `theme="light"` |
| `epc_gui/services/job_runner.py` | `QProcess.setEnvironment` (broken) | `QProcessEnvironment` + `setProcessEnvironment` |
| `epc_gui/scripts/*` | constructed `MainWindow` directly | `build_main_window()` factory; new `ui_regression.py` |
| `epc_gui/requirements.txt` | Fluent optional/comment | `PyQt-Fluent-Widgets==1.11.3` pinned |
| `.github/workflows/epc-ci.yml`, `run_all_tests.ps1` | GUI smokes only | + UI interaction regression step |

## 1. Verification matrix (all run on Windows, Python 3.13.8, offscreen)

| Gate | Command | Result |
| --- | --- | --- |
| Engine fast | `python -m pytest tests -q -m "not slow"` | **78 passed, 1 deselected, 217.31s** |
| Engine slow | `python -m pytest tests -q -m "slow"` | **1 passed, 18.32s** |
| GUI boot | `python epc_gui\scripts\brief_start_quit.py` | `started OK` |
| P0 smoke | `python epc_gui\scripts\smoke_headless.py` | `ALL SMOKE OK` |
| P1 smoke | `python epc_gui\scripts\smoke_p1.py` | `ALL P1 SMOKE OK` |
| P2 smoke | `python epc_gui\scripts\smoke_p2.py` | `ALL P2 / P2.1 SMOKE OK` |
| UI interaction | `python epc_gui\scripts\ui_regression.py` | `UI REGRESSION EXIT code=0 failures=0` (38 checks) |
| Single entry | `powershell -File run_all_tests.ps1` | `ALL GATES OK`, exit 0 |
| Desktop window | `python -m epc_gui.app` (QT_QPA_PLATFORM=windows) | visible window, `MainWindowTitle="EPC Desktop"`, handle ≠ 0 |

UI regression checks (all green) cover: four-page stack; animated + deterministic
navigation and nav-item click routing; dark switch → `qconfig`/tokens and back;
language combo → locale + nav text; `load_shortcut(sample)` → job name/YAML/editor;
sugar table; vague dry-run (fail text + `FailRose`) and sample dry-run (pass text);
a real `run_job` through `QProcess` → exit 0, B.db 4950 rows, audit written,
`lbl_exit`, auto-switch to preview; preview paging (offset 0→80); chart1 three
views; out-of-range hover payloads; overall label + gate lights from audit;
history entry + click routing to compare with db path label; theme idempotence.

## 2. Deviations from the plan (all API-driven, each verified at runtime)

1. **Titled cards → `HeaderCardWidget`** (`config_page.py` ×4, `compare_page.py` ×3).
   `CardWidget` in 1.11.3 has no `setTitle`/`setCheckable`/`setChecked`; the plan's
   `retranslate()` calls would raise `AttributeError`. `HeaderCardWidget` owns
   `viewLayout` + `setTitle`, so child layouts were re-parented into it.
2. **`TableWidget(rows, cols)` → `TableWidget(parent)` + `setRowCount/ColumnCount`.**
   1.11.3 signature is `(self, parent=None)`; the 3-arg call raised `TypeError`.
3. **`ComboBox.addItem(text, icon=None, userData=None)`.** The 2-arg QComboBox form
   put the view key into `icon`; switched to `userData=` (verified `currentData()`).
4. **Preview filter band title**: `CardWidget` has no title setter, so a
   `CaptionLabel` `lbl_filt` carries `preview.filter` (zh 过滤 / en Filter).
5. **`_on_c1_hover` int guard**: `QRectF.contains(int)` has no overload; a 2-line
   `isinstance(pos, (QPoint, QPointF))` guard keeps the production `SignalProxy`
   path identical and makes out-of-range probes exception-free.
6. **Card view margins trimmed** to `(12, 8, 12, 10)` to keep the dense compare
   page near QGroupBox density (page min-height 962 < shell 1269).
7. **Sugar band is no longer collapsible** (QGroupBox `checkable` had no Fluent
   equivalent chosen); it renders expanded by default — the old default state.
8. **`restyle` shim deleted** after all call sites migrated (repo grep: zero hits).

## 3. Real defect found by the UI regression

`job_runner.py` called `QProcess.setEnvironment(...)`, which does not exist in
PyQt5 (only `setProcessEnvironment(QProcessEnvironment)`). Every headless test used
`run_blocking()` (subprocess), so the interactive **Run** button had never actually
started a job. Fixed by building a `QProcessEnvironment`, prepending `repo_root()`
to `PYTHONPATH`, and calling `setProcessEnvironment`; the dead list-form branch of
`_ensure_repo_on_pythonpath` was removed. After the fix, `ui_regression` drives a real
job end-to-end: exit 0, 4950 rows, audit, preview auto-switch.

## 4. Screenshots (`epc_gui/screenshots/`, 19 PNGs, regenerated post-redesign)

- `page_a_config.png` 23811 B — config page, light Fluent shell, four bands.
- `page_b_preview.png` 23558 B — preview with sample DB loaded.
- `page_c_compare.png` 39255 B — compare, three-view chart1 + readout band.
- `page_c_fail_h3hard.png` 27298 B — red job: overall FAIL, H3-hard light FAIL.
- `capture_p1_*.png` ×6, `capture_p2_*.png` ×9 — view/locale/dark variants.

## 5. Known gaps (honest)

- Visual quality was **not** inspected by pixels — the analysis model cannot read
  images; a human pass over the 19 PNGs (or the live window) is still required.
- The desktop window probe verifies a real visible handle, not a pixel diff against
  a reference.
- CI job is written but not activated (repo has no git remote); `run_all_tests.ps1`
  is the exercised equivalent.
- Fluent shell was exercised on Windows only (offscreen + desktop); Linux/macOS
  paths rely on the same `build_main_window()` but were not run here.

## 6. Repro

```
python -m pip install -r requirements.txt
python -m pip install -r epc_gui/requirements.txt   # PyQt-Fluent-Widgets==1.11.3
powershell -ExecutionPolicy Bypass -File run_all_tests.ps1
python -m epc_gui.app                                # desktop window
```
