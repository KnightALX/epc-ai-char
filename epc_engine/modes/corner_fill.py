"""Op-Geom: corner_fill_geom — seed rectangle corners → interior targets."""
from __future__ import annotations

from ..construct import construct_b
from ..construct_types import AXIS_KEYS, CellMeta, ConstructResult
from ..job import Job
from ..source import load_source_db
from .common import finish_job, resolve_field_keys, resolve_pvt_list
from .gates_h import check_h1, check_h2_seed_instances
from .geom_seed import resolve_seeds_and_targets
from .h3_hard import (
    check_h3_hard,
    format_h3_hard_audit,
    holdout_keys,
    idw_config,
    p95_pred_vs_pred_truth,
    p95_vs_truth,
)
from .source_util import subset_source


def run_corner_fill(job: Job) -> int:
    gf = job.geom_fill
    if gf is None:
        raise ValueError("mode=corner_fill_geom requires geom_fill: section")

    source = load_source_db(job.source_db)
    print(
        f"[epc] mode=corner_fill_geom operator=corner_fill_geom "
        f"source={job.source_db}"
    )
    seeds, targets = resolve_seeds_and_targets(
        source,
        seed_instances=gf.get("seed_instances"),
        target_instances=list(gf["target_instances"]),
        seed_pool=gf.get("seed_pool"),
        require_corner_coverage=bool(gf.get("require_corner_coverage", True)),
    )
    print(f"[epc] seeds ({len(seeds)}): {seeds}")
    print(f"[epc] targets ({len(targets)}): {targets}")

    base = job.path.parent
    pvts = resolve_pvt_list(gf.get("pvt_list", "all_from_source"), source, base)
    field_keys = resolve_field_keys(job.field_keys_policy, source)
    print(f"[epc] pvts={len(pvts)} keys={len(field_keys)}")

    # Construct interiors using seed-only source so IDW cannot see hold-out interiors
    seed_src = subset_source(source, instances=seeds)
    print("[epc] constructing targets from seed corners…")
    tgt_result = construct_b(seed_src, targets, pvts, field_keys, job.construct)
    print(
        f"[epc] backend_used={tgt_result.backend} fallback={tgt_result.fallback_used} "
        f"model_sha16={tgt_result.model_sha16}"
    )

    # Merge: seeds exact copy + targets constructed
    out_instances = list(dict.fromkeys(seeds + targets))
    result = ConstructResult(
        field_keys=list(field_keys),
        n=tgt_result.n,
        backend=tgt_result.backend,
        prior=tgt_result.prior,
        fallback_used=tgt_result.fallback_used,
        model_path=tgt_result.model_path,
        model_sha16=tgt_result.model_sha16,
        apply_on=tgt_result.apply_on,
    )

    # Seed copy
    sample_group = next(iter(source.groups.values()))
    for inst in seeds:
        for pvt in pvts:
            if not source.has_group(inst, pvt):
                raise RuntimeError(f"seed group missing in source: {inst}×{pvt}")
            result.meta[(inst, pvt)] = CellMeta(
                status="seed_from_source",
                extrapolated=False,
                notes="operator=corner_fill_geom exact seed copy",
            )
            for key in field_keys:
                val = source.get(inst, pvt, key)
                if val is None:
                    if key in AXIS_KEYS:
                        val = sample_group[key]
                    else:
                        raise RuntimeError(f"seed missing cell {inst}/{pvt}/{key}")
                result.data[(inst, pvt, key)] = val

    # Targets
    for (inst, pvt), meta in tgt_result.meta.items():
        meta.notes = (meta.notes + "; operator=corner_fill_geom").strip("; ")
        if meta.status == "seed_from_A":
            # Should not happen for interiors excluded from seed_src; keep label honest
            meta.status = "config_extrapolated"
            meta.extrapolated = True
        result.meta[(inst, pvt)] = meta
    for k, v in tgt_result.data.items():
        result.data[k] = v

    h1_ok, h1_msg = check_h1(result, out_instances, pvts, field_keys)
    print(f"[epc] {h1_msg}")
    h2_ok, h2_msg, _ = check_h2_seed_instances(
        result, source, seeds, pvts, field_keys
    )
    print(f"[epc] {h2_msg}")

    # H3-hard: same-protocol hold-out vs idw_nn when backend ≠ idw_nn
    protocol = f"geom_4corner_holdout:{','.join(targets)}"
    hkeys = holdout_keys(field_keys)
    backend_used = (tgt_result.backend or job.construct.backend or "idw_nn").strip()
    if backend_used == "idw_nn":
        p95_sel = p95_vs_truth(tgt_result, source, targets, pvts, hkeys)
        h3_ok, h3_msg, h3_audit = check_h3_hard(
            backend=backend_used,
            p95_selected=p95_sel,
            p95_idw=p95_sel,
            protocol_id=protocol,
        )
    else:
        print("[epc] H3-hard: constructing idw_nn baseline on same seed/targets…")
        idw_result = construct_b(seed_src, targets, pvts, field_keys, idw_config())
        p95_sel, p95_idw = p95_pred_vs_pred_truth(
            tgt_result, idw_result, source, targets, pvts, hkeys
        )
        h3_ok, h3_msg, h3_audit = check_h3_hard(
            backend=backend_used,
            p95_selected=p95_sel,
            p95_idw=p95_idw,
            protocol_id=protocol,
        )
    print(f"[epc] {h3_msg}")

    h_ok = h1_ok and h2_ok and h3_ok
    h_msg = f"{h1_msg}; {h2_msg}; {h3_msg}"

    extra = [
        "## P2 operator",
        "",
        f"- **mode / operator**: `corner_fill_geom`",
        f"- **seeds**: {', '.join(f'`{s}`' for s in seeds)}",
        f"- **targets**: {', '.join(f'`{t}`' for t in targets)}",
        f"- **backend**: `{result.backend}`",
        f"- **H1**: {h1_msg}",
        f"- **H2**: {h2_msg}",
        f"- **H3-hard**: {h3_msg}",
        "",
    ]
    extra.extend(format_h3_hard_audit(h3_audit))
    return finish_job(
        job,
        source,
        out_instances,
        pvts,
        result,
        h_ok=h_ok,
        h_msg=h_msg,
        extra_audit_lines=extra,
    )
