#!/usr/bin/env python3
"""Run the prompt01 local smoke backtest."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.backtesting.local_backtester import LocalSmokeBacktester  # noqa: E402
from tools.data_tools.dataset_mirror import create_smoke_subset  # noqa: E402
from tools.data_tools.dataset_validator import validate_smoke_dataset  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local deterministic smoke backtest.")
    parser.add_argument("--track", choices=["macro", "sector"], default="macro")
    parser.add_argument("--data-root", default=str(REPO_ROOT / "data" / "sample" / "smoke_test"))
    parser.add_argument("--output", default=str(REPO_ROOT / "outputs" / "smoke_tests" / "local_smoke.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root = Path(args.data_root)
    create_smoke_subset(data_root)
    validation = validate_smoke_dataset(data_root)
    if not validation["ok"]:
        raise RuntimeError(f"Smoke dataset validation failed: {validation}")
    backtester = LocalSmokeBacktester(data_root=data_root, track=args.track)
    result = backtester.run(Path(args.output))
    print(f"{args.output} status={result['status']} final_value={result['final_value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
