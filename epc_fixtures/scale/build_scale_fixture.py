"""Build a large synthetic source DB for scale evaluation (A_scale.db).

Honesty note: values are DERIVED from the shipped A_ref.db (nearest-geometry
copy scaled by a smooth geometric trend + deterministic per-cell jitter),
not PDK-calibrated silicon data. Purpose = scale/throughput eval of the
engine (row counts, wall time, memory), NOT accuracy claims.

Usage:
    python epc_fixtures/scale/build_scale_fixture.py --instances 200
Writes:
    epc_fixtures/scale/A_scale.db                 (N x 40 x 50 rows)
    epc_fixtures/scale/B_scale_instance_list.txt  (50 targets)
"""
from __future__ import annotations

import argparse
import hashlib
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "epc_fixtures"
A_REF = FIXTURES / "A_ref.db"
SCALE_DIR = FIXTURES / "scale"

DEPTHS = [32, 48, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, 480, 512]
WIDTHS = [4, 8, 16, 32, 48, 64, 80, 100, 128]
OPTIONS = "SWISDC"

# Target instances for B (kept fixed so scale YAMLs are stable):
# includes HINP3TCAM512X100SWISDC (exact in A) to keep the shipped
# table_upper_bound constraint locator meaningful.
B_TARGETS = [
    "HINP3TCAM512X100SWISDC",
    "HINP3TCAM96X16SWISDC",
    "HINP3TCAM128X48SWISDC",
    "HINP3TCAM128X80SWISDC",
    "HINP3TCAM160X64SWISDC",
    "HINP3TCAM160X100SWISDC",
    "HINP3TCAM192X8SWISDC",
    "HINP3TCAM192X48SWISDC",
    "HINP3TCAM256X80SWISDC",
    "HINP3TCAM320X64SWISDC",
    "HINP3TCAM320X100SWISDC",
    "HINP3TCAM384X8SWISDC",
    "HINP3TCAM384X64SWISDC",
    "HINP3TCAM448X32SWISDC",
    "HINP3TCAM512X48SWISDC",
    "HINP3TCAM512X80SWISDC",
    "HINP3TCAM64X48SWISDC",
    "HINP3TCAM96X80SWISDC",
    "HINP3TCAM128X4SWISDC",
    "HINP3TCAM192X32SWISDC",
    "HINP3TCAM256X4SWISDC",
    "HINP3TCAM256X100SWISDC",
    "HINP3TCAM320X8SWISDC",
    "HINP3TCAM384X80SWISDC",
    "HINP3TCAM448X100SWISDC",
    "HINP3TCAM64X16SWISDC",
    "HINP3TCAM96X64SWISDC",
    "HINP3TCAM160X48SWISDC",
    "HINP3TCAM192X80SWISDC",
    "HINP3TCAM256X64SWISDC",
    "HINP3TCAM384X48SWISDC",
    "HINP3TCAM448X8SWISDC",
    "HINP3TCAM448X64SWISDC",
    "HINP3TCAM512X4SWISDC",
    "HINP3TCAM64X32SWISDC",
    "HINP3TCAM96X48SWISDC",
    "HINP3TCAM128X16SWISDC",
    "HINP3TCAM160X80SWISDC",
    "HINP3TCAM320X48SWISDC",
    "HINP3TCAM384X16SWISDC",
    "HINP3TCAM64X8SWISDC",
    "HINP3TCAM64X80SWISDC",
    "HINP3TCAM96X32SWISDC",
    "HINP3TCAM128X64SWISDC",
    "HINP3TCAM160X16SWISDC",
    "HINP3TCAM192X100SWISDC",
    "HINP3TCAM256X16SWISDC",
    "HINP3TCAM320X16SWISDC",
    "HINP3TCAM384X100SWISDC",
    "HINP3TCAM448X48SWISDC",
]
assert len(B_TARGETS) == 50


def _grid_names(limit: int) -> list[str]:
    out: list[str] = []
    for d in DEPTHS:
        for w in WIDTHS:
            out.append(f"HINP3TCAM{d}X{w}{OPTIONS}")
            if len(out) >= limit:
                return out
    # mux variants double the namespace for very large scales
    base = list(out)
    i = 0
    while len(out) < limit and i < len(base):
        out.append(base[i].replace("SWISDC", "M2SWISDC"))
        i += 1
    # third tier: M4 variants (grid x M2 x M4)
    j = 0
    while len(out) < limit and j < len(base):
        out.append(base[j].replace("SWISDC", "M4SWISDC"))
        j += 1
    return out


