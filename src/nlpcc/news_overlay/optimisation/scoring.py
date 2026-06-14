"""Robust Prompt02 scoring."""

from __future__ import annotations

from statistics import mean, pstdev


def robust_score(
    sharpes: list[float],
    *,
    max_drawdowns: list[float],
    turnovers: list[float],
    no_news_sharpe: float,
    ranks: list[float] | None = None,
) -> float:
    """Score a candidate with robustness penalties, not raw Sharpe only."""

    if not sharpes:
        return -999.0
    sharpe_mean = mean(sharpes)
    sharpe_std = pstdev(sharpes) if len(sharpes) > 1 else 0.0
    drawdown_penalty = max(0.0, mean(max_drawdowns) - 0.12) * 4.0
    turnover_penalty = max(0.0, mean(turnovers) - 0.006) * 30.0
    underperf_penalty = max(0.0, no_news_sharpe - sharpe_mean)
    instability_penalty = (pstdev(ranks) / 10.0) if ranks and len(ranks) > 1 else 0.0
    return round(
        sharpe_mean
        - 0.40 * sharpe_std
        - 0.25 * drawdown_penalty
        - 0.15 * turnover_penalty
        - 0.20 * underperf_penalty
        - 0.10 * instability_penalty,
        6,
    )
