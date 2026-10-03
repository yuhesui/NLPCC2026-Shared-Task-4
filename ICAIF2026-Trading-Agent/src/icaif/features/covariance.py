"""Covariance estimators with shrinkage.

Ported idea: AlphaAllocator ``stage3_trade/models/shrinkage_covariance.py``
(fixed-alpha shrink to an average-variance diagonal target). Kept as
``fixed_shrinkage`` for continuity, and extended with:

* ``ledoit_wolf``: analytic optimal intensity toward a scaled identity
  (Ledoit & Wolf 2004, "A well-conditioned estimator...");
* ``constant_correlation``: LW (2004, "Honey, I shrunk...") target;
* ``ewma_covariance``.

All return symmetric positive-definite matrices (eigenvalue floor).
"""

from __future__ import annotations

import numpy as np

from icaif.data.market.panel import MarketView
from icaif.features.returns import bar_returns


def _clean(returns: np.ndarray) -> np.ndarray:
    """Drop rows with any NaN (pairwise-complete covariances are not PSD-safe)."""

    if returns.size == 0:
        return returns
    return returns[np.isfinite(returns).all(axis=1)]


def make_psd(cov: np.ndarray, floor: float = 1e-12) -> np.ndarray:
    sym = (cov + cov.T) / 2.0
    vals, vecs = np.linalg.eigh(sym)
    vals = np.maximum(vals, floor)
    return (vecs * vals) @ vecs.T


def sample_covariance(returns: np.ndarray) -> np.ndarray:
    x = _clean(returns)
    if x.shape[0] < 2:
        raise ValueError("need at least 2 complete return rows for a covariance")
    return np.cov(x, rowvar=False, ddof=1)


def fixed_shrinkage(returns: np.ndarray, alpha: float) -> tuple[np.ndarray, float]:
    """AlphaAllocator-compatible: (1-a) S + a * mean(diag S) * I."""

    s = sample_covariance(returns)
    a = float(np.clip(alpha, 0.0, 1.0))
    target = np.eye(s.shape[0]) * np.trace(s) / s.shape[0]
    return make_psd((1 - a) * s + a * target), a


def ledoit_wolf(returns: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit-Wolf shrinkage toward mu*I with the analytic optimal intensity."""

    x = _clean(returns)
    t, n = x.shape
    if t < 2:
        raise ValueError("need at least 2 complete return rows")
    xc = x - x.mean(axis=0)
    s = xc.T @ xc / t
    mu = np.trace(s) / n
    target = mu * np.eye(n)
    d2 = np.sum((s - target) ** 2) / n
    b_bar2 = sum(np.sum((np.outer(row, row) - s) ** 2) for row in xc) / (t**2 * n)
    b2 = min(b_bar2, d2)
    shrink = 0.0 if d2 == 0 else b2 / d2
    cov = shrink * target + (1 - shrink) * s
    return make_psd(cov * t / max(t - 1, 1)), float(shrink)


def constant_correlation(returns: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit-Wolf (2004) shrinkage toward the constant-correlation target."""

    x = _clean(returns)
    t, n = x.shape
    if t < 3:
        raise ValueError("need at least 3 complete return rows")
    xc = x - x.mean(axis=0)
    s = xc.T @ xc / t
    var = np.diag(s)
    sd = np.sqrt(np.maximum(var, 1e-18))
    corr = s / np.outer(sd, sd)
    r_bar = (corr.sum() - n) / (n * (n - 1))
    f = r_bar * np.outer(sd, sd)
    np.fill_diagonal(f, var)
    # Follows the reference covCor implementation (Ledoit & Wolf 2004).
    y = xc**2
    pi_mat = y.T @ y / t - s**2
    pi_hat = pi_mat.sum()
    theta = (xc**3).T @ xc / t - var[:, None] * s
    np.fill_diagonal(theta, 0.0)
    rho_hat = np.trace(pi_mat) + r_bar * np.sum(np.outer(1.0 / sd, sd) * theta)
    gamma = np.sum((f - s) ** 2)
    kappa = (pi_hat - rho_hat) / gamma if gamma > 0 else 0.0
    shrink = float(np.clip(kappa / t, 0.0, 1.0))
    cov = shrink * f + (1 - shrink) * s
    return make_psd(cov * t / (t - 1)), shrink


def ewma_covariance(returns: np.ndarray, halflife_bars: float) -> np.ndarray:
    x = _clean(returns)
    if x.shape[0] < 2:
        raise ValueError("need at least 2 complete return rows")
    decay = 0.5 ** (1.0 / halflife_bars)
    w = decay ** np.arange(x.shape[0] - 1, -1, -1, dtype=float)
    w /= w.sum()
    mu = w @ x
    xc = x - mu
    return make_psd((xc * w[:, None]).T @ xc)


def estimate_covariance(view: MarketView, *, lookback_bars: int, method: str = "ledoit_wolf",
                        alpha: float = 0.2, halflife_bars: float = 65.0) -> tuple[np.ndarray, dict[str, float]]:
    """Per-bar covariance from the decision view; returns (cov, diagnostics)."""

    rets = bar_returns(view, lookback_bars)
    complete = int(np.isfinite(rets).all(axis=1).sum()) if rets.size else 0
    if method == "sample":
        cov, shrink = make_psd(sample_covariance(rets)), 0.0
    elif method == "fixed":
        cov, shrink = fixed_shrinkage(rets, alpha)
    elif method == "ledoit_wolf":
        cov, shrink = ledoit_wolf(rets)
    elif method == "constant_correlation":
        cov, shrink = constant_correlation(rets)
    elif method == "ewma":
        cov, shrink = ewma_covariance(rets, halflife_bars), 0.0
    else:
        raise ValueError(f"unknown covariance method {method!r}")
    return cov, {"shrinkage": shrink, "rows_used": complete}
