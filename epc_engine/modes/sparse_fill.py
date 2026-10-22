"""Op-Sparse: pvt_sparse_fill — sparse seed PVTs → full target pvt list."""
from __future__ import annotations

from pathlib import Path

from ..construct import construct_b
from ..construct_types import AXIS_KEYS, CellMeta, ConstructResult
from ..job import Job
from ..source import load_source_db
from .common import (
    finish_job,
    resolve_field_keys,
    resolve_instance_list,
    resolve_pvt_list,
)
from .gates_h import check_h1, check_h2_seed_cells
from .h3_hard import (
    check_h3_hard,
    drop_instance_pvt,
    format_h3_hard_audit,
    holdout_keys,
    idw_config,
    p95_pred_vs_pred_truth,
)


def _complete_pvts_for_instance(
    source, inst: str, field_keys: list[str], n: int
) -> list[str]:
    """PVTs where the instance has a full (non-hole) group for all field_keys."""
    from ..values import parse_tokens

    out = []
    for pvt in source.pvts:
        if not source.has_group(inst, pvt):
            continue
        ok = True
        for key in field_keys:
            val = source.get(inst, pvt, key)
            if val is None or not str(val).strip():
                ok = False
                break
            try:
                toks = parse_tokens(val)
            except ValueError:
                ok = False
                break
            if key in AXIS_KEYS and len(toks) != n:
                ok = False
                break
        if ok:
            out.append(pvt)
    return out


def _truth_source_for_lop(sparse_source, hold_inst: str, hold_pvt: str):
    """Prefer A_ref for hold-out truth; fall back to sparse (pre-drop) values."""
    a_ref = Path("/workspace/epc_fixtures/A_ref.db")
    if a_ref.is_file():
        try:
            full = load_source_db(a_ref)
            if full.get(hold_inst, hold_pvt, "tran_index") is not None:
                return full
        except Exception:
            pass
    return sparse_source


