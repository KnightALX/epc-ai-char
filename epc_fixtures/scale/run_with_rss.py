"""Run an EPC engine job while sampling peak memory of the python process.

Usage: python epc_fixtures/scale/run_with_rss.py <yaml> [--poll-ms 50]
Prints: EXIT, wall_seconds, peak_rss_mb — machine-readable for scale evals.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import psutil


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = [a for a in sys.argv[1:] if not a.startswith("--poll-ms")]
    poll_ms = 50
    for a in sys.argv[1:]:
        if a.startswith("--poll-ms="):
            poll_ms = int(a.split("=", 1)[1])
    if not args:
        print("usage: run_with_rss.py <yaml> [--poll-ms=N]", file=sys.stderr)
        return 2
    yaml_path = Path(args[0])
    t0 = time.time()
    proc = subprocess.Popen(
        [sys.executable, "-m", "epc_engine", str(yaml_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    peak = 0
    tail: list[str] = []
    out_lines: list[str] = []
    try:
        while proc.poll() is None:
            try:
                rss = psutil.Process(proc.pid).memory_info().rss
                peak = max(peak, rss)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            time.sleep(poll_ms / 1000.0)
        for line in proc.stdout:
            out_lines.append(line)
    finally:
        if proc.poll() is None:
            proc.kill()
    wall = time.time() - t0
    tail = out_lines[-25:]
    print("".join(tail), end="")
    print(f"RSS_PEAK_MB={peak / (1024 * 1024):.1f}")
    print(f"WALL_SECONDS={wall:.2f}")
    print(f"EXIT={proc.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
