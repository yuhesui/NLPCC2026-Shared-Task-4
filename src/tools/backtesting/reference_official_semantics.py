"""Reference local replay for official value-holding semantics.

The official server stores each holding as monetary value, not share quantity.
At trade submission it first applies the current day's percentage move to
existing holdings, then executes buy orders from decision-time cash, then sell
orders by percentage of the current holding value. Same-day sell proceeds are
therefore not available for buys planned at the same decision timestamp.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.execution.order_planner import OrderPlannerConfig, plan_orders_from_target_weights
from tools.backtesting.metrics import compute_backtest_metrics


COMMISSION_RATE = 0.0001


@dataclass(frozen=True)
class OfficialSemanticsInput:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    open_prices: np.ndarray
    pct_changes: np.ndarray
    target_weights: np.ndarray
    initial_capital: float = 100000.0
    commission_rate: float = COMMISSION_RATE
    planner_config: OrderPlannerConfig = OrderPlannerConfig()
    emulate_official_finish_update: bool = True


@dataclass(frozen=True)
class OfficialSemanticsResult:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    portfolio_values: tuple[float, ...]
    weights: tuple[dict[str, float], ...]
    transactions: tuple[dict[str, Any], ...]
    metrics: dict[str, float]
    final_value: float
    diagnostics: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "engine": "reference_official_semantics",
            "dates": list(self.dates),
            "assets": list(self.assets),
            "portfolio_values": list(self.portfolio_values),
            "weights": list(self.weights),
            "transactions": list(self.transactions),
            "metrics": self.metrics,
            "final_value": self.final_value,
            "diagnostics": self.diagnostics,
        }


def validate_official_semantics_input(data: OfficialSemanticsInput) -> None:
    if data.open_prices.ndim != 2 or data.pct_changes.ndim != 2 or data.target_weights.ndim != 2:
        raise ValueError("open_prices, pct_changes, and target_weights must be 2D arrays.")
    expected = (len(data.dates), len(data.assets))
    if data.open_prices.shape != expected or data.pct_changes.shape != expected:
        raise ValueError("price matrix shapes must match dates/assets.")
    if data.target_weights.shape != expected:
        raise ValueError("target_weights shape must match dates/assets.")
    if len(data.dates) == 0 or len(data.assets) == 0:
        raise ValueError("At least one date and one asset are required.")
    if not np.isfinite(data.open_prices).all() or (data.open_prices <= 0).any():
        raise ValueError("open_prices must be finite positive values.")
    if not np.isfinite(data.pct_changes).all():
        raise ValueError("pct_changes must be finite.")
    if not np.isfinite(data.target_weights).all() or (data.target_weights < -1e-12).any():
        raise ValueError("target_weights must be finite and non-negative.")


def run_reference_official_semantics(data: OfficialSemanticsInput) -> OfficialSemanticsResult:
    """Replay target weights using the local official-semantics reference path."""

    validate_official_semantics_input(data)
    cash = float(data.initial_capital)
    holdings = {asset: 0.0 for asset in data.assets}
    values: list[float] = []
    weight_history: list[dict[str, float]] = []
    transactions: list[dict[str, Any]] = []
    successful_trade_dates: set[str] = set()

    for date_index, date in enumerate(data.dates):
        portfolio = _portfolio_payload(cash, holdings, data.assets, data.open_prices[date_index])
        targets = {
            asset: max(0.0, float(data.target_weights[date_index, asset_index]))
            for asset_index, asset in enumerate(data.assets)
        }
        plan = plan_orders_from_target_weights(
            targets,
            current_portfolio=portfolio,
            current_open_by_fund=_open_payload(data.assets, data.open_prices[date_index]),
            fund_pool=data.assets,
            config=data.planner_config,
        )

        for asset_index, asset in enumerate(data.assets):
            if holdings.get(asset, 0.0) > 0:
                holdings[asset] *= 1.0 + float(data.pct_changes[date_index, asset_index]) / 100.0

        for trade in _buys_first(plan.trades):
            action = trade.get("action")
            asset = str(trade.get("fund_id"))
            if asset not in holdings:
                continue
            if action == "buy":
                amount = float(trade.get("amount", 0.0) or 0.0)
                if amount <= 0 or cash + 1e-2 < amount:
                    continue
                commission = amount * data.commission_rate
                cash = max(0.0, cash - amount)
                holdings[asset] = holdings.get(asset, 0.0) + amount - commission
                transactions.append(
                    {
                        "date": date,
                        "fund_id": asset,
                        "action": "buy",
                        "amount": round(amount, 6),
                        "commission": round(commission, 6),
                    }
                )
                successful_trade_dates.add(date)
            elif action == "sell":
                percentage = float(trade.get("percentage", 0.0) or 0.0)
                if percentage <= 0 or percentage > 1 or holdings.get(asset, 0.0) <= 0:
                    continue
                value_to_sell = holdings[asset] * percentage
                commission = value_to_sell * data.commission_rate
                holdings[asset] = max(0.0, holdings[asset] - value_to_sell)
                cash += value_to_sell - commission
                transactions.append(
                    {
                        "date": date,
                        "fund_id": asset,
                        "action": "sell",
                        "percentage": round(percentage, 6),
                        "amount_sold": round(value_to_sell, 6),
                        "commission": round(commission, 6),
                    }
                )
                successful_trade_dates.add(date)

        total_value = cash + sum(holdings.values())
        values.append(float(total_value))
        weight_history.append(_weights(holdings, total_value))

    finish_update_applied = False
    if data.emulate_official_finish_update and data.dates[-1] in successful_trade_dates:
        last_index = len(data.dates) - 1
        for asset_index, asset in enumerate(data.assets):
            if holdings.get(asset, 0.0) > 0:
                holdings[asset] *= 1.0 + float(data.pct_changes[last_index, asset_index]) / 100.0
        total_value = cash + sum(holdings.values())
        values.append(float(total_value))
        weight_history.append(_weights(holdings, total_value))
        finish_update_applied = True

    metrics = compute_backtest_metrics(values, weight_history=weight_history).as_dict()
    diagnostics = {
        "semantics": "official_value_holdings_buy_first_sell_second",
        "commission_rate": data.commission_rate,
        "same_day_sell_proceeds_for_buys": False,
        "finish_update_applied": finish_update_applied,
        "planner_config": asdict(data.planner_config),
    }
    return OfficialSemanticsResult(
        dates=data.dates,
        assets=data.assets,
        portfolio_values=tuple(values),
        weights=tuple(weight_history),
        transactions=tuple(transactions),
        metrics=metrics,
        final_value=float(values[-1]),
        diagnostics=diagnostics,
    )


def load_official_semantics_arrays(
    data_root: Path,
    track: TrackName,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    max_dates: int | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray]:
    """Load common-date open and pctchange matrices from local CSV data."""

    assets = tuple(fund_id for fund_id in get_fund_pool(track) if (data_root / "price_data" / f"{fund_id}.csv").exists())
    if not assets:
        raise RuntimeError(f"No price files available for track {track} under {data_root}")
    start_int = int(start_date.replace("-", "").replace("/", "")) if start_date else None
    end_int = int(end_date.replace("-", "").replace("/", "")) if end_date else None
    rows_by_asset: dict[str, list[dict[str, str]]] = {}
    common_dates: set[str] | None = None
    for asset in assets:
        rows = _load_price_rows(data_root, asset)
        rows_by_asset[asset] = rows
        dates = {
            row["date"]
            for row in rows
            if (start_int is None or int(row["date"]) >= start_int)
            and (end_int is None or int(row["date"]) <= end_int)
        }
        common_dates = dates if common_dates is None else common_dates & dates
    dates = tuple(sorted(common_dates or ()))
    if max_dates is not None:
        dates = dates[: max(1, int(max_dates))]
    if not dates:
        raise RuntimeError(f"No common dates across assets for track {track} under {data_root}")

    open_prices = np.empty((len(dates), len(assets)), dtype=float)
    pct_changes = np.empty_like(open_prices)
    for col, asset in enumerate(assets):
        by_date = {row["date"]: row for row in rows_by_asset[asset]}
        for row_idx, date in enumerate(dates):
            row = by_date[date]
            open_prices[row_idx, col] = float(row["open"])
            pct_changes[row_idx, col] = float(row.get("pctchange", 0.0) or 0.0)
    return dates, assets, open_prices, pct_changes


def equal_weight_targets(date_count: int, asset_count: int, *, invested_weight: float = 0.98) -> np.ndarray:
    if date_count <= 0 or asset_count <= 0:
        raise ValueError("date_count and asset_count must be positive.")
    return np.full((date_count, asset_count), float(invested_weight) / asset_count, dtype=float)


def _load_price_rows(data_root: Path, fund_id: str) -> list[dict[str, str]]:
    path = data_root / "price_data" / f"{fund_id}.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _open_payload(assets: tuple[str, ...], open_row: np.ndarray) -> dict[str, float]:
    return {asset: float(open_row[index]) for index, asset in enumerate(assets)}


def _portfolio_payload(
    cash: float,
    holdings: Mapping[str, float],
    assets: tuple[str, ...],
    open_row: np.ndarray,
) -> dict[str, Any]:
    return {
        "cash": cash,
        "capital": cash,
        "holdings": {
            asset: {"value": float(holdings.get(asset, 0.0)), "price": float(open_row[index])}
            for index, asset in enumerate(assets)
            if holdings.get(asset, 0.0) > 1e-9
        },
        "total_value": cash + sum(float(value) for value in holdings.values() if value > 0),
    }


def _buys_first(trades: tuple[dict[str, float | str], ...]) -> list[dict[str, float | str]]:
    return [trade for trade in trades if trade.get("action") == "buy"] + [
        trade for trade in trades if trade.get("action") == "sell"
    ]


def _weights(holdings: Mapping[str, float], total_value: float) -> dict[str, float]:
    if total_value <= 0:
        return {}
    return {asset: float(value) / total_value for asset, value in holdings.items() if value > 1e-9}
