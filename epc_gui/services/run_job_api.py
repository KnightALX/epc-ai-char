"""P1-E Should: thin run_job wrapper. Gates still from audit + EXIT only."""
from __future__ import annotations

from pathlib import Path

from epc_gui.services.job_runner import RunResult, run_blocking


def run_job(path: str | Path, *, timeout: float = 600.0) -> RunResult:
    """Subprocess CLI equivalent; does not invent PASS/FAIL."""
    return run_blocking(path, timeout=timeout)
