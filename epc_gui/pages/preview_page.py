"""Page B — read-only output db preview."""
from __future__ import annotations

from pathlib import Path

from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import (
    CardWidget,
    CaptionLabel,
    ComboBox,
    PushButton,
    TableWidget,
    TitleLabel,
)

from epc_gui.i18n import tr
from epc_gui.services.db_reader import CharDb
from epc_gui.paths import fixtures_root


class PreviewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._db_path: str | None = None
        self._offset = 0
        self._page_size = 80
        self._distinct_inst: list[str] = []
        self._distinct_pvt: list[str] = []
        self._distinct_key: list[str] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        self.title = TitleLabel("")
        root.addWidget(self.title)

        row = QHBoxLayout()
        self.lbl_path = CaptionLabel("")
        self.btn_open = PushButton("")
        self.btn_open.clicked.connect(self.browse_db)
        row.addWidget(self.lbl_path, stretch=1)
        row.addWidget(self.btn_open)
        root.addLayout(row)

        self.filt = CardWidget()
        fh = QHBoxLayout(self.filt)
        # Fluent CardWidget has no group-box title; a leading caption keeps the
        # band title visible and locale-driven (see retranslate).
        self.lbl_filt = CaptionLabel("")
        fh.addWidget(self.lbl_filt)
        self.cb_inst = ComboBox()
        self.cb_pvt = ComboBox()
        self.cb_key = ComboBox()
        for cb in (self.cb_inst, self.cb_pvt, self.cb_key):
            cb.setMinimumWidth(160)
            cb.currentIndexChanged.connect(self._reload)
        fh.addWidget(QLabel("instance"))
        fh.addWidget(self.cb_inst, stretch=1)
        fh.addWidget(QLabel("pvt"))
        fh.addWidget(self.cb_pvt, stretch=1)
        fh.addWidget(QLabel("key"))
        fh.addWidget(self.cb_key, stretch=1)
        root.addWidget(self.filt)

        # 1.11.3 TableWidget.__init__(parent=None) has no (rows, cols) overload
        self.table = TableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["instance", "pvt", "field_key", "value"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellClicked.connect(self._on_cell)
        root.addWidget(self.table, stretch=1)

        nav = QHBoxLayout()
        self.btn_prev = PushButton("")
        self.btn_next = PushButton("")
        self.lbl_page = CaptionLabel("")
        self.btn_prev.clicked.connect(self._prev)
        self.btn_next.clicked.connect(self._next)
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)
        nav.addWidget(self.lbl_page)
        nav.addStretch(1)
        root.addLayout(nav)

        self.matrix = TableWidget(self)
        self.matrix.setRowCount(0)
        self.matrix.setColumnCount(0)
        self.matrix.setMaximumHeight(200)
        self.matrix.setToolTip("")
        root.addWidget(self.matrix)

        self.retranslate()

    def retranslate(self) -> None:
        self.title.setText(tr("preview.title"))
        if not self._db_path:
            self.lbl_path.setText(tr("preview.not_open"))
        self.btn_open.setText(tr("preview.open_db"))
        self.lbl_filt.setText(tr("preview.filter"))
        self.btn_prev.setText(tr("btn.prev"))
        self.btn_next.setText(tr("btn.next"))
        self.matrix.setToolTip(tr("tip.matrix"))
        # Refresh "All" combo labels without losing selection
        if self._db_path:
            self._refill_combos_keep_selection()

    def _all_label(self) -> str:
        return tr("filter.all")

    def _refill_combos_keep_selection(self) -> None:
        def refill(cb: ComboBox, items: list[str]) -> None:
            prev = cb.currentText()
            was_all = prev in ("全部", "All", "全部 / All", self._all_label()) or not prev
            cb.blockSignals(True)
            cb.clear()
            cb.addItems([self._all_label()] + items)
            if was_all:
                cb.setCurrentIndex(0)
            else:
                i = cb.findText(prev)
                cb.setCurrentIndex(i if i >= 0 else 0)
            cb.blockSignals(False)

        refill(self.cb_inst, self._distinct_inst)
        refill(self.cb_pvt, self._distinct_pvt)
        refill(self.cb_key, self._distinct_key)

    def open_db(self, path: str) -> None:
        p = Path(path)
        if not p.is_file():
            self.lbl_path.setText(tr("preview.missing", path=path))
            return
        self._db_path = str(p)
        self.lbl_path.setText(str(p))
        self._offset = 0
        with CharDb(p) as db:
            self._distinct_inst = db.distinct("instance")
            self._distinct_pvt = db.distinct("pvt")
            self._distinct_key = db.distinct("field_key")
            self._fill_combo(self.cb_inst, [self._all_label()] + self._distinct_inst)
            self._fill_combo(self.cb_pvt, [self._all_label()] + self._distinct_pvt)
            self._fill_combo(self.cb_key, [self._all_label()] + self._distinct_key)
            self.lbl_page.setText(f"COUNT={db.count()}")
        self._reload()

    def browse_db(self) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.open_db"), str(fixtures_root()), "SQLite (*.db)"
        )
        if p:
            self.open_db(p)

    @staticmethod
    def _fill_combo(cb: ComboBox, items: list[str]) -> None:
        cb.blockSignals(True)
        cb.clear()
        cb.addItems(items)
        cb.blockSignals(False)

    def _filt(self) -> tuple[str | None, str | None, str | None]:
        all_labels = {tr("filter.all"), "全部", "All", "全部 / All"}

        def v(cb: ComboBox) -> str | None:
            t = cb.currentText()
            return None if (not t or t in all_labels) else t

        return v(self.cb_inst), v(self.cb_pvt), v(self.cb_key)

    def _reload(self) -> None:
        if not self._db_path:
            return
        inst, pvt, key = self._filt()
        with CharDb(self._db_path) as db:
            rows = db.page(
                instance=inst, pvt=pvt, key=key, offset=self._offset, limit=self._page_size
            )
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, col in enumerate(("instance", "pvt", "field_key", "value")):
                item = QTableWidgetItem(str(r[col])[:200])
                self.table.setItem(i, j, item)
        self.lbl_page.setText(
            f"offset={self._offset}  rows={len(rows)}  path={self._db_path}"
        )

    def _prev(self) -> None:
        self._offset = max(0, self._offset - self._page_size)
        self._reload()

    def _next(self) -> None:
        self._offset += self._page_size
        self._reload()

    def _on_cell(self, row: int, _col: int) -> None:
        val_item = self.table.item(row, 3)
        if not val_item:
            return
        toks = val_item.text().split()
        n = int(len(toks) ** 0.5)
        if n * n == len(toks) and n > 1:
            self.matrix.setRowCount(n)
            self.matrix.setColumnCount(n)
            for i in range(n):
                for j in range(n):
                    self.matrix.setItem(i, j, QTableWidgetItem(toks[i * n + j]))
        else:
            self.matrix.setRowCount(1)
            self.matrix.setColumnCount(len(toks) or 1)
            for j, t in enumerate(toks or ["empty"]):
                self.matrix.setItem(0, j, QTableWidgetItem(t))
