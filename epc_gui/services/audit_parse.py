"""Parse engine audit.md → status lights. NEVER re-evaluate gates."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GateLight:
    name: str
    status: str  # PASS | FAIL | SKIP | 未知 | n/a
    detail: str = ""


@dataclass
class AuditSummary:
    path: str
    overall: str  # PASS | FAIL | 未知
    gates_ok: str  # True | False | 未知
    exit_hint: str = ""
    mode: str = ""
    backend: str = ""
    rows_written: str = ""
    db_written: str = ""  # yes | no | 未知
    gates: list[GateLight] = field(default_factory=list)
    snippet: str = ""
    parse_ok: bool = False
    raw_gates_line: str = ""
    has_unknown_gate: bool = False
    display_overall: str = ""  # mutes green when a present gate stays 未知


_TITLE_RE = re.compile(
    r"^#\s+EPC Audit Report\s+[—\-]\s+.+?\s+[—\-]\s+\*\*(PASS|FAIL)\*\*",
    re.M,
)
_GATES_OK_RE = re.compile(r"\*\*gates_ok:\s*`?(True|False)`?\*\*", re.I)
_RESULT_RE = re.compile(r"Result:\s*\*\*(PASS|FAIL)\*\*", re.I)
_MODE_RE = re.compile(r"\*\*mode\s*/\s*operator\*\*:\s*`([^`]+)`", re.I)
_BACKEND_RE = re.compile(r"\*\*construct\.backend\*\*:\s*`([^`]+)`", re.I)
_ROWS_RE = re.compile(r"rows written\s*\|\s*\*\*(\d+)\*\*", re.I)
_DB_WRITTEN_RE = re.compile(r"B\.db written:\s*\*\*([^*]+)\*\*", re.I)

_G3_COUNT_RE = re.compile(
    r"\*\*G3 expanded_constraint_count\*\*:\s*`?(\d+)`?\s*"
    r"\(sugar_declared=(True|False)\)",
    re.I,
)
_G1_MIX_RE = re.compile(
    r"\*\*G1 baseline mix\*\*:\s*A_exact=(\d+),\s*style_proxy=(\d+),\s*relative_evals=(\d+)",
    re.I,
)
_G2_SPOT_RE = re.compile(r"\*\*G2 spot-check\*\*:\s*(PASS|FAIL)\b", re.I)


def _gate_mentioned(text: str, name: str) -> bool:
    if name == "H3":
        return bool(re.search(r"(?<!-)H3(?!-hard)", text))
    if name == "H3-hard":
        return "H3-hard" in text
    # G1 / G2 / G3 / H1 / H2 — word-ish
    return bool(re.search(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9-])", text))


def _extract_gate(text: str, name: str) -> GateLight:
    pat = re.compile(
        rf"{re.escape(name)}\s+(PASS|FAIL|SKIP)(?:\s*[:：]\s*([^\n|]+))?",
        re.I,
    )
    m = pat.search(text)
    if m:
        return GateLight(name=name, status=m.group(1).upper(), detail=(m.group(2) or "").strip())
    pat2 = re.compile(rf"{re.escape(name)}\s+n/a", re.I)
    if pat2.search(text):
        return GateLight(name=name, status="n/a", detail="")
    if not _gate_mentioned(text, name):
        return GateLight(name=name, status="n/a", detail="not in audit")
    return GateLight(name=name, status="未知", detail="")


def _enrich_g_gates(text: str, lights: list[GateLight]) -> list[GateLight]:
    by = {g.name: g for g in lights}
    if by.get("G3", GateLight("G3", "未知")).status == "未知":
        m = _G3_COUNT_RE.search(text)
        if m:
            count, sugar = int(m.group(1)), m.group(2).lower() == "true"
            if not sugar and count == 0:
                by["G3"] = GateLight("G3", "n/a", detail=f"count={count} sugar=False")
            elif sugar and count == 0:
                by["G3"] = GateLight("G3", "FAIL", detail="sugar but count=0")
            else:
                by["G3"] = GateLight("G3", "未知", detail=f"count={count} sugar=True")
    if by.get("G1", GateLight("G1", "未知")).status == "未知":
        m = _G1_MIX_RE.search(text)
        if m:
            a_exact, style_proxy, rel = int(m.group(1)), int(m.group(2)), int(m.group(3))
            detail = f"A_exact={a_exact} style_proxy={style_proxy} relative_evals={rel}"
            if rel == 0 and a_exact == 0:
                by["G1"] = GateLight("G1", "n/a", detail=detail)
            else:
                by["G1"] = GateLight("G1", "未知", detail=detail)
    m2 = _G2_SPOT_RE.search(text)
    if m2:
        # Prefer section header over inline "G2 n/a (P2 mode)" footnote
        by["G2"] = GateLight("G2", m2.group(1).upper(), detail="spot-check")
    elif by.get("G2", GateLight("G2", "未知")).status == "未知":
        pass
    # When H3-hard is definitive, bare H3 is not a separate lamp
    hh = by.get("H3-hard")
    if hh and hh.status in ("PASS", "FAIL", "SKIP", "n/a") and by.get("H3", GateLight("H3", "未知")).status == "未知":
        by["H3"] = GateLight("H3", "n/a", detail="see H3-hard")
    order = ["G1", "G2", "G3", "H1", "H2", "H3-hard", "H3"]
    return [by[n] for n in order if n in by]


def parse_audit(path: str | Path) -> AuditSummary:
    p = Path(path)
    if not p.is_file():
        return AuditSummary(
            path=str(p),
            overall="未知",
            gates_ok="未知",
            parse_ok=False,
            snippet=f"(file missing: {p})",
            display_overall="未知",
            has_unknown_gate=True,
        )
    text = p.read_text(encoding="utf-8", errors="replace")
    title = _TITLE_RE.search(text)
    gates_ok_m = _GATES_OK_RE.search(text)
    result_m = _RESULT_RE.search(text)
    overall = "未知"
    if title:
        overall = title.group(1).upper()
    elif result_m:
        overall = result_m.group(1).upper()
    gates_ok = gates_ok_m.group(1) if gates_ok_m else "未知"

    names = ["G1", "G2", "G3", "H1", "H2", "H3-hard", "H3"]
    lights: list[GateLight] = []
    for name in names:
        if name == "H3":
            gl = _extract_gate(text, "H3")
            if "H3-hard" in text and gl.status not in ("未知", "n/a"):
                m = re.search(r"(?<!-)H3(?!-hard)\s+(PASS|FAIL|SKIP)", text, re.I)
                if m:
                    gl = GateLight(name="H3", status=m.group(1).upper())
                elif not _gate_mentioned(text, "H3"):
                    gl = GateLight(name="H3", status="n/a", detail="see H3-hard")
            lights.append(gl)
        else:
            lights.append(_extract_gate(text, name))

    lights = _enrich_g_gates(text, lights)

    has_unknown = any(g.status == "未知" for g in lights)
    # U11: unknown lamp must never paint overall green
    display_overall = overall
    if has_unknown and overall == "PASS":
        display_overall = "含未知"
    if not (title or gates_ok_m or result_m):
        display_overall = "未知"

    mode_m = _MODE_RE.search(text)
    backend_m = _BACKEND_RE.search(text)
    rows_m = _ROWS_RE.search(text)
    db_m = _DB_WRITTEN_RE.search(text)
    snippet = "\n".join(text.splitlines()[:40])
    raw = ""
    if gates_ok_m:
        start = max(0, gates_ok_m.start() - 20)
        raw = text[start : gates_ok_m.end() + 200].splitlines()[0][:400]

    return AuditSummary(
        path=str(p),
        overall=overall,
        gates_ok=str(gates_ok),
        mode=mode_m.group(1) if mode_m else "",
        backend=backend_m.group(1) if backend_m else "",
        rows_written=rows_m.group(1) if rows_m else "",
        db_written=(db_m.group(1).strip() if db_m else "未知"),
        gates=lights,
        snippet=snippet,
        parse_ok=title is not None or gates_ok_m is not None or result_m is not None,
        raw_gates_line=raw,
        has_unknown_gate=has_unknown,
        display_overall=display_overall or overall,
    )


# --- P2.1: constraint sat_rate (read-only audit counts; never recompute from db) ---

@dataclass
class ConstraintSatRate:
    """PASS/FAIL counts from audit ## Constraints. Descriptive only — not a gate."""

    pass_n: int | None = None
    total_m: int | None = None
    section_found: bool = False
    parseable: bool = False


