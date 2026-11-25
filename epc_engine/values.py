"""Value parsing / formatting for scalar and N×N table strings."""
from __future__ import annotations


def parse_tokens(value: str) -> list[float]:
    parts = value.split()
    if not parts:
        raise ValueError("empty value")
    return [float(x) for x in parts]


def is_axis_or_table(n_tokens: int, n: int) -> str:
    if n_tokens == 1:
        return "scalar"
    if n_tokens == n:
        return "vector_axis"
    if n_tokens == n * n:
        return "matrix_flat"
    return "unknown"


def fmt_scalar(x: float) -> str:
    """Serialize floats with enough digits for <<1e-6 relative re-read error.

    Legacy magnitude-tier ``:.2f``/``:.5f`` caused ~1e-5 relative error on
    mid-sized delay cells after constraint write-back; use significant-digit
    formatting instead (do not loosen G2 thresholds).
    """
    # 12 significant digits → typical relative round-trip ≪ 1e-6
    return format(float(x), ".12g")


def format_tokens(vals: list[float]) -> str:
    return " ".join(fmt_scalar(v) for v in vals)


def infer_n_from_axes(tran: str, load: str) -> int:
    nt = len(tran.split())
    nl = len(load.split())
    if nt != nl:
        raise ValueError(f"tran/load axis length mismatch: {nt} vs {nl}")
    return nt
