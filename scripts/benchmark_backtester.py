#!/usr/bin/env python3
"""Bounded benchmark for Prompt16 reference and batched backtesters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.execution.order_planner import OrderPlannerConfig  # noqa: E402
from tools.backtesting.backtester_parity import compare_reference_to_candidate  # noqa: E402
from tools.backtesting.cuda_vectorized_backtester import BatchedOfficialSemanticsInput, run_batched_official_semantics  # noqa: E402
from tools.backtesting.reference_official_semantics import (  # noqa: E402
    OfficialSemanticsInput,
    equal_weight_targets,
    load_official_semantics_arrays,
    run_reference_official_semantics,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Prompt16 official-semantics backtesters.")
    parser.add_argument("--track", default="macro")
    parser.add_argument("--max-dates", type=int, default=20)
    parser.add_argument("--candidates", type=int, default=8)
    parser.add_argument("--backend", default="auto", choices=["auto", "torch", "numpy"])
    parser.add_argument("--output", default=str(REPO_ROOT / ".var" / "prompt16" / "benchmarks" / "backtester_benchmark.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dates, assets, open_prices, pct_changes = load_official_semantics_arrays(
        REPO_ROOT / "data" / "train_2024",
        args.track,
        max_dates=args.max_dates,
    )
    planner = OrderPlannerConfig(max_weight=1.0, cash_reserve=0.0, max_turnover=1.0, rebalance_threshold=0.0)
    base_targets = equal_weight_targets(len(dates), len(assets), invested_weight=0.98)
    reference_start = perf_counter()
    reference = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=dates,
            assets=assets,
            open_prices=open_prices,
            pct_changes=pct_changes,
            target_weights=base_targets,
            planner_config=planner,
        )
    )
    reference_seconds = perf_counter() - reference_start

    target_batch = np.stack([base_targets for _ in range(args.candidates)], axis=0)
    batch_start = perf_counter()
    batched = run_batched_official_semantics(
        BatchedOfficialSemanticsInput(
            dates=dates,
            assets=assets,
            open_prices=open_prices,
            pct_changes=pct_changes,
            target_weights=target_batch,
            candidate_names=tuple(f"eq_{index}" for index in range(args.candidates)),
            planner_config=planner,
        ),
        backend=args.backend,
    )
    batch_seconds = perf_counter() - batch_start
    parity = compare_reference_to_candidate(reference, batched.candidates[0], tolerance=1e-5)
    payload = {
        "status": "ok",
        "track": args.track,
        "dates": len(dates),
        "assets": len(assets),
        "candidates": args.candidates,
        "reference_seconds": reference_seconds,
        "batch_seconds": batch_seconds,
        "backend": batched.backend,
        "device": batched.device,
        "speedup_vs_reference_loop": (reference_seconds * args.candidates / batch_seconds) if batch_seconds > 0 else None,
        "parity": parity.as_dict(),
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
