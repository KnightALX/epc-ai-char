"""Cross-process Transfer: linear Transfer Ratio + Residual TL.

Protocol helpers shared by offline hold-out and online transfer_ab mode.
No stamp. Does not touch AB-hard / LON / H3 semantics.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

from .backends.features import cell_coords, feature_row
from .construct_types import AXIS_KEYS
from .parse import parse_instance, parse_pvt
from .source import SourceDB, load_source_db
from .train_lib import CORE_KEYS, EPS, RANDOM_SEED, ErrAgg, _axis_from_source, _rel_err
from .values import format_tokens, parse_tokens

PROTOCOL_ID = "transfer_holdout_v0"
GATE_TRANSFER = "TRANSFER-hard"
WARP_ID_DEFAULT = "warp_nl_v0"


def _finite(x: float) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def evaluate_transfer_hard_gates(
    p95_rtl: float,
    p95_tr: float,
) -> tuple[bool, dict[str, bool], dict[str, Any]]:
    """TRANSFER-hard: p95_RTL ≤ p95_TR (equality OK)."""
    ok = (
        _finite(p95_rtl)
        and _finite(p95_tr)
        and float(p95_rtl) <= float(p95_tr)
    )
    gates = {GATE_TRANSFER: ok}
    detail = {
        "protocol": PROTOCOL_ID,
        "p95_residual_tl": p95_rtl,
        "p95_linear_tr": p95_tr,
        "delta": (float(p95_rtl) - float(p95_tr)) if ok or (_finite(p95_rtl) and _finite(p95_tr)) else float("nan"),
        "pass": ok,
        "compare": "<=",
        "note": "TRANSFER-hard uses ≤ (unify with AB/LON/H3). No stamp this round.",
    }
    return ok, gates, detail


def estimate_transfer_ratios(
    src: SourceDB,
    seed: SourceDB,
    keys: list[str],
) -> dict[str, float]:
    """Global per-key median ratio r = tgt/src on seed-aligned locators.

    Forbidden to use hold-out truth. Axes skipped.
    """
    ratios: dict[str, list[float]] = {k: [] for k in keys}
    for (inst, pvt), g in seed.groups.items():
        if not src.has_group(inst, pvt):
            continue
        for key in keys:
            if key in AXIS_KEYS:
                continue
            tv = g.get(key)
            sv = src.get(inst, pvt, key)
            if tv is None or sv is None:
                continue
            t_toks = parse_tokens(tv)
            s_toks = parse_tokens(sv)
            if len(t_toks) != len(s_toks):
                continue
            for t, s in zip(t_toks, s_toks):
                if abs(s) < EPS:
                    continue
                ratios[key].append(float(t) / float(s))
    out: dict[str, float] = {}
    for key, rs in ratios.items():
        if not rs:
            out[key] = 1.0
        else:
            out[key] = float(np.median(np.asarray(rs, dtype=np.float64)))
    return out


def apply_linear_tr(
    src_val: str,
    key: str,
    ratios: dict[str, float],
) -> str:
    if key in AXIS_KEYS:
        return src_val
    r = float(ratios.get(key, 1.0))
    toks = parse_tokens(src_val)
    return format_tokens([r * t for t in toks])


def prior_tr_tokens(
    src: SourceDB,
    inst: str,
    pvt: str,
    key: str,
    ratios: dict[str, float],
) -> list[float] | None:
    sv = src.get(inst, pvt, key)
    if sv is None:
        return None
    if key in AXIS_KEYS:
        return parse_tokens(sv)
    r = float(ratios.get(key, 1.0))
    return [r * t for t in parse_tokens(sv)]


def _make_tl_regressor(seed: int = RANDOM_SEED) -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        max_depth=6,
        max_iter=140,
        learning_rate=0.08,
        min_samples_leaf=6,
        l2_regularization=0.05,
        random_state=seed,
    )


def build_xy_transfer(
    src: SourceDB,
    seed: SourceDB,
    keys: list[str],
    ratios: dict[str, float],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Residual labels on seed: truth_tgt − prior_tr; features include prior_tr."""
    n_axis, tran_axis, load_axis = _axis_from_source(src)
    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for key in keys:
        if key in AXIS_KEYS:
            continue
        X_rows: list[list[float]] = []
        y_rows: list[float] = []
        for (inst, pvt), g in seed.groups.items():
            if not src.has_group(inst, pvt):
                continue
            tv = g.get(key)
            if tv is None:
                continue
            prior = prior_tr_tokens(src, inst, pvt, key, ratios)
            if prior is None:
                continue
            true_toks = parse_tokens(tv)
            if len(true_toks) != len(prior):
                continue
            ip = parse_instance(inst)
            pp = parse_pvt(pvt)
            coords = cell_coords(len(true_toks), n_axis)
            for flat_i, i, j in coords:
                tran_v = tran_axis[i] if i < len(tran_axis) else float(i)
                load_v = load_axis[j] if j < len(load_axis) else float(j)
                if len(true_toks) == 1:
                    tran_v, load_v = 0.0, 0.0
                ph = prior[flat_i]
                X_rows.append(
                    feature_row(
                        ip,
                        pp,
                        cell_i=i,
                        cell_j=j,
                        tran_val=tran_v,
                        load_val=load_v,
                        prior_hat=ph,
                        nn_pp=pp,  # same pvt aligned; ΔV/ΔT = 0
                    )
                )
                y_rows.append(true_toks[flat_i] - ph)
        if X_rows:
            out[key] = (
                np.asarray(X_rows, dtype=np.float64),
                np.asarray(y_rows, dtype=np.float64),
            )
    return out


