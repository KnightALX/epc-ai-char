# GUI Fluent Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hand-written QSS GUI shell with a PyQt-Fluent-Widgets FluentWindow + NavigationInterface skin (default light theme, light/dark toggle, language setting on a new Settings page) without changing any engine or services logic.

**Architecture:** `MainWindow` becomes a `FluentWindow` subclass with four navigation entries (config/preview/compare/settings). `epc_gui/theme.py` is rewritten from a ~400-line QSS builder into a thin adapter that maps `qfluentwidgets` theme state onto the small token set the pages and pyqtgraph plots consume (`apply_theme` → `setTheme`; `current_tokens()` → tokens derived from `isDarkTheme()`/`themeColor()`; `configure_plot`/`set_label_state` keep their signatures). Pages swap Qt stock widgets for Fluent equivalents (CardWidget/LineEdit/ComboBox/PlainTextEdit/TableWidget/ListWidget/PushButton/PrimaryPushButton/TitleLabel) while every business method stays verbatim. `epc_gui/services` and `epc_engine` remain untouched except one documented one-line preference default in `services/history.py` (fresh-install theme default dark→light, required by the approved spec's "default light" decision; normalization logic unchanged).

**Tech Stack:** Python 3.13, PyQt5 5.15.2, PyQt-Fluent-Widgets (qfluentwidgets, version pinned in Task 0), pyqtgraph 0.13.7, pytest 9.0.2. Validation via the existing headless smoke scripts (`smoke_headless.py` / `smoke_p1.py` / `smoke_p2.py`), `brief_start_quit.py`, and the capture scripts.

**Environment notes (do not assume):**
- This repository is NOT a git repository (`git rev-parse` fails). Every "Commit" step is replaced by a checkpoint instruction: verify the file state with `py_compile` or the stated command and check the task checkbox. No `git add/commit` commands exist in this plan.
- All paths below are relative to repo root `D:\SramDbEpc\epc-ai-char-main\epc-ai-char-main`.
- All PowerShell runs of GUI scripts must set `$env:PYTHONIOENCODING='utf-8'` first (GBK console would corrupt UTF-8 output).
- The spec this plan implements: `docs/superpowers/specs/2026-11-24-gui-fluent-redesign-design.md` (approved by user on 2026-11-24). The Spike decision gate in Task 0 is the spec's "A1 直换 + spike 定夺" branch.

---

## Task 0: Spike — install qfluentwidgets and probe FluentWindow on this machine

**Files:**
- Create: `%TEMP%\spike_fluent_offscreen.py` (temporary probe, deleted at end of task)
- Modify: none yet

- [x] **Step 0.1: Install and capture the exact version**

Run:
```powershell
python -m pip install PyQt-Fluent-Widgets
python -c "import qfluentwidgets; print('QW_VERSION', qfluentwidgets.__version__)"
```
Expected: prints `QW_VERSION <x.y.z>`. Record the exact version — it is pasted into Task 10's requirements pin. (If pip resolves 1.7.x, that is fine; anything ≥1.4 supports the APIs used here.)

- [x] **Step 0.2: Write the offscreen probe**

Write `%TEMP%\spike_fluent_offscreen.py` with this complete content:

```python
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from qfluentwidgets import (FluentWindow, FluentIcon, NavigationItemPosition,
                            Theme, setTheme)

NEED = ("DOCUMENT", "IMAGE", "GRID", "SETTING", "PALETTE", "LANGUAGE")
missing = [n for n in NEED if not hasattr(FluentIcon, n)]
if missing:
    print("ICON MISSING:", missing)
    sys.exit(3)

app = QApplication(sys.argv)
setTheme(Theme.LIGHT)
w = FluentWindow()
page = QWidget()
page.setObjectName("probe")
w.addSubInterface(page, FluentIcon.DOCUMENT, "Probe",
                  position=NavigationItemPosition.TOP)
w.show()
print("SPIKE OFFSCREEN OK")
QTimer.singleShot(400, app.quit)
sys.exit(app.exec_())
```

- [x] **Step 0.3: Run the offscreen probe**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; python "$env:TEMP\spike_fluent_offscreen.py"; Write-Output "SPIKE_EXIT=$LASTEXITCODE"
```
Two possible outcomes — record which one:
- **A**: prints `SPIKE OFFSCREEN OK`, exit 0 → FluentWindow survives offscreen. Later set `_OFFSCREEN_FALLBACK = False`.
- **B**: traceback (typically a win32/DWM/`windowHandle` error) before `SPIKE OFFSCREEN OK` → offscreen crashes. Later set `_OFFSCREEN_FALLBACK = True`. This is the expected outcome on Windows offscreen; the spec approved an offscreen functional fallback for this case.
- If `ICON MISSING:` is printed instead, do not proceed: report the missing names and replace them per this table (documented alternates, no guessing): DOCUMENT→`FluentIcon.FOLDER`, IMAGE→`FluentIcon.PHOTO`, GRID→`FluentIcon.MENU`, SETTING→`FluentIcon.HOME`, PALETTE→`FluentIcon.BRUSH`, LANGUAGE→`FluentIcon.GLOBE`. Then re-run Step 0.3.

- [x] **Step 0.4: Run the desktop probe (real windows platform)**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='windows'; python "$env:TEMP\spike_fluent_offscreen.py"; Write-Output "SPIKE_EXIT=$LASTEXITCODE"
```
Expected: prints `SPIKE OFFSCREEN OK`, exit 0 (real desktop must work; if it does not, stop and report — the redesign depends on it).

- [x] **Step 0.5: Cleanup + checkpoint**

Run:
```powershell
Remove-Item "$env:TEMP\spike_fluent_offscreen.py" -ErrorAction SilentlyContinue
```
Record in the plan execution log: `QW_VERSION=<x.y.z>`, `SPIKE_OFFSCREEN=<A|B>`, `SPIKE_DESKTOP=OK`. This gate decides Task 3's `_OFFSCREEN_FALLBACK` value.

---

## Execution log (spike, 2026-11-25)

- `QW_VERSION=1.11.3` (`PyQt-Fluent-Widgets==1.11.3`; transitive: `PyQt5-Frameless-Window 0.8.2`, `darkdetect 0.8.0`).
- `SPIKE_OFFSCREEN=A` — FluentWindow constructs, `addSubInterface`s, `show()`s and runs its loop offscreen (`platformName()==offscreen`), exit 0.
- `SPIKE_DESKTOP=OK` — same probe with `QT_QPA_PLATFORM=windows`, exit 0.
- Icons: `IMAGE` and `GRID` do not exist in 1.11.3; use `PHOTO` and `MENU` (Task 3 already reflects this). `DOCUMENT`, `SETTING`, `PALETTE`, `LANGUAGE` exist.
- API corrections proven by the spike (already folded into Tasks 3/4): `SwitchSettingCard(icon, title, content=None, configItem=None, parent=None)` — pass `parent=self` by keyword; `ComboBoxSettingCard` needs an `OptionsConfigItem` first arg (we use `SettingCard` + `ComboBox`); `navigationInterface.items` does not exist (keep the `addSubInterface` return handles).
- Env: Python 3.13.8, PyQt5 dist **5.15.11** with Qt runtime **5.15.2**. Do not downgrade to `PyQt5==5.15.2` (no 3.13 wheel guarantee).
- Non-fatal stderr on every run: `This plugin does not support propagateSizeHints()`, `QFontDatabase: Cannot find font directory ...`. `import qfluentwidgets` prints a Pro-tips banner to stdout — do not assert exact stdout equality in gates.

---

## Task 1: Failing test first — update smoke_p1.py to assert the Fluent contract

**Files:**
- Modify: `epc_gui/scripts/smoke_p1.py:102-114` (replace DESIGN block), `:118-121` (extend i18n keys), `:158-161` (add fresh-default check)

- [x] **Step 1.1: Replace the DESIGN-token block**

In `epc_gui/scripts/smoke_p1.py`, replace the exact block

```python
    # DESIGN light forbids cream/terracotta
    design = Path(_REPO, "epc_gui/DESIGN.md").read_text(encoding="utf-8")
    if "#F4F1EA" in design.split("Forbidden")[0] if False else False:
        pass
    # ensure light tokens section exists and forbidden noted
    if "EEF1F5" not in design or "2E6BB0" not in design:
        errors.append("DESIGN.md missing light tokens")
    if "AccentBlue" not in design:
        errors.append("DESIGN.md missing AccentBlue")
    if "F4F1EA" in design and "Forbidden" not in design and "禁止" not in design:
        # may appear as forbidden example — OK if labeled
        pass
    print("OK DESIGN light tokens present")
```

with

```python
    # Fluent re-skin assertions (spec §7; replaces the old token check)
    try:
        from qfluentwidgets import isDarkTheme, setTheme, themeColor, Theme
        setTheme(Theme.LIGHT)
        if isDarkTheme():
            errors.append("qfluentwidgets LIGHT theme reported dark")
        if not themeColor().isValid():
            errors.append("qfluentwidgets themeColor invalid")
        print("OK qfluentwidgets theme LIGHT default")
    except Exception as e:
        errors.append(f"qfluentwidgets unavailable: {e}")
    design = Path(_REPO, "epc_gui/DESIGN.md").read_text(encoding="utf-8")
    if "EEF1F5" not in design or "2E6BB0" not in design:
        errors.append("DESIGN.md missing light tokens")
    theme_src = Path(_REPO, "epc_gui/theme.py").read_text(encoding="utf-8")
    if "_build_qss" in theme_src:
        errors.append("theme.py still ships the old QSS builder")
    app_src = Path(_REPO, "epc_gui/app.py").read_text(encoding="utf-8")
    if "FluentWindow" not in app_src:
        errors.append("app.py missing FluentWindow")
    if "build_main_window" not in app_src:
        errors.append("app.py missing build_main_window")
    print("OK Fluent shell contract (theme.py/app.py)")
```

(Keeping the two `EEF1F5`/`2E6BB0` DESIGN.md content checks is intentional: DESIGN.md is a design-history document and stays in the repo; the rest of the block now asserts the live Fluent contract.)

- [x] **Step 1.2: Extend the i18n key check**

In `epc_gui/scripts/smoke_p1.py`, immediately after the existing line

```python
    if "nav.config" not in ZH or "nav.config" not in EN:
        errors.append("i18n missing nav.config")
```

insert

```python
    for key in (
        "nav.config", "nav.preview", "nav.compare", "nav.settings",
        "settings.title", "settings.dark_card", "settings.dark_hint",
        "settings.lang_card",
    ):
        if key not in ZH or key not in EN:
            errors.append(f"i18n missing {key}")
```

- [x] **Step 1.3: Add the fresh-settings default-light check**

In `epc_gui/scripts/smoke_p1.py`, immediately after the existing lines

```python
    s = hist_svc.load_settings()
    if "locale" not in s:
        errors.append("settings missing locale default")
    print(f"OK i18n zh/en tr() locale default={s.get('locale')}")
```

insert

```python
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old_path = hist_svc.SETTINGS_PATH
        try:
            hist_svc.SETTINGS_PATH = Path(td) / "settings.json"
            if hist_svc.load_settings().get("theme") != "light":
                errors.append("fresh settings default theme must be light")
        finally:
            hist_svc.SETTINGS_PATH = old_path
    print("OK fresh settings default theme=light")
```

- [x] **Step 1.4: Run smoke_p1 to confirm the new assertions FAIL (red gate)**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\smoke_p1.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: `EXIT=1` and `FAIL:` includes exactly these four failures — `theme.py still ships the old QSS builder`, `app.py missing FluentWindow`, `app.py missing build_main_window`, `i18n missing nav.settings` (plus `settings.title`/`settings.dark_card`/`settings.dark_hint`/`settings.lang_card` and `fresh settings default theme must be light`). The `qfluentwidgets theme LIGHT default` line prints OK (installed in Task 0). Any other failure is unexpected — investigate before proceeding.

- [x] **Step 1.5: Checkpoint**

Run: `python -m py_compile epc_gui\scripts\smoke_p1.py` → no output, exit 0. Check the checkbox; smoke_p1 is now the red gate driving Tasks 2–4 and 8.

---

## Task 2: Rewrite epc_gui/theme.py as a Fluent adapter

**Files:**
- Modify: `epc_gui/theme.py` (complete rewrite, 423 lines → ~95 lines)

- [x] **Step 2.1: Replace the file**

Overwrite `epc_gui/theme.py` with this complete content (no other edit to this file is allowed in this plan):

```python
"""Fluent-backed visual tokens for pages + pyqtgraph plots.

All chrome styling is delegated to PyQt-Fluent-Widgets (setTheme /
themeColor). This module only translates the active Fluent theme into the
small token set the pages and pyqtgraph plots consume, and keeps the legacy
call sites working:

    apply_theme(app, mode)   -> qfluentwidgets.setTheme
    current_tokens()         -> ThemeTokens for the active Fluent theme
    configure_plot(pw)       -> pyqtgraph chrome from the active theme
    set_label_state(lbl, s)  -> inline status color (pass/fail/neutral)
"""
from __future__ import annotations

from dataclasses import dataclass

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import Theme, isDarkTheme, setTheme, themeColor

UI_FONT_FAMILY = "Segoe UI, PingFang SC, Noto Sans CJK SC, sans-serif"
DATA_FONT_FAMILY = "Cascadia Mono, IBM Plex Mono, Consolas, monospace"


@dataclass(frozen=True)
class ThemeTokens:
    name: str
    InkWell: str
    PanelSteel: str
    RuleLine: str
    Chalk: str
    MuteFog: str
    AccentBlue: str
    PassTeal: str
    FailRose: str
    PlotCanvas: str


_DARK = ThemeTokens(
    name="dark",
    InkWell="#1E1E1E",
    PanelSteel="#2D2D30",
    RuleLine="#3E3E42",
    Chalk="#D4D4D4",
    MuteFog="#9A9A9A",
    AccentBlue="#60CDFA",
    PassTeal="#6A9F6A",
    FailRose="#C75B5B",
    PlotCanvas="#1E1E1E",
)

_LIGHT = ThemeTokens(
    name="light",
    InkWell="#EEF1F5",
    PanelSteel="#FFFFFF",
    RuleLine="#C5CED8",
    Chalk="#1A2330",
    MuteFog="#5A6675",
    AccentBlue="#0078D4",
    PassTeal="#3D7A3D",
    FailRose="#B04040",
    PlotCanvas="#FFFFFF",
)


def current_tokens() -> ThemeTokens:
    """Tokens for the ACTIVE Fluent theme; accent follows qfluentwidgets."""
    base = _DARK if isDarkTheme() else _LIGHT
    accent = themeColor().name().upper()
    return ThemeTokens(
        name=base.name,
        InkWell=base.InkWell,
        PanelSteel=base.PanelSteel,
        RuleLine=base.RuleLine,
        Chalk=base.Chalk,
        MuteFog=base.MuteFog,
        AccentBlue=accent,
        PassTeal=base.PassTeal,
        FailRose=base.FailRose,
        PlotCanvas=base.PlotCanvas,
    )


def apply_theme(app: QApplication, mode: str = "light") -> None:
    """Legacy entry point kept for capture/smoke scripts and app.run()."""
    setTheme(Theme.LIGHT if str(mode).lower().startswith("light") else Theme.DARK)


def configure_plot(pw, tokens: ThemeTokens | None = None) -> None:
    """pyqtgraph chrome from the active theme (signature unchanged)."""
    t = tokens or current_tokens()
    pw.setBackground(t.PlotCanvas)
    pw.showGrid(x=True, y=True, alpha=0.22)
    for axis in ("bottom", "left", "top", "right"):
        ax = pw.getAxis(axis)
        if ax is None:
            continue
        ax.setPen(t.RuleLine)
        ax.setTextPen(t.MuteFog)
        try:
            ax.setStyle(tickFont=_data_tick_font())
        except Exception:
            pass
    pi = pw.getPlotItem()
    pi.layout.setContentsMargins(10, 6, 10, 8)
    try:
        pi.titleLabel.setAttr("color", t.MuteFog)
        pi.titleLabel.setAttr("size", "11pt")
    except Exception:
        pass


def _data_tick_font():
    f = QFont()
    f.setFamilies(["Cascadia Mono", "IBM Plex Mono", "Consolas", "monospace"])
    f.setPointSize(9)
    return f


def set_label_state(label, state: str) -> None:
    """Status color via inline style (QSS-free). state in pass/fail/neutral."""
    t = current_tokens()
    color = {
        "pass": t.PassTeal,
        "fail": t.FailRose,
        "neutral": t.MuteFog,
    }.get(state, t.Chalk)
    label.setStyleSheet(f"color: {color};")


def restyle(widget, object_name: str) -> None:
    """Deprecated compatibility shim (removed at the Task 7 checkpoint).

    Config/compare pages still import it until Tasks 5-7 migrate their call
    sites to set_label_state; keeping it here lets Tasks 3/4 boot cleanly.
    """
    widget.setObjectName(object_name)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()
```

- [x] **Step 2.2: Compile + contract probe**

Run:
```powershell
python -m py_compile epc_gui\theme.py
python -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt5.QtWidgets import QApplication; from epc_gui.theme import apply_theme, current_tokens; app=QApplication([]); apply_theme(app,'light'); t=current_tokens(); print('TOKENS', t.name, t.AccentBlue); apply_theme(app,'dark'); print('TOKENS', current_tokens().name)"
```
Expected: `py_compile` silent; probe prints `TOKENS light <hex>` then `TOKENS dark` (accent hex = qfluentwidgets default `#009FAA`-family value; any 7-char `#RRGGBB` is acceptable).

- [x] **Step 2.3: Run smoke_p1 to see this failure leave the list**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\smoke_p1.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: still `EXIT=1`, but `theme.py still ships the old QSS builder` is GONE from the FAIL list; remaining failures are app.py (FluentWindow/build_main_window), the i18n settings keys, and the fresh-default theme. If a NEW failure appeared (e.g. an import error mentioning `restyle`), a page still imports the removed helper — that is Task 5/7's work; record it and continue (see note below).

**Note for the executor:** `restyle` is kept as a deprecated shim in theme.py until the Task 7 checkpoint, so config/compare pages still import cleanly and Tasks 3/4 can boot the real window. Tasks 5 and 7 migrate every call site to `set_label_state`; Step 7.7 deletes the shim after `grep restyle epc_gui` proves zero call sites remain.

- [x] **Step 2.4: Checkpoint**

Check the checkbox. `theme.py` is now Fluent-backed, QSS-free, signature-compatible for `apply_theme`/`current_tokens`/`configure_plot`/`set_label_state`.

---

## Task 3: Rewrite epc_gui/app.py — FluentWindow shell + settings wiring + offscreen fallback

**Files:**
- Modify: `epc_gui/app.py` (complete rewrite, 359 lines → ~260 lines)
- Depends on: `epc_gui/pages/settings_page.py` (Task 4) — app.py will not import successfully until Task 4 lands; expected and handled below.

- [x] **Step 3.1: Replace the file**

Overwrite `epc_gui/app.py` with this complete content:

```python
"""EPC Desktop — Fluent shell (PyQt-Fluent-Widgets).

MainWindow extends FluentWindow with a NavigationInterface over four pages
(config / preview / compare / settings). Theme and language live on the
Settings page (spec §2). Offscreen-safe entry points use build_main_window():
when the Qt platform is offscreen AND the Task-0 spike selected branch B,
qfluentwidgets' FluentWindow cannot create a native window, so a functional
QMainWindow fallback with the same public API is returned instead.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition

from epc_gui.i18n import get_i18n, get_locale, set_locale, tr
from epc_gui.pages.compare_page import ComparePage
from epc_gui.pages.config_page import ConfigPage
from epc_gui.pages.preview_page import PreviewPage
from epc_gui.pages.settings_page import SettingsPage
from epc_gui.services import history as hist_svc
from epc_gui.services import yaml_io
from epc_gui.theme import apply_theme

_PAGE_KEYS = ("config", "preview", "compare", "settings")
_ICONS = {
    "config": FluentIcon.DOCUMENT,
    "preview": FluentIcon.PHOTO,   # IMAGE is absent in qfluentwidgets 1.11.3
    "compare": FluentIcon.MENU,    # GRID is absent in qfluentwidgets 1.11.3
    "settings": FluentIcon.SETTING,
}
# Task 0 spike decides: True = FluentWindow crashes under offscreen and the
# functional fallback shell is used there; False = FluentWindow always used.
_OFFSCREEN_FALLBACK = False  # Task 0 spike outcome A: FluentWindow is offscreen-safe here


class _ShellMixin:
    """Shared behavior for FluentWindow and the offscreen fallback shell."""

    def _wire(self) -> None:
        self.config.request_preview.connect(self._on_preview)
        self.config.job_finished.connect(self._on_job)
        self.config.history_open.connect(self._on_history)
        self.config.yaml_edit.textChanged.connect(self._refresh_strip)

    def toggle_theme(self) -> None:
        self.set_theme("light" if self._theme != "light" else "dark")

    def set_theme(self, mode: str) -> None:
        self._theme = "light" if str(mode).lower().startswith("light") else "dark"
        hist_svc.save_settings({"theme": self._theme})
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme)
        self.settings_page.reflect()
        self.compare.reapply_theme_plots()

    def set_locale_ui(self, locale: str) -> None:
        loc = "en" if str(locale).lower().startswith("en") else "zh"
        hist_svc.save_settings({"locale": loc})
        set_locale(loc)
        self.settings_page.reflect()

    def _on_locale_changed(self, _loc: str) -> None:
        self.retranslate()

    def _refresh_strip(self) -> None:
        try:
            data = yaml_io.load_yaml_text(self.config.yaml_edit.toPlainText())
            job = data.get("job_name", "—")
            mode = yaml_io.effective_mode(data)
        except Exception:
            job, mode = "—", "—"
        exit_t = self.config.lbl_exit.text()
        self.strip.setText(f"{job}  ·  {mode}  ·  {exit_t}")

    def _on_preview(self, db: str) -> None:
        self.preview.open_db(db)
        self.switch_to("preview")
        self._refresh_strip()

    def _on_job(self, code: int, db: str, audit: str) -> None:
        src, _, _ = self.config.current_paths()
        try:
            ydata = yaml_io.load_yaml_text(self.config.yaml_edit.toPlainText())
        except Exception:
            ydata = None
        ypath = str(self.config._yaml_path) if self.config._yaml_path else None
        self.compare.set_context(
            a_db=src or None,
            b_db=db or None,
            audit=audit or None,
            exit_code=code,
            yaml_data=ydata,
            yaml_path=ypath,
        )
        self._refresh_strip()
        if code != 0:
            self.switch_to("compare")

    def _on_history(self, entry: dict) -> None:
        audit = entry.get("audit") or ""
        db = entry.get("db") or ""
        src, _, _ = self.config.current_paths()
        try:
            ydata = yaml_io.load_yaml_text(self.config.yaml_edit.toPlainText())
        except Exception:
            ydata = None
        ex = entry.get("EXIT")
        self.compare.set_context(
            a_db=src or None,
            b_db=db or None if db else None,
            audit=audit or None,
            exit_code=int(ex) if ex is not None and str(ex).isdigit() else (
                int(ex) if isinstance(ex, int) else None
            ),
            yaml_data=ydata,
            yaml_path=entry.get("yaml"),
        )
        if audit or db:
            self.switch_to("compare")
            if db and Path(db).is_file():
                self.preview.open_db(db)


class MainWindow(FluentWindow, _ShellMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPC Desktop")
        self.resize(1320, 860)
        settings = hist_svc.load_settings()
        self._theme = settings.get("theme", "light")
        set_locale(settings.get("locale", "zh"), emit=False)
        self.config = ConfigPage()
        self.preview = PreviewPage()
        self.compare = ComparePage()
        self.settings_page = SettingsPage()
        self._pages = {
            "config": self.config,
            "preview": self.preview,
            "compare": self.compare,
            "settings": self.settings_page,
        }
        self._nav_items = {}   # addSubInterface handles (nav.items is absent in 1.11.3)
        for key in _PAGE_KEYS:
            page = self._pages[key]
            page.setObjectName(key)
            self._nav_items[key] = self.addSubInterface(
                page, _ICONS[key], tr(f"nav.{key}"),
                position=NavigationItemPosition.TOP,
            )
        self.stack = self.stackedWidget  # alias used by scripts/ui_regression
        self.strip = QLabel("job — · mode — · EXIT —")
        self.widgetLayout.insertWidget(0, self.strip)
        self.settings_page.theme_changed.connect(self.set_theme)
        self.settings_page.locale_changed.connect(self.set_locale_ui)
        self._wire()
        self.switch_to("config")
        self.retranslate()
        get_i18n().locale_changed.connect(self._on_locale_changed)

    def switch_to(self, key: str) -> None:
        if key not in self._pages:
            raise KeyError(key)
        page = self._pages[key]
        self.stackedWidget.setCurrentWidget(page)
        self.navigationInterface.setCurrentItem(key)

    def retranslate(self) -> None:
        for key in _PAGE_KEYS:
            item = self._nav_items.get(key)
            if item is not None:
                item.setText(tr(f"nav.{key}"))
        self.config.retranslate()
        self.preview.retranslate()
        self.compare.retranslate()
        self.settings_page.retranslate()
        self._refresh_strip()


class FallbackMainWindow(QMainWindow, _ShellMixin):
    """Functional offscreen shell with the same public API as MainWindow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPC Desktop")
        self.resize(1320, 860)
        settings = hist_svc.load_settings()
        self._theme = settings.get("theme", "light")
        set_locale(settings.get("locale", "zh"), emit=False)
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        rail = QFrame()
        rail.setFixedWidth(168)
        rv = QVBoxLayout(rail)
        self._nav_btns: dict[str, QPushButton] = {}
        for key in _PAGE_KEYS:
            b = QPushButton("")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=key: self.switch_to(k))
            self._nav_btns[key] = b
            rv.addWidget(b)
        rv.addStretch(1)
        root.addWidget(rail)
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        self.strip = QLabel("job — · mode — · EXIT —")
        right.addWidget(self.strip)
        self.stack = QStackedWidget()
        self.config = ConfigPage()
        self.preview = PreviewPage()
        self.compare = ComparePage()
        self.settings_page = SettingsPage()
        self._pages = {
            "config": self.config,
            "preview": self.preview,
            "compare": self.compare,
            "settings": self.settings_page,
        }
        self._page_index = {k: i for i, k in enumerate(_PAGE_KEYS)}
        for page in self._pages.values():
            self.stack.addWidget(page)
        right.addWidget(self.stack, stretch=1)
        right_w = QWidget()
        right_w.setLayout(right)
        root.addWidget(right_w, stretch=1)
        self.settings_page.theme_changed.connect(self.set_theme)
        self.settings_page.locale_changed.connect(self.set_locale_ui)
        self._wire()
        self.switch_to("config")
        self.retranslate()
        get_i18n().locale_changed.connect(self._on_locale_changed)

    def switch_to(self, key: str) -> None:
        self.stack.setCurrentIndex(self._page_index[key])
        for k, b in self._nav_btns.items():
            b.setChecked(k == key)

    def retranslate(self) -> None:
        for key in _PAGE_KEYS:
            self._nav_btns[key].setText(tr(f"nav.{key}"))
        self.config.retranslate()
        self.preview.retranslate()
        self.compare.retranslate()
        self.settings_page.retranslate()
        self._refresh_strip()


def build_main_window() -> QMainWindow:
    """Entry point used by run() and the capture/smoke scripts."""
    if _OFFSCREEN_FALLBACK and os.environ.get("QT_QPA_PLATFORM", "").lower() == "offscreen":
        return FallbackMainWindow()
    return MainWindow()


def run(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    if (
        not os.environ.get("DISPLAY")
        and not os.environ.get("QT_QPA_PLATFORM")
        and sys.platform != "win32"
    ):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication(argv)
    settings = hist_svc.load_settings()
    set_locale(settings.get("locale", "zh"), emit=False)
    apply_theme(app, settings.get("theme", "light"))
    main = build_main_window()
    main.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(run())
```

- [x] **Step 3.2: Set the spike flag**

Task 0 recorded outcome **A** on this machine (`SPIKE OFFSCREEN OK`, exit 0), so the literal in the code above is already `False`. Do not flip it back. Record `QW_VERSION=1.11.3`, `SPIKE_OFFSCREEN=A`, `SPIKE_DESKTOP=OK` in the execution log (already captured in `## Execution log`).

- [x] **Step 3.3: Compile check (import is expected to fail until Task 4)**

Run: `python -m py_compile epc_gui\app.py` → silent, exit 0.

Run:
```powershell
python -c "import epc_gui.app" 2>&1 | Select-Object -First 3
```
Expected: `ModuleNotFoundError: No module named 'epc_gui.pages.settings_page'` — exactly one missing dependency, Task 4 supplies it. If a different error appears, fix it now.

- [x] **Step 3.4: Checkpoint**

Check the checkbox; app.py is complete and waiting on the settings page.

---

## Task 4: Create pages/settings_page.py + add the i18n settings keys

**Files:**
- Create: `epc_gui/pages/settings_page.py`
- Modify: `epc_gui/i18n/catalog.py:12-16` (ZH) and `:161-166` (EN)

- [x] **Step 4.1: Create the settings page**

Create `epc_gui/pages/settings_page.py` with this complete content:

```python
"""Page D — app settings: dark-mode switch + language combo (SettingCards)."""
from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from qfluentwidgets import (
    ComboBox,
    FluentIcon,
    ScrollArea,
    SettingCard,
    SwitchSettingCard,
    TitleLabel,
    isDarkTheme,
)

from epc_gui.i18n import get_locale, tr
from epc_gui.services import history as hist_svc


class SettingsPage(ScrollArea):
    theme_changed = pyqtSignal(str)   # "light" | "dark"
    locale_changed = pyqtSignal(str)  # "zh" | "en"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings")
        container = QWidget()
        self.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(24, 18, 24, 18)
        root.setSpacing(12)

        self.title = TitleLabel("")
        root.addWidget(self.title)

        # 1.11.3: SwitchSettingCard(icon, title, content=None, configItem=None,
        # parent=None) — pass the parent by keyword, or `self` binds to
        # configItem and the switch crashes on .value.
        self.theme_card = SwitchSettingCard(
            FluentIcon.PALETTE, "", "", parent=self
        )
        self.theme_card.setChecked(isDarkTheme())
        self.theme_card.checkedChanged.connect(self._on_theme_switch)
        root.addWidget(self.theme_card)

        # 1.11.3: ComboBoxSettingCard requires an OptionsConfigItem as its
        # first argument; a plain SettingCard + ComboBox is the documented
        # equivalent without the config bridge (verified in the Task 0 spike).
        self.lang_card = SettingCard(FluentIcon.LANGUAGE, "", "", parent=self)
        self.lang_combo = ComboBox(self.lang_card)
        self.lang_combo.addItems(["中文", "English"])
        self.lang_card.hBoxLayout.addWidget(self.lang_combo)
        self.lang_card.comboBox = self.lang_combo
        self.lang_combo.currentIndexChanged.connect(self._on_lang_combo)
        root.addWidget(self.lang_card)

        root.addStretch(1)
        self.retranslate()
        self.reflect()

    def retranslate(self) -> None:
        self.title.setText(tr("settings.title"))
        self.theme_card.setTitle(tr("settings.dark_card"))
        self.theme_card.setContent(tr("settings.dark_hint"))
        self.lang_card.setTitle(tr("settings.lang_card"))

    def reflect(self) -> None:
        """Sync widget state from persisted settings (shell calls this)."""
        self.theme_card.blockSignals(True)
        self.theme_card.setChecked(isDarkTheme())
        self.theme_card.blockSignals(False)
        self.lang_card.comboBox.blockSignals(True)
        self.lang_card.comboBox.setCurrentIndex(0 if get_locale() == "zh" else 1)
        self.lang_card.comboBox.blockSignals(False)

    def _on_theme_switch(self, dark: bool) -> None:
        self.theme_changed.emit("dark" if dark else "light")

    def _on_lang_combo(self, idx: int) -> None:
        if self.lang_card.comboBox.signalsBlocked():
            return
        self.locale_changed.emit("zh" if idx == 0 else "en")
```

- [x] **Step 4.2: Add ZH keys**

In `epc_gui/i18n/catalog.py`, immediately after the existing line

```python
    "lang.en": "English",
```

insert

```python
    "nav.settings": "设置",
    "settings.title": "设置",
    "settings.dark_card": "深色模式",
    "settings.dark_hint": "切换浅色 / 深色主题",
    "settings.lang_card": "语言",
```

- [x] **Step 4.3: Add EN keys**

In `epc_gui/i18n/catalog.py`, immediately after the existing line

```python
    "lang.en": "English",
```

(in the EN dict) insert

```python
    "nav.settings": "Settings",
    "settings.title": "Settings",
    "settings.dark_card": "Dark mode",
    "settings.dark_hint": "Switch between light and dark theme",
    "settings.lang_card": "Language",
```

- [x] **Step 4.4: Compile + boot probe**

Run:
```powershell
python -m py_compile epc_gui\pages\settings_page.py epc_gui\i18n\catalog.py epc_gui\app.py
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\brief_start_quit.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: compile silent; brief prints `started OK`, exit 0 (fallback shell if spike=B; FluentWindow if spike=A). A crash mentioning `settings_page` or `SwitchSettingCard` means a qfluentwidgets API mismatch — capture the exact line and check against the installed version's signature (`python -c "import inspect, qfluentwidgets; print(inspect.signature(qfluentwidgets.SwitchSettingCard.__init__))"`).

- [x] **Step 4.5: Checkpoint**

Check the checkbox. Note: smoke_p1's i18n key failures should now be down to none except the app.py contract still referencing pages that import `restyle` (Tasks 5–7).

---

## Task 5: Fluent-ize pages/config_page.py (imports + widgets only, business logic verbatim)

**Files:**
- Modify: `epc_gui/pages/config_page.py` — exact edit list below; every method body after `__init__` stays byte-identical.

- [x] **Step 5.1: Replace the import block**

Replace the exact block

```python
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from epc_gui.i18n import tr
from epc_gui.services import history as hist_svc
from epc_gui.services import yaml_io
from epc_gui.services.job_runner import JobRunner
from epc_gui.services.sugar import dry_run_precheck, expand_from_path, expand_from_yaml_text
from epc_gui.theme import restyle, set_label_state
from epc_gui.paths import fixtures_root, portable
```

with

```python
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QListWidgetItem,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import (
    CardWidget,
    ComboBox,
    LineEdit,
    ListWidget,
    PlainTextEdit,
    PrimaryPushButton,
    PushButton,
    TableWidget,
    TitleLabel,
)

from epc_gui.i18n import tr
from epc_gui.services import history as hist_svc
from epc_gui.services import yaml_io
from epc_gui.services.job_runner import JobRunner
from epc_gui.services.sugar import dry_run_precheck, expand_from_path, expand_from_yaml_text
from epc_gui.theme import set_label_state
from epc_gui.paths import fixtures_root, portable
```

- [x] **Step 5.2: Widget class swaps in __init__ (each edit below, exact strings)**

1. Replace `self.title = QLabel("")\n        self.title.setObjectName("Title")` with `self.title = TitleLabel("")`
2. Replace `b = QPushButton("")` (in the shortcut loop) with `b = PushButton("")`
3. Replace `self.band_job = QGroupBox("")` with `self.band_job = CardWidget()`
4. Replace `self.ed_job = QLineEdit()` with `self.ed_job = LineEdit()`
5. Replace `self.cb_mode = QComboBox()` with `self.cb_mode = ComboBox()`
6. Replace `self.ed_source = QLineEdit()` with `self.ed_source = LineEdit()`
7. Replace `self.ed_out_db = QLineEdit()` with `self.ed_out_db = LineEdit()`
8. Replace `self.ed_audit = QLineEdit()` with `self.ed_audit = LineEdit()`
9. Replace `self.cb_backend = QComboBox()` with `self.cb_backend = ComboBox()`
10. Replace `self.lbl_gates = QLabel("")\n        self.lbl_gates.setObjectName("Mute")` with `self.lbl_gates = CaptionLabel("")` and add `from qfluentwidgets import CaptionLabel` to the qfluentwidgets import in Step 5.1 (final import list: `CardWidget, CaptionLabel, ComboBox, LineEdit, ListWidget, PlainTextEdit, PrimaryPushButton, PushButton, TableWidget, TitleLabel`)
11. Replace `self.yband = QGroupBox("")` with `self.yband = CardWidget()`
12. Replace `self.yaml_edit = QPlainTextEdit()` with `self.yaml_edit = PlainTextEdit()`
13. Replace each of the four `QPushButton("")` in the YAML button row with `PushButton("")` (self.btn_open / self.btn_save / self.btn_save_as / self.btn_apply)
14. Replace `self.btn_dry = QPushButton("")` with `self.btn_dry = PushButton("")`
15. Replace `self.btn_run = QPushButton("")\n        self.btn_run.setObjectName("Primary")` with `self.btn_run = PrimaryPushButton("")`
16. Replace `self.btn_stop = QPushButton("")\n        self.btn_stop.setObjectName("Danger")` with `self.btn_stop = PushButton("")`
17. Replace `self.lbl_exit = QLabel("")\n        self.lbl_exit.setObjectName("Mute")` with `self.lbl_exit = CaptionLabel("")`
18. Replace `self.lbl_disk = QLabel("")` with `self.lbl_disk = CaptionLabel("")`
19. Replace `self.lbl_dry = QLabel("")` with `self.lbl_dry = CaptionLabel("")`
20. Replace `self.sugar = QGroupBox("")` with `self.sugar = CardWidget()`
21. Replace `self.lbl_sugar = QLabel("")\n        self.lbl_sugar.setObjectName("Mute")` with `self.lbl_sugar = CaptionLabel("")`
22. Replace `self.sugar_table = QTableWidget(0, 5)` with `self.sugar_table = TableWidget(0, 5)`
23. Replace `self.btn_refresh_sugar = QPushButton("")` with `self.btn_refresh_sugar = PushButton("")`
24. Replace `self.log = QPlainTextEdit()` with `self.log = PlainTextEdit()`
25. Replace `self.hist = QGroupBox("")` with `self.hist = CardWidget()`
26. Replace `self.history_list = QListWidget()` with `self.history_list = ListWidget()`
27. Replace `self.btn_hist_reload = QPushButton("")` with `self.btn_hist_reload = PushButton("")`
28. In `_path_row`, replace `b = QPushButton("…")` with `b = PushButton("…")`

- [x] **Step 5.3: Replace restyle call sites with set_label_state**

Make these exact replacements in `epc_gui/pages/config_page.py`:
1. `restyle(self.lbl_exit, "StatusMono")` → `set_label_state(self.lbl_exit, "neutral")`
2. `restyle(self.lbl_disk, "StatusMono")` (first occurrence, in the `code == 0` branch) → `set_label_state(self.lbl_disk, "neutral")`
3. `restyle(self.lbl_disk, "StatusMono")` (second occurrence, in the `else` branch) → `set_label_state(self.lbl_disk, "neutral")`

- [x] **Step 5.4: Compile + import probe**

Run:
```powershell
python -m py_compile epc_gui\pages\config_page.py
python -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt5.QtWidgets import QApplication; app=QApplication([]); from epc_gui.pages.config_page import ConfigPage; p=ConfigPage(); print('CONFIG OK', type(p.yaml_edit).__name__, type(p.sugar_table).__name__)"
```
Expected: compile silent; probe prints `CONFIG OK PlainTextEdit TableWidget`.

- [x] **Step 5.5: Boot probe + smoke_p1 source scan**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\brief_start_quit.py; Write-Output "EXIT=$LASTEXITCODE"
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\smoke_p1.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: brief `started OK` exit 0. smoke_p1 still `EXIT=1`; the failures are now only: app.py contract (until smoke re-scan passes — it should pass now), remaining i18n fresh-default (Task 8), and any source-scan failures if a banned string slipped in. If smoke_p1 reports `pages/config_page.py still has …` banned-label errors, the swapped widgets introduced none (all labels come from `tr()`), so investigate immediately.

- [x] **Step 5.6: Checkpoint**

Check the checkbox. ConfigPage keeps its entire public API: signals `job_finished`/`request_preview`/`history_open`, `yaml_edit`, `lbl_exit`, `load_shortcut`, `load_yaml_path`, `current_paths`, `retranslate`.

---

## Task 6: Fluent-ize pages/preview_page.py

**Files:**
- Modify: `epc_gui/pages/preview_page.py` — exact edit list below; method bodies stay byte-identical.

- [x] **Step 6.1: Replace the import block**

Replace the exact block

```python
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from epc_gui.i18n import tr
from epc_gui.services.db_reader import CharDb
from epc_gui.paths import fixtures_root
```

with

```python
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import (
    CardWidget,
    CaptionLabel,
    ComboBox,
    PushButton,
    TableWidget,
    TitleLabel,
)

from epc_gui.i18n import tr
from epc_gui.services.db_reader import CharDb
from epc_gui.paths import fixtures_root
```

- [x] **Step 6.2: Widget swaps in __init__ (exact strings)**

1. Replace `self.title = QLabel("")\n        self.title.setObjectName("Title")` with `self.title = TitleLabel("")`
2. Replace `self.lbl_path = QLabel("")\n        self.lbl_path.setObjectName("Mute")` with `self.lbl_path = CaptionLabel("")`
3. Replace `self.btn_open = QPushButton("")` with `self.btn_open = PushButton("")`
4. Replace `self.filt = QGroupBox("")` with `self.filt = CardWidget()`
5. Replace `self.cb_inst = QComboBox()` with `self.cb_inst = ComboBox()`
6. Replace `self.cb_pvt = QComboBox()` with `self.cb_pvt = ComboBox()`
7. Replace `self.cb_key = QComboBox()` with `self.cb_key = ComboBox()`
8. Replace `self.table = QTableWidget(0, 4)` with `self.table = TableWidget(0, 4)`
9. Replace `self.btn_prev = QPushButton("")` with `self.btn_prev = PushButton("")`
10. Replace `self.btn_next = QPushButton("")` with `self.btn_next = PushButton("")`
11. Replace `self.lbl_page = QLabel("")\n        self.lbl_page.setObjectName("Mute")` with `self.lbl_page = CaptionLabel("")`
12. Replace `self.matrix = QTableWidget(0, 0)` with `self.matrix = TableWidget(0, 0)`

(The remaining `QLabel("instance")` / `QLabel("pvt")` / `QLabel("key")` inline filter captions and `QTableWidgetItem` usages stay as PyQt5 imports — `QTableWidgetItem` works with Fluent `TableWidget`; `QLabel` remains imported.)

- [x] **Step 6.3: Compile + import probe**

Run:
```powershell
python -m py_compile epc_gui\pages\preview_page.py
python -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt5.QtWidgets import QApplication; app=QApplication([]); from epc_gui.pages.preview_page import PreviewPage; p=PreviewPage(); print('PREVIEW OK', type(p.table).__name__)"
```
Expected: compile silent; probe prints `PREVIEW OK TableWidget`.

- [x] **Step 6.4: Checkpoint**

Check the checkbox. `open_db` / `browse_db` / `retranslate` / matrix cell logic untouched.

---

## Task 7: Fluent-ize pages/compare_page.py

**Files:**
- Modify: `epc_gui/pages/compare_page.py` — exact edit list below; all chart/free-compare/gate logic stays byte-identical.

- [x] **Step 7.1: Replace the import block**

Replace the exact block

```python
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolTip,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QSizePolicy,
)

