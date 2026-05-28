"""Inverse-volatility risk anchor."""

from __future__ import annotations

import math

from nlpcc.stage3_trade.models.equal_weight_state import equal_weight, normalize_weights


def sample_volatility(returns: list[float] | tuple[float, ...], floor: float = 1e-6) -> float:
    if len(returns) < 2:
        return floor
    mean = sum(returns) / len(returns)
    variance = sum((value - mean) ** 2 for value in returns) / (len(returns) - 1)
    return max(math.sqrt(variance), floor)


def inverse_volatility_weights(
    returns_by_fund: dict[str, list[float] | tuple[float, ...]],
    *,
    total: float = 1.0,
    floor: float = 1e-6,
) -> dict[str, float]:
    if not returns_by_fund:
        return {}
    raw = {
        fund_id: 1.0 / sample_volatility(tuple(returns), floor=floor)
        for fund_id, returns in returns_by_fund.items()
    }
    weights = normalize_weights(raw, total)
    return weights or equal_weight(returns_by_fund, total=total)
