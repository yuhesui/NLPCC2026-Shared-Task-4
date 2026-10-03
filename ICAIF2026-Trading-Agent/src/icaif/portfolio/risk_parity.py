"""Equal-risk-contribution (risk parity) with ICAIF caps and explicit gross.

AlphaAllocator (``nlpcc/portfolio/risk_parity.py``) used a multiplicative
fixed-point update ``w <- w * sqrt(b / rc)`` from an inverse-vol start. That
update is kept as ``method="multiplicative"`` for comparison, but it does not
converge for covariance matrices with mixed-sign correlations (found by
``tests/portfolio``). The default is cyclical coordinate descent on the convex
problem  min_y 0.5 y'Σy - Σ b_i log y_i  (Griveau-Billion, Richard & Roncalli
2013), whose solution scaled to ``gross`` is the ERC portfolio; it converges
for any positive-definite Σ.

Caps: if scaled ERC weights exceed the cap, capped names are fixed at the cap
and the remaining budget is re-solved over the free names (repeat). Risk
contributions of capped names are then necessarily below budget; this is
reported via ``max_rc_error`` over free names only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.portfolio.constraints import Constraints, scale_to_capped_simplex


@dataclass(frozen=True)
class ERCResult:
    weights: np.ndarray
    iterations: int
    max_rc_error: float
    converged: bool


def risk_contributions(w: np.ndarray, cov: np.ndarray) -> np.ndarray:
    var = float(w @ cov @ w)
    if var <= 0:
        return np.zeros_like(w)
    return w * (cov @ w) / var


def _ccd(cov: np.ndarray, b: np.ndarray, free: np.ndarray, *, max_iter: int, tol: float) -> tuple[np.ndarray, int]:
    """Coordinate descent on the log-barrier ERC objective over ``free`` names
    (others held at 0). Returns the unscaled solution and iterations used."""

    y = np.where(free, 1.0 / np.sqrt(np.diag(cov)), 0.0)
    y[free] /= y[free].sum()
    diag = np.diag(cov)
    for it in range(1, max_iter + 1):
        y_old = y.copy()
        for i in np.flatnonzero(free):
            cross = cov[i] @ y - diag[i] * y[i]
            y[i] = (-cross + np.sqrt(cross * cross + 4.0 * diag[i] * b[i])) / (2.0 * diag[i])
        if np.abs(y - y_old).max() <= tol * max(1.0, np.abs(y).max()):
            return y, it
    return y, max_iter


def solve_erc(
    cov: np.ndarray,
    gross: float,
    cons: Constraints | None = None,
    *,
    budgets: np.ndarray | None = None,
    method: str = "ccd",
    max_iter: int = 1000,
    tol: float = 1e-10,
) -> ERCResult:
    cons = cons or Constraints()
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if cov.shape != (n, n) or not np.isfinite(cov).all():
        raise ValueError("covariance must be a finite square matrix")
    cov = (cov + cov.T) / 2.0 + np.eye(n) * 1e-12
    if budgets is None:
        b = np.full(n, 1.0 / n)
    else:
        b = np.asarray(budgets, dtype=float)
        if b.shape != (n,) or (b < 0).any() or b.sum() <= 0:
            raise ValueError("risk budgets must be non-negative with positive sum")
        b = b / b.sum()
    if gross <= 0:
        return ERCResult(np.zeros(n), 0, 0.0, True)
    if gross > cons.max_weight * np.count_nonzero(b) + 1e-12:
        raise ValueError("gross exceeds what the cap allows on budgeted names")
    if method == "multiplicative":
        return _multiplicative(cov, b, gross, cons, max_iter=max_iter, tol=1e-8)
    if method != "ccd":
        raise ValueError(f"unknown ERC method {method!r}")

    free = b > 0
    w = np.zeros(n)
    capped = np.zeros(n, dtype=bool)
    total_it = 0
    for _ in range(n):
        y, it = _ccd(cov, b, free & ~capped, max_iter=max_iter, tol=tol)
        total_it += it
        y = np.where(free & ~capped, y, 0.0)
        remaining = gross - cons.max_weight * capped.sum()
        w = np.where(capped, cons.max_weight, 0.0)
        if y.sum() > 0:
            w = w + y / y.sum() * remaining
        over = (w > cons.max_weight + 1e-12) & ~capped
        if not over.any():
            break
        capped |= over
    w = np.clip(w, 0.0, cons.max_weight)
    rc = risk_contributions(w, cov)
    active = free & ~capped
    target = b[active] / b[active].sum() * rc[active].sum() if active.any() else b[active]
    err = float(np.abs(rc[active] - target).max()) if active.any() else 0.0
    return ERCResult(w, total_it, err, err < 1e-6)


def _multiplicative(cov: np.ndarray, b: np.ndarray, gross: float, cons: Constraints, *, max_iter: int,
                    tol: float) -> ERCResult:
    """AlphaAllocator's update, kept for comparison only."""

    inv_vol = 1.0 / np.sqrt(np.maximum(np.diag(cov), 1e-18))
    w = scale_to_capped_simplex(inv_vol * np.where(b > 0, 1.0, 0.0), cons.max_weight, gross, on_zero="raise")
    err = np.inf
    it = 0
    for it in range(1, max_iter + 1):  # noqa: B007 - iteration count is reported
        rc = risk_contributions(w, cov)
        active = b > 0
        err = float(np.abs(rc[active] - b[active]).max())
        if err < tol:
            break
        w = scale_to_capped_simplex(w * np.sqrt(b / np.maximum(rc, 1e-18)), cons.max_weight, gross, on_zero="raise")
    return ERCResult(w, it, err, err < tol)
