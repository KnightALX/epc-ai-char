#!/usr/bin/env python3
"""Generate synthetic DEMO EPC fixture assets (expanded).

NOT real foundry / PDK data. Regenerates everything under <repo>/epc_fixtures/ (script directory).
Scale target: 20 instances × 40 pvts × ~50 field_keys ≈ 40_000 rows.
Table axes: N=5.
"""
from __future__ import annotations

import math
import re
import sqlite3
from pathlib import Path

OUT = Path(__file__).resolve().parent
DB_PATH = OUT / "A_ref.db"

# ---------------------------------------------------------------------------
# 20 instances — same option SWISDC; depth×width grid with clear corners
# Corners: 64×8, 512×8, 64×100, 512×100; intermediates scattered.
# ---------------------------------------------------------------------------
GEOMS: list[tuple[int, int]] = [
    (64, 8), (64, 32), (64, 64), (64, 100),          # depth 64 row + corners
    (96, 16), (96, 48),
    (128, 8), (128, 32), (128, 72),
    (192, 16), (192, 64),
    (256, 8), (256, 32), (256, 100),
    (384, 16), (384, 48),
    (512, 8), (512, 32), (512, 64), (512, 100),      # depth 512 row + corners
]
assert len(GEOMS) == 20


def inst_name(depth: int, width: int) -> str:
    return f"HINP3TCAM{depth}X{width}SWISDC"


INSTANCES = [inst_name(d, w) for d, w in GEOMS]

# B extras: geometries NOT in A (≥2)
B_EXTRA_GEOMS = [(128, 64), (256, 48), (384, 100)]
B_EXTRA_INSTANCES = [inst_name(d, w) for d, w in B_EXTRA_GEOMS]
for g in B_EXTRA_GEOMS:
    assert g not in GEOMS, g

# B instance list: subset of A (corners + a few mid) + extras
B_FROM_A = [
    inst_name(64, 8),
    inst_name(64, 100),
    inst_name(128, 32),
    inst_name(256, 32),
    inst_name(512, 8),
    inst_name(512, 100),
]

# ---------------------------------------------------------------------------
# 40 PVTs — corner × voltage × temp variety
# Naming: {CORNER}_{VDDC}V_{VDDP}V_{TEMP}
# ---------------------------------------------------------------------------
def _v(s: str) -> str:
    """0.675 -> 0P675V style token (already formatted fragment)."""
    return s


PVTS: list[str] = [
    # SSGNP family (slow)
    "SSGNP_0P675V_0P675V_M40C",
    "SSGNP_0P675V_0P675V_0C",
    "SSGNP_0P675V_0P675V_25C",
    "SSGNP_0P675V_0P675V_85C",
    "SSGNP_0P675V_0P675V_125C",
    "SSGNP_0P75V_0P75V_M40C",
    "SSGNP_0P75V_0P75V_25C",
    "SSGNP_0P75V_0P75V_125C",
    "SSGNP_0P90V_0P90V_M40C",
    "SSGNP_0P90V_0P90V_25C",
    "SSGNP_0P90V_0P90V_125C",
    "SSGNP_0P99V_0P99V_M40C",
    "SSGNP_0P99V_0P99V_25C",
    "SSGNP_0P99V_0P99V_125C",
    # TT family (typical)
    "TT_0P675V_0P675V_M40C",
    "TT_0P675V_0P675V_25C",
    "TT_0P675V_0P675V_125C",
    "TT_0P80V_0P80V_M40C",
    "TT_0P80V_0P80V_0C",
    "TT_0P80V_0P80V_25C",
    "TT_0P80V_0P80V_85C",
    "TT_0P80V_0P80V_125C",
    "TT_0P90V_0P90V_M40C",
    "TT_0P90V_0P90V_25C",
    "TT_0P90V_0P90V_125C",
    "TT_0P99V_0P99V_25C",
    "TT_0P99V_0P99V_125C",
    "TT_1P05V_1P05V_25C",
    # FFGNP family (fast)
    "FFGNP_0P675V_0P675V_M40C",
    "FFGNP_0P675V_0P675V_25C",
    "FFGNP_0P80V_0P80V_M40C",
    "FFGNP_0P80V_0P80V_25C",
    "FFGNP_0P80V_0P80V_125C",
    "FFGNP_0P90V_0P90V_25C",
    "FFGNP_0P99V_0P99V_M40C",
    "FFGNP_0P99V_0P99V_25C",
    "FFGNP_0P99V_0P99V_125C",
    "FFGNP_1P05V_1P05V_M40C",
    "FFGNP_1P05V_1P05V_25C",
    "FFGNP_1P05V_1P05V_125C",
]
assert len(PVTS) == 40, len(PVTS)
assert len(set(PVTS)) == 40

