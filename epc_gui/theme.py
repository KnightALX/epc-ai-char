"""Visual tokens from DESIGN.md — Virtuoso-like cool gray + blue QSS + plot chrome."""
from __future__ import annotations

from dataclasses import dataclass

from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import QApplication

UI_FONT_FAMILY = "Noto Sans, Source Sans 3, Segoe UI, PingFang SC, Noto Sans CJK SC, sans-serif"
DATA_FONT_FAMILY = "IBM Plex Mono, Cascadia Mono, DejaVu Sans Mono, Noto Sans Mono, monospace"


@dataclass(frozen=True)
class ThemeTokens:
    name: str
    InkWell: str
    PanelSteel: str
    RuleLine: str
    Chalk: str
    MuteFog: str
    AccentBlue: str
    TraceAmber: str  # alias of AccentBlue (legacy name; value is blue)
    PvtCyan: str  # secondary series / deeper cool gray-blue (not high-sat cyan)
    PassTeal: str
    FailRose: str
    PlotCanvas: str
    PVT_LINE_COLORS: tuple[str, ...]


# Virtuoso CIW-like dark — cool gray base, single blue accent
DARK = ThemeTokens(
    name="dark",
    InkWell="#1E1E1E",
    PanelSteel="#2D2D30",
    RuleLine="#3E3E42",
    Chalk="#D4D4D4",
    MuteFog="#9A9A9A",
    AccentBlue="#4A90D9",
    TraceAmber="#4A90D9",
    PvtCyan="#6B7C8A",
    PassTeal="#6A9F6A",
    FailRose="#C75B5B",
    PlotCanvas="#1E1E1E",
    PVT_LINE_COLORS=(
        "#4A90D9",  # AccentBlue
        "#7A8B99",  # SteelGray
        "#5A7A9A",  # SlateBlue
        "#8A9AAA",  # MistSteel
        "#3D6A9A",  # DeepSky
        "#A0A8B0",  # SilverFog
    ),
)

# Cool steel light — FORBIDDEN: cream #F4F1EA, terracotta #D97757
LIGHT = ThemeTokens(
    name="light",
    InkWell="#EEF1F5",
    PanelSteel="#FFFFFF",
    RuleLine="#C5CED8",
    Chalk="#1A2330",
    MuteFog="#5A6675",
    AccentBlue="#2E6BB0",  # deepened for WCAG on light paper
    TraceAmber="#2E6BB0",
    PvtCyan="#5A6B7A",
    PassTeal="#3D7A3D",
    FailRose="#B04040",
    PlotCanvas="#FFFFFF",
    PVT_LINE_COLORS=(
        "#2E6BB0",
        "#5A6B7A",
        "#3D5A7A",
        "#6A7A8A",
        "#1E4A7A",
        "#7A8894",
    ),
)

# Module-level aliases (updated by apply_theme) for legacy imports
InkWell = DARK.InkWell
PanelSteel = DARK.PanelSteel
RuleLine = DARK.RuleLine
Chalk = DARK.Chalk
MuteFog = DARK.MuteFog
AccentBlue = DARK.AccentBlue
TraceAmber = DARK.TraceAmber
PvtCyan = DARK.PvtCyan
PassTeal = DARK.PassTeal
FailRose = DARK.FailRose
PVT_LINE_COLORS = list(DARK.PVT_LINE_COLORS)

_CURRENT = DARK


def current_tokens() -> ThemeTokens:
    return _CURRENT


