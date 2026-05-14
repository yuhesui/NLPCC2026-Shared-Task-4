"""Turnover measurement and control utilities."""

from __future__ import annotations

from typing import Mapping, Sequence


def estimate_turnover(current: Mapping[str, float], target: Mapping[str, float]) -> float:
    """Estimate one-way turnover between current and target weights."""
    keys = set(current) | set(target)
    return 0.5 * sum(abs(target.get(key, 0.0) - current.get(key, 0.0)) for key in keys)


def apply_no_trade_band(
    current: Mapping[str, float],
    target: Mapping[str, float],
    no_trade_band: float,
    *,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Keep current weights where target changes are smaller than a band."""
    keys = tuple(universe) if universe is not None else tuple(sorted(set(current) | set(target)))
    band = max(0.0, float(no_trade_band or 0.0))
    adjusted: dict[str, float] = {}
    for asset in keys:
        cur = float(current.get(asset, 0.0))
        tgt = float(target.get(asset, 0.0))
        adjusted[asset] = cur if abs(tgt - cur) < band else tgt
    return adjusted


def apply_turnover_cap(
    current: Mapping[str, float],
    target: Mapping[str, float],
    max_turnover: float | None,
    *,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Scale the move from current to target when one-way turnover exceeds a cap."""
    if max_turnover is None:
        return dict(target)
    cap = max(0.0, float(max_turnover))
    keys = tuple(universe) if universe is not None else tuple(sorted(set(current) | set(target)))
    turnover = estimate_turnover(current, target)
    if turnover <= cap + 1e-12 or turnover <= 1e-12:
        return {asset: float(target.get(asset, 0.0)) for asset in keys}
    scale = cap / turnover
    return {
        asset: float(current.get(asset, 0.0)) + scale * (float(target.get(asset, 0.0)) - float(current.get(asset, 0.0)))
        for asset in keys
    }