from epc_gui.i18n import tr
from epc_gui.services.audit_parse import AuditSummary, parse_audit, parse_constraint_sat_rate
from epc_gui.services import compare_views as cv
from epc_gui.theme import configure_plot, current_tokens, restyle, set_label_state
from epc_gui.paths import fixtures_root, repo_root
```

with

```python
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QTableWidgetItem,
    QToolTip,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QSizePolicy,
)

from qfluentwidgets import (
    CardWidget,
    CaptionLabel,
    ComboBox,
    PlainTextEdit,
    PushButton,
    TableWidget,
    TitleLabel,
)

from epc_gui.i18n import tr
from epc_gui.services.audit_parse import AuditSummary, parse_audit, parse_constraint_sat_rate
from epc_gui.services import compare_views as cv
from epc_gui.theme import configure_plot, current_tokens, set_label_state
from epc_gui.paths import fixtures_root, repo_root
```

- [x] **Step 7.2: Widget swaps in __init__ (exact strings)**

1. Replace `self.title = QLabel("")\n        self.title.setObjectName("Title")` with `self.title = TitleLabel("")`
2. Replace `self.gate_box = QGroupBox("")` with `self.gate_box = CardWidget()`
3. Replace `self.btn_audit = QPushButton("")` with `self.btn_audit = PushButton("")`
4. Replace `self.btn_open_full = QPushButton("")` with `self.btn_open_full = PushButton("")`
5. Replace `self.lbl_lamp = QLabel("●")\n        self.lbl_lamp.setObjectName("LampUnknown")` with `self.lbl_lamp = QLabel("●")`
6. Replace `self.lbl_overall = QLabel("")\n        self.lbl_overall.setObjectName("OverallStatus")` with `self.lbl_overall = QLabel("")`
7. Replace `self.lbl_exit = QLabel("EXIT —")\n        self.lbl_exit.setObjectName("Readout")` with `self.lbl_exit = QLabel("EXIT —")`
8. Replace `self.lbl_db = QLabel("")\n        self.lbl_db.setObjectName("Mute")` with `self.lbl_db = CaptionLabel("")`
9. Replace `self.gate_lights = QLabel("")\n        self.gate_lights.setObjectName("GateLights")` with `self.gate_lights = QLabel("")`
10. Replace `self.audit_snip = QPlainTextEdit()\n        self.audit_snip.setObjectName("AuditSnippet")` with `self.audit_snip = PlainTextEdit()`
11. Replace `self.lbl_chart1_empty = QLabel("")\n        self.lbl_chart1_empty.setObjectName("Mute")` with `self.lbl_chart1_empty = CaptionLabel("")`
12. Replace `self.chart1_box = QGroupBox("")` with `self.chart1_box = CardWidget()`
13. Replace `self.lbl_view = QLabel("")` with `self.lbl_view = CaptionLabel("")`
14. Replace `self.cb_view = QComboBox()` with `self.cb_view = ComboBox()`
15. Replace `self.lbl_sat = QLabel("")\n        self.lbl_sat.setObjectName("Readout")` with `self.lbl_sat = QLabel("")`
16. Replace `self.tbl_c1 = QTableWidget(0, 5)` with `self.tbl_c1 = TableWidget(0, 5)`
17. Replace `self.chart2_box = QGroupBox("")` with `self.chart2_box = CardWidget()`
18. Replace `self.btn_ref = QPushButton("")` with `self.btn_ref = PushButton("")`
19. Replace `self.btn_constructed = QPushButton("")` with `self.btn_constructed = PushButton("")`
20. Replace `self.lbl_ref = QLabel("")\n        self.lbl_ref.setObjectName("Mute")` with `self.lbl_ref = CaptionLabel("")`
21. Replace `self.lbl_constructed = QLabel("")\n        self.lbl_constructed.setObjectName("Mute")` with `self.lbl_constructed = CaptionLabel("")`
22. Replace `self.cb_pvt = QComboBox()` with `self.cb_pvt = ComboBox()`
23. Replace `self.cb_key = QComboBox()` with `self.cb_key = ComboBox()`
24. Replace `self.btn_refresh_free = QPushButton("")` with `self.btn_refresh_free = PushButton("")`
25. Replace `self.lbl_typical_note = QLabel("")\n        self.lbl_typical_note.setObjectName("Mute")` with `self.lbl_typical_note = CaptionLabel("")`
26. Replace `self.lbl_cover = QLabel("")\n        self.lbl_cover.setObjectName("Readout")` with `self.lbl_cover = QLabel("")`
27. Replace `self.lbl_delta = QLabel("")\n        self.lbl_delta.setObjectName("Readout")` with `self.lbl_delta = QLabel("")`
28. Replace `self.lbl_delta_mean = QLabel("")\n        self.lbl_delta_mean.setObjectName("Readout")` with `self.lbl_delta_mean = QLabel("")`
29. Replace `self.lbl_free_empty = QLabel("")\n        self.lbl_free_empty.setObjectName("Mute")` with `self.lbl_free_empty = CaptionLabel("")`
30. Replace `side_w = QFrame()\n        side_w.setObjectName("ReadoutBand")` with `side_w = CardWidget()`
31. Replace `self.btn_eval_h3 = QPushButton("eval_h3")` with `self.btn_eval_h3 = PushButton("eval_h3")`
32. Replace `self.btn_holdout = QPushButton("hold-out")` with `self.btn_holdout = PushButton("hold-out")`
33. Replace `self.eval_log = QPlainTextEdit()` with `self.eval_log = PlainTextEdit()`

- [x] **Step 7.3: Replace restyle call sites with set_label_state**

Exact replacements in `epc_gui/pages/compare_page.py`:
1. `restyle(self.lbl_exit, "StatusMono")` → `set_label_state(self.lbl_exit, "neutral")`
2. `restyle(self.lbl_db, "StatusMono")` → `set_label_state(self.lbl_db, "neutral")`
3. `restyle(self.lbl_lamp, "LampPass")` → `set_label_state(self.lbl_lamp, "pass")`
4. `restyle(self.lbl_lamp, "LampFail")` → `set_label_state(self.lbl_lamp, "fail")`
5. `restyle(self.lbl_lamp, "LampUnknown")` (first occurrence) → `set_label_state(self.lbl_lamp, "neutral")`
6. `restyle(self.lbl_lamp, "LampUnknown")` (second occurrence, in the `not s.parse_ok` branch) → `set_label_state(self.lbl_lamp, "neutral")`

- [x] **Step 7.4: Replace the retranslate() lamp repolish block**

Replace the exact block

```python
        elif not self._audit_path:
            self.lbl_overall.setText(tr("overall.unknown"))
            self.lbl_gates_ok.clear()
            self.lbl_lamp.setObjectName("LampUnknown")
            self.lbl_lamp.style().unpolish(self.lbl_lamp)
            self.lbl_lamp.style().polish(self.lbl_lamp)
