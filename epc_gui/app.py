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
