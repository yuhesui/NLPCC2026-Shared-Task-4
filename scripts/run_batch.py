#!/usr/bin/env python3
"""Run a small batch of strategy names over one track/config period."""

from __future__ import annotations

import argparse
import json

from nlpcc4.backtest.runner import RunRequest, run_strategy_request
from nlpcc4.common.config import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], required=True)
    parser.add_argument("--strategy", action="append", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--llm-mode", choices=["off", "manual", "api"], default="off")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    results = []
    for strategy_name in args.strategy:
        config = load_config(args.config, overrides={"strategy": {"name": strategy_name, "track": args.track}, "llm": {"mode": args.llm_mode}})
        results.append(
            run_strategy_request(
                RunRequest(
                    track=args.track,
                    strategy_name=strategy_name,
                    config=config,
                    config_path=args.config,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    output_dir=args.output_dir,
                    llm_mode=args.llm_mode,
                    dry_run=args.dry_run,
                )
            )
        )
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
