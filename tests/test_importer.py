"""Importer tests: arbitrary source schema -> SourceDB via introspection."""
from __future__ import annotations

import sqlite3

import pytest

from epc_engine.importer import (
    inspect_schema,
    load_source_db_flexible,
    resolve_mapping,
)

PARSED_INST = "HINP3TCAM64X8SWISDC"
PARSED_PVT = "TT_0P80V_0P80V_25C"


def _build_realish_db(path, *, include_bad: bool = False) -> None:
    """A foundry-style DB: table `timing`, renamed columns, extra cols."""
    conn = sqlite3.connect(str(path))
    conn.execute(
        "CREATE TABLE timing("
        "cell_name TEXT, corner TEXT, arc TEXT, nominal TEXT, note TEXT)"
    )
    conn.execute(
        "INSERT INTO timing VALUES (?,?,?,?,?)",
        (PARSED_INST, PARSED_PVT, "tcq", "10 20 30", "x"),
    )
    conn.execute(
        "INSERT INTO timing VALUES (?,?,?,?,?)",
        (PARSED_INST, PARSED_PVT, "tcd", "5 5 5", "x"),
    )
    conn.execute(
        "INSERT INTO timing VALUES (?,?,?,?,?)",
        ("HINP3TCAM96X16SWISDC", PARSED_PVT, "tcq", "11 21 31", "x"),
    )
    conn.execute(
        "INSERT INTO timing VALUES (?,?,?,?,?)",
        ("HINP3TCAM96X16SWISDC", PARSED_PVT, "tcd", "6 6 6", "x"),
    )
    if include_bad:
        conn.execute(
            "INSERT INTO timing VALUES (?,?,?,?,?)",
            ("BAD_NAME_42", PARSED_PVT, "tcq", "1 1 1", "x"),
        )
    conn.commit()
    conn.close()


COL_MAP = {
    "instance": "cell_name",
    "pvt": "corner",
    "field_key": "arc",
    "value": "nominal",
}


def test_inspect_schema_lists_user_tables(tmp_path):
    db = tmp_path / "real.db"
    _build_realish_db(db)
    schema = inspect_schema(db)
    assert "timing" in schema
    assert set(schema["timing"]) >= {"cell_name", "corner", "arc", "nominal"}
    assert not any(t.startswith("sqlite_") for t in schema)


def test_load_flexible_with_explicit_table_and_map(tmp_path):
    db = tmp_path / "real.db"
    _build_realish_db(db)
    src = load_source_db_flexible(db, table="timing", col_map=COL_MAP)
    assert src.table == "timing"
    assert src.instances == ["HINP3TCAM64X8SWISDC", "HINP3TCAM96X16SWISDC"]
    assert src.pvts == [PARSED_PVT]
    assert src.field_keys == ["tcd", "tcq"]
    assert len(src.rows) == 4
    assert src.rows[(PARSED_INST, PARSED_PVT, "tcq")] == "10 20 30"
    assert len(src.inst_parts) == 2
    assert src.unparseable == set()


def test_load_flexible_auto_detects_table(tmp_path):
    db = tmp_path / "real.db"
    _build_realish_db(db)
    src = load_source_db_flexible(db, col_map=COL_MAP)
    assert src.table == "timing"
    assert len(src.rows) == 4


def test_load_flexible_contract_default(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "c.db"))
    conn.execute(
        "CREATE TABLE char_data(instance TEXT, pvt TEXT, field_key TEXT, value TEXT)"
    )
    conn.execute(
        "INSERT INTO char_data VALUES (?,?,?,?)",
        (PARSED_INST, PARSED_PVT, "tcq", "1 1 1"),
    )
    conn.commit()
    conn.close()
    src = load_source_db_flexible(tmp_path / "c.db")
    assert src.table == "char_data"
    assert len(src.rows) == 1


def test_unparseable_names_skip_or_raise(tmp_path):
    db = tmp_path / "real.db"
    _build_realish_db(db, include_bad=True)
    src = load_source_db_flexible(db, table="timing", col_map=COL_MAP)
    assert "instance:BAD_NAME_42" in src.unparseable
    assert len(src.rows) == 5  # still loaded
    assert len(src.inst_parts) == 2  # but excluded from IDW candidates
    with pytest.raises(ValueError):
        load_source_db_flexible(
            db, table="timing", col_map=COL_MAP, strict_parse=True
        )


def test_resolve_mapping_errors_are_actionable(tmp_path):
    db = tmp_path / "real.db"
    _build_realish_db(db)
    schema = inspect_schema(db)
    with pytest.raises(ValueError, match="not found"):
        resolve_mapping(schema, table="nope", col_map=None)
    with pytest.raises(ValueError, match="missing mapped columns"):
        resolve_mapping(
            schema,
            table="timing",
            col_map={"instance": "cell_name", "pvt": "no_such_col"},
        )
    with pytest.raises(ValueError, match="no table satisfies mapping"):
        resolve_mapping(
            schema,
            table=None,
            col_map={"instance": "ghost", "pvt": "ghost"},
        )


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_source_db_flexible(tmp_path / "absent.db")
