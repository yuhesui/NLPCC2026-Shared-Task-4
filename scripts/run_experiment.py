#!/usr/bin/env python3
"""Run a JSON experiment suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.experiments.experiment_config import ExperimentSuiteConfig  # noqa: E402
from tools.experiments.runner import run_suite  # noqa: E402
from tools.reporting.experiment_report import write_experiment_report_artifacts  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local experiment suite.")
    parser.add_argument("--config", default=str(REPO_ROOT / "configs" / "tools" / "experiments" / "prompt10_ablation_suite.json"))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--report-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(Path(args.config).read_text(encoding="utf-8"))
    suite = ExperimentSuiteConfig.from_mapping(payload)
    output_dir = Path(args.output_dir) if args.output_dir else None
    results = run_suite(suite, output_dir=output_dir)
    report_dir = Path(args.report_dir) if args.report_dir else suite.report_dir
    artifacts = write_experiment_report_artifacts(
        results=results,
        report_dir=report_dir,
        title=f"{suite.name} Report",
    )
    print(json.dumps({"suite": suite.name, "runs": len(results), "artifacts": artifacts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
