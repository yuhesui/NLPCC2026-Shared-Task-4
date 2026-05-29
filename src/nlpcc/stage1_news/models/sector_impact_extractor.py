"""Aggregate event tuples into sector impacts."""

from __future__ import annotations

from collections import defaultdict

from nlpcc.stage1_news.schema import EventTuple, SectorImpact


def _signed(event: EventTuple) -> float:
    if event.direction == "positive":
        return 1.0
    if event.direction == "negative":
        return -1.0
    return 0.0


def extract_sector_impacts(events: tuple[EventTuple, ...]) -> tuple[SectorImpact, ...]:
    totals: dict[str, float] = defaultdict(float)
    confidence_totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        for sector in event.sectors:
            totals[sector] += _signed(event) * event.intensity * event.confidence
            confidence_totals[sector] += event.confidence
            counts[sector] += 1

    impacts: list[SectorImpact] = []
    for sector in sorted(counts):
        average = totals[sector] / counts[sector]
        direction = "positive" if average > 0.05 else "negative" if average < -0.05 else "neutral"
        impacts.append(
            SectorImpact(
                sector=sector,
                direction=direction,
                intensity=min(1.0, abs(average)),
                confidence=min(1.0, confidence_totals[sector] / counts[sector]),
                evidence_count=counts[sector],
            )
        )
    return tuple(impacts)


def sector_impact_score(impact: SectorImpact) -> float:
    """Signed scalar impact used by Track 2 allocation modules."""

    if impact.direction == "positive":
        return impact.intensity * impact.confidence
    if impact.direction == "negative":
        return -impact.intensity * impact.confidence
    return 0.0
