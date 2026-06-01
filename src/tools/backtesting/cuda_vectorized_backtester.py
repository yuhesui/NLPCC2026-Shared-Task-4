"""Batched official-semantics replay with optional Torch CUDA acceleration.

This backend accelerates the part that matters for grid search: replaying many
target-weight candidates over the same date and asset matrices. It does not
call strategy agents; candidate generation must still use leakage-safe inputs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
from typing import Any

import numpy as np

from nlpcc.execution.order_planner import OrderPlannerConfig
from tools.backtesting.metrics import compute_backtest_metrics


@dataclass(frozen=True)
class BatchedOfficialSemanticsInput:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    open_prices: np.ndarray
    pct_changes: np.ndarray
    target_weights: np.ndarray
    candidate_names: tuple[str, ...] | None = None
    initial_capital: float = 100000.0
    commission_rate: float = 0.0001
    planner_config: OrderPlannerConfig = OrderPlannerConfig()
    emulate_official_finish_update: bool = True


@dataclass(frozen=True)
class CandidateBacktestResult:
    name: str
    portfolio_values: tuple[float, ...]
    final_value: float
    weights: tuple[dict[str, float], ...]
    metrics: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "portfolio_values": list(self.portfolio_values),
            "final_value": self.final_value,
            "weights": list(self.weights),
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class BatchedOfficialSemanticsResult:
    backend: str
    device: str
    candidate_count: int
    date_count: int
    asset_count: int
    candidates: tuple[CandidateBacktestResult, ...]
    diagnostics: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "engine": "batched_official_semantics",
            "backend": self.backend,
            "device": self.device,
            "candidate_count": self.candidate_count,
            "date_count": self.date_count,
            "asset_count": self.asset_count,
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "diagnostics": self.diagnostics,
        }


def run_batched_official_semantics(
    data: BatchedOfficialSemanticsInput,
    *,
    backend: str = "auto",
    prefer_cuda: bool = True,
) -> BatchedOfficialSemanticsResult:
    """Run a batched replay using Torch when available, otherwise NumPy."""

    _validate_batched_input(data)
    selected_backend = backend.lower()
    if selected_backend not in {"auto", "torch", "numpy"}:
        raise ValueError("backend must be one of: auto, torch, numpy.")
    if selected_backend in {"auto", "torch"} and importlib.util.find_spec("torch") is not None:
        try:
            return _run_torch(data, prefer_cuda=prefer_cuda and selected_backend != "numpy")
        except Exception:
            if selected_backend == "torch":
                raise
    return _run_numpy(data)


def _validate_batched_input(data: BatchedOfficialSemanticsInput) -> None:
    if data.open_prices.ndim != 2 or data.pct_changes.ndim != 2:
        raise ValueError("open_prices and pct_changes must be 2D arrays.")
    expected_prices = (len(data.dates), len(data.assets))
    if data.open_prices.shape != expected_prices or data.pct_changes.shape != expected_prices:
        raise ValueError("price matrix shapes must match dates/assets.")
    if data.target_weights.ndim != 3:
        raise ValueError("target_weights must have shape candidates x dates x assets.")
    if data.target_weights.shape[1:] != expected_prices:
        raise ValueError("target_weights date/asset dimensions must match input matrices.")
    if len(data.dates) == 0 or len(data.assets) == 0 or data.target_weights.shape[0] == 0:
        raise ValueError("At least one candidate, date, and asset are required.")
    if data.candidate_names is not None and len(data.candidate_names) != data.target_weights.shape[0]:
        raise ValueError("candidate_names length must match candidate count.")
    if not np.isfinite(data.open_prices).all() or (data.open_prices <= 0).any():
        raise ValueError("open_prices must be finite positive values.")
    if not np.isfinite(data.pct_changes).all() or not np.isfinite(data.target_weights).all():
        raise ValueError("pct_changes and target_weights must be finite.")
    if (data.target_weights < -1e-12).any():
        raise ValueError("target_weights must be non-negative.")


def _run_torch(data: BatchedOfficialSemanticsInput, *, prefer_cuda: bool) -> BatchedOfficialSemanticsResult:
    import torch  # type: ignore

    device = torch.device("cuda" if prefer_cuda and torch.cuda.is_available() else "cpu")
    dtype = torch.float64
    target = torch.as_tensor(data.target_weights, dtype=dtype, device=device)
    pct = torch.as_tensor(data.pct_changes, dtype=dtype, device=device) / 100.0

    cash = torch.full((target.shape[0],), float(data.initial_capital), dtype=dtype, device=device)
    holdings = torch.zeros((target.shape[0], target.shape[2]), dtype=dtype, device=device)
    values_history: list[np.ndarray] = []
    weights_history: list[np.ndarray] = []
    last_trade_success = torch.zeros((target.shape[0],), dtype=torch.bool, device=device)
    cfg = data.planner_config

    for date_index in range(target.shape[1]):
        total = cash + holdings.sum(dim=1)
        current_weights = torch.where(total[:, None] > 0, holdings / total[:, None], torch.zeros_like(holdings))
        clean = torch.clamp(target[:, date_index, :], min=0.0)
        if cfg.max_weight is not None:
            clean = torch.clamp(clean, max=float(cfg.max_weight))
        if cfg.max_turnover is not None:
            turnover = 0.5 * torch.abs(clean - current_weights).sum(dim=1)
            limit = float(cfg.max_turnover)
            blend = torch.where(turnover > limit, torch.full_like(turnover, limit) / torch.clamp(turnover, min=1e-18), torch.ones_like(turnover))
            clean = current_weights + blend[:, None] * (clean - current_weights)

        diff = clean - current_weights
        active = torch.abs(diff) >= float(cfg.rebalance_threshold)
        sell_pct = torch.where(
            (diff < 0) & active & (current_weights > 0),
            torch.minimum(torch.ones_like(diff), torch.abs(diff) / torch.clamp(current_weights, min=1e-18)),
            torch.zeros_like(diff),
        )
        sell_pct = _torch_round6(sell_pct)
        sell_pct = torch.where(sell_pct >= float(cfg.min_sell_percentage), sell_pct, torch.zeros_like(sell_pct))

        buy_needs = torch.where((diff > 0) & active, diff * total[:, None], torch.zeros_like(diff))
        buy_budget = torch.clamp(cash - (float(cfg.cash_reserve) * total), min=0.0)
        total_needed = buy_needs.sum(dim=1)
        scale = torch.where(total_needed > 0, torch.minimum(torch.ones_like(total_needed), buy_budget / torch.clamp(total_needed, min=1e-18)), torch.zeros_like(total_needed))
        buy_amounts = _torch_round6(buy_needs * scale[:, None])
        buy_amounts = torch.where(buy_amounts >= float(cfg.min_trade_amount), buy_amounts, torch.zeros_like(buy_amounts))

        holdings = holdings * (1.0 + pct[date_index, :][None, :])
        buy_totals = buy_amounts.sum(dim=1)
        cash = torch.clamp(cash - buy_totals, min=0.0)
        holdings = holdings + buy_amounts * (1.0 - float(data.commission_rate))
        sold_values = holdings * sell_pct
        holdings = torch.clamp(holdings - sold_values, min=0.0)
        cash = cash + sold_values.sum(dim=1) * (1.0 - float(data.commission_rate))
        last_trade_success = (buy_totals > 0) | (sold_values.sum(dim=1) > 0)

        value = cash + holdings.sum(dim=1)
        values_history.append(value.detach().cpu().numpy())
        weights_history.append(torch.where(value[:, None] > 0, holdings / value[:, None], torch.zeros_like(holdings)).detach().cpu().numpy())

    finish_mask = last_trade_success.detach().cpu().numpy().astype(bool)
    if data.emulate_official_finish_update and bool(last_trade_success.any().item()):
        mask = last_trade_success[:, None].to(dtype=dtype)
        holdings = holdings * (1.0 + mask * pct[-1, :][None, :])
        value = cash + holdings.sum(dim=1)
        values_history.append(value.detach().cpu().numpy())
        weights_history.append(torch.where(value[:, None] > 0, holdings / value[:, None], torch.zeros_like(holdings)).detach().cpu().numpy())

    return _build_result(
        data,
        backend="torch",
        device=str(device),
        values_history=values_history,
        weights_history=weights_history,
        finish_mask=finish_mask,
    )


def _run_numpy(data: BatchedOfficialSemanticsInput) -> BatchedOfficialSemanticsResult:
    target = data.target_weights.astype(float, copy=False)
    pct = data.pct_changes.astype(float, copy=False) / 100.0
    cash = np.full(target.shape[0], float(data.initial_capital), dtype=float)
    holdings = np.zeros((target.shape[0], target.shape[2]), dtype=float)
    values_history: list[np.ndarray] = []
    weights_history: list[np.ndarray] = []
    last_trade_success = np.zeros(target.shape[0], dtype=bool)
    cfg = data.planner_config

    for date_index in range(target.shape[1]):
        total = cash + holdings.sum(axis=1)
        current_weights = np.divide(holdings, total[:, None], out=np.zeros_like(holdings), where=total[:, None] > 0)
        clean = np.clip(target[:, date_index, :], 0.0, None)
        if cfg.max_weight is not None:
            clean = np.clip(clean, 0.0, float(cfg.max_weight))
        if cfg.max_turnover is not None:
            turnover = 0.5 * np.abs(clean - current_weights).sum(axis=1)
            blend = np.where(turnover > float(cfg.max_turnover), float(cfg.max_turnover) / np.maximum(turnover, 1e-18), 1.0)
            clean = current_weights + blend[:, None] * (clean - current_weights)

        diff = clean - current_weights
        active = np.abs(diff) >= float(cfg.rebalance_threshold)
        sell_pct = np.where(
            (diff < 0) & active & (current_weights > 0),
            np.minimum(1.0, np.abs(diff) / np.maximum(current_weights, 1e-18)),
            0.0,
        )
        sell_pct = np.round(sell_pct, 6)
        sell_pct = np.where(sell_pct >= float(cfg.min_sell_percentage), sell_pct, 0.0)

        buy_needs = np.where((diff > 0) & active, diff * total[:, None], 0.0)
        buy_budget = np.maximum(0.0, cash - float(cfg.cash_reserve) * total)
        total_needed = buy_needs.sum(axis=1)
        scale = np.where(total_needed > 0, np.minimum(1.0, buy_budget / np.maximum(total_needed, 1e-18)), 0.0)
        buy_amounts = np.round(buy_needs * scale[:, None], 6)
        buy_amounts = np.where(buy_amounts >= float(cfg.min_trade_amount), buy_amounts, 0.0)

        holdings = holdings * (1.0 + pct[date_index, :][None, :])
        buy_totals = buy_amounts.sum(axis=1)
        cash = np.maximum(0.0, cash - buy_totals)
        holdings = holdings + buy_amounts * (1.0 - float(data.commission_rate))
        sold_values = holdings * sell_pct
        holdings = np.maximum(0.0, holdings - sold_values)
        cash = cash + sold_values.sum(axis=1) * (1.0 - float(data.commission_rate))
        last_trade_success = (buy_totals > 0) | (sold_values.sum(axis=1) > 0)

        value = cash + holdings.sum(axis=1)
        values_history.append(value.copy())
        weights_history.append(np.divide(holdings, value[:, None], out=np.zeros_like(holdings), where=value[:, None] > 0))

    finish_mask = last_trade_success.copy()
    if data.emulate_official_finish_update and bool(last_trade_success.any()):
        holdings = holdings * (1.0 + last_trade_success[:, None].astype(float) * pct[-1, :][None, :])
        value = cash + holdings.sum(axis=1)
        values_history.append(value.copy())
        weights_history.append(np.divide(holdings, value[:, None], out=np.zeros_like(holdings), where=value[:, None] > 0))

    return _build_result(
        data,
        backend="numpy",
        device="cpu",
        values_history=values_history,
        weights_history=weights_history,
        finish_mask=finish_mask,
    )


def _build_result(
    data: BatchedOfficialSemanticsInput,
    *,
    backend: str,
    device: str,
    values_history: list[np.ndarray],
    weights_history: list[np.ndarray],
    finish_mask: np.ndarray,
) -> BatchedOfficialSemanticsResult:
    value_matrix = np.vstack(values_history).T
    weight_tensor = np.stack(weights_history, axis=1)
    names = data.candidate_names or tuple(f"candidate_{index}" for index in range(data.target_weights.shape[0]))
    candidates: list[CandidateBacktestResult] = []
    for candidate_index, name in enumerate(names):
        candidate_values = value_matrix[candidate_index]
        candidate_weights = weight_tensor[candidate_index]
        if len(values_history) > len(data.dates) and not bool(finish_mask[candidate_index]):
            candidate_values = candidate_values[:-1]
            candidate_weights = candidate_weights[:-1]
        values = tuple(float(value) for value in candidate_values)
        weights = tuple(_weight_row(data.assets, candidate_weights[row_index]) for row_index in range(candidate_weights.shape[0]))
        metrics = compute_backtest_metrics(values, weight_history=weights).as_dict()
        candidates.append(
            CandidateBacktestResult(
                name=name,
                portfolio_values=values,
                final_value=float(values[-1]),
                weights=weights,
                metrics=metrics,
            )
        )
    diagnostics = {
        "semantics": "batched_official_value_holdings_buy_first_sell_second",
        "planner_config": asdict(data.planner_config),
        "same_day_sell_proceeds_for_buys": False,
        "torch_cuda_requested": backend == "torch" and device == "cuda",
    }
    return BatchedOfficialSemanticsResult(
        backend=backend,
        device=device,
        candidate_count=len(candidates),
        date_count=len(data.dates),
        asset_count=len(data.assets),
        candidates=tuple(candidates),
        diagnostics=diagnostics,
    )


def _torch_round6(value: Any) -> Any:
    import torch  # type: ignore

    return torch.round(value * 1_000_000.0) / 1_000_000.0


def _weight_row(assets: tuple[str, ...], weights: np.ndarray) -> dict[str, float]:
    return {asset: float(weight) for asset, weight in zip(assets, weights) if weight > 1e-12}
