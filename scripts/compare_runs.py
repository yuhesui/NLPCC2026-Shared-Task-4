#!/usr/bin/env python3
"""CLI stub for future run comparison."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default=".var/runs")
    parser.add_argument("--metric", default="sharpe")
    args = parser.parse_args()
    print(
        "PLANNED - not implemented yet: compare runs "
        f"in {args.runs_dir} by {args.metric}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
