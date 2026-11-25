"""Load and validate EPC job YAML (incl. P1 relative_improve sugar expansion)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .defaults import DEFAULT_POWER_KEYS, DEFAULT_SPEED_KEYS
from .paths import portable


@dataclass
class ConstraintSpec:
    type: str
    instances: list[str]
    pvts: list[str]
    keys: list[str]
    table_cells: str | None
    cell: str | None
    target: dict[str, Any]
    raw: dict[str, Any]
    allow_proxy_baseline: bool = True
    sugar_origin: str | None = None  # e.g. "relative_improve_vs_source[i]/speed"
    key_family: str | None = None  # "speed" | "power" | None


@dataclass
class ConstructConfig:
    backend: str = "idw_nn"
    prior: str = "idw_nn"
    model_path: Path | None = None
    fallback: str = "idw_nn"
    apply_on: str = "all_extrapolated"  # all_extrapolated | geom_only
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


SUPPORTED_MODES = (
    "epc_ab",
    "corner_fill_geom",
    "pvt_missing_fill",
    "pvt_sparse_fill",
    "transfer_ab",
)


@dataclass
class Job:
    path: Path
    version: str
    job_name: str
    source_process: str
    source_db: Path
    target_process: str
    instance_list_path: Path
    pvt_list_path: Path
    field_keys_policy: str
    table_axes: list[str]
    style_enabled: bool
    constraints: list[ConstraintSpec]
    output_db: Path
    audit_path: Path
    require_constraint_satisfaction: bool
    on_violation: str
    construct: ConstructConfig = field(default_factory=ConstructConfig)
    expanded_constraint_count: int = 0
    sugar_declared: bool = False
    mode: str = "epc_ab"
    geom_fill: dict[str, Any] | None = None
    missing_fill: dict[str, Any] | None = None
    sparse_fill: dict[str, Any] | None = None
    source_table: str | None = None
    source_col_map: dict[str, str] | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


REQUIRED_ATOMIC_FIELDS = ("type", "instances", "pvts", "keys", "target")


def _require(d: dict, *keys: str, ctx: str) -> None:
    missing = [k for k in keys if k not in d]
    if missing:
        raise ValueError(f"{ctx}: missing keys {missing}")


def _parse_construct(raw: dict, base: Path, resolve) -> ConstructConfig:
    c = raw.get("construct") or {}
    if not isinstance(c, dict):
        c = {}
    backend = str(c.get("backend", "idw_nn")).strip()
    nested_gbdt = (
        c.get("residual_gbdt") if isinstance(c.get("residual_gbdt"), dict) else {}
    )
    nested_tl = c.get("residual_tl") if isinstance(c.get("residual_tl"), dict) else {}
    nested_ltr = c.get("linear_tr") if isinstance(c.get("linear_tr"), dict) else {}
    if backend in ("residual_tl", "linear_tr"):
        nested = nested_tl or nested_ltr or {}
        prior = str(nested.get("prior") or c.get("prior") or "linear_tr").strip()
        fallback = str(
            nested.get("fallback") or c.get("fallback") or "linear_tr"
        ).strip()
        apply_on = str(
            nested.get("apply_on") or c.get("apply_on") or "transfer_seed_fit"
        ).strip()
        mp = nested.get("model_path") or c.get("model_path")
    else:
        nested = nested_gbdt
        prior = str(nested.get("prior") or c.get("prior") or "idw_nn").strip()
        fallback = str(nested.get("fallback") or c.get("fallback") or "idw_nn").strip()
        apply_on = str(
            nested.get("apply_on") or c.get("apply_on") or "all_extrapolated"
        ).strip()
        if apply_on not in ("all_extrapolated", "geom_only"):
            raise ValueError(
                f"construct.residual_gbdt.apply_on={apply_on!r}; "
                "expected all_extrapolated|geom_only"
            )
        mp = nested.get("model_path") or c.get("model_path")
    model_path = resolve(mp) if mp else None
    return ConstructConfig(
        backend=backend,
        prior=prior,
        model_path=model_path,
        fallback=fallback,
        apply_on=apply_on,
        raw=c,
    )


def _has_table_or_scalar(c: dict) -> bool:
    if "table_cells" in c:
        return True
    if c.get("cell") is not None:
        return True
    if c.get("scalar"):
        return True
    return False


def _atomic_from_dict(
    c: dict,
    *,
    allow_proxy_baseline: bool = True,
    sugar_origin: str | None = None,
    key_family: str | None = None,
) -> ConstraintSpec:
    return ConstraintSpec(
        type=c["type"],
        instances=list(c["instances"]),
        pvts=list(c["pvts"]),
        keys=list(c["keys"]),
        table_cells=c.get("table_cells"),
        cell=c.get("cell") or ("scalar" if c.get("scalar") else None),
        target=dict(c["target"]),
        raw=c,
        allow_proxy_baseline=allow_proxy_baseline,
        sugar_origin=sugar_origin,
        key_family=key_family,
    )


def _expand_relative_improve(c: dict, ctx: str) -> tuple[list[ConstraintSpec], int]:
    """Expand sugar → atomic relative_delta_vs_source; return (specs, expected_count)."""
    instances = c.get("instances")
    pvts = c.get("pvts")
    if not instances or not isinstance(instances, list) or len(instances) == 0:
        raise ValueError(
            f"{ctx}: relative_improve_vs_source rejected (missing/empty instances); "
            "vague PPA not allowed"
        )
    if not pvts or not isinstance(pvts, list) or len(pvts) == 0:
        raise ValueError(
            f"{ctx}: relative_improve_vs_source rejected (missing/empty pvts); "
            "vague PPA not allowed"
        )
    if not _has_table_or_scalar(c):
        raise ValueError(
            f"{ctx}: relative_improve_vs_source rejected "
            "(need table_cells or cell/scalar); vague PPA not allowed"
        )

    speed_pct = c.get("speed_improve_pct")
    power_pct = c.get("power_improve_pct")
    has_speed = speed_pct is not None and float(speed_pct) != 0.0
    has_power = power_pct is not None and float(power_pct) != 0.0
    if not has_speed and not has_power:
        raise ValueError(
            f"{ctx}: relative_improve_vs_source rejected "
            "(speed_improve_pct and power_improve_pct both missing/0)"
        )

    speed_keys = list(c.get("speed_keys") or DEFAULT_SPEED_KEYS)
    power_keys = list(c.get("power_keys") or DEFAULT_POWER_KEYS)
    overlap = set(speed_keys) & set(power_keys)
    if overlap:
        raise ValueError(
            f"{ctx}: speed_keys ∩ power_keys non-empty → reject: {sorted(overlap)}"
        )

    allow_proxy = bool(c.get("allow_proxy_baseline", True))
    baseline = c.get("baseline", "source_aligned")
    table_cells = c.get("table_cells")
    cell = c.get("cell") or ("scalar" if c.get("scalar") else None)

    expanded: list[ConstraintSpec] = []
    expected = 0
    n_inst, n_pvt = len(instances), len(pvts)

    if has_speed:
        expected += n_inst * n_pvt * len(speed_keys)
        for key in speed_keys:
            atomic = {
                "type": "relative_delta_vs_source",
                "instances": list(instances),
                "pvts": list(pvts),
                "keys": [key],
                "target": {
                    "mode": "delta_pct",
                    "delta_pct": -float(speed_pct),
                    "baseline": baseline,
                },
            }
            if table_cells is not None:
                atomic["table_cells"] = table_cells
            if cell is not None:
                atomic["cell"] = cell
            if c.get("scalar"):
                atomic["scalar"] = c["scalar"]
            expanded.append(
                _atomic_from_dict(
                    atomic,
                    allow_proxy_baseline=allow_proxy,
                    sugar_origin=f"{ctx}:speed",
                    key_family="speed",
                )
            )

    if has_power:
        expected += n_inst * n_pvt * len(power_keys)
        for key in power_keys:
            atomic = {
                "type": "relative_delta_vs_source",
                "instances": list(instances),
                "pvts": list(pvts),
                "keys": [key],
                "target": {
                    "mode": "delta_pct",
                    "delta_pct": -float(power_pct),
                    "baseline": baseline,
                },
            }
            if table_cells is not None:
                atomic["table_cells"] = table_cells
            if cell is not None:
                atomic["cell"] = cell
            if c.get("scalar"):
                atomic["scalar"] = c["scalar"]
            expanded.append(
                _atomic_from_dict(
                    atomic,
                    allow_proxy_baseline=allow_proxy,
                    sugar_origin=f"{ctx}:power",
                    key_family="power",
                )
            )

    if expected == 0:
        raise ValueError(f"{ctx}: expanded_constraint_count=0 (G3)")
    return expanded, expected


def _relative_locator_keys(spec: ConstraintSpec) -> list[tuple[str, str, str]]:
    out = []
    for inst in spec.instances:
        for pvt in spec.pvts:
            for key in spec.keys:
                out.append((inst, pvt, key))
    return out


def _check_relative_conflicts(constraints: list[ConstraintSpec]) -> None:
    """Same (inst,pvt,key) under multiple relative_delta → reject load."""
    seen: dict[tuple[str, str, str], int] = {}
    for i, c in enumerate(constraints):
        if c.type != "relative_delta_vs_source":
            continue
        for loc in _relative_locator_keys(c):
            if loc in seen:
                raise ValueError(
                    f"conflicting relative constraints on locator "
                    f"{loc[0]}×{loc[1]}×{loc[2]} "
                    f"(constraints[{seen[loc]}] vs [{i}]) — reject"
                )
            seen[loc] = i


def resolve_mode(raw: dict, mode_override: str | None = None) -> str:
    """Resolve mode from CLI override / YAML mode / YAML operator; conflict → reject."""
    yaml_mode = raw.get("mode")
    yaml_op = raw.get("operator")
    if yaml_mode is not None:
        yaml_mode = str(yaml_mode).strip()
    if yaml_op is not None:
        yaml_op = str(yaml_op).strip()
    if yaml_mode and yaml_op and yaml_mode != yaml_op:
        raise ValueError(
            f"mode/operator conflict: mode={yaml_mode!r} operator={yaml_op!r} — reject"
        )
    chosen = mode_override or yaml_mode or yaml_op or "epc_ab"
    chosen = str(chosen).strip()
    if chosen not in SUPPORTED_MODES:
        raise ValueError(f"unknown mode={chosen!r}; supported={SUPPORTED_MODES}")
    return chosen


def load_job(path: str | Path, mode_override: str | None = None) -> Job:
    path = Path(path).resolve()
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError("job YAML root must be a mapping")

    mode = resolve_mode(raw, mode_override)

    _require(raw, "source", "output", ctx="job")
    src = raw["source"]
    _require(src, "db_path", ctx="source")
    out = raw["output"]
    _require(out, "db_path", "audit_report_path", ctx="output")
    gates = raw.get("gates") or {}
    fp = raw.get("field_policy") or {"keys": "all_from_source", "table_axes": ["tran_index", "load_index"]}

    tgt = raw.get("target") or {}
    if mode in ("epc_ab", "transfer_ab"):
        _require(raw, "target", "field_policy", "gates", ctx="job")
        tgt = raw["target"]
        _require(src, "process", "db_path", ctx="source")
        _require(tgt, "process", ctx="target")
        if "instance_list_path" not in tgt and "instances" not in tgt:
            raise ValueError("target: need instance_list_path or instances")
        if "pvt_list_path" not in tgt and "pvts" not in tgt:
            raise ValueError("target: need pvt_list_path or pvts")
        if mode == "transfer_ab":
            if "seed_db" not in tgt and "seed_db_path" not in tgt:
                raise ValueError("transfer_ab target: need seed_db")
        gates = raw["gates"]
        fp = raw["field_policy"]
    else:
        # P2 modes: process labels optional
        if "process" not in src:
            src = {**src, "process": "DEMO_A"}
        if "process" not in tgt:
            tgt = {**tgt, "process": src.get("process", "DEMO_A")}

    constraints: list[ConstraintSpec] = []
    expanded_count = 0
    sugar_declared = False

    for i, c in enumerate(raw.get("constraints") or []):
        ctx = f"constraints[{i}]"
        if not isinstance(c, dict) or "type" not in c:
            raise ValueError(f"{ctx}: need type")
        ctype = c["type"]

        if ctype == "relative_improve_vs_source":
            sugar_declared = True
            specs, n_exp = _expand_relative_improve(c, ctx)
            constraints.extend(specs)
            expanded_count += n_exp
            continue

        # Atomic constraints
        _require(c, *REQUIRED_ATOMIC_FIELDS, ctx=ctx)
        if not _has_table_or_scalar(c):
            raise ValueError(f"{ctx}: need table_cells or cell/scalar")
        allow_proxy = bool(c.get("allow_proxy_baseline", True))
        # Nested target may also carry the flag
        if "allow_proxy_baseline" in (c.get("target") or {}):
            allow_proxy = bool(c["target"]["allow_proxy_baseline"])
        constraints.append(
            _atomic_from_dict(c, allow_proxy_baseline=allow_proxy)
        )

    _check_relative_conflicts(constraints)

    if sugar_declared and expanded_count == 0:
        raise ValueError("G3: sugar declared but expanded_constraint_count=0")

    style = raw.get("style_from_source") or {}
    base = path.parent

    def resolve(p: str | Path) -> Path:
        pp = portable(p)
        return pp if pp.is_absolute() else (base / pp).resolve()

    inst_path = (
        resolve(tgt["instance_list_path"])
        if "instance_list_path" in tgt
        else None
    )
    pvt_path = resolve(tgt["pvt_list_path"]) if "pvt_list_path" in tgt else None

    if mode == "corner_fill_geom":
        gf = raw.get("geom_fill")
        if not isinstance(gf, dict) or "target_instances" not in gf:
            raise ValueError("corner_fill_geom: need geom_fill.target_instances")
    if mode == "pvt_missing_fill":
        if not isinstance(raw.get("missing_fill"), dict):
            # allow empty missing_fill defaults
            raw.setdefault("missing_fill", {})
    if mode == "pvt_sparse_fill":
        sf = raw.get("sparse_fill")
        if not isinstance(sf, dict):
            raise ValueError("pvt_sparse_fill: need sparse_fill: section")

    _onv = str(gates.get("on_violation", "fail_job")).strip()
    if _onv not in ("fail_job", "soft_clip"):
        raise ValueError(
            f"gates.on_violation={_onv!r} invalid; must be fail_job or soft_clip "
            "(whitespace/case typos are rejected, not silently clipped)"
        )
    return Job(
        path=path,
        version=str(raw.get("version", "")),
        job_name=str(raw.get("job_name", path.stem)),
        source_process=str(src.get("process", "DEMO_A")),
        source_db=resolve(src["db_path"]),
        target_process=str(tgt.get("process", src.get("process", "DEMO_A"))),
        instance_list_path=inst_path or Path(""),
        pvt_list_path=pvt_path or Path(""),
        field_keys_policy=str(fp.get("keys", "all_from_source")),
        table_axes=list(fp.get("table_axes") or ["tran_index", "load_index"]),
        style_enabled=bool(style.get("enabled", True)),
        constraints=constraints,
        output_db=resolve(out["db_path"]),
        audit_path=resolve(out["audit_report_path"]),
        require_constraint_satisfaction=bool(
            gates.get("require_constraint_satisfaction", True)
        ),
        on_violation=_onv,
        construct=_parse_construct(raw, base, resolve),
        expanded_constraint_count=expanded_count,
        sugar_declared=sugar_declared,
        mode=mode,
        geom_fill=raw.get("geom_fill") if isinstance(raw.get("geom_fill"), dict) else None,
        missing_fill=raw.get("missing_fill") if isinstance(raw.get("missing_fill"), dict) else None,
        sparse_fill=raw.get("sparse_fill") if isinstance(raw.get("sparse_fill"), dict) else None,
        source_table=src.get("table") if isinstance(src.get("table"), str) else None,
        source_col_map=src.get("col_map") if isinstance(src.get("col_map"), dict) else None,
        raw=raw,
    )


def read_list_file(path: Path) -> list[str]:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            lines.append(s)
    return lines


def load_target_lists(job: Job) -> tuple[list[str], list[str]]:
    raw = job.raw["target"]
    if job.instance_list_path and job.instance_list_path.exists():
        instances = read_list_file(job.instance_list_path)
    else:
        instances = list(raw["instances"])
    if job.pvt_list_path and job.pvt_list_path.exists():
        pvts = read_list_file(job.pvt_list_path)
    else:
        pvts = list(raw["pvts"])
    if not instances or not pvts:
        raise ValueError("empty instance or pvt list")
    return instances, pvts