def _build_qss(t: ThemeTokens) -> str:
    accent = t.AccentBlue
    return f"""
QMainWindow, QWidget {{
    background-color: {t.InkWell};
    color: {t.Chalk};
    font-family: {UI_FONT_FAMILY};
    font-size: 13px;
}}
QScrollArea {{ background: {t.InkWell}; border: none; }}
/* Field bands = instrument panels: hairline, no soft shadow stack */
QFrame#FieldBand, QGroupBox {{
    background-color: {t.PanelSteel};
    border: 1px solid {t.RuleLine};
    border-radius: 2px;
    margin-top: 8px;
    padding: 10px 10px 8px 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {t.MuteFog};
    font-size: 13px;
    font-weight: 500;
}}
QFrame#ReadoutBand {{
    background-color: {t.InkWell};
    border-left: 1px solid {t.RuleLine};
    border-radius: 0;
    padding: 8px 10px;
}}
QLabel {{ color: {t.Chalk}; }}
QLabel#Mute, QLabel.mute {{ color: {t.MuteFog}; font-size: 11px; }}
QLabel#Title {{ font-size: 18px; font-weight: 500; color: {t.Chalk}; letter-spacing: 0.2px; }}
QLabel#Section {{ font-size: 13px; font-weight: 500; color: {t.MuteFog}; }}
QLabel#Pass {{ color: {t.PassTeal}; font-family: {DATA_FONT_FAMILY}; }}
QLabel#Fail {{ color: {t.FailRose}; font-family: {DATA_FONT_FAMILY}; }}
QLabel#Unknown {{ color: {t.MuteFog}; font-family: {DATA_FONT_FAMILY}; }}
QLabel#LampPass {{ color: {t.PassTeal}; font-size: 14px; }}
QLabel#LampFail {{ color: {t.FailRose}; font-size: 14px; }}
QLabel#LampUnknown {{ color: {t.MuteFog}; font-size: 14px; }}
QLabel#Readout {{
    font-family: {DATA_FONT_FAMILY};
    font-size: 13px;
    color: {t.Chalk};
    padding: 2px 0;
}}
QLabel#ReadoutMuted {{
    font-family: {DATA_FONT_FAMILY};
    font-size: 11px;
    color: {t.MuteFog};
}}
QLabel#GateLights {{
    font-family: {DATA_FONT_FAMILY};
    font-size: 12px;
    color: {t.MuteFog};
}}
QLabel#StatusMono {{
    font-family: {DATA_FONT_FAMILY};
    font-size: 12px;
    color: {t.MuteFog};
}}
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: {t.InkWell};
    color: {t.Chalk};
    border: 1px solid {t.RuleLine};
    border-radius: 2px;
    padding: 5px 8px;
    selection-background-color: {accent};
    selection-color: #FFFFFF;
    font-family: {DATA_FONT_FAMILY};
    font-size: 12px;
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {accent};
}}
QPlainTextEdit#YamlEditor {{
    font-family: {DATA_FONT_FAMILY};
    font-size: 12px;
}}
QPlainTextEdit#AuditSnippet {{
    font-family: {DATA_FONT_FAMILY};
    font-size: 11px;
    color: {t.MuteFog};
    background: {t.InkWell};
    border: 1px solid {t.RuleLine};
    border-radius: 2px;
}}
QComboBox QAbstractItemView {{
    background: {t.PanelSteel};
    color: {t.Chalk};
    selection-background-color: {accent};
    selection-color: #FFFFFF;
    border: 1px solid {t.RuleLine};
}}
QPushButton {{
    background-color: {t.PanelSteel};
    color: {t.Chalk};
    border: 1px solid {t.RuleLine};
    border-radius: 2px;
    padding: 6px 12px;
    font-size: 13px;
}}
QPushButton:hover {{ border-color: {accent}; color: {t.Chalk}; }}
QPushButton:pressed {{ background-color: {t.RuleLine}; }}
QPushButton:disabled {{ color: {t.MuteFog}; border-color: {t.RuleLine}; }}
QPushButton#Primary {{
    background-color: {accent};
    color: #FFFFFF;
    border: 1px solid {accent};
    font-weight: 500;
}}
QPushButton#Primary:hover {{ background-color: {accent}; color: #FFFFFF; }}
QPushButton#Danger {{
    border-color: {t.FailRose};
    color: {t.FailRose};
    background: transparent;
}}
QPushButton#Danger:hover {{ background: {t.FailRose}; color: #FFFFFF; }}
QTableWidget, QTableView {{
    background-color: {t.InkWell};
    alternate-background-color: {t.PanelSteel};
    gridline-color: {t.RuleLine};
    color: {t.Chalk};
    border: 1px solid {t.RuleLine};
    border-radius: 2px;
    font-family: {DATA_FONT_FAMILY};
    font-size: 12px;
}}
QHeaderView::section {{
    background-color: {t.PanelSteel};
    color: {t.MuteFog};
    border: none;
    border-bottom: 1px solid {t.RuleLine};
    border-right: 1px solid {t.RuleLine};
    padding: 5px 6px;
    font-family: {UI_FONT_FAMILY};
    font-size: 12px;
}}
QCheckBox {{ color: {t.Chalk}; spacing: 6px; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {t.RuleLine};
    background: {t.InkWell};
    border-radius: 2px;
}}
QCheckBox::indicator:checked {{
    background: {accent};
    border-color: {accent};
}}
QListWidget {{
    background: {t.InkWell};
    border: 1px solid {t.RuleLine};
    border-radius: 2px;
    color: {t.Chalk};
    font-family: {DATA_FONT_FAMILY};
    font-size: 12px;
}}
QListWidget::item {{ padding: 3px 6px; }}
QListWidget::item:selected {{
    background: {accent};
    color: #FFFFFF;
}}
QStatusBar {{
    background: {t.PanelSteel};
    color: {t.MuteFog};
    border-top: 1px solid {t.RuleLine};
}}
QSplitter::handle {{ background: {t.RuleLine}; width: 1px; height: 1px; }}
QProgressBar {{
    border: 1px solid {t.RuleLine};
    background: {t.InkWell};
    text-align: center;
    color: {t.Chalk};
    border-radius: 2px;
}}
QProgressBar::chunk {{ background: {accent}; }}
QScrollBar:vertical {{
    background: {t.InkWell}; width: 9px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t.RuleLine}; border-radius: 2px; min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {t.InkWell}; height: 9px; margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {t.RuleLine}; border-radius: 2px; min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QTabWidget::pane {{
    border: 1px solid {t.RuleLine};
    background: {t.InkWell};
}}
QTabBar::tab {{
    background: {t.PanelSteel};
    color: {t.MuteFog};
    border: 1px solid {t.RuleLine};
    padding: 6px 12px;
    border-radius: 2px;
}}
QTabBar::tab:selected {{
    color: {t.Chalk};
    border-bottom: 2px solid {accent};
    border-bottom-color: {accent};
}}
QToolTip {{
    background-color: {t.PanelSteel};
    color: {t.Chalk};
    border: 1px solid {t.RuleLine};
    padding: 4px 8px;
    font-size: 12px;
}}
"""


