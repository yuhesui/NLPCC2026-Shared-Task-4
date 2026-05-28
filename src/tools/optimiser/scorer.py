"""Scoring utilities for optimiser outputs."""

from __future__ import annotations

from typing import Any, Iterable


def score_metrics(
    metrics: dict[str, float],
    *,
    sharpe_weight: float = 1.0,
    return_weight: float = 0.25,
    drawdown_penalty: float = 0.5,
    turnover_penalty: float = 0.1,
) -> float:
    return (
        (sharpe_weight * float(metrics.get("sharpe_ratio", 0.0)))
        + (return_weight * float(metrics.get("cumulative_return", 0.0)))
        - (drawdown_penalty * float(metrics.get("max_drawdown", 0.0)))
        - (turnover_penalty * float(metrics.get("turnover", 0.0)))
    )


def attach_scores(results: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for result in results:
        item = dict(result)
        item["score"] = score_metrics(item.get("metrics", {}))
        scored.append(item)
    return scored


def rank_results(results: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(attach_scores(results), key=lambda item: (-item["score"], str(item.get("params", {}))))
