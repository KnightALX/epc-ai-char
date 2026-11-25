"""Feature vectors for residual GBDT (geometry + PVT + cell + prior_hat)."""
from __future__ import annotations

import math

from ..parse import InstanceParts, PvtParts

# Corner one-hot order: SS / TT / FF (unknown → all 0)
FEATURE_NAMES = [
    "log2_depth",
    "log2_width",
    "corner_rank",
    "corner_ss",
    "corner_tt",
    "corner_ff",
    "vdd",
    "vddp",
    "temp",
    "inv_vdd",
    "v_x_t",
    "delta_v",
    "delta_vddp",
    "delta_t",
    "nn_vdd",
    "nn_temp",
    "cell_i",
    "cell_j",
    "tran_val",
    "load_val",
    "prior_hat",
]


def _corner_onehot(pp: PvtParts) -> tuple[float, float, float]:
    c = pp.corner.upper()
    if c.startswith("SS"):
        return 1.0, 0.0, 0.0
    if c.startswith("TT"):
        return 0.0, 1.0, 0.0
    if c.startswith("FF"):
        return 0.0, 0.0, 1.0
    return 0.0, 0.0, 0.0


def geom_pvt_base(
    ip: InstanceParts,
    pp: PvtParts,
    *,
    nn_pp: PvtParts | None = None,
) -> list[float]:
    """Geometry + PVT block; nn_pp supplies ΔV/ΔT vs the prior's NN pvt."""
    ss, tt, ff = _corner_onehot(pp)
    v = max(float(pp.vdd), 1e-6)
    ref = nn_pp if nn_pp is not None else pp
    return [
        math.log2(max(ip.depth, 1)),
        math.log2(max(ip.width, 1)),
        float(pp.corner_rank),
        ss,
        tt,
        ff,
        float(pp.vdd),
        float(pp.vddp),
        float(pp.temp),
        1.0 / v,
        float(pp.vdd) * float(pp.temp),
        float(pp.vdd) - float(ref.vdd),
        float(pp.vddp) - float(ref.vddp),
        float(pp.temp) - float(ref.temp),
        float(ref.vdd),
        float(ref.temp),
    ]


def feature_row(
    ip: InstanceParts,
    pp: PvtParts,
    *,
    cell_i: int,
    cell_j: int,
    tran_val: float,
    load_val: float,
    prior_hat: float,
    nn_pp: PvtParts | None = None,
) -> list[float]:
    return geom_pvt_base(ip, pp, nn_pp=nn_pp) + [
        float(cell_i),
        float(cell_j),
        float(tran_val),
        float(load_val),
        float(prior_hat),
    ]


def cell_coords(n_tokens: int, n_axis: int) -> list[tuple[int, int, int]]:
    """Return list of (flat_idx, i, j) for scalar or N×N table."""
    if n_tokens == 1:
        return [(0, 0, 0)]
    if n_tokens == n_axis * n_axis:
        out = []
        for i in range(n_axis):
            for j in range(n_axis):
                out.append((i * n_axis + j, i, j))
        return out
    # unexpected length: treat as flat vector with j=0
    return [(k, k, 0) for k in range(n_tokens)]
