"""Construct B field values — backend facade (idw_nn | residual_gbdt)."""
from __future__ import annotations

from .construct_types import AXIS_KEYS, CellMeta, ConstructResult
from .job import ConstructConfig
from .source import SourceDB

# Re-export types for constraints / audit
__all__ = [
    "AXIS_KEYS",
    "CellMeta",
    "ConstructResult",
    "ConstructConfig",
    "construct_b",
]


def construct_b(
    source: SourceDB,
    b_instances: list[str],
    b_pvts: list[str],
    field_keys: list[str],
    cfg: ConstructConfig | None = None,
) -> ConstructResult:
    from .backends import run_construct

    return run_construct(source, b_instances, b_pvts, field_keys, cfg)
