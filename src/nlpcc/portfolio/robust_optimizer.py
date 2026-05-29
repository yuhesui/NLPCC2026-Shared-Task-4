"""Constrained robust mean-variance optimiser."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.target_weights import project_long_only_capped_vector, vector_to_weights


@dataclass(frozen=True)
class OptimizerConfig:
    risk_aversion: float = 4.0
    anchor_penalty: float = 2.0
    uncertainty_shrinkage: float = 0.35
    max_iter: int = 300
    step_size: float = 0.05

    @classmethod
    def from_mapping(cls, values: dict | None) -> "OptimizerConfig":
        if not values:
            return cls()
        return cls(**{key: value for key, value in values.items() if key in cls.__dataclass_fields__})


def robust_expected_returns(expected_returns: np.ndarray, confidence: np.ndarray | None, *, shrinkage: float) -> np.ndarray:
    if confidence is None or confidence.size == 0:
        return expected_returns * (1.0 - shrinkage)
    mean_confidence = float(np.maximum(0.0, np.minimum(1.0, confidence)).mean())
    return expected_returns * (1.0 - (float(shrinkage) * (1.0 - mean_confidence)))


def optimize_long_only_mean_variance(
    *,
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    assets: tuple[str, ...],
    constraints: PortfolioConstraints,
    anchor_weights: np.ndarray,
    config: OptimizerConfig | None = None,
    confidence: np.ndarray | None = None,
) -> dict[str, float]:
    cfg = config or OptimizerConfig()
    if expected_returns.ndim != 1:
        raise ValueError("expected_returns must be a vector")
    if covariance_matrix.shape != (len(expected_returns), len(expected_returns)):
        raise ValueError("covariance_matrix shape does not match expected returns")
    if anchor_weights.shape != expected_returns.shape:
        raise ValueError("anchor_weights shape does not match expected returns")
    if not np.isfinite(expected_returns).all() or not np.isfinite(covariance_matrix).all():
        raise ValueError("optimizer inputs contain non-finite values")

    cov = (covariance_matrix.astype(float) + covariance_matrix.astype(float).T) / 2.0
    cov = cov + np.eye(cov.shape[0], dtype=float) * 1e-10
    mu = robust_expected_returns(expected_returns.astype(float), confidence, shrinkage=cfg.uncertainty_shrinkage)
    weights = project_long_only_capped_vector(
        anchor_weights.astype(float),
        max_weight=constraints.max_weight,
        total=constraints.invested_weight,
    )
    for _ in range(cfg.max_iter):
        gradient = mu - (2.0 * cfg.risk_aversion * (cov @ weights)) - (2.0 * cfg.anchor_penalty * (weights - anchor_weights))
        candidate = project_long_only_capped_vector(
            weights + (cfg.step_size * gradient),
            max_weight=constraints.max_weight,
            total=constraints.invested_weight,
        )
        if float(np.abs(candidate - weights).max()) < 1e-10:
            weights = candidate
            break
        weights = candidate
    if not np.isfinite(weights).all():
        raise ValueError("optimizer produced non-finite weights")
    return vector_to_weights(weights, assets)
