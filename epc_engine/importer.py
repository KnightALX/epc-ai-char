"""Real-database import adapter: arbitrary source schema -> SourceDB.

Contract databases use table `char_data(instance, pvt, field_key, value)`.
Real foundry/characterization DBs rarely do. This module introspects the
schema and maps physical columns onto the logical four, so downstream
(backends, constraints, gates) never knows the difference.

YAML usage (all optional; defaults are the contract schema):
    source:
      db_path: /path/to/real.db
      table: timing_arcs          # default: char_data (auto-detected if absent)
      col_map:                    # default: identity on the four logical names
        instance: cell_name
        pvt: pvt_corner
        field_key: arc
        value: nominal
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .parse import InstanceParts, parse_instance, parse_pvt
from .source import SourceDB

LOGICAL_COLUMNS = ("instance", "pvt", "field_key", "value")


def inspect_schema(path: Path) -> dict[str, list[str]]:
    """Return {table_name: [columns]} for every user table in the DB."""
    conn = sqlite3.connect(str(path))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        out: dict[str, list[str]] = {}
        for (name,) in rows:
            cols = conn.execute(f'PRAGMA table_info("{name}")').fetchall()
            out[name] = [c[1] for c in cols]
    finally:
        conn.close()
    return out


def resolve_mapping(
    schema: dict[str, list[str]],
    table: str | None,
    col_map: dict[str, str] | None,
) -> tuple[str, dict[str, str]]:
    """Pick the source table and the logical->physical column mapping.

    Raises ValueError with an actionable message when the mapping cannot be
    satisfied (missing table / column), instead of loading garbage.
    """
    cmap = dict(col_map or {})
    for logical in LOGICAL_COLUMNS:
        cmap.setdefault(logical, logical)

    if table is not None:
        if table not in schema:
            raise ValueError(
                f"source.table={table!r} not found; tables: {sorted(schema)}"
            )
        missing = [l for l in LOGICAL_COLUMNS if cmap[l] not in schema[table]]
        if missing:
            raise ValueError(
                f"table {table!r} missing mapped columns "
                f"{ {l: cmap[l] for l in missing} }; has {schema[table]}"
            )
        return table, cmap

    # auto-detect: prefer char_data; else any table containing all 4 mapped cols
    if "char_data" in schema:
        missing = [l for l in LOGICAL_COLUMNS if cmap[l] not in schema["char_data"]]
        if not missing:
            return "char_data", cmap
    for tname, cols in schema.items():
        if all(cmap[l] in cols for l in LOGICAL_COLUMNS):
            return tname, cmap
    raise ValueError(
        f"no table satisfies mapping {cmap}; schema: "
        f"{ {t: c for t, c in schema.items()} }"
    )


def load_source_db_flexible(
    path: Path,
    *,
    table: str | None = None,
    col_map: dict[str, str] | None = None,
    strict_parse: bool = False,
) -> SourceDB:
    """Load any SQLite char DB into a SourceDB via schema introspection.

    strict_parse=False: rows whose instance/pvt fail to parse are still loaded
    but excluded from inst_parts/pvt_parts (so IDW candidates ignore them).
    The caller can detect this via the returned `unparseable` attribute.
    strict_parse=True: raise on the first unparseable name.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"source db not found: {path}")
    schema = inspect_schema(path)
    tname, cmap = resolve_mapping(schema, table, col_map)
    cols = schema[tname]

    inst_c = cmap["instance"]
    pvt_c = cmap["pvt"]
    key_c = cmap["field_key"]
    val_c = cmap["value"]

    conn = sqlite3.connect(str(path))
    try:
        cur = conn.execute(
            f'SELECT "{inst_c}", "{pvt_c}", "{key_c}", "{val_c}" FROM "{tname}"'
        )
        rows: dict[tuple[str, str, str], str] = {}
        groups: dict[tuple[str, str], dict[str, str]] = {}
        inst_set: set[str] = set()
        pvt_set: set[str] = set()
        key_set: set[str] = set()
        unparseable: set[str] = set()
        for inst, pvt, key, value in cur:
            rows[(inst, pvt, key)] = value
            groups.setdefault((inst, pvt), {})[key] = value
            inst_set.add(inst)
            pvt_set.add(pvt)
            key_set.add(key)
    finally:
        conn.close()

    inst_parts: dict[str, InstanceParts] = {}
    pvt_parts: dict[str, object] = {}
    for name in sorted(inst_set):
        try:
            inst_parts[name] = parse_instance(name)
        except ValueError:
            unparseable.add(f"instance:{name}")
            if strict_parse:
                raise
    for name in sorted(pvt_set):
        try:
            pvt_parts[name] = parse_pvt(name)  # type: ignore[assignment]
        except ValueError:
            unparseable.add(f"pvt:{name}")
            if strict_parse:
                raise

    src = SourceDB(
        path=path,
        rows=rows,
        instances=sorted(inst_set),
        pvts=sorted(pvt_set),
        field_keys=sorted(key_set),
        inst_parts=inst_parts,
        pvt_parts=pvt_parts,  # type: ignore[arg-type]
        groups=groups,
    )
    src.unparseable = unparseable  # type: ignore[attr-defined]
    src.table = tname  # type: ignore[attr-defined]
    return src
