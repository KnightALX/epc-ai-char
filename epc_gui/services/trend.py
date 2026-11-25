"""T0 capacity × typical value series. typical = median_cell for N×N tables."""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from epc_engine.construct_types import AXIS_KEYS
from epc_engine.parse import parse_instance
from epc_engine.values import parse_tokens

from .db_reader import CharDb

TYPICAL_LABEL = "typical=median_cell"


@dataclass(frozen=True)
class TypicalResult:
    value: float | None
    kind: str  # scalar | median_cell | skip_axis | unknown
    n: int
    cell_index: int | None = None
    tran_i: int | None = None
    load_i: int | None = None


def capacity_of(instance: str) -> int:
    p = parse_instance(instance)
    return int(p.depth) * int(p.width)


def typical_value(value_str: str, n: int = 5) -> TypicalResult:
    """P0 fixed rule (scope §3.3 / Kai nail):

    1. scalar (1 token) → use it
    2. N×N table → **median cell** at (tran_index mid, load_index mid)
       mid = n // 2 (0-based); flat index = mid * n + mid
       UI label: typical=median_cell  (NOT median/mean of all tokens)
    3. axis vector (n tokens) → skip for trend Y
    """
    try:
        toks = parse_tokens(value_str)
    except Exception:
        return TypicalResult(None, "unknown", n)
    if len(toks) == 1:
        return TypicalResult(toks[0], "scalar", n)
    if len(toks) == n * n:
        mid = n // 2
        idx = mid * n + mid
        return TypicalResult(toks[idx], "median_cell", n, idx, mid, mid)
    if len(toks) == n:
        return TypicalResult(None, "skip_axis", n)
    return TypicalResult(None, "unknown", n)


@dataclass
class SeriesPoint:
    instance: str
    capacity: int
    value: float


@dataclass
class TrendSeries:
    key: str
    pvt: str
    points: list[SeriesPoint]
    typical_kind: str = TYPICAL_LABEL


def infer_n(db: CharDb) -> int:
    for ax in AXIS_KEYS:
        # any instance/pvt
        row = db.page(key=ax, limit=1)
        if row:
            nt = len(row[0]["value"].split())
            if nt > 0:
                return nt
    return 5


def build_series(
    db_path: str | Path,
    *,
    key: str,
    pvts: Iterable[str],
    instances: Iterable[str] | None = None,
    n: int | None = None,
) -> list[TrendSeries]:
    if key in AXIS_KEYS:
        return []
    with CharDb(db_path) as db:
        n_ax = n if n is not None else infer_n(db)
        insts = list(instances) if instances is not None else db.distinct("instance")
        # sort by capacity asc, then name
        ranked: list[tuple[int, str]] = []
        for inst in insts:
            try:
                ranked.append((capacity_of(inst), inst))
            except Exception:
                continue
        ranked.sort(key=lambda t: (t[0], t[1]))
        out: list[TrendSeries] = []
        for pvt in pvts:
            pts: list[SeriesPoint] = []
            kind = TYPICAL_LABEL
            for cap, inst in ranked:
                raw = db.get_value(inst, pvt, key)
                if raw is None:
                    continue
                tv = typical_value(raw, n_ax)
                if tv.value is None:
                    continue
                if tv.kind == "median_cell":
                    kind = TYPICAL_LABEL
                elif tv.kind == "scalar":
                    kind = "typical=scalar"
                pts.append(SeriesPoint(inst, cap, float(tv.value)))
            out.append(TrendSeries(key=key, pvt=pvt, points=pts, typical_kind=kind))
        return out


def max_rel_err(a: float, b: float) -> float:
    den = max(abs(a), abs(b), 1e-30)
    return abs(a - b) / den


def seed_overlay_error(
    a_db: str | Path,
    b_db: str | Path,
    instance: str,
    pvt: str,
    key: str,
    n: int = 5,
) -> tuple[float, str]:
    """T1: max relative error A vs B for one locator. Display only."""
    with CharDb(a_db) as da, CharDb(b_db) as db:
        va = da.get_value(instance, pvt, key)
        vb = db.get_value(instance, pvt, key)
    if va is None or vb is None:
        return float("nan"), "missing"
    ta, tb = parse_tokens(va), parse_tokens(vb)
    if len(ta) != len(tb):
        return float("nan"), "len_mismatch"
    errs = [max_rel_err(x, y) for x, y in zip(ta, tb)]
    return max(errs) if errs else float("nan"), "ok"


# --- P1 helpers: T1 seed_from_A, T3 bars, export rows ---

SPEED_HINTS = ("tcq", "taccess", "tcd", "tselr1", "clk_to_q", "delay", "period")
POWER_HINTS = ("leakage", "power", "energy", "dynamic")


def _is_speed_key(k: str) -> bool:
    kl = k.lower()
    return any(h in kl for h in SPEED_HINTS)


def _is_power_key(k: str) -> bool:
    kl = k.lower()
    return any(h in kl for h in POWER_HINTS)


