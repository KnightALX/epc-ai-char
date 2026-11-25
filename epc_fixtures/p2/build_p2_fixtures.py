#!/usr/bin/env python3
"""Build P2 punched/sparse DBs and lists under <repo>/epc_fixtures/p2/ (script directory)."""
from __future__ import annotations

import random
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
A_REF = ROOT.parent / "A_ref.db"

INTERIOR = "HINP3TCAM256X32SWISDC"
PVT8 = [
    "TT_0P80V_0P80V_25C",
    "TT_0P90V_0P90V_25C",
    "SSGNP_0P99V_0P99V_125C",
    "SSGNP_0P675V_0P675V_125C",
    "FFGNP_0P675V_0P675V_M40C",
    "FFGNP_1P05V_1P05V_25C",
    "TT_0P80V_0P80V_125C",
    "SSGNP_0P90V_0P90V_25C",
]
SPARSE_SEED_PVTS = [
    "TT_0P80V_0P80V_25C",
    "SSGNP_0P99V_0P99V_125C",
    "FFGNP_0P675V_0P675V_M40C",
    "TT_0P90V_0P90V_25C",
]
AXIS = {"tran_index", "load_index"}


def copy_subset(src: Path, dst: Path, instances: list[str], pvts: list[str]) -> int:
    if dst.exists():
        dst.unlink()
    conn_s = sqlite3.connect(str(src))
    conn_d = sqlite3.connect(str(dst))
    try:
        conn_d.execute(
            "CREATE TABLE char_data(instance TEXT, pvt TEXT, field_key TEXT, value TEXT, "
            "PRIMARY KEY(instance, pvt, field_key))"
        )
        rows = []
        q = (
            "SELECT instance, pvt, field_key, value FROM char_data "
            "WHERE instance=? AND pvt=?"
        )
        for inst in instances:
            for pvt in pvts:
                rows.extend(conn_s.execute(q, (inst, pvt)))
        conn_d.executemany(
            "INSERT INTO char_data(instance, pvt, field_key, value) VALUES (?,?,?,?)",
            rows,
        )
        conn_d.commit()
        return len(rows)
    finally:
        conn_s.close()
        conn_d.close()


def punch_holes(db: Path, frac: float = 0.012, seed: int = 42) -> list[tuple]:
    """Punch holes but keep ≥1 donor per (pvt,key)."""
    rng = random.Random(seed)
    conn = sqlite3.connect(str(db))
    try:
        cells = [
            (i, p, k, v)
            for i, p, k, v in conn.execute(
                "SELECT instance, pvt, field_key, value FROM char_data"
            )
            if k not in AXIS
        ]
        by: dict[tuple[str, str], list] = defaultdict(list)
        for c in cells:
            by[(c[1], c[2])].append(c)
        candidates = [c for lst in by.values() if len(lst) > 1 for c in lst]
        n_punch = min(max(1, int(len(cells) * frac)), len(candidates))
        remaining = {k: len(v) for k, v in by.items()}
        rng.shuffle(candidates)
        punched = []
        for c in candidates:
            if len(punched) >= n_punch:
                break
            i, p, k, v = c
            if remaining[(p, k)] <= 1:
                continue
            punched.append(c)
            remaining[(p, k)] -= 1
        for i, p, k, _ in punched:
            conn.execute(
                "DELETE FROM char_data WHERE instance=? AND pvt=? AND field_key=?",
                (i, p, k),
            )
        conn.commit()
        (Path(str(db) + ".punched.txt")).write_text(
            "\n".join(f"{i}\t{p}\t{k}\t{v}" for i, p, k, v in punched) + "\n",
            encoding="utf-8",
        )
        return punched
    finally:
        conn.close()


def write_list(path: Path, items: list[str]) -> None:
    path.write_text("\n".join(items) + "\n", encoding="utf-8")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_list(ROOT / "pvt8.txt", PVT8)
    write_list(ROOT / "sparse_target_pvts.txt", PVT8)

    miss_inst = [INTERIOR, "HINP3TCAM128X32SWISDC"]
    miss_db = ROOT / "A_missing_punched.db"
    n = copy_subset(A_REF, miss_db, miss_inst, PVT8)
    punched = punch_holes(miss_db)
    print(f"missing base rows={n} punched={len(punched)} → {miss_db}")

    sparse_inst = [INTERIOR, "HINP3TCAM128X32SWISDC"]
    sparse_db = ROOT / "A_sparse.db"
    n2 = copy_subset(A_REF, sparse_db, sparse_inst, SPARSE_SEED_PVTS)
    print(f"sparse base rows={n2} → {sparse_db}")

    weak_db = ROOT / "A_sparse_weak.db"
    n3 = copy_subset(A_REF, weak_db, [INTERIOR], SPARSE_SEED_PVTS[:1])
    print(f"weak sparse rows={n3} → {weak_db}")
    print("OK fixtures built")


if __name__ == "__main__":
    main()
