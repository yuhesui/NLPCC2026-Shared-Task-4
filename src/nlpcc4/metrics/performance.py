"""Performance metric aggregation."""

from __future__ import annotations

from nlpcc4.metrics.drawdown import max_drawdown
from nlpcc4.metrics.sharpe import annualized_sharpe, daily_returns
from nlpcc4.metrics.turnover import average_turnover, total_turnover


def cumulative_return(equity_curve: list[float]) -> float:
    """Return total cumulative return."""
    if len(equity_curve) < 2 or equity_curve[0] <= 0:
        return 0.0
    return equity_curve[-1] / equity_curve[0] - 1.0


def concentration(weights: dict[str, float]) -> float:
    """Herfindahl concentration for a weight vector."""
    return sum(float(value) ** 2 for value in weights.values())


def estimate_cost_drag(turnovers: list[float], friction: float = 0.0001) -> float:
    """Estimate return drag from one-way turnover and transaction friction."""
    return total_turnover(turnovers) * friction


def summarize_performance(
    equity_curve: list[float],
    *,
    turnovers: list[float] | None = None,
    risk_free_rate: float = 0.0,
    friction: float = 0.0001,
    final_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Summarize an equity curve with deterministic Phase 1a metrics."""
    turnovers = turnovers or []
    returns = daily_returns(equity_curve)
    return {
        "cumulative_return": cumulative_return(equity_curve),
        "annualized_sharpe": annualized_sharpe(returns, risk_free_rate=risk_free_rate),
        "max_drawdown": max_drawdown(equity_curve),
        "average_daily_turnover": average_turnover(turnovers),
        "total_turnover": total_turnover(turnovers),
        "cost_drag_estimate": estimate_cost_drag(turnovers, friction=friction),
        "concentration": concentration(final_weights or {}),
        "num_days": float(max(len(equity_curve) - 1, 0)),
    }
