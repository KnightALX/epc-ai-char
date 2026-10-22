"""AB-hard: offline LOI/LOP p95_selected ≤ p95_idw_nn + online read-only stamp.

Decoupled from P2 Op-Geom H3-hard (modes/h3_hard.py). Do not import that module.
"""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")
PROTOCOL_ID = "loi_v0+lop_v0"
PROTOCOL_LOI = "loi_v0"
PROTOCOL_LOP = "lop_v0"

# Gate ID renames (strict-< → ≤); keep legacy aliases for history links.
GATE_AB_LOI = "AB-hard-LOI"
GATE_AB_LOP = "AB-hard-LOP"
GATE_ALIAS_LOI = "P-LOI-base"  # historical alias of AB-hard-LOI
GATE_ALIAS_LOP = "P-LOP"  # historical alias of AB-hard-LOP
GATE_LOI_REG = "P-LOI-reg"


def stamp_path_for(model_path: Path | str | None) -> Path | None:
    if model_path is None:
        return None
    p = Path(model_path)
    return p.with_suffix(p.suffix + ".ab_hard.json")


def evaluate_ab_hard_gates(
    p95_selected_loi: float,
    p95_idw_loi: float,
    p95_selected_lop: float,
    p95_idw_lop: float,
    *,
    p95_loi_reg_ok: bool | None = None,
) -> tuple[bool, dict[str, bool], dict[str, Any]]:
    """Offline AB-hard: both LOI and LOP require p95_sel ≤ p95_idw (equality OK).

    Returns (all_ab_hard_ok, gates_dict, detail).
    P-LOI-reg is orthogonal; pass p95_loi_reg_ok if known (included in overall
    hard-exit set by train, but not required for stamp.ab_hard PASS which is
    AB-hard-LOI ∧ AB-hard-LOP only).
    """
    loi_ok = (
        _finite(p95_selected_loi)
        and _finite(p95_idw_loi)
        and p95_selected_loi <= p95_idw_loi
    )
    lop_ok = (
        _finite(p95_selected_lop)
        and _finite(p95_idw_lop)
        and p95_selected_lop <= p95_idw_lop
    )
    gates = {
        GATE_AB_LOI: loi_ok,
        GATE_AB_LOP: lop_ok,
        # Aliases (same boolean) so old docs/CI still resolve
        GATE_ALIAS_LOI: loi_ok,
        GATE_ALIAS_LOP: lop_ok,
    }
    if p95_loi_reg_ok is not None:
        gates[GATE_LOI_REG] = bool(p95_loi_reg_ok)

    detail = {
        "protocol": PROTOCOL_ID,
        "loi": {
            "protocol": PROTOCOL_LOI,
            "p95_selected": p95_selected_loi,
            "p95_idw_nn": p95_idw_loi,
            "delta": _delta(p95_selected_loi, p95_idw_loi),
            "pass": loi_ok,
        },
        "lop": {
            "protocol": PROTOCOL_LOP,
            "p95_selected": p95_selected_lop,
            "p95_idw_nn": p95_idw_lop,
            "delta": _delta(p95_selected_lop, p95_idw_lop),
            "pass": lop_ok,
        },
        "compare": "<=",
        "note": (
            "AB-hard uses ≤ (unify with H3-hard); replaces algo-upgrade strict < "
            f"for {GATE_ALIAS_LOI}/{GATE_ALIAS_LOP}."
        ),
    }
    return loi_ok and lop_ok, gates, detail


