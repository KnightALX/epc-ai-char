"""Apply user constraints (priority over style) and evaluate gates (P1 G1)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .construct import ConstructResult
from .job import ConstraintSpec, Job
from .source import SourceDB
from .values import format_tokens, parse_tokens

VALID_BASELINE_SOURCES = frozenset({"A_exact", "style_proxy"})


@dataclass
class ConstraintEval:
    index: int
    type: str
    locator: str
    passed: bool
    detail: str
    applied: bool = False
    metrics: dict[str, Any] = field(default_factory=dict)


def _iter_locators(c: ConstraintSpec):
    for inst in c.instances:
        for pvt in c.pvts:
            for key in c.keys:
                yield inst, pvt, key


def _cell_indices(c: ConstraintSpec, n_tokens: int) -> list[int]:
    if c.table_cells == "all_cells" or c.cell == "all_cells":
        return list(range(n_tokens))
    if c.cell == "scalar" or c.table_cells is None and c.cell == "scalar":
        return [0]
    if isinstance(c.table_cells, list):
        idxs = []
        side = int(round(n_tokens**0.5))
        square = side * side == n_tokens
        for item in c.table_cells:
            if isinstance(item, int):
                if item < 0:
                    raise ValueError(f"negative table_cells index: {item}")
                idxs.append(item)
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                if not square:
                    raise ValueError(
                        f"(row,col) cell form needs a square table; "
                        f"got {n_tokens} tokens"
                    )
                r, col = item
                if r < 0 or col < 0 or r >= side or col >= side:
                    raise ValueError(
                        f"cell ({r},{col}) out of range for {side}×{side} table"
                    )
                idxs.append(int(r) * side + int(col))
            else:
                raise ValueError(f"bad table_cells item: {item!r}")
        bad = [j for j in idxs if j < 0 or j >= n_tokens]
        if bad:
            raise ValueError(
                f"table_cells index {bad[0]} out of range for {n_tokens} tokens"
            )
        return idxs
    if c.cell == "scalar":
        return [0]
    raise ValueError(f"unsupported table_cells/cell: {c.table_cells!r}/{c.cell!r}")


def _proxy_ref_summary(result: ConstructResult, inst: str, pvt: str) -> str:
    """Non-empty reference summary for style_proxy audit (G1)."""
    meta = result.meta.get((inst, pvt))
    if meta is None:
        return "style_proxy:pre_constraint_construct"
    notes = (meta.notes or "").strip()
    status = meta.status or ""
    parts = []
    if status:
        parts.append(f"status={status}")
    if notes:
        parts.append(notes)
    if meta.residual_applied:
        parts.append(f"residual={meta.residual_reason or 'yes'}")
    summary = "; ".join(parts) if parts else "style_proxy:pre_constraint_construct"
    return summary


def _source_aligned_baseline(
    source: SourceDB,
    result: ConstructResult,
    inst: str,
    pvt: str,
    key: str,
) -> tuple[list[float], str, str]:
    """Return (tokens, baseline_source, proxy_ref_summary).

    S2=A: A_exact if present, else style_proxy = pre-constraint constructed value.
    """
    a_val = source.get(inst, pvt, key)
    if a_val is not None:
        return parse_tokens(a_val), "A_exact", ""
    b_val = result.data.get((inst, pvt, key))
    if b_val is None:
        raise RuntimeError(f"no baseline for {inst}/{pvt}/{key}")
    ref = _proxy_ref_summary(result, inst, pvt)
    return parse_tokens(b_val), "style_proxy", ref


def _allow_clip(job: Job) -> bool:
    """Clip bounds only when on_violation is not fail_job (e.g. soft_clip)."""
    return job.on_violation != "fail_job"


def apply_constraints(
    job: Job,
    source: SourceDB,
    result: ConstructResult,
) -> list[ConstraintEval]:
    """Apply / verify constraints (constraint > style).

    Under ``on_violation: fail_job`` (sample default), bound constraints only
    *verify* — they do not clip-then-pass. ``relative_delta_vs_source`` still
    sets constrained cells to the forced target baseline×(1+δ/100).
    """
    evals: list[ConstraintEval] = []
    clip = _allow_clip(job)

    for i, c in enumerate(job.constraints):
        if not (c.instances and c.pvts and c.keys):
            raise ValueError(
                f"constraint #{i} ({c.type}): instances/pvts/keys must all be "
                "non-empty; an empty locator would silently skip the constraint"
            )
        if c.type == "table_upper_bound":
            evals.extend(_apply_upper_bound(i, c, result, allow_clip=clip))
        elif c.type == "relative_delta_vs_source":
            evals.extend(_apply_relative_delta(i, c, source, result))
        elif c.type == "value_range":
            evals.extend(_apply_value_range(i, c, result, allow_clip=clip))
        else:
            evals.append(
                ConstraintEval(
                    index=i,
                    type=c.type,
                    locator="(job)",
                    passed=False,
                    detail=f"unsupported constraint type: {c.type}",
                )
            )
    return evals


def _apply_upper_bound(
    index: int,
    c: ConstraintSpec,
    result: ConstructResult,
    *,
    allow_clip: bool,
) -> list[ConstraintEval]:
    target = c.target
    if target.get("mode") not in (None, "range"):
        pass
    op = target.get("op", "<=")
    bound = float(target["value"])
    if op != "<=":
        raise ValueError(f"table_upper_bound only supports <=, got {op}")

    out: list[ConstraintEval] = []
    for inst, pvt, key in _iter_locators(c):
        loc = f"{inst} × {pvt} × {key}"
        raw = result.data.get((inst, pvt, key))
        if raw is None:
            out.append(
                ConstraintEval(
                    index=index,
                    type=c.type,
                    locator=loc,
                    passed=False,
                    detail="missing constructed value",
                )
            )
            continue
        toks = parse_tokens(raw)
        idxs = _cell_indices(c, len(toks))
        before_max = max(toks[j] for j in idxs)
        new_toks = list(toks)
        clipped = 0
        if allow_clip:
            for j in idxs:
                if new_toks[j] > bound:
                    new_toks[j] = bound
                    clipped += 1
            result.data[(inst, pvt, key)] = format_tokens(new_toks)
            after_max = max(new_toks[j] for j in idxs)
            passed = after_max <= bound + 1e-9
            mode = "clip"
        else:
            after_max = before_max
            passed = before_max <= bound + 1e-9
            mode = "verify_only"
        out.append(
            ConstraintEval(
                index=index,
                type=c.type,
                locator=loc,
                passed=passed,
                applied=True,
                detail=(
                    f"op<= {bound}; mode={mode}; before_max={before_max:.6g}; "
                    f"after_max={after_max:.6g}; cells_clipped={clipped}/{len(idxs)}"
                ),
                metrics={
                    "bound": bound,
                    "before_max": before_max,
                    "after_max": after_max,
                    "cells_clipped": clipped,
                    "n_cells": len(idxs),
                    "mode": mode,
                },
            )
        )
    return out


def _apply_relative_delta(
    index: int,
    c: ConstraintSpec,
    source: SourceDB,
    result: ConstructResult,
) -> list[ConstraintEval]:
    target = c.target
    delta_pct = float(target["delta_pct"])
    factor = 1.0 + delta_pct / 100.0
    baseline_mode = target.get("baseline", "source_aligned")
    if baseline_mode != "source_aligned":
        raise ValueError(f"unsupported baseline: {baseline_mode}")

    out: list[ConstraintEval] = []
    for inst, pvt, key in _iter_locators(c):
        loc = f"{inst} × {pvt} × {key}"
        baseline, baseline_source, proxy_ref = _source_aligned_baseline(
            source, result, inst, pvt, key
        )

        # S2: allow_proxy_baseline=false → whole locator FAIL if needs proxy
        if baseline_source == "style_proxy" and not c.allow_proxy_baseline:
            out.append(
                ConstraintEval(
                    index=index,
                    type=c.type,
                    locator=loc,
                    passed=False,
                    applied=False,
                    detail=(
                        "allow_proxy_baseline=false but baseline needs style_proxy "
                        f"(ref={proxy_ref or 'n/a'})"
                    ),
                    metrics={
                        "delta_pct": delta_pct,
                        "factor": factor,
                        "baseline_source": baseline_source,
                        "baseline0": baseline[0] if baseline else None,
                        "proxy_ref": proxy_ref,
                        "allow_proxy_baseline": False,
                        "key_family": c.key_family,
                        "sugar_origin": c.sugar_origin,
                    },
                )
            )
            continue

        idxs = _cell_indices(c, len(baseline))
        desired = [baseline[j] * factor for j in range(len(baseline))]
        new_toks = list(
            parse_tokens(result.data[(inst, pvt, key)])
            if (inst, pvt, key) in result.data
            else list(baseline)
        )
        if len(new_toks) != len(baseline):
            new_toks = list(desired)
        for j in idxs:
            new_toks[j] = desired[j]
        result.data[(inst, pvt, key)] = format_tokens(new_toks)

        max_rel_err = 0.0
        for j in idxs:
            b = baseline[j]
            got = new_toks[j]
            exp = b * factor
            if abs(exp) < 1e-15:
                err = abs(got - exp)
            else:
                err = abs(got / exp - 1.0)
            max_rel_err = max(max_rel_err, err)
        passed = max_rel_err < 1e-6
        out.append(
            ConstraintEval(
                index=index,
                type=c.type,
                locator=loc,
                passed=passed,
                applied=True,
                detail=(
                    f"delta_pct={delta_pct} → ×{factor:.4f}; "
                    f"baseline_source={baseline_source}; "
                    f"max_rel_err={max_rel_err:.3e}; "
                    f"sample baseline0={baseline[0]:.6g} → {new_toks[0]:.6g}"
                    + (f"; proxy_ref={proxy_ref}" if proxy_ref else "")
                ),
                metrics={
                    "delta_pct": delta_pct,
                    "factor": factor,
                    "max_rel_err": max_rel_err,
                    "baseline0": baseline[0],
                    "result0": new_toks[0],
                    "g2_cells": list(idxs),
                    "g2_baselines": [baseline[j] for j in idxs],
                    "baseline_source": baseline_source,
                    "proxy_ref": proxy_ref,
                    "allow_proxy_baseline": c.allow_proxy_baseline,
                    "n_cells": len(idxs),
                    "key_family": c.key_family,
                    "sugar_origin": c.sugar_origin,
                    "instance": inst,
                    "pvt": pvt,
                    "key": key,
                },
            )
        )
    return out


def _apply_value_range(
    index: int,
    c: ConstraintSpec,
    result: ConstructResult,
    *,
    allow_clip: bool,
) -> list[ConstraintEval]:
    target = c.target
    op = str(target.get("op", "<="))
    if op not in ("<=", ">=", "<", ">"):
        raise ValueError(
            f"value_range op={op!r} invalid; must be one of <=, >=, <, >"
        )
    bound = float(target["value"])
    out: list[ConstraintEval] = []
    for inst, pvt, key in _iter_locators(c):
        loc = f"{inst} × {pvt} × {key}"
        raw = result.data.get((inst, pvt, key))
        if raw is None:
            out.append(
                ConstraintEval(
                    index=index, type=c.type, locator=loc, passed=False, detail="missing"
                )
            )
            continue
        toks = parse_tokens(raw)
        idxs = _cell_indices(c, len(toks))
        new_toks = list(toks)
        clipped = 0
        if allow_clip:
            for j in idxs:
                if op == "<=" and new_toks[j] > bound:
                    new_toks[j] = bound
                    clipped += 1
                elif op == ">=" and new_toks[j] < bound:
                    new_toks[j] = bound
                    clipped += 1
                elif op == "<" and new_toks[j] >= bound:
                    # strictly below bound regardless of sign (old bound*(1-eps)
                    # landed on the wrong side for negative bounds)
                    new_toks[j] = math.nextafter(bound, -math.inf)
                    clipped += 1
                elif op == ">" and new_toks[j] <= bound:
                    new_toks[j] = math.nextafter(bound, math.inf)
                    clipped += 1
            result.data[(inst, pvt, key)] = format_tokens(new_toks)
            mode = "clip"
        else:
            mode = "verify_only"
        vals = [new_toks[j] for j in idxs]
        if op == "<=":
            passed = all(v <= bound + 1e-9 for v in vals)
        elif op == ">=":
            passed = all(v >= bound - 1e-9 for v in vals)
        elif op == "<":
            passed = all(v < bound for v in vals)
        elif op == ">":
            passed = all(v > bound for v in vals)
        else:
            passed = True
        out.append(
            ConstraintEval(
                index=index,
                type=c.type,
                locator=loc,
                passed=passed,
                applied=True,
                detail=(
                    f"op{op} {bound}; mode={mode}; "
                    f"max={max(vals):.6g} min={min(vals):.6g}; "
                    f"cells_clipped={clipped}/{len(idxs)}"
                ),
                metrics={
                    "bound": bound,
                    "op": op,
                    "mode": mode,
                    "cells_clipped": clipped,
                },
            )
        )
    return out


def check_g1_auditability(evals: list[ConstraintEval]) -> tuple[bool, str]:
    """G1: every applied relative constraint must have auditable baseline_source."""
    problems = []
    for e in evals:
        if e.type != "relative_delta_vs_source":
            continue
        if not e.applied and not e.passed:
            # fail from allow_proxy — still require baseline_source in metrics
            src = (e.metrics or {}).get("baseline_source")
            if src not in VALID_BASELINE_SOURCES:
                problems.append(f"#{e.index} {e.locator}: missing/illegal baseline_source")
            continue
        if not e.applied:
            continue
        src = (e.metrics or {}).get("baseline_source")
        if src not in VALID_BASELINE_SOURCES:
            problems.append(
                f"#{e.index} {e.locator}: baseline_source={src!r} not in "
                f"{sorted(VALID_BASELINE_SOURCES)}"
            )
            continue
        if src == "style_proxy":
            ref = (e.metrics or {}).get("proxy_ref") or ""
            if not str(ref).strip():
                problems.append(
                    f"#{e.index} {e.locator}: style_proxy missing non-empty proxy_ref"
                )
        if "baseline0" not in (e.metrics or {}):
            problems.append(f"#{e.index} {e.locator}: missing baseline0")
    if problems:
        return False, "G1 FAIL: " + "; ".join(problems[:5])
    return True, "G1 PASS: all relative baselines auditable"


def evaluate_gates(
    job: Job, evals: list[ConstraintEval]
) -> tuple[bool, str]:
    """Return (ok, message). Includes G1 when relative constraints present."""
    parts: list[str] = []
    ok = True

    if job.require_constraint_satisfaction:
        failed = [e for e in evals if not e.passed]
        present = {e.index for e in evals}
        silent = [i for i in range(len(job.constraints)) if i not in present]
        if silent:
            ok = False
            parts.append(
                f"constraints FAIL: #{silent} produced no evaluations "
                "(locator matched nothing)"
            )
        elif failed:
            ok = False
            msg = "; ".join(
                f"#{e.index} {e.type} {e.locator}: {e.detail}" for e in failed[:8]
            )
            parts.append(f"constraints FAIL: {msg}")
        else:
            parts.append("all constraints PASS")
    else:
        parts.append("gates.require_constraint_satisfaction=false")

    # G3 soft check at gate time (hard reject already at load)
    if job.sugar_declared:
        n_rel_evals = sum(
            1
            for e in evals
            if e.type == "relative_delta_vs_source" and e.metrics.get("sugar_origin")
        )
        # One eval per (inst,pvt,key) from sugar-expanded atomics
        if job.expanded_constraint_count <= 0:
            ok = False
            parts.append("G3 FAIL: expanded_constraint_count=0")
        elif n_rel_evals != job.expanded_constraint_count:
            # count of applied+failed sugar-origin evals should match expansion
            ok = False
            parts.append(
                f"G3 FAIL: sugar evals={n_rel_evals} != "
                f"expanded_constraint_count={job.expanded_constraint_count}"
            )
        else:
            parts.append(
                f"G3 PASS: expanded_constraint_count={job.expanded_constraint_count}"
            )

    g1_ok, g1_msg = check_g1_auditability(evals)
    if not g1_ok:
        ok = False
    parts.append(g1_msg)

    return ok, " | ".join(parts)