# B extras: PVTs NOT in A (≥2)
B_EXTRA_PVTS = [
    "SSGNP_1P05V_1P05V_M40C",   # SS + high-V cold — not in A
    "FFGNP_0P75V_0P75V_85C",    # FF mid-V warm — not in A
    "TT_1P05V_1P05V_M40C",      # TT high-V cold — not in A
]
for p in B_EXTRA_PVTS:
    assert p not in PVTS, p

# B pvt list: subset of A + extras
B_FROM_A_PVTS = [
    "SSGNP_0P675V_0P675V_M40C",
    "SSGNP_0P99V_0P99V_125C",
    "TT_0P80V_0P80V_25C",
    "TT_0P90V_0P90V_125C",
    "FFGNP_1P05V_1P05V_M40C",
    "FFGNP_0P80V_0P80V_25C",
    "SSGNP_0P75V_0P75V_125C",
    "TT_0P675V_0P675V_25C",
]

# ---------------------------------------------------------------------------
# Axes N=5
# ---------------------------------------------------------------------------
N = 5
TRAN_INDEX = [0.005, 0.01, 0.02, 0.04, 0.08]   # ns-like
LOAD_INDEX = [0.001, 0.005, 0.01, 0.025, 0.05]  # pF-like

# ---------------------------------------------------------------------------
# ~50 field_keys — identical for every (instance, pvt)
# ---------------------------------------------------------------------------
AXIS_KEYS = ["tran_index", "load_index"]

# Flattened 5×5 tables (row-major i*N+j, i=tran, j=load)
TABLE_KEYS = [
    "tselr1_min_period",
    "tcq",
    "tselw1_min_period",
    "tcd",
    "taccess",
    "tpd_clk_q",
    "taddr_setup",
    "taddr_hold",
    "twen_setup",
    "twen_hold",
    "tcen_setup",
    "tcen_hold",
    "tdata_setup",
    "tdata_hold",
]

# Scalars (leakage / power / cap / energy / misc timing)
SCALAR_KEYS = [
    "leakage_vddc",
    "leakage_vddp",
    "write_power_vddc",
    "write_power_vddp",
    "read_power_vddc",
    "read_power_vddp",
    "standby_power_vddc",
    "dynamic_energy_read",
    "dynamic_energy_write",
    "dynamic_energy_search",
    "pin_cap_a",
    "pin_cap_d",
    "pin_cap_clk",
    "pin_cap_cen",
    "pin_cap_wen",
    "bitline_cap",
    "wordline_cap",
    "setup_time_a_scalar",
    "hold_time_a_scalar",
    "clk_to_q_scalar",
    "min_pulse_width_clk",
    "min_period_scalar",
    "search_power_vddc",
    "search_latency_scalar",
    "retention_leakage",
    "ir_drop_est",
    "em_margin",
    "noise_margin_snm",
    "vdd_min_func",
    "area_um2",
    "metal_cap_est",
    "slew_out_est",
    "fanout_load_nom",
    "temp_coeff_delay",
]

FIELD_KEYS = AXIS_KEYS + TABLE_KEYS + SCALAR_KEYS
assert len(FIELD_KEYS) == len(set(FIELD_KEYS))
assert 45 <= len(FIELD_KEYS) <= 55, len(FIELD_KEYS)

