#!/usr/bin/env python3
"""GUI-P1 headless smoke: U1/U2/U4/U10 (+ audit R3, requirements)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))
os.environ.setdefault("PYTHONPATH", str(_REPO))

from epc_gui.services.audit_parse import parse_audit
from epc_gui.services.sugar import dry_run_precheck, expand_from_path
from epc_gui.services import trend as trend_svc
from epc_gui.services.yaml_io import FIXTURE_SHORTCUTS, load_yaml
from epc_gui.paths import portable


def main() -> int:
    errors: list[str] = []
    print("=== GUI-P1 headless smoke ===")

    # U10 requirements
    req = Path(_REPO, "epc_gui/requirements.txt").read_text(encoding="utf-8")
    for pkg in ("joblib", "scikit-learn"):
        if pkg not in req:
            errors.append(f"requirements missing {pkg}")
    try:
        import joblib  # noqa: F401
        import sklearn  # noqa: F401
        print("OK U10 joblib+sklearn importable")
    except Exception as e:
        errors.append(f"U10 import {e}")

    # U1 sugar expand
    green = FIXTURE_SHORTCUTS["p1_green"]
    res = expand_from_path(green)
    if not res.ok:
        errors.append(f"U1 expand fail {res.error}")
    else:
        n_rows = len(res.relative_rows or [])
        print(
            f"U1 expanded_constraint_count={res.expanded_constraint_count} "
            f"relative_rows={n_rows} sugar_declared={res.sugar_declared}"
        )
        if res.expanded_constraint_count != n_rows:
            # engine count should match flattened relative rows for this fixture
            errors.append(
                f"U1 count mismatch engine={res.expanded_constraint_count} rows={n_rows}"
            )
        if res.expanded_constraint_count != 16:
            errors.append(f"U1 want expanded=16 got {res.expanded_constraint_count}")

    # U2 dry-run vague — no db write
    vague = Path(_REPO, "epc_fixtures/p1/epc_job.p1_r1_vague.yaml")
    vdata = load_yaml(vague)
    out_db = portable(str((vdata.get("output") or {}).get("db_path", "") or "/tmp/no_such_vague.db"))
    if out_db.is_file():
        out_db.unlink()
    before = out_db.is_file()
    r2 = dry_run_precheck(path=vague)
    after = out_db.is_file()
    print(f"U2 vague ok={r2.ok} err={r2.error[:90] if r2.error else ''}")
    if r2.ok:
        errors.append("U2 vague should fail dry-run")
    if after and not before:
        errors.append(f"U2 vague wrote db {out_db}")
    # green dry-run pass
    g2 = dry_run_precheck(path=green)
    print(f"U2 green dry-run ok={g2.ok} expanded={g2.expanded_constraint_count}")
    if not g2.ok:
        errors.append(f"U2 green dry-run fail {g2.error}")

    # U4 T1 seed_from_A on DEMO sample
    sample = load_yaml(FIXTURE_SHORTCUTS["sample"])
    a, b = portable(sample["source"]["db_path"]), portable(sample["output"]["db_path"])
    if Path(b).is_file() and Path(a).is_file():
        inst, pvt, key, err, st = trend_svc.find_seed_from_a(a, b, sample)
        print(f"U4 seed_from_A {inst}×{pvt}×{key} max_rel={err:.3e} {st}")
        if not (err == err and err < 1e-9 and st == "seed_from_A"):
            errors.append(f"U4 seed max_rel={err} st={st}")
    else:
        errors.append("U4 sample db missing")

    # U11 / R3 geom audit lights
    geom_audit = Path(_REPO, "epc_fixtures/p2/out_geom_audit.md")
    s = parse_audit(geom_audit)
    lights = {g.name: g.status for g in s.gates}
    print(f"U11 geom lights={lights} display={s.display_overall} unk={s.has_unknown_gate}")
    if s.display_overall != "PASS":
        errors.append(f"U11 display_overall={s.display_overall}")
    if s.has_unknown_gate:
        errors.append(f"U11 still has unknown {lights}")
    for need in ("H1", "H2", "H3-hard"):
        if lights.get(need) == "未知":
            errors.append(f"U11 {need} still 未知")
    # unknown must not be green: synthetic check
    if any(g.status == "未知" for g in s.gates) and s.display_overall == "PASS":
        errors.append("U11 unknown painted overall green")

    # Fluent re-skin assertions (spec §7; replaces the old token check)
    try:
        from qfluentwidgets import isDarkTheme, setTheme, themeColor, Theme
        setTheme(Theme.LIGHT)
        if isDarkTheme():
            errors.append("qfluentwidgets LIGHT theme reported dark")
        if not themeColor().isValid():
            errors.append("qfluentwidgets themeColor invalid")
        print("OK qfluentwidgets theme LIGHT default")
    except Exception as e:
        errors.append(f"qfluentwidgets unavailable: {e}")
    design = Path(_REPO, "epc_gui/DESIGN.md").read_text(encoding="utf-8")
    if "EEF1F5" not in design or "2E6BB0" not in design:
        errors.append("DESIGN.md missing light tokens")
    before = len(errors)
    theme_src = Path(_REPO, "epc_gui/theme.py").read_text(encoding="utf-8")
    if "_build_qss" in theme_src:
        errors.append("theme.py still ships the old QSS builder")
    app_src = Path(_REPO, "epc_gui/app.py").read_text(encoding="utf-8")
    if "class MainWindow(FluentWindow" not in app_src:
        errors.append("app.py MainWindow is not a FluentWindow")
    if "def build_main_window" not in app_src:
        errors.append("app.py missing build_main_window")
    if len(errors) == before:
        print("OK Fluent shell contract (theme.py/app.py)")

    # i18n locale tables + settings
    from epc_gui.i18n import tr, set_locale, get_locale
    from epc_gui.i18n.catalog import ZH, EN
    from epc_gui.services import history as hist_svc
    if "nav.config" not in ZH or "nav.config" not in EN:
        errors.append("i18n missing nav.config")
    for key in (
        "nav.config", "nav.preview", "nav.compare", "nav.settings",
        "settings.title", "settings.dark_card", "settings.dark_hint",
        "settings.lang_card",
    ):
        if key not in ZH or key not in EN:
            errors.append(f"i18n missing {key}")
    set_locale("zh", emit=False)
    if tr("btn.dry_run") != "预检":
        errors.append(f"zh dry_run={tr('btn.dry_run')!r}")
    set_locale("en", emit=False)
    if tr("btn.dry_run") != "Dry-run":
        errors.append(f"en dry_run={tr('btn.dry_run')!r}")
    # forbid known stacked bilingual control labels from the old copy pass
    banned = (
        "预检 / Dry-run",
        "糖衣展开 / Expand",
        "配置 / Config",
        "运行 / Run",
        "导出对比 / Export",
        "深色 / Dark",
        "浅色 / Light",
        "叠 A / Overlay A",
        "未打开 / —",
        "门禁 / Gates",
    )
    blob = "\n".join(list(ZH.values()) + list(EN.values()))
    for b in banned:
        if b in blob:
            errors.append(f"banned stacked label still present: {b!r}")
    # pages/app source must not hardcode stacked labels either
    for rel in ("app.py", "pages/config_page.py", "pages/preview_page.py", "pages/compare_page.py"):
        src = Path(_REPO, "epc_gui", rel).read_text(encoding="utf-8")
        for b in banned:
            if b in src:
                errors.append(f"{rel} still has {b!r}")
    # DESIGN writing must mention locale switch, not stacked bilingual on controls
    if "locale" not in design.lower() and "语言" not in design:
        errors.append("DESIGN.md missing locale/language switch")
    if "`中文 / EN`" in design or "每控件" in design:
        # old stacked rule should be gone from Writing
        if "Do **not**" not in design and "禁止" not in design and "not stacked" not in design.lower():
            errors.append("DESIGN.md still pushes stacked bilingual without ban")
    s = hist_svc.load_settings()
    if "locale" not in s:
        errors.append("settings missing locale default")
    print(f"OK i18n zh/en tr() locale default={s.get('locale')}")
    before = len(errors)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old_path = hist_svc.SETTINGS_PATH
        try:
            hist_svc.SETTINGS_PATH = Path(td) / "settings.json"
            if hist_svc.load_settings().get("theme") != "light":
                errors.append("fresh settings default theme must be light")
        finally:
            hist_svc.SETTINGS_PATH = old_path
    if len(errors) == before:
        print("OK fresh settings default theme=light")

    # copy hygiene: deleted microcopy must stay empty; widgets not showing slogans
    for empty_key in (
        "footer.demo",
        "config.disc",
        "preview.hint",
        "compare.hint",
        "sugar.summary",
        "preview.matrix_hint",
        "brand.sub",
    ):
        set_locale("zh", emit=False)
        if tr(empty_key).strip():
            errors.append(f"zh {empty_key} should be empty, got {tr(empty_key)!r}")
        set_locale("en", emit=False)
        if tr(empty_key).strip():
            errors.append(f"en {empty_key} should be empty, got {tr(empty_key)!r}")
    set_locale("zh", emit=False)
    if tr("group.expand") != "约束预览":
        errors.append(f"zh group.expand={tr('group.expand')!r}")
    if tr("lang.chrome") != "语言":
        errors.append(f"zh lang.chrome={tr('lang.chrome')!r}")
    if tr("dry.pass") != "预检通过":
        errors.append(f"zh dry.pass={tr('dry.pass')!r}")
    set_locale("en", emit=False)
    if tr("group.expand") != "Constraints":
        errors.append(f"en group.expand={tr('group.expand')!r}")
    if tr("lang.chrome") != "Language":
        errors.append(f"en lang.chrome={tr('lang.chrome')!r}")
    # ban disclaimer / sugar jargon in catalogs
    banned_copy = (
        "不承诺精度",
        "夹具优先",
        "fixtures first",
        "no accuracy claim",
        "糖衣展开",
        "expanded_constraint_count=",
        "sugar_declared=",
        "语言 Language",
        "DEMO 夹具",
        "DEMO fixtures",
    )
    blob2 = "\n".join(list(ZH.values()) + list(EN.values()))
    for b in banned_copy:
        if b in blob2:
            errors.append(f"banned copy still in i18n: {b!r}")
    # UI sources must not keep disclaimer widgets wired
    for rel in ("app.py", "pages/config_page.py", "pages/preview_page.py", "pages/compare_page.py"):
        src = Path(_REPO, "epc_gui", rel).read_text(encoding="utf-8")
        for b in ("footer.demo", "config.disc", "preview.hint", "compare.hint", "sugar.summary"):
            if f'tr("{b}"' in src or f"tr('{b}'" in src:
                errors.append(f"{rel} still calls tr({b})")
        if "self.foot" in src and rel == "app.py":
            errors.append("app.py still has self.foot")
        if "self.disc" in src and rel == "pages/config_page.py":
            errors.append("config_page still has self.disc")
        if "self.hint" in src and rel in ("pages/preview_page.py", "pages/compare_page.py"):
            errors.append(f"{rel} still has self.hint")
    print("OK copy hygiene (empty keys + no disclaimer)")

    if errors:
        print("FAIL:", errors)
        return 1
    print("ALL P1 SMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
