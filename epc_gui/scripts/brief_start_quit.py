#!/usr/bin/env python3
from __future__ import annotations
import os, sys
from pathlib import Path
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from epc_gui.app import build_main_window
from epc_gui.theme import apply_theme

app = QApplication(sys.argv)
apply_theme(app, "light")
w = build_main_window()
w.show()
print("started OK")
QTimer.singleShot(500, app.quit)
raise SystemExit(app.exec_())
