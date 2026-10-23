"""Portable paths: no hard-coded /workspace (cluster-safe)."""
from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent


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
