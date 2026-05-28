"""Stage 3 model registry."""

from __future__ import annotations

from typing import Callable

from nlpcc.stage3_trade.models.breadth import breadth_score
from nlpcc.stage3_trade.models.covariance import sample_covariance
from nlpcc.stage3_trade.models.drawdown import max_drawdown_from_prices
from nlpcc.stage3_trade.models.equal_weight_state import equal_weight
from nlpcc.stage3_trade.models.inverse_volatility import inverse_volatility_weights
from nlpcc.stage3_trade.models.momentum import momentum_weights
from nlpcc.stage3_trade.models.sector_trend import sector_trend_weights
from nlpcc.stage3_trade.models.shrinkage_covariance import shrink_covariance
from nlpcc.stage3_trade.models.turnover_state import one_way_turnover


STAGE3_MODELS: dict[str, Callable] = {
    "equal_weight": equal_weight,
    "inverse_volatility": inverse_volatility_weights,
    "momentum": momentum_weights,
    "sector_trend": sector_trend_weights,
    "covariance": sample_covariance,
    "shrinkage_covariance": shrink_covariance,
    "drawdown": max_drawdown_from_prices,
    "breadth": breadth_score,
    "turnover": one_way_turnover,
}


def get_stage3_model(name: str) -> Callable:
    try:
        return STAGE3_MODELS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown Stage 3 model: {name!r}") from exc
