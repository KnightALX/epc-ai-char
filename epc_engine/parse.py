"""Instance and PVT parsers (T1 v1.1)."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

INSTANCE_RE = re.compile(
    r"^(?P<vendor>HI)(?P<process>NP3)(?P<family>[A-Z]+?)"
    r"(?P<depth>\d+)X(?P<width>\d+)(?:M(?P<mux>\d+))?(?P<options>[A-Z0-9]+)$"
)

VOLT_RE = re.compile(r"^(\d+)P(\d+)V$", re.I)
TEMP_RE = re.compile(r"^(M)?(\d+)C$", re.I)

CORNER_RANK = {
    "SSGNP": 0.0,
    "SS": 0.0,
    "TT": 1.0,
    "FFGNP": 2.0,
    "FF": 2.0,
}


@dataclass(frozen=True)
class InstanceParts:
    vendor: str
    process: str
    family: str
    depth: int
    width: int
    mux: int | None
    options: str
    name: str

    @property
    def xy(self) -> tuple[float, float]:
        return (math.log2(self.depth), math.log2(self.width))


@dataclass(frozen=True)
class PvtParts:
    corner: str
    vdd: float
    vddp: float
    temp: float
    name: str

    @property
    def corner_rank(self) -> float:
        for k, v in CORNER_RANK.items():
            if self.corner.upper().startswith(k):
                return v
        return 1.0


def parse_instance(name: str) -> InstanceParts:
    m = INSTANCE_RE.match(name.strip())
    if not m:
        raise ValueError(f"instance parse failed: {name!r}")
    mux = m.group("mux")
    return InstanceParts(
        vendor=m.group("vendor"),
        process=m.group("process"),
        family=m.group("family"),
        depth=int(m.group("depth")),
        width=int(m.group("width")),
        mux=int(mux) if mux else None,
        options=m.group("options"),
        name=name.strip(),
    )


def parse_volt(tok: str) -> float:
    m = VOLT_RE.match(tok.strip())
    if not m:
        raise ValueError(f"voltage parse failed: {tok!r}")
    return float(f"{m.group(1)}.{m.group(2)}")


def parse_temp(tok: str) -> float:
    m = TEMP_RE.match(tok.strip())
    if not m:
        raise ValueError(f"temp parse failed: {tok!r}")
    val = float(m.group(2))
    return -val if m.group(1) else val


def parse_pvt(name: str) -> PvtParts:
    parts = name.strip().split("_")
    if len(parts) != 4:
        raise ValueError(f"pvt parse failed (need 4 tokens): {name!r}")
    return PvtParts(
        corner=parts[0],
        vdd=parse_volt(parts[1]),
        vddp=parse_volt(parts[2]),
        temp=parse_temp(parts[3]),
        name=name.strip(),
    )


def geom_distance(a: InstanceParts, b: InstanceParts) -> float:
    ax, ay = a.xy
    bx, by = b.xy
    return math.hypot(ax - bx, ay - by)


def pvt_distance(a: PvtParts, b: PvtParts) -> float:
    """Weighted distance: same-corner preferred, then V/T."""
    dc = abs(a.corner_rank - b.corner_rank) * 3.0
    if a.corner.upper() != b.corner.upper():
        dc += 0.5
    dv = abs(a.vdd - b.vdd) / 0.1  # ~0.1 V unit
    dt = abs(a.temp - b.temp) / 40.0  # ~40 C unit
    return math.sqrt(dc * dc + dv * dv + dt * dt)
