"""Page A — job config, constraint preview, dry-run, history, embedded run."""
from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from epc_gui.i18n import tr
from epc_gui.services import history as hist_svc
from epc_gui.services import yaml_io
from epc_gui.services.job_runner import JobRunner
from epc_gui.services.sugar import dry_run_precheck, expand_from_path, expand_from_yaml_text
from epc_gui.theme import current_tokens
from epc_gui.paths import fixtures_root


class ConfigPage(QWidget):
    job_finished = pyqtSignal(int, str, str)  # exit, db_path, audit_path
    request_preview = pyqtSignal(str)
    history_open = pyqtSignal(dict)  # entry → shell may open audit/db

    def __init__(self, parent=None):
        super().__init__(parent)
        self._yaml_path: Path | None = None
        self._data: dict = {}
        self.runner = JobRunner(self)
        self.runner.output.connect(self._append_log)
        self.runner.finished.connect(self._on_finished)
        self.runner.started.connect(lambda: self._set_running(True))

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        self.title = QLabel("")
        self.title.setObjectName("Title")
        root.addWidget(self.title)
        # disc removed (DEMO disclaimer) — no empty placeholder

        row = QHBoxLayout()
        self._shortcut_btns: dict[str, QPushButton] = {}
        for key in ("sample", "p1_green", "p2_geom_green", "p2_geom_residual_h3hard_red"):
            b = QPushButton("")
            b.clicked.connect(lambda _=False, k=key: self.load_shortcut(k))
            self._shortcut_btns[key] = b
            row.addWidget(b)
        row.addStretch(1)
        root.addLayout(row)

        # Layout A: single vertical column — form → YAML → run → constraints → history
        self.band_job = QGroupBox("")
        form = QFormLayout(self.band_job)
        self.ed_job = QLineEdit()
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(list(yaml_io.MODES))
        self.ed_source = QLineEdit()
        self.ed_out_db = QLineEdit()
        self.ed_audit = QLineEdit()
        self.cb_backend = QComboBox()
        self.cb_backend.addItems(["idw_nn", "residual_gbdt"])
        self.lbl_gates = QLabel("")
        self.lbl_gates.setObjectName("Mute")
        form.addRow("job_name", self.ed_job)
        form.addRow("mode", self.cb_mode)
        form.addRow("source.db", self._path_row(self.ed_source))
        form.addRow("output.db", self._path_row(self.ed_out_db, save=True))
        form.addRow("audit.md", self._path_row(self.ed_audit, save=True))
        form.addRow("construct.backend", self.cb_backend)
        form.addRow("gates", self.lbl_gates)
        root.addWidget(self.band_job)

        self.yband = QGroupBox("")
        yv = QVBoxLayout(self.yband)
        self.yaml_edit = QPlainTextEdit()
        self.yaml_edit.setObjectName("YamlEditor")
        self.yaml_edit.setMinimumHeight(140)
        yv.addWidget(self.yaml_edit)
        brow = QHBoxLayout()
        self.btn_open = QPushButton("")
        self.btn_save = QPushButton("")
        self.btn_save_as = QPushButton("")
        self.btn_apply = QPushButton("")
        self.btn_open.clicked.connect(self.open_yaml_dialog)
        self.btn_save.clicked.connect(lambda: self.save_yaml(save_as=False))
        self.btn_save_as.clicked.connect(lambda: self.save_yaml(save_as=True))
        self.btn_apply.clicked.connect(self.sync_form_into_yaml)
        brow.addWidget(self.btn_open)
        brow.addWidget(self.btn_save)
        brow.addWidget(self.btn_save_as)
        brow.addWidget(self.btn_apply)
        brow.addStretch(1)
        yv.addLayout(brow)
        root.addWidget(self.yband, stretch=2)

        runrow = QHBoxLayout()
        self.btn_dry = QPushButton("")
        self.btn_run = QPushButton("")
        self.btn_run.setObjectName("Primary")
        self.btn_stop = QPushButton("")
        self.btn_stop.setObjectName("Danger")
        self.btn_stop.setEnabled(False)
        self.lbl_exit = QLabel("")
        self.lbl_exit.setObjectName("Mute")
        self.lbl_disk = QLabel("")
        self.lbl_dry = QLabel("")
        self.lbl_dry.setWordWrap(True)
        self.btn_dry.clicked.connect(self.dry_run)
        self.btn_run.clicked.connect(self.run_job)
        self.btn_stop.clicked.connect(self.runner.stop)
        runrow.addWidget(self.btn_dry)
        runrow.addWidget(self.btn_run)
        runrow.addWidget(self.btn_stop)
        runrow.addWidget(self.lbl_exit)
        runrow.addWidget(self.lbl_disk)
        runrow.addStretch(1)
        root.addLayout(runrow)
        root.addWidget(self.lbl_dry)

        # Constraint preview — full width, collapsible, under YAML / run
        self.sugar = QGroupBox("")
        self.sugar.setCheckable(True)
        self.sugar.setChecked(True)
        sv = QVBoxLayout(self.sugar)
        self.lbl_sugar = QLabel("")
        self.lbl_sugar.setObjectName("Mute")
        self.lbl_sugar.setWordWrap(True)
        self.lbl_sugar.hide()  # only shown on empty/fail; no metadata summary bar
        sv.addWidget(self.lbl_sugar)
        self.sugar_table = QTableWidget(0, 5)
        self.sugar_table.setHorizontalHeaderLabels(
            ["instance", "pvt", "key", "delta_pct", "sugar_origin"]
        )
        self.sugar_table.setAlternatingRowColors(True)
        self.sugar_table.horizontalHeader().setStretchLastSection(True)
        self.sugar_table.setMaximumHeight(160)
        self.sugar_table.setMinimumHeight(80)
        sv.addWidget(self.sugar_table)
        srow = QHBoxLayout()
        self.btn_refresh_sugar = QPushButton("")
        self.btn_refresh_sugar.clicked.connect(self.refresh_sugar)
        srow.addWidget(self.btn_refresh_sugar)
        srow.addStretch(1)
        sv.addLayout(srow)
        root.addWidget(self.sugar)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(100)
        root.addWidget(self.log)

        # History — narrow bottom strip (not side-by-side with constraints)
        self.hist = QGroupBox("")
        hv = QHBoxLayout(self.hist)
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(88)
        self.history_list.setMinimumHeight(64)
        self.history_list.itemDoubleClicked.connect(self._on_history_click)
        self.history_list.itemClicked.connect(self._on_history_click)
        hv.addWidget(self.history_list, stretch=1)
        self.btn_hist_reload = QPushButton("")
        self.btn_hist_reload.setFixedWidth(72)
        self.btn_hist_reload.clicked.connect(self.reload_history)
        hv.addWidget(self.btn_hist_reload)
        root.addWidget(self.hist)

        self.retranslate()
        self.reload_history()
        if yaml_io.FIXTURE_SHORTCUTS["sample"].is_file():
            self.load_shortcut("sample")

    def retranslate(self) -> None:
        self.title.setText(tr("config.title"))
        self._shortcut_btns["sample"].setText(tr("shortcut.sample"))
        self._shortcut_btns["p1_green"].setText(tr("shortcut.p1_green"))
        self._shortcut_btns["p2_geom_green"].setText(tr("shortcut.p2_geom_green"))
        self._shortcut_btns["p2_geom_residual_h3hard_red"].setText(tr("shortcut.h3hard_red"))
        self.band_job.setTitle(tr("group.job"))
        self.yband.setTitle(tr("group.yaml"))
        self.yband.setToolTip(tr("tip.yaml"))
        self.sugar.setTitle(tr("group.expand"))
        self.sugar.setToolTip(tr("tip.expand"))
        self.hist.setTitle(tr("group.history"))
        self.lbl_gates.setText(tr("gates.read_only"))
        self.lbl_gates.setToolTip(tr("tip.gates"))
        self.btn_open.setText(tr("btn.open"))
        self.btn_save.setText(tr("btn.save"))
        self.btn_save_as.setText(tr("btn.save_as"))
        self.btn_apply.setText(tr("btn.sync_form"))
        self.btn_apply.setToolTip(tr("tip.sync_form"))
        self.btn_refresh_sugar.setText(tr("btn.refresh"))
        self.btn_hist_reload.setText(tr("btn.refresh"))
        self.btn_dry.setText(tr("btn.dry_run"))
        self.btn_dry.setToolTip(tr("tip.dry_run"))
        self.btn_run.setText(tr("btn.run"))
        self.btn_stop.setText(tr("btn.stop"))
        self.log.setPlaceholderText(tr("placeholder.engine_log"))
        txt = self.lbl_exit.text()
        idle_marks = {"", "EXIT —", "EXIT …", "EXIT ...", tr("exit.idle"), tr("exit.running")}
        if txt in idle_marks or (txt.startswith("EXIT") and not any(c.isdigit() for c in txt)):
            if "…" not in txt and "..." not in txt:
                self.lbl_exit.setText(tr("exit.idle"))

    def _path_row(self, edit: QLineEdit, save: bool = False) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(edit, stretch=1)
        b = QPushButton("…")
        b.setFixedWidth(32)

        def browse():
            if save:
                p, _ = QFileDialog.getSaveFileName(
                    self, tr("dialog.choose_path"), edit.text() or str(fixtures_root())
                )
            else:
                p, _ = QFileDialog.getOpenFileName(
                    self, tr("dialog.choose_file"), edit.text() or str(fixtures_root())
                )
            if p:
                edit.setText(p)

        b.clicked.connect(browse)
        h.addWidget(b)
        return w

    def load_shortcut(self, key: str) -> None:
        self.load_yaml_path(yaml_io.FIXTURE_SHORTCUTS[key])

    def load_yaml_path(self, path: Path | str) -> None:
        p = Path(path)
        data = yaml_io.load_yaml(p)
        conflict = yaml_io.mode_conflict_message(data)
        self._yaml_path = p
        self._data = data
        self.yaml_edit.setPlainText(p.read_text(encoding="utf-8"))
        self._fill_form(data)
        if conflict:
            self._append_log(tr("log.reject_hint", msg=conflict))
        self.refresh_sugar()

    def _fill_form(self, data: dict) -> None:
        self.ed_job.setText(str(data.get("job_name", "")))
        mode = yaml_io.effective_mode(data)
        idx = self.cb_mode.findText(mode)
        if idx >= 0:
            self.cb_mode.setCurrentIndex(idx)
        src = (data.get("source") or {}).get("db_path", "")
        self.ed_source.setText(str(src))
        out = data.get("output") or {}
        self.ed_out_db.setText(str(out.get("db_path", "")))
        self.ed_audit.setText(str(out.get("audit_report_path", "")))
        backend = (data.get("construct") or {}).get("backend", "idw_nn")
        bi = self.cb_backend.findText(str(backend))
        if bi >= 0:
            self.cb_backend.setCurrentIndex(bi)

    def sync_form_into_yaml(self) -> None:
        try:
            data = yaml_io.load_yaml_text(self.yaml_edit.toPlainText())
        except Exception as e:
            self._append_log(tr("log.yaml_err", error=e))
            return
        data["job_name"] = self.ed_job.text().strip()
        data["mode"] = self.cb_mode.currentText()
        data.setdefault("source", {})["db_path"] = self.ed_source.text().strip()
        data.setdefault("output", {})["db_path"] = self.ed_out_db.text().strip()
        data.setdefault("output", {})["audit_report_path"] = self.ed_audit.text().strip()
        data.setdefault("construct", {})["backend"] = self.cb_backend.currentText()
        data.setdefault("gates", {})["on_violation"] = "fail_job"
        data.setdefault("gates", {})["require_constraint_satisfaction"] = True
        self.yaml_edit.setPlainText(yaml_io.dump_yaml_text(data))
        self._data = data

    def open_yaml_dialog(self) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.open_yaml"), str(fixtures_root()), "YAML (*.yaml *.yml)"
        )
        if p:
            self.load_yaml_path(p)

    def save_yaml(self, save_as: bool = False) -> None:
        path = self._yaml_path
        if save_as or path is None:
            p, _ = QFileDialog.getSaveFileName(
                self,
                tr("dialog.save_yaml"),
                str(path or (fixtures_root() / "epc_job.gui.yaml")),
                "YAML (*.yaml)",
            )
            if not p:
                return
            path = Path(p)
        try:
            data = yaml_io.load_yaml_text(self.yaml_edit.toPlainText())
        except Exception as e:
            self._append_log(tr("log.yaml_err", error=e))
            return
        yaml_io.save_yaml(path, data)
        self._yaml_path = path
        self._data = data
        self._append_log(tr("log.saved", path=path))
        hist_svc.append_history(
            {
                "event": "save_as" if save_as else "save",
                "yaml": str(path),
                "mode": yaml_io.effective_mode(data),
                "EXIT": None,
                "audit": str((data.get("output") or {}).get("audit_report_path", "")),
                "db": str((data.get("output") or {}).get("db_path", "")),
            }
        )
        self.reload_history()
        self.refresh_sugar()

    def refresh_sugar(self) -> None:
        t = current_tokens()
        text = self.yaml_edit.toPlainText()
        if self._yaml_path and self._yaml_path.is_file():
            try:
                on_disk = self._yaml_path.read_text(encoding="utf-8")
            except Exception:
                on_disk = ""
            if text.strip() == on_disk.strip():
                res = expand_from_path(self._yaml_path)
            else:
                res = expand_from_yaml_text(text)
        else:
            res = expand_from_yaml_text(text) if text.strip() else None
        if res is None:
            self.lbl_sugar.setText(tr("sugar.empty"))
            self.lbl_sugar.setStyleSheet(f"color: {t.MuteFog};")
            self.lbl_sugar.show()
            self.sugar_table.setRowCount(0)
            return
        if not res.ok:
            self.lbl_sugar.setText(tr("sugar.fail", error=res.error))
            self.lbl_sugar.setStyleSheet(f"color: {t.FailRose};")
            self.lbl_sugar.show()
            self.sugar_table.setRowCount(0)
            return
        # success: no metadata microcopy bar
        self.lbl_sugar.hide()
        self.lbl_sugar.clear()
        rows = res.relative_rows or []
        self.sugar_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [
                r.instance,
                r.pvt,
                r.key,
                "" if r.delta_pct is None else str(r.delta_pct),
                r.sugar_origin or "",
            ]
            for j, v in enumerate(vals):
                self.sugar_table.setItem(i, j, QTableWidgetItem(v))

    def dry_run(self) -> None:
        self.sync_form_into_yaml()
        text = self.yaml_edit.toPlainText()
        try:
            data = yaml_io.load_yaml_text(text)
        except Exception as e:
            self.lbl_dry.setText(tr("dry.fail", error=e))
            self.lbl_dry.setStyleSheet(f"color: {current_tokens().FailRose};")
            return
        conflict = yaml_io.mode_conflict_message(data)
        if conflict:
            self.lbl_dry.setText(tr("dry.fail", error=conflict))
            self.lbl_dry.setStyleSheet(f"color: {current_tokens().FailRose};")
            self._append_log(tr("log.dry_tag", msg=conflict))
            return
        out_db = Path(str((data.get("output") or {}).get("db_path", "") or ""))
        before = out_db.is_file() if str(out_db) else False
        mtime_before = out_db.stat().st_mtime if before else None
        res = dry_run_precheck(yaml_text=text)
        after = out_db.is_file() if str(out_db) else False
        mtime_after = out_db.stat().st_mtime if after else None
        wrote = (not before and after) or (
            before and after and mtime_before is not None and mtime_after is not None and mtime_after > mtime_before
        )
        if wrote:
            self.lbl_dry.setText(tr("dry.wrote_db"))
            self.lbl_dry.setStyleSheet(f"color: {current_tokens().FailRose};")
            return
        if not res.ok:
            self.lbl_dry.setText(tr("dry.fail", error=res.error))
            self.lbl_dry.setStyleSheet(f"color: {current_tokens().FailRose};")
            self._append_log(tr("log.dry_fail", error=res.error))
            return
        self.lbl_dry.setText(tr("dry.pass"))
        self.lbl_dry.setStyleSheet(f"color: {current_tokens().MuteFog};")
        self._append_log(
            tr(
                "log.dry_pass",
                mode=res.mode,
                backend=res.backend,
                c=res.constraint_count,
                n=res.expanded_constraint_count,
            )
        )
        self.refresh_sugar()

    def run_job(self) -> None:
        self.sync_form_into_yaml()
        try:
            data = yaml_io.load_yaml_text(self.yaml_edit.toPlainText())
        except Exception as e:
            self._append_log(tr("log.yaml_err", error=e))
            return
        conflict = yaml_io.mode_conflict_message(data)
        if conflict:
            self._append_log(tr("log.reject", msg=conflict))
            return
        path = self._yaml_path or fixtures_root() / "_gui_last_job.yaml"
        yaml_io.save_yaml(path, data)
        self._yaml_path = path
        self._data = data
        self.log.clear()
        self.lbl_exit.setText(tr("exit.running"))
        self.lbl_disk.setText("")
        self._append_log(f"$ python -m epc_engine {path}\n")
        self.runner.start(path)

    def _set_running(self, running: bool) -> None:
        self.btn_run.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_dry.setEnabled(not running)

    def _append_log(self, text: str) -> None:
        self.log.moveCursor(self.log.textCursor().MoveOperation.End)
        self.log.insertPlainText(text)
        self.log.moveCursor(self.log.textCursor().MoveOperation.End)

    def _on_finished(self, code: int) -> None:
        self._set_running(False)
        out = self._data.get("output") or {}
        db_path = str(out.get("db_path", ""))
        audit_path = str(out.get("audit_report_path", ""))
        self.lbl_exit.setText(tr("exit.code", code=code))
        # EXIT / 已落盘: neutral mono; true pass/fail only via lamps elsewhere
        mono = (
            f"color: {current_tokens().MuteFog}; "
            "font-family: IBM Plex Mono, DejaVu Sans Mono, monospace;"
        )
        if code == 0:
            self.lbl_exit.setObjectName("StatusMono")
            self.lbl_exit.setStyleSheet(mono)
            exists = Path(db_path).is_file() if db_path else False
            self.lbl_disk.setText(tr("disk.written") if exists else tr("disk.pass_no_db"))
            self.lbl_disk.setStyleSheet(mono)
            if exists:
                self.request_preview.emit(db_path)
        else:
            self.lbl_exit.setObjectName("StatusMono")
            self.lbl_exit.setStyleSheet(mono)
            exists = Path(db_path).is_file() if db_path else False
            self.lbl_disk.setText(tr("disk.fail_but_db") if exists else tr("disk.not_written"))
            self.lbl_disk.setStyleSheet(mono)
        hist_svc.append_history(
            {
                "event": "run",
                "yaml": str(self._yaml_path or ""),
                "mode": yaml_io.effective_mode(self._data),
                "EXIT": code,
                "audit": audit_path,
                "db": db_path,
            }
        )
        self.reload_history()
        self.job_finished.emit(code, db_path, audit_path)

    def reload_history(self) -> None:
        self.history_list.clear()
        for e in reversed(hist_svc.load_history(40)):
            ts = e.get("ts", "")
            mode = e.get("mode", "")
            ex = e.get("EXIT", "—")
            y = Path(str(e.get("yaml", ""))).name
            item = QListWidgetItem(f"{ts}  {y}  {mode}  EXIT={ex}")
            item.setData(Qt.UserRole, e)
            self.history_list.addItem(item)

    def _on_history_click(self, item: QListWidgetItem) -> None:
        e = item.data(Qt.UserRole) or {}
        y = e.get("yaml")
        if y and Path(y).is_file():
            self.load_yaml_path(y)
        self.history_open.emit(dict(e))

    def current_paths(self) -> tuple[str, str, str]:
        return (
            self.ed_source.text().strip(),
            self.ed_out_db.text().strip(),
            self.ed_audit.text().strip(),
        )
