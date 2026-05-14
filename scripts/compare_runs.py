#!/usr/bin/env python3
"""Compare generated run metrics."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from nlpcc4.common.paths import run_root
from nlpcc4.experiments.compare import compare_metric


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", "--runs-dir", default=str(run_root()))
    parser.add_argument("--metric", default="annualized_sharpe")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    rows = compare_metric(args.run_dir, args.metric)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = sorted({key for row in rows for key in row})
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
