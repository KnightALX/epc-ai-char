"""Portable paths: no hard-coded /workspace (cluster-safe)."""
from __future__ import annotations

import os
import re
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
_WIN_WORKSPACE = re.compile(r"^[A-Za-z]:/workspace/")


def repo_root() -> Path:
    """Repository root containing epc_gui/ (+ usually epc_engine/, epc_fixtures/)."""
    env = os.environ.get("EPC_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    parent = PACKAGE_DIR.parent
    if (parent / "epc_fixtures").is_dir() or (parent / "epc_engine").is_dir():
        return parent
    for p in PACKAGE_DIR.parents:
        if (p / "epc_fixtures").is_dir() and (p / "epc_gui").is_dir():
            return p
    return parent


def fixtures_root() -> Path:
    """DEMO / fixture tree. Prefer env EPC_FIXTURES_ROOT, else <repo>/epc_fixtures."""
    env = os.environ.get("EPC_FIXTURES_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return repo_root() / "epc_fixtures"


def portable(p: str | Path) -> Path:
    """Rebase legacy ``/workspace/...`` cluster paths onto this machine's repo root.

    Mirrors :func:`epc_engine.paths.portable` so GUI-side filesystem checks agree
    with the engine subprocess (the engine rebases the same way at job load).
    Non-``/workspace`` paths pass through untouched.
    """
    s = str(p)
    root = repo_root()
    marker = "/workspace/"
    if s.startswith(marker):
        return (root / s[len(marker):]).resolve()
    if _WIN_WORKSPACE.match(s):
        rest = s[s.index(marker) + len(marker):]
        return (root / rest).resolve()
    return Path(s)
