# EPC synthetic fixtures (DEMO) — expanded

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
| instance | **20** (all option `SWISDC`) |
| pvt | **40** |
| field_key | **50** (identical per instance×pvt) |
| rows `COUNT(*)` | **40000** (= 20×40×50) |
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

### Instances in A_ref (20)

- `HINP3TCAM64X8SWISDC`
- `HINP3TCAM64X32SWISDC`
- `HINP3TCAM64X64SWISDC`
- `HINP3TCAM64X100SWISDC`
- `HINP3TCAM96X16SWISDC`
- `HINP3TCAM96X48SWISDC`
- `HINP3TCAM128X8SWISDC`
- `HINP3TCAM128X32SWISDC`
- `HINP3TCAM128X72SWISDC`
- `HINP3TCAM192X16SWISDC`
- `HINP3TCAM192X64SWISDC`
- `HINP3TCAM256X8SWISDC`
- `HINP3TCAM256X32SWISDC`
- `HINP3TCAM256X100SWISDC`
- `HINP3TCAM384X16SWISDC`
- `HINP3TCAM384X48SWISDC`
- `HINP3TCAM512X8SWISDC`
- `HINP3TCAM512X32SWISDC`
- `HINP3TCAM512X64SWISDC`
- `HINP3TCAM512X100SWISDC`

Corners present: `64X8`, `512X8`, `64X100`, `512X100`.

### PVTs in A_ref (40)

First 8 (see DB / generator for full 40):

- `SSGNP_0P675V_0P675V_M40C`
- `SSGNP_0P675V_0P675V_0C`
- `SSGNP_0P675V_0P675V_25C`
- `SSGNP_0P675V_0P675V_85C`
- `SSGNP_0P675V_0P675V_125C`
- `SSGNP_0P75V_0P75V_M40C`
- `SSGNP_0P75V_0P75V_25C`
- `SSGNP_0P75V_0P75V_125C`
- … (SSGNP / TT / FFGNP × voltage × temp)

### Field keys (50)

**Axes:** `tran_index`, `load_index`

**Tables (5×5):** `tselr1_min_period`, `tcq`, `tselw1_min_period`, `tcd`, `taccess`, `tpd_clk_q`, `taddr_setup`, `taddr_hold`, `twen_setup`, `twen_hold`, `tcen_setup`, `tcen_hold`, `tdata_setup`, `tdata_hold`

**Scalars:** `leakage_vddc`, `leakage_vddp`, `write_power_vddc`, `write_power_vddp`, `read_power_vddc`, `read_power_vddp`, `standby_power_vddc`, `dynamic_energy_read`, `dynamic_energy_write`, `dynamic_energy_search`, `pin_cap_a`, `pin_cap_d`, `pin_cap_clk`, `pin_cap_cen`, `pin_cap_wen`, `bitline_cap`, `wordline_cap`, `setup_time_a_scalar`, `hold_time_a_scalar`, `clk_to_q_scalar`, `min_pulse_width_clk`, `min_period_scalar`, `search_power_vddc`, `search_latency_scalar`, `retention_leakage`, `ir_drop_est`, `em_margin`, `noise_margin_snm`, `vdd_min_func`, `area_um2`, `metal_cap_est`, `slew_out_est`, `fanout_load_nom`, `temp_coeff_delay`

## B lists

**B instances:** `HINP3TCAM64X8SWISDC`, `HINP3TCAM64X100SWISDC`, `HINP3TCAM128X32SWISDC`, `HINP3TCAM256X32SWISDC`, `HINP3TCAM512X8SWISDC`, `HINP3TCAM512X100SWISDC`, `HINP3TCAM128X64SWISDC`, `HINP3TCAM256X48SWISDC`, `HINP3TCAM384X100SWISDC`

Extras not in A: `HINP3TCAM128X64SWISDC`, `HINP3TCAM256X48SWISDC`, `HINP3TCAM384X100SWISDC`

**B PVTs:** `SSGNP_0P675V_0P675V_M40C`, `SSGNP_0P99V_0P99V_125C`, `TT_0P80V_0P80V_25C`, `TT_0P90V_0P90V_125C`, `FFGNP_1P05V_1P05V_M40C`, `FFGNP_0P80V_0P80V_25C`, `SSGNP_0P75V_0P75V_125C`, `TT_0P675V_0P675V_25C`, `SSGNP_1P05V_1P05V_M40C`, `FFGNP_0P75V_0P75V_85C`, `TT_1P05V_1P05V_M40C`

Extras not in A: `SSGNP_1P05V_1P05V_M40C`, `FFGNP_0P75V_0P75V_85C`, `TT_1P05V_1P05V_M40C`

## Spot-check with sqlite3

```bash
sqlite3 /workspace/epc_fixtures/A_ref.db "SELECT COUNT(*) FROM char_data;"
sqlite3 /workspace/epc_fixtures/A_ref.db \
  "SELECT COUNT(DISTINCT instance), COUNT(DISTINCT pvt), COUNT(DISTINCT field_key) FROM char_data;"
sqlite3 /workspace/epc_fixtures/A_ref.db \
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
   `tselr1_min_period` × `all_cells` with `max=1500` (ps-like).
   A_ref max cell for that locator ≈ **1387.90** ≤ 1500 → absolute
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
