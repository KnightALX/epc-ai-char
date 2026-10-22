#!/usr/bin/env python3
"""Capture Page A/B/C (+ fail) via QWidget.grab() — offscreen safe."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, "/workspace")

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from epc_gui.app import MainWindow
from epc_gui.theme import apply_theme
from epc_gui.services.yaml_io import FIXTURE_SHORTCUTS, load_yaml

OUT = Path("/workspace/epc_gui/screenshots")
OUT.mkdir(parents=True, exist_ok=True)


def grab(widget, name: str) -> None:
    pix = widget.grab()
    path = OUT / name
    pix.save(str(path), "PNG")
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def main() -> int:
    app = QApplication(sys.argv)
    apply_theme(app)
    win = MainWindow()
    win.show()
    win.resize(1280, 820)

    def step1():
        win.config.load_shortcut("sample")
        grab(win, "page_a_config.png")
        y = load_yaml(FIXTURE_SHORTCUTS["sample"])
        db = y["output"]["db_path"]
        audit = y["output"]["audit_report_path"]
        if Path(db).is_file():
            win.preview.open_db(db)
        win.switch_to("preview")
        QTimer.singleShot(250, lambda: step2(db, audit, y))

    def step2(db, audit, y):
        grab(win, "page_b_preview.png")
        win.compare.set_context(
            a_db=y["source"]["db_path"],
            b_db=db,
            audit=audit,
            exit_code=0,
            yaml_data=y,
        )
        win.switch_to("compare")
        QTimer.singleShot(500, step3)

    def step3():
        grab(win, "page_c_compare.png")
        red = load_yaml(FIXTURE_SHORTCUTS["p2_geom_residual_h3hard_red"])
        win.compare.set_context(
            a_db=red["source"]["db_path"],
            b_db=red["output"]["db_path"],
            audit=red["output"]["audit_report_path"],
            exit_code=1,
            yaml_data=red,
        )
        QTimer.singleShot(250, step4)

    def step4():
        grab(win, "page_c_fail_h3hard.png")
        app.quit()

    QTimer.singleShot(300, step1)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
