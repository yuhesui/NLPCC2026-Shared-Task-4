"""Sharpe-ratio utilities."""

from __future__ import annotations

from statistics import mean, pstdev


def daily_returns(equity_curve: list[float]) -> list[float]:
    """Convert an equity curve into simple daily returns."""
    returns: list[float] = []
    for previous, current in zip(equity_curve, equity_curve[1:]):
        if previous > 0:
            returns.append(current / previous - 1.0)
    return returns


def annualized_sharpe(returns: list[float], risk_free_rate: float = 0.0, periods: int = 252) -> float:
    """Compute annualized Sharpe ratio with population volatility."""
    clean = [float(value) for value in returns if value == value]
    if len(clean) < 2:
        return 0.0
    sigma = pstdev(clean)
    if sigma <= 1e-12:
        return 0.0
    daily_rf = risk_free_rate / periods
    return (mean(clean) - daily_rf) / sigma * (periods ** 0.5)


def sharpe_ratio(returns: list[float]) -> float:
    """Backward-compatible alias for annualized Sharpe."""
    return annualized_sharpe(returns)
