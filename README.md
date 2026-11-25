# EPC — AI Characterization (A→B .db)

Private workspace for SRAM/Memory compiler characterization transfer: construct B process `.db` from A reference `.db` + instance/pvt lists + optional constraints.

## Layout

| Path | Role |
|------|------|
| `epc_engine/` | Construction engine (idw_nn, residual_gbdt, transfer_ab / Residual TL, gates) |
| `epc_gui/` | PyQt-Fluent GUI (config / preview / compare) |
| `epc_fixtures/` | DEMO fixtures, suites, acceptance reports |
| `EPC_*.md` | Specs (P0–P2, AB-hard, LON, transfer, GUI) |

## Quick start

```bash
# sample / residual job (see epc_engine/README.md)
PYTHONPATH=. python3 -m epc_engine path/to/job.yaml

# GUI
python3 -m epc_gui

# suites
bash epc_fixtures/run_ab_hard_suite.sh
bash epc_fixtures/run_lon_holdout_suite.sh
bash epc_fixtures/transfer/run_transfer_suite.sh
```

DEMO fixtures are synthetic — not foundry/PDK calibration.

## Status (2026-10)

GUI P0–P2.1, H3-hard, AB-hard, LON, slide25/26 Residual TL transfer — independently accepted PASS.
