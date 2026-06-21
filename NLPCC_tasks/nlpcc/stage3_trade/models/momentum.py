"""Price momentum features and long-only weights."""

from __future__ import annotations

from nlpcc.stage3_trade.models.equal_weight_state import equal_weight, normalize_weights


def momentum_score(closes: list[float] | tuple[float, ...], window: int = 20) -> float:
    values = [float(value) for value in closes if value is not None and float(value) > 0]
    if len(values) < 2:
        return 0.0
    lookback = min(max(1, window), len(values) - 1)
    start = values[-lookback - 1]
    if start == 0:
        return 0.0
    return (values[-1] / start) - 1.0


def blended_momentum_score(closes: list[float] | tuple[float, ...], windows: tuple[int, ...]) -> float:
    if not windows:
        return momentum_score(closes)
    scores = [momentum_score(closes, window=window) for window in windows]
    return sum(scores) / len(scores)


def momentum_weights(
    close_by_fund: dict[str, list[float] | tuple[float, ...]],
    *,
    windows: tuple[int, ...] = (20, 60),
    total: float = 1.0,
) -> dict[str, float]:
    scores = {fund_id: max(0.0, blended_momentum_score(closes, windows)) for fund_id, closes in close_by_fund.items()}
    weights = normalize_weights(scores, total)
    return weights or equal_weight(close_by_fund, total=total)
