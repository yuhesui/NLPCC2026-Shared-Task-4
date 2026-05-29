"""Black-Litterman view integration utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from nlpcc.portfolio.risk_parity import covariance_to_matrix
from nlpcc.stage2_text_store.schema import Stage2TextState


ASSET_GROUP_TO_FUNDS: dict[str, tuple[str, ...]] = {
    "equity_beta": ("000300.SH", "000905.SH", "399006.SZ", "000688.SH"),
    "technology_growth": ("399006.SZ", "000688.SH", "000941.SH", "399971.SZ"),
    "consumer": ("000932.SH",),
    "energy": ("000928.SH",),
    "materials": ("000819.SH",),
    "gold": ("518880.SH",),
    "bonds": ("000012.SH",),
    "financials": ("000300.SH",),
    "real_estate": ("000300.SH",),
}


@dataclass(frozen=True)
class BlackLittermanInputs:
    covariance: np.ndarray
    prior_returns: np.ndarray
    view_matrix: np.ndarray
    view_returns: np.ndarray
    view_uncertainty: np.ndarray
    view_confidence: np.ndarray
    assets: tuple[str, ...]


@dataclass(frozen=True)
class BlackLittermanResult:
    posterior_returns: np.ndarray
    view_count: int
    diagnostics: dict[str, float | int]


def equilibrium_returns(covariance_matrix: np.ndarray, anchor_weights: np.ndarray, *, risk_aversion: float) -> np.ndarray:
    return float(risk_aversion) * covariance_matrix @ anchor_weights


def build_bl_inputs(
    *,
    covariance: dict[str, dict[str, float]],
    assets: tuple[str, ...],
    anchor_weights: np.ndarray,
    text_state: Stage2TextState,
    risk_aversion: float = 2.5,
    tau: float = 0.05,
    min_confidence: float = 0.05,
    view_return_scale: float = 1.0,
) -> BlackLittermanInputs:
    cov = covariance_to_matrix(covariance, assets)
    prior = equilibrium_returns(cov, anchor_weights, risk_aversion=risk_aversion)
    asset_index = {asset: index for index, asset in enumerate(assets)}
    rows: list[np.ndarray] = []
    q_values: list[float] = []
    confidences: list[float] = []
    for view in text_state.bl_views:
        if view.direction == "neutral" or view.confidence < min_confidence:
            continue
        mapped = tuple(asset for asset in ASSET_GROUP_TO_FUNDS.get(view.asset_group, (view.asset_group,)) if asset in asset_index)
        if not mapped:
            continue
        row = np.zeros(len(assets), dtype=float)
        for asset in mapped:
            row[asset_index[asset]] = 1.0 / len(mapped)
        rows.append(row)
        confidence = max(0.0, min(1.0, float(view.confidence)))
        q_values.append((float(view.expected_return_bps) / 10000.0) * confidence * float(view_return_scale))
        confidences.append(confidence)

    if not rows:
        return BlackLittermanInputs(
            covariance=cov,
            prior_returns=prior,
            view_matrix=np.zeros((0, len(assets)), dtype=float),
            view_returns=np.zeros(0, dtype=float),
            view_uncertainty=np.zeros((0, 0), dtype=float),
            view_confidence=np.zeros(0, dtype=float),
            assets=assets,
        )

    view_matrix = np.vstack(rows)
    confidence_vector = np.array(confidences, dtype=float)
    base_variance = max(float(np.mean(np.diag(cov))), 1e-8)
    uncertainty_diag = base_variance * np.maximum(1.0 - confidence_vector, 0.05)
    return BlackLittermanInputs(
        covariance=cov,
        prior_returns=prior,
        view_matrix=view_matrix,
        view_returns=np.array(q_values, dtype=float),
        view_uncertainty=np.diag(uncertainty_diag),
        view_confidence=confidence_vector,
        assets=assets,
    )


def black_litterman_posterior(inputs: BlackLittermanInputs, *, tau: float = 0.05) -> BlackLittermanResult:
    if inputs.view_matrix.shape[0] == 0:
        raise ValueError("No valid BL views available")
    cov = inputs.covariance
    p = inputs.view_matrix
    omega = inputs.view_uncertainty
    scaled_cov = cov * float(tau)
    inv_scaled_cov = np.linalg.pinv(scaled_cov)
    inv_omega = np.linalg.pinv(omega)
    precision = inv_scaled_cov + p.T @ inv_omega @ p
    right = inv_scaled_cov @ inputs.prior_returns + p.T @ inv_omega @ inputs.view_returns
    posterior = np.linalg.pinv(precision) @ right
    if not np.isfinite(posterior).all():
        raise ValueError("BL posterior contains non-finite values")
    return BlackLittermanResult(
        posterior_returns=posterior,
        view_count=int(p.shape[0]),
        diagnostics={
            "view_count": int(p.shape[0]),
            "mean_confidence": float(inputs.view_confidence.mean()) if inputs.view_confidence.size else 0.0,
        },
    )
