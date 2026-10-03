"""Turnover-penalised mean-variance optimiser.

    max_w   alpha' w  -  lam * w' Σ w  -  gamma * ||w - w_prev||_1
    s.t.    0 <= w_i <= cap,   sum_i w_i <= g

Solved by FISTA on the smooth part with an exact proximal step for
``h(w) = gamma ||w - w_prev||_1 + I{0<=w<=cap, sum w<=g}``: the prox is
separable once the sum constraint's multiplier ``mu >= 0`` is fixed, and
``mu`` is found by bisection. Dependency-free (NumPy only) and deterministic.

``gamma`` should be at least the per-unit trading cost (0.001 per unit of
traded notional, in the same return units as ``alpha``) — see
``cost_adjusted_gamma``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.core.constants import FEE_RATE
from icaif.portfolio.constraints import Constraints


@dataclass(frozen=True)
class OptimResult:
    weights: np.ndarray
    objective: float
    iterations: int
    converged: bool


def objective(w: np.ndarray, alpha: np.ndarray, cov: np.ndarray, lam: float, gamma: float, w_prev: np.ndarray) -> float:
    return float(alpha @ w - lam * w @ cov @ w - gamma * np.abs(w - w_prev).sum())


def _prox_fixed_mu(y: np.ndarray, step: float, gamma: float, w_prev: np.ndarray, cap: float, mu: float) -> np.ndarray:
    """argmin_z 1/(2 step) ||z - y||^2 + gamma |z - w_prev|_1 + mu sum z, z in [0, cap]."""

    shifted = y - step * mu
    d = shifted - w_prev
    z = w_prev + np.sign(d) * np.maximum(np.abs(d) - step * gamma, 0.0)
    return np.clip(z, 0.0, cap)


def prox_h(y: np.ndarray, step: float, gamma: float, w_prev: np.ndarray, cap: float, gross: float) -> np.ndarray:
    z = _prox_fixed_mu(y, step, gamma, w_prev, cap, 0.0)
    if z.sum() <= gross + 1e-12:
        return z
    lo, hi = 0.0, 1.0
    while _prox_fixed_mu(y, step, gamma, w_prev, cap, hi).sum() > gross:
        hi *= 2.0
        if hi > 1e12:
            break
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if _prox_fixed_mu(y, step, gamma, w_prev, cap, mid).sum() > gross:
            lo = mid
        else:
            hi = mid
    return _prox_fixed_mu(y, step, gamma, w_prev, cap, hi)


def optimize(
    alpha: np.ndarray,
    cov: np.ndarray,
    w_prev: np.ndarray,
    *,
    lam: float,
    gamma: float,
    gross: float,
    cons: Constraints | None = None,
    max_iter: int = 2000,
    tol: float = 1e-10,
) -> OptimResult:
    cons = cons or Constraints()
    alpha = np.asarray(alpha, dtype=float)
    cov = (np.asarray(cov, dtype=float) + np.asarray(cov, dtype=float).T) / 2.0
    w_prev = np.asarray(w_prev, dtype=float)
    if not (np.isfinite(alpha).all() and np.isfinite(cov).all() and np.isfinite(w_prev).all()):
        raise ValueError("optimizer inputs must be finite")
    if lam < 0 or gamma < 0:
        raise ValueError("lam and gamma must be non-negative")
    g = float(np.clip(gross, 0.0, cons.max_gross))
    lip = 2.0 * lam * float(np.linalg.eigvalsh(cov).max()) if lam > 0 else 0.0
    step = 1.0 / max(lip, 1e-8) if lip > 0 else 1.0
    start = np.clip(w_prev, 0.0, cons.max_weight)
    if start.sum() > g:
        start = start * (g / start.sum())
    x = start.copy()
    y = x.copy()
    t = 1.0
    converged = False
    it = 0
    for it in range(1, max_iter + 1):  # noqa: B007 - iteration count is reported
        grad = -(alpha - 2.0 * lam * cov @ y)  # gradient of the minimised smooth part
        x_new = prox_h(y - step * grad, step, gamma, w_prev, cons.max_weight, g)
        t_new = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * t * t))
        y = x_new + ((t - 1.0) / t_new) * (x_new - x)
        if np.abs(x_new - x).max() < tol:
            x = x_new
            converged = True
            break
        x, t = x_new, t_new
    return OptimResult(x, objective(x, alpha, cov, lam, gamma, w_prev), it, converged)


def cost_adjusted_gamma(extra_penalty: float = 0.0, fee_rate: float = FEE_RATE) -> float:
    """Minimum sensible L1 penalty: the fee per unit of traded weight plus a
    turnover-rank penalty (turnover is itself a ranking metric)."""

    return fee_rate + max(0.0, extra_penalty)
