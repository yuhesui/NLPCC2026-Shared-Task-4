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


DEFAULT_SMOKE_ROOT = REPO_ROOT / "data" / "sample" / "smoke_test"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local deterministic smoke backtest.")
    parser.add_argument("--track", choices=["macro", "sector"], default="macro")
    parser.add_argument("--data-root", default=str(DEFAULT_SMOKE_ROOT))
    parser.add_argument("--output", default=str(REPO_ROOT / "outputs" / "smoke_tests" / "local_smoke.json"))
    parser.add_argument(
        "--prepare-smoke-data",
        action="store_true",
        help="Create the synthetic smoke dataset at --data-root before running. The default smoke_test path is prepared automatically.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root = Path(args.data_root)
    should_prepare = args.prepare_smoke_data or data_root.resolve() == DEFAULT_SMOKE_ROOT.resolve()
    if should_prepare:
        create_smoke_subset(data_root)
        validation = validate_smoke_dataset(data_root)
        if not validation["ok"]:
            raise RuntimeError(f"Smoke dataset validation failed: {validation}")
    elif not data_root.exists():
        raise FileNotFoundError(f"Data root does not exist: {data_root}")
    backtester = LocalSmokeBacktester(data_root=data_root, track=args.track)
    result = backtester.run(Path(args.output))
    print(f"{args.output} status={result['status']} final_value={result['final_value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
