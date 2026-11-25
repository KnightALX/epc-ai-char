#!/usr/bin/env python3
"""Capture P2 compare screenshots: chart1 with/without constraints + chart2 lines."""
from __future__ import annotations

import os
import sys
from copy import deepcopy
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(_REPO))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from epc_gui.app import build_main_window
from epc_gui.services import history as hist_svc
from epc_gui.services.yaml_io import FIXTURE_SHORTCUTS, load_yaml
from epc_gui.theme import apply_theme
from epc_gui.paths import portable

OUT = Path(_REPO, "epc_gui/screenshots")
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
    win = build_main_window()
    win.show()
    win.resize(1320, 900)

    p1 = load_yaml(FIXTURE_SHORTCUTS["p1_green"])
    a = portable(p1["source"]["db_path"])
    b = portable(p1["output"]["db_path"])
    audit = portable(p1["output"]["audit_report_path"])
    empty = deepcopy(p1)
    empty["constraints"] = []

    def step_with_constraints():
        win.set_theme("dark")
        win.set_locale_ui("zh")
        win.compare.set_context(
            a_db=a,
            b_db=b,
            audit=audit,
            exit_code=0,
            yaml_data=p1,
            yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
        )
        win.switch_to("compare")
        QTimer.singleShot(500, step_grab_with)

    def step_grab_with():
        grab(win, "p2_dark_compare_chart1_constraints.png")
        grab(win, "p2_dark_compare.png")
        win.compare.set_context(
            a_db=a,
            b_db=b,
            audit=audit,
            exit_code=0,
            yaml_data=empty,
            yaml_path=None,
        )
        win.switch_to("compare")
        QTimer.singleShot(400, step_grab_empty)

    def step_grab_empty():
        grab(win, "p2_dark_compare_no_constraints.png")
        win.set_locale_ui("en")
        win.compare.set_context(
            a_db=a,
            b_db=b,
            audit=audit,
            exit_code=0,
            yaml_data=p1,
            yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
        )
        win.switch_to("compare")
        QTimer.singleShot(400, step_en)

    def step_en():
        grab(win, "p2_dark_compare_en.png")
        win.set_theme("light")
        win.set_locale_ui("zh")
        win.compare.set_context(
            a_db=a,
            b_db=b,
            audit=audit,
            exit_code=0,
            yaml_data=p1,
            yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
        )
        win.switch_to("compare")
        QTimer.singleShot(500, step_light_with)

    def step_light_with():
        grab(win, "p2_light_compare.png")
        grab(win, "p2_light_compare_chart1_constraints.png")
        win.compare.set_context(
            a_db=a,
            b_db=b,
            audit=audit,
            exit_code=0,
            yaml_data=empty,
            yaml_path=None,
        )
        win.switch_to("compare")
        QTimer.singleShot(400, step_light_empty)

    def step_light_empty():
        grab(win, "p2_light_compare_no_constraints.png")
        win.set_theme("dark")
        win.set_locale_ui("zh")
        win.config.load_shortcut("p1_green")
        win.switch_to("config")
        QTimer.singleShot(400, step_config_dark)

    def step_config_dark():
        grab(win, "p2_dark_config.png")
        win.set_theme("light")
        win.switch_to("config")
        QTimer.singleShot(400, step_config_light)

    def step_config_light():
        grab(win, "p2_light_config.png")
        app.quit()

    QTimer.singleShot(300, step_with_constraints)
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
