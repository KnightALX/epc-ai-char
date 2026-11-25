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
