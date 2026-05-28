"""Backtesting metric utilities."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class BacktestMetrics:
    cumulative_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    turnover: float

    def as_dict(self) -> dict[str, float]:
        return {
            "cumulative_return": self.cumulative_return,
            "annualized_volatility": self.annualized_volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "turnover": self.turnover,
        }


def daily_returns(values: Sequence[float]) -> list[float]:
    returns: list[float] = []
    for previous, current in zip(values, values[1:]):
        if previous == 0:
            continue
        returns.append((current / previous) - 1.0)
    return returns


def cumulative_return(values: Sequence[float]) -> float:
    if len(values) < 2 or values[0] == 0:
        return 0.0
    return (values[-1] / values[0]) - 1.0


def annualized_volatility(returns: Sequence[float], periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    variance = sum((item - mean) ** 2 for item in returns) / (len(returns) - 1)
    return math.sqrt(variance) * math.sqrt(periods_per_year)


def sharpe_ratio(
    returns: Sequence[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    if not returns:
        return 0.0
    vol = annualized_volatility(returns, periods_per_year)
    if vol == 0:
        return 0.0
    mean_daily = sum(returns) / len(returns)
    annualized_excess = (mean_daily * periods_per_year) - risk_free_rate
    return annualized_excess / vol


def max_drawdown(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak == 0:
            continue
        drawdown = (value / peak) - 1.0
        worst = min(worst, drawdown)
    return abs(worst)


def weight_turnover(weight_history: Sequence[dict[str, float]]) -> float:
    """Average one-way turnover from consecutive target/holding weights."""

    if len(weight_history) < 2:
        return 0.0
    turnovers: list[float] = []
    for previous, current in zip(weight_history, weight_history[1:]):
        assets = set(previous) | set(current)
        turnovers.append(0.5 * sum(abs(current.get(asset, 0.0) - previous.get(asset, 0.0)) for asset in assets))
    return sum(turnovers) / len(turnovers)


def transaction_turnover(transactions: Iterable[dict], portfolio_values: Sequence[float]) -> float:
    values = list(portfolio_values)
    if not values:
        return 0.0
    denominator = sum(values) / len(values)
    if denominator == 0:
        return 0.0
    traded = 0.0
    for transaction in transactions:
        amount = transaction.get("amount")
        if amount is None:
            amount = transaction.get("amount_sold", 0.0)
        traded += abs(float(amount or 0.0))
    return traded / denominator


def compute_backtest_metrics(
    portfolio_values: Sequence[float],
    *,
    risk_free_rate: float = 0.0,
    weight_history: Sequence[dict[str, float]] | None = None,
    transactions: Iterable[dict] | None = None,
) -> BacktestMetrics:
    returns = daily_returns(portfolio_values)
    if weight_history is not None:
        turnover_value = weight_turnover(weight_history)
    elif transactions is not None:
        turnover_value = transaction_turnover(transactions, portfolio_values)
    else:
        turnover_value = 0.0
    return BacktestMetrics(
        cumulative_return=cumulative_return(portfolio_values),
        annualized_volatility=annualized_volatility(returns),
        sharpe_ratio=sharpe_ratio(returns, risk_free_rate=risk_free_rate),
        max_drawdown=max_drawdown(portfolio_values),
        turnover=turnover_value,
    )
