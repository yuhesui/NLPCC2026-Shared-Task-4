#!/usr/bin/env python3
"""Run prompt11 repository verification audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.verification.verification_suite import run_verification_suite, write_verification_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run import, leakage, data, dependency, and docs verification audits.")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "outputs" / "reports" / "prompt11"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_verification_suite(REPO_ROOT)
    artifacts = write_verification_outputs(report, output_dir=Path(args.output_dir))
    print(json.dumps({"status": "ok", "artifacts": artifacts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