def constrained_locators(yaml_data: dict | None) -> set[tuple[str, str, str]]:
    """Instance×pvt×key touched by relative constraints (may ≠ seed)."""
    out: set[tuple[str, str, str]] = set()
    if not yaml_data:
        return out
    for c in yaml_data.get("constraints") or []:
        if c.get("type") not in ("relative_delta_vs_source", "relative_improve_vs_source"):
            continue
        for inst in c.get("instances") or []:
            for pvt in c.get("pvts") or []:
                for key in c.get("keys") or []:
                    out.add((str(inst), str(pvt), str(key)))
                # sugar may expand keys later; still record declared
    return out


def find_seed_from_a(
    a_db: str | Path,
    b_db: str | Path,
    yaml_data: dict | None = None,
    *,
    prefer_key: str | None = None,
) -> tuple[str, str, str, float, str]:
    """Default T1 locator: first A∩B group with max_rel < 1e-9 (seed_from_A).

    Skips YAML relative-constraint locators first; falls back to any match.
    Returns (instance, pvt, key, max_rel, status).
    """
    constrained = constrained_locators(yaml_data)
    with CharDb(a_db) as da, CharDb(b_db) as db:
        insts = [i for i in da.distinct("instance") if i in set(db.distinct("instance"))]
        pvts = [p for p in da.distinct("pvt") if p in set(db.distinct("pvt"))]
        keys = [
            k
            for k in da.distinct("field_key")
            if k in set(db.distinct("field_key")) and k not in AXIS_KEYS
        ]
    if prefer_key and prefer_key in keys:
        keys = [prefer_key] + [k for k in keys if k != prefer_key]
    # Prefer speed-ish keys for stable DEMO seed
    keys = sorted(keys, key=lambda k: (0 if _is_speed_key(k) else 1, k))

    def scan(skip_constrained: bool) -> tuple[str, str, str, float, str] | None:
        for inst in insts:
            for pvt in pvts:
                for key in keys:
                    if skip_constrained and (inst, pvt, key) in constrained:
                        continue
                    err, st = seed_overlay_error(a_db, b_db, inst, pvt, key)
                    if st == "ok" and err == err and err < 1e-9:
                        return inst, pvt, key, err, "seed_from_A"
        return None

    hit = scan(True) or scan(False)
    if hit:
        return hit
    # Fallback first overlapping
    if insts and pvts and keys:
        err, st = seed_overlay_error(a_db, b_db, insts[0], pvts[0], keys[0])
        return insts[0], pvts[0], keys[0], err, st if st != "ok" else "manual_fallback"
    return "", "", "", float("nan"), "missing"


@dataclass
class T3Bar:
    key: str
    family: str  # speed | power
    instance: str
    pvt: str
    baseline: float | None
    b_value: float | None
    target: float | None
    delta_pct: float | None
    baseline_source: str


def t3_bars(
    a_db: str | Path,
    b_db: str | Path,
    yaml_data: dict,
    *,
    n: int = 5,
) -> list[T3Bar]:
    """Baseline (A typical) vs B typical vs target for ≥1 speed + ≥1 power if present."""
    rels = [
        c
        for c in (yaml_data.get("constraints") or [])
        if c.get("type") in ("relative_delta_vs_source", "relative_improve_vs_source")
    ]
    bars: list[T3Bar] = []
    have_speed = False
    have_power = False
    for c in rels:
        tgt = c.get("target") or {}
        delta = tgt.get("delta_pct")
        try:
            delta_f = float(delta) if delta is not None else None
        except (TypeError, ValueError):
            delta_f = None
        # sugar improve: synthetic keys from speed_pct/power_pct — need expanded keys
        keys = list(c.get("keys") or [])
        if c.get("type") == "relative_improve_vs_source" and not keys:
            continue
        baseline_src = str(tgt.get("baseline") or "source_aligned")
        insts = list(c.get("instances") or [])
        pvts = list(c.get("pvts") or [])
        if not insts or not pvts:
            continue
        inst, pvt = insts[0], pvts[0]
        for key in keys:
            fam = "speed" if _is_speed_key(key) else ("power" if _is_power_key(key) else "other")
            if fam == "speed" and have_speed:
                continue
            if fam == "power" and have_power:
                continue
            with CharDb(a_db) as da, CharDb(b_db) as db:
                va = da.get_value(inst, pvt, key)
                vb = db.get_value(inst, pvt, key)
            ta = typical_value(va, n) if va else TypicalResult(None, "unknown", n)
            tb = typical_value(vb, n) if vb else TypicalResult(None, "unknown", n)
            target = None
            if ta.value is not None and delta_f is not None:
                target = float(ta.value) * (1.0 + delta_f / 100.0)
            bars.append(
                T3Bar(
                    key=key,
                    family=fam,
                    instance=inst,
                    pvt=pvt,
                    baseline=ta.value,
                    b_value=tb.value,
                    target=target,
                    delta_pct=delta_f,
                    baseline_source=baseline_src,
                )
            )
            if fam == "speed":
                have_speed = True
            if fam == "power":
                have_power = True
            if have_speed and have_power:
                return bars
    return bars


def series_to_csv_rows(series_list: list[TrendSeries]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for ser in series_list:
        for p in ser.points:
            rows.append(
                {
                    "capacity": p.capacity,
                    "instance": p.instance,
                    "pvt": ser.pvt,
                    "key": ser.key,
                    "typical": p.value,
                }
            )
    return rows
