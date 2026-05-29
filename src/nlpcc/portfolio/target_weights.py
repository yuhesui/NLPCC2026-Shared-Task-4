"""Target-weight vector and dictionary utilities."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np


def normalize_weight_dict(weights: Mapping[str, float], *, total: float = 1.0) -> dict[str, float]:
    positive = {asset: max(0.0, float(weight)) for asset, weight in weights.items()}
    gross = sum(positive.values())
    if gross <= 0:
        return {}
    return {asset: (weight / gross) * total for asset, weight in positive.items() if weight > 0}


def weights_to_vector(weights: Mapping[str, float], assets: Iterable[str]) -> np.ndarray:
    return np.array([float(weights.get(asset, 0.0)) for asset in assets], dtype=float)


def vector_to_weights(vector: np.ndarray, assets: Iterable[str], *, min_abs: float = 1e-12) -> dict[str, float]:
    return {
        asset: round(float(weight), 10)
        for asset, weight in zip(assets, vector)
        if float(weight) > min_abs
    }


def blend_weight_dicts(weight_sets: Mapping[str, tuple[float, Mapping[str, float]]], *, total: float) -> dict[str, float]:
    raw: dict[str, float] = {}
    for blend_weight, weights in weight_sets.values():
        for asset, weight in weights.items():
            raw[asset] = raw.get(asset, 0.0) + (float(blend_weight) * float(weight))
    return normalize_weight_dict(raw, total=total)


def project_long_only_capped_vector(
    values: np.ndarray,
    *,
    max_weight: float,
    total: float,
) -> np.ndarray:
    """Project positive scores to a capped long-only simplex approximation."""

    if values.ndim != 1:
        raise ValueError("values must be a 1D vector")
    count = values.shape[0]
    if count == 0:
        return values.astype(float)
    cap = max(0.0, float(max_weight))
    target_total = min(max(0.0, float(total)), cap * count if cap > 0 else 0.0)
    if target_total <= 0 or cap <= 0:
        return np.zeros(count, dtype=float)

    remaining_assets = np.ones(count, dtype=bool)
    result = np.zeros(count, dtype=float)
    scores = np.maximum(np.asarray(values, dtype=float), 0.0)
    if float(scores.sum()) <= 0:
        scores = np.ones(count, dtype=float)

    remaining_total = target_total
    while remaining_assets.any() and remaining_total > 1e-12:
        active_scores = scores[remaining_assets]
        if float(active_scores.sum()) <= 0:
            active_scores = np.ones(active_scores.shape[0], dtype=float)
        proposed = active_scores / float(active_scores.sum()) * remaining_total
        active_indices = np.where(remaining_assets)[0]
        over = proposed > cap
        if not bool(over.any()):
            result[active_indices] = proposed
            break
        capped_indices = active_indices[over]
        result[capped_indices] = cap
        remaining_assets[capped_indices] = False
        remaining_total = target_total - float(result.sum())
    return result


def project_long_only_capped_weights(
    weights: Mapping[str, float],
    assets: Iterable[str],
    *,
    max_weight: float,
    total: float,
) -> dict[str, float]:
    asset_tuple = tuple(assets)
    vector = weights_to_vector(weights, asset_tuple)
    projected = project_long_only_capped_vector(vector, max_weight=max_weight, total=total)
    return vector_to_weights(projected, asset_tuple)