# Base ps for each table key (synthetic)
TABLE_BASE_PS = {
    "tselr1_min_period": 220.0,
    "tcq": 140.0,
    "tselw1_min_period": 240.0,
    "tcd": 110.0,
    "taccess": 180.0,
    "tpd_clk_q": 130.0,
    "taddr_setup": 55.0,
    "taddr_hold": 22.0,
    "twen_setup": 48.0,
    "twen_hold": 20.0,
    "tcen_setup": 50.0,
    "tcen_hold": 18.0,
    "tdata_setup": 60.0,
    "tdata_hold": 25.0,
}


def parse_geom(name: str) -> tuple[int, int]:
    m = re.search(r"(\d+)X(\d+)", name)
    if not m:
        raise ValueError(name)
    return int(m.group(1)), int(m.group(2))


def parse_pvt(pvt: str) -> dict:
    """Extract corner, voltage (V), temp (C) from token."""
    parts = pvt.split("_")
    corner = parts[0]  # SSGNP / TT / FFGNP
    # voltage like 0P675V
    def volt(tok: str) -> float:
        t = tok.upper().rstrip("V").replace("P", ".")
        return float(t)

    vdd = volt(parts[1])
    # temp like M40C / 25C / 125C
    ttok = parts[3]
    if ttok.startswith("M"):
        temp = -float(ttok[1:].rstrip("C"))
    else:
        temp = float(ttok.rstrip("C"))
    return dict(corner=corner, vdd=vdd, temp=temp)


def pvt_factors(pvt: str) -> dict:
    """Synthetic corner multipliers — discernible SS/TT/FF × V × T trends."""
    info = parse_pvt(pvt)
    corner, vdd, temp = info["corner"], info["vdd"], info["temp"]

    # corner base delay / leak
    if corner.startswith("SS"):
        c_delay, c_leak = 1.35, 0.85
    elif corner.startswith("FF"):
        c_delay, c_leak = 0.78, 1.25
    else:  # TT
        c_delay, c_leak = 1.00, 1.00

    # voltage: lower V → worse delay, lower leak/power
    # ref 0.80 V
    v_ref = 0.80
    delay_v = (v_ref / max(vdd, 0.5)) ** 1.35
    power_v = (vdd / v_ref) ** 2.0
    leak_v = (vdd / v_ref) ** 2.4

    # temperature: hot → slightly worse delay (for SS more), much higher leak
    # ref 25 C
    t_ref = 25.0
    delay_t = 1.0 + 0.0018 * (temp - t_ref)  # mild
    if corner.startswith("SS") and vdd < 0.70 and temp < 0:
        delay_t *= 1.08  # cold + low-V SS extra pain
    leak_t = math.exp(0.018 * (temp - t_ref))  # strong temp on leak
    power_t = 1.0 + 0.0025 * (temp - t_ref)

    delay = c_delay * delay_v * delay_t
    power = c_delay * 0.0 + 1.0  # power mostly V/T, mild corner
    if corner.startswith("FF"):
        power_c = 1.12
    elif corner.startswith("SS"):
        power_c = 0.92
    else:
        power_c = 1.00
    power = power_c * power_v * power_t
    leak = c_leak * leak_v * leak_t
    cap = 1.0 + 0.01 * (vdd - v_ref)  # tiny
    return dict(delay=delay, power=power, leak=leak, cap=cap, vdd=vdd, temp=temp)


def geom_factors(depth: int, width: int) -> dict:
    """Monotonic-ish with depth/width (log-scaled). Ref = 64×8."""
    d_ref, w_ref = 64.0, 8.0
    delay = 1.0 + 0.22 * math.log2(depth / d_ref) + 0.18 * math.log2(width / w_ref)
    bits = depth * width
    bits_ref = d_ref * w_ref
    power = 0.55 + 0.45 * (bits / bits_ref) ** 0.55
    leak = 0.50 + 0.50 * (bits / bits_ref) ** 0.60
    cap = 0.85 + 0.15 * (width / w_ref) ** 0.5
    area = bits / bits_ref
    return dict(delay=delay, power=power, leak=leak, cap=cap, area=area, bits=bits)


def fmt_scalar(x: float, nd: int = 4) -> str:
    if abs(x) >= 1000:
        return f"{x:.1f}"
    if abs(x) >= 100:
        return f"{x:.2f}"
    if abs(x) >= 10:
        return f"{x:.3f}"
    return f"{x:.{nd}f}"