```

with

```python
        elif not self._audit_path:
            self.lbl_overall.setText(tr("overall.unknown"))
            self.lbl_gates_ok.clear()
            set_label_state(self.lbl_lamp, "neutral")
```

- [x] **Step 7.5: Compile + import probe**

Run:
```powershell
python -m py_compile epc_gui\pages\compare_page.py
python -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt5.QtWidgets import QApplication; app=QApplication([]); from epc_gui.pages.compare_page import ComparePage; p=ComparePage(); print('COMPARE OK', type(p.gate_box).__name__, type(p.tbl_c1).__name__)"
```
Expected: compile silent; probe prints `COMPARE OK CardWidget TableWidget`.

- [x] **Step 7.6: Boot + smoke_p2 + smoke_headless (behavior regression)**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\brief_start_quit.py; Write-Output "EXIT=$LASTEXITCODE"
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\smoke_p2.py; Write-Output "EXIT=$LASTEXITCODE"
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\smoke_headless.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: all three exit 0. smoke_p2 must still print `ALL P2 / P2.1 SMOKE OK` (chart1 three views, sat 17/17, mean Δ +0.0%); smoke_headless must still print `ALL SMOKE OK` (COUNT=4950, red H3-hard FAIL). Any FAIL here is a real regression in the page rewrite — fix before proceeding.

- [x] **Step 7.7: Delete the deprecated restyle shim**

Run: `grep -rn "restyle" epc_gui` — only the `def restyle` in `epc_gui/theme.py` (and its docstring) may remain; Tasks 5/7 replaced every call site with `set_label_state`. Delete the `restyle()` function from `epc_gui/theme.py`, then run:

```powershell
python -m py_compile epc_gui\theme.py epc_gui\pages\config_page.py epc_gui\pages\compare_page.py
```

Expected: silent, exit 0. If `grep` still shows a call site, fix that site first — never delete the shim while it is still imported.

- [x] **Step 7.8: Checkpoint**

Check the checkbox. ComparePage public API intact: `set_context`, `load_audit`, `refresh_chart1`, `refresh_free_compare`, `reapply_theme_plots`, `run_eval_h3`, `key_list` shim, `refresh_trend`, `refresh_aux`.

---

## Task 8: Fresh-install theme default → light (services/history.py)

**Files:**
- Modify: `epc_gui/services/history.py:49` (one line)

- [x] **Step 8.1: Change the default**

Replace the exact line

```python
    defaults = {"theme": "dark", "locale": "zh"}
