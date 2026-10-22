"""Read-only sqlite char_data access with pagination."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class CharDb:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(str(self.path))
        self._conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "CharDb":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0])

    def distinct(self, col: str) -> list[str]:
        if col not in ("instance", "pvt", "field_key"):
            raise ValueError(col)
        rows = self._conn.execute(
            f"SELECT DISTINCT {col} FROM char_data ORDER BY {col}"
        ).fetchall()
        return [r[0] for r in rows]

    def page(
        self,
        *,
        instance: str | None = None,
        pvt: str | None = None,
        key: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        wheres: list[str] = []
        args: list[Any] = []
        if instance:
            wheres.append("instance = ?")
            args.append(instance)
        if pvt:
            wheres.append("pvt = ?")
            args.append(pvt)
        if key:
            wheres.append("field_key = ?")
            args.append(key)
        where = (" WHERE " + " AND ".join(wheres)) if wheres else ""
        sql = (
            f"SELECT instance, pvt, field_key, value FROM char_data{where} "
            f"ORDER BY instance, pvt, field_key LIMIT ? OFFSET ?"
        )
        args.extend([limit, offset])
        rows = self._conn.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

    def get_value(self, instance: str, pvt: str, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM char_data WHERE instance=? AND pvt=? AND field_key=?",
            (instance, pvt, key),
        ).fetchone()
        return None if row is None else str(row[0])

    def exists(self) -> bool:
        return self.path.is_file()
