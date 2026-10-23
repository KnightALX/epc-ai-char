#!/usr/bin/env python3
"""Capture P1 screenshots: config per locale + dark/light compare."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, "/workspace")

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from epc_gui.app import MainWindow
from epc_gui.services import history as hist_svc
from epc_gui.services.yaml_io import FIXTURE_SHORTCUTS, load_yaml
from epc_gui.theme import apply_theme

OUT = Path("/workspace/epc_gui/screenshots")
OUT.mkdir(parents=True, exist_ok=True)


def grab(widget, name: str) -> None:
    pix = widget.grab()
    path = OUT / name
    pix.save(str(path), "PNG")
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def main() -> int:
    hist_svc.save_settings({"theme": "dark", "locale": "zh"})
    app = QApplication(sys.argv)
    apply_theme(app, "dark")
    win = MainWindow()
    win.show()
    win.resize(1320, 860)

    sample = load_yaml(FIXTURE_SHORTCUTS["sample"])
    p1 = load_yaml(FIXTURE_SHORTCUTS["p1_green"])
    db = sample["output"]["db_path"]
    audit = sample["output"]["audit_report_path"]
    p1_db = p1["output"]["db_path"]
    use_db = p1_db if Path(p1_db).is_file() else db
    use_audit = p1["output"]["audit_report_path"] if Path(p1_db).is_file() else audit
    use_yaml = p1 if Path(p1_db).is_file() else sample
    use_src = use_yaml["source"]["db_path"]

    def prep_compare():
        win.compare.set_context(
            a_db=use_src,
            b_db=use_db,
            audit=use_audit,
            exit_code=0,
            yaml_data=use_yaml,
            yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
        )
        win.switch_to("compare")
        kl = win.compare.key_list
        for i in range(min(2, kl.count())):
            kl.item(i).setSelected(True)
        win.compare.refresh_trend()

    def step_zh_config():
        win.set_theme("dark")
        win.set_locale_ui("zh")
        win.config.load_shortcut("p1_green")
        win.switch_to("config")
        QTimer.singleShot(400, step_zh_config_grab)

    def step_zh_config_grab():
        grab(win, "p1_dark_config_zh.png")
        # also keep legacy name for older docs
        grab(win, "p1_dark_config.png")
        win.set_locale_ui("en")
        win.config.load_shortcut("p1_green")
        win.switch_to("config")
        QTimer.singleShot(400, step_en_config_grab)

    def step_en_config_grab():
        grab(win, "p1_dark_config_en.png")
        win.set_locale_ui("zh")
        prep_compare()
        QTimer.singleShot(600, step_dark_compare)

    def step_dark_compare():
        grab(win, "p1_dark_compare.png")
        win.set_theme("light")
        win.set_locale_ui("zh")
        win.config.load_shortcut("p1_green")
        win.switch_to("config")
        QTimer.singleShot(400, step_light_config)

    def step_light_config():
        grab(win, "p1_light_config.png")
        prep_compare()
        QTimer.singleShot(600, step_light_compare)

    def step_light_compare():
        grab(win, "p1_light_compare.png")
        app.quit()

    QTimer.singleShot(300, step_zh_config)
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
