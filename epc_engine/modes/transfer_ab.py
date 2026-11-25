"""Online mode: transfer_ab — A_src + A_tgt_seed → B_tgt.

Must NOT read hold-out / A_tgt_full truth.
Accuracy hard gate is offline suite; this path writes B_tgt + audit.
No transfer stamp this round.
"""
from __future__ import annotations

import sys
from pathlib import Path

from ..audit import write_audit
from ..construct_types import AXIS_KEYS, CellMeta, ConstructResult
from ..paths import portable
from ..job import Job, load_target_lists
from ..source import load_source_db
from ..transfer_lib import PROTOCOL_ID, train_transfer_bundle, predict_group_value
from ..write_db import write_b_db


def _resolve_seed_db(job: Job) -> Path:
    raw = job.raw.get("target") or {}
    seed = raw.get("seed_db") or raw.get("seed_db_path")
    if not seed:
        raise ValueError("transfer_ab: target.seed_db required")
    p = portable(seed)
    if not p.is_absolute():
        p = (job.path.parent / p).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"transfer_ab seed_db not found: {p}")
    return p


def _backend(job: Job) -> str:
    cfg = job.construct
    b = (cfg.backend or "residual_tl").strip()
    # nested residual_tl / linear_tr blocks allowed
    raw_c = cfg.raw or {}
    if b in ("residual_tl", "linear_tr"):
        return b
    # if user put backend under nested key
    if isinstance(raw_c.get("residual_tl"), dict) and not raw_c.get("backend"):
        return "residual_tl"
    if b in ("residual_gbdt", "idw_nn"):
        raise ValueError(
            f"transfer_ab: construct.backend={b!r} not valid here; "
            "use residual_tl|linear_tr"
        )
    raise ValueError(
        f"transfer_ab: unknown construct.backend={b!r}; expected residual_tl|linear_tr"
    )


def construct_transfer(
    job: Job,
    *,
    b_instances: list[str],
    b_pvts: list[str],
    field_keys: list[str],
) -> ConstructResult:
    src = load_source_db(job.source_db)
    seed_path = _resolve_seed_db(job)
    seed = load_source_db(seed_path)
    backend = _backend(job)

    # Train keys: all non-axis keys we will write (or at least intersection)
    train_keys = [k for k in field_keys if k not in AXIS_KEYS and k in src.field_keys]
    bundle = train_transfer_bundle(
        src, seed, train_keys, backend=backend
    )

    data: dict[tuple[str, str, str], str] = {}
    meta: dict[tuple[str, str], CellMeta] = {}
    for inst in b_instances:
        for pvt in b_pvts:
            # Prefer seed truth when available (visible target seed)
            use_seed = seed.has_group(inst, pvt)
            for key in field_keys:
                if use_seed and key in seed.groups[(inst, pvt)]:
                    val = seed.groups[(inst, pvt)][key]
                    status = "seed_from_tgt"
                else:
                    val = predict_group_value(bundle, src, inst, pvt, key)
                    if val is None:
                        # fallback: try copy src axis
                        if key in AXIS_KEYS and src.has_group(inst, pvt):
                            val = src.get(inst, pvt, key)
                        else:
                            # NEVER fabricate "0" and let the gate pass on it:
                            # a missing prediction must surface as a hard error.
                            raise ValueError(
                                f"transfer backend {backend} could not predict "
                                f"{inst}/{pvt}/{key} and no source axis to copy"
                            )
                    status = "transfer_pred"
                data[(inst, pvt, key)] = val  # type: ignore[assignment]
            meta[(inst, pvt)] = CellMeta(
                status=status if use_seed else "transfer_pred",
                extrapolated=not use_seed,
                notes=f"backend={backend}; protocol={PROTOCOL_ID}",
                residual_applied=(backend == "residual_tl" and not use_seed),
                residual_reason="transfer_rtl" if backend == "residual_tl" else "transfer_tr",
            )

    return ConstructResult(
        data=data,
        meta=meta,
        field_keys=list(field_keys),
        n=5,
        backend=backend,
        prior="linear_tr",
        fallback_used=False,
        model_path=None,
        model_sha16=None,
        apply_on="transfer_seed_fit",
    )


