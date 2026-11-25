"""Op-Miss: pvt_missing_fill — fill missing/bad keys inside existing groups."""
from __future__ import annotations

from pathlib import Path

from ..backends import idw_nn
from ..construct_types import AXIS_KEYS, CellMeta, ConstructResult
from ..job import Job
from ..parse import parse_instance
from ..source import load_source_db
from ..values import parse_tokens
from .common import (
    finish_job,
    resolve_field_keys,
    resolve_instance_list,
    resolve_pvt_list,
)
from .gates_h import check_h1, check_h2_seed_cells, p95
from .h3_hard import (
    cell_rel_errs,
    check_h3_hard,
    find_punched_sidecar,
    format_h3_hard_audit,
    load_punched_truth,
)


def _is_bad_value(val: str | None, n: int, key: str) -> bool:
    if val is None:
        return True
    s = val.strip()
    if not s:
        return True
    try:
        toks = parse_tokens(s)
    except ValueError:
        return True
    if key in AXIS_KEYS:
        return len(toks) != n
    if len(toks) == 1:
        return False
    if len(toks) == n * n:
        return False
    if len(toks) == n:
        return False
    return True


def run_missing_fill(job: Job) -> int:
    mf = job.missing_fill
    if mf is None:
        raise ValueError("mode=pvt_missing_fill requires missing_fill: section")

    source = load_source_db(job.source_db)
    print(f"[epc] mode=pvt_missing_fill source={job.source_db}")

    create_missing = bool(mf.get("create_missing_groups", False))
    base = job.path.parent
    instances = resolve_instance_list(mf.get("instances", "all_in_source"), source, base)
    pvts = resolve_pvt_list(mf.get("pvts", "all_from_source"), source, base)
    field_keys = resolve_field_keys(job.field_keys_policy, source)

    # Infer N from any existing group
    sample = next(iter(source.groups.values()))
    n = len(sample["tran_index"].split())

    # Red path: YAML demands groups that don't exist
    demand_groups = mf.get("require_groups")  # optional list of [inst,pvt]
    if demand_groups:
        missing_groups = [
            (a, b)
            for a, b in demand_groups
            if not source.has_group(a, b)
        ]
        if missing_groups and not create_missing:
            raise ValueError(
                f"pvt_missing_fill: {len(missing_groups)} whole groups absent "
                f"and create_missing_groups=false — FAIL (use Op-Sparse). "
                f"example={missing_groups[0]}"
            )

    # Also: if instances×pvts includes absent groups and create_missing false,
    # we only operate on existing intersection (do not invent groups).
    existing_pairs = [
        (i, p) for i in instances for p in pvts if source.has_group(i, p)
    ]
    absent = [
        (i, p) for i in instances for p in pvts if not source.has_group(i, p)
    ]
    if absent and mf.get("fail_if_absent_groups", False) and not create_missing:
        raise ValueError(
            f"pvt_missing_fill: absent groups ({len(absent)}) with "
            f"fail_if_absent_groups and create_missing_groups=false"
        )

    # Detect holes
    holes: list[tuple[str, str, str]] = []
    intact: list[tuple[str, str, str]] = []
    for inst, pvt in existing_pairs:
        for key in field_keys:
            val = source.get(inst, pvt, key)
            if _is_bad_value(val, n, key):
                holes.append((inst, pvt, key))
            else:
                intact.append((inst, pvt, key))

    print(
        f"[epc] existing_groups={len(existing_pairs)} holes={len(holes)} "
        f"intact={len(intact)} absent_groups={len(absent)}"
    )

    # Build output covering existing_pairs only (default) — full key set
    out_instances = sorted({i for i, _ in existing_pairs})
    out_pvts = sorted({p for _, p in existing_pairs})
    # Preserve YAML order when possible
    out_instances = [i for i in instances if i in set(out_instances)]
    out_pvts = [p for p in pvts if p in set(out_pvts)]

    result = ConstructResult(
        field_keys=list(field_keys),
        n=n,
        backend=job.construct.backend,
        prior=job.construct.prior,
        apply_on=job.construct.apply_on,
    )

    # First copy intact + axes
    for inst, pvt in existing_pairs:
        result.meta[(inst, pvt)] = CellMeta(
            status="seed_from_source",
            extrapolated=False,
            notes="operator=pvt_missing_fill intact group",
        )
        for key in field_keys:
            val = source.get(inst, pvt, key)
            if not _is_bad_value(val, n, key):
                result.data[(inst, pvt, key)] = val  # type: ignore[arg-type]

    def _fill_one(inst: str, pvt: str, key: str) -> str:
        """Fill one hole: same-pvt IDW → same-inst other PVT → global donor."""
        ip = parse_instance(inst)
        # 1) geometry IDW at same pvt among donors that still have key
        try:
            return idw_nn.lookup_or_idw(source, inst, ip, pvt, key)
        except Exception:
            pass
        # 2) same instance, nearest other pvt that has key
        from ..parse import parse_pvt, pvt_distance

        target_pp = parse_pvt(pvt)
        donors = []
        for opvt in source.pvts:
            if opvt == pvt:
                continue
            val = source.get(inst, opvt, key)
            if val is None or not str(val).strip():
                continue
            donors.append((pvt_distance(target_pp, source.pvt_parts[opvt]), opvt, val))
        if donors:
            donors.sort()
            _, nn_name, val = donors[0]
            return idw_nn.optional_pvt_scale(source, val, key, target_pp, nn_name)
        # 3) any other instance×pvt with this key (closest geom then pvt)
        from ..parse import geom_distance

        best = None
        for (oi, op), g in source.groups.items():
            if oi == inst and op == pvt:
                continue
            val = g.get(key)
            if val is None:
                continue
            d = geom_distance(ip, source.inst_parts[oi]) + pvt_distance(
                target_pp, source.pvt_parts[op]
            )
            if best is None or d < best[0]:
                best = (d, val, op)
        if best is None:
            raise RuntimeError(f"no donor for hole {inst}×{pvt}×{key}")
        return idw_nn.optional_pvt_scale(source, best[1], key, target_pp, best[2])

    hole_notes: list[str] = []
    for inst, pvt, key in holes:
        if key in AXIS_KEYS:
            result.data[(inst, pvt, key)] = sample[key]
            hole_notes.append(f"{inst}×{pvt}×{key}=axis_repaired")
            continue
        val = _fill_one(inst, pvt, key)
        result.data[(inst, pvt, key)] = val
        meta = result.meta[(inst, pvt)]
        meta.status = "missing_filled"
        meta.extrapolated = True
        meta.notes = "operator=pvt_missing_fill provisional=true"
        hole_notes.append(f"{inst}×{pvt}×{key}")

    # Ensure every existing pair has all keys
    for inst, pvt in existing_pairs:
        for key in field_keys:
            if (inst, pvt, key) not in result.data:
                if key in AXIS_KEYS:
                    result.data[(inst, pvt, key)] = sample[key]
                else:
                    ip = parse_instance(inst)
                    result.data[(inst, pvt, key)] = idw_nn.lookup_or_idw(
                        source, inst, ip, pvt, key
                    )

    # Hole fill uses IDW lookup (groups with holes cannot run seed_from_A construct).

    h1_ok, h1_msg = check_h1(result, out_instances, out_pvts, field_keys)
    print(f"[epc] {h1_msg}")
    h2_ok, h2_msg, _ = check_h2_seed_cells(result, source, intact)
    print(f"[epc] {h2_msg}")

    backend_used = (job.construct.backend or "idw_nn").strip()
    protocol = f"miss_punched_holes:{Path(source.path).name}"
    if backend_used == "idw_nn":
        h3_ok, h3_msg, h3_audit = check_h3_hard(
            backend=backend_used,
            p95_selected=float("nan"),
            p95_idw=float("nan"),
            protocol_id=protocol,
        )
    else:
        punch = find_punched_sidecar(Path(source.path))
        if punch is None:
            h3_ok, h3_msg, h3_audit = check_h3_hard(
                backend=backend_used,
                p95_selected=float("nan"),
                p95_idw=float("nan"),
                protocol_id=protocol,
                skip_reason="no punched truth sidecar",
            )
        else:
            punched = load_punched_truth(punch)
            errs_sel: list[float] = []
            errs_idw: list[float] = []
            for inst, pvt, key, truth in punched:
                got = result.data.get((inst, pvt, key))
                if got is None:
                    errs_sel.append(1.0)
                else:
                    errs_sel.extend(cell_rel_errs(got, truth))
                # Re-fill with idw path for baseline (same helper)
                try:
                    if key in AXIS_KEYS:
                        idw_val = sample[key]
                    else:
                        idw_val = _fill_one(inst, pvt, key)
                    errs_idw.extend(cell_rel_errs(idw_val, truth))
                except Exception:
                    errs_idw.append(1.0)
            h3_ok, h3_msg, h3_audit = check_h3_hard(
                backend=backend_used,
                p95_selected=p95(errs_sel),
                p95_idw=p95(errs_idw),
                protocol_id=protocol,
            )
    print(f"[epc] {h3_msg}")

    extra = [
        "## P2 operator",
        "",
        f"- **mode / operator**: `pvt_missing_fill`",
        f"- **create_missing_groups**: `{create_missing}`",
        f"- **holes filled**: {len(holes)}",
        f"- **intact (H2)**: {len(intact)}",
        f"- **H1**: {h1_msg}",
        f"- **H2**: {h2_msg}",
        f"- **H3-hard**: {h3_msg}",
        "",
        "### Missing list (sample ≤40)",
        "",
    ]
    for h in hole_notes[:40]:
        extra.append(f"- `{h}`")
    if len(hole_notes) > 40:
        extra.append(f"- … +{len(hole_notes) - 40} more")
    extra.append("")
    extra.extend(format_h3_hard_audit(h3_audit))

    return finish_job(
        job,
        source,
        out_instances,
        out_pvts,
        result,
        h_ok=h1_ok and h2_ok and h3_ok,
        h_msg=f"{h1_msg}; {h2_msg}; {h3_msg}",
        extra_audit_lines=extra,
    )
