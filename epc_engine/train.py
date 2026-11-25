"""Offline train + hold-out: python -m epc_engine.train"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ab_hard import (
    GATE_AB_LOI,
    GATE_AB_LOP,
    GATE_LOI_REG,
    stamp_from_holdout_report,
    write_stamp,
)
from .paths import repo_root
from .source import load_source_db
from .train_lib import (
    RANDOM_SEED,
    run_holdout,
    save_bundle,
    sha16,
    train_full_model,
    write_holdout_report,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epc_engine.train",
        description="Train residual_gbdt on A_ref and/or run hold-out eval",
    )
    p.add_argument(
        "--source-db",
        default=str(repo_root() / "epc_fixtures" / "A_ref.db"),
        help="A_ref sqlite path (train labels from A only)",
    )
    p.add_argument(
        "--model-out",
        default=str(repo_root() / "epc_engine" / "models" / "residual_gbdt.joblib"),
        help="Where to write the production model bundle",
    )
    p.add_argument(
        "--report-out",
        default=str(repo_root() / "epc_fixtures" / "algo_holdout_report.md"),
        help="Hold-out markdown report path",
    )
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    p.add_argument(
        "--skip-holdout",
        action="store_true",
        help="Only train full model (no LOI/LOP report)",
    )
    p.add_argument(
        "--skip-train",
        action="store_true",
        help="Only run hold-out (no production model)",
    )
    p.add_argument(
        "--require-ab-hard",
        action="store_true",
        default=True,
        help="EXIT≠0 and refuse model promote when AB-hard FAIL (default on)",
    )
    p.add_argument(
        "--no-require-ab-hard",
        action="store_false",
        dest="require_ab_hard",
        help="Allow EXIT 0 even if AB-hard FAIL (debug only; still prints FAIL)",
    )
    return p


def _hard_gates_ok(gates: dict) -> bool:
    ab_loi = gates.get(GATE_AB_LOI, gates.get("P-LOI-base", False))
    ab_lop = gates.get(GATE_AB_LOP, gates.get("P-LOP", False))
    reg = gates.get(GATE_LOI_REG, False)
    return bool(ab_loi and ab_lop and reg)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = load_source_db(Path(args.source_db))
    print(
        f"[train] A={source.path} instances={len(source.instances)} "
        f"pvts={len(source.pvts)} keys={len(source.field_keys)}"
    )

    model_path = Path(args.model_out)
    report_path = Path(args.report_out)

    if not args.skip_holdout:
        print("[train] running LOI/LOP hold-out on core keys…")
        report = run_holdout(source, seed=args.seed)
        report["source_path"] = str(source.path)
        lb, lr = report["loi_baseline"], report["loi_residual"]
        print(
            f"[train] LOI p95 baseline={lb['p95']:.6g} residual={lr['p95']:.6g} "
            f"le_idw={lr['p95'] <= lb['p95']}"
        )
        pb, pr = report["lop_baseline"], report["lop_residual"]
        print(
            f"[train] LOP p95 baseline={pb['p95']:.6g} residual={pr['p95']:.6g} "
            f"le_idw={pr['p95'] <= pb['p95']}"
        )
        gates = report.get("gates") or {}
        for gid in (GATE_AB_LOP, GATE_AB_LOI, GATE_LOI_REG, "P-LOP", "P-LOI-base"):
            if gid in gates:
                ok = gates.get(gid, False)
                print(f"[train] gate {gid}={'PASS' if ok else 'FAIL'}")
        if not gates.get(GATE_AB_LOI, False):
            print("[train] WARNING: AB-hard-LOI failed", file=sys.stderr)
        if not gates.get(GATE_AB_LOP, False):
            print("[train] WARNING: AB-hard-LOP failed", file=sys.stderr)
    else:
        report = None

    hard_ok = _hard_gates_ok(report.get("gates") or {}) if report is not None else True

    if not args.skip_train:
        if report is not None and args.require_ab_hard and not hard_ok:
            print(
                "[train] REFUSING to promote residual_gbdt.joblib "
                "(AB-hard / P-LOI-reg FAIL) — no model overwrite",
                file=sys.stderr,
            )
            model_path_written = None
        else:
            print("[train] fitting full residual models on all A keys…")
            bundle = train_full_model(source, seed=args.seed)
            # Embed provisional stamp (sha filled after final dump); sidecar is authoritative.
            if report is not None:
                provisional = stamp_from_holdout_report(
                    report, model_sha16="pending", backend="residual_gbdt"
                )
                bundle["ab_hard_stamp"] = provisional
            save_bundle(bundle, model_path)
            model_sha = sha16(model_path)
            print(
                f"[train] model → {model_path} "
                f"keys={len(bundle['keys_trained'])} "
                f"sha16={model_sha} "
                f"sec={bundle['train_seconds']:.1f}"
            )
            if report is not None:
                stamp = stamp_from_holdout_report(
                    report, model_sha16=model_sha, backend="residual_gbdt"
                )
                # Sidecar binds to current file sha (do not re-dump joblib after this).
                # Bundle embed may still say pending/old; load_stamp prefers sidecar.
                sp = write_stamp(stamp, model_path)
                print(
                    f"[train] AB-hard stamp → {sp} "
                    f"status={stamp.get('ab_hard')} sha16={model_sha}"
                )
            model_path_written = model_path
    else:
        model_path_written = model_path if model_path.is_file() else None
        if report is not None and model_path_written is not None:
            # Hold-out only: still refresh stamp against existing model
            model_sha = sha16(model_path_written)
            stamp = stamp_from_holdout_report(
                report, model_sha16=model_sha, backend="residual_gbdt"
            )
            sp = write_stamp(stamp, model_path_written)
            print(
                f"[train] AB-hard stamp (holdout-only) → {sp} "
                f"status={stamp.get('ab_hard')}"
            )

    if report is not None:
        write_holdout_report(
            report,
            report_path,
            model_path_written
            if isinstance(model_path_written, Path) and model_path_written.is_file()
            else None,
        )
        print(f"[train] report → {report_path}")

    if report is not None and args.require_ab_hard:
        g = report.get("gates") or {}
        if not _hard_gates_ok(g):
            print(
                "[train] FAIL: AB-hard-LOI / AB-hard-LOP / P-LOI-reg — EXIT 3",
                file=sys.stderr,
            )
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
