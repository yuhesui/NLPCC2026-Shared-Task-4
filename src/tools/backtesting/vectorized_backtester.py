"""NumPy-backed matrix backtesting engine.

This engine evaluates target-weight matrices against close-price matrices. It
does not call agents day-by-day; strategy code must provide target weights that
were generated from leakage-safe inputs.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from nlpcc.core.fund_universe import get_fund_pool
from tools.backtesting.metrics import compute_backtest_metrics


@dataclass(frozen=True)
class MatrixBacktestInput:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    close_prices: np.ndarray
    target_weights: np.ndarray
    initial_capital: float = 100000.0
    commission_rate: float = 0.0001


@dataclass(frozen=True)
class MatrixBacktestResult:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    portfolio_values: tuple[float, ...]
    weights: tuple[dict[str, float], ...]
    turnover: tuple[float, ...]
    metrics: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "engine": "numpy_matrix",
            "dates": list(self.dates),
            "assets": list(self.assets),
            "portfolio_values": list(self.portfolio_values),
            "weights": list(self.weights),
            "turnover": list(self.turnover),
            "metrics": self.metrics,
            "final_value": self.portfolio_values[-1] if self.portfolio_values else None,
        }


@dataclass(frozen=True)
class BatchBacktestSpec:
    name: str
    data_root: Path
    track: str
    target_weights: dict[str, float] | None = None
    output_path: Path | None = None


def _validate_input(data: MatrixBacktestInput) -> None:
    if data.close_prices.ndim != 2 or data.target_weights.ndim != 2:
        raise ValueError("close_prices and target_weights must be 2D arrays.")
    if data.close_prices.shape != data.target_weights.shape:
        raise ValueError("close_prices and target_weights must have matching shape.")
    if data.close_prices.shape != (len(data.dates), len(data.assets)):
        raise ValueError("Matrix shape must match dates/assets lengths.")
    if len(data.dates) < 1:
        raise ValueError("At least one date is required.")
    if not np.isfinite(data.close_prices).all() or (data.close_prices <= 0).any():
        raise ValueError("close_prices must be finite positive values.")
    if not np.isfinite(data.target_weights).all() or (data.target_weights < -1e-12).any():
        raise ValueError("target_weights must be finite non-negative values.")
    row_sums = data.target_weights.sum(axis=1)
    if (row_sums > 1.0 + 1e-9).any():
        raise ValueError("target weight rows must sum to 1.0 or less.")


def run_matrix_backtest(data: MatrixBacktestInput) -> MatrixBacktestResult:
    _validate_input(data)
    dates, assets = data.dates, data.assets
    close = data.close_prices.astype(float, copy=False)
    targets = data.target_weights.astype(float, copy=False)

    values = np.empty(len(dates), dtype=float)
    turnovers = np.zeros(len(dates), dtype=float)
    weights_matrix = np.zeros_like(targets, dtype=float)
    values[0] = float(data.initial_capital)
    weights_matrix[0] = targets[0]

    for idx in range(1, len(dates)):
        relatives = close[idx] / close[idx - 1]
        growth = float(np.dot(weights_matrix[idx - 1], relatives) + (1.0 - weights_matrix[idx - 1].sum()))
        value_before_rebalance = values[idx - 1] * growth
        drifted = (weights_matrix[idx - 1] * relatives) / growth if growth > 0 else np.zeros(len(assets))
        turnover = 0.5 * float(np.abs(targets[idx] - drifted).sum())
        cost = value_before_rebalance * turnover * data.commission_rate
        values[idx] = value_before_rebalance - cost
        turnovers[idx] = turnover
        weights_matrix[idx] = targets[idx]

    weight_history = [
        {asset: float(weight) for asset, weight in zip(assets, row) if weight > 0}
        for row in weights_matrix
    ]
    metrics = compute_backtest_metrics(values.tolist(), weight_history=weight_history).as_dict()
    return MatrixBacktestResult(
        dates=dates,
        assets=assets,
        portfolio_values=tuple(float(value) for value in values),
        weights=tuple(weight_history),
        turnover=tuple(float(value) for value in turnovers),
        metrics=metrics,
    )


def load_close_price_matrix(data_root: Path, track: str) -> tuple[tuple[str, ...], tuple[str, ...], np.ndarray]:
    assets = tuple(fund_id for fund_id in get_fund_pool(track) if (data_root / "price_data" / f"{fund_id}.csv").exists())
    if not assets:
        raise RuntimeError(f"No price files available for track {track} under {data_root}")

    rows_by_asset: dict[str, list[dict[str, str]]] = {}
    common_dates: set[str] | None = None
    for asset in assets:
        with (data_root / "price_data" / f"{asset}.csv").open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows_by_asset[asset] = rows
        dates = {row["date"] for row in rows}
        common_dates = dates if common_dates is None else common_dates & dates
    dates_tuple = tuple(sorted(common_dates or ()))
    if not dates_tuple:
        raise RuntimeError(f"No common dates across assets for track {track} under {data_root}")

    close = np.empty((len(dates_tuple), len(assets)), dtype=float)
    for col, asset in enumerate(assets):
        by_date = {row["date"]: row for row in rows_by_asset[asset]}
        close[:, col] = np.array([float(by_date[date]["close"]) for date in dates_tuple], dtype=float)
    return dates_tuple, assets, close


def equal_weight_target_matrix(date_count: int, asset_count: int, invested_weight: float = 1.0) -> np.ndarray:
    if asset_count <= 0:
        raise ValueError("asset_count must be positive.")
    return np.full((date_count, asset_count), float(invested_weight) / asset_count, dtype=float)


def run_equal_weight_matrix_backtest(
    data_root: Path,
    track: str,
    *,
    invested_weight: float = 0.98,
    initial_capital: float = 100000.0,
    commission_rate: float = 0.0001,
) -> MatrixBacktestResult:
    dates, assets, close = load_close_price_matrix(data_root, track)
    targets = equal_weight_target_matrix(len(dates), len(assets), invested_weight=invested_weight)
    return run_matrix_backtest(
        MatrixBacktestInput(
            dates=dates,
            assets=assets,
            close_prices=close,
            target_weights=targets,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
        )
    )


def run_vectorized_backtest(specs: Iterable[BatchBacktestSpec]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in specs:
        dates, assets, close = load_close_price_matrix(spec.data_root, spec.track)
        if spec.target_weights is None:
            targets = equal_weight_target_matrix(len(dates), len(assets), invested_weight=0.98)
        else:
            row = np.array([float(spec.target_weights.get(asset, 0.0)) for asset in assets], dtype=float)
            targets = np.tile(row, (len(dates), 1))
        result = run_matrix_backtest(MatrixBacktestInput(dates, assets, close, targets)).as_dict()
        result["run_name"] = spec.name
        if spec.output_path:
            import json

            spec.output_path.parent.mkdir(parents=True, exist_ok=True)
            spec.output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        results.append(result)
    return results