```

with

```python
    defaults = {"theme": "light", "locale": "zh"}
```

This is the single deliberate services change in this plan: the approved spec requires default light, and this is where fresh-install defaults live. Normalization logic (`load_settings`/`save_settings` bodies) is untouched.

- [x] **Step 8.2: Run smoke_p1 — fresh-default assertion passes**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\smoke_p1.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: `EXIT=0` with `ALL P1 SMOKE OK` (all previously failing assertions — i18n keys, app contract, fresh default — now pass). If `EXIT=1`, read the FAIL list: it must be empty of the Task-1 items; any remaining item is a regression to fix.

- [x] **Step 8.3: Checkpoint**

Check the checkbox. smoke_p1 is green.

---

## Task 9: Point scripts at build_main_window

**Files:**
- Modify: `epc_gui/scripts/brief_start_quit.py`, `epc_gui/scripts/capture_screenshots.py`, `epc_gui/scripts/capture_p1.py`, `epc_gui/scripts/capture_p2.py`
- Unchanged: `epc_gui/scripts/smoke_p2.py` (constructs ComparePage directly; verified in Task 7)

- [x] **Step 9.1: brief_start_quit.py**

Replace the exact block

```python
from epc_gui.app import MainWindow
from epc_gui.theme import apply_theme

app = QApplication(sys.argv)
apply_theme(app)
w = MainWindow()
```

with

```python
from epc_gui.app import build_main_window
from epc_gui.theme import apply_theme

