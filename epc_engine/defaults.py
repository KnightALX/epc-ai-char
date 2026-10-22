"""DEMO default speed/power key groupings for P1 relative_improve sugar (§3)."""
from __future__ import annotations

# Smaller-is-better timing / delay-class keys → improve X% ⇒ delta_pct=-X
DEFAULT_SPEED_KEYS: list[str] = [
    "tselr1_min_period",
    "tselw1_min_period",
    "tcq",
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
    "setup_time_a_scalar",
    "hold_time_a_scalar",
    "clk_to_q_scalar",
    "min_pulse_width_clk",
    "min_period_scalar",
    "search_latency_scalar",
    "slew_out_est",
]

# Smaller-is-better power / energy keys → improve Y% ⇒ delta_pct=-Y
DEFAULT_POWER_KEYS: list[str] = [
    "leakage_vddc",
    "leakage_vddp",
    "retention_leakage",
    "write_power_vddc",
    "write_power_vddp",
    "read_power_vddc",
    "read_power_vddp",
    "standby_power_vddc",
    "search_power_vddc",
    "dynamic_energy_read",
    "dynamic_energy_write",
    "dynamic_energy_search",
]