def fit_transfer_models(
    xy: dict[str, tuple[np.ndarray, np.ndarray]],
    seed: int = RANDOM_SEED,
) -> dict[str, HistGradientBoostingRegressor]:
    models: dict[str, HistGradientBoostingRegressor] = {}
    for key, (X, y) in xy.items():
        if X.shape[0] < 16:
            continue
        m = _make_tl_regressor(seed)
        m.fit(X, y)
        models[key] = m
    return models


def predict_rtl_tokens(
    model: HistGradientBoostingRegressor | None,
    src: SourceDB,
    inst: str,
    pvt: str,
    key: str,
    prior_toks: list[float],
) -> list[float]:
    if model is None:
        return list(prior_toks)
    n_axis, tran_axis, load_axis = _axis_from_source(src)
    ip = parse_instance(inst)
    pp = parse_pvt(pvt)
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
                nn_pp=pp,
            )
        )
    resid = model.predict(np.asarray(X_rows, dtype=np.float64))
    return [float(prior_toks[k] + resid[k]) for k in range(len(prior_toks))]


@dataclass
class TransferBundle:
    ratios: dict[str, float]
    models: dict[str, Any] = field(default_factory=dict)
    keys: list[str] = field(default_factory=list)
    backend: str = "residual_tl"
    seed_n_groups: int = 0
    protocol: str = PROTOCOL_ID


def train_transfer_bundle(
    src: SourceDB,
    seed: SourceDB,
    keys: list[str] | None = None,
    *,
    backend: str = "residual_tl",
    rng_seed: int = RANDOM_SEED,
) -> TransferBundle:
    keys = list(keys or CORE_KEYS)
    keys = [k for k in keys if k in src.field_keys and k not in AXIS_KEYS]
    # For online: also train on all non-axis keys present in both
    ratios = estimate_transfer_ratios(src, seed, keys)
    models: dict[str, Any] = {}
    if backend == "residual_tl":
        xy = build_xy_transfer(src, seed, keys, ratios)
        models = fit_transfer_models(xy, seed=rng_seed)
    return TransferBundle(
        ratios=ratios,
        models=models,
        keys=keys,
        backend=backend,
        seed_n_groups=len(seed.groups),
        protocol=PROTOCOL_ID,
    )


def predict_group_value(
    bundle: TransferBundle,
    src: SourceDB,
    inst: str,
    pvt: str,
    key: str,
) -> str | None:
    sv = src.get(inst, pvt, key)
    if sv is None:
        return None
    if key in AXIS_KEYS:
        return sv
    prior = prior_tr_tokens(src, inst, pvt, key, bundle.ratios)
    if prior is None:
        return None
    if bundle.backend == "linear_tr":
        return format_tokens(prior)
    model = bundle.models.get(key)
    hat = predict_rtl_tokens(model, src, inst, pvt, key, prior)
    return format_tokens(hat)


def load_pair(
    src_path: Path,
    seed_path: Path,
) -> tuple[SourceDB, SourceDB]:
    return load_source_db(Path(src_path)), load_source_db(Path(seed_path))
