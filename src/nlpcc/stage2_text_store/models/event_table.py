"""Event-table construction from Stage 1 event tuples."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha1

from nlpcc.stage1_news.schema import EventTuple, Stage1Output
from nlpcc.stage2_text_store.schema import EventTableRow


def signed_direction(direction: str) -> float:
    if direction == "positive":
        return 1.0
    if direction == "negative":
        return -1.0
    return 0.0


def stable_event_id(news_id: str, event_type: str, sector: str, direction: str) -> str:
    raw = "|".join((news_id, event_type, sector, direction)).encode("utf-8")
    return sha1(raw).hexdigest()[:16]


@dataclass
class _Accumulator:
    signed_intensity_total: float = 0.0
    confidence_total: float = 0.0
    duplicate_count: int = 0
    evidence: str = ""


def build_event_table(stage1_output: Stage1Output | None) -> tuple[EventTableRow, ...]:
    """Build a deterministic, sector-expanded event table.

    Duplicate Stage 1 events are merged by ``news_id/event_type/sector/direction``.
    The merged row preserves the average signal and records ``duplicate_count``.
    """

    if stage1_output is None:
        return ()

    accumulators: dict[tuple[str, str, str, str], _Accumulator] = defaultdict(_Accumulator)
    for event in stage1_output.events:
        sectors = event.sectors or ("unknown",)
        for sector in sectors:
            key = (event.news_id, event.event_type, sector, event.direction)
            bucket = accumulators[key]
            bucket.signed_intensity_total += signed_direction(event.direction) * event.intensity
            bucket.confidence_total += event.confidence
            bucket.duplicate_count += 1
            if not bucket.evidence:
                bucket.evidence = event.evidence

    rows: list[EventTableRow] = []
    for news_id, event_type, sector, direction in sorted(accumulators):
        bucket = accumulators[(news_id, event_type, sector, direction)]
        count = max(1, bucket.duplicate_count)
        rows.append(
            EventTableRow(
                event_id=stable_event_id(news_id, event_type, sector, direction),
                news_id=news_id,
                event_type=event_type,
                sector=sector,
                direction=direction,
                signed_intensity=round(bucket.signed_intensity_total / count, 8),
                confidence=round(bucket.confidence_total / count, 8),
                evidence=bucket.evidence,
                duplicate_count=count,
            )
        )
    return tuple(rows)


def event_to_row(event: EventTuple, sector: str) -> EventTableRow:
    """Convert a single Stage 1 event and sector to an event-table row."""

    return EventTableRow(
        event_id=stable_event_id(event.news_id, event.event_type, sector, event.direction),
        news_id=event.news_id,
        event_type=event.event_type,
        sector=sector,
        direction=event.direction,
        signed_intensity=round(signed_direction(event.direction) * event.intensity, 8),
        confidence=round(event.confidence, 8),
        evidence=event.evidence,
    )
