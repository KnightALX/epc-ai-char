# EPC Transfer Hold-out Report — residual_tl vs linear_tr

- Generated: **2026-10-22 22:30:45 CST** (Asia/Shanghai)
- Protocol: **Transfer** (`transfer_holdout_v0`)
- Warp id: **`warp_nl_v0`** (pseudo dual-process; ≠ true PDK)
- Seed groups: **120**; eval (non-seed) groups: **680**
- Core keys: `tselr1_min_period, tcq, tcd, taccess, leakage_vddc, read_power_vddc, write_power_vddc, dynamic_energy_read`
- ε = `1e-12`; random_seed = `42`
- Ratio policy: `global_per_key_median_on_seed` (seed only — hold-out truth never used for r)
- Relative error: `|hat-true|/max(|true|,ε)` at cell level
- **No transfer stamp** this round (decoupled from AB-hard / LON / H3)
- **DEMO synthetic only** — not foundry calibration

- A_src: `/workspace/epc_fixtures/transfer/A_src.db`
- A_tgt_seed: `/workspace/epc_fixtures/transfer/A_tgt_seed.db`
- A_tgt_full (eval only): `/workspace/epc_fixtures/transfer/A_tgt_full.db`
- Reproduce: `python3 /workspace/epc_fixtures/transfer/build_pseudo_domains.py --a-ref /workspace/epc_fixtures/A_ref.db --out-dir /workspace/epc_fixtures/transfer --seed-frac 0.15 --rng-seed 42`

## Acceptance gate (TRANSFER-hard)

| ID | Criterion | p95_RTL | p95_TR | delta | n_cells | n_eval_groups | protocol | Result |
|---|---|---|---|---|---|---|---|---|
| **TRANSFER-hard** | p95_RTL ≤ p95_TR | 0.0228121 | 0.249832 | -0.22702 | 70720 | 680 | `transfer_holdout_v0` | **PASS** |

**TRANSFER-hard: PASS** (compare `≤`; equality OK)

## Summary

| Method | p95 | p50 | max | n | ≤ TR? |
|---|---|---|---|---|---|
| **linear_tr** | 0.249832 | 0.0862117 | 0.621202 | 70720 | — |
| **residual_tl** | 0.0228121 | 0.00465718 | 0.951453 | 70720 | YES |

### Low-V stratified (Should)

- Threshold: VDD < `0.75`
- linear_tr p95_lowV = `0.192403` (n=17160)
- residual_tl p95_lowV = `0.0253819` (n=17160)

## Per-key p95

| key | linear_tr p95 | residual_tl p95 | Δ | r (seed median) |
|---|---|---|---|---|
| `tselr1_min_period` | 0.249832 | 0.0203667 | -0.229465 | 1.07405 |
| `tcq` | 0.249832 | 0.0211987 | -0.228633 | 1.07405 |
| `tcd` | 0.249832 | 0.0206577 | -0.229174 | 1.07405 |
| `taccess` | 0.249832 | 0.0211116 | -0.22872 | 1.07405 |
| `leakage_vddc` | 0.612829 | 0.220455 | -0.392374 | 1.30663 |
| `read_power_vddc` | 0.112657 | 0.0364386 | -0.0762182 | 1.10064 |
| `write_power_vddc` | 0.112657 | 0.0366422 | -0.0760146 | 1.10064 |
| `dynamic_energy_read` | 0.112657 | 0.0362621 | -0.0763946 | 1.10064 |

## Notes

- Prior = linear Transfer Ratio on aligned src locator; residual = GBDT(x, prior_tr).
- Features: log2(d/w), PVT, cell axes, prior_tr (tran/load axes never shuffled).
- Hard gate: **TRANSFER-hard** (`p95_RTL ≤ p95_TR`). Flag `--require-transfer-hard` / `--no-require-transfer-hard` (default off).
- **Not** same-process LOI/LOP/LON evidence. **Not** AB stamp / Op-Geom H3.
- leaked_seed_guard=0 (must be 0)