def _jitter(name: str, pvt: str, key: str, cell: int) -> float:
    h = hashlib.sha256(f"{name}|{pvt}|{key}|{cell}".encode()).digest()
    # deterministic ±0.05% jitter
    return ((int.from_bytes(h[:4], "big") / (2**32 - 1)) - 0.5) * 0.001


def _factor(depth: int, width: int, ref_depth: int, ref_width: int) -> float:
    # smooth trend: delay/energy grow with size; keep magnitude bounded
    return ((depth / ref_depth) ** 0.25) * ((width / ref_width) ** 0.15)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--instances", type=int, default=200)
    p.add_argument("--out", type=Path, default=SCALE_DIR / "A_scale.db")
    p.add_argument("--b-list", type=Path, default=SCALE_DIR / "B_scale_instance_list.txt")
    args = p.parse_args()

    if not A_REF.is_file():
        print(f"missing {A_REF}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(str(A_REF))
    rows = conn.execute("SELECT instance, pvt, field_key, value FROM char_data").fetchall()
    conn.close()

    by_group: dict[tuple[str, str], dict[str, str]] = {}
    inst_set: set[str] = set()
    pvt_set: set[str] = set()
    key_set: set[str] = set()
    for inst, pvt, key, val in rows:
        by_group.setdefault((inst, pvt), {})[key] = val
        inst_set.add(inst)
        pvt_set.add(pvt)
        key_set.add(key)

    sys.path.insert(0, str(ROOT))
    from epc_engine.parse import geom_distance, parse_instance

    shipped = sorted(inst_set)
    shipped_parts = {n: parse_instance(n) for n in shipped}

    def nearest_ref(name: str) -> str:
        parts = parse_instance(name)
        best, best_d = shipped[0], float("inf")
        for ref in shipped:
            d = geom_distance(parts, shipped_parts[ref])
            if d < best_d:
                best, best_d = ref, d
        return best

    # instance set: shipped (exact) + grid variants up to N total
    chosen: list[str] = list(shipped)
    for name in _grid_names(args.instances * 3):
        if name in inst_set or name in chosen:
            continue
        chosen.append(name)
        if len(chosen) >= args.instances:
            break

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out_conn = sqlite3.connect(str(args.out))
    out_conn.execute(
        "CREATE TABLE IF NOT EXISTS char_data ("
        "instance TEXT NOT NULL, pvt TEXT NOT NULL, field_key TEXT NOT NULL, "
        "value TEXT NOT NULL, PRIMARY KEY (instance, pvt, field_key))"
    )
    n_written = 0
    for name in chosen:
        if name in inst_set:
            groups = {(name, pvt): by_group[(name, pvt)] for pvt in pvt_set}
        else:
            ref = nearest_ref(name)
            d, w = parse_instance(name).depth, parse_instance(name).width
            rd, rw = shipped_parts[ref].depth, shipped_parts[ref].width
            f = _factor(d, w, rd, rw)
            groups = {}
            for pvt in pvt_set:
                g = dict(by_group[(ref, pvt)])
                for key in key_set:
                    toks = g[key].split()
                    try:
                        vals = [float(t) * f for t in toks]
                    except ValueError:
                        continue  # non-numeric token stays as-is
                    jittered = [v * (1.0 + _jitter(name, pvt, key, i)) for i, v in enumerate(vals)]
                    g[key] = " ".join(f"{v:.12g}" for v in jittered)
                groups[(name, pvt)] = g
        for (_, pvt), g in sorted(groups.items()):
            for key in sorted(key_set):
                out_conn.execute(
                    "INSERT OR REPLACE INTO char_data VALUES (?,?,?,?)",
                    (name, pvt, key, g[key]),
                )
                n_written += 1
    out_conn.commit()
    total = out_conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]
    out_conn.close()

    args.b_list.parent.mkdir(parents=True, exist_ok=True)
    args.b_list.write_text("\n".join(B_TARGETS) + "\n", encoding="utf-8")
    print(
        f"built {args.out}: {len(chosen)} instances x {len(pvt_set)} pvts x "
        f"{len(key_set)} keys = {total} rows ({n_written} written)"
    )
    print(f"B targets: {args.b_list} ({len(B_TARGETS)} names)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
