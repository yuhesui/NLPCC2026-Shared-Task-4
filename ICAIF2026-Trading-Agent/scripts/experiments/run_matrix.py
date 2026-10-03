#!/usr/bin/env python3
"""Expand the experiment matrix and run every runnable experiment; write a report.

  python scripts/experiments/run_matrix.py [--families quant_baselines,text_ablations] [--limit N]

On the default (synthetic) data this is a PLUMBING run: results are graded
`synthetic_plumbing` and say nothing about real-market value.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from icaif.core.config import REPO_ROOT, load_config
from icaif.core.time import utc_now
from icaif.experiments.matrix import expand_matrix
from icaif.experiments.registry import ExperimentRegistry
from icaif.experiments.reporting import markdown_table
from icaif.experiments.runner import run_experiment


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matrix", default="configs/experiments/initial_matrix.yaml")
    p.add_argument("--families", default="")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--registry", default=str(REPO_ROOT / "outputs" / "experiments"))
    p.add_argument("--report", default=str(REPO_ROOT / "outputs" / "reports" / "matrix_report.md"))
    args = p.parse_args()
    matrix = load_config(args.matrix)
    fams = set(filter(None, args.families.split(","))) or None
    registry = ExperimentRegistry(Path(args.registry))
    rows, failures = [], []
    for i, (family, exp) in enumerate(expand_matrix(matrix, families=fams)):
        if args.limit and i >= args.limit:
            break
        try:
            out = run_experiment({"experiment": exp}, registry=registry)
            rows.append(out)
            m = out["metrics"]
            fb = int(out["summary"].get("fallback_rounds", 0))
            flag = f"  WARNING fallback_rounds={fb}" if fb else ""
            print(f"{out['experiment_id']:<70} CR={m['cumulative_return']:+.4f} SR={m['sharpe_ratio']:+.2f} "
                  f"MDD={m['maximum_drawdown']:.4f} TO={m['turnover']:.4f}{flag}")
        except Exception as error:  # noqa: BLE001 - report and continue; failures listed in the report
            failures.append({"family": family, "name": exp.get("name"), "error": f"{type(error).__name__}: {error}"})
            print(f"FAILED {family}/{exp.get('name')}: {error}")
    ids = {r["experiment_id"] for r in rows}
    records = [r for r in registry.load_all() if r["experiment_id"] in ids]
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# Experiment matrix run ({utc_now().isoformat()})", "", markdown_table(records), ""]
    if failures:
        body += ["## Failures", "", "```json", json.dumps(failures, indent=2), "```"]
    report.write_text("\n".join(body), encoding="utf-8")
    print(f"\n{len(rows)} ok, {len(failures)} failed -> {report}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