def build_stamp(
    *,
    model_sha16: str,
    backend: str,
    p95_selected_loi: float,
    p95_idw_loi: float,
    p95_selected_lop: float,
    p95_idw_lop: float,
    gates: dict[str, bool] | None = None,
    source_path: str | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    ok, g, detail = evaluate_ab_hard_gates(
        p95_selected_loi,
        p95_idw_loi,
        p95_selected_lop,
        p95_idw_lop,
    )
    if gates:
        g = {**g, **gates}
        ok = bool(g.get(GATE_AB_LOI) and g.get(GATE_AB_LOP))
    now = datetime.now(tz=SHANGHAI).isoformat(timespec="seconds")
    return {
        "ab_hard": "PASS" if ok else "FAIL",
        "ab_hard_protocol": PROTOCOL_ID,
        "backend": backend,
        "model_sha16": model_sha16,
        "stamp_sha16": model_sha16,
        "stamp_generated": now,
        "generated": now,
        "source_path": source_path,
        "seed": seed,
        "p95_selected_loi": p95_selected_loi,
        "p95_idw_loi": p95_idw_loi,
        "p95_selected_lop": p95_selected_lop,
        "p95_idw_lop": p95_idw_lop,
        "delta_loi": detail["loi"]["delta"],
        "delta_lop": detail["lop"]["delta"],
        "gates": {
            GATE_AB_LOI: bool(g.get(GATE_AB_LOI)),
            GATE_AB_LOP: bool(g.get(GATE_AB_LOP)),
            GATE_LOI_REG: g.get(GATE_LOI_REG),
            GATE_ALIAS_LOI: bool(g.get(GATE_ALIAS_LOI, g.get(GATE_AB_LOI))),
            GATE_ALIAS_LOP: bool(g.get(GATE_ALIAS_LOP, g.get(GATE_AB_LOP))),
        },
        "compare": "<=",
        "detail": detail,
    }


def write_stamp(stamp: dict[str, Any], model_path: Path | str) -> Path:
    path = stamp_path_for(model_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_stamp(model_path: Path | str | None) -> dict[str, Any] | None:
    """Load sidecar stamp; also try embedding from joblib bundle meta."""
    if model_path is None:
        return None
    path = stamp_path_for(model_path)
    if path is not None and path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    # Fallback: joblib meta key "ab_hard_stamp"
    try:
        import joblib

        p = Path(model_path)
        if p.is_file():
            bundle = joblib.load(p)
            if isinstance(bundle, dict):
                emb = bundle.get("ab_hard_stamp")
                if isinstance(emb, dict):
                    return emb
    except Exception:
        pass
    return None


def check_ab_hard_online(
    *,
    backend: str,
    model_path: Path | str | None,
    model_sha16: str | None = None,
    fallback_used: bool = False,
) -> tuple[bool, str, dict[str, Any]]:
    """Online epc_ab gate: read stamp only (no LOI fold recompute).

    - idw_nn → SKIP (ok)
    - residual with model-missing fallback → SKIP (ok, noted)
    - else require stamp PASS + matching sha
    """
    backend = (backend or "idw_nn").strip()
    audit: dict[str, Any] = {
        "ab_hard": "SKIP",
        "ab_hard_protocol": PROTOCOL_ID,
        "backend": backend,
        "model_path": str(model_path) if model_path else None,
        "stamp_sha16": None,
        "stamp_generated": None,
        "p95_selected_loi": None,
        "p95_idw_loi": None,
        "p95_selected_lop": None,
        "p95_idw_lop": None,
        "reason": None,
    }

    if backend == "idw_nn":
        audit["ab_hard"] = "SKIP"
        audit["reason"] = "backend_idw_nn"
        return True, "ab_hard: SKIP (backend=idw_nn)", audit

    if fallback_used and (
        model_path is None or not Path(model_path).is_file()
    ):
        audit["ab_hard"] = "SKIP"
        audit["reason"] = "model_missing_fallback"
        return (
            True,
            "ab_hard: SKIP (model missing → idw fallback; not masking AB-hard FAIL)",
            audit,
        )

    stamp = load_stamp(model_path)
    if stamp is None:
        audit["ab_hard"] = "FAIL"
        audit["reason"] = "missing_stamp"
        msg = (
            "ab_hard: FAIL (missing_stamp) — non-idw backend requires "
            f"sidecar {stamp_path_for(model_path)} or bundle ab_hard_stamp"
        )
        return False, msg, audit

    # Copy numeric fields for audit
    for k in (
        "p95_selected_loi",
        "p95_idw_loi",
        "p95_selected_lop",
        "p95_idw_lop",
        "stamp_generated",
        "generated",
    ):
        if k in stamp and stamp[k] is not None:
            audit[k if k != "generated" else "stamp_generated"] = stamp[k]
    audit["stamp_sha16"] = stamp.get("model_sha16") or stamp.get("stamp_sha16")
    audit["ab_hard_protocol"] = stamp.get("ab_hard_protocol") or PROTOCOL_ID

    status = str(stamp.get("ab_hard") or "").upper()
    if status != "PASS":
        audit["ab_hard"] = "FAIL"
        audit["reason"] = "offline_fail"
        msg = (
            f"ab_hard: FAIL (offline_fail) stamp.ab_hard={status!r} "
            f"backend={backend}"
        )
        return False, msg, audit

    stamp_sha = str(stamp.get("model_sha16") or stamp.get("stamp_sha16") or "")
    live_sha = model_sha16
    if live_sha is None and model_path and Path(model_path).is_file():
        live_sha = _sha16(Path(model_path))
    if not stamp_sha or not live_sha or stamp_sha != live_sha:
        audit["ab_hard"] = "FAIL"
        audit["reason"] = "stale"
        audit["live_sha16"] = live_sha
        msg = (
            f"ab_hard: FAIL (stale) stamp_sha16={stamp_sha!r} "
            f"live_sha16={live_sha!r}"
        )
        return False, msg, audit

    # Stamp claims PASS but re-check ≤ from recorded p95 (defense in depth)
    try:
        sel_loi = float(stamp["p95_selected_loi"])
        idw_loi = float(stamp["p95_idw_loi"])
        sel_lop = float(stamp["p95_selected_lop"])
        idw_lop = float(stamp["p95_idw_lop"])
    except (KeyError, TypeError, ValueError):
        audit["ab_hard"] = "FAIL"
        audit["reason"] = "missing_stamp"
        return False, "ab_hard: FAIL (stamp missing p95 fields)", audit

    ok, _, _ = evaluate_ab_hard_gates(sel_loi, idw_loi, sel_lop, idw_lop)
    if not ok:
        audit["ab_hard"] = "FAIL"
        audit["reason"] = "offline_fail"
        return False, "ab_hard: FAIL (stamp p95 violate ≤)", audit

    audit["ab_hard"] = "PASS"
    audit["reason"] = None
    msg = (
        f"ab_hard: PASS protocol={PROTOCOL_ID} "
        f"loi={sel_loi:.6g}≤{idw_loi:.6g} lop={sel_lop:.6g}≤{idw_lop:.6g} "
        f"stamp_sha16={stamp_sha}"
    )
    return True, msg, audit


def format_ab_hard_audit(audit: dict[str, Any]) -> list[str]:
    lines = [
        "## AB-hard (epc_ab hold-out stamp)",
        "",
        f"- **ab_hard**: `{audit.get('ab_hard')}`",
        f"- **ab_hard_protocol**: `{audit.get('ab_hard_protocol')}`",
        f"- **backend**: `{audit.get('backend')}`",
        f"- **p95_selected_loi**: `{audit.get('p95_selected_loi')}`",
        f"- **p95_idw_loi**: `{audit.get('p95_idw_loi')}`",
        f"- **p95_selected_lop**: `{audit.get('p95_selected_lop')}`",
        f"- **p95_idw_lop**: `{audit.get('p95_idw_lop')}`",
        f"- **stamp_sha16**: `{audit.get('stamp_sha16')}`",
        f"- **stamp_generated**: `{audit.get('stamp_generated')}`",
    ]
    if audit.get("reason"):
        lines.append(f"- **reason**: `{audit['reason']}`")
    if audit.get("live_sha16"):
        lines.append(f"- **live_sha16**: `{audit['live_sha16']}`")
    lines.append("")
    return lines


def stamp_from_holdout_report(
    report: dict[str, Any],
    *,
    model_sha16: str,
    backend: str = "residual_gbdt",
) -> dict[str, Any]:
    lb = report["loi_baseline"]
    lr = report["loi_residual"]
    pb = report["lop_baseline"]
    pr = report["lop_residual"]
    gates = report.get("gates") or {}
    return build_stamp(
        model_sha16=model_sha16,
        backend=backend,
        p95_selected_loi=float(lr["p95"]),
        p95_idw_loi=float(lb["p95"]),
        p95_selected_lop=float(pr["p95"]),
        p95_idw_lop=float(pb["p95"]),
        gates=gates,
        source_path=report.get("source_path"),
        seed=report.get("seed"),
    )


def _finite(x: float) -> bool:
    return isinstance(x, (int, float)) and not math.isnan(x) and not math.isinf(x)


def _delta(sel: float, idw: float) -> float | None:
    if _finite(sel) and _finite(idw):
        return float(sel) - float(idw)
    return None


def _sha16(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]
