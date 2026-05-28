"""Black-Litterman view storage from Stage 1 view signals."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from nlpcc.stage1_news.schema import Stage1Output
from nlpcc.stage2_text_store.schema import BLViewRecord


def _view_id(asset_group: str, direction: str) -> str:
    return f"{asset_group}:{direction}".replace(" ", "_").lower()


@dataclass
class _ViewAccumulator:
    expected_return_total: float = 0.0
    confidence_total: float = 0.0
    count: int = 0
    rationale: str = ""


def build_bl_view_store(stage1_output: Stage1Output | None) -> tuple[BLViewRecord, ...]:
    """Deduplicate and average Stage 1 BL views by asset group and direction."""

    if stage1_output is None:
        return ()

    buckets: dict[tuple[str, str], _ViewAccumulator] = defaultdict(_ViewAccumulator)
    for view in stage1_output.bl_views:
        key = (view.asset_group, view.direction)
        bucket = buckets[key]
        bucket.expected_return_total += view.expected_return_bps
        bucket.confidence_total += view.confidence
        bucket.count += 1
        if not bucket.rationale:
            bucket.rationale = view.rationale

    records: list[BLViewRecord] = []
    for asset_group, direction in sorted(buckets):
        bucket = buckets[(asset_group, direction)]
        count = max(1, bucket.count)
        records.append(
            BLViewRecord(
                view_id=_view_id(asset_group, direction),
                asset_group=asset_group,
                direction=direction,
                expected_return_bps=round(bucket.expected_return_total / count, 8),
                confidence=round(bucket.confidence_total / count, 8),
                rationale=bucket.rationale,
                source_count=count,
            )
        )
    return tuple(records)
