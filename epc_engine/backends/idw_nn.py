"""Baseline construct: geometry IDW (k=4,p=2) + PVT NN + optional V/T/corner scale."""
from __future__ import annotations

from ..construct_types import AXIS_KEYS, CellMeta, ConstructResult
from ..parse import (
    InstanceParts,
    PvtParts,
    geom_distance,
    parse_instance,
    parse_pvt,
    pvt_distance,
)
from ..source import SourceDB
from ..values import format_tokens, parse_tokens


def nearest_pvt(target: PvtParts, source: SourceDB) -> str:
    best_name = source.pvts[0]
    best_d = float("inf")
    for name, parts in source.pvt_parts.items():
        d = pvt_distance(target, parts)
        if d < best_d:
            best_d = d
            best_name = name
    return best_name


def idw_weights(
    target: InstanceParts,
    candidates: list[tuple[str, InstanceParts]],
    k: int = 4,
    power: float = 2.0,
) -> list[tuple[str, float]]:
    scored = []
    for name, parts in candidates:
        d = geom_distance(target, parts)
        scored.append((name, d))
    scored.sort(key=lambda x: x[1])
    nearest = scored[: max(1, min(k, len(scored)))]
    if nearest[0][1] < 1e-12:
        return [(nearest[0][0], 1.0)]
    weights = []
    for name, d in nearest:
        weights.append((name, 1.0 / (d**power)))
    s = sum(w for _, w in weights)
    return [(n, w / s) for n, w in weights]


def blend_token_lists(
    samples: list[tuple[float, list[float]]],
) -> list[float]:
    if not samples:
        raise ValueError("no samples to blend")
    n = len(samples[0][1])
    out = [0.0] * n
    wsum = 0.0
    for w, toks in samples:
        if len(toks) != n:
            raise ValueError("token length mismatch in blend")
        wsum += w
        for i, t in enumerate(toks):
            out[i] += w * t
    if wsum <= 0:
        raise ValueError("zero weight sum")
    return [x / wsum for x in out]


def lookup_or_idw(
    source: SourceDB,
    inst: str,
    inst_parts: InstanceParts,
    pvt_name: str,
    key: str,
    exclude_instances: set[str] | None = None,
) -> str:
    """Geometry IDW at pvt_name; optional exclude set (leave-one training)."""
    exclude = exclude_instances or set()
    if inst not in exclude:
        exact = source.get(inst, pvt_name, key)
        if exact is not None:
            return exact

    candidates = [
        (name, parts)
        for name, parts in source.inst_parts.items()
        if name not in exclude and (name, pvt_name) in source.groups
    ]
    if not candidates:
        raise RuntimeError(
            f"no A candidates for pvt={pvt_name} (exclude={sorted(exclude)[:3]}…)"
        )

    weights = idw_weights(inst_parts, candidates)
    samples: list[tuple[float, list[float]]] = []
    for name, w in weights:
        val = source.get(name, pvt_name, key)
        if val is None:
            continue
        samples.append((w, parse_tokens(val)))
    if not samples:
        raise RuntimeError(f"no values for key={key} at pvt={pvt_name}")
    wsum = sum(w for w, _ in samples)
    samples = [(w / wsum, t) for w, t in samples]
    blended = blend_token_lists(samples)
    return format_tokens(blended)


def optional_pvt_scale(
    source: SourceDB,
    value: str,
    key: str,
    target_pvt: PvtParts,
    nn_pvt_name: str,
) -> str:
    nn = source.pvt_parts[nn_pvt_name]
    delay_keys = {
        "tselr1_min_period",
        "tcq",
        "tselw1_min_period",
        "tcd",
        "taccess",
        "tpd_clk_q",
        "taddr_setup",
        "taddr_hold",
        "twen_setup",
        "twen_hold",
        "tcen_setup",
        "tcen_hold",
        "tdata_setup",
        "tdata_hold",
        "setup_time_a_scalar",
        "hold_time_a_scalar",
        "clk_to_q_scalar",
        "min_pulse_width_clk",
        "min_period_scalar",
        "search_latency_scalar",
        "slew_out_est",
        "temp_coeff_delay",
    }
    power_keys = {
        "leakage_vddc",
        "leakage_vddp",
        "retention_leakage",
        "write_power_vddc",
        "write_power_vddp",
        "read_power_vddc",
        "read_power_vddp",
        "standby_power_vddc",
        "search_power_vddc",
        "dynamic_energy_read",
        "dynamic_energy_write",
        "dynamic_energy_search",
    }

    def delay_factor(p: PvtParts) -> float:
        if p.corner.upper().startswith("SS"):
            c = 1.35
        elif p.corner.upper().startswith("FF"):
            c = 0.78
        else:
            c = 1.0
        v_ref = 0.80
        delay_v = (v_ref / max(p.vdd, 0.5)) ** 1.35
        delay_t = 1.0 + 0.0018 * (p.temp - 25.0)
        return c * delay_v * delay_t

    def power_factor(p: PvtParts) -> float:
        if p.corner.upper().startswith("FF"):
            pc = 1.12
        elif p.corner.upper().startswith("SS"):
            pc = 0.92
        else:
            pc = 1.0
        v_ref = 0.80
        return pc * (p.vdd / v_ref) ** 2.0 * (1.0 + 0.0025 * (p.temp - 25.0))

    if key in delay_keys:
        f = delay_factor(target_pvt) / max(delay_factor(nn), 1e-12)
    elif key in power_keys:
        f = power_factor(target_pvt) / max(power_factor(nn), 1e-12)
    else:
        return value

    toks = parse_tokens(value)
    return format_tokens([t * f for t in toks])


