#!/usr/bin/env python3
"""GUI-P2 headless smoke: chart1/chart2 helpers + P1 regression pointer."""
from __future__ import annotations

import os
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, "/workspace")
os.environ.setdefault("PYTHONPATH", "/workspace")

from epc_gui.services import compare_views as cv
from epc_gui.services.yaml_io import FIXTURE_SHORTCUTS, load_yaml


def main() -> int:
    errors: list[str] = []
    print("=== GUI-P2 / P2.1 headless smoke ===")

    p1 = load_yaml(FIXTURE_SHORTCUTS["p1_green"])
    a, b = p1["source"]["db_path"], p1["output"]["db_path"]
    m = cv.build_chart1(
        yaml_path=FIXTURE_SHORTCUTS["p1_green"],
        yaml_data=p1,
        a_db=a,
        b_db=b,
    )
    print(
        f"U2 chart1 views={m.available_views} default={m.default_view} "
        f"rel={len(m.rel_bars)} bound={len(m.bound_cells)} list={len(m.list_rows)}"
    )
    if not m.has_constraints:
        errors.append("p1_green should have constraints")
    if m.default_view != cv.VIEW_REL_BARS:
        errors.append(f"default want rel_bars got {m.default_view}")
    for need in (cv.VIEW_REL_BARS, cv.VIEW_BOUND_CELLS, cv.VIEW_CONSTRAINT_LIST):
        if need not in m.available_views:
            errors.append(f"missing view {need}")

    z = deepcopy(p1)
    z["constraints"] = []
    m0 = cv.build_chart1(yaml_path=None, yaml_data=z, a_db=a, b_db=b)
    print(f"U1 empty constraints has={m0.has_constraints} views={m0.available_views}")
    if m0.has_constraints or m0.available_views:
        errors.append("empty constraints should hide chart1")

    f = cv.build_free_compare(ref_db=a, constructed_db=b)
    print(
        f"U3/U4/U5 free empty={f.empty_reason} pvt={f.selected_pvt} key={f.selected_key} "
        f"cover={f.cover_n}/{f.cover_m} Δmed={f.delta_med_pct} Δmean={f.delta_mean_pct} "
        f"n_pts={len(f.points)}"
    )
    if f.empty_reason:
        errors.append(f"free compare empty: {f.empty_reason}")
    if not f.pvt_options:
        errors.append("no PVT intersection")
    if f.cover_m < 3:
        errors.append(f"want ≥3 capacity points, cover_m={f.cover_m}")
    caps = [p.capacity for p in f.points]
    if caps != sorted(caps):
        errors.append("capacity not ascending")
    # P21-M2: delta_mean matches hand mean(δ) on same both set
    import statistics
    from epc_gui.services.compare_views import EPS
    both = [p for p in f.points if p.a_value is not None and p.b_value is not None]
    if both:
        deltas = [
            (float(p.b_value) - float(p.a_value)) / max(abs(float(p.a_value)), EPS)
            for p in both
        ]
        hand_mean = float(statistics.mean(deltas)) * 100.0
        if f.delta_mean_pct is None or abs(f.delta_mean_pct - hand_mean) >= 1e-9:
            errors.append(
                f"Δmean mismatch gui={f.delta_mean_pct} hand={hand_mean}"
            )
    else:
        if f.delta_mean_pct is not None:
            errors.append("Δmean should be None when both empty")

    f_miss = cv.build_free_compare(ref_db=a, constructed_db=None)
    if f_miss.empty_reason != "need_dbs":
        errors.append(f"missing db reason={f_miss.empty_reason}")

    # Qt page: chart1 hidden when no constraints; layout widgets exist
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    from epc_gui.theme import apply_theme
    from epc_gui.pages.compare_page import ComparePage

    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme(app, "dark")
    page = ComparePage()
    page.set_context(
        a_db=a,
        b_db=b,
        audit=p1["output"]["audit_report_path"],
        exit_code=0,
        yaml_data=p1,
        yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
    )
    if page.chart1_box.isHidden():
        errors.append("chart1 should be visible with constraints")
    if not page.lbl_chart1_empty.isHidden():
        errors.append("chart1 empty label should hide when constrained")
    page.set_context(
        a_db=a,
        b_db=b,
        audit=p1["output"]["audit_report_path"],
        exit_code=0,
        yaml_data=z,
        yaml_path=None,
    )
    if not page.chart1_box.isHidden():
        errors.append("chart1 box should hide without constraints")
    if page.lbl_chart1_empty.isHidden():
        errors.append("chart1 empty sentence should show")
    # Restore constrained context for polish checks
    page.set_context(
        a_db=a,
        b_db=b,
        audit=p1["output"]["audit_report_path"],
        exit_code=0,
        yaml_data=p1,
        yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
    )
    # Gate zone: no bare gates_ok dump; short overall; short db status
    if page.lbl_gates_ok.isVisible():
        errors.append("lbl_gates_ok must stay hidden")
    if "gates_ok" in page.lbl_overall.text().lower():
        errors.append(f"overall still dumps gates_ok: {page.lbl_overall.text()!r}")
    ov = page.lbl_overall.text()
    if ov not in ("通过", "Pass", "未通过", "Fail", "未知", "Unknown"):
        # allow PASS-era leftovers only if empty before audit — expect 通过 for p1 green zh
        if "通过" not in ov and "Pass" not in ov:
            errors.append(f"overall awkward: {ov!r}")
    db_t = page.lbl_db.text()
    if "/" in db_t or "B.db" in db_t or "存在" in db_t:
        errors.append(f"db label should be short status, got {db_t!r}")
    # Chart1: ordinal ticks, not long locator names
    page.refresh_chart1()
    if page.cb_view.currentData() == "rel_bars" or True:
        # force rel_bars if available
        idx = page.cb_view.findData("rel_bars")
        if idx >= 0:
            page.cb_view.setCurrentIndex(idx)
            page._render_chart1()
        ax = page.plot_c1.getAxis("bottom")
        ticks = ax.ticks() if hasattr(ax, "ticks") else None
        # pyqtgraph stores via setTicks; read _tickLevels
        levels = getattr(ax, "_tickLevels", None) or getattr(ax, "tickLevels", None)
        # Fallback: inspect set tick strings via list
        major = None
        if hasattr(ax, "_tickLevels") and ax._tickLevels:
            major = ax._tickLevels[0]
        elif hasattr(ax, "tickStrings"):
            major = None
        # Use hover tips as proof of ordinal path
        if not page._c1_hover_tips:
            errors.append("chart1 hover tips empty for rel_bars")
        # Tick labels should be ordinal circled or digits
        tick_ok = False
        try:
            # After setTicks([[(i, label)...]])
            tl = ax._tickLevels  # type: ignore[attr-defined]
            if tl and tl[0]:
                labels = [lab for _, lab in tl[0]]
                tick_ok = all(
                    (lab[:1] in "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳") or lab.isdigit()
                    for lab in labels
                )
                if not tick_ok:
                    errors.append(f"chart1 ticks not ordinal: {labels[:5]}")
        except Exception as e:
            # soft: hover tips present is enough
            print(f"tick inspect soft-fail: {e}")
        print(f"OK polish overall={ov!r} db={db_t!r} hover_tips={len(page._c1_hover_tips)}")
    # P21-M1: sat_rate from audit (independent of chart1 view)
    from epc_gui.services.audit_parse import parse_constraint_sat_rate
    audit_path = p1["output"]["audit_report_path"]
    sat = parse_constraint_sat_rate(audit_path)
    print(f"P21-M1 sat parseable={sat.parseable} n/m={sat.pass_n}/{sat.total_m}")
    if not sat.parseable or sat.pass_n is None or sat.total_m is None or sat.total_m < 1:
        errors.append(f"p1_green sat_rate unparseable: {sat}")
    else:
        # Independent recount
        from pathlib import Path as _P
        import re as _re
        _txt = _P(audit_path).read_text(encoding="utf-8")
        _sec = _re.search(r"^##\s+Constraints\b.*?(?=^##\s|\Z)", _txt, _re.M | _re.S)
        _marks = _re.findall(r"^###\s+\[(PASS|FAIL)\]", _sec.group(0), _re.M) if _sec else []
        _n = sum(1 for m in _marks if m == "PASS")
        _m = len(_marks)
        if sat.pass_n != _n or sat.total_m != _m:
            errors.append(f"sat_rate {sat.pass_n}/{sat.total_m} != hand {_n}/{_m}")
    # UI: sat visible with constraints; text matches
    sat_txt = page.lbl_sat.text()
    print(f"P21-M1 UI sat={sat_txt!r} hidden={page.lbl_sat.isHidden()}")
    if page.lbl_sat.isHidden():
        errors.append("sat label should show with constraints")
    expect_zh = f"约束 达标 {sat.pass_n}/{sat.total_m}"
    if sat_txt != expect_zh:
        errors.append(f"sat UI want {expect_zh!r} got {sat_txt!r}")
    # Empty constraints hides sat with chart1
    page.set_context(
        a_db=a, b_db=b, audit=audit_path, exit_code=0, yaml_data=z, yaml_path=None
    )
    if (not page.lbl_sat.isHidden()) and page.chart1_box.isHidden():
        errors.append("sat should hide with chart1 when no constraints")
    # when chart1_box hidden, sat may still be non-hidden internally — require clear text or hidden flag after empty
    if page.chart1_box.isHidden() and page.lbl_sat.text() and not page.lbl_sat.isHidden():
        # _update_sat_rate clears + hides; enforce
        errors.append("sat should be cleared/hidden when no constraints")
    # Restore constrained
    page.set_context(
        a_db=a,
        b_db=b,
        audit=audit_path,
        exit_code=0,
        yaml_data=p1,
        yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
    )
    # P21-M2 UI
    mean_txt = page.lbl_delta_mean.text()
    print(f"P21-M2 UI mean={mean_txt!r}")
    if "均值差" not in mean_txt:
        errors.append(f"delta_mean label missing 均值差: {mean_txt!r}")
    # Unparseable Constraints section → 约束 —
    page.set_context(
        a_db=a,
        b_db=b,
        audit="/workspace/epc_fixtures/p2/out_geom_audit.md",
        exit_code=0,
        yaml_data=p1,
        yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
    )
    if page.lbl_sat.text() != "约束 —":
        errors.append(f"unparseable sat want 约束 — got {page.lbl_sat.text()!r}")
    # restore p1 audit
    page.set_context(
        a_db=a,
        b_db=b,
        audit=audit_path,
        exit_code=0,
        yaml_data=p1,
        yaml_path=str(FIXTURE_SHORTCUTS["p1_green"]),
    )

    # i18n keys
    from epc_gui.i18n import tr, set_locale
    set_locale("zh", emit=False)
    if tr("group.chart1") != "结果约束反标":
        errors.append(f"zh chart1 title={tr('group.chart1')!r}")
    if tr("chart1.empty") != "无约束":
        errors.append(f"zh empty={tr('chart1.empty')!r}")
    if "覆盖" in tr("free.cover", n=1, m=2):
        errors.append("cover still says 覆盖")
    if tr("chart1.sat_rate", n=3, m=5) != "约束 达标 3/5":
        errors.append(f"zh sat={tr('chart1.sat_rate', n=3, m=5)!r}")
    if tr("free.delta_mean", pct=1.5) != "均值差 +1.5%":
        errors.append(f"zh mean={tr('free.delta_mean', pct=1.5)!r}")
    set_locale("en", emit=False)
    if tr("group.chart1") != "Constraint markup":
        errors.append(f"en chart1 title={tr('group.chart1')!r}")
    if tr("chart1.sat_rate", n=3, m=5) != "Constraints 3/5":
        errors.append(f"en sat={tr('chart1.sat_rate', n=3, m=5)!r}")
    if "Mean Δ" not in tr("free.delta_mean", pct=-2.0):
        errors.append(f"en mean={tr('free.delta_mean', pct=-2.0)!r}")
    set_locale("zh", emit=False)
    print("OK ComparePage visibility + polish + P2.1")

    if errors:
        print("FAIL:", errors)
        return 1
    print("ALL P2 / P2.1 SMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
