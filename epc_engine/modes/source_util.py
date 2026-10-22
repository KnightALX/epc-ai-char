"""SourceDB helpers for P2 modes (subset / copy groups)."""
from __future__ import annotations

from pathlib import Path

from ..parse import parse_instance, parse_pvt
from ..source import SourceDB


def subset_source(
    source: SourceDB,
    *,
    instances: list[str] | None = None,
    pvts: list[str] | None = None,
) -> SourceDB:
    """Return a SourceDB view restricted to given instances and/or pvts."""
    inst_allow = set(instances) if instances is not None else None
    pvt_allow = set(pvts) if pvts is not None else None
    rows = {}
    groups = {}
    for (inst, pvt, key), val in source.rows.items():
        if inst_allow is not None and inst not in inst_allow:
            continue
        if pvt_allow is not None and pvt not in pvt_allow:
            continue
        rows[(inst, pvt, key)] = val
        groups.setdefault((inst, pvt), {})[key] = val
    inst_set = sorted({k[0] for k in groups})
    pvt_set = sorted({k[1] for k in groups})
    key_set = sorted({k[2] for k in rows})
    inst_parts = {n: parse_instance(n) for n in inst_set}
    pvt_parts = {n: parse_pvt(n) for n in pvt_set}
    return SourceDB(
        path=source.path,
        rows=rows,
        instances=inst_set,
        pvts=pvt_set,
        field_keys=key_set,
        inst_parts=inst_parts,
        pvt_parts=pvt_parts,
        groups=groups,
    )


def clone_empty_like(path: Path) -> SourceDB:
    return SourceDB(path=path)
