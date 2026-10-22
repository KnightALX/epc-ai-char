"""P2 reusable operator modes (same CLI + YAML mode dispatch)."""
from __future__ import annotations

from ..job import Job

SUPPORTED_MODES = (
    "epc_ab",
    "corner_fill_geom",
    "pvt_missing_fill",
    "pvt_sparse_fill",
    "transfer_ab",
)


def run_mode(job: Job) -> int:
    """Dispatch non-epc_ab modes. epc_ab stays in cli.run_epc_ab."""
    mode = job.mode
    if mode == "corner_fill_geom":
        from .corner_fill import run_corner_fill

        return run_corner_fill(job)
    if mode == "pvt_missing_fill":
        from .missing_fill import run_missing_fill

        return run_missing_fill(job)
    if mode == "pvt_sparse_fill":
        from .sparse_fill import run_sparse_fill

        return run_sparse_fill(job)
    if mode == "transfer_ab":
        from .transfer_ab import run_transfer_ab

        return run_transfer_ab(job)
    raise ValueError(f"unknown mode={mode!r}; supported={SUPPORTED_MODES}")
