"""residual_gbdt: v_hat = prior(idw_nn) + residual_GBDT(x).

Online default apply_on=all_extrapolated: every non-seed group gets residual.
Dual-head bundle (models_geom / models_pvt) preferred; legacy single "models"
falls back to geom head for all residual applications.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import joblib
import numpy as np

from ..construct_types import AXIS_KEYS, ConstructResult
from ..job import ConstructConfig
from ..parse import parse_instance, parse_pvt
from ..source import SourceDB
from ..values import format_tokens, parse_tokens
from . import idw_nn
from .features import cell_coords, feature_row


def _sha16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_model_bundle(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"residual model not found: {path}")
    bundle = joblib.load(path)
    if not isinstance(bundle, dict):
        raise ValueError(f"bad residual model bundle: {path}")
    # Accept dual-head or legacy single "models"
    if "models_geom" not in bundle and "models" not in bundle:
        raise ValueError(f"bad residual model bundle (no models*): {path}")
    return bundle


def _heads(bundle: dict) -> tuple[dict, dict]:
    geom = bundle.get("models_geom") or bundle.get("models") or {}
    pvt = bundle.get("models_pvt") or geom
    return geom, pvt


def _extrapolation_reason(
    b_inst: str,
    b_pvt: str,
    a_inst_set: set[str],
    a_pvt_set: set[str],
    source: SourceDB,
) -> str:
    """Return seed_from_A | geom | pvt | both."""
    in_i = b_inst in a_inst_set
    in_p = b_pvt in a_pvt_set
    if in_i and in_p and source.has_group(b_inst, b_pvt):
        return "seed_from_A"
    if (not in_i) and (not in_p):
        return "both"
    if not in_i:
        return "geom"
    return "pvt"


def construct(
    source: SourceDB,
    b_instances: list[str],
    b_pvts: list[str],
    field_keys: list[str],
    cfg: ConstructConfig,
) -> ConstructResult:
    model_path = cfg.model_path
    fallback = (cfg.fallback or "idw_nn").strip()
    prior_name = (cfg.prior or "idw_nn").strip()
    apply_on = (cfg.apply_on or "all_extrapolated").strip()

    if model_path is None or not Path(model_path).is_file():
        if fallback == "idw_nn":
            result = idw_nn.construct(source, b_instances, b_pvts, field_keys)
            result.backend = "residual_gbdt"
            result.prior = prior_name
            result.fallback_used = True
            result.model_path = model_path
            result.model_sha16 = None
            result.apply_on = apply_on
            for (inst, pvt), meta in result.meta.items():
                meta.residual_applied = False
                meta.residual_reason = "fallback"
                meta.notes = (meta.notes + "; residual fallback→idw_nn").strip("; ")
            return result
        raise FileNotFoundError(
            f"residual_gbdt model_path missing and fallback={fallback!r}"
        )

    bundle = load_model_bundle(Path(model_path))
    models_geom, models_pvt = _heads(bundle)
    # Keys eligible for pvt-head residual (meaningful leave-pvt prior error).
    # None / missing → apply all keys (legacy bundles).
    raw_apply = bundle.get("pvt_apply_keys")
    pvt_apply_keys: set[str] | None = (
        set(raw_apply) if isinstance(raw_apply, (list, tuple, set)) else None
    )
    n_axis = int(bundle.get("n_axis", 5))
    tran_axis = [float(x) for x in bundle.get("tran_axis", list(range(n_axis)))]
    load_axis = [float(x) for x in bundle.get("load_axis", list(range(n_axis)))]

    prior_result = idw_nn.construct(source, b_instances, b_pvts, field_keys)
    result = ConstructResult(
        data=dict(prior_result.data),
        meta=dict(prior_result.meta),
        field_keys=list(field_keys),
        n=prior_result.n,
        backend="residual_gbdt",
        prior=prior_name,
        fallback_used=False,
        model_path=Path(model_path),
        model_sha16=_sha16(Path(model_path)),
        apply_on=apply_on,
    )

    a_inst_set = set(source.instances)
    a_pvt_set = set(source.pvts)

    for b_inst in b_instances:
        ip = parse_instance(b_inst)
        for b_pvt in b_pvts:
            pp = parse_pvt(b_pvt)
            meta = result.meta[(b_inst, b_pvt)]
            reason = _extrapolation_reason(
                b_inst, b_pvt, a_inst_set, a_pvt_set, source
            )

            if reason == "seed_from_A":
                meta.residual_applied = False
                meta.residual_reason = "seed_from_A"
                meta.notes = (
                    meta.notes + "; residual_applied=false (seed_from_A)"
                ).strip("; ")
                continue

            # geom_only: skip pure-PVT (and keep prior)
            if apply_on == "geom_only" and reason == "pvt":
                meta.residual_applied = False
                meta.residual_reason = "geom_only_skip"
                meta.notes = (
                    meta.notes
                    + "; residual_applied=false (geom_only; pvt-only skipped)"
                ).strip("; ")
                continue

            # Choose head: pvt-only → pvt head; geom/both → geom head
            if reason == "pvt":
                models = models_pvt
                head = "pvt"
            else:
                models = models_geom
                head = "geom"

            # NN pvt for Δ features (same rule as prior)
            if b_pvt in a_pvt_set:
                nn_pp = pp
            else:
                nn_name = idw_nn.nearest_pvt(pp, source)
                nn_pp = source.pvt_parts[nn_name]

            applied_any = False
            for key in field_keys:
                if key in AXIS_KEYS:
                    continue
                if (
                    head == "pvt"
                    and pvt_apply_keys is not None
                    and key not in pvt_apply_keys
                ):
                    continue
                model = models.get(key)
                if model is None:
                    continue
                prior_toks = parse_tokens(result.data[(b_inst, b_pvt, key)])
                coords = cell_coords(len(prior_toks), n_axis)
                new_toks: list[float] = []
                X_rows = []
                for flat_i, i, j in coords:
                    tran_v = tran_axis[i] if i < len(tran_axis) else float(i)
                    load_v = load_axis[j] if j < len(load_axis) else float(j)
                    if len(prior_toks) == 1:
                        tran_v, load_v = 0.0, 0.0
                    X_rows.append(
                        feature_row(
                            ip,
                            pp,
                            cell_i=i,
                            cell_j=j,
                            tran_val=tran_v,
                            load_val=load_v,
                            prior_hat=prior_toks[flat_i],
                            nn_pp=nn_pp,
                        )
                    )
                X = np.asarray(X_rows, dtype=np.float64)
                resid = model.predict(X)
                for flat_i, _, _ in coords:
                    new_toks.append(float(prior_toks[flat_i] + resid[flat_i]))
                result.data[(b_inst, b_pvt, key)] = format_tokens(new_toks)
                applied_any = True

            if not applied_any and head == "pvt":
                # Gated: no eligible keys → keep prior; still mark reason
                meta.residual_applied = False
                meta.residual_reason = reason
                meta.notes = (
                    meta.notes
                    + f"; residual_applied=false reason={reason} "
                    + "(pvt_apply_keys gate; prior kept)"
                ).strip("; ")
                continue

            meta.residual_applied = True
            meta.residual_reason = reason
            meta.notes = (
                meta.notes
                + f"; residual_applied=true reason={reason} head={head}"
                + f"(+{Path(model_path).name})"
            ).strip("; ")

    return result
