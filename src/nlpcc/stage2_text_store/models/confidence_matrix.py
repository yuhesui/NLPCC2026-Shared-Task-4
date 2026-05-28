"""Confidence matrix construction for quantified text views."""

from __future__ import annotations

from nlpcc.stage2_text_store.schema import BLViewRecord, ConfidenceMatrix


def clamp_confidence(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def build_confidence_matrix(
    bl_views: tuple[BLViewRecord, ...],
    *,
    min_confidence: float = 0.0,
    max_confidence: float = 1.0,
) -> ConfidenceMatrix:
    """Build a diagonal confidence matrix keyed by BL asset group."""

    grouped: dict[str, list[float]] = {}
    for view in bl_views:
        grouped.setdefault(view.asset_group, []).append(view.confidence)

    labels = tuple(sorted(grouped))
    rows: list[tuple[float, ...]] = []
    for row_label in labels:
        row: list[float] = []
        for col_label in labels:
            if row_label == col_label:
                average = sum(grouped[row_label]) / len(grouped[row_label])
                row.append(round(clamp_confidence(average, min_confidence, max_confidence), 8))
            else:
                row.append(0.0)
        rows.append(tuple(row))
    return ConfidenceMatrix(labels=labels, values=tuple(rows))