def fmt_table(cells: list[float]) -> str:
    return " ".join(fmt_scalar(c, 3) for c in cells)


def make_table(base_ps: float, pf: dict, gf: dict) -> list[float]:
    """Row-major N×N: increases with load (j) and tran (i)."""
    cells = []
    for i in range(N):
        for j in range(N):
            scale = 1.0 + 0.10 * i + 0.22 * j
            val = base_ps * pf["delay"] * gf["delay"] * scale
            cells.append(val)
    return cells


def build_fields(instance: str, pvt: str) -> dict[str, str]:
    depth, width = parse_geom(instance)
    pf = pvt_factors(pvt)
    gf = geom_factors(depth, width)

    out: dict[str, str] = {
        "tran_index": " ".join(str(x) for x in TRAN_INDEX),
        "load_index": " ".join(str(x) for x in LOAD_INDEX),
    }

    for tk in TABLE_KEYS:
        cells = make_table(TABLE_BASE_PS[tk], pf, gf)
        out[tk] = fmt_table(cells)

    # scalars
    leak_c = 0.010 * gf["leak"] * pf["leak"]
    leak_p = 0.006 * gf["leak"] * pf["leak"]
    wpow_c = 0.80 * gf["power"] * pf["power"]
    wpow_p = 0.35 * gf["power"] * pf["power"]
    rpow_c = 0.50 * gf["power"] * pf["power"]
    rpow_p = 0.22 * gf["power"] * pf["power"]
    sb_pow = 0.08 * gf["leak"] * pf["leak"] * pf["power"]
    dyn_r = 0.20 * gf["power"] * pf["power"]
    dyn_w = 0.28 * gf["power"] * pf["power"]
    dyn_s = 0.35 * gf["power"] * pf["power"]
    pincap_a = 0.0040 * gf["cap"] * pf["cap"]
    pincap_d = 0.0035 * gf["cap"] * pf["cap"]
    pincap_clk = 0.0055 * gf["cap"] * pf["cap"]
    pincap_cen = 0.0030 * gf["cap"] * pf["cap"]
    pincap_wen = 0.0032 * gf["cap"] * pf["cap"]
    bl_cap = 0.015 * (depth / 64.0) ** 0.7 * pf["cap"]
    wl_cap = 0.012 * (width / 8.0) ** 0.6 * pf["cap"]
    setup_s = 42.0 * pf["delay"] * gf["delay"]
    hold_s = 16.0 * pf["delay"] * (0.9 + 0.1 * gf["delay"])
    clkq_s = 95.0 * pf["delay"] * gf["delay"]
    mpw = 80.0 * pf["delay"] * gf["delay"]
    minper = 250.0 * pf["delay"] * gf["delay"]
    spow = 0.60 * gf["power"] * pf["power"]
    slat = 120.0 * pf["delay"] * gf["delay"]
    ret_leak = 0.004 * gf["leak"] * pf["leak"]
    ir_drop = 8.0 + 4.0 * gf["power"] * pf["power"]
    em_m = 1.20 - 0.08 * gf["power"] * pf["power"]  # margin shrinks with power
    snm = 0.22 * (pf["vdd"] / 0.80) * (1.05 - 0.02 * gf["delay"])
    vdd_min = 0.55 + 0.02 * gf["delay"] + (0.03 if pf["temp"] < 0 else 0.0)
    area = 1200.0 * gf["area"]
    metal_c = 0.008 * gf["cap"] * (gf["bits"] / 512.0) ** 0.3
    slew = 0.015 * pf["delay"] * (1.0 + 0.1 * gf["delay"])
    fanout = 4.0 * gf["cap"]
    tco_d = 0.0015 + 0.0002 * gf["delay"]

    out.update({
        "leakage_vddc": fmt_scalar(leak_c, 5),
        "leakage_vddp": fmt_scalar(leak_p, 5),
        "write_power_vddc": fmt_scalar(wpow_c, 4),
        "write_power_vddp": fmt_scalar(wpow_p, 4),
        "read_power_vddc": fmt_scalar(rpow_c, 4),
        "read_power_vddp": fmt_scalar(rpow_p, 4),
        "standby_power_vddc": fmt_scalar(sb_pow, 5),
        "dynamic_energy_read": fmt_scalar(dyn_r, 4),
        "dynamic_energy_write": fmt_scalar(dyn_w, 4),
        "dynamic_energy_search": fmt_scalar(dyn_s, 4),
        "pin_cap_a": fmt_scalar(pincap_a, 5),
        "pin_cap_d": fmt_scalar(pincap_d, 5),
        "pin_cap_clk": fmt_scalar(pincap_clk, 5),
        "pin_cap_cen": fmt_scalar(pincap_cen, 5),
        "pin_cap_wen": fmt_scalar(pincap_wen, 5),
        "bitline_cap": fmt_scalar(bl_cap, 5),
        "wordline_cap": fmt_scalar(wl_cap, 5),
        "setup_time_a_scalar": fmt_scalar(setup_s, 3),
        "hold_time_a_scalar": fmt_scalar(hold_s, 3),
        "clk_to_q_scalar": fmt_scalar(clkq_s, 3),
        "min_pulse_width_clk": fmt_scalar(mpw, 3),
        "min_period_scalar": fmt_scalar(minper, 3),
        "search_power_vddc": fmt_scalar(spow, 4),
        "search_latency_scalar": fmt_scalar(slat, 3),
        "retention_leakage": fmt_scalar(ret_leak, 5),
        "ir_drop_est": fmt_scalar(ir_drop, 3),
        "em_margin": fmt_scalar(em_m, 4),
        "noise_margin_snm": fmt_scalar(snm, 4),
        "vdd_min_func": fmt_scalar(vdd_min, 4),
        "area_um2": fmt_scalar(area, 2),
        "metal_cap_est": fmt_scalar(metal_c, 5),
        "slew_out_est": fmt_scalar(slew, 5),
        "fanout_load_nom": fmt_scalar(fanout, 3),
        "temp_coeff_delay": fmt_scalar(tco_d, 5),
    })

    assert set(out.keys()) == set(FIELD_KEYS), (
        set(FIELD_KEYS) - set(out.keys()),
        set(out.keys()) - set(FIELD_KEYS),
    )
    return out


