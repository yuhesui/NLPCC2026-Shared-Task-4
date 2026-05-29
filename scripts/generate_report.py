#!/usr/bin/env python3
"""Generate report artifacts from experiment result JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.reporting.experiment_report import write_experiment_report_artifacts  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown/CSV/text figures from experiment JSON results.")
    parser.add_argument("--input-dir", default=str(REPO_ROOT / "outputs" / "experiments" / "prompt10"))
    parser.add_argument("--report-dir", default=str(REPO_ROOT / "outputs" / "reports" / "prompt10"))
    parser.add_argument("--title", default="Prompt10 Ablation Report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(input_dir.glob("*.json"))]
    artifacts = write_experiment_report_artifacts(results=results, report_dir=Path(args.report_dir), title=args.title)
    print(json.dumps({"runs": len(results), "artifacts": artifacts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
