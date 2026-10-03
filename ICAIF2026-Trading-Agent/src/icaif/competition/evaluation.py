"""Official ICAIF metric definitions (docs/evaluation.md) and rank scoring.

Re-implemented (not imported) so the backtester has no runtime dependency on
the kit; ``tests/competition/test_evaluation.py`` checks the bundled official
example and, when the kit is present, parity with ``kit.evaluation``.

Periods k = 1..K over non-cancelled rounds:
  B_k  NAV immediately before round k executes (pre-fee)
  E_k  NAV at the period endpoint (immediately before the next rebalance)
  N_k  buy + sell notional of round k (0 when the round held)
  r_k = E_k / B_k - 1
M1 cumulative return  = E_K / B_1 - 1
M2 Sharpe             = 42 * mean(r) / sample_std(r)    (0 if K == 1 or std == 0)
M3 max drawdown       over [initial, every endpoint, every official daily close]
M4 turnover           = mean_k N_k / B_k
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext

from icaif.core.constants import INITIAL_NAV, METRICS_CALCULATION_VERSION

_CTX = Context(prec=40, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class Period:
    nav_before: float
    nav_after_period: float
    traded_notional: float


@dataclass(frozen=True)
class OfficialMetrics:
    cumulative_return: float
    sharpe_ratio: float
    maximum_drawdown: float
    turnover: float
    periods: int
    calculation_version: str = METRICS_CALCULATION_VERSION

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "cumulative_return": self.cumulative_return,
            "sharpe_ratio": self.sharpe_ratio,
            "maximum_drawdown": self.maximum_drawdown,
            "turnover": self.turnover,
            "periods": self.periods,
            "calculation_version": self.calculation_version,
        }


def _d(value: float | str | Decimal) -> Decimal:
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("non-finite NAV/notional")
    return result


def compute_official_metrics(
    periods: Sequence[Period],
    valuation_points: Sequence[float],
    *,
    initial_nav: float = INITIAL_NAV,
    continuity_tolerance: float = 1e-6,
) -> OfficialMetrics:
    """Exact-decimal metrics. ``valuation_points`` starts with the initial NAV and
    contains every period endpoint plus every official daily close, in time order
    (deduplicated by timestamp by the caller)."""

    if not periods:
        raise ValueError("at least one completed period is required")
    with localcontext(_CTX):
        initial = _d(initial_nav)
        points = [_d(v) for v in valuation_points]
        if not points or abs(points[0] - initial) > _d(continuity_tolerance):
            raise ValueError("valuation points must start at the initial NAV")
        previous = initial
        returns: list[Decimal] = []
        ratios: list[Decimal] = []
        for idx, period in enumerate(periods):
            before, end, notional = _d(period.nav_before), _d(period.nav_after_period), _d(period.traded_notional)
            if before <= 0 or end <= 0 or notional < 0:
                raise ValueError(f"period {idx}: NAV must be positive and notional non-negative")
            if abs(before - previous) > _d(continuity_tolerance):
                raise ValueError(f"period {idx}: B_k must equal previous E_(k-1)")
            returns.append(end / before - 1)
            ratios.append(notional / before)
            previous = end
        peak, drawdown = points[0], Decimal(0)
        for value in points[1:]:
            if value <= 0:
                raise ValueError("valuations must be positive")
            peak = max(peak, value)
            drawdown = max(drawdown, (peak - value) / peak)
        count = Decimal(len(returns))
        mean = sum(returns, Decimal(0)) / count
        sharpe = Decimal(0)
        if len(returns) > 1:
            variance = sum(((r - mean) ** 2 for r in returns), Decimal(0)) / (count - 1)
            if variance > 0:
                sharpe = Decimal(1764).sqrt() * mean / variance.sqrt()
        return OfficialMetrics(
            cumulative_return=float(previous / initial - 1),
            sharpe_ratio=float(sharpe),
            maximum_drawdown=float(drawdown),
            turnover=float(sum(ratios, Decimal(0)) / count),
            periods=len(returns),
        )


# ----------------------------------------------------------------------------
# Rank scoring (only meaningful with a comparator population)
# ----------------------------------------------------------------------------

_DIRECTION = {
    "cumulative_return": True,  # higher is better
    "sharpe_ratio": True,
    "maximum_drawdown": False,  # lower is better
    "turnover": False,
}


def _average_ranks(values: Sequence[float], higher_is_better: bool) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: -values[i] if higher_is_better else values[i])
    ranks = [0.0] * len(values)
    pos = 0
    while pos < len(order):
        end = pos
        while end + 1 < len(order) and values[order[end + 1]] == values[order[pos]]:
            end += 1
        avg = (pos + 1 + end + 1) / 2.0
        for j in range(pos, end + 1):
            ranks[order[j]] = avg
        pos = end + 1
    return ranks


def overall_rank_scores(population: Mapping[str, Mapping[str, float]]) -> dict[str, dict[str, float]]:
    """Per-team metric ranks (ties -> average rank) and Overall Rank Score (mean).

    Returns ``{team: {"rank_<metric>": r, ..., "overall_rank_score": s, "position": p}}``
    where position applies the official tie-breaks (higher CR, higher Sharpe,
    lower MDD, lower turnover) and shares positions on exact four-metric ties.
    """

    teams = list(population)
    result: dict[str, dict[str, float]] = {t: {} for t in teams}
    for metric, higher in _DIRECTION.items():
        values = [float(population[t][metric]) for t in teams]
        for team, rank in zip(teams, _average_ranks(values, higher), strict=True):
            result[team][f"rank_{metric}"] = rank
    for team in teams:
        result[team]["overall_rank_score"] = sum(result[team][f"rank_{m}"] for m in _DIRECTION) / len(_DIRECTION)

    def key(team: str) -> tuple[float, ...]:
        m = population[team]
        return (
            result[team]["overall_rank_score"],
            -float(m["cumulative_return"]),
            -float(m["sharpe_ratio"]),
            float(m["maximum_drawdown"]),
            float(m["turnover"]),
        )

    ordered = sorted(teams, key=key)
    for idx, team in enumerate(ordered):
        if idx > 0 and key(team) == key(ordered[idx - 1]):
            result[team]["position"] = result[ordered[idx - 1]]["position"]
        else:
            result[team]["position"] = float(idx + 1)
    return result
