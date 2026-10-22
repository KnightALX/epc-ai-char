"""Page C — P2: gate zone → chart1 constraint markup → chart2 free compare."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QDesktopServices
from PyQt6.QtWidgets import (
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
from epc_gui.theme import configure_plot, current_tokens

HOLDOUT_MD = Path("/workspace/epc_fixtures/algo_holdout_report.md")
EVAL_H3 = Path("/workspace/epc_fixtures/p2/eval_h3.py")
H3_REPORT = Path("/workspace/epc_fixtures/p2/h3_report.md")


class ComparePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._audit_path: str | None = None
        self._b_db: str | None = None
        self._a_db: str | None = None
        self._ref_db: str | None = None
        self._constructed_db: str | None = None
        self._yaml: dict | None = None
        self._yaml_path: str | None = None
        self._exit_code: int | None = None
        self._last_audit: AuditSummary | None = None
        self._chart1: cv.Chart1Model | None = None
        self._free: cv.FreeCompareModel | None = None
        self._plot_widgets: list = []

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        self.title = QLabel("")
        self.title.setObjectName("Title")
        root.addWidget(self.title)

        # --- Gate zone (P2-G0) ---
        self.gate_box = QGroupBox("")
        gv = QVBoxLayout(self.gate_box)
        grow = QHBoxLayout()
        grow.setSpacing(8)
        self.btn_audit = QPushButton("")
        self.btn_audit.clicked.connect(self.browse_audit)
        self.btn_open_full = QPushButton("")
        self.btn_open_full.clicked.connect(self.open_full_audit)
        self.lbl_lamp = QLabel("●")
        self.lbl_lamp.setObjectName("LampUnknown")
        self.lbl_overall = QLabel("")
        self.lbl_gates_ok = QLabel("")  # kept hidden; no bare gates_ok field dump
        self.lbl_gates_ok.setVisible(False)
        self.lbl_exit = QLabel("EXIT —")
        self.lbl_exit.setObjectName("Readout")
        self.lbl_db = QLabel("")
        self.lbl_db.setObjectName("Mute")
        grow.addWidget(self.btn_audit)
        grow.addWidget(self.btn_open_full)
        grow.addSpacing(6)
        grow.addWidget(self.lbl_lamp)
        grow.addWidget(self.lbl_overall)
        grow.addWidget(self.lbl_exit)
        grow.addWidget(self.lbl_db)
        grow.addStretch(1)
        gv.addLayout(grow)
        self.gate_lights = QLabel("")
        self.gate_lights.setObjectName("GateLights")
        self.gate_lights.setWordWrap(True)
        gv.addWidget(self.gate_lights)
        self.audit_snip = QPlainTextEdit()
        self.audit_snip.setObjectName("AuditSnippet")
        self.audit_snip.setReadOnly(True)
        self.audit_snip.setMaximumHeight(64)
        gv.addWidget(self.audit_snip)
        root.addWidget(self.gate_box)

        # --- Chart 1 empty state (shown when no constraints) ---
        self.lbl_chart1_empty = QLabel("")
        self.lbl_chart1_empty.setObjectName("Mute")
        self.lbl_chart1_empty.setWordWrap(True)
        self.lbl_chart1_empty.setContentsMargins(4, 2, 4, 6)
        root.addWidget(self.lbl_chart1_empty)

        # --- Chart 1 · constraint evidence ---
        self.chart1_box = QGroupBox("")
        c1 = QVBoxLayout(self.chart1_box)
        c1row = QHBoxLayout()
        self.lbl_view = QLabel("")
        self.cb_view = QComboBox()
        self.cb_view.currentIndexChanged.connect(self._on_view_changed)
        c1row.addWidget(self.lbl_view)
        c1row.addWidget(self.cb_view)
        c1row.addStretch(1)
        self.lbl_sat = QLabel("")
        self.lbl_sat.setObjectName("Readout")
        self.lbl_sat.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        c1row.addWidget(self.lbl_sat)
        c1.addLayout(c1row)
        self.plot_c1 = pg.PlotWidget()
        configure_plot(self.plot_c1)
        self.plot_c1.setMinimumHeight(168)
        self.plot_c1.setMaximumHeight(248)
        self._c1_hover_tips: list[str] = []
        self._c1_proxy = pg.SignalProxy(
            self.plot_c1.scene().sigMouseMoved, rateLimit=40, slot=self._on_c1_hover
        )
        c1.addWidget(self.plot_c1)
        self.tbl_c1 = QTableWidget(0, 5)
        self.tbl_c1.setMaximumHeight(180)
        self.tbl_c1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_c1.setVisible(False)
        c1.addWidget(self.tbl_c1)
        root.addWidget(self.chart1_box)
        self._plot_widgets = [self.plot_c1]

        # --- Chart 2 · free compare ---
        self.chart2_box = QGroupBox("")
        c2 = QVBoxLayout(self.chart2_box)
        ctrl = QHBoxLayout()
        self.btn_ref = QPushButton("")
        self.btn_constructed = QPushButton("")
        self.btn_ref.clicked.connect(lambda: self._pick_compare_db("ref"))
        self.btn_constructed.clicked.connect(lambda: self._pick_compare_db("constructed"))
        self.lbl_ref = QLabel("")
        self.lbl_ref.setObjectName("Mute")
        self.lbl_constructed = QLabel("")
        self.lbl_constructed.setObjectName("Mute")
        self.cb_pvt = QComboBox()
        self.cb_key = QComboBox()
        self.cb_pvt.setMinimumWidth(160)
        self.cb_key.setMinimumWidth(140)
        self.cb_pvt.currentIndexChanged.connect(self._on_free_filter)
        self.cb_key.currentIndexChanged.connect(self._on_free_filter)
        self.btn_refresh_free = QPushButton("")
        self.btn_refresh_free.clicked.connect(self.refresh_free_compare)
        ctrl.addWidget(self.btn_ref)
        ctrl.addWidget(self.lbl_ref)
        ctrl.addWidget(self.btn_constructed)
        ctrl.addWidget(self.lbl_constructed)
        ctrl.addWidget(QLabel("PVT"))
        ctrl.addWidget(self.cb_pvt)
        ctrl.addWidget(QLabel("key"))
        ctrl.addWidget(self.cb_key)
        ctrl.addWidget(self.btn_refresh_free)
        ctrl.addStretch(1)
        c2.addLayout(ctrl)

        body = QHBoxLayout()
        self.plot_c2 = pg.PlotWidget()
        configure_plot(self.plot_c2)
        self.plot_c2.setLabel("bottom", "capacity")
        self.plot_c2.setLabel("left", "typical")
        self.plot_c2.addLegend(offset=(10, 10))
        self.plot_c2.setMinimumHeight(220)
        self.plot_c2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body.addWidget(self.plot_c2, stretch=3)

        side = QVBoxLayout()
        side.setContentsMargins(10, 4, 4, 4)
        side.setSpacing(6)
        self.lbl_typical_note = QLabel("")
        self.lbl_typical_note.setObjectName("Mute")
        self.lbl_typical_note.setVisible(False)  # median_cell → tooltip only
        self.lbl_cover = QLabel("")
        self.lbl_cover.setObjectName("Readout")
        self.lbl_delta = QLabel("")
        self.lbl_delta.setObjectName("Readout")
        self.lbl_delta_mean = QLabel("")
        self.lbl_delta_mean.setObjectName("Readout")
        self.lbl_free_empty = QLabel("")
        self.lbl_free_empty.setObjectName("Mute")
        self.lbl_free_empty.setWordWrap(True)
        side.addWidget(self.lbl_cover)
        side.addWidget(self.lbl_delta)
        side.addWidget(self.lbl_delta_mean)
        side.addWidget(self.lbl_free_empty)
        side.addStretch(1)
        side_w = QFrame()
        side_w.setObjectName("ReadoutBand")
        side_w.setLayout(side)
        side_w.setMinimumWidth(148)
        side_w.setMaximumWidth(200)
        body.addWidget(side_w)
        c2.addLayout(body)
        root.addWidget(self.chart2_box, stretch=1)
        self._plot_widgets.append(self.plot_c2)

        # Should: thin aux for eval_h3 / hold-out (not Must clutter)
        aux = QHBoxLayout()
        self.btn_eval_h3 = QPushButton("eval_h3")
        self.btn_holdout = QPushButton("hold-out")
        self.btn_eval_h3.clicked.connect(self.run_eval_h3)
        self.btn_holdout.clicked.connect(lambda: self._open_md(HOLDOUT_MD))
        self.eval_log = QPlainTextEdit()
        self.eval_log.setReadOnly(True)
        self.eval_log.setMaximumHeight(60)
        aux.addWidget(self.btn_eval_h3)
        aux.addWidget(self.btn_holdout)
        aux.addWidget(self.eval_log, stretch=1)
        root.addLayout(aux)

        self.retranslate()

    # ---- i18n ----
    def retranslate(self) -> None:
        self.title.setText(tr("compare.title"))
        self.gate_box.setTitle(tr("group.gates"))
        self.gate_box.setToolTip(tr("tip.compare_gates"))
        self.btn_audit.setText(tr("btn.open_audit"))
        self.btn_open_full.setText(tr("btn.open_full_audit"))
        self.chart1_box.setTitle(tr("group.chart1"))
        self.chart1_box.setToolTip(tr("tip.chart1"))
        self.lbl_view.setText(tr("chart1.view"))
        self.lbl_chart1_empty.setText(tr("chart1.empty"))
        self.chart2_box.setTitle(tr("group.chart2"))
        self.chart2_box.setToolTip(tr("tip.chart2"))
        self.btn_ref.setText(tr("btn.ref_db"))
        self.btn_constructed.setText(tr("btn.constructed_db"))
        self.btn_refresh_free.setText(tr("btn.refresh"))
        self.eval_log.setPlaceholderText(tr("placeholder.eval_log"))
        self.tbl_c1.setHorizontalHeaderLabels(
            [
                tr("col.type"),
                tr("col.instance"),
                tr("col.pvt"),
                tr("col.key"),
                tr("col.detail"),
            ]
        )
        # refresh dynamic labels
        if self._last_audit is not None:
            self._apply_summary(self._last_audit)
        elif not self._audit_path:
            self.lbl_overall.setText(tr("overall.unknown"))
            self.lbl_gates_ok.clear()
            self.lbl_lamp.setObjectName("LampUnknown")
            self.lbl_lamp.style().unpolish(self.lbl_lamp)
            self.lbl_lamp.style().polish(self.lbl_lamp)
        if self._exit_code is not None:
            self.lbl_exit.setText(f"EXIT {self._exit_code}")
        self._update_path_labels()
        self._retranslate_view_combo()
        if self._chart1 is not None:
            self._apply_chart1_visibility()
            self._render_chart1()
        if self._free is not None:
            self._render_free_compare()

    def _retranslate_view_combo(self) -> None:
        labels = {
            cv.VIEW_REL_BARS: tr("view.rel_bars"),
            cv.VIEW_BOUND_CELLS: tr("view.bound_cells"),
            cv.VIEW_CONSTRAINT_LIST: tr("view.constraint_list"),
        }
        self.cb_view.blockSignals(True)
        cur = self.cb_view.currentData()
        for i in range(self.cb_view.count()):
            data = self.cb_view.itemData(i)
            if data in labels:
                self.cb_view.setItemText(i, labels[data])
        if cur is not None:
            idx = self.cb_view.findData(cur)
            if idx >= 0:
                self.cb_view.setCurrentIndex(idx)
        self.cb_view.blockSignals(False)

    # ---- context ----
    def set_context(
        self,
        *,
        a_db: str | None,
        b_db: str | None,
        audit: str | None,
        exit_code: int | None = None,
        yaml_data: dict | None = None,
        yaml_path: str | None = None,
    ) -> None:
        if a_db:
            self._a_db = a_db
            self._ref_db = a_db
        if b_db:
            self._b_db = b_db
            self._constructed_db = b_db
        if audit:
            self.load_audit(audit)
        if exit_code is not None:
            self._exit_code = exit_code
            self.lbl_exit.setText(f"EXIT {exit_code}")
            self.lbl_exit.setStyleSheet(
                f"color: {current_tokens().PassTeal};"
                if exit_code == 0
                else f"color: {current_tokens().FailRose};"
            )
        if yaml_data is not None:
            self._yaml = yaml_data
            # When a fresh YAML dict is supplied, path may be cleared (None)
            # so expand uses the dict rather than a stale fixture path.
            self._yaml_path = yaml_path
        elif yaml_path:
            self._yaml_path = yaml_path
        self._update_path_labels()
        self.refresh_chart1()
        self.refresh_free_compare()

    def _update_path_labels(self) -> None:
        def short(p: str | None) -> str:
            if not p:
                return "—"
            return Path(p).name

        self.lbl_ref.setText(short(self._ref_db))
        self.lbl_constructed.setText(short(self._constructed_db))
        if self._b_db:
            exists = Path(self._b_db).is_file()
            key = "db.b_exists" if exists else "db.b_missing"
            self.lbl_db.setText(tr(key))
            self.lbl_db.setToolTip(self._b_db)
            self.lbl_db.setStyleSheet(
                f"color: {current_tokens().PassTeal if exists else current_tokens().FailRose};"
            )
        else:
            self.lbl_db.setText(tr("db.b_missing"))
            self.lbl_db.setToolTip("")

    # ---- gates ----
    def browse_audit(self) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.open_audit"), "/workspace/epc_fixtures", "Markdown (*.md)"
        )
        if p:
            self.load_audit(p)

    def load_audit(self, path: str) -> None:
        self._audit_path = path
        self._apply_summary(parse_audit(path))
        self._update_sat_rate()

    def open_full_audit(self) -> None:
        if not self._audit_path or not Path(self._audit_path).is_file():
            self.browse_audit()
            return
        try:
            QDesktopServices.openUrl(Path(self._audit_path).as_uri())
        except Exception:
            pass

    def _apply_summary(self, s: AuditSummary) -> None:
        self._last_audit = s
        disp = s.display_overall or s.overall
        if disp == "PASS":
            self.lbl_overall.setText(tr("overall.pass"))
            color = current_tokens().PassTeal
            self.lbl_lamp.setObjectName("LampPass")
        elif disp == "FAIL":
            self.lbl_overall.setText(tr("overall.fail"))
            color = current_tokens().FailRose
            self.lbl_lamp.setObjectName("LampFail")
        else:
            self.lbl_overall.setText(tr("overall.unknown"))
            color = current_tokens().MuteFog
            self.lbl_lamp.setObjectName("LampUnknown")
        self.lbl_lamp.style().unpolish(self.lbl_lamp)
        self.lbl_lamp.style().polish(self.lbl_lamp)
        self.lbl_overall.setStyleSheet(f"color: {color}; font-weight: 500;")
        self.lbl_gates_ok.clear()
        # Short light-bar codes only; skip n/a clutter
        parts = [
            f"{g.name}-{g.status}"
            for g in s.gates
            if g.status and g.status.lower() not in ("n/a",)
        ]
        self.gate_lights.setText(" · ".join(parts))
        self.audit_snip.setPlainText(s.snippet)
        if not s.parse_ok:
            self.lbl_overall.setText(tr("overall.unknown"))
            self.lbl_overall.setStyleSheet(f"color: {current_tokens().MuteFog}; font-weight: 500;")
            self.lbl_lamp.setObjectName("LampUnknown")
            self.lbl_lamp.style().unpolish(self.lbl_lamp)
            self.lbl_lamp.style().polish(self.lbl_lamp)

    # ---- chart 1 ----
    def refresh_chart1(self) -> None:
        self._chart1 = cv.build_chart1(
            yaml_path=self._yaml_path,
            yaml_data=self._yaml,
            a_db=self._a_db or self._ref_db,
            b_db=self._b_db or self._constructed_db,
        )
        self._apply_chart1_visibility()
        model = self._chart1
        self.cb_view.blockSignals(True)
        self.cb_view.clear()
        labels = {
            cv.VIEW_REL_BARS: tr("view.rel_bars"),
            cv.VIEW_BOUND_CELLS: tr("view.bound_cells"),
            cv.VIEW_CONSTRAINT_LIST: tr("view.constraint_list"),
        }
        for v in model.available_views:
            self.cb_view.addItem(labels.get(v, v), v)
        if model.default_view:
            idx = self.cb_view.findData(model.default_view)
            if idx >= 0:
                self.cb_view.setCurrentIndex(idx)
        self.cb_view.blockSignals(False)
        self._update_sat_rate()
        self._render_chart1()

    def _apply_chart1_visibility(self) -> None:
        has = bool(self._chart1 and self._chart1.has_constraints)
        self.chart1_box.setVisible(has)
        self.lbl_chart1_empty.setVisible(not has)
        if not has:
            self.lbl_chart1_empty.setText(tr("chart1.empty"))
        self._update_sat_rate()

    def _update_sat_rate(self) -> None:
        """P21-M1: show audit-derived 达标 n/m beside chart1; hide with band when no constraints."""
        has = bool(self._chart1 and self._chart1.has_constraints)
        if not has:
            self.lbl_sat.clear()
            self.lbl_sat.setVisible(False)
            return
        self.lbl_sat.setVisible(True)
        sat = parse_constraint_sat_rate(self._audit_path)
        if not sat.parseable or sat.pass_n is None or sat.total_m is None:
            self.lbl_sat.setText(tr("chart1.sat_na"))
        else:
            self.lbl_sat.setText(tr("chart1.sat_rate", n=sat.pass_n, m=sat.total_m))

    def _on_view_changed(self, _idx: int = 0) -> None:
        self._render_chart1()

    @staticmethod
    def _ordinal_tick(i: int) -> str:
        circled = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
        return circled[i] if 0 <= i < len(circled) else str(i + 1)

    def _on_c1_hover(self, evt) -> None:
        tips = self._c1_hover_tips
        if not tips or not self.plot_c1.isVisible():
            return
        pos = evt[0] if isinstance(evt, (tuple, list)) else evt
        if not self.plot_c1.sceneBoundingRect().contains(pos):
            QToolTip.hideText()
            return
        mouse = self.plot_c1.plotItem.vb.mapSceneToView(pos)
        x = float(mouse.x())
        idx = int(round(x))
        if 0 <= idx < len(tips) and abs(x - idx) < 0.45:
            QToolTip.showText(QCursor.pos(), tips[idx], self.plot_c1)
        else:
            QToolTip.hideText()

    def _render_chart1(self) -> None:
        model = self._chart1
        self._c1_hover_tips = []
        if not model or not model.has_constraints:
            self.plot_c1.clear()
            self.tbl_c1.setVisible(False)
            return
        view = self.cb_view.currentData() or model.default_view
        t = current_tokens()
        if view == cv.VIEW_CONSTRAINT_LIST:
            self.plot_c1.setVisible(False)
            self.tbl_c1.setVisible(True)
            rows = model.list_rows
            self.tbl_c1.setRowCount(len(rows))
            for i, r in enumerate(rows):
                vals = [r.ctype, r.instance, r.pvt, r.key, r.detail]
                for j, val in enumerate(vals):
                    self.tbl_c1.setItem(i, j, QTableWidgetItem(val))
            return

        self.tbl_c1.setVisible(False)
        self.plot_c1.setVisible(True)
        self.plot_c1.clear()
        if view == cv.VIEW_REL_BARS:
            bars = model.rel_bars
            if not bars:
                return
            x = list(range(len(bars)))
            bw = 0.25
            base = [b.baseline if b.baseline is not None else 0 for b in bars]
            bvals = [b.b_value if b.b_value is not None else 0 for b in bars]
            tgts = [b.target if b.target is not None else 0 for b in bars]
            self.plot_c1.addItem(
                pg.BarGraphItem(x=[i - bw for i in x], height=base, width=bw, brush=t.MuteFog)
            )
            self.plot_c1.addItem(pg.BarGraphItem(x=x, height=bvals, width=bw, brush=t.TraceAmber))
            self.plot_c1.addItem(
                pg.BarGraphItem(x=[i + bw for i in x], height=tgts, width=bw, brush=t.PvtCyan)
            )
            ax = self.plot_c1.getAxis("bottom")
            ax.setTicks([[(i, self._ordinal_tick(i)) for i in x]])
            self.plot_c1.setTitle(tr("view.rel_bars"))
            tips = []
            for b in bars:
                dlt = f"{b.delta_pct:+.2f}%" if b.delta_pct is not None else "—"
                tips.append(
                    "\n".join(
                        [
                            "relative",
                            f"instance: {b.instance}",
                            f"pvt: {b.pvt}",
                            f"key: {b.key}",
                            f"baseline: {b.baseline}",
                            f"B: {b.b_value}",
                            f"target: {b.target}",
                            f"δ: {dlt}",
                        ]
                    )
                )
            self._c1_hover_tips = tips
        elif view == cv.VIEW_BOUND_CELLS:
            cells = model.bound_cells
            if not cells:
                return
            x = list(range(len(cells)))
            heights = [c.b_value if c.b_value is not None else 0 for c in cells]
            self.plot_c1.addItem(
                pg.BarGraphItem(x=x, height=heights, width=0.6, brush=t.TraceAmber)
            )
            for i, c in enumerate(cells):
                if c.bound is None:
                    continue
                self.plot_c1.plot(
                    [i - 0.4, i + 0.4],
                    [c.bound, c.bound],
                    pen=pg.mkPen(color=t.FailRose, width=2),
                )
            ax = self.plot_c1.getAxis("bottom")
            ax.setTicks([[(i, self._ordinal_tick(i)) for i in x]])
            self.plot_c1.setTitle(tr("view.bound_cells"))
            tips = []
            for c in cells:
                tips.append(
                    "\n".join(
                        [
                            f"bound ({c.op})",
                            f"instance: {c.instance}",
                            f"pvt: {c.pvt}",
                            f"key: {c.key}",
                            f"B: {c.b_value}",
                            f"bound: {c.bound} {c.unit}".strip(),
                        ]
                    )
                )
            self._c1_hover_tips = tips

    # ---- chart 2 ----
    def _pick_compare_db(self, which: str) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.open_db"), "/workspace/epc_fixtures", "SQLite (*.db)"
        )
        if not p:
            return
        if which == "ref":
            self._ref_db = p
        else:
            self._constructed_db = p
            self._b_db = p
        self._update_path_labels()
        self.refresh_free_compare()

    def _on_free_filter(self, _idx: int = 0) -> None:
        if self.cb_pvt.signalsBlocked() or self.cb_key.signalsBlocked():
            return
        self.refresh_free_compare(keep_selection=True)

    def refresh_free_compare(self, *, keep_selection: bool = False) -> None:
        pvt = self.cb_pvt.currentText() if keep_selection else None
        key = self.cb_key.currentText() if keep_selection else None
        # When PVT changes, don't force old key if invalid
        if keep_selection and not pvt:
            pvt = None
        self._free = cv.build_free_compare(
            ref_db=self._ref_db,
            constructed_db=self._constructed_db,
            pvt=pvt or None,
            key=key or None,
        )
        self._fill_free_combos()
        self._render_free_compare()

    def _fill_free_combos(self) -> None:
        model = self._free
        if model is None:
            return
        self.cb_pvt.blockSignals(True)
        self.cb_key.blockSignals(True)
        self.cb_pvt.clear()
        self.cb_pvt.addItems(model.pvt_options)
        if model.selected_pvt:
            i = self.cb_pvt.findText(model.selected_pvt)
            if i >= 0:
                self.cb_pvt.setCurrentIndex(i)
        self.cb_key.clear()
        self.cb_key.addItems(model.key_options)
        if model.selected_key:
            i = self.cb_key.findText(model.selected_key)
            if i >= 0:
                self.cb_key.setCurrentIndex(i)
        self.cb_pvt.blockSignals(False)
        self.cb_key.blockSignals(False)

    def _render_free_compare(self) -> None:
        model = self._free
        self.plot_c2.clear()
        self.plot_c2.addLegend(offset=(10, 10))
        if model is None:
            return
        if model.empty_reason:
            self.lbl_cover.setText("")
            self.lbl_delta.setText("")
            self.lbl_delta_mean.setText("")
            self.lbl_cover.setToolTip("")
            self.lbl_delta.setToolTip("")
            self.lbl_delta_mean.setToolTip("")
            self.plot_c2.setToolTip("")
            self.lbl_typical_note.clear()
            key_map = {
                "need_dbs": "free.need_dbs",
                "no_pvt": "free.no_pvt",
                "no_key": "free.no_key",
                "no_points": "free.no_points",
            }
            self.lbl_free_empty.setText(tr(key_map.get(model.empty_reason, "free.need_dbs")))
            return
        self.lbl_free_empty.setText("")
        self.lbl_typical_note.clear()
        tip_typ = tr("tip.typical")
        self.lbl_cover.setToolTip(tip_typ)
        self.lbl_delta.setToolTip(tip_typ)
        self.lbl_delta_mean.setToolTip(tip_typ)
        self.plot_c2.setToolTip(tip_typ)
        self.lbl_cover.setText(tr("free.cover", n=model.cover_n, m=model.cover_m))
        if model.delta_med_pct is None:
            self.lbl_delta.setText(tr("free.delta_na"))
        else:
            self.lbl_delta.setText(tr("free.delta_med", pct=model.delta_med_pct))
        if model.delta_mean_pct is None:
            self.lbl_delta_mean.setText(tr("free.delta_mean_na"))
        else:
            self.lbl_delta_mean.setText(tr("free.delta_mean", pct=model.delta_mean_pct))

        t = current_tokens()
        # Ref dashed/muted; constructed solid/accent
        xs_a, ys_a, xs_b, ys_b = [], [], [], []
        for p in model.points:
            if p.a_value is not None:
                xs_a.append(p.capacity)
                ys_a.append(p.a_value)
            if p.b_value is not None:
                xs_b.append(p.capacity)
                ys_b.append(p.b_value)
        if xs_a:
            self.plot_c2.plot(
                xs_a,
                ys_a,
                pen=pg.mkPen(color=t.MuteFog, width=1.5, style=Qt.PenStyle.DashLine),
                symbol="o",
                symbolSize=5,
                symbolBrush=t.MuteFog,
                name=tr("legend.ref"),
            )
        if xs_b:
            self.plot_c2.plot(
                xs_b,
                ys_b,
                pen=pg.mkPen(color=t.TraceAmber, width=2),
                symbol="o",
                symbolSize=6,
                symbolBrush=t.TraceAmber,
                name=tr("legend.constructed"),
            )
        self.plot_c2.setTitle(f"{model.selected_key} · {model.selected_pvt}")

    # ---- should aux ----
    def run_eval_h3(self) -> None:
        self.eval_log.clear()
        if not EVAL_H3.is_file():
            self.eval_log.setPlainText(f"missing {EVAL_H3}")
            return
        env = os.environ.copy()
        pp = env.get("PYTHONPATH", "")
        parts = [p for p in pp.split(os.pathsep) if p]
        if "/workspace" not in parts:
            parts.insert(0, "/workspace")
        env["PYTHONPATH"] = os.pathsep.join(parts)
        self.eval_log.appendPlainText(f"$ {sys.executable} {EVAL_H3}\n")
        try:
            p = subprocess.run(
                [sys.executable, str(EVAL_H3)],
                capture_output=True,
                text=True,
                env=env,
                cwd="/workspace",
                timeout=600,
            )
        except Exception as e:
            self.eval_log.appendPlainText(f"error: {e}")
            return
        self.eval_log.appendPlainText(p.stdout[-3000:])
        if p.stderr:
            self.eval_log.appendPlainText(p.stderr[-1500:])
        self.eval_log.appendPlainText(f"\nEXIT={p.returncode}")

    def _open_md(self, path: Path) -> None:
        if not path.is_file():
            self.eval_log.setPlainText(f"missing {path}")
            return
        try:
            QDesktopServices.openUrl(path.as_uri())
        except Exception:
            self.eval_log.setPlainText(path.read_text(encoding="utf-8", errors="replace")[:4000])

    def reapply_theme_plots(self) -> None:
        for pw in self._plot_widgets:
            configure_plot(pw)
        self._render_chart1()
        self._render_free_compare()

    # Back-compat shims used by older capture scripts (no-op / redirected)
    @property
    def key_list(self):
        return _ShimList()

    def refresh_trend(self) -> None:
        self.refresh_free_compare()

    def refresh_aux(self) -> None:
        self.refresh_chart1()


class _ShimList:
    """Minimal stand-in so legacy capture scripts do not crash."""

    def count(self) -> int:
        return 0

    def item(self, _i: int):
        return None
