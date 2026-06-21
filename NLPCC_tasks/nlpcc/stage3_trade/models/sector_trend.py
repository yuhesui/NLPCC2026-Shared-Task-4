"""Track 2 sector trend baseline features."""

from __future__ import annotations

from nlpcc.stage3_trade.models.breadth import breadth_score
from nlpcc.stage3_trade.models.equal_weight_state import equal_weight, normalize_weights
from nlpcc.stage3_trade.models.momentum import momentum_score


def sector_trend_scores(
    close_by_fund: dict[str, list[float] | tuple[float, ...]],
    returns_by_fund: dict[str, list[float] | tuple[float, ...]],
    *,
    trend_window: int = 20,
    breadth_window: int = 20,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for fund_id, closes in close_by_fund.items():
        momentum_component = momentum_score(closes, window=trend_window)
        breadth_component = breadth_score(returns_by_fund.get(fund_id, ()), window=breadth_window) - 0.5
        scores[fund_id] = momentum_component + breadth_component
    return scores


def sector_trend_weights(
    close_by_fund: dict[str, list[float] | tuple[float, ...]],
    returns_by_fund: dict[str, list[float] | tuple[float, ...]],
    *,
    trend_window: int = 20,
    breadth_window: int = 20,
    total: float = 1.0,
) -> dict[str, float]:
    scores = sector_trend_scores(
        close_by_fund,
        returns_by_fund,
        trend_window=trend_window,
        breadth_window=breadth_window,
    )
    positive = {fund_id: max(0.0, score) for fund_id, score in scores.items()}
    weights = normalize_weights(positive, total)
    return weights or equal_weight(close_by_fund, total=total)
