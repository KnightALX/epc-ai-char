"""Write B.db SQLite char_data."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .construct import ConstructResult


SCHEMA = """
CREATE TABLE char_data(
  instance  TEXT,
  pvt       TEXT,
  field_key TEXT,
  value     TEXT,
  PRIMARY KEY(instance, pvt, field_key)
);
"""


def write_b_db(
    path: Path,
    result: ConstructResult,
    instances: list[str],
    pvts: list[str],
) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.cursor()
        cur.execute(SCHEMA)
        rows = []
        for inst in instances:
            for pvt in pvts:
                for key in result.field_keys:
                    val = result.data[(inst, pvt, key)]
                    rows.append((inst, pvt, key, val))
        cur.executemany(
            "INSERT INTO char_data(instance, pvt, field_key, value) VALUES (?,?,?,?)",
            rows,
        )
        cur.execute("CREATE INDEX idx_inst ON char_data(instance)")
        cur.execute("CREATE INDEX idx_pvt ON char_data(pvt)")
        cur.execute("CREATE INDEX idx_key ON char_data(field_key)")
        conn.commit()
        return len(rows)
    finally:
        conn.close()