def run_sparse_fill(job: Job) -> int:
    sf = job.sparse_fill
    if sf is None:
        raise ValueError("mode=pvt_sparse_fill requires sparse_fill: section")

    source = load_source_db(job.source_db)
    print(f"[epc] mode=pvt_sparse_fill source={job.source_db}")

    base = job.path.parent
    instances = resolve_instance_list(sf.get("instances", "all_in_source"), source, base)
    target_pvts = resolve_pvt_list(
        sf.get("target_pvt_list", sf.get("pvt_list", "all_from_source")),
        source,
        base,
    )
    # Allow target list from path key used in YAML sketch
    if "target_pvt_list_path" in sf and sf.get("target_pvt_list") is None:
        target_pvts = resolve_pvt_list(sf["target_pvt_list_path"], source, base)

    field_keys = resolve_field_keys(job.field_keys_policy, source)
    sample = next(iter(source.groups.values()))
    n = len(sample["tran_index"].split())

    allow_weak = bool(sf.get("allow_weak_seed", False))
    min_seed = int(sf.get("min_seed_pvts", 3))

    # Per-instance seed PVTs
    seed_map: dict[str, list[str]] = {}
    for inst in instances:
        seeds = _complete_pvts_for_instance(source, inst, field_keys, n)
        if sf.get("seed_pvts") and sf["seed_pvts"] != "auto":
            wanted = set(sf["seed_pvts"])
            seeds = [p for p in seeds if p in wanted]
        seed_map[inst] = seeds
        if len(seeds) < min_seed and not allow_weak:
            raise ValueError(
                f"pvt_sparse_fill: instance {inst} seed_pvts={len(seeds)} < {min_seed} "
                f"and allow_weak_seed=false — FAIL"
            )
        if len(seeds) < 1:
            raise ValueError(
                f"pvt_sparse_fill: instance {inst} has zero complete seed pvts — FAIL"
            )

    print(
        f"[epc] instances={len(instances)} target_pvts={len(target_pvts)} "
        f"min_seed_seen={min(len(v) for v in seed_map.values())}"
    )

    # Construct using source as-is: missing target pvts → pvt_extrapolated via backend.
    # Restrict source PVTs? Keep all seed pvts present in DB so NN works.
    print("[epc] constructing sparse→dense…")
    constructed = construct_b(source, instances, target_pvts, field_keys, job.construct)
    print(
        f"[epc] backend_used={constructed.backend} fallback={constructed.fallback_used} "
        f"model_sha16={constructed.model_sha16}"
    )

    result = ConstructResult(
        field_keys=list(field_keys),
        n=constructed.n,
        backend=constructed.backend,
        prior=constructed.prior,
        fallback_used=constructed.fallback_used,
        model_path=constructed.model_path,
        model_sha16=constructed.model_sha16,
        apply_on=constructed.apply_on,
    )

    intact_cells: list[tuple[str, str, str]] = []
    for inst in instances:
        seed_set = set(seed_map[inst])
        for pvt in target_pvts:
            if pvt in seed_set and source.has_group(inst, pvt):
                # Exact seed copy (H2)
                result.meta[(inst, pvt)] = CellMeta(
                    status="seed_from_source",
                    extrapolated=False,
                    notes="operator=pvt_sparse_fill seed pvt copy",
                )
                for key in field_keys:
                    val = source.get(inst, pvt, key)
                    if val is None:
                        raise RuntimeError(f"sparse seed missing {inst}/{pvt}/{key}")
                    result.data[(inst, pvt, key)] = val
                    intact_cells.append((inst, pvt, key))
            else:
                # Take constructed extrapolation
                meta = constructed.meta[(inst, pvt)]
                meta.notes = (
                    meta.notes + "; operator=pvt_sparse_fill"
                ).strip("; ")
                if not meta.extrapolated:
                    meta.extrapolated = True
                    meta.status = "pvt_extrapolated"
                result.meta[(inst, pvt)] = meta
                for key in field_keys:
                    result.data[(inst, pvt, key)] = constructed.data[(inst, pvt, key)]

    h1_ok, h1_msg = check_h1(result, instances, target_pvts, field_keys)
    print(f"[epc] {h1_msg}")
    h2_ok, h2_msg, _ = check_h2_seed_cells(result, source, intact_cells)
    print(f"[epc] {h2_msg}")

    # H3-hard: leave-one-pvt on first instance's first seed pvt (matches eval_h3)
    backend_used = (constructed.backend or job.construct.backend or "idw_nn").strip()
    lop_inst = instances[0]
    hold_pvt = seed_map[lop_inst][0]
    protocol = f"sparse_lop:{lop_inst}:{hold_pvt}"
    hkeys = holdout_keys(field_keys)
    if backend_used == "idw_nn":
        h3_ok, h3_msg, h3_audit = check_h3_hard(
            backend=backend_used,
            p95_selected=float("nan"),
            p95_idw=float("nan"),
            protocol_id=protocol,
        )
    else:
        print(
            f"[epc] H3-hard leave-one-pvt: hide {lop_inst}×{hold_pvt}, "
            "compare selected vs idw_nn…"
        )
        src2 = drop_instance_pvt(source, lop_inst, hold_pvt)
        truth_src = _truth_source_for_lop(source, lop_inst, hold_pvt)
        r_sel = construct_b(src2, [lop_inst], [hold_pvt], hkeys, job.construct)
        r_idw = construct_b(src2, [lop_inst], [hold_pvt], hkeys, idw_config())
        p95_sel, p95_idw = p95_pred_vs_pred_truth(
            r_sel, r_idw, truth_src, [lop_inst], [hold_pvt], hkeys
        )
        h3_ok, h3_msg, h3_audit = check_h3_hard(
            backend=backend_used,
            p95_selected=p95_sel,
            p95_idw=p95_idw,
            protocol_id=protocol,
        )
    print(f"[epc] {h3_msg}")

    extra = [
        "## P2 operator",
        "",
        f"- **mode / operator**: `pvt_sparse_fill`",
        f"- **allow_weak_seed**: `{allow_weak}`",
        f"- **min_seed_pvts**: `{min_seed}`",
        f"- **H1**: {h1_msg}",
        f"- **H2**: {h2_msg}",
        f"- **H3-hard**: {h3_msg}",
        "",
        "### Seed PVT counts",
        "",
    ]
    for inst in instances:
        extra.append(f"- `{inst}`: {len(seed_map[inst])} seeds")
    extra.append("")
    extra.extend(format_h3_hard_audit(h3_audit))

    return finish_job(
        job,
        source,
        instances,
        target_pvts,
        result,
        h_ok=h1_ok and h2_ok and h3_ok,
        h_msg=f"{h1_msg}; {h2_msg}; {h3_msg}",
        extra_audit_lines=extra,
    )
