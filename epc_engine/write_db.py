"""Write B.db SQLite char_data (atomic tmp+rename; no partial files).

Schema now carries an embedded provenance table `db_meta` (key/value) so every
produced library answers: which YAML, which source DB, which backend/model,
and what the gates said — without opening the audit markdown.
"""
from __future__ import annotations

import hashlib
import math
import os
import sqlite3
from pathlib import Path

from .construct import ConstructResult
from .values import parse_tokens

DB_META_TABLE = "db_meta"
DB_USER_VERSION = 1

SCHEMA = """
CREATE TABLE char_data(
  instance  TEXT,
  pvt       TEXT,
  field_key TEXT,
  value     TEXT,
  PRIMARY KEY(instance, pvt, field_key)
);
"""


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _create_meta_table(cur: sqlite3.Cursor) -> None:
    cur.execute(
        f"CREATE TABLE {DB_META_TABLE} (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )


def write_b_db(
    path: Path,
    result: ConstructResult,
    instances: list[str],
    pvts: list[str],
    meta: dict[str, str] | None = None,
) -> int:
    """Write B.db atomically: build a tmp sibling, then os.replace into place.

    A crash mid-write leaves the previous B.db untouched (or no file on first
    run), never a half-written library. Non-finite values are rejected instead
    of being persisted as the strings "nan"/"inf".
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists():
        tmp.unlink()
    conn = sqlite3.connect(str(tmp))
    n = 0
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA user_version = %d" % DB_USER_VERSION)
        cur.execute(SCHEMA)
        _create_meta_table(cur)
        rows = []
        for inst in instances:
            for pvt in pvts:
                for key in result.field_keys:
                    val = result.data[(inst, pvt, key)]
                    toks = parse_tokens(val)
                    if not all(math.isfinite(t) for t in toks):
                        raise ValueError(
                            f"refusing to write non-finite value for "
                            f"{inst}/{pvt}/{key}: {val!r}"
                        )
                    rows.append((inst, pvt, key, val))
        cur.executemany(
            "INSERT INTO char_data(instance, pvt, field_key, value) VALUES (?,?,?,?)",
            rows,
        )
        cur.execute("CREATE INDEX idx_pvt ON char_data(pvt)")
        cur.execute("CREATE INDEX idx_key ON char_data(field_key)")
        if meta:
            cur.executemany(
                f"INSERT INTO {DB_META_TABLE}(key, value) VALUES (?,?)",
                [(str(k), str(v)) for k, v in meta.items()],
            )
        conn.commit()
        n = len(rows)
    except BaseException:
        conn.close()
        if tmp.exists():
            tmp.unlink()
        raise
    finally:
        try:
            conn.close()
        except sqlite3.Error:
            pass
    os.replace(tmp, path)
    return n


def update_db_meta(path: Path, entries: dict[str, str]) -> None:
    """Append final gate status to an existing B.db (post-G2, success only).

    Best-effort: called only on the final PASS path; a failure here must not
    turn a produced library into a job failure, so it never raises.
    """
    try:
        conn = sqlite3.connect(str(path))
        cur = conn.cursor()
        cur.executemany(
            f"INSERT OR REPLACE INTO {DB_META_TABLE}(key, value) VALUES (?,?)",
            [(str(k), str(v)) for k, v in entries.items()],
        )
        conn.commit()
        conn.close()
    except sqlite3.Error:
        pass


def read_db_meta(path: Path) -> dict[str, str]:
    """Read back the embedded provenance of a produced B.db."""
    conn = sqlite3.connect(str(path))
    try:
        try:
            rows = conn.execute(
                f"SELECT key, value FROM {DB_META_TABLE}"
            ).fetchall()
        except sqlite3.Error:
            rows = []
    finally:
        conn.close()
    return {k: v for k, v in rows}