_CONSTRAINTS_SECTION_RE = re.compile(
    r"^##\s+Constraints\b.*?(?=^##\s|\Z)",
    re.M | re.S,
)
_CONSTRAINT_MARK_RE = re.compile(r"^###\s+\[(PASS|FAIL)\]", re.M)


def parse_constraint_sat_rate(path: str | Path | None) -> ConstraintSatRate:
    """Count explicit ### [PASS] / ### [FAIL] under ## Constraints.

    Footnote / omitted relative PASS lines are ignored (only markers in the file count).
    Missing section or zero markers → parseable=False (UI shows em-dash).
    """
    if not path:
        return ConstraintSatRate()
    p = Path(path)
    if not p.is_file():
        return ConstraintSatRate()
    text = p.read_text(encoding="utf-8", errors="replace")
    sec_m = _CONSTRAINTS_SECTION_RE.search(text)
    if not sec_m:
        return ConstraintSatRate(section_found=False, parseable=False)
    section = sec_m.group(0)
    marks = _CONSTRAINT_MARK_RE.findall(section)
    if not marks:
        return ConstraintSatRate(section_found=True, parseable=False)
    pass_n = sum(1 for m in marks if m.upper() == "PASS")
    fail_n = sum(1 for m in marks if m.upper() == "FAIL")
    return ConstraintSatRate(
        pass_n=pass_n,
        total_m=pass_n + fail_n,
        section_found=True,
        parseable=True,
    )
