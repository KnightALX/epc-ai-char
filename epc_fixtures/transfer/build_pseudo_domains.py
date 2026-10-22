#!/usr/bin/env python3
"""Build pseudo dual-process fixtures from A_ref (nonlinear warp).

Outputs under /workspace/epc_fixtures/transfer/:
  A_src.db          — copy of A_ref (domain=src)
  A_tgt_full.db     — warped target full truth (offline eval only)
  A_tgt_seed.db     — ~15% seed + forced boundary corners
  seed_manifest.json
  warp_meta.json

Never overwrites A_ref.db. Warp id: warp_nl_v0
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import sqlite3
from pathlib import Path

from epc_engine.parse import parse_pvt
from epc_engine.train_lib import LOI_INSTANCES, LOP_PVTS, RANDOM_SEED
from epc_engine.values import format_tokens, parse_tokens

WARP_ID = "warp_nl_v0"
AXIS_KEYS = ("tran_index", "load_index")

DELAY_KEYS = {
    "tselr1_min_period",
    "tcq",
    "tcd",
    "taccess",
    "clk_to_q_scalar",
    "min_period_scalar",
    "thold",
    "thold_a",
    "thold_d",
    "tsetup",
    "tsetup_a",
    "tsetup_d",
    "hold_time_a_scalar",
}
LEAKAGE_KEYS = {"leakage_vddc", "leakage_vddp"}
POWER_KEYS = {
    "read_power_vddc",
    "write_power_vddc",
    "dynamic_energy_read",
    "dynamic_energy_write",
    "dynamic_energy_search",
}


def key_family(key: str) -> str:
    if key in AXIS_KEYS:
        return "axis"
    if key in LEAKAGE_KEYS or key.startswith("leakage"):
        return "leakage"
    if key in POWER_KEYS or "power" in key or "energy" in key:
        return "power"
    if key in DELAY_KEYS or key.startswith("t"):
        return "delay"
    return "other"


def g_h(pp, key: str) -> tuple[float, float]:
    """Nonlinear warp (g, h): v_tgt = g * v_src + h.

    Designed so a single global linear ratio is systematically biased,
    especially at low-V and leakage family.
    """
    fam = key_family(key)
    if fam == "axis":
        return 1.0, 0.0
    v = max(float(pp.vdd), 0.50)
    t = float(pp.temp)
    corner = pp.corner.upper()
    ss = corner.startswith("SS")
    ff = corner.startswith("FF")

    if fam == "leakage":
        # Strong exponential in 1/V — global median r under-fits low-V SS
        g = 1.18 * math.exp(0.62 * (1.0 / v - 1.0 / 0.80))
        g *= 1.0 + 0.0035 * (t - 25.0) / 100.0
        if ss:
            g *= 1.28
        elif ff:
            g *= 0.82
        h = 5e-4 * ((0.80 / v) ** 3)
        return g, h

    if fam == "delay":
        # Mild at high V; quadratic blow-up at low V + SS bump
        g = 1.03 + 0.22 * ((0.80 / v) ** 2 - 1.0) + 0.0009 * (t - 25.0)
        if ss:
            g *= 1.10
        elif ff:
            g *= 0.96
        return g, 0.0

    if fam == "power":
        g = 1.06 + 0.14 * ((0.80 / v) ** 1.5 - 1.0) + 0.0005 * (t - 25.0)
        if ss:
            g *= 1.08
        return g, 0.0

    # other
    g = 1.04 + 0.06 * ((0.80 / v) - 1.0)
    return g, 0.0


def warp_value(value: str, pp, key: str) -> str:
    if key in AXIS_KEYS:
        return value
    g, h = g_h(pp, key)
    toks = parse_tokens(value)
    out = [g * t + h for t in toks]
    return format_tokens(out)


def copy_db(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    shutil.copy2(src, dst)


def warp_db(src: Path, dst: Path) -> dict:
    copy_db(src, dst)
    conn = sqlite3.connect(str(dst))
    try:
        rows = conn.execute(
            "SELECT instance, pvt, field_key, value FROM char_data"
        ).fetchall()
        n_changed = 0
        n_same = 0
        updates = []
        for inst, pvt, key, value in rows:
            if key in AXIS_KEYS:
                n_same += 1
                continue
            pp = parse_pvt(pvt)
            new_v = warp_value(value, pp, key)
            if new_v != value:
                n_changed += 1
            else:
                n_same += 1
            updates.append((new_v, inst, pvt, key))
        conn.executemany(
            "UPDATE char_data SET value=? WHERE instance=? AND pvt=? AND field_key=?",
            updates,
        )
        conn.commit()
    finally:
        conn.close()
    return {"n_rows": len(rows), "n_changed": n_changed, "n_axis_unchanged": n_same}


def select_seed_groups(
    conn: sqlite3.Connection,
    *,
    seed_frac: float = 0.15,
    rng_seed: int = RANDOM_SEED,
) -> list[tuple[str, str]]:
    groups = conn.execute(
        "SELECT DISTINCT instance, pvt FROM char_data"
    ).fetchall()
    groups = [(i, p) for i, p in groups]
    forced = []
    remaining = []
    loi = set(LOI_INSTANCES)
    lop = set(LOP_PVTS)
    for inst, pvt in groups:
        if inst in loi and pvt in lop:
            forced.append((inst, pvt))
        else:
            remaining.append((inst, pvt))
    target_n = max(len(forced), int(round(len(groups) * seed_frac)))
    rng = random.Random(rng_seed)
    rng.shuffle(remaining)
    need = max(0, target_n - len(forced))
    chosen = list(forced) + remaining[:need]
    chosen.sort()
    return chosen


def write_seed_db(full: Path, seed_out: Path, seed_groups: list[tuple[str, str]]) -> int:
    if seed_out.exists():
        seed_out.unlink()
    shutil.copy2(full, seed_out)
    conn = sqlite3.connect(str(seed_out))
    try:
        # Keep only seed groups
        conn.execute("CREATE TEMP TABLE keep(instance TEXT, pvt TEXT, PRIMARY KEY(instance,pvt))")
        conn.executemany("INSERT INTO keep VALUES (?,?)", seed_groups)
        conn.execute(
            "DELETE FROM char_data WHERE NOT EXISTS ("
            "  SELECT 1 FROM keep k WHERE k.instance=char_data.instance AND k.pvt=char_data.pvt"
            ")"
        )
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]
        n_g = conn.execute(
            "SELECT COUNT(*) FROM (SELECT DISTINCT instance,pvt FROM char_data)"
        ).fetchone()[0]
        conn.execute("VACUUM")
    finally:
        conn.close()
    return n_g


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build transfer pseudo domains")
    ap.add_argument(
        "--a-ref",
        default="/workspace/epc_fixtures/A_ref.db",
    )
    ap.add_argument(
        "--out-dir",
        default="/workspace/epc_fixtures/transfer",
    )
    ap.add_argument("--seed-frac", type=float, default=0.15)
    ap.add_argument("--rng-seed", type=int, default=RANDOM_SEED)
    args = ap.parse_args(argv)

    a_ref = Path(args.a_ref).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    if a_ref.name != "A_ref.db" and "A_ref" not in str(a_ref):
        print(f"[warn] unexpected A_ref path: {a_ref}")

    a_src = out / "A_src.db"
    a_tgt_full = out / "A_tgt_full.db"
    a_tgt_seed = out / "A_tgt_seed.db"

    print(f"[transfer-build] A_ref={a_ref}")
    print(f"[transfer-build] warp_id={WARP_ID}")
    copy_db(a_ref, a_src)
    print(f"[transfer-build] A_src ← copy → {a_src}")

    stats = warp_db(a_ref, a_tgt_full)
    print(
        f"[transfer-build] A_tgt_full warped rows={stats['n_rows']} "
        f"changed={stats['n_changed']} → {a_tgt_full}"
    )

    conn = sqlite3.connect(str(a_tgt_full))
    try:
        n_groups = conn.execute(
            "SELECT COUNT(*) FROM (SELECT DISTINCT instance,pvt FROM char_data)"
        ).fetchone()[0]
        seed_groups = select_seed_groups(
            conn, seed_frac=args.seed_frac, rng_seed=args.rng_seed
        )
    finally:
        conn.close()

    n_seed = write_seed_db(a_tgt_full, a_tgt_seed, seed_groups)
    forced_n = sum(
        1
        for i, p in seed_groups
        if i in set(LOI_INSTANCES) and p in set(LOP_PVTS)
    )
    print(
        f"[transfer-build] A_tgt_seed groups={n_seed}/{n_groups} "
        f"({100.0 * n_seed / n_groups:.1f}%) forced_boundary={forced_n} → {a_tgt_seed}"
    )

    # Sanity: src vs tgt not bitwise identical on a core value
    c1 = sqlite3.connect(str(a_src))
    c2 = sqlite3.connect(str(a_tgt_full))
    try:
        r1 = c1.execute(
            "SELECT value FROM char_data WHERE field_key='leakage_vddc' LIMIT 1"
        ).fetchone()[0]
        r2 = c2.execute(
            "SELECT value FROM char_data WHERE field_key='leakage_vddc' LIMIT 1"
        ).fetchone()[0]
        assert r1 != r2, "warp produced identical leakage — fake transfer"
    finally:
        c1.close()
        c2.close()

    meta = {
        "warp_id": WARP_ID,
        "formula": "v_tgt = g(V,T,corner,key_family)*v_src + h(...)",
        "seed_frac": args.seed_frac,
        "rng_seed": args.rng_seed,
        "n_groups_full": n_groups,
        "n_groups_seed": n_seed,
        "forced_boundary_groups": forced_n,
        "loi_instances": list(LOI_INSTANCES),
        "lop_pvts": list(LOP_PVTS),
        "a_ref": str(a_ref),
        "stats": stats,
        "reproduce": (
            f"python3 /workspace/epc_fixtures/transfer/build_pseudo_domains.py "
            f"--a-ref {a_ref} --out-dir {out} --seed-frac {args.seed_frac} "
            f"--rng-seed {args.rng_seed}"
        ),
    }
    (out / "warp_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "seed_groups": [{"instance": i, "pvt": p} for i, p in seed_groups],
        "n": len(seed_groups),
        "forced_boundary": [
            {"instance": i, "pvt": p}
            for i, p in seed_groups
            if i in set(LOI_INSTANCES) and p in set(LOP_PVTS)
        ],
    }
    (out / "seed_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[transfer-build] meta → {out / 'warp_meta.json'}")
    print("[transfer-build] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
