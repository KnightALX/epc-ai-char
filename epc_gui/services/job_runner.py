"""Embedded subprocess runner for python -m epc_engine <yaml>."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from PyQt5.QtCore import QObject, QProcess, pyqtSignal

from epc_gui.paths import repo_root


@dataclass
class RunResult:
    exit_code: int
    stdout: str
    stderr: str
    yaml_path: str


def _ensure_repo_on_pythonpath(env_lines_or_dict, *, as_qprocess_list: bool) -> object:
    root = str(repo_root())
    if as_qprocess_list:
        env = list(env_lines_or_dict)
        extras = [root]
        merged = False
        out_env = []
        for line in env:
            if line.startswith("PYTHONPATH="):
                val = line.split("=", 1)[1]
                parts = [p for p in val.split(os.pathsep) if p]
                for e in extras:
                    if e not in parts:
                        parts.insert(0, e)
                out_env.append("PYTHONPATH=" + os.pathsep.join(parts))
                merged = True
            else:
                out_env.append(line)
        if not merged:
            out_env.append("PYTHONPATH=" + os.pathsep.join(extras))
        return out_env
    env = dict(env_lines_or_dict)
    pp = env.get("PYTHONPATH", "")
    parts = [p for p in pp.split(os.pathsep) if p]
    if root not in parts:
        parts.insert(0, root)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


class JobRunner(QObject):
    output = pyqtSignal(str)
    finished = pyqtSignal(int)  # exit code
    started = pyqtSignal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._proc = QProcess(self)
        self._proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._on_out)
        self._proc.finished.connect(self._on_finished)
        self._yaml = ""

    @property
    def running(self) -> bool:
        return self._proc.state() != QProcess.ProcessState.NotRunning

    def start(self, yaml_path: str | Path, *, python: str | None = None) -> None:
        if self.running:
            raise RuntimeError("job already running")
        y = str(Path(yaml_path).resolve())
        self._yaml = y
        py = python or sys.executable
        out_env = _ensure_repo_on_pythonpath(QProcess.systemEnvironment(), as_qprocess_list=True)
        self._proc.setEnvironment(out_env)
        self._proc.setWorkingDirectory(str(repo_root()))
        self.started.emit()
        self._proc.start(py, ["-m", "epc_engine", y])

    def stop(self) -> None:
        if self.running:
            self._proc.kill()

    def _on_out(self) -> None:
        data = bytes(self._proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        if data:
            self.output.emit(data)

    def _on_finished(self, code: int, _status) -> None:
        self.finished.emit(int(code))


def run_blocking(yaml_path: str | Path, *, python: str | None = None, timeout: float = 600.0) -> RunResult:
    """Headless smoke helper (no Qt event loop required)."""
    import subprocess

    py = python or sys.executable
    env = _ensure_repo_on_pythonpath(os.environ, as_qprocess_list=False)
    y = str(Path(yaml_path).resolve())
    p = subprocess.run(
        [py, "-m", "epc_engine", y],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(repo_root()),
        timeout=timeout,
    )
    return RunResult(p.returncode, p.stdout, p.stderr, y)
