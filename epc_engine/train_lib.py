"""Offline residual-GBDT training and hold-out eval (A_ref only).

Dual-head:
  - models_geom: leave-one-instance residual labels (LOI / new geometry)
  - models_pvt:  leave-one-pvt residual labels (LOP / new PVT)

Online default apply_on=all_extrapolated uses the matching head.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

from .backends import idw_nn
from .backends.features import FEATURE_NAMES, cell_coords, feature_row
from .construct_types import AXIS_KEYS
from .parse import parse_instance, parse_pvt, pvt_distance
from .source import SourceDB
from .values import parse_tokens

SHANGHAI = ZoneInfo("Asia/Shanghai")
EPS = 1e-12
RANDOM_SEED = 42

# Anchor from accepted geom-only residual report (P-LOI-reg)
LOI_PREV_P95 = 0.102331
LOI_REG_MAX = LOI_PREV_P95 * 1.05  # 0.107448

CORE_KEYS = [
    "tselr1_min_period",
    "tcq",
    "tcd",
    "taccess",
    "leakage_vddc",
    "read_power_vddc",
    "write_power_vddc",
    "dynamic_energy_read",
]

LOI_INSTANCES = [
    "HINP3TCAM64X8SWISDC",
    "HINP3TCAM512X100SWISDC",
    "HINP3TCAM64X100SWISDC",
    "HINP3TCAM512X8SWISDC",
    "HINP3TCAM256X32SWISDC",
]

LOP_PVTS = [
    "TT_0P80V_0P80V_25C",
    "SSGNP_0P99V_0P99V_125C",
    "FFGNP_0P675V_0P675V_M40C",
    "SSGNP_0P675V_0P675V_125C",
    "FFGNP_1P05V_1P05V_25C",
    "TT_0P90V_0P90V_M40C",
]


def _axis_from_source(source: SourceDB) -> tuple[int, list[float], list[float]]:
    g = next(iter(source.groups.values()))
    tran = [float(x) for x in g["tran_index"].split()]
    load = [float(x) for x in g["load_index"].split()]
    if len(tran) != len(load):
        raise RuntimeError("axis length mismatch")
    return len(tran), tran, load


def _rel_err(hat: float, true: float, eps: float = EPS) -> float:
    return abs(hat - true) / max(abs(true), eps)


def nearest_pvt_excluding(
    target_name: str,
    source: SourceDB,
    excluded: set[str],
) -> str:
    b_pp = parse_pvt(target_name) if target_name in source.pvt_parts else parse_pvt(target_name)
    # Prefer pre-parsed parts when available
    if target_name in source.pvt_parts:
        b_pp = source.pvt_parts[target_name]
    best_name = None
    best_d = float("inf")
    for name, parts in source.pvt_parts.items():
        if name in excluded:
            continue
        d = pvt_distance(b_pp, parts)
        if d < best_d:
            best_d = d
            best_name = name
    if best_name is None:
        raise RuntimeError("no remaining pvts for NN")
    return best_name


# PVT residual is only applied for keys where leave-pvt prior error is
# meaningful. Delay tables are already near-perfect under optional_pvt_scale;
# forcing a residual there overfits noise and fails P-LOP.
PVT_APPLY_PRIOR_P95_THR = 1e-4


def select_pvt_apply_keys(
    source: SourceDB,
    keys: list[str],
    *,
    thr: float = PVT_APPLY_PRIOR_P95_THR,
    sample_pvts: list[str] | None = None,
) -> list[str]:
    """Keys eligible for pvt-head residual.

    Only **scalar** fields (1 token) whose leave-one-pvt prior p95 ≥ thr.
    N×N delay/power tables are already near-perfect under optional_pvt_scale;
    residual there overfits noise and fails P-LOP.
    """
    pvts = list(sample_pvts or source.pvts)
    # Probe token length from first available group
    probe_inst = source.instances[0]
    probe_pvt = source.pvts[0]
    out: list[str] = []
    use_pvts = pvts if len(pvts) <= 40 else pvts[:: max(1, len(pvts) // 40)]
    for key in keys:
        if key in AXIS_KEYS:
            continue
        sample = source.get(probe_inst, probe_pvt, key)
        if sample is None:
            continue
        n_tok = len(parse_tokens(sample))
        if n_tok != 1:
            continue  # tables: keep prior on pvt-only
        errs: list[float] = []
        for pvt in use_pvts:
            if pvt not in source.pvt_parts:
                continue
            for inst in source.instances:
                if not source.has_group(inst, pvt):
                    continue
                true_toks = parse_tokens(source.get(inst, pvt, key))  # type: ignore[arg-type]
                prior_toks = _prior_leave_one_pvt(source, inst, pvt, key, {pvt})
                for t, p in zip(true_toks, prior_toks):
                    errs.append(_rel_err(p, t))
        if not errs:
            continue
        p95 = float(np.percentile(np.asarray(errs, dtype=np.float64), 95))
        if p95 >= thr:
            out.append(key)
    return out


@dataclass
class ErrAgg:
    errs: list[float] = field(default_factory=list)

    def add(self, e: float) -> None:
        self.errs.append(float(e))

    def extend(self, other: "ErrAgg") -> None:
        self.errs.extend(other.errs)

    def summary(self) -> dict[str, float]:
        if not self.errs:
            return {"n": 0, "p50": float("nan"), "p95": float("nan"), "max": float("nan")}
        a = np.asarray(self.errs, dtype=np.float64)
        return {
            "n": int(a.size),
            "p50": float(np.percentile(a, 50)),
            "p95": float(np.percentile(a, 95)),
            "max": float(a.max()),
        }


def _make_regressor(
    seed: int = RANDOM_SEED,
    *,
    head: str = "geom",
) -> HistGradientBoostingRegressor:
    # Slightly stronger regularization on pvt head: prior already near-perfect
    # on DEMO delay; avoid overshooting tiny residuals.
    if head == "pvt":
        return HistGradientBoostingRegressor(
            max_depth=4,
            max_iter=160,
            learning_rate=0.05,
            min_samples_leaf=12,
            l2_regularization=0.2,
            random_state=seed,
        )
    return HistGradientBoostingRegressor(
        max_depth=6,
        max_iter=120,
        learning_rate=0.08,
        min_samples_leaf=8,
        l2_regularization=0.05,
        random_state=seed,
    )


def _append_xy_rows(
    X_rows: list[list[float]],
    y_rows: list[float],
    *,
    source: SourceDB,
    inst: str,
    pvt: str,
    key: str,
    true_toks: list[float],
    prior_toks: list[float],
    nn_pp,
    n_axis: int,
    tran_axis: list[float],
    load_axis: list[float],
) -> None:
    ip = parse_instance(inst)
    pp = parse_pvt(pvt)
    if len(prior_toks) != len(true_toks):
        raise RuntimeError(
            f"token len mismatch {inst}/{pvt}/{key}: "
            f"{len(prior_toks)} vs {len(true_toks)}"
        )
    coords = cell_coords(len(true_toks), n_axis)
    for flat_i, i, j in coords:
        tran_v = tran_axis[i] if i < len(tran_axis) else float(i)
        load_v = load_axis[j] if j < len(load_axis) else float(j)
        if len(true_toks) == 1:
            tran_v, load_v = 0.0, 0.0
        ph = prior_toks[flat_i]
        X_rows.append(
            feature_row(
                ip,
                pp,
                cell_i=i,
                cell_j=j,
                tran_val=tran_v,
                load_val=load_v,
                prior_hat=ph,
                nn_pp=nn_pp,
            )
        )
        y_rows.append(true_toks[flat_i] - ph)


def build_xy_geom(
    source: SourceDB,
    keys: list[str],
    *,
    exclude_instances: set[str] | None = None,
    pvt_filter: set[str] | None = None,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Leave-one-instance residual labels (geometry extrapolation)."""
    n_axis, tran_axis, load_axis = _axis_from_source(source)
    exclude_base = set(exclude_instances or set())
    insts = [i for i in source.instances if i not in exclude_base]
    pvts = [p for p in source.pvts if pvt_filter is None or p in pvt_filter]

    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for key in keys:
        if key in AXIS_KEYS:
            continue
        X_rows: list[list[float]] = []
        y_rows: list[float] = []
        for inst in insts:
            excl = exclude_base | {inst}
            for pvt in pvts:
                if not source.has_group(inst, pvt):
                    continue
                true_toks = parse_tokens(source.get(inst, pvt, key))  # type: ignore[arg-type]
                prior_toks = idw_nn.prior_tokens_for_group(
                    source, inst, pvt, key, exclude_instances=excl
                )
                # Same pvt → ΔV/ΔT = 0
                nn_pp = source.pvt_parts[pvt]
                _append_xy_rows(
                    X_rows,
                    y_rows,
                    source=source,
                    inst=inst,
                    pvt=pvt,
                    key=key,
                    true_toks=true_toks,
                    prior_toks=prior_toks,
                    nn_pp=nn_pp,
                    n_axis=n_axis,
                    tran_axis=tran_axis,
                    load_axis=load_axis,
                )
        if X_rows:
            out[key] = (
                np.asarray(X_rows, dtype=np.float64),
                np.asarray(y_rows, dtype=np.float64),
            )
    return out


