"""Persist job history + GUI settings under epc_gui/state/."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from epc_gui.paths import PACKAGE_DIR

STATE_DIR = PACKAGE_DIR / "state"
HISTORY_PATH = STATE_DIR / "job_history.json"
SETTINGS_PATH = STATE_DIR / "settings.json"
_SHANGHAI = timezone(timedelta(hours=8))


def _ensure_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_history(limit: int = 50) -> list[dict[str, Any]]:
    _ensure_dir()
    if not HISTORY_PATH.is_file():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return data[-limit:]


def append_history(entry: dict[str, Any]) -> None:
    _ensure_dir()
    items = load_history(limit=500)
    row = dict(entry)
    if "ts" not in row:
        row["ts"] = datetime.now(_SHANGHAI).strftime("%Y-%m-%d %H:%M:%S Asia/Shanghai")
    items.append(row)
    HISTORY_PATH.write_text(
        json.dumps(items[-200:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_settings() -> dict[str, Any]:
    _ensure_dir()
    defaults = {"theme": "light", "locale": "zh"}
    if not SETTINGS_PATH.is_file():
        return dict(defaults)
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return dict(defaults)
    if not isinstance(data, dict):
        return dict(defaults)
    out = dict(defaults)
    out.update(data)
    loc = str(out.get("locale", "zh")).lower()
    out["locale"] = "en" if loc.startswith("en") else "zh"
    theme = str(out.get("theme", "dark")).lower()
    out["theme"] = "light" if theme.startswith("light") else "dark"
    return out


def save_settings(data: dict[str, Any]) -> None:
    _ensure_dir()
    cur = load_settings()
    cur.update(data)
    loc = str(cur.get("locale", "zh")).lower()
    cur["locale"] = "en" if loc.startswith("en") else "zh"
    theme = str(cur.get("theme", "dark")).lower()
    cur["theme"] = "light" if theme.startswith("light") else "dark"
    SETTINGS_PATH.write_text(
        json.dumps(cur, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
