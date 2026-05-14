#!/usr/bin/env python3
"""Run one named ablation variant."""

from __future__ import annotations

import argparse
import json

from nlpcc4.backtest.runner import RunRequest, run_strategy_request
from nlpcc4.common.config import load_config
from nlpcc4.experiments.ablations import build_ablation_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--ablation", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--llm-mode", choices=["off", "manual", "api"], default="off")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = build_ablation_config(load_config(args.config), args.ablation)
    config["strategy"] = {"name": args.strategy, "track": args.track, "ablation": args.ablation}
    config["llm"]["mode"] = args.llm_mode
    result = run_strategy_request(
        RunRequest(
            track=args.track,
            strategy_name=args.strategy,
            config=config,
            config_path=args.config,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output_dir,
            llm_mode=args.llm_mode,
            run_id=args.run_id,
            dry_run=args.dry_run,
        )
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
