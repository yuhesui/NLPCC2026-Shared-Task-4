"""Stable subwindow effect estimator for causal overlays."""

from __future__ import annotations

from typing import Any, Iterable


def estimate_stable_effects(
    event_scores: Iterable[tuple[str, float]],
    *,
    subwindow_count: int = 4,
) -> dict[str, Any]:
    windows: list[dict[str, list[float]]] = [dict() for _ in range(max(1, subwindow_count))]
    for idx, (label, score) in enumerate(event_scores):
        bucket = windows[idx % len(windows)]
        bucket.setdefault(label, []).append(float(score))
    labels = sorted({label for bucket in windows for label in bucket})
    output: dict[str, dict[str, float]] = {}
    for label in labels:
        values = [
            sum(bucket.get(label, [0.0])) / max(len(bucket.get(label, [])), 1)
            for bucket in windows
        ]
        mean = sum(values) / len(values)
        same_sign = sum(1 for value in values if value == 0 or (value > 0) == (mean >= 0)) / len(values)
        dispersion = sum(abs(value - mean) for value in values) / len(values)
        output[label] = {
            "mean_effect": round(mean, 8),
            "stability": round(max(0.0, min(1.0, same_sign / (1.0 + dispersion))), 8),
        }
    return {"status": "available_mvp", "component": "stable_effect_estimator", "effects": output}
