"""Shared construct result types (avoid circular imports with backends)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


AXIS_KEYS = ("tran_index", "load_index")


@dataclass
class CellMeta:
    status: str  # seed_from_A | migrated | config_extrapolated | pvt_extrapolated | ...
    extrapolated: bool = False
    notes: str = ""
    residual_applied: bool = False
    residual_reason: str = ""  # seed_from_A | geom | pvt | both | fallback | geom_only_skip


@dataclass
class ConstructResult:
    # (instance, pvt, key) -> value str
    data: dict[tuple[str, str, str], str] = field(default_factory=dict)
    meta: dict[tuple[str, str], CellMeta] = field(default_factory=dict)
    field_keys: list[str] = field(default_factory=list)
    n: int = 5
    # Audit / backend provenance
    backend: str = "idw_nn"
    prior: str = "idw_nn"
    fallback_used: bool = False
    model_path: Path | None = None
    model_sha16: str | None = None
    apply_on: str = "all_extrapolated"