def run_transfer_ab(job: Job) -> int:
    print(f"[epc] mode=transfer_ab job={job.job_name} yaml={job.path}")
    print(f"[epc] source(A_src)={job.source_db}")
    seed_path = _resolve_seed_db(job)
    print(f"[epc] target.seed_db={seed_path}")
    backend = _backend(job)
    print(f"[epc] construct.backend={backend} prior=linear_tr protocol={PROTOCOL_ID}")

    # Hard guard: never open A_tgt_full from job paths
    for p in (job.source_db, seed_path, job.output_db):
        if "A_tgt_full" in Path(p).name:
            print(
                "[epc] ERROR: transfer_ab must not use A_tgt_full as I/O",
                file=sys.stderr,
            )
            return 2

    src = load_source_db(job.source_db)
    b_instances, b_pvts = load_target_lists(job)
    print(f"[epc] B lists: instances={len(b_instances)} pvts={len(b_pvts)}")

    if job.field_keys_policy == "all_from_source":
        field_keys = list(src.field_keys)
    else:
        raise ValueError(f"unsupported field_policy.keys: {job.field_keys_policy}")

    print("[epc] constructing transfer…")
    result = construct_transfer(
        job, b_instances=b_instances, b_pvts=b_pvts, field_keys=field_keys
    )
    expected = len(b_instances) * len(b_pvts) * len(field_keys)
    if len(result.data) != expected:
        print(
            f"[epc] ERROR: constructed {len(result.data)} cells, expected {expected}",
            file=sys.stderr,
        )
        return 2

    # Optional constraints (same fail_job semantics); no AB-hard stamp for transfer
    from ..constraints import apply_constraints, evaluate_gates

    print("[epc] applying constraints (if any)…")
    evals = apply_constraints(job, src, result) if job.constraints else []
    n_fail = sum(1 for e in evals if not e.passed)
    n_pass = sum(1 for e in evals if e.passed)
    print(f"[epc] constraint evals: PASS={n_pass} FAIL={n_fail} total={len(evals)}")
    gates_ok, gates_msg = evaluate_gates(job, evals) if job.constraints else (True, "no constraints")
    print(f"[epc] gates: {'PASS' if gates_ok else 'FAIL'} — {gates_msg}")

    fail_job = (not gates_ok) and job.on_violation == "fail_job"
    if fail_job:
        if job.output_db.is_file():
            job.output_db.unlink()
        write_audit(
            job.audit_path,
            job,
            src,
            b_instances,
            b_pvts,
            result,
            evals,
            0,
            False,
            gates_msg,
            g2_ok=False,
            g2_msg="G2 skipped (gates FAIL, no B.db)",
            g2_results=[],
            ab_hard_audit={
                "status": "SKIP",
                "reason": "transfer_ab: no AB stamp; protocol=" + PROTOCOL_ID,
                "backend": backend,
                "seed_db": str(seed_path),
                "seed_groups": len(load_source_db(seed_path).groups),
            },
        )
        print(f"[epc] audit (FAIL) → {job.audit_path}")
        return 1

    print(f"[epc] writing B.db → {job.output_db}")
    n = write_b_db(job.output_db, result, b_instances, b_pvts)
    print(f"[epc] wrote {n} rows")
    write_audit(
        job.audit_path,
        job,
        src,
        b_instances,
        b_pvts,
        result,
        evals,
        n,
        True,
        gates_msg + f" | transfer backend={backend} protocol={PROTOCOL_ID}",
        g2_ok=True,
        g2_msg="G2 SKIP: transfer_ab (no relative sugar required)",
        g2_results=[],
        ab_hard_audit={
            "status": "SKIP",
            "reason": "transfer_ab: no AB/LON/transfer stamp this round",
            "backend": backend,
            "prior": "linear_tr",
            "protocol": PROTOCOL_ID,
            "seed_db": str(seed_path),
            "seed_groups": len(load_source_db(seed_path).groups),
        },
    )
    print(f"[epc] audit → {job.audit_path}")
    print("[epc] OK")
    return 0