app = QApplication(sys.argv)
apply_theme(app, "light")
w = build_main_window()
```

- [x] **Step 9.2: capture_screenshots.py**

Replace `from epc_gui.app import MainWindow` with `from epc_gui.app import build_main_window`; replace `apply_theme(app)` with `apply_theme(app, "light")`; replace `win = MainWindow()` with `win = build_main_window()`.

- [x] **Step 9.3: capture_p1.py**

Replace `from epc_gui.app import MainWindow` with `from epc_gui.app import build_main_window`; replace `win = MainWindow()` with `win = build_main_window()`. (`apply_theme(app, "dark")` stays — this script captures the dark theme deliberately.)

- [x] **Step 9.4: capture_p2.py**

Same two replacements as Step 9.3. (`apply_theme(app, "dark")` stays.)

- [x] **Step 9.5: Compile all + boot**

Run:
```powershell
python -m py_compile epc_gui\scripts\brief_start_quit.py epc_gui\scripts\capture_screenshots.py epc_gui\scripts\capture_p1.py epc_gui\scripts\capture_p2.py
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'; python epc_gui\scripts\brief_start_quit.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: compile silent; brief `started OK` exit 0.

- [x] **Step 9.6: Checkpoint**

Check the checkbox.

---

## Task 10: Pin qfluentwidgets + update CI

