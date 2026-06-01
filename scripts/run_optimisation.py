#!/usr/bin/env python3
"""Run a bounded Prompt16 optimisation smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.optimiser.five_fold_split import load_combined_trading_dates, make_five_fold_80_20_splits  # noqa: E402
from tools.optimiser.optimisation_engine import run_five_fold_optimisation  # noqa: E402
from tools.optimiser.parameter_space import prompt16_default_parameter_spaces  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bounded Prompt16 optimisation smoke.")
    parser.add_argument("--strategy", default="dro_bl_rp")
    parser.add_argument("--max-candidates", type=int, default=2)
    parser.add_argument("--output", default=str(REPO_ROOT / ".var" / "prompt16" / "smoke_results" / "optimisation_smoke.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dates = load_combined_trading_dates([REPO_ROOT / "data" / "train_2024", REPO_ROOT / "data" / "public_a_2025"])
    folds = make_five_fold_80_20_splits(dates)
    spaces = prompt16_default_parameter_spaces()
    if args.strategy not in spaces:
        raise SystemExit(f"Unknown strategy space: {args.strategy}")

    def objective(params, fold):
        tau = float(params.get("tau", 0.05))
        validation_size_penalty = len(fold.validation_dates) / max(1, len(dates))
        return {
            "status": "ok",
            "metrics": {
                "sharpe_ratio": 1.0 - abs(tau - 0.05) - validation_size_penalty,
                "cumulative_return": 0.05,
                "max_drawdown": 0.10,
                "turnover": 0.05,
            },
        }

    rows = run_five_fold_optimisation(
        spaces[args.strategy],
        folds,
        objective,
        max_candidates=args.max_candidates,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"status": "ok", "strategy": args.strategy, "rows": rows}, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "rows": len(rows), "output": str(output_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
