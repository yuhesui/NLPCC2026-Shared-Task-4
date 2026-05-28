"""Flat feature-table aggregation for Stage 2."""

from __future__ import annotations

from collections import Counter, defaultdict

from nlpcc.stage1_news.schema import Stage1Output
from nlpcc.stage2_text_store.schema import FlatFeatureRow


def _confidence_average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 8)


def _signed(direction: str) -> float:
    if direction == "positive":
        return 1.0
    if direction == "negative":
        return -1.0
    return 0.0


def _row(name: str, value: float, confidence: float, source_count: int, date_int: int | None) -> FlatFeatureRow:
    return FlatFeatureRow(
        feature_name=name,
        value=round(float(value), 8),
        confidence=round(float(confidence), 8),
        source_count=source_count,
        date_int=date_int,
    )


def build_flat_feature_table(stage1_output: Stage1Output | None, *, date_int: int | None = None) -> tuple[FlatFeatureRow, ...]:
    """Aggregate Stage 1 output into stable scalar features."""

    if stage1_output is None:
        return ()

    rows: list[FlatFeatureRow] = [
        _row("news.item_count", len(stage1_output.items), 1.0, len(stage1_output.items), date_int),
        _row("news.event_count", len(stage1_output.events), 1.0, len(stage1_output.events), date_int),
        _row("news.bl_view_count", len(stage1_output.bl_views), 1.0, len(stage1_output.bl_views), date_int),
    ]

    sentiment_counts = Counter(signal.label for signal in stage1_output.sentiments)
    sentiment_confidences: dict[str, list[float]] = defaultdict(list)
    for signal in stage1_output.sentiments:
        sentiment_confidences[signal.label].append(signal.confidence)
    for label in ("positive", "negative", "neutral"):
        rows.append(
            _row(
                f"sentiment.{label}_count",
                sentiment_counts.get(label, 0),
                _confidence_average(sentiment_confidences[label]),
                sentiment_counts.get(label, 0),
                date_int,
            )
        )

    for impact in sorted(stage1_output.sector_impacts, key=lambda item: item.sector):
        signed_intensity = _signed(impact.direction) * impact.intensity
        rows.append(
            _row(
                f"sector.{impact.sector}.signed_intensity",
                signed_intensity,
                impact.confidence,
                impact.evidence_count,
                date_int,
            )
        )

    for view in sorted(stage1_output.bl_views, key=lambda item: (item.asset_group, item.direction)):
        rows.append(
            _row(
                f"bl.{view.asset_group}.expected_return_bps",
                view.expected_return_bps,
                view.confidence,
                1,
                date_int,
            )
        )
    return tuple(rows)
