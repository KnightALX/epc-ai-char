#!/usr/bin/env python3
"""UI interaction regression: drive the real callbacks and assert observable state.

Offscreen-safe. Covers: navigation switching, the settings cards (theme +
language), shortcut loading, constraint preview, dry-run (green/red), a real
engine run through run_job (QProcess), preview paging, compare view switching +
hover bounds, history replay, and theme re-apply idempotence.

Exit 0 only when every assertion holds; prints one OK/FAIL line per check.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(_REPO))

from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication

from epc_gui.app import build_main_window
from epc_gui.i18n import get_locale, tr
from epc_gui.paths import portable
from epc_gui.services import history as hist_svc
from epc_gui.services.yaml_io import FIXTURE_SHORTCUTS, load_yaml, save_yaml
from epc_gui.theme import apply_theme, current_tokens
from qfluentwidgets import isDarkTheme

errors: list[str] = []


def check(cond, msg: str) -> None:
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        errors.append(msg)


def guard(fn):
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except Exception:
            errors.append(f"{fn.__name__} raised")
            print(f"FAIL {fn.__name__} raised")
            traceback.print_exc()
            return None

    return wrapper


def spin(app, ms: int = 120) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()
    app.processEvents()


def wait_until(app, pred, timeout_s: float = 180.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        app.processEvents()
        if pred():
            return True
        time.sleep(0.05)
    return False


def main() -> int:
    app = QApplication(sys.argv)
    apply_theme(app, "light")
    win = build_main_window()
    win.show()
    spin(app, 200)
    data = load_yaml(FIXTURE_SHORTCUTS["sample"])

    # 1) shell: four pages registered, config is current
    check(
        win.stack.count() == 4,
        f"stack has four pages (count={win.stack.count()})",
    )
    check(
        win.stack.currentWidget() is win.config,
        "config page active at startup",
    )

    # 2) navigation routing: the real (animated) path must eventually land
    win.switch_to("preview")
    landed = wait_until(app, lambda: win.stack.currentWidget() is win.preview, timeout_s=8)
    check(landed, "switch_to('preview') lands on the preview page (animated path)")
    # deterministic from here on: the Fluent stack fades between pages
    win.stack.setAnimationEnabled(False)
    keys = ("config", "preview", "compare", "settings", "config", "config")
    nav_ok = True
    for key in keys:
        win.switch_to(key)
        spin(app, 40)
        if win.stack.currentWidget() is not win._pages[key]:
            nav_ok = False
    check(nav_ok, "switch_to() routes the stack deterministically, repeat-safe")
    win._nav_items["compare"].click()
    spin(app, 60)
    check(win.stack.currentWidget() is win.compare, "clicking a nav item routes through the shell")

    # 3) settings: dark switch -> qconfig + tokens, then back to light
    page = win.settings_page
    page.theme_card.setChecked(True)
    spin(app, 80)
    check(isDarkTheme() and current_tokens().name == "dark", "dark switch drives qconfig + dark tokens")
    page.theme_card.setChecked(False)
    spin(app, 80)
    check((not isDarkTheme()) and current_tokens().name == "light", "light switch restores light tokens")

    # 4) settings: language combo -> locale + nav labels
    zh_nav = tr("nav.config") if get_locale() == "zh" else None
    page.lang_combo.setCurrentIndex(1)
    spin(app, 80)
    en_nav = tr("nav.config")
    check(get_locale() == "en", "language combo switches locale to en")
    check(en_nav != zh_nav if zh_nav else True, "en nav.config label differs from zh")
    item = win._nav_items.get("config")
    check(item is not None and item.text() == en_nav, "nav item text follows locale change")
    page.lang_combo.setCurrentIndex(0)
    spin(app, 80)
    check(get_locale() == "zh", "language combo switches back to zh")

    # 5) shortcut load fills the form + YAML editor
    win.config.load_shortcut("sample")
    spin(app, 80)
    job_name = data.get("job_name", "")
    check(
        bool(job_name) and win.config.ed_job.text() == job_name,
        f"load_shortcut fills ed_job with the job name ({win.config.ed_job.text()})",
    )
    yaml_path = str(getattr(win.config, "_yaml_path", "") or "")
    check(yaml_path.endswith("epc_job.sample.yaml"), f"load_shortcut points at the sample YAML ({yaml_path})")
    check(len(win.config.yaml_edit.toPlainText()) > 100, "load_shortcut fills the YAML editor")

    # 6) constraint preview table mirrors the declared sugar rows
    win.config.refresh_sugar()
    spin(app, 80)
    rows = win.config.sugar_table.rowCount()
    check(rows >= 1, f"sugar table lists the declared sugar row(s) (got {rows})")

    # 7) dry-run callbacks: red contract on the vague fixture, green on sample
    from epc_gui.theme import current_tokens as _tok

    t = _tok()
    vague = _REPO / "epc_fixtures/p1/epc_job.p1_r1_vague.yaml"
    win.config.load_yaml_path(str(vague))
    spin(app, 60)
    win.config.dry_run()
    spin(app, 60)
    check(
        "预检失败" in win.config.lbl_dry.text() and t.FailRose in win.config.lbl_dry.styleSheet(),
        "vague dry-run shows the failure text in the fail color",
    )
    win.config.load_shortcut("sample")
    spin(app, 60)
    win.config.dry_run()
    spin(app, 60)
    check(
        "预检通过" in win.config.lbl_dry.text() and t.MuteFog in win.config.lbl_dry.styleSheet(),
        "sample dry-run shows the pass text in the neutral color",
    )
    check(
        "constraints=2" in win.config.log.toPlainText(),
        "dry-run log counts the two declared constraints",
    )

    # 8) real engine run through run_job (QProcess) into a temp db
    tmp = Path(tempfile.mkdtemp(prefix="epc_ui_reg_"))
    data = load_yaml(FIXTURE_SHORTCUTS["sample"])
    db_out = tmp / "B_ui_reg.db"
    audit_out = tmp / "B_ui_reg_audit.md"
    data["output"]["db_path"] = str(db_out)
    data["output"]["audit_report_path"] = str(audit_out)
    job_yaml = tmp / "epc_job.ui_reg.yaml"
    save_yaml(job_yaml, data)
    win.config.load_yaml_path(str(job_yaml))
    spin(app, 60)
    seen: dict = {}
    win.config.job_finished.connect(lambda code, db, audit: seen.update(code=code, db=db, audit=audit))

    def done() -> bool:
        return "code" in seen

    win.config.run_job()
    finished = wait_until(app, done, timeout_s=240)
    spin(app, 200)
    check(finished, "run_job finished (job_finished emitted)")
    check(seen.get("code") == 0, f"run_job exit code 0 (got {seen.get('code')})")
    check(Path(seen.get("db", "")).is_file(), "run_job wrote the B db")
    check(Path(seen.get("audit", "")).is_file(), "run_job wrote the audit report")
    rows = 0
    if Path(seen.get("db", "")).is_file():
        import sqlite3

        con = sqlite3.connect(str(seen["db"]))
        try:
            rows = con.execute("SELECT COUNT(*) FROM char_data").fetchone()[0]
        finally:
            con.close()
    check(rows == 4950, f"run_job db row count == 4950 (got {rows})")
    check("EXIT" in win.config.lbl_exit.text() and "0" in win.config.lbl_exit.text(), "lbl_exit shows EXIT 0")
    check(win.stack.currentWidget() is win.preview, "request_preview switched the shell to the preview page")

    # 9) preview paging on the freshly generated db
    win.preview.open_db(str(db_out))
    spin(app, 120)
    first = win.preview.table.rowCount()
    check(first > 0, f"preview shows rows ({first})")
    win.preview.btn_next.click()
    spin(app, 120)
    check("offset=80" in win.preview.lbl_page.text(), f"next page advances offset ({win.preview.lbl_page.text()})")

    # 10) compare: context + three view switches + hover bounds
    win.compare.set_context(
        a_db=str(_REPO / "epc_fixtures/A_ref.db"),
        b_db=str(db_out),
        audit=str(audit_out),
        exit_code=0,
        yaml_data=data,
        yaml_path=str(job_yaml),
    )
    spin(app, 200)
    check(win.compare.cb_view.count() == 3, f"chart1 offers three views (got {win.compare.cb_view.count()})")
    views_ok = True
    for i in range(win.compare.cb_view.count()):
        win.compare.cb_view.setCurrentIndex(i)
        spin(app, 80)
        if win.compare.tbl_c1.rowCount() < 0:
            views_ok = False
    check(views_ok, "switching every chart1 view does not raise")
    win.compare._on_c1_hover(-1)
    win.compare._on_c1_hover(10**6)
    check(True, "hover with out-of-range int payloads is guarded")
    check(bool(win.compare.lbl_overall.text()), f"overall label populated ({win.compare.lbl_overall.text()})")
    check(bool(win.compare.gate_lights), "gate lights parsed from the audit")

    # 11) history replay: click the newest entry, compare context follows
    win.config.reload_history()
    spin(app, 80)
    check(win.config.history_list.count() >= 1, "history list has the run we just made")
    if win.config.history_list.count() >= 1:
        win.config._on_history_click(win.config.history_list.item(0))
        spin(app, 120)
        check(win.stack.currentWidget() is win.compare, "history click routes to the compare page")
        check(bool(win.compare.lbl_db.text()), "history click fills the db path label")

    # 12) theme re-apply is idempotent and repaints plots safely
    apply_theme(app, "dark")
    apply_theme(app, "dark")
    win.compare.reapply_theme_plots()
    check(current_tokens().name == "dark", "re-applying the dark theme is idempotent")
    win.set_theme("light")
    spin(app, 80)
    check((not isDarkTheme()) and current_tokens().name == "light", "set_theme('light') restores light")

    print(f"UI REGRESSION EXIT code={1 if errors else 0} failures={len(errors)}")
    for e in errors:
        print("  - " + e)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