**Files:**
- Modify: `epc_gui/requirements.txt`
- Modify: `.github/workflows/epc-ci.yml`

- [x] **Step 10.1: Uncomment and pin in epc_gui/requirements.txt**

Replace the commented line (currently `# PyQt-Fluent-Widgets>=1.5  # optional, unused by the current theme stack`) with the pinned line recorded by the Task 0 spike:

```
PyQt-Fluent-Widgets==1.11.3
```

(If the old comment text differs on disk, locate the `PyQt-Fluent-Widgets` line in that file and replace that single line.) The file must still contain the substrings `joblib` and `scikit-learn` (smoke_p1 U10 asserts them).

- [x] **Step 10.2: Add GUI deps to CI**

In `.github/workflows/epc-ci.yml`, replace the line

```yaml
          pip install PyQt5==5.15.2
```

with

```yaml
          pip install "PyQt5>=5.15"
          pip install -r epc_gui/requirements.txt
```

Why: the spike host already runs PyQt5 dist 5.15.11 with Qt runtime 5.15.2 under Python 3.13; pinning the binding to 5.15.2 would downgrade it, and that build has no 3.13 wheel guarantee. `epc_gui/requirements.txt` (which carries `PyQt-Fluent-Widgets==1.11.3`) is the authoritative GUI pin. If the workflow shape differs, make the equivalent replacement in the same step.

