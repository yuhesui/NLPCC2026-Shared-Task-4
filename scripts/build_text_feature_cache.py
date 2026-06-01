#!/usr/bin/env python3
"""Build bounded Prompt17 Stage 1 text feature caches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.stage1_news.feature_cache import TEXT_FEATURE_MODES, build_text_feature_cache  # noqa: E402
from tools.experiments.leakage_safe_input_builder import LeakageSafeInputBuilder  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Stage 1 feature caches for Prompt17.")
    parser.add_argument("--data-root", default=str(REPO_ROOT / "data" / "train_2024"))
    parser.add_argument("--track", choices=["macro", "sector"], default="macro")
    parser.add_argument("--cache-root", default=str(REPO_ROOT / ".var" / "prompt17" / "text_feature_cache"))
    parser.add_argument("--max-dates", type=int, default=10)
    parser.add_argument("--modes", default=",".join(TEXT_FEATURE_MODES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    builder = LeakageSafeInputBuilder(data_root=Path(args.data_root), track=args.track)  # type: ignore[arg-type]
    dates = builder.selected_dates(max_dates=args.max_dates)
    records = build_text_feature_cache(
        dates=dates,
        news_provider=builder.visible_news,
        cache_path=Path(args.cache_root),
        modes=tuple(item.strip() for item in args.modes.split(",") if item.strip()),
    )
    payload = {
        "status": "ok",
        "track": args.track,
        "data_root": args.data_root,
        "cache_root": args.cache_root,
        "date_count": len(dates),
        "record_count": len(records),
        "records": [record.as_dict() for record in records],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