def _sync_aliases(t: ThemeTokens) -> None:
    global InkWell, PanelSteel, RuleLine, Chalk, MuteFog
    global AccentBlue, TraceAmber, PvtCyan, PassTeal, FailRose, PVT_LINE_COLORS, _CURRENT
    _CURRENT = t
    InkWell = t.InkWell
    PanelSteel = t.PanelSteel
    RuleLine = t.RuleLine
    Chalk = t.Chalk
    MuteFog = t.MuteFog
    AccentBlue = t.AccentBlue
    TraceAmber = t.TraceAmber
    PvtCyan = t.PvtCyan
    PassTeal = t.PassTeal
    FailRose = t.FailRose
    PVT_LINE_COLORS = list(t.PVT_LINE_COLORS)


def apply_theme(app: QApplication, mode: str = "dark") -> ThemeTokens:
    t = LIGHT if str(mode).lower().startswith("light") else DARK
    _sync_aliases(t)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(t.InkWell))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(t.Chalk))
    pal.setColor(QPalette.ColorRole.Base, QColor(t.InkWell))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(t.PanelSteel))
    pal.setColor(QPalette.ColorRole.Text, QColor(t.Chalk))
    pal.setColor(QPalette.ColorRole.Button, QColor(t.PanelSteel))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(t.Chalk))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(t.AccentBlue))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(t.PanelSteel))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(t.Chalk))
    app.setPalette(pal)
    app.setStyleSheet(_build_qss(t))
    try:
        from qfluentwidgets import Theme, setTheme, setThemeColor

        setTheme(Theme.LIGHT if t.name == "light" else Theme.DARK)
        setThemeColor(t.AccentBlue)
    except Exception:
        pass
    f = QFont()
    f.setFamilies(["Noto Sans", "Segoe UI", "PingFang SC", "sans-serif"])
    f.setPointSize(10)
    app.setFont(f)
    return t


def configure_plot(pw, tokens: ThemeTokens | None = None) -> None:
    """Apply DESIGN chart chrome — PlotCanvas bg, RuleLine axes, MuteFog ticks."""
    t = tokens or _CURRENT
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
    # Quiet plot title (section scale)
    try:
        pi.titleLabel.setAttr("color", t.MuteFog)
        pi.titleLabel.setAttr("size", "11pt")
    except Exception:
        pass


def _data_tick_font():
    f = QFont()
    f.setFamilies(["IBM Plex Mono", "Cascadia Mono", "DejaVu Sans Mono", "monospace"])
    f.setPointSize(9)
    return f