def build_xy_pvt(
    source: SourceDB,
    keys: list[str],
    *,
    exclude_pvts: set[str] | None = None,
    instance_filter: set[str] | None = None,
    # When building full train: for each pvt, pretend that pvt is held
    per_point_leave: bool = True,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Leave-one-pvt residual labels (PVT extrapolation)."""
    n_axis, tran_axis, load_axis = _axis_from_source(source)
    held_fixed = set(exclude_pvts or set())
    insts = [
        i
        for i in source.instances
        if instance_filter is None or i in instance_filter
    ]

    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for key in keys:
        if key in AXIS_KEYS:
            continue
        X_rows: list[list[float]] = []
        y_rows: list[float] = []
        for inst in insts:
            for pvt in source.pvts:
                if pvt in held_fixed:
                    continue
                if not source.has_group(inst, pvt):
                    continue
                # Pretend this pvt (and any fold-held) are absent
                if per_point_leave:
                    excl_pvts = held_fixed | {pvt}
                else:
                    excl_pvts = held_fixed
                    if not excl_pvts:
                        continue
                true_toks = parse_tokens(source.get(inst, pvt, key))  # type: ignore[arg-type]
                prior_toks = _prior_leave_one_pvt(
                    source, inst, pvt, key, excl_pvts
                )
                nn_name = nearest_pvt_excluding(pvt, source, excl_pvts)
                nn_pp = source.pvt_parts[nn_name]
                _append_xy_rows(
                    X_rows,
                    y_rows,
                    source=source,
                    inst=inst,
                    pvt=pvt,
                    key=key,
                    true_toks=true_toks,
                    prior_toks=prior_toks,
                    nn_pp=nn_pp,
                    n_axis=n_axis,
                    tran_axis=tran_axis,
                    load_axis=load_axis,
                )
        if X_rows:
            out[key] = (
                np.asarray(X_rows, dtype=np.float64),
                np.asarray(y_rows, dtype=np.float64),
            )
    return out


# Back-compat alias used by older call sites / tests
def build_xy_for_keys(
    source: SourceDB,
    keys: list[str],
    *,
    exclude_instances: set[str] | None = None,
    instance_filter: set[str] | None = None,
    pvt_filter: set[str] | None = None,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    return build_xy_geom(
        source,
        keys,
        exclude_instances=exclude_instances,
        pvt_filter=pvt_filter,
    )


def fit_models(
    xy: dict[str, tuple[np.ndarray, np.ndarray]],
    seed: int = RANDOM_SEED,
    *,
    head: str = "geom",
) -> dict[str, HistGradientBoostingRegressor]:
    models: dict[str, HistGradientBoostingRegressor] = {}
    for key, (X, y) in xy.items():
        if X.shape[0] < 20:
            continue
        m = _make_regressor(seed, head=head)
        m.fit(X, y)
        models[key] = m
    return models


def predict_residual_tokens(
    model: HistGradientBoostingRegressor,
    source: SourceDB,
    inst: str,
    pvt: str,
    key: str,
    prior_toks: list[float],
    *,
    nn_pp=None,
) -> list[float]:
    n_axis, tran_axis, load_axis = _axis_from_source(source)
    ip = parse_instance(inst)
    pp = parse_pvt(pvt)
    if nn_pp is None:
        nn_pp = source.pvt_parts.get(pvt, pp)
    coords = cell_coords(len(prior_toks), n_axis)
    X_rows = []
    for flat_i, i, j in coords:
        tran_v = tran_axis[i] if i < len(tran_axis) else float(i)
        load_v = load_axis[j] if j < len(load_axis) else float(j)
        if len(prior_toks) == 1:
            tran_v, load_v = 0.0, 0.0
        X_rows.append(
            feature_row(
                ip,
                pp,
                cell_i=i,
                cell_j=j,
                tran_val=tran_v,
                load_val=load_v,
                prior_hat=prior_toks[flat_i],
                nn_pp=nn_pp,
            )
        )
    resid = model.predict(np.asarray(X_rows, dtype=np.float64))
    return [float(prior_toks[k] + resid[k]) for k in range(len(prior_toks))]


def _prior_leave_one_pvt(
    source: SourceDB,
    inst: str,
    held_pvt: str,
    key: str,
    held_pvts: set[str],
) -> list[float]:
    """Prior as if held_pvt(s) were absent: NN among remaining pvts + scale."""
    from .backends.idw_nn import lookup_or_idw, optional_pvt_scale

    b_pp = (
        source.pvt_parts[held_pvt]
        if held_pvt in source.pvt_parts
        else parse_pvt(held_pvt)
    )
    best_name = nearest_pvt_excluding(held_pvt, source, held_pvts)
    ip = parse_instance(inst)
    val = lookup_or_idw(source, inst, ip, best_name, key)
    val = optional_pvt_scale(source, val, key, b_pp, best_name)
    return parse_tokens(val)


def eval_holdout_fold(
    source: SourceDB,
    *,
    held_instances: set[str] | None,
    held_pvts: set[str] | None,
    keys: list[str],
    seed: int = RANDOM_SEED,
) -> tuple[ErrAgg, ErrAgg, dict[str, ErrAgg], dict[str, ErrAgg]]:
    """Return (baseline_agg, residual_agg, baseline_by_key, residual_by_key).

    LOI: train geom head excluding held instance; apply residual on held.
    LOP: train pvt head excluding held pvt; apply residual on held.
    """
    if held_instances:
        xy = build_xy_geom(source, keys, exclude_instances=set(held_instances))
        models = fit_models(xy, seed=seed, head="geom")
        test_insts = [i for i in source.instances if i in held_instances]
        test_pvts = list(source.pvts)
        mode = "loi"
        pvt_apply_keys: set[str] | None = None  # geom: all keys
    else:
        assert held_pvts is not None
        train_pvts = set(source.pvts) - set(held_pvts)
        xy = build_xy_pvt(
            source,
            keys,
            exclude_pvts=set(held_pvts),
            per_point_leave=True,
        )
        models = fit_models(xy, seed=seed, head="pvt")
        test_insts = list(source.instances)
        test_pvts = [p for p in source.pvts if p in held_pvts]
        mode = "lop"
        # Gate: only keys with meaningful leave-pvt prior error (exclude held)
        pvt_apply_keys = set(
            select_pvt_apply_keys(
                source,
                keys,
                sample_pvts=[p for p in source.pvts if p not in held_pvts],
            )
        )
        _ = train_pvts

    base_agg, res_agg = ErrAgg(), ErrAgg()
    base_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    res_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}

    for inst in test_insts:
        for pvt in test_pvts:
            if not source.has_group(inst, pvt):
                continue
            for key in keys:
                true_toks = parse_tokens(source.get(inst, pvt, key))  # type: ignore[arg-type]
                if mode == "loi":
                    prior_toks = idw_nn.prior_tokens_for_group(
                        source,
                        inst,
                        pvt,
                        key,
                        exclude_instances=set(held_instances or set()),
                    )
                    nn_pp = source.pvt_parts[pvt]
                else:
                    prior_toks = _prior_leave_one_pvt(
                        source, inst, pvt, key, held_pvts or set()
                    )
                    nn_name = nearest_pvt_excluding(
                        pvt, source, held_pvts or set()
                    )
                    nn_pp = source.pvt_parts[nn_name]

                for t, p in zip(true_toks, prior_toks):
                    e = _rel_err(p, t)
                    base_agg.add(e)
                    base_by[key].add(e)

                model = models.get(key)
                apply = True
                if mode == "lop" and pvt_apply_keys is not None:
                    apply = key in pvt_apply_keys
                if model is None or not apply:
                    hat_toks = prior_toks
                else:
                    hat_toks = predict_residual_tokens(
                        model,
                        source,
                        inst,
                        pvt,
                        key,
                        prior_toks,
                        nn_pp=nn_pp,
                    )
                for t, h in zip(true_toks, hat_toks):
                    e = _rel_err(h, t)
                    res_agg.add(e)
                    res_by[key].add(e)
    return base_agg, res_agg, base_by, res_by


def run_holdout(
    source: SourceDB,
    keys: list[str] | None = None,
    seed: int = RANDOM_SEED,
) -> dict:
    keys = list(keys or CORE_KEYS)
    keys = [k for k in keys if k in source.field_keys and k not in AXIS_KEYS]

    loi_base, loi_res = ErrAgg(), ErrAgg()
    loi_base_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    loi_res_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    loi_folds = [i for i in LOI_INSTANCES if i in source.instances]
    for inst in loi_folds:
        b, r, bb, rb = eval_holdout_fold(
            source, held_instances={inst}, held_pvts=None, keys=keys, seed=seed
        )
        loi_base.extend(b)
        loi_res.extend(r)
        for k in keys:
            loi_base_by[k].extend(bb[k])
            loi_res_by[k].extend(rb[k])

    lop_base, lop_res = ErrAgg(), ErrAgg()
    lop_base_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    lop_res_by: dict[str, ErrAgg] = {k: ErrAgg() for k in keys}
    lop_folds = [p for p in LOP_PVTS if p in source.pvts]
    for pvt in lop_folds:
        b, r, bb, rb = eval_holdout_fold(
            source, held_instances=None, held_pvts={pvt}, keys=keys, seed=seed
        )
        lop_base.extend(b)
        lop_res.extend(r)
        for k in keys:
            lop_base_by[k].extend(bb[k])
            lop_res_by[k].extend(rb[k])

    lb, lr = loi_base.summary(), loi_res.summary()
    pb, pr = lop_base.summary(), lop_res.summary()
    # AB-hard: p95_selected ≤ p95_idw_nn (equality allowed; unify with H3-hard).
    # Legacy IDs P-LOP / P-LOI-base kept as aliases of AB-hard-LOP / AB-hard-LOI.
    from .ab_hard import GATE_AB_LOI, GATE_AB_LOP, GATE_ALIAS_LOI, GATE_ALIAS_LOP, GATE_LOI_REG
    from .ab_hard import evaluate_ab_hard_gates

    ab_ok, ab_gates, ab_detail = evaluate_ab_hard_gates(
        float(lr["p95"]),
        float(lb["p95"]),
        float(pr["p95"]),
        float(pb["p95"]),
        p95_loi_reg_ok=float(lr["p95"]) <= LOI_REG_MAX,
    )
    gates = {
        GATE_AB_LOP: ab_gates[GATE_AB_LOP],
        GATE_AB_LOI: ab_gates[GATE_AB_LOI],
        GATE_ALIAS_LOP: ab_gates[GATE_ALIAS_LOP],
        GATE_ALIAS_LOI: ab_gates[GATE_ALIAS_LOI],
        GATE_LOI_REG: float(lr["p95"]) <= LOI_REG_MAX,
        "P-LOI-reg+": float(lr["p95"]) <= LOI_PREV_P95,
    }

    return {
        "keys": keys,
        "loi_folds": loi_folds,
        "lop_folds": lop_folds,
        "loi_baseline": lb,
        "loi_residual": lr,
        "lop_baseline": pb,
        "lop_residual": pr,
        "loi_by_key": {
            k: {"baseline": loi_base_by[k].summary(), "residual": loi_res_by[k].summary()}
            for k in keys
        },
        "lop_by_key": {
            k: {"baseline": lop_base_by[k].summary(), "residual": lop_res_by[k].summary()}
            for k in keys
        },
        "gates": gates,
        "ab_hard_ok": ab_ok,
        "ab_hard_detail": ab_detail,
        "loi_prev_p95": LOI_PREV_P95,
        "loi_reg_max": LOI_REG_MAX,
        "eps": EPS,
        "seed": seed,
        "apply_on": "all_extrapolated",
        "heads": "models_geom+models_pvt",
        "backend": "residual_gbdt",
    }


def train_full_model(
    source: SourceDB,
    keys: list[str] | None = None,
    seed: int = RANDOM_SEED,
) -> dict:
    """Train dual-head residual models on all A_ref."""
    n_axis, tran_axis, load_axis = _axis_from_source(source)
    if keys is None:
        keys = [k for k in source.field_keys if k not in AXIS_KEYS]
    else:
        keys = [k for k in keys if k not in AXIS_KEYS]
    t0 = time.time()
    print("[train_lib] building geom (leave-instance) XY…")
    xy_geom = build_xy_geom(source, keys)
    print("[train_lib] building pvt (leave-pvt) XY…")
    xy_pvt = build_xy_pvt(source, keys, per_point_leave=True)
    print("[train_lib] fitting geom head…")
    models_geom = fit_models(xy_geom, seed=seed, head="geom")
    print("[train_lib] fitting pvt head…")
    models_pvt = fit_models(xy_pvt, seed=seed, head="pvt")
    pvt_apply_keys = select_pvt_apply_keys(source, keys)
    print(
        f"[train_lib] pvt_apply_keys ({len(pvt_apply_keys)}/"
        f"{len(keys)}): {pvt_apply_keys[:12]}{'…' if len(pvt_apply_keys)>12 else ''}"
    )
    elapsed = time.time() - t0
    bundle = {
        "version": 2,
        "backend": "residual_gbdt",
        "prior": "idw_nn",
        "apply_on_default": "all_extrapolated",
        "heads": ["models_geom", "models_pvt"],
        "pvt_apply_keys": list(pvt_apply_keys),
        "pvt_apply_prior_p95_thr": PVT_APPLY_PRIOR_P95_THR,
        "random_seed": seed,
        "feature_names": list(FEATURE_NAMES),
        "n_axis": n_axis,
        "tran_axis": tran_axis,
        "load_axis": load_axis,
        "keys_trained": sorted(set(models_geom) | set(models_pvt)),
        "n_train_rows_geom": {k: int(xy_geom[k][0].shape[0]) for k in models_geom},
        "n_train_rows_pvt": {k: int(xy_pvt[k][0].shape[0]) for k in models_pvt},
        "models_geom": models_geom,
        "models_pvt": models_pvt,
        # Legacy single-head alias → geom (geom_only / old loaders)
        "models": models_geom,
        "trained_at": datetime.now(tz=SHANGHAI).isoformat(timespec="seconds"),
        "source_path": str(source.path),
        "train_seconds": elapsed,
        "note": (
            "DEMO synthetic dual-head residual models; not physical/PDK calibration. "
            "models_geom: leave-instance; models_pvt: leave-pvt."
        ),
    }
    return bundle


def save_bundle(bundle: dict, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path, compress=3)
    return path


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def write_holdout_report(
    report: dict, path: Path, model_path: Path | None = None
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(tz=SHANGHAI).strftime("%Y-%m-%d %H:%M:%S %Z")
    lb, lr = report["loi_baseline"], report["loi_residual"]
    pb, pr = report["lop_baseline"], report["lop_residual"]
    gates = report.get("gates") or {}
    prev = report.get("loi_prev_p95", LOI_PREV_P95)
    reg_max = report.get("loi_reg_max", LOI_REG_MAX)

    def gmark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = [
        "# EPC Algorithm Hold-out Report — residual_gbdt vs idw_nn",
        "",
        f"- Generated: **{now}** (Asia/Shanghai)",
        f"- Protocol: LOI ({len(report['loi_folds'])} folds) + LOP ({len(report['lop_folds'])} folds)",
        f"- Core keys: `{', '.join(report['keys'])}`",
        f"- ε = `{report['eps']}`; random_seed = `{report['seed']}`",
        f"- Relative error: `|hat-true|/max(|true|,ε)` at cell level",
        f"- **apply_on**: `{report.get('apply_on', 'all_extrapolated')}` "
        f"(heads=`{report.get('heads', 'dual')}`)",
        f"- **DEMO synthetic only** — not foundry/PDK calibration",
        "",
        "> **Policy (PVT residual v0):** residual on every non-`seed_from_A` "
        "extrapolation (geom / pvt / both). Dual-head: geom←leave-instance, "
        "pvt←leave-pvt.",
        "",
    ]
    if model_path:
        lines.append(
            f"- Production model: `{model_path}` (sha256[:16]={sha16(model_path)})"
        )

    p_ab_lop = gates.get("AB-hard-LOP", gates.get("P-LOP", pr["p95"] <= pb["p95"]))
    p_ab_loi = gates.get("AB-hard-LOI", gates.get("P-LOI-base", lr["p95"] <= lb["p95"]))
    p_lop = p_ab_lop  # alias
    p_loi_base = p_ab_loi  # alias
    p_loi_reg = gates.get("P-LOI-reg", lr["p95"] <= reg_max)
    p_loi_reg_plus = gates.get("P-LOI-reg+", lr["p95"] <= prev)
    all_hard = p_ab_lop and p_ab_loi and p_loi_reg
    d_loi = float(lr["p95"]) - float(lb["p95"])
    d_lop = float(pr["p95"]) - float(pb["p95"])
    backend = report.get("backend", "residual_gbdt")

    lines += [
        "",
        "## Acceptance gates (AB-hard / PVT residual)",
        "",
        f"| ID | Criterion | p95_selected | p95_idw_nn | delta | backend | protocol | Result |",
        f"|---|---|---|---|---|---|---|---|",
        f"| **AB-hard-LOP** | p95_sel ≤ p95_idw | "
        f"{pr['p95']:.6g} | {pb['p95']:.6g} | {d_lop:.6g} | `{backend}` | `lop_v0` | "
        f"**{gmark(p_ab_lop)}** |",
        f"| **AB-hard-LOI** | p95_sel ≤ p95_idw | "
        f"{lr['p95']:.6g} | {lb['p95']:.6g} | {d_loi:.6g} | `{backend}` | `loi_v0` | "
        f"**{gmark(p_ab_loi)}** |",
        f"| **P-LOI-reg** | p95_residual ≤ prev×1.05 | "
        f"{lr['p95']:.6g} | (reg) | — | `{backend}` | `loi_v0` | "
        f"**{gmark(p_loi_reg)}** |",
        f"| P-LOI-reg+ (bonus) | p95_residual ≤ prev | "
        f"{lr['p95']:.6g} | (prev={prev:.6g}) | — | `{backend}` | `loi_v0` | "
        f"**{gmark(p_loi_reg_plus)}** |",
        f"| alias P-LOP | = AB-hard-LOP (legacy strict-< → ≤) | "
        f"{pr['p95']:.6g} | {pb['p95']:.6g} | {d_lop:.6g} | `{backend}` | `lop_v0` | "
        f"**{gmark(p_lop)}** |",
        f"| alias P-LOI-base | = AB-hard-LOI (legacy strict-< → ≤) | "
        f"{lr['p95']:.6g} | {lb['p95']:.6g} | {d_loi:.6g} | `{backend}` | `loi_v0` | "
        f"**{gmark(p_loi_base)}** |",
        "",
        f"**Hard gates overall: {'ALL PASS' if all_hard else 'FAIL'}** "
        f"(AB-hard-LOI ∧ AB-hard-LOP ∧ P-LOI-reg; compare `≤`)",
        "",
        "## Summary table",
        "",
        f"| Protocol | baseline idw_nn p95 | residual_gbdt p95 | n | ≤ idw? |",
        f"|---|---|---|---|---|",
        f"| **LOI** (`loi_v0`) | {lb['p95']:.6g} | {lr['p95']:.6g} | {lr['n']} | "
        f"{'YES' if lr['p95'] <= lb['p95'] else 'NO'} |",
        f"| **LOP** (`lop_v0`) | {pb['p95']:.6g} | {pr['p95']:.6g} | {pr['n']} | "
        f"{'YES' if pr['p95'] <= pb['p95'] else 'NO'} |",
        "",
        f"- LOI p50 baseline={lb['p50']:.6g} residual={lr['p50']:.6g}",
        f"- LOI max baseline={lb['max']:.6g} residual={lr['max']:.6g}",
        f"- LOP p50 baseline={pb['p50']:.6g} residual={pr['p50']:.6g}",
        f"- LOP max baseline={pb['max']:.6g} residual={pr['max']:.6g}",
        "",
        "### LOI folds",
        "",
    ]
    for x in report["loi_folds"]:
        lines.append(f"- `{x}`")
    lines += ["", "### LOP folds", ""]
    for x in report["lop_folds"]:
        lines.append(f"- `{x}`")

    lines += [
        "",
        "## Per-key LOI (p95)",
        "",
        "| key | baseline p95 | residual p95 | Δ |",
        "|---|---|---|---|",
    ]
    for k in report["keys"]:
        b = report["loi_by_key"][k]["baseline"]["p95"]
        r = report["loi_by_key"][k]["residual"]["p95"]
        lines.append(f"| `{k}` | {b:.6g} | {r:.6g} | {r-b:.6g} |")

    lines += [
        "",
        "## Per-key LOP (p95)",
        "",
        "| key | baseline p95 | residual p95 | Δ |",
        "|---|---|---|---|",
    ]
    for k in report["keys"]:
        b = report["lop_by_key"][k]["baseline"]["p95"]
        r = report["lop_by_key"][k]["residual"]["p95"]
        lines.append(f"| `{k}` | {b:.6g} | {r:.6g} | {r-b:.6g} |")

    lines += [
        "",
        "## Notes",
        "",
        "- Prior = existing IDW+NN (leave-one-instance / leave-one-pvt).",
        "- Residual = sklearn `HistGradientBoostingRegressor` per key × head; "
        "`prior_hat` + ΔV/ΔT/1/V/V×T/corner-onehot are features.",
        "- Hard gates: **AB-hard-LOI**, **AB-hard-LOP** (≤ idw; aliases P-LOI-base / P-LOP), "
        "**P-LOI-reg** (parallel). Compare unified with H3-hard (`≤`).",
        "- Online `epc_ab` reads AB-hard stamp (sidecar `*.ab_hard.json`); no per-job LOI recompute.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
