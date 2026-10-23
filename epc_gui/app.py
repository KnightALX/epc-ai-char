"""Main window shell — probe-station rack per DESIGN.md (P0+P1).

FluentWindow aborts under offscreen/xvfb (frameless), so we keep QMainWindow
(Won't P1-L1). ThemeColor still applied; dark/light tokens from DESIGN.md.
Locale zh|en via Settings strip (independent of theme).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from epc_gui.i18n import get_i18n, get_locale, set_locale, tr
from epc_gui.pages.compare_page import ComparePage
from epc_gui.pages.config_page import ConfigPage
from epc_gui.pages.preview_page import PreviewPage
from epc_gui.services import history as hist_svc
from epc_gui.services import yaml_io
from epc_gui.theme import apply_theme, current_tokens


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPC Desktop")
        self.resize(1320, 860)
        settings = hist_svc.load_settings()
        self._theme = settings.get("theme", "dark")
        set_locale(settings.get("locale", "zh"), emit=False)
        self._build_chrome()
        self._wire()
        self.switch_to("config")
        self._refresh_strip()
        self._apply_shell_colors()
        self.retranslate()
        get_i18n().locale_changed.connect(self._on_locale_changed)

    def _build_chrome(self) -> None:
        t = current_tokens()
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.rail = QFrame()
        self.rail.setObjectName("NavRail")
        self.rail.setFixedWidth(168)
        rv = QVBoxLayout(self.rail)
        rv.setContentsMargins(0, 18, 0, 12)
        rv.setSpacing(2)
        self.brand = QLabel("EPC")
        rv.addWidget(self.brand)
        self.sub = QLabel("")
        rv.addWidget(self.sub)

        self._nav_btns: dict[str, QPushButton] = {}
        for key in ("config", "preview", "compare"):
            b = QPushButton("")
            b.setObjectName("navBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=key: self.switch_to(k))
            self._nav_btns[key] = b
            rv.addWidget(b)
        rv.addStretch(1)
        root.addWidget(self.rail)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        strip_row = QHBoxLayout()
        self.strip = QLabel("job — · mode — · EXIT —")
        strip_row.addWidget(self.strip, stretch=1)

        self.lbl_lang = QLabel("")
        strip_row.addWidget(self.lbl_lang)
        self.cb_locale = QComboBox()
        self.cb_locale.setMinimumWidth(100)
        self.cb_locale.addItem("", "zh")
        self.cb_locale.addItem("", "en")
        self.cb_locale.currentIndexChanged.connect(self._on_locale_combo)
        strip_row.addWidget(self.cb_locale)

        self.btn_theme = QPushButton("")
        self.btn_theme.clicked.connect(self.toggle_theme)
        strip_row.addWidget(self.btn_theme)
        strip_w = QWidget()
        strip_w.setObjectName("StickyStrip")
        strip_w.setLayout(strip_row)
        self.strip_w = strip_w
        right.addWidget(strip_w)

        self.stack = QStackedWidget()
        self.config = ConfigPage()
        self.preview = PreviewPage()
        self.compare = ComparePage()
        self.stack.addWidget(self.config)
        self.stack.addWidget(self.preview)
        self.stack.addWidget(self.compare)
        right.addWidget(self.stack, stretch=1)

        right_w = QWidget()
        right_w.setLayout(right)
        root.addWidget(right_w, stretch=1)
        self._page_index = {"config": 0, "preview": 1, "compare": 2}
        self._sync_locale_combo()
        self._update_theme_button()

    def _wire(self) -> None:
        self.config.request_preview.connect(self._on_preview)
        self.config.job_finished.connect(self._on_job)
        self.config.history_open.connect(self._on_history)
        self.config.yaml_edit.textChanged.connect(self._refresh_strip)

    def _apply_shell_colors(self) -> None:
        t = current_tokens()
        self.setStyleSheet(f"QMainWindow {{ background: {t.InkWell}; }}")
        self.rail.setStyleSheet(
            f"""
            QFrame#NavRail {{
                background: {t.PanelSteel};
                border-right: 1px solid {t.RuleLine};
            }}
            """
        )
        self.brand.setStyleSheet(
            f"color: {t.TraceAmber}; font-size: 18px; font-weight: 500; padding: 0 16px 8px 16px;"
        )
        self.sub.setStyleSheet(
            f"color: {t.MuteFog}; font-size: 11px; padding: 0 16px 14px 16px;"
        )
        self.strip_w.setStyleSheet(
            f"""
            QWidget#StickyStrip {{
                background: {t.PanelSteel};
                border-bottom: 1px solid {t.RuleLine};
            }}
            """
        )
        self.strip.setStyleSheet(
            f"""
            color: {t.MuteFog};
            padding: 9px 14px;
            font-family: IBM Plex Mono, DejaVu Sans Mono, monospace;
            font-size: 12px;
            """
        )
        self.lbl_lang.setStyleSheet(f"color: {t.MuteFog}; font-size: 12px;")
        cur = None
        for k, idx in self._page_index.items():
            if self.stack.currentIndex() == idx:
                cur = k
                break
        if cur:
            self.switch_to(cur)

    def toggle_theme(self) -> None:
        self._theme = "light" if self._theme != "light" else "dark"
        hist_svc.save_settings({"theme": self._theme})
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme)
        self._update_theme_button()
        self._apply_shell_colors()
        self.compare.reapply_theme_plots()

    def _update_theme_button(self) -> None:
        self.btn_theme.setText(
            tr("theme.light") if self._theme == "light" else tr("theme.dark")
        )

    def set_theme(self, mode: str) -> None:
        self._theme = "light" if str(mode).lower().startswith("light") else "dark"
        hist_svc.save_settings({"theme": self._theme})
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme)
        self._update_theme_button()
        self._apply_shell_colors()
        self.compare.reapply_theme_plots()

    def set_locale_ui(self, locale: str) -> None:
        """Public for capture/smoke: persist + refresh."""
        loc = "en" if str(locale).lower().startswith("en") else "zh"
        hist_svc.save_settings({"locale": loc})
        set_locale(loc)
        self._sync_locale_combo()

    def _sync_locale_combo(self) -> None:
        self.cb_locale.blockSignals(True)
        want = get_locale()
        for i in range(self.cb_locale.count()):
            if self.cb_locale.itemData(i) == want:
                self.cb_locale.setCurrentIndex(i)
                break
        self.cb_locale.blockSignals(False)

    def _on_locale_combo(self, _idx: int = 0) -> None:
        data = self.cb_locale.currentData()
        if not data:
            return
        hist_svc.save_settings({"locale": data})
        set_locale(str(data))

    def _on_locale_changed(self, _loc: str) -> None:
        self.retranslate()

    def retranslate(self) -> None:
        sub = tr("brand.sub")
        self.sub.setText(sub)
        self.sub.setVisible(bool(sub.strip()))
        self._nav_btns["config"].setText(tr("nav.config"))
        self._nav_btns["preview"].setText(tr("nav.preview"))
        self._nav_btns["compare"].setText(tr("nav.compare"))
        self.lbl_lang.setText(tr("lang.chrome"))
        self.cb_locale.blockSignals(True)
        for i in range(self.cb_locale.count()):
            code = self.cb_locale.itemData(i)
            self.cb_locale.setItemText(i, tr("lang.zh") if code == "zh" else tr("lang.en"))
        self.cb_locale.blockSignals(False)
        self._update_theme_button()
        self.config.retranslate()
        self.preview.retranslate()
        self.compare.retranslate()
        self._refresh_strip()

    def switch_to(self, key: str) -> None:
        t = current_tokens()
        self.stack.setCurrentIndex(self._page_index[key])
        for k, b in self._nav_btns.items():
            active = k == key
            if active:
                b.setStyleSheet(
                    f"""
                    QPushButton#navBtn {{
                        text-align: left; padding: 10px 16px; border: none;
                        border-left: 3px solid {t.TraceAmber}; background: {t.InkWell};
                        color: {t.TraceAmber}; border-radius: 0;
                    }}
                    """
                )
            else:
                b.setStyleSheet(
                    f"""
                    QPushButton#navBtn {{
                        text-align: left; padding: 10px 16px; border: none;
                        border-left: 3px solid transparent; background: transparent;
                        color: {t.Chalk}; border-radius: 0;
                    }}
                    QPushButton#navBtn:hover {{ color: {t.TraceAmber}; }}
                    """
                )

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


def run(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    import os

    if not os.environ.get("DISPLAY") and not os.environ.get("QT_QPA_PLATFORM"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication(argv)
    settings = hist_svc.load_settings()
    set_locale(settings.get("locale", "zh"), emit=False)
    apply_theme(app, settings.get("theme", "dark"))
    main = MainWindow()
    main.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(run())
