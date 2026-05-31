"""Stable-effect causal event graph MVP for Stage 2."""

from __future__ import annotations

from typing import Any

from nlpcc.stage2_text_store.schema import EventTableRow

def build_causal_event_graph_stub() -> dict[str, str]:
    return {
        "status": "available_mvp",
        "component": "causal_event_graph",
        "reason": "Use build_causal_event_graph for invariant event-sector impact scores.",
    }


def build_causal_event_graph(event_table: tuple[EventTableRow, ...], *, subwindow_count: int = 4) -> dict[str, Any]:
    """Estimate stable event-type to sector impacts from current text state only."""

    if not event_table:
        return {
            "status": "available_mvp",
            "component": "causal_event_graph",
            "edges": (),
            "stable_impact_by_sector": {},
            "event_count": 0,
        }
    windows: list[list[EventTableRow]] = [[] for _ in range(max(1, subwindow_count))]
    for idx, event in enumerate(event_table):
        windows[idx % len(windows)].append(event)
    grouped: dict[tuple[str, str], list[float]] = {}
    for window in windows:
        partial: dict[tuple[str, str], list[float]] = {}
        for event in window:
            key = (event.event_type, event.sector)
            partial.setdefault(key, []).append(event.signed_intensity * event.confidence)
        for key, values in partial.items():
            grouped.setdefault(key, []).append(sum(values) / max(len(values), 1))
    edges: list[dict[str, Any]] = []
    sector_scores: dict[str, float] = {}
    for (event_type, sector), values in sorted(grouped.items()):
        mean = sum(values) / len(values)
        sign_consistency = sum(1 for value in values if value == 0 or (value > 0) == (mean >= 0)) / len(values)
        stability = max(0.0, min(1.0, sign_consistency * (1.0 / (1.0 + _mean_abs_deviation(values, mean)))))
        edge_score = mean * stability
        edges.append(
            {
                "source": f"event:{event_type}",
                "target": sector,
                "relation": "stable_event_impact",
                "impact": round(mean, 8),
                "stability": round(stability, 8),
                "score": round(edge_score, 8),
                "window_count": len(values),
            }
        )
        sector_scores[sector] = sector_scores.get(sector, 0.0) + edge_score
    return {
        "status": "available_mvp",
        "component": "causal_event_graph",
        "edges": tuple(edges),
        "stable_impact_by_sector": {key: round(value, 8) for key, value in sector_scores.items()},
        "event_count": len(event_table),
        "subwindow_count": len(windows),
    }


def _mean_abs_deviation(values: list[float], mean: float) -> float:
    return sum(abs(value - mean) for value in values) / max(len(values), 1)
