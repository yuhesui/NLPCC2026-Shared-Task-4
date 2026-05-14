"""Rule-based macro rotation baseline."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.data.features import momentum_breadth
from nlpcc4.data.news_features import news_sentiment_score
from nlpcc4.execution.constraints import project_long_only
from nlpcc4.strategies.track1_macro.universe import (
    TRACK1_COMMODITY_ASSETS,
    TRACK1_DEFENSIVE_ASSETS,
    TRACK1_GROWTH_ASSETS,
    TRACK1_UNIVERSE,
)


def rule_based_macro_targets(
    historical_prices: Mapping[str, Sequence[Mapping]],
    news: Sequence[Mapping],
    fund_pool: Sequence[str] = TRACK1_UNIVERSE,
    *,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
) -> dict[str, float]:
    """Simple deterministic macro rotation baseline."""
    breadth = momentum_breadth(historical_prices, 20)
    sentiment = news_sentiment_score(news)
    defensive = tuple(asset for asset in TRACK1_DEFENSIVE_ASSETS if asset in fund_pool)
    growth = tuple(asset for asset in TRACK1_GROWTH_ASSETS if asset in fund_pool)
    commodity = tuple(asset for asset in TRACK1_COMMODITY_ASSETS if asset in fund_pool)
    raw = {asset: 1.0 for asset in fund_pool}
    if sentiment < -0.2 or breadth < 0.35:
        for asset in defensive:
            raw[asset] += 3.0
    elif sentiment > 0.2 and breadth > 0.55:
        for asset in growth:
            raw[asset] += 2.0
    else:
        for asset in commodity:
            raw[asset] += 1.2
    return project_long_only(raw, universe=fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
