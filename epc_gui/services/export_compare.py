"""Export T0 PNG + CSV under epc_gui/exports/."""
from __future__ import annotations

import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable

from epc_gui.paths import PACKAGE_DIR

EXPORT_DIR = PACKAGE_DIR / "exports"
_SHANGHAI = timezone(timedelta(hours=8))


def _stamp() -> str:
    return datetime.now(_SHANGHAI).strftime("%Y%m%d_%H%M%S")


def ensure_export_dir() -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    return EXPORT_DIR


def write_csv(rows: Iterable[dict], path: Path | None = None) -> Path:
    ensure_export_dir()
    path = path or (EXPORT_DIR / f"t0_compare_{_stamp()}.csv")
    rows = list(rows)
    fields = ["capacity", "instance", "pvt", "key", "typical"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return path


def grab_widget_png(widget, path: Path | None = None) -> Path:
    ensure_export_dir()
    path = path or (EXPORT_DIR / f"t0_compare_{_stamp()}.png")
    pix = widget.grab()
    if not pix.save(str(path), "PNG"):
        raise RuntimeError(f"failed to save PNG {path}")
    return path
