#!/usr/bin/env python3
from __future__ import annotations
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, "/workspace")
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from epc_gui.app import MainWindow
from epc_gui.theme import apply_theme

app = QApplication(sys.argv)
apply_theme(app)
w = MainWindow()
w.show()
print("started OK")
QTimer.singleShot(500, app.quit)
raise SystemExit(app.exec_())
