#!/usr/bin/env python3
"""CLI wrapper for ``src.tools.utils.implementation_log``."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.utils.implementation_log import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    ImplementationLog,
    create_implementation_log,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a prompt implementation log.")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--files", required=True)
    parser.add_argument("--tests", required=True)
    parser.add_argument("--caveats", required=True)
    parser.add_argument("--next-steps", required=True)
    parser.add_argument(
        "--artifacts",
        default="",
        help="Optional comma-separated artifact paths recorded in the log.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for implementation logs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifacts = tuple(item.strip() for item in args.artifacts.split(",") if item.strip())
    log = ImplementationLog(
        prompt_id=args.prompt_id,
        phase=args.phase,
        summary=args.summary,
        files=args.files,
        tests=args.tests,
        caveats=args.caveats,
        next_steps=args.next_steps,
        artifacts=artifacts,
    )
    path = create_implementation_log(log, output_dir=args.output_dir)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

