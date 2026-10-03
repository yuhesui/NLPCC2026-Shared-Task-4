"""ICAIF portfolio constraints and projections.

Feasible set:  0 <= w_i <= 0.30,  sum_i w_i <= g <= 1  (residual = cash).

Two projections are provided:

* :func:`project_capped_simplex` — exact Euclidean projection onto
  ``{0 <= w <= cap, sum w = total}`` (bisection on the shift ``tau``).
* :func:`scale_to_capped_simplex` — AlphaAllocator's proportional
  water-filling (``project_long_only_capped_vector``): scale positive scores to
  ``total`` and redistribute capped excess proportionally. Ported with one
  deliberate change: all-zero scores no longer become equal weight silently;
  the caller chooses ``on_zero="cash"`` (zeros) or ``"equal"`` or ``"raise"``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.core.constants import MAX_GROSS, MAX_WEIGHT


class ZeroSignalError(ValueError):
    pass


@dataclass(frozen=True)
class Constraints:
    max_weight: float = MAX_WEIGHT
    max_gross: float = MAX_GROSS
    min_gross: float = 0.0

    def __post_init__(self) -> None:
        if not 0 < self.max_weight <= MAX_WEIGHT:
            raise ValueError("max_weight must be in (0, 0.30] for ICAIF")
        if not 0 <= self.min_gross <= self.max_gross <= MAX_GROSS:
            raise ValueError("require 0 <= min_gross <= max_gross <= 1")


def project_capped_simplex(v: np.ndarray, cap: float, total: float, *, tol: float = 1e-12) -> np.ndarray:
    """argmin ||w - v||^2  s.t. 0 <= w <= cap, sum w = total (exact)."""

    v = np.asarray(v, dtype=float)
    n = v.size
    if not np.isfinite(v).all():
        raise ValueError("projection input contains non-finite values")
    if total < -tol or total > n * cap + tol:
        raise ValueError(f"infeasible total {total} for n={n}, cap={cap}")
    total = float(np.clip(total, 0.0, n * cap))
    lo, hi = float(v.min() - cap - 1.0), float(v.max() + 1.0)
    for _ in range(200):
        tau = 0.5 * (lo + hi)
        s = np.clip(v - tau, 0.0, cap).sum()
        if s > total:
            lo = tau
        else:
            hi = tau
        if hi - lo < tol:
            break
    w = np.clip(v - 0.5 * (lo + hi), 0.0, cap)
    # remove residual bisection error on the free coordinates
    free = (w > 0) & (w < cap)
    if free.any():
        w[free] += (total - w.sum()) / free.sum()
        w = np.clip(w, 0.0, cap)
    return w


def project_to_feasible(v: np.ndarray, cons: Constraints, *, gross: float | None = None) -> np.ndarray:
    """Euclidean projection onto ``{0 <= w <= cap, min_gross <= sum w <= g}``."""

    g = cons.max_gross if gross is None else float(np.clip(gross, 0.0, cons.max_gross))
    w = np.clip(np.asarray(v, dtype=float), 0.0, cons.max_weight)
    s = w.sum()
    if s > g + 1e-12:
        return project_capped_simplex(v, cons.max_weight, g)
    if s < cons.min_gross - 1e-12:
        return project_capped_simplex(v, cons.max_weight, cons.min_gross)
    return w


def scale_to_capped_simplex(scores: np.ndarray, cap: float, total: float, *, on_zero: str = "cash") -> np.ndarray:
    """Weights proportional to positive scores, capped, summing to ``total``."""

    scores = np.maximum(np.nan_to_num(np.asarray(scores, dtype=float), nan=0.0), 0.0)
    n = scores.size
    target = min(max(0.0, float(total)), cap * n)
    if target <= 0:
        return np.zeros(n)
    if scores.sum() <= 0:
        if on_zero == "cash":
            return np.zeros(n)
        if on_zero == "raise":
            raise ZeroSignalError("all scores are zero")
        if on_zero != "equal":
            raise ValueError(f"unknown on_zero={on_zero!r}")
        scores = np.ones(n)
    result = np.zeros(n)
    active = scores > 0
    remaining = target
    while active.any() and remaining > 1e-12:
        proposed = scores[active] / scores[active].sum() * remaining
        idx = np.flatnonzero(active)
        over = proposed > cap
        if not over.any():
            result[idx] = proposed
            break
        result[idx[over]] = cap
        active[idx[over]] = False
        remaining = target - result.sum()
    return result


def constraint_violations(w: np.ndarray, cons: Constraints | None = None, *, tol: float = 1e-10) -> list[str]:
    cons = cons or Constraints()
    w = np.asarray(w, dtype=float)
    issues = []
    if not np.isfinite(w).all():
        issues.append("non_finite")
        return issues
    if (w < -tol).any():
        issues.append("negative_weight")
    if (w > cons.max_weight + tol).any():
        issues.append("above_max_weight")
    if w.sum() > cons.max_gross + tol:
        issues.append("above_max_gross")
    return issues
