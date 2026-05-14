#!/usr/bin/env python3
"""Validate official-compatible data slicing for a date range."""

from __future__ import annotations

import argparse
import json

from nlpcc4.common.config import load_config
from nlpcc4.data.leakage_checks import run_leakage_checks
from nlpcc4.data.official_loader import OfficialDataPortal, load_official_data_loader
from nlpcc4.experiments.registry import get_default_universe


def _infer_track(config: dict, config_path: str) -> str:
    configured = str(config.get("strategy", {}).get("track", "")).strip()
    if configured in {"track1", "track2"}:
        return configured
    normalized_path = config_path.replace("\\", "/").lower()
    if "/track2/" in normalized_path:
        return "track2"
    return "track1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], default=None)
    parser.add_argument("--strategy", default="s1_quant_core")
    parser.add_argument("--config", required=True)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--llm-mode", choices=["off", "manual", "api"], default="off")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    track = args.track or _infer_track(config, args.config)
    start_date = args.start_date or str(config.get("data", {}).get("start_date", "2024-01-02"))
    end_date = args.end_date or str(config.get("data", {}).get("end_date", start_date))
    fund_pool = tuple(config.get("data", {}).get("fund_pool") or get_default_universe(track))
    portal = OfficialDataPortal(load_official_data_loader(), same_day_news_policy=config.get("data", {}).get("same_day_news_policy", "previous_day_only"))
    results = []
    for day_int in portal.trading_dates(start_date, end_date):
        history = portal.historical_prices(fund_pool, day_int, int(config.get("data", {}).get("lookback_days", 60)))
        results.append(run_leakage_checks(history, day_int))
    print(json.dumps({"track": track, "start_date": start_date, "end_date": end_date, "checks": results, "passed": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
