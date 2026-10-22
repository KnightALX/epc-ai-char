"""H3-hard: non-idw backends must not exceed idw_nn p95 on the same hold-out protocol."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from ..construct_types import AXIS_KEYS, ConstructResult
from ..job import ConstructConfig
from ..source import SourceDB
from ..train_lib import CORE_KEYS
from ..values import parse_tokens
from .gates_h import p95, relative_err

EPS = 1e-12


def cell_rel_errs(pred: str, truth: str) -> list[float]:
    try:
        pt = parse_tokens(pred)
        tt = parse_tokens(truth)
    except ValueError:
        return [1.0]
    if len(pt) != len(tt):
        return [1.0]
    return [relative_err(a, b) for a, b in zip(pt, tt)]


def check_h3_hard(
    *,
    backend: str,
    p95_selected: float,
    p95_idw: float,
    protocol_id: str,
    skip_reason: str | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    """Return (ok, msg, audit_dict).

    When backend == idw_nn (or explicit skip_reason), H3-hard is SKIP (ok=True).
    Else require finite both and p95_selected <= p95_idw (equality allowed).
    """
    backend = (backend or "idw_nn").strip()
    delta: float | None
    if (
        isinstance(p95_selected, float)
        and isinstance(p95_idw, float)
        and not math.isnan(p95_selected)
        and not math.isnan(p95_idw)
    ):
        delta = p95_selected - p95_idw
    else:
        delta = None

    audit: dict[str, Any] = {
        "h3_hard": "SKIP",
        "p95_selected": p95_selected,
        "p95_idw_nn": p95_idw,
        "delta": delta,
        "backend": backend,
        "protocol": protocol_id,
    }

    if backend == "idw_nn" or skip_reason:
        audit["h3_hard"] = "SKIP"
        if skip_reason:
            audit["skip_reason"] = skip_reason
            msg = f"H3-hard SKIP ({skip_reason})"
        else:
            msg = "H3-hard SKIP (backend=idw_nn)"
        return True, msg, audit

    if (
        not isinstance(p95_selected, float)
        or not isinstance(p95_idw, float)
        or math.isnan(p95_selected)
        or math.isnan(p95_idw)
        or math.isinf(p95_selected)
        or math.isinf(p95_idw)
    ):
        audit["h3_hard"] = "FAIL"
        msg = (
            f"H3-hard FAIL: non-finite p95 "
            f"(selected={p95_selected}, idw={p95_idw}) protocol={protocol_id}"
        )
        return False, msg, audit

    if p95_selected <= p95_idw:
        audit["h3_hard"] = "PASS"
        msg = (
            f"H3-hard PASS: p95_selected={p95_selected:.6g} ≤ "
            f"p95_idw_nn={p95_idw:.6g} (delta={delta:.6g}) protocol={protocol_id}"
        )
        return True, msg, audit

    audit["h3_hard"] = "FAIL"
    msg = (
        f"H3-hard FAIL: p95_selected={p95_selected:.6g} > "
        f"p95_idw_nn={p95_idw:.6g} (delta={delta:.6g}) "
        f"backend={backend} protocol={protocol_id}"
    )
    return False, msg, audit


def format_h3_hard_audit(audit: dict[str, Any]) -> list[str]:
    lines = [
        "## H3-hard",
        "",
        f"- **h3_hard**: `{audit.get('h3_hard')}`",
        f"- **backend**: `{audit.get('backend')}`",
        f"- **protocol**: `{audit.get('protocol')}`",
        f"- **p95_selected**: `{audit.get('p95_selected')}`",
        f"- **p95_idw_nn**: `{audit.get('p95_idw_nn')}`",
        f"- **delta**: `{audit.get('delta')}`",
    ]
    if audit.get("skip_reason"):
        lines.append(f"- **skip_reason**: `{audit['skip_reason']}`")
    lines.append("")
    return lines


def holdout_keys(field_keys: list[str] | None = None) -> list[str]:
    keys = [k for k in CORE_KEYS if k not in AXIS_KEYS]
    if field_keys is not None:
        allow = set(field_keys)
        keys = [k for k in keys if k in allow]
    return keys


def p95_vs_truth(
    pred: ConstructResult,
    truth_source: SourceDB,
    instances: list[str],
    pvts: list[str],
    keys: list[str],
) -> float:
    errs: list[float] = []
    for inst in instances:
        for pvt in pvts:
            for key in keys:
                truth = truth_source.get(inst, pvt, key)
                if truth is None:
                    continue
                got = pred.data.get((inst, pvt, key))
                if got is None:
                    errs.append(1.0)
                    continue
                errs.extend(cell_rel_errs(got, truth))
    return p95(errs)


def p95_pred_vs_pred_truth(
    pred_a: ConstructResult,
    pred_b: ConstructResult,
    truth_source: SourceDB,
    instances: list[str],
    pvts: list[str],
    keys: list[str],
) -> tuple[float, float]:
    """Return (p95_a, p95_b) vs the same truth cells."""
    errs_a: list[float] = []
    errs_b: list[float] = []
    for inst in instances:
        for pvt in pvts:
            for key in keys:
                truth = truth_source.get(inst, pvt, key)
                if truth is None:
                    continue
                ga = pred_a.data.get((inst, pvt, key))
                gb = pred_b.data.get((inst, pvt, key))
                if ga is None:
                    errs_a.append(1.0)
                else:
                    errs_a.extend(cell_rel_errs(ga, truth))
                if gb is None:
                    errs_b.append(1.0)
                else:
                    errs_b.extend(cell_rel_errs(gb, truth))
    return p95(errs_a), p95(errs_b)


def find_punched_sidecar(source_path: Path) -> Path | None:
    """Look for punched truth next to source db."""
    p = Path(source_path)
    candidates = [
        Path(str(p) + ".punched.txt"),
        p.with_suffix(p.suffix + ".punched.txt"),
        p.with_name(p.stem + ".punched.txt"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def load_punched_truth(path: Path) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 4:
            rows.append((parts[0], parts[1], parts[2], parts[3]))
    return rows


def drop_instance_pvt(source: SourceDB, inst: str, hold_pvt: str) -> SourceDB:
    """SourceDB view without one (inst, pvt) group — for leave-one-pvt."""
    from ..parse import parse_instance, parse_pvt

    rows = {
        k: v
        for k, v in source.rows.items()
        if not (k[0] == inst and k[1] == hold_pvt)
    }
    groups: dict[tuple[str, str], dict[str, str]] = {}
    for (i, p, key), val in rows.items():
        groups.setdefault((i, p), {})[key] = val
    inst_set = sorted({k[0] for k in groups})
    pvt_set = sorted({k[1] for k in groups})
    key_set = sorted({k[2] for k in rows})
    return SourceDB(
        path=source.path,
        rows=rows,
        instances=inst_set,
        pvts=pvt_set,
        field_keys=key_set,
        inst_parts={n: parse_instance(n) for n in inst_set},
        pvt_parts={n: parse_pvt(n) for n in pvt_set},
        groups=groups,
    )


def idw_config() -> ConstructConfig:
    return ConstructConfig(backend="idw_nn")
