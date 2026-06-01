#!/usr/bin/env python3
"""Generate Prompt17 SystemRunner target tensors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.experiments.candidate_factory import build_prompt17_candidates  # noqa: E402
from tools.experiments.target_tensor_generator import TargetTensorGenerationRequest, generate_target_tensor  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate official-semantics target tensors through SystemRunner.")
    parser.add_argument("--track", choices=["macro", "sector"], default="macro")
    parser.add_argument("--data-root", default=str(REPO_ROOT / "data" / "train_2024"))
    parser.add_argument("--output-root", default=str(REPO_ROOT / ".var" / "prompt17"))
    parser.add_argument("--max-dates", type=int, default=20)
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    per_track = max(1, int(args.max_candidates)) if args.max_candidates else None
    candidates = [
        item.with_stage1_cache(Path(args.output_root) / "text_feature_cache")
        for item in build_prompt17_candidates(repo_root=REPO_ROOT, max_per_track=per_track)
        if item.track == args.track
    ][: args.max_candidates]
    result = generate_target_tensor(
        TargetTensorGenerationRequest(
            repo_root=REPO_ROOT,
            data_root=Path(args.data_root),
            track=args.track,  # type: ignore[arg-type]
            candidates=candidates,
            output_root=Path(args.output_root),
            max_dates=args.max_dates,
            lookback_days=args.lookback_days,
            force=args.force,
        )
    )
    print(json.dumps({"status": "ok", "result": result.as_dict()}, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
