"""Rectangle-corner seed resolution for Op-Geom."""
from __future__ import annotations

from ..parse import InstanceParts, parse_instance
from ..source import SourceDB


def assert_same_family_options(names: list[str], *, ctx: str) -> None:
    if not names:
        raise ValueError(f"{ctx}: empty instance list")
    parts = [parse_instance(n) for n in names]
    fam = {(p.family, p.options) for p in parts}
    if len(fam) > 1:
        raise ValueError(
            f"{ctx}: DEMO forbids mixed family/options; got {sorted(fam)}"
        )


def rectangle_corners(pool: list[str]) -> list[str]:
    """Pick 4 instances at (d_min,w_min),(d_min,w_max),(d_max,w_min),(d_max,w_max)."""
    assert_same_family_options(pool, ctx="corner_pool")
    parts = [(n, parse_instance(n)) for n in pool]
    depths = {p.depth for _, p in parts}
    widths = {p.width for _, p in parts}
    dmin, dmax = min(depths), max(depths)
    wmin, wmax = min(widths), max(widths)
    want = {(dmin, wmin), (dmin, wmax), (dmax, wmin), (dmax, wmax)}
    by_xy: dict[tuple[int, int], str] = {}
    for n, p in parts:
        xy = (p.depth, p.width)
        if xy in want and xy not in by_xy:
            by_xy[xy] = n
    missing = want - set(by_xy)
    if missing:
        raise ValueError(
            f"corner_pool: cannot find rectangle corners for {sorted(missing)}"
        )
    # Stable order: (dmin,wmin), (dmin,wmax), (dmax,wmin), (dmax,wmax)
    order = [(dmin, wmin), (dmin, wmax), (dmax, wmin), (dmax, wmax)]
    return [by_xy[xy] for xy in order]


def corner_xy_set(seeds: list[str]) -> set[tuple[int, int]]:
    return {(parse_instance(n).depth, parse_instance(n).width) for n in seeds}


def required_corner_xy(pool_or_seeds: list[str]) -> set[tuple[int, int]]:
    parts = [parse_instance(n) for n in pool_or_seeds]
    depths = {p.depth for p in parts}
    widths = {p.width for p in parts}
    dmin, dmax = min(depths), max(depths)
    wmin, wmax = min(widths), max(widths)
    return {(dmin, wmin), (dmin, wmax), (dmax, wmin), (dmax, wmax)}


def check_seed_covers_corners(
    seeds: list[str],
    pool: list[str],
    *,
    require: bool = True,
) -> None:
    """Explicit seeds must cover the rectangle corners of the seed/pool hull."""
    if not require:
        return
    # Hull from seeds ∪ pool (prefer pool if given for intended rectangle)
    hull = list(dict.fromkeys(list(pool) + list(seeds)))
    assert_same_family_options(hull, ctx="seed_corner_check")
    need = required_corner_xy(hull if pool else seeds)
    have = corner_xy_set(seeds)
    missing = need - have
    if missing:
        raise ValueError(
            f"seed_instances missing rectangle corner coverage: {sorted(missing)} "
            f"(have={sorted(have)}) — FAIL"
        )


def resolve_seeds_and_targets(
    source: SourceDB,
    *,
    seed_instances: list[str] | None,
    target_instances: list[str],
    seed_pool: list[str] | None = None,
    require_corner_coverage: bool = True,
) -> tuple[list[str], list[str]]:
    pool = list(seed_pool) if seed_pool else list(source.instances)
    if seed_instances:
        seeds = list(seed_instances)
        check_seed_covers_corners(
            seeds, pool, require=require_corner_coverage
        )
    else:
        seeds = rectangle_corners(pool)

    targets = [t for t in target_instances if t not in set(seeds)]
    if not targets:
        raise ValueError("corner_fill_geom: no non-seed target_instances")

    all_names = list(dict.fromkeys(seeds + targets))
    assert_same_family_options(all_names, ctx="corner_fill_geom")
    # Targets must exist? Op-Geom can invent new geom — but DEMO targets usually in A.
    # Allow targets not in source (extrapolate); seeds must be in source.
    for s in seeds:
        if s not in source.instances:
            raise ValueError(f"seed instance not in source.db: {s}")
    return seeds, targets
