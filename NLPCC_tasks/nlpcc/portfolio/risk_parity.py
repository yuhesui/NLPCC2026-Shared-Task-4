"""NumPy-backed long-only risk-parity allocator."""

from __future__ import annotations

import numpy as np

from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.target_weights import project_long_only_capped_vector, vector_to_weights


def covariance_to_matrix(
    covariance: dict[str, dict[str, float]],
    assets: tuple[str, ...],
    *,
    diagonal_floor: float = 1e-8,
) -> np.ndarray:
    matrix = np.zeros((len(assets), len(assets)), dtype=float)
    for row, left in enumerate(assets):
        for col, right in enumerate(assets):
            matrix[row, col] = float(covariance.get(left, {}).get(right, 0.0))
    matrix = (matrix + matrix.T) / 2.0
    for idx in range(len(assets)):
        matrix[idx, idx] = max(float(matrix[idx, idx]), diagonal_floor)
    return matrix


def inverse_volatility_vector(covariance_matrix: np.ndarray, *, total: float) -> np.ndarray:
    diag = np.maximum(np.diag(covariance_matrix), 1e-12)
    inv_vol = 1.0 / np.sqrt(diag)
    return inv_vol / float(inv_vol.sum()) * total


def risk_contributions(weights: np.ndarray, covariance_matrix: np.ndarray) -> np.ndarray:
    portfolio_variance = float(weights @ covariance_matrix @ weights)
    if portfolio_variance <= 0:
        return np.zeros_like(weights)
    marginal = covariance_matrix @ weights
    return weights * marginal / portfolio_variance


def solve_risk_parity_vector(
    covariance_matrix: np.ndarray,
    *,
    constraints: PortfolioConstraints,
    budgets: np.ndarray | None = None,
    max_iter: int = 250,
    tolerance: float = 1e-8,
) -> np.ndarray:
    """Approximate equal-risk-contribution weights with capped projection."""

    if covariance_matrix.ndim != 2 or covariance_matrix.shape[0] != covariance_matrix.shape[1]:
        raise ValueError("covariance_matrix must be square")
    asset_count = covariance_matrix.shape[0]
    if asset_count == 0:
        return np.array([], dtype=float)
    cov = (covariance_matrix.astype(float) + covariance_matrix.astype(float).T) / 2.0
    cov = cov + np.eye(asset_count, dtype=float) * 1e-10
    if not np.isfinite(cov).all():
        raise ValueError("covariance_matrix contains non-finite values")

    target_budgets = budgets.astype(float) if budgets is not None else np.ones(asset_count, dtype=float)
    target_budgets = np.maximum(target_budgets, 0.0)
    if float(target_budgets.sum()) <= 0:
        target_budgets = np.ones(asset_count, dtype=float)
    target_budgets = target_budgets / float(target_budgets.sum())

    weights = project_long_only_capped_vector(
        inverse_volatility_vector(cov, total=constraints.invested_weight),
        max_weight=constraints.max_weight,
        total=constraints.invested_weight,
    )
    for _ in range(max_iter):
        contributions = risk_contributions(weights, cov)
        if float(np.abs(contributions - target_budgets).max()) < tolerance:
            break
        adjustment = np.sqrt(np.divide(target_budgets, np.maximum(contributions, 1e-12)))
        weights = project_long_only_capped_vector(
            weights * adjustment,
            max_weight=constraints.max_weight,
            total=constraints.invested_weight,
        )
    return weights


def solve_risk_parity_weights(
    covariance: dict[str, dict[str, float]],
    assets: tuple[str, ...],
    *,
    constraints: PortfolioConstraints,
) -> dict[str, float]:
    matrix = covariance_to_matrix(covariance, assets)
    weights = solve_risk_parity_vector(matrix, constraints=constraints)
    return vector_to_weights(weights, assets)