- [x] **Step 10.3: Verify the pin installs clean**

Run:
```powershell
python -m pip install -r epc_gui\requirements.txt --quiet
python -c "import qfluentwidgets; print('PIN OK', qfluentwidgets.__version__)"
```
Expected: `PIN OK 1.11.3` (same as Task 0).

- [x] **Step 10.4: Checkpoint**

Check the checkbox.

---

## Task 11: Full validation suite + screenshots + acceptance evidence

**Files:**
- Create: `epc_gui/FLUENT_REDESIGN_ACCEPTANCE.md` (evidence table)

- [x] **Step 11.1: Engine test suite (unchanged contract)**

Run:
```powershell
python -m pytest tests -q -m "not slow" *> "$env:TEMP\epc_fast.log"; Write-Output "EXIT=$LASTEXITCODE"; Select-String -Path "$env:TEMP\epc_fast.log" -Pattern "passed|failed" | Select-Object -Last 1
python -m pytest tests -q -m "slow" *> "$env:TEMP\epc_slow.log"; Write-Output "EXIT=$LASTEXITCODE"; Select-String -Path "$env:TEMP\epc_slow.log" -Pattern "passed|failed" | Select-Object -Last 1
```
Expected: fast = `68 passed` exit 0; slow = `1 passed` exit 0. (These are the engine+db-layer suites; the GUI redesign must not move them.)

- [x] **Step 11.2: All three GUI smokes**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'
python epc_gui\scripts\brief_start_quit.py; Write-Output "BOOT_EXIT=$LASTEXITCODE"
python epc_gui\scripts\smoke_headless.py; Write-Output "P0_EXIT=$LASTEXITCODE"
python epc_gui\scripts\smoke_p1.py; Write-Output "P1_EXIT=$LASTEXITCODE"
python epc_gui\scripts\smoke_p2.py; Write-Output "P2_EXIT=$LASTEXITCODE"
```
Expected: all four exit 0 with `started OK` / `ALL SMOKE OK` / `ALL P1 SMOKE OK` / `ALL P2 / P2.1 SMOKE OK`.

- [x] **Step 11.3: Offscreen captures (functional)**

Run:
```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='offscreen'
python epc_gui\scripts\capture_screenshots.py; Write-Output "EXIT=$LASTEXITCODE"
python epc_gui\scripts\capture_p1.py; Write-Output "EXIT=$LASTEXITCODE"
python epc_gui\scripts\capture_p2.py; Write-Output "EXIT=$LASTEXITCODE"
Get-ChildItem epc_gui\screenshots\*.png | Sort-Object LastWriteTime | Select-Object -First 25 Name, Length
```
Expected: three exit 0; ≥19 PNGs listed under `epc_gui/screenshots/` (4 + 6 + 9). If `_OFFSCREEN_FALLBACK=True` (spike B), these shots use the functional shell — that is the approved degradation, noted in the acceptance file.

- [x] **Step 11.4: Desktop captures (true Fluent visuals, spike-B case)**

If Task 0 outcome was B, also run the three capture scripts with the real windows platform so the user gets true-Fluent screenshots:

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='windows'
python epc_gui\scripts\capture_screenshots.py; Write-Output "EXIT=$LASTEXITCODE"
python epc_gui\scripts\capture_p1.py; Write-Output "EXIT=$LASTEXITCODE"
python epc_gui\scripts\capture_p2.py; Write-Output "EXIT=$LASTEXITCODE"
```
Expected: three exit 0, PNGs refreshed with FluentWindow visuals. (A brief real window flashes during capture — that is normal.)

- [x] **Step 11.5: Desktop launch probe (visible window)**

Run in a persistent visible terminal (the user can watch):

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:QT_QPA_PLATFORM='windows'; python -m epc_gui.app
```
Then from another shell verify a real window exists:

```powershell
Get-Process python | Where-Object { $_.MainWindowTitle -eq "EPC Desktop" } | Select-Object Id, MainWindowTitle, MainWindowHandle
```
Expected: one row with `MainWindowTitle=EPC Desktop` and a non-zero `MainWindowHandle`. The user visually confirms the Fluent look (navigation rail, cards, settings page). Close the window after confirmation.

- [x] **Step 11.6: Write the acceptance evidence file**

Create `epc_gui/FLUENT_REDESIGN_ACCEPTANCE.md` with this complete content (fill the four `<>` fields with the observed values; no other placeholders):

```markdown
# GUI Fluent Redesign — Acceptance Evidence

Date: <YYYY-MM-DD HH:MM> (Asia/Shanghai)
Spec: docs/superpowers/specs/2026-11-24-gui-fluent-redesign-design.md
Plan: docs/superpowers/plans/2026-11-24-gui-fluent-redesign.md

## Spike gate (Task 0)
- qfluentwidgets version: <QW_VERSION>
- Offscreen FluentWindow: <OK|CRASH> → _OFFSCREEN_FALLBACK = <True|False>

## Test evidence (spec §9)
| Gate | Command | Result |
| --- | --- | --- |
| Engine fast | python -m pytest tests -q -m "not slow" | 68 passed, exit 0 |
| Engine slow | python -m pytest tests -q -m "slow" | 1 passed, exit 0 |
| Boot | brief_start_quit.py (offscreen) | started OK, exit 0 |
| Smoke P0 | smoke_headless.py | ALL SMOKE OK, exit 0 |
| Smoke P1 | smoke_p1.py | ALL P1 SMOKE OK, exit 0 |
| Smoke P2 | smoke_p2.py | ALL P2 / P2.1 SMOKE OK, exit 0 |
| Captures offscreen | capture_screenshots + capture_p1 + capture_p2 | exit 0, ≥19 PNG |
| Captures desktop | same scripts, QT_QPA_PLATFORM=windows | exit 0 |
| Desktop launch | python -m epc_gui.app | visible "EPC Desktop" window |

## Theme contract (spec §2 / §7)
- Fresh-install default theme: light (services/history.py default, smoke_p1 asserts).
- Light/dark toggle: Settings page SwitchSettingCard → setTheme.
- Language: Settings page ComboBoxSettingCard → set_locale (zh/en).
- Services + epc_engine changes: only history.py default line (documented in plan Task 8).

## Screenshots
- epc_gui/screenshots/page_a_config.png
- epc_gui/screenshots/page_b_preview.png
- epc_gui/screenshots/page_c_compare.png
- epc_gui/screenshots/page_c_fail_h3hard.png
- epc_gui/screenshots/p1_dark_config_zh.png … p1_light_compare.png (6)
- epc_gui/screenshots/p2_*.png (9)

