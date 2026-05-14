#!/usr/bin/env python3
"""Copy a generated run summary into a report path."""

from __future__ import annotations

import argparse
from pathlib import Path

from nlpcc4.common.paths import run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", "--output-dir", required=True)
    args = parser.parse_args()
    source = run_dir(args.run_id) / "run_summary.md"
    if not source.exists():
        raise SystemExit(f"Missing run summary: {source}")
    output = Path(args.output)
    if output.suffix.lower() != ".md":
        output = output / f"{args.run_id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
