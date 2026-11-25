"""Construct backends: idw_nn (baseline) and residual_gbdt."""
from __future__ import annotations

from ..construct_types import ConstructResult
from ..job import ConstructConfig
from ..source import SourceDB
from . import idw_nn, residual_gbdt

SUPPORTED = ("idw_nn", "residual_gbdt")


def run_construct(
    source: SourceDB,
    b_instances: list[str],
    b_pvts: list[str],
    field_keys: list[str],
    cfg: ConstructConfig | None = None,
) -> ConstructResult:
    cfg = cfg or ConstructConfig()
    backend = (cfg.backend or "idw_nn").strip()
    if backend == "idw_nn":
        result = idw_nn.construct(source, b_instances, b_pvts, field_keys)
        result.backend = "idw_nn"
        result.prior = "idw_nn"
        result.fallback_used = False
        result.model_path = None
        return result
    if backend == "residual_gbdt":
        return residual_gbdt.construct(
            source, b_instances, b_pvts, field_keys, cfg
        )
    raise ValueError(
        f"unknown construct.backend={backend!r}; supported={SUPPORTED}"
    )
