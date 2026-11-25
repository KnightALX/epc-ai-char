"""P2 chart helpers: constraint evidence (chart 1) + free A/B compare (chart 2).

GUI never invents sugar-expand rules (engine load_job only) and never decides PASS/FAIL.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from epc_engine.construct_types import AXIS_KEYS
from epc_engine.job import Job

from .db_reader import CharDb
from .sugar import SugarExpandResult, expand_from_path, expand_from_yaml_text
from . import trend as trend_svc
from . import yaml_io

EPS = 1e-12

VIEW_REL_BARS = "rel_bars"
VIEW_BOUND_CELLS = "bound_cells"
VIEW_CONSTRAINT_LIST = "constraint_list"


@dataclass
class RelBar:
    label: str
    instance: str
    pvt: str
    key: str
    baseline: float | None
    b_value: float | None
    target: float | None
    delta_pct: float | None


@dataclass
class BoundCell:
    label: str
    instance: str
    pvt: str
    key: str
    b_value: float | None
    bound: float | None
    op: str
    unit: str


@dataclass
class ConstraintListRow:
    ctype: str
    instance: str
    pvt: str
    key: str
    detail: str


@dataclass
class Chart1Model:
    has_constraints: bool
    available_views: list[str]
    default_view: str | None
    rel_bars: list[RelBar]
    bound_cells: list[BoundCell]
    list_rows: list[ConstraintListRow]
    error: str = ""


@dataclass
class AlignPoint:
    instance: str
    capacity: int
    a_value: float | None
    b_value: float | None


@dataclass
class FreeCompareModel:
    empty_reason: str | None  # i18n key suffix or None if ok
    pvt_options: list[str]
    key_options: list[str]
    selected_pvt: str
    selected_key: str
    points: list[AlignPoint]
    cover_n: int
    cover_m: int
    delta_med_pct: float | None
    delta_mean_pct: float | None
    typical_kind: str


def load_expanded(
    *,
    yaml_path: str | Path | None = None,
    yaml_data: dict | None = None,
) -> SugarExpandResult:
    if yaml_path and Path(yaml_path).is_file():
        return expand_from_path(yaml_path)
    if yaml_data is not None:
        return expand_from_yaml_text(yaml_io.dump_yaml_text(yaml_data))
    return SugarExpandResult(ok=False, error="no yaml")


def _job_constraints(job: Job | None) -> list[Any]:
    if job is None:
        return []
    return list(job.constraints or [])


def build_chart1(
    *,
    yaml_path: str | Path | None,
    yaml_data: dict | None,
    a_db: str | Path | None,
    b_db: str | Path | None,
    max_bars: int = 16,
) -> Chart1Model:
    res = load_expanded(yaml_path=yaml_path, yaml_data=yaml_data)
    if not res.ok:
        return Chart1Model(
            has_constraints=False,
            available_views=[],
            default_view=None,
            rel_bars=[],
            bound_cells=[],
            list_rows=[],
            error=res.error,
        )
    cons = _job_constraints(res.job)
    if not cons:
        return Chart1Model(
            has_constraints=False,
            available_views=[],
            default_view=None,
            rel_bars=[],
            bound_cells=[],
            list_rows=[],
        )

    a_ok = bool(a_db and Path(a_db).is_file())
    b_ok = bool(b_db and Path(b_db).is_file())
    n_ax = 5
    if b_ok:
        try:
            with CharDb(b_db) as db:
                n_ax = trend_svc.infer_n(db)
        except Exception:
            pass

    rel_bars: list[RelBar] = []
    bound_cells: list[BoundCell] = []
    list_rows: list[ConstraintListRow] = []

    for c in cons:
        ctype = str(c.type)
        tgt = c.target or {}
        if ctype == "relative_delta_vs_source":
            try:
                delta_f = float(tgt.get("delta_pct")) if tgt.get("delta_pct") is not None else None
            except (TypeError, ValueError):
                delta_f = None
            for inst in c.instances or []:
                for pvt in c.pvts or []:
                    for key in c.keys or []:
                        list_rows.append(
                            ConstraintListRow(
                                ctype="relative",
                                instance=str(inst),
                                pvt=str(pvt),
                                key=str(key),
                                detail=f"δ={delta_f}%" if delta_f is not None else "",
                            )
                        )
                        if len(rel_bars) >= max_bars:
                            continue
                        baseline = b_val = target = None
                        if a_ok and b_ok:
                            with CharDb(a_db) as da, CharDb(b_db) as db:
                                va = da.get_value(str(inst), str(pvt), str(key))
                                vb = db.get_value(str(inst), str(pvt), str(key))
                            ta = trend_svc.typical_value(va, n_ax) if va else None
                            tb = trend_svc.typical_value(vb, n_ax) if vb else None
                            baseline = ta.value if ta else None
                            b_val = tb.value if tb else None
                            if baseline is not None and delta_f is not None:
                                target = float(baseline) * (1.0 + delta_f / 100.0)
                        short = f"{str(inst)[-12:]}·{str(key)}"
                        rel_bars.append(
                            RelBar(
                                label=short,
                                instance=str(inst),
                                pvt=str(pvt),
                                key=str(key),
                                baseline=baseline,
                                b_value=b_val,
                                target=target,
                                delta_pct=delta_f,
                            )
                        )
        elif ctype == "table_upper_bound":
            try:
                bound = float(tgt.get("value")) if tgt.get("value") is not None else None
            except (TypeError, ValueError):
                bound = None
            op = str(tgt.get("op") or "<=")
            unit = str(tgt.get("unit") or "")
            for inst in c.instances or []:
                for pvt in c.pvts or []:
                    for key in c.keys or []:
                        list_rows.append(
                            ConstraintListRow(
                                ctype="upper",
                                instance=str(inst),
                                pvt=str(pvt),
                                key=str(key),
                                detail=f"{op} {bound}{unit}".strip(),
                            )
                        )
                        b_val = None
                        if b_ok:
                            with CharDb(b_db) as db:
                                vb = db.get_value(str(inst), str(pvt), str(key))
                            tb = trend_svc.typical_value(vb, n_ax) if vb else None
                            b_val = tb.value if tb else None
                        short = f"{str(inst)[-12:]}·{str(key)}"
                        bound_cells.append(
                            BoundCell(
                                label=short,
                                instance=str(inst),
                                pvt=str(pvt),
                                key=str(key),
                                b_value=b_val,
                                bound=bound,
                                op=op,
                                unit=unit,
                            )
                        )
        else:
            for inst in (c.instances or ["—"])[:1]:
                for pvt in (c.pvts or ["—"])[:1]:
                    for key in (c.keys or ["—"])[:1]:
                        list_rows.append(
                            ConstraintListRow(
                                ctype=ctype,
                                instance=str(inst),
                                pvt=str(pvt),
                                key=str(key),
                                detail="",
                            )
                        )

    views: list[str] = []
    if rel_bars:
        views.append(VIEW_REL_BARS)
    if bound_cells:
        views.append(VIEW_BOUND_CELLS)
    if list_rows:
        views.append(VIEW_CONSTRAINT_LIST)

    default = None
    if VIEW_REL_BARS in views:
        default = VIEW_REL_BARS
    elif VIEW_BOUND_CELLS in views:
        default = VIEW_BOUND_CELLS
    elif VIEW_CONSTRAINT_LIST in views:
        default = VIEW_CONSTRAINT_LIST

    return Chart1Model(
        has_constraints=True,
        available_views=views,
        default_view=default,
        rel_bars=rel_bars,
        bound_cells=bound_cells,
        list_rows=list_rows,
    )


def db_pvt_key_sets(path: str | Path) -> tuple[set[str], set[str], set[str]]:
    with CharDb(path) as db:
        pvts = set(db.distinct("pvt"))
        keys = {k for k in db.distinct("field_key") if k not in AXIS_KEYS}
        insts = set(db.distinct("instance"))
    return pvts, keys, insts


def keys_under_pvt(path: str | Path, pvt: str) -> set[str]:
    with CharDb(path) as db:
        rows = db.page(pvt=pvt, limit=100000)
    return {r["field_key"] for r in rows if r["field_key"] not in AXIS_KEYS}


def build_free_compare(
    *,
    ref_db: str | Path | None,
    constructed_db: str | Path | None,
    pvt: str | None = None,
    key: str | None = None,
) -> FreeCompareModel:
    empty = FreeCompareModel(
        empty_reason="need_dbs",
        pvt_options=[],
        key_options=[],
        selected_pvt="",
        selected_key="",
        points=[],
        cover_n=0,
        cover_m=0,
        delta_med_pct=None,
        delta_mean_pct=None,
        typical_kind=trend_svc.TYPICAL_LABEL,
    )
    if not (ref_db and constructed_db and Path(ref_db).is_file() and Path(constructed_db).is_file()):
        return empty

    try:
        pa, ka, _ = db_pvt_key_sets(ref_db)
        pb, kb, _ = db_pvt_key_sets(constructed_db)
    except Exception:
        return empty

    pvt_opts = sorted(pa & pb)
    if not pvt_opts:
        return FreeCompareModel(
            empty_reason="no_pvt",
            pvt_options=[],
            key_options=[],
            selected_pvt="",
            selected_key="",
            points=[],
            cover_n=0,
            cover_m=0,
            delta_med_pct=None,
            delta_mean_pct=None,
            typical_kind=trend_svc.TYPICAL_LABEL,
        )

    sel_pvt = pvt if pvt in pvt_opts else pvt_opts[0]
    # Prefer keys present under this PVT in both DBs; fallback to global ∩
    try:
        keys_p = keys_under_pvt(ref_db, sel_pvt) & keys_under_pvt(constructed_db, sel_pvt)
    except Exception:
        keys_p = set()
    key_opts = sorted(keys_p) if keys_p else sorted(ka & kb)
    if not key_opts:
        return FreeCompareModel(
            empty_reason="no_key",
            pvt_options=pvt_opts,
            key_options=[],
            selected_pvt=sel_pvt,
            selected_key="",
            points=[],
            cover_n=0,
            cover_m=0,
            delta_med_pct=None,
            delta_mean_pct=None,
            typical_kind=trend_svc.TYPICAL_LABEL,
        )

    # Prefer a speed-ish key for demo readability
    preferred = []
    for needle in ("tcq", "tselr1_min_period", "clk_to_q", "delay", "period", "taccess"):
        preferred.extend([k for k in key_opts if needle in k and k not in preferred])
    ordered_keys = preferred + [k for k in key_opts if k not in preferred]
    sel_key = key if key in key_opts else ordered_keys[0]

    with CharDb(ref_db) as da, CharDb(constructed_db) as db:
        n_ax = trend_svc.infer_n(db)
        insts_a = {
            r["instance"]
            for r in da.page(pvt=sel_pvt, key=sel_key, limit=100000)
        }
        insts_b = {
            r["instance"]
            for r in db.page(pvt=sel_pvt, key=sel_key, limit=100000)
        }
        union = sorted(insts_a | insts_b, key=lambda i: (trend_svc.capacity_of(i), i))
        points: list[AlignPoint] = []
        kind = trend_svc.TYPICAL_LABEL
        for inst in union:
            try:
                cap = trend_svc.capacity_of(inst)
            except Exception:
                continue
            va = da.get_value(inst, sel_pvt, sel_key) if inst in insts_a else None
            vb = db.get_value(inst, sel_pvt, sel_key) if inst in insts_b else None
            ta = trend_svc.typical_value(va, n_ax) if va else None
            tb = trend_svc.typical_value(vb, n_ax) if vb else None
            av = ta.value if ta and ta.value is not None else None
            bv = tb.value if tb and tb.value is not None else None
            if ta and ta.kind == "scalar":
                kind = "typical=scalar"
            points.append(AlignPoint(inst, cap, av, bv))

    if not points:
        return FreeCompareModel(
            empty_reason="no_points",
            pvt_options=pvt_opts,
            key_options=key_opts,
            selected_pvt=sel_pvt,
            selected_key=sel_key,
            points=[],
            cover_n=0,
            cover_m=0,
            delta_med_pct=None,
            delta_mean_pct=None,
            typical_kind=kind,
        )

    both = [p for p in points if p.a_value is not None and p.b_value is not None]
    deltas: list[float] = []
    for p in both:
        a = float(p.a_value)
        b = float(p.b_value)
        deltas.append((b - a) / max(abs(a), EPS))
    med = None
    mean_pct = None
    if deltas:
        med = float(statistics.median(deltas)) * 100.0
        mean_pct = float(statistics.mean(deltas)) * 100.0

    return FreeCompareModel(
        empty_reason=None,
        pvt_options=pvt_opts,
        key_options=key_opts,
        selected_pvt=sel_pvt,
        selected_key=sel_key,
        points=points,
        cover_n=len(both),
        cover_m=len(points),
        delta_med_pct=med,
        delta_mean_pct=mean_pct,
        typical_kind=kind,
    )
