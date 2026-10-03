#!/usr/bin/env python3
"""Build weakly-labelled (article, asset) pairs with hard negatives (FINETUNING_PLAN Stage B).

  python scripts/train/build_relevance_pairs.py --news data/raw/news/*.jsonl --out data/processed/pairs.jsonl \
      --train-end 2026-06-30T20:00:00+00:00
  python scripts/train/build_relevance_pairs.py --synthetic --out /tmp/pairs.jsonl   # plumbing check

Only articles available before --train-end are used; the manifest hash is printed for the registry.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

from icaif.core.schemas import content_hash
from icaif.core.time import parse_timestamp
from icaif.data.market.synthetic import generate_synthetic_world
from icaif.data.news.sources import JsonlNewsSource
from icaif.models.text.pairs import build_pairs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--news", nargs="*", default=[])
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--train-end", default="2100-01-01T00:00:00+00:00")
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    end = parse_timestamp(args.train_end)
    if args.synthetic:
        articles = generate_synthetic_world().articles
    else:
        src = JsonlNewsSource("local", [Path(x) for x in args.news], latency=timedelta(minutes=5))
        articles = src.fetch(parse_timestamp("1900-01-01T00:00:00+00:00"), end)
    articles = [a for a in articles if a.available_at <= end]
    pairs = build_pairs(articles, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(asdict(x)) for x in pairs) + "\n", encoding="utf-8")
    kinds: dict[str, int] = {}
    for x in pairs:
        kinds[x.negative_type] = kinds.get(x.negative_type, 0) + 1
    print(json.dumps({"pairs": len(pairs), "by_type": kinds, "manifest_hash": content_hash([asdict(x) for x in pairs])[:16],
                      "synthetic": args.synthetic}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
