"""Pre-decision and pre-submission safety checks.

Each check returns a list of issue codes; the agent turns issues into
explicit fallback events (never silently ignored).
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np

from icaif.portfolio.constraints import Constraints, constraint_violations
from icaif.runtime.state import DecisionContext


def input_issues(ctx: DecisionContext, *, max_staleness: timedelta, min_bars: int) -> list[str]:
    issues: list[str] = []
    view = ctx.market_state
    if view.as_of != ctx.decision_time:
        issues.append("view_as_of_mismatch")
    if ctx.decision_time >= ctx.deadline:
        issues.append("decision_time_after_deadline")
    if view.n_bars < min_bars:
        issues.append("insufficient_history")
    stale = view.staleness()
    if stale is None or stale > max_staleness:
        issues.append("stale_market_data")
    last = view.last_close()
    if not np.isfinite(last).all():
        issues.append("missing_prices")
    cw = np.asarray(ctx.current_weights, dtype=float)
    if not np.isfinite(cw).all() or (cw < -1e-9).any() or cw.sum() > 1.0 + 1e-6:
        issues.append("inconsistent_portfolio_state")
    if not np.isfinite(ctx.nav_estimate) or ctx.nav_estimate <= 0:
        issues.append("invalid_nav")
    return issues


def output_issues(target: np.ndarray, current: np.ndarray, *, cons: Constraints, max_turnover: float) -> list[str]:
    issues = constraint_violations(target, cons)
    if not issues and float(np.abs(target - current).sum()) > max_turnover + 1e-12:
        issues.append("turnover_above_hard_limit")
    return issues
