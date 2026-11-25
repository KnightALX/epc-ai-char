"""Load source A.db into memory."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .parse import InstanceParts, PvtParts, parse_instance, parse_pvt


@dataclass
class SourceDB:
    path: Path
    # (instance, pvt, field_key) -> value string
    rows: dict[tuple[str, str, str], str] = field(default_factory=dict)
    instances: list[str] = field(default_factory=list)
    pvts: list[str] = field(default_factory=list)
    field_keys: list[str] = field(default_factory=list)
    inst_parts: dict[str, InstanceParts] = field(default_factory=dict)
    pvt_parts: dict[str, PvtParts] = field(default_factory=dict)
    # (instance, pvt) -> {field_key: value}
    groups: dict[tuple[str, str], dict[str, str]] = field(default_factory=dict)

    def get(self, instance: str, pvt: str, key: str) -> str | None:
        return self.rows.get((instance, pvt, key))

    def has_group(self, instance: str, pvt: str) -> bool:
        return (instance, pvt) in self.groups


def load_source_db(path: Path) -> SourceDB:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"source db not found: {path}")
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.execute(
            "SELECT instance, pvt, field_key, value FROM char_data"
        )
        rows: dict[tuple[str, str, str], str] = {}
        groups: dict[tuple[str, str], dict[str, str]] = {}
        inst_set: set[str] = set()
        pvt_set: set[str] = set()
        key_set: set[str] = set()
        for inst, pvt, key, value in cur:
            rows[(inst, pvt, key)] = value
            groups.setdefault((inst, pvt), {})[key] = value
            inst_set.add(inst)
            pvt_set.add(pvt)
            key_set.add(key)
    finally:
        conn.close()

    instances = sorted(inst_set)
    pvts = sorted(pvt_set)
    field_keys = sorted(key_set)

    inst_parts = {}
    for name in instances:
        inst_parts[name] = parse_instance(name)
    pvt_parts = {}
    for name in pvts:
        pvt_parts[name] = parse_pvt(name)

    return SourceDB(
        path=path,
        rows=rows,
        instances=instances,
        pvts=pvts,
        field_keys=field_keys,
        inst_parts=inst_parts,
        pvt_parts=pvt_parts,
        groups=groups,
    )