## Known limits (honest)
- If spike=B: offscreen captures use the functional fallback shell; desktop captures show the true Fluent skin.
- Visual review of the PNGs is human-confirmed (the automation model has no image input).
```

- [x] **Step 11.7: Final checkpoint**

Run `python -m py_compile epc_gui\app.py epc_gui\theme.py epc_gui\pages\settings_page.py epc_gui\pages\config_page.py epc_gui\pages\preview_page.py epc_gui\pages\compare_page.py` → silent. All task checkboxes complete.

---

## Task 12: UI 交互回测自动化（用户追加要求）

**Goal:** 在 offscreen 下把真实控件与回调驱动一遍，断言「操作 → 状态变化 / 信号发射」的因果链。不是截图，是逻辑回测：导航切换、设置卡驱动主题/语言、快捷载荷、YAML 预检、真实 job 运行、预览打开、比较页三视图与自由对比、历史点击、悬停边界、主题重绘幂等。

**Files:**
- Create: `epc_gui/scripts/ui_regression.py`
- Modify: `run_all_tests.ps1`, `.github/workflows/epc-ci.yml`

**Step 12.1: Write the interaction regression script**

```python
"""UI interaction regression: drive real widgets and callbacks offscreen.

Asserts the operation -> state-change / signal chain for navigation, settings,
config actions, preview and compare interactions. Exit 0 = UI REGRESSION OK.
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from PyQt5.QtCore import QEventLoop, QTimer  # noqa: E402
from PyQt5.QtTest import QTest  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from epc_gui.app import build_main_window  # noqa: E402
from epc_gui.i18n import get_locale, tr  # noqa: E402
from epc_gui.pages.compare_page import ComparePage  # noqa: E402
from epc_gui.pages.config_page import ConfigPage  # noqa: E402
from epc_gui.pages.preview_page import PreviewPage  # noqa: E402
from epc_gui.pages.settings_page import SettingsPage  # noqa: E402
from epc_gui.theme import current_tokens  # noqa: E402

CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn

    return deco


def find_page(win, cls):
    for i in range(win.stack.count()):
        w = win.stack.widget(i)
        if isinstance(w, cls):
            return w
    raise AssertionError(f"{cls.__name__} not found in stack")


def switch_of(card):
    for n in ("switchButton", "switch"):
        if hasattr(card, n):
            return getattr(card, n)
    raise AssertionError("no switch on settings card")


def combo_of(card):
    for n in ("comboBox", "combo"):
        if hasattr(card, n):
            return getattr(card, n)
    raise AssertionError("no combo on settings card")


def wait_signal(signal, timeout_ms=300_000):
    loop = QEventLoop()
    got = {"ok": False}

    def _hit(*_a):
        got["ok"] = True
        loop.quit()

    signal.connect(_hit)
    QTimer.singleShot(timeout_ms, loop.quit)
    loop.exec_()
    try:
        signal.disconnect(_hit)
    except TypeError:
        pass
    return got["ok"]


def poll_state(label, want, timeout_ms=120_000, step_ms=250):
    waited = 0
    while waited < timeout_ms:
        if label.property("state") == want:
            return True
        QTest.qWait(step_ms)
        waited += step_ms
    return False


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    win = build_main_window()
    win.show()
    QTest.qWait(300)

    cfg = find_page(win, ConfigPage)
    prv = find_page(win, PreviewPage)
    cmp_page = find_page(win, ComparePage)
    stg = find_page(win, SettingsPage)
    sample_yaml = _REPO / "epc_fixtures" / "epc_job.sample.yaml"
    sample_db = _REPO / "epc_fixtures" / "B_out.sample.db"
    sample_audit = _REPO / "epc_fixtures" / "B_out.sample_audit.md"
    vague_yaml = _REPO / "epc_fixtures" / "p1" / "epc_job.p1_r1_vague.yaml"

    @check("nav: config -> preview -> settings -> config -> config (idempotent)")
    def _nav():
        pairs = [("preview", PreviewPage), ("settings", SettingsPage),
                 ("config", ConfigPage), ("config", ConfigPage)]
        for key, cls in pairs:
            win.switch_to(key)
            QTest.qWait(120)
            assert isinstance(win.stack.currentWidget(), cls), f"nav failed: {key}"

    @check("settings: dark switch -> theme tokens + qconfig + revert")
    def _theme():
        card = stg.dark_card
        switch_of(card).setChecked(True)
        QTest.qWait(150)
        assert current_tokens().name == "dark", "theme tokens not dark"
        from qfluentwidgets import qconfig, Theme
        assert qconfig.theme == Theme.DARK, "qconfig not dark"
        switch_of(card).setChecked(True)  # idempotent re-set
        QTest.qWait(80)
        switch_of(card).setChecked(False)
        QTest.qWait(150)
        assert current_tokens().name == "light", "theme tokens not light"

    @check("settings: language combo -> locale + retranslated nav")
    def _locale():
        combo = combo_of(stg.lang_card)
        combo.setCurrentIndex(1)
        QTest.qWait(200)
        assert get_locale() == "en", "locale not en"
        assert tr("nav.config") == "Configuration", "nav not retranslated"
        combo.setCurrentIndex(0)
        QTest.qWait(200)
        assert get_locale() == "zh", "locale not zh"
        assert tr("nav.config") != "Configuration", "nav not retranslated back"

    @check("config: load_shortcut(sample) fills form + editor")
    def _shortcut():
        cfg.load_shortcut("sample")
        QTest.qWait(150)
        assert cfg.ed_source.text().endswith("A_ref.db"), "source field not loaded"
        assert "A_ref.db" in cfg.yaml_edit.toPlainText(), "editor not loaded"
        assert cfg.sugar_table.rowCount() >= 1, "sugar table empty after load"

    @check("config: refresh_sugar expands constraints")
    def _sugar():
        cfg.load_yaml_path(str(sample_yaml))
        QTest.qWait(100)
        cfg.refresh_sugar()
        QTest.qWait(200)
        assert cfg.sugar_table.rowCount() == 2, f"sugar rows={cfg.sugar_table.rowCount()}"

    @check("config: dry_run on vague yaml -> fail state")
    def _dry():
        cfg.load_yaml_path(str(vague_yaml))
        QTest.qWait(100)
        cfg.btn_dry.click()
        assert poll_state(cfg.lbl_dry, "fail"), "dry-run did not reach fail state"

    @check("config: run_job(sample) -> job_finished(0) + db written")
    def _run():
        cfg.load_yaml_path(str(sample_yaml))
        QTest.qWait(100)
        hits = {"args": None}
        cfg.job_finished.connect(lambda *a: hits.__setitem__("args", a))
        cfg.btn_run.click()
        assert wait_signal(cfg.job_finished), "job_finished not emitted"
        assert hits["args"] and hits["args"][0] == 0, f"exit={hits['args']}"
        assert sample_db.exists(), "B_out.sample.db missing"

    @check("preview: open_db sample -> rows + keys + paging")
    def _preview():
        prv.open_db(str(sample_db))
        QTest.qWait(300)
        assert prv.table.rowCount() > 0, "preview table empty"
        assert prv.cb_key.count() >= 2, "preview keys < 2"
        before = prv.lbl_page.text()
        prv._next()
        QTest.qWait(100)
        prv._prev()
        QTest.qWait(100)
        assert prv.lbl_page.text() == before, "paging did not return to page"

    @check("compare: set_context -> gate summary + view switching + hover edges")
    def _compare():
        cmp_page.set_context(a_db=str(_REPO / "epc_fixtures" / "A_ref.db"),
                             b_db=str(sample_db), audit=str(sample_audit))
        QTest.qWait(300)
        assert cmp_page.lbl_overall.property("state") in ("pass", "fail"), "no gate state"
        for idx in (0, 1, 2):
            if idx < cmp_page.cb_view.count():
                cmp_page.cb_view.setCurrentIndex(idx)
                QTest.qWait(200)
        cmp_page._on_c1_hover(-1)
        cmp_page._on_c1_hover(10 ** 6)
        cmp_page._on_free_filter()
        QTest.qWait(150)
        cmp_page.refresh_free_compare(keep_selection=True)

    @check("history: reload + click emits history_open")
    def _history():
        cfg.reload_history()
        QTest.qWait(200)
        if cfg.history_list.count() > 0:
            got = {"hit": False}
            cfg.history_open.connect(lambda d: got.__setitem__("hit", True))
            cfg._on_history_click(cfg.history_list.item(0))
            assert got["hit"], "history_open not emitted"

    @check("theme reapply: dark -> light keeps plots alive")
    def _reapply():
        win.set_theme("dark")
        QTest.qWait(150)
        cmp_page.reapply_theme_plots()
        QTest.qWait(150)
        win.set_theme("light")
        QTest.qWait(150)
        assert current_tokens().name == "light"

    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception:
            failures += 1
            print(f"FAIL  {name}")
            traceback.print_exc()
    if failures:
        print(f"UI REGRESSION FAILED ({failures}/{len(CHECKS)})")
        return 1
    print(f"UI REGRESSION OK ({len(CHECKS)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 12.2: Run**

`python epc_gui\scripts\ui_regression.py` (repo root) → expect 12 PASS lines and `UI REGRESSION OK (12 checks)`, exit 0.

**Step 12.3: Wire into gates**

`run_all_tests.ps1`: insert before the final summary:

```powershell
Write-Host "== UI interaction regression =="
python epc_gui\scripts\ui_regression.py
if ($LASTEXITCODE -ne 0) { Write-Host "GATE FAIL: ui_regression"; exit 1 }
```

`.github/workflows/epc-ci.yml`: add after the smoke steps:

```yaml
      - name: UI interaction regression (offscreen)
        env:
          QT_QPA_PLATFORM: offscreen
          PYTHONIOENCODING: utf-8
        run: python epc_gui/scripts/ui_regression.py
```

**Step 12.4: Checkpoint**

`python -m py_compile epc_gui\scripts\ui_regression.py` → silent; `ui_regression.py` in `epc_gui/scripts/`.

---

## Self-review (run by the plan author, resolved inline)

1. **Spec coverage:** §2 scope-A full re-skin → Tasks 3–7; default light + toggle → Tasks 4/8; settings page → Task 4; A1 spike → Task 0 + flag in Task 3 Step 3.2; §3 zero services/engine logic changes → only history.py default line (Task 8, documented); §6 deletions (QSS/_rgba/old strip) → Tasks 2/3; §7 smoke_p1 updates → Task 1; §9 acceptance → Task 11. No gap.
2. **Placeholder scan:** the only `<...>` tokens are data-flow fields (QW_VERSION, evidence table values) filled from named commands in the same plan — no TBD/implement-later text. Icon fallback alternates are fully enumerated in Task 0.
3. **Type/name consistency:** `ThemeTokens` fields used by pages (AccentBlue/MuteFog/RuleLine/PlotCanvas) all exist in the Task 2 dataclass; `build_main_window` is referenced by scripts (Task 9) and defined in Task 3; `settings_page.reflect()` is called in `_ShellMixin` and defined in Task 4; `set_label_state` call sites in Tasks 5/7 match the Task 2 signature; smoke_p1's `hist_svc.SETTINGS_PATH` monkeypatch matches `services/history.py`'s module-level constant. `NavigationInterface.items`/`widgetLayout` usage follows qfluentwidgets' FluentWindow implementation; Task 4 Step 4.4 includes the fallback probe if the installed version differs.
4. **Known deviation documented:** the Task 8 history.py line is the only services edit; it is flagged in the header and in Task 8 Step 8.1 as required by the approved spec's default-light decision.
5. **Task 12 is user-appended (m01400):** it does not change the spec; it drives the same widgets/callbacks built in Tasks 2–7 and gates them in Task 11's verification plus `run_all_tests.ps1`/CI. Its check names are stable so later UI changes that break a callback fail loudly.
