"""Portable path resolution: legacy /workspace paths → repo root.

The shipped fixtures hardcode ``/workspace/...`` (the Linux CI checkout root).
On any other machine — notably Windows, where ``/workspace/x`` resolves to
``<drive>:/workspace/x`` — those paths must rebase onto the repository root.
This module is the single rebase point for the engine and fixture scripts.
``EPC_REPO_ROOT`` overrides auto-detection.

Rebase rule:
- ``/workspace/rest`` (also Windows ``<drive>:/workspace/rest``) → ``<repo_root>/rest``
- anything else → unchanged.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

_WIN_WORKSPACE = re.compile(r"^[A-Za-z]:/workspace/")


def repo_root() -> Path:
    """Repository root containing epc_engine/ (+ epc_fixtures/, epc_gui/)."""
    env = os.environ.get("EPC_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    parent = PACKAGE_DIR.parent
    if (parent / "epc_fixtures").is_dir() or (parent / "epc_engine").is_dir():
        return parent
    for p in PACKAGE_DIR.parents:
        if (p / "epc_fixtures").is_dir() and (p / "epc_engine").is_dir():
            return p
    return parent


def portable(p: str | Path) -> Path:
    """Rebase legacy ``/workspace/...`` onto repo_root(); other paths unchanged."""
    s = str(p)
    low = s.replace("\\", "/")
    if low.startswith("/workspace/"):
        return (repo_root() / s[len("/workspace/"):]).resolve()
    m = _WIN_WORKSPACE.match(low)
    if m:
        return (repo_root() / s[m.end():]).resolve()
    return Path(p)