def prior_tokens_for_group(
    source: SourceDB,
    b_inst: str,
    b_pvt: str,
    key: str,
    exclude_instances: set[str] | None = None,
) -> list[float]:
    """Compute IDW+NN prior tokens for one (inst,pvt,key); never exact-copies excluded inst."""
    exclude = set(exclude_instances or set())
    b_ip = parse_instance(b_inst)
    b_pp = parse_pvt(b_pvt)
    a_inst_set = set(source.instances) - exclude
    a_pvt_set = set(source.pvts)

    in_a_inst = b_inst in a_inst_set
    in_a_pvt = b_pvt in a_pvt_set

    if (
        in_a_inst
        and in_a_pvt
        and source.has_group(b_inst, b_pvt)
        and b_inst not in exclude
    ):
        val = source.get(b_inst, b_pvt, key)
        if val is None:
            raise RuntimeError(f"missing A cell {b_inst}/{b_pvt}/{key}")
        return parse_tokens(val)

    if in_a_inst and not in_a_pvt:
        pvt_for_style = nearest_pvt(b_pp, source)
        val = lookup_or_idw(
            source, b_inst, b_ip, pvt_for_style, key, exclude_instances=exclude
        )
        val = optional_pvt_scale(source, val, key, b_pp, pvt_for_style)
        return parse_tokens(val)

    if not in_a_inst and in_a_pvt:
        pvt_for_style = b_pvt
        val = lookup_or_idw(
            source, b_inst, b_ip, pvt_for_style, key, exclude_instances=exclude
        )
        return parse_tokens(val)

    # both new (or inst excluded so treated as new geom)
    pvt_for_style = nearest_pvt(b_pp, source) if not in_a_pvt else b_pvt
    val = lookup_or_idw(
        source, b_inst, b_ip, pvt_for_style, key, exclude_instances=exclude
    )
    if not in_a_pvt:
        val = optional_pvt_scale(source, val, key, b_pp, pvt_for_style)
    return parse_tokens(val)


def construct(
    source: SourceDB,
    b_instances: list[str],
    b_pvts: list[str],
    field_keys: list[str],
) -> ConstructResult:
    sample_group = next(iter(source.groups.values()))
    tran = sample_group.get("tran_index")
    load = sample_group.get("load_index")
    if not tran or not load:
        raise RuntimeError("source missing tran_index/load_index")
    n = len(tran.split())
    if n != len(load.split()):
        raise RuntimeError("source axis length mismatch")

    result = ConstructResult(field_keys=list(field_keys), n=n)
    a_inst_set = set(source.instances)
    a_pvt_set = set(source.pvts)

    for b_inst in b_instances:
        b_ip = parse_instance(b_inst)
        in_a_inst = b_inst in a_inst_set
        for b_pvt in b_pvts:
            b_pp = parse_pvt(b_pvt)
            in_a_pvt = b_pvt in a_pvt_set

            if in_a_inst and in_a_pvt and source.has_group(b_inst, b_pvt):
                status = "seed_from_A"
                extrapolated = False
                notes = "exact (instance,pvt) in A"
                pvt_for_style = b_pvt
            elif in_a_inst and not in_a_pvt:
                status = "pvt_extrapolated"
                extrapolated = True
                pvt_for_style = nearest_pvt(b_pp, source)
                notes = f"pvt∉A; NN={pvt_for_style}"
            elif not in_a_inst and in_a_pvt:
                status = "config_extrapolated"
                extrapolated = True
                pvt_for_style = b_pvt
                notes = "instance∉A; geometry IDW at target pvt"
            else:
                status = "config_extrapolated"
                extrapolated = True
                pvt_for_style = nearest_pvt(b_pp, source)
                notes = f"instance∉A and pvt∉A; geom IDW @ NN pvt={pvt_for_style}"

            result.meta[(b_inst, b_pvt)] = CellMeta(
                status=status, extrapolated=extrapolated, notes=notes
            )

            for key in field_keys:
                if key in AXIS_KEYS:
                    result.data[(b_inst, b_pvt, key)] = sample_group[key]
                    continue

                if status == "seed_from_A":
                    val = source.get(b_inst, b_pvt, key)
                    if val is None:
                        raise RuntimeError(
                            f"missing A cell {b_inst}/{b_pvt}/{key}"
                        )
                else:
                    val = lookup_or_idw(
                        source, b_inst, b_ip, pvt_for_style, key
                    )
                    if not in_a_pvt:
                        val = optional_pvt_scale(
                            source, val, key, b_pp, pvt_for_style
                        )
                result.data[(b_inst, b_pvt, key)] = val

    return result
