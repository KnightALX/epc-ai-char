"""Entry: python -m epc_gui"""
from __future__ import annotations

import sys


def main() -> int:
    from epc_gui.app import run

    return run()


if __name__ == "__main__":
    sys.exit(main())
