"""Write audit report markdown (P1 G1–G3 fields)."""
from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .constraints import ConstraintEval
from .construct import ConstructResult
from .job import Job
from .paths import portable
from .source import SourceDB

SHANGHAI = ZoneInfo("Asia/Shanghai")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def write_audit(
    path: Path,
    job: Job,
    source: SourceDB,
    b_instances: list[str],
    b_pvts: list[str],
    result: ConstructResult,
    evals: list[ConstraintEval],
    row_count: int,
    gates_ok: bool,
    gates_msg: str,
    *,
    g2_ok: bool = True,
    g2_msg: str = "",
    g2_results: list[dict[str, Any]] | None = None,
    ab_hard_audit: dict[str, Any] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(tz=SHANGHAI).strftime("%Y-%m-%d %H:%M:%S %Z")

    a_inst = set(source.instances)
    a_pvt = set(source.pvts)
    new_inst = [x for x in b_instances if x not in a_inst]
    new_pvt = [x for x in b_pvts if x not in a_pvt]

    extr = sum(1 for m in result.meta.values() if m.extrapolated)
    yaml_fp = _sha256_file(job.path) if job.path.exists() else "n/a"
    db_fp = _sha256_file(source.path)

    status = "PASS" if gates_ok else "FAIL"
    cfg = job.construct
    model_line = "n/a"
    if result.model_path:
        model_line = (
            f"`{result.model_path}` (sha256[:16]={result.model_sha16 or 'n/a'})"
        )

    rel_evals = [e for e in evals if e.type == "relative_delta_vs_source"]
    n_a_exact = sum(
        1 for e in rel_evals if (e.metrics or {}).get("baseline_source") == "A_exact"
    )
    n_proxy = sum(
        1
        for e in rel_evals
        if (e.metrics or {}).get("baseline_source") == "style_proxy"
    )

    lines = [
        f"# EPC Audit Report — {job.job_name} — **{status}**",
        "",
        f"- Generated: **{now}** (Asia/Shanghai)",
        f"- Engine: `epc_engine`",
        f"- **mode / operator**: `{getattr(job, 'mode', 'epc_ab')}`",
        f"- Job YAML: `{job.path}` (sha256[:16]={yaml_fp})",
        f"- Source DB: `{source.path}` (sha256[:16]={db_fp})",
        f"- Target process: `{job.target_process}` ← `{job.source_process}`",
        f"- **construct.backend**: `{result.backend}` (cfg `{cfg.backend}`)",
        f"- **construct.prior**: `{result.prior}`",
        f"- **construct.apply_on**: `{getattr(result, 'apply_on', cfg.apply_on)}`",
        f"- **fallback_used**: `{result.fallback_used}`",
        f"- **model**: {model_line}",
        f"- Hold-out report (offline): `{portable('/workspace/epc_fixtures/algo_holdout_report.md')}`",
        f"- **gates_ok: `{gates_ok}`** — {gates_msg}",
        f"- B.db written: **{'yes' if gates_ok and row_count > 0 else 'no (FAIL / skipped)'}**",
        "",
        "## P1 credibility gates (G1–G3)",
        "",
        f"- **G3 expanded_constraint_count**: `{job.expanded_constraint_count}` "
        f"(sugar_declared={job.sugar_declared})",
        f"- **G1 baseline mix**: A_exact={n_a_exact}, style_proxy={n_proxy}, "
        f"relative_evals={len(rel_evals)}",
        f"- **G2 spot-check**: {'PASS' if g2_ok else 'FAIL'} — {g2_msg}",
        "",
    ]
    if g2_results:
        lines += [
            "| family | instance | pvt | key | δ% | baseline_source | detail | ok |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in g2_results:
            lines.append(
                f"| {r.get('key_family') or '-'} | `{r.get('instance')}` | "
                f"`{r.get('pvt')}` | `{r.get('key')}` | {r.get('delta_pct')} | "
                f"{r.get('baseline_source')} | {r.get('detail','')} | {r.get('ok')} |"
            )
        lines.append("")

    lines += [
        "## I/O summary",
        "",
        f"| Axis | Count |",
        f"|---|---|",
        f"| B instances | {len(b_instances)} |",
        f"| B pvts | {len(b_pvts)} |",
        f"| field_keys | {len(result.field_keys)} |",
        f"| rows written | **{row_count}** |",
        f"| table N | {result.n} |",
        f"| groups extrapolated | {extr} / {len(result.meta)} |",
        "",
        "### B instances ∉ A",
        "",
    ]
    if new_inst:
        for x in new_inst:
            lines.append(f"- `{x}`")
    else:
        lines.append("- (none)")
    lines += ["", "### B pvts ∉ A", ""]
    if new_pvt:
        for x in new_pvt:
            lines.append(f"- `{x}`")
    else:
        lines.append("- (none)")

    lines += [
        "",
        "## Constraints (AND; constraint > style)",
        "",
    ]
    # Cap verbose relative listings in audit: show FAIL all + sample of PASS
    shown = 0
    max_pass_rel = 24
    for e in evals:
        is_rel = e.type == "relative_delta_vs_source"
        if is_rel and e.passed and shown >= max_pass_rel:
            continue
        mark = "PASS" if e.passed else "FAIL"
        lines.append(f"### [{mark}] #{e.index} `{e.type}`")
        lines.append("")
        lines.append(f"- Locator: `{e.locator}`")
        lines.append(f"- Applied: {e.applied}")
        lines.append(f"- Detail: {e.detail}")
        if e.metrics:
            # Prefer compact relative metrics
            m = e.metrics
            if is_rel:
                lines.append(
                    f"- baseline_source: `{m.get('baseline_source')}` "
                    f"baseline0=`{m.get('baseline0')}` "
                    f"proxy_ref=`{m.get('proxy_ref') or ''}` "
                    f"family=`{m.get('key_family')}`"
                )
            else:
                lines.append(f"- Metrics: `{m}`")
        lines.append("")
        if is_rel and e.passed:
            shown += 1
    n_rel_pass = sum(1 for e in rel_evals if e.passed)
    if n_rel_pass > max_pass_rel:
        lines.append(
            f"_… {n_rel_pass - max_pass_rel} additional relative PASS evals omitted; "
            f"see expanded_constraint_count / G2._"
        )
        lines.append("")

    if ab_hard_audit:
        from .ab_hard import format_ab_hard_audit

        lines.extend(format_ab_hard_audit(ab_hard_audit))

    lines += [
        "## Gates",
        "",
        f"- require_constraint_satisfaction: `{job.require_constraint_satisfaction}`",
        f"- on_violation: `{job.on_violation}`",
        f"- Result: **{'PASS' if gates_ok else 'FAIL'}** — {gates_msg}",
        "",
        "## Group status sample",
        "",
        "| instance | pvt | status | extrapolated | residual_applied | residual_reason | notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for (inst, pvt), meta in sorted(result.meta.items()):
        ra = getattr(meta, "residual_applied", False)
        rr = getattr(meta, "residual_reason", "") or "-"
        lines.append(
            f"| `{inst}` | `{pvt}` | {meta.status} | {meta.extrapolated} | "
            f"{ra} | {rr} | {meta.notes} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- Synthetic DEMO fixtures are not foundry/PDK truth.",
        "- P1: `relative_improve_vs_source` expands to atomic "
        "`relative_delta_vs_source` (improve X% → delta_pct=-X).",
        "- S2 baseline: A_exact else style_proxy (pre-constraint construct); "
        "`allow_proxy_baseline:false` fails the job if proxy needed.",
        "- S5 production: `on_violation: fail_job` verify-only; FAIL does not keep B.db.",
        "- G1 auditability / G2 rewrite spot-check / G3 expansion count.",
        "- AB-hard: non-idw epc_ab requires offline LOI/LOP stamp (`≤` idw); "
        "missing/stale/FAIL → no B.db (decoupled from P2 H3-hard).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
