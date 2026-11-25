"""Unit tests: epc_engine.paths — legacy /workspace rebase (portability)."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from epc_engine.paths import portable, repo_root

from conftest import REPO


def test_repo_root_detection():
    assert repo_root() == REPO


def test_repo_root_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("EPC_REPO_ROOT", str(tmp_path))
    assert repo_root() == tmp_path.resolve()


def test_portable_rebases_posix_workspace():
    assert portable("/workspace/epc_fixtures/A_ref.db") == (
        REPO / "epc_fixtures" / "A_ref.db"
    ).resolve()


def test_portable_rebases_windows_workspace():
    assert portable("D:/workspace/epc_fixtures/A_ref.db") == (
        REPO / "epc_fixtures" / "A_ref.db"
    ).resolve()


def test_portable_rebases_backslash_windows_workspace():
    assert portable(r"D:\workspace\epc_fixtures\A_ref.db") == (
        REPO / "epc_fixtures" / "A_ref.db"
    ).resolve()


def test_portable_leaves_relative_untouched():
    assert portable("some/rel/path.db") == Path("some/rel/path.db")


def test_portable_leaves_other_absolute_untouched():
    p = portable(str(Path.cwd() / "x.db"))
    assert p == Path(str(Path.cwd() / "x.db"))


def test_portable_env_root_respected(tmp_path, monkeypatch):
    monkeypatch.setenv("EPC_REPO_ROOT", str(tmp_path))
    assert portable("/workspace/a/b.db") == (tmp_path / "a" / "b.db").resolve()
