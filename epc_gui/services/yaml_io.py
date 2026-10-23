"""Load / save EPC job YAML (no engine side effects)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from epc_gui.paths import fixtures_root

MODES = (
    "epc_ab",
    "corner_fill_geom",
    "pvt_missing_fill",
    "pvt_sparse_fill",
)


def _fixture_shortcuts() -> dict[str, Path]:
    root = fixtures_root()
    return {
        "sample": root / "epc_job.sample.yaml",
        "p1_green": root / "p1" / "epc_job.p1_improve_green.yaml",
        "p2_geom_green": root / "p2" / "job_corner_fill_green.yaml",
        "p2_geom_residual_h3hard_red": root / "p2" / "job_corner_fill_residual_h3hard.yaml",
    }


# Lazy-friendly alias used by callers that index FIXTURE_SHORTCUTS
class _FixtureMap(dict):
    def __getitem__(self, key):
        return _fixture_shortcuts()[key]

    def get(self, key, default=None):
        return _fixture_shortcuts().get(key, default)

    def items(self):
        return _fixture_shortcuts().items()

    def keys(self):
        return _fixture_shortcuts().keys()

    def values(self):
        return _fixture_shortcuts().values()

    def __contains__(self, key):
        return key in _fixture_shortcuts()

    def __iter__(self):
        return iter(_fixture_shortcuts())


FIXTURE_SHORTCUTS = _FixtureMap()


def load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {p}")
    return data


def save_yaml(path: str | Path, data: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def dump_yaml_text(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def load_yaml_text(text: str) -> dict[str, Any]:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return data


def effective_mode(data: dict[str, Any]) -> str:
    mode = data.get("mode") or data.get("operator") or "epc_ab"
    return str(mode)


def mode_conflict_message(data: dict[str, Any]) -> str | None:
    """Named hard check when mode and operator disagree (R2 optional)."""
    m, o = data.get("mode"), data.get("operator")
    if m is not None and o is not None and str(m) != str(o):
        return f"mode/operator conflict: mode={m!r} operator={o!r}"
    return None
