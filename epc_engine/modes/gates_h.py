"""P2 hard gates H1 (completeness) / H2 (seed unchanged)."""
from __future__ import annotations

import math
from typing import Iterable

from ..construct_types import AXIS_KEYS, ConstructResult
from ..source import SourceDB
from ..values import parse_tokens

EPS = 1e-12
H2_MAX_REL = 1e-9


def relative_err(a: float, b: float) -> float:
    den = max(abs(a), EPS)
    return abs(a - b) / den


def max_rel_tokens(va: str, vb: str) -> float:
    if va == vb:
        return 0.0
    try:
        ta = parse_tokens(va)
        tb = parse_tokens(vb)
    except ValueError:
        return float("inf") if va != vb else 0.0
    if len(ta) != len(tb):
        return float("inf")
    return max(relative_err(x, y) for x, y in zip(ta, tb))


def check_h1(
    result: ConstructResult,
    instances: list[str],
    pvts: list[str],
    field_keys: list[str],
) -> tuple[bool, str]:
    expected = len(instances) * len(pvts) * len(field_keys)
    n = len(result.data)
    if n != expected:
        return False, f"H1 FAIL: COUNT={n} expected={expected} (|I|×|P|×|K|)"
    # Axis keys present & length N for every group
    for inst in instances:
        for pvt in pvts:
            for ak in AXIS_KEYS:
                if (inst, pvt, ak) not in result.data:
                    return False, f"H1 FAIL: missing axis {ak} at {inst}×{pvt}"
            tran = result.data[(inst, pvt, "tran_index")]
            load = result.data[(inst, pvt, "load_index")]
            nt = len(tran.split())
            nl = len(load.split())
            if nt != nl or nt != result.n:
                return (
                    False,
                    f"H1 FAIL: axis len mismatch at {inst}×{pvt}: "
                    f"tran={nt} load={nl} N={result.n}",
                )
            for key in field_keys:
                if key in AXIS_KEYS:
                    continue
                val = result.data.get((inst, pvt, key))
                if val is None:
                    return False, f"H1 FAIL: missing {inst}×{pvt}×{key}"
                toks = val.split()
                # scalar=1 or N² table
                if len(toks) not in (1, result.n * result.n, result.n):
                    # allow N for rare vector; tables must be N² or 1
                    if len(toks) != result.n * result.n and len(toks) != 1:
                        return (
                            False,
                            f"H1 FAIL: bad token count {len(toks)} for "
                            f"{inst}×{pvt}×{key} (N={result.n})",
                        )
    return True, f"H1 PASS: COUNT={expected} axes ok"


def check_h2_seed_cells(
    result: ConstructResult,
    source: SourceDB,
    seed_cells: Iterable[tuple[str, str, str]],
) -> tuple[bool, str, float]:
    """seed_cells = (inst,pvt,key) that must match source bit/numeric-wise."""
    worst = 0.0
    worst_loc = ""
    n = 0
    for inst, pvt, key in seed_cells:
        src = source.get(inst, pvt, key)
        got = result.data.get((inst, pvt, key))
        if src is None:
            return False, f"H2 FAIL: seed missing in source {inst}×{pvt}×{key}", float("inf")
        if got is None:
            return False, f"H2 FAIL: seed missing in result {inst}×{pvt}×{key}", float("inf")
        if got == src:
            n += 1
            continue
        rel = max_rel_tokens(src, got)
        if rel > worst:
            worst = rel
            worst_loc = f"{inst}×{pvt}×{key}"
        if rel >= H2_MAX_REL:
            return (
                False,
                f"H2 FAIL: seed changed at {worst_loc} max_rel={rel:.3e} (≥{H2_MAX_REL})",
                rel,
            )
        n += 1
    return True, f"H2 PASS: {n} seed cells unchanged (max_rel={worst:.3e})", worst


def check_h2_seed_instances(
    result: ConstructResult,
    source: SourceDB,
    seed_instances: list[str],
    pvts: list[str],
    field_keys: list[str],
) -> tuple[bool, str, float]:
    cells = [
        (inst, pvt, key)
        for inst in seed_instances
        for pvt in pvts
        for key in field_keys
        if source.get(inst, pvt, key) is not None
    ]
    return check_h2_seed_cells(result, source, cells)


def p95(xs: list[float]) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    idx = min(len(ys) - 1, max(0, int(math.ceil(0.95 * len(ys)) - 1)))
    return ys[idx]
