#!/usr/bin/env python3
"""Generate missing manual LLM prompts without running trades."""

from __future__ import annotations

import argparse
import json

from nlpcc4.backtest.runner import RunRequest, run_strategy_request
from nlpcc4.common.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config, overrides={"strategy": {"name": args.strategy, "track": args.track}, "llm": {"mode": "manual"}})
    result = run_strategy_request(
        RunRequest(
            track=args.track,
            strategy_name=args.strategy,
            config=config,
            config_path=args.config,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output_dir,
            llm_mode="manual",
            run_id=args.run_id,
            dry_run=True,
            prompt_only=True,
        )
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