def write_db() -> int:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE char_data(
          instance TEXT,
          pvt TEXT,
          field_key TEXT,
          value TEXT,
          PRIMARY KEY(instance, pvt, field_key)
        )
        """
    )
    rows = []
    for inst in INSTANCES:
        for pvt in PVTS:
            fields = build_fields(inst, pvt)
            for k, v in fields.items():
                rows.append((inst, pvt, k, v))
    cur.executemany(
        "INSERT INTO char_data(instance, pvt, field_key, value) VALUES (?,?,?,?)",
        rows,
    )
    # helpful indexes for spot-checks
    cur.execute("CREATE INDEX idx_inst ON char_data(instance)")
    cur.execute("CREATE INDEX idx_pvt ON char_data(pvt)")
    cur.execute("CREATE INDEX idx_key ON char_data(field_key)")
    conn.commit()
    conn.close()
    return len(rows)


def max_table_cell(instance: str, pvt: str, key: str) -> float:
    fields = build_fields(instance, pvt)
    cells = [float(x) for x in fields[key].split()]
    return max(cells)


def write_lists() -> None:
    inst_lines = B_FROM_A + B_EXTRA_INSTANCES
    pvt_lines = B_FROM_A_PVTS + B_EXTRA_PVTS
    (OUT / "B_instance_list.txt").write_text(
        "\n".join(inst_lines) + "\n", encoding="utf-8"
    )
    (OUT / "B_pvt_list.txt").write_text(
        "\n".join(pvt_lines) + "\n", encoding="utf-8"
    )


def write_yaml(bound_max: float) -> None:
    # ceil bound a bit above A max so A is green; still drives B for new geom/pvt
    bound_int = int(math.ceil(bound_max / 50.0) * 50) + 100
    yaml = f'''# epc_job.sample.yaml — DEMO/synthetic only (not a real foundry process)
# Generated for Kai EPC fixture pack (expanded). Paths under /workspace/epc_fixtures.
version: "0.1"
job_name: "DEMO_A_to_DEMO_B_sample"

source:
  process: "DEMO_A"
  db_path: "{DB_PATH}"

target:
  process: "DEMO_B"
  instance_list_path: "{OUT / "B_instance_list.txt"}"
  pvt_list_path: "{OUT / "B_pvt_list.txt"}"

field_policy:
  keys: all_from_source
  table_axes: ["tran_index", "load_index"]

style_from_source:
  enabled: true
  notes: "Inherit DEMO_A synthetic trends; user constraints always win (§8)."

constraints:  # all AND; each locates instance×pvt×key×point + range|±%
  # Absolute upper bound on min_period table (all cells)
  - type: table_upper_bound
    instances: ["HINP3TCAM512X100SWISDC"]
    pvts: ["SSGNP_0P99V_0P99V_125C"]
    keys: ["tselr1_min_period"]
    table_cells: "all_cells"
    target:
      mode: range
      op: "<="
      value: {bound_int}
      unit: "ps"

  # Relative delta vs source: -4% => ×0.96 on delay/min_period-class key
  - type: relative_delta_vs_source
    instances: ["HINP3TCAM64X8SWISDC"]
    pvts: ["TT_0P80V_0P80V_25C"]
    keys: ["tcq"]
    table_cells: "all_cells"
    target:
      mode: delta_pct
      delta_pct: -4
      baseline: source_aligned

output:
  db_path: "{OUT / "B_out.sample.db"}"
  audit_report_path: "{OUT / "B_out.sample_audit.md"}"

gates:
  require_constraint_satisfaction: true
  on_violation: fail_job
'''
    (OUT / "epc_job.sample.yaml").write_text(yaml, encoding="utf-8")
    return bound_int


def write_readme(
    n_rows: int,
    n_inst: int,
    n_pvt: int,
    n_key: int,
    bound_int: int,
    a_max_cell: float,
) -> None:
    inst_bullets = "\n".join(f"- `{n}`" for n in INSTANCES)
    pvt_preview = "\n".join(f"- `{p}`" for p in PVTS[:8])
    table_list = ", ".join(f"`{k}`" for k in TABLE_KEYS)
    scalar_list = ", ".join(f"`{k}`" for k in SCALAR_KEYS)
    b_inst = B_FROM_A + B_EXTRA_INSTANCES
    b_pvt = B_FROM_A_PVTS + B_EXTRA_PVTS
    readme = f'''# EPC synthetic fixtures (DEMO) — expanded

**Not real foundry / PDK data.** All numbers are synthetic DEMO assets for
pipeline, schema, interpolation, and constraint tests (Kai EPC A→B construction).

## Layout

| File | Role |
|---|---|
| `A_ref.db` | Source (DEMO_A) SQLite char library |
| `B_instance_list.txt` | Target instances (subset of A + ≥2 new geometries) |
| `B_pvt_list.txt` | Target PVTs (subset of A + ≥2 new PVTs) |
| `epc_job.sample.yaml` | Sample EPC job with ≥2 legal constraints |
| `generate_fixtures.py` | Regenerator (run to overwrite this pack) |
| `README.md` | This file |

## Scale

| Axis | Count |
|---|---|
| instance | **{n_inst}** (all option `SWISDC`) |
| pvt | **{n_pvt}** |
| field_key | **{n_key}** (identical per instance×pvt) |
| rows `COUNT(*)` | **{n_rows}** (= {n_inst}×{n_pvt}×{n_key}) |
| table N | **5** (5×5 = 25 cells, row-major) |

## Schema

```sql
CREATE TABLE char_data(
  instance TEXT,
  pvt TEXT,
  field_key TEXT,
  value TEXT,
  PRIMARY KEY(instance, pvt, field_key)
);
```

- `value`: scalar string, or space-separated flattened **N×N** table
  (here **N=5**, row-major `i*N+j` with `i=tran`, `j=load`).
- Axes: `tran_index` / `load_index` (length N, same for every group).

### Instances in A_ref ({n_inst})

{inst_bullets}

Corners present: `64X8`, `512X8`, `64X100`, `512X100`.

### PVTs in A_ref ({n_pvt})

First 8 (see DB / generator for full 40):

{pvt_preview}
- … (SSGNP / TT / FFGNP × voltage × temp)

### Field keys ({n_key})

**Axes:** `tran_index`, `load_index`

**Tables (5×5):** {table_list}

**Scalars:** {scalar_list}

## B lists

**B instances:** {", ".join(f"`{x}`" for x in b_inst)}

Extras not in A: {", ".join(f"`{x}`" for x in B_EXTRA_INSTANCES)}

**B PVTs:** {", ".join(f"`{x}`" for x in b_pvt)}

Extras not in A: {", ".join(f"`{x}`" for x in B_EXTRA_PVTS)}

## Spot-check with sqlite3

```bash
sqlite3 /workspace/epc_fixtures/A_ref.db "SELECT COUNT(*) FROM char_data;"
sqlite3 /workspace/epc_fixtures/A_ref.db \\
  "SELECT COUNT(DISTINCT instance), COUNT(DISTINCT pvt), COUNT(DISTINCT field_key) FROM char_data;"
sqlite3 /workspace/epc_fixtures/A_ref.db \\
  "SELECT value FROM char_data WHERE instance='HINP3TCAM512X100SWISDC'
     AND pvt='SSGNP_0P99V_0P99V_125C' AND field_key='tselr1_min_period';"
# max cell of that table (python one-liner also fine):
python3 - <<'PY'
import sqlite3
c=sqlite3.connect("/workspace/epc_fixtures/A_ref.db")
v=c.execute("SELECT value FROM char_data WHERE instance=? AND pvt=? AND field_key=?",
  ("HINP3TCAM512X100SWISDC","SSGNP_0P99V_0P99V_125C","tselr1_min_period")).fetchone()[0]
cells=list(map(float,v.split())); print(len(cells), max(cells), min(cells))
PY
```

## Constraint self-check (sample YAML)

1. `table_upper_bound` on `HINP3TCAM512X100SWISDC` × `SSGNP_0P99V_0P99V_125C` ×
   `tselr1_min_period` × `all_cells` with `max={bound_int}` (ps-like).
   A_ref max cell for that locator ≈ **{a_max_cell:.2f}** ≤ {bound_int} → absolute
   gate green on A; still drives B for new geometries / PVTs.
2. `relative_delta_vs_source` on `HINP3TCAM64X8SWISDC` × `TT_0P80V_0P80V_25C` ×
   `tcq` × `all_cells` with `delta_pct: -4` → target = source × **0.96**
   (`baseline: source_aligned`). Constraints beat style (§8).

## Trends (synthetic, for interpolation tests)

- Larger depth/width → larger delay / min_period / power / leakage (monotonic-ish).
- PVT: SS + low-V (+ cold) worse timing than TT mid; FF faster; leakage rises
  with temperature and voltage.
- Table cells increase with load and/or tran index (row-major).

## Regenerate

```bash
python3 /workspace/epc_fixtures/generate_fixtures.py
```

## Known limitations

- Synthetic DEMO only — do **not** treat as foundry silicon or PDK truth.
- Process tags `DEMO_A` / `DEMO_B` / `NP3` in names are placeholders.
- Units are implicit (ps / mW / uA / pF style magnitudes), not schema-enforced.
- Trends are heuristics for pipeline tests, not calibrated models.
- `B_out.sample.db` is only named in YAML; this pack does **not** run the EPC engine.
'''
    (OUT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = write_db()
    write_lists()

    a_max = max_table_cell(
        "HINP3TCAM512X100SWISDC",
        "SSGNP_0P99V_0P99V_125C",
        "tselr1_min_period",
    )
    bound_int = write_yaml(a_max)

    n_inst, n_pvt, n_key = len(INSTANCES), len(PVTS), len(FIELD_KEYS)
    write_readme(n, n_inst, n_pvt, n_key, bound_int, a_max)

    print(f"Wrote {n} rows to {DB_PATH}")
    print(f"distinct: instance={n_inst} pvt={n_pvt} field_key={n_key}")
    print(f"constraint bound={bound_int} (A max cell={a_max:.2f})")
    print("B extra instances:", B_EXTRA_INSTANCES)
    print("B extra pvts:", B_EXTRA_PVTS)
    print("Done:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
