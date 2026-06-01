"""Generate leakage-safe target-weight tensors through SystemRunner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

import numpy as np

from nlpcc.core.fund_universe import TrackName
from nlpcc.execution.order_planner import OrderPlannerConfig, plan_orders_from_target_weights
from nlpcc.runtime.system_runner import SystemRunner
from tools.experiments.candidate_factory import CandidateSpec
from tools.experiments.leakage_safe_input_builder import (
    LeakageSafeInputBuilder,
    MarketArrays,
    open_payload,
    portfolio_payload,
)
from tools.experiments.strategy_config_expander import materialize_prompt17_configs
from tools.experiments.target_tensor_cache import TargetTensorBundle, TargetTensorCache, tensor_fingerprint


@dataclass(frozen=True)
class TargetTensorGenerationRequest:
    repo_root: Path
    data_root: Path
    track: TrackName
    candidates: list[CandidateSpec]
    output_root: Path
    start_date: str | None = None
    end_date: str | None = None
    max_dates: int | None = None
    lookback_days: int = 60
    news_lookback_calendar_days: int = 1
    initial_capital: float = 100000.0
    commission_rate: float = 0.0001
    force: bool = False


@dataclass(frozen=True)
class TargetTensorGenerationResult:
    bundle: TargetTensorBundle
    cache_key: str
    npz_path: Path
    metadata_path: Path
    config_root: Path
    diagnostics: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "cache_key": self.cache_key,
            "npz_path": str(self.npz_path),
            "metadata_path": str(self.metadata_path),
            "config_root": str(self.config_root),
            "diagnostics": self.diagnostics,
            "metadata": self.bundle.metadata,
        }


def planner_config_for_track(track: TrackName) -> OrderPlannerConfig:
    if track == "sector":
        return OrderPlannerConfig(max_weight=0.25, cash_reserve=0.03, max_turnover=0.25, rebalance_threshold=0.01)
    return OrderPlannerConfig(max_weight=0.35, cash_reserve=0.03, max_turnover=0.25, rebalance_threshold=0.01)


def generate_target_tensor(request: TargetTensorGenerationRequest) -> TargetTensorGenerationResult:
    if not request.candidates:
        raise ValueError("At least one candidate is required.")
    cache_root = request.output_root / "target_tensors"
    cache = TargetTensorCache(cache_root)
    cache_payload = {
        "track": request.track,
        "data_root": str(request.data_root),
        "start_date": request.start_date,
        "end_date": request.end_date,
        "max_dates": request.max_dates,
        "lookback_days": request.lookback_days,
        "news_lookback_calendar_days": request.news_lookback_calendar_days,
        "initial_capital": request.initial_capital,
        "commission_rate": request.commission_rate,
        "candidates": [
            {
                "name": candidate.name,
                "system_name": candidate.system_name,
                "config_hash": candidate.config_hash,
                "text_mode": candidate.text_mode,
            }
            for candidate in request.candidates
        ],
    }
    cache_key = cache.key_for(cache_payload)
    if cache.exists(cache_key) and not request.force:
        bundle = cache.load(cache_key)
        npz_path, metadata_path = cache.paths_for(cache_key)
        return TargetTensorGenerationResult(
            bundle=bundle,
            cache_key=cache_key,
            npz_path=npz_path,
            metadata_path=metadata_path,
            config_root=request.output_root / "generated_configs",
            diagnostics={"cache_hit": True},
        )

    started = perf_counter()
    config_root = request.output_root / "generated_configs" / request.track
    materialize_prompt17_configs(repo_root=request.repo_root, output_config_root=config_root, candidates=request.candidates)
    builder = LeakageSafeInputBuilder(
        data_root=request.data_root,
        track=request.track,
        lookback_days=request.lookback_days,
        news_lookback_calendar_days=request.news_lookback_calendar_days,
    )
    arrays = builder.market_arrays(start_date=request.start_date, end_date=request.end_date, max_dates=request.max_dates)
    planner_config = planner_config_for_track(request.track)
    target_tensor = np.zeros((len(request.candidates), len(arrays.dates), len(arrays.assets)), dtype=float)
    candidate_diagnostics: list[dict[str, Any]] = []
    leakage_checks: list[dict[str, Any]] = []

    for candidate_index, candidate in enumerate(request.candidates):
        runner = SystemRunner.for_track(
            request.track,
            strategy=candidate.system_name,
            fallback_strategy=candidate.fallback_strategy,
            config_root=config_root,
        )
        cash = float(request.initial_capital)
        holdings = {asset: 0.0 for asset in arrays.assets}
        fallback_days = 0
        raw_fallback_days = 0
        failed_days = 0
        for date_index, decision_date in enumerate(arrays.dates):
            open_row = arrays.open_prices[date_index]
            day_input = builder.build_day(
                decision_date=decision_date,
                current_portfolio=portfolio_payload(cash, holdings, arrays.assets, open_row),
                load_news=candidate.load_news,
            )
            if candidate_index == 0:
                leakage_checks.append(day_input.diagnostics)
            try:
                decision = runner.run_day(
                    track=request.track,
                    fund_pool=arrays.assets,
                    historical_prices=day_input.historical_prices,
                    news=day_input.news,
                    current_portfolio=day_input.current_portfolio,
                    date_to_decision=decision_date,
                )
                if decision.fallback_status.get("fallback_used"):
                    fallback_days += 1
                if (decision.raw_decision.get("metadata", {}) or {}).get("fallback_used"):
                    raw_fallback_days += 1
                target_row = np.asarray(
                    [max(0.0, float(decision.target_weights.get(asset, 0.0))) for asset in arrays.assets],
                    dtype=float,
                )
            except Exception:
                failed_days += 1
                target_row = np.zeros((len(arrays.assets),), dtype=float)
            target_tensor[candidate_index, date_index, :] = target_row
            cash, holdings = _advance_official_portfolio(
                cash=cash,
                holdings=holdings,
                assets=arrays.assets,
                open_row=open_row,
                pct_row=arrays.pct_changes[date_index],
                target_weights=target_row,
                planner_config=planner_config,
                commission_rate=request.commission_rate,
            )
        candidate_diagnostics.append(
            {
                "name": candidate.name,
                "system_name": candidate.system_name,
                "track": candidate.track,
                "text_mode": candidate.text_mode,
                "fallback_days": fallback_days,
                "raw_stage_fallback_days": raw_fallback_days,
                "failed_days": failed_days,
                "target_nonzero_days": int((target_tensor[candidate_index].sum(axis=1) > 0).sum()),
            }
        )

    bundle = TargetTensorBundle(
        dates=arrays.dates,
        assets=arrays.assets,
        candidate_names=tuple(candidate.name for candidate in request.candidates),
        open_prices=arrays.open_prices,
        pct_changes=arrays.pct_changes,
        target_weights=target_tensor,
        metadata={
            "cache_payload": cache_payload,
            "planner_config": asdict(planner_config),
            "candidate_metadata": [candidate.as_dict() for candidate in request.candidates],
            "candidate_diagnostics": candidate_diagnostics,
            "leakage_summary": _leakage_summary(leakage_checks),
            "tensor_shape": list(target_tensor.shape),
            "tensor_fingerprint": "",
            "elapsed_seconds": round(perf_counter() - started, 6),
            "engine": "SystemRunner_target_tensor_generator",
        },
    )
    bundle.metadata["tensor_fingerprint"] = tensor_fingerprint(bundle)
    npz_path, metadata_path = cache.save(cache_key, bundle)
    return TargetTensorGenerationResult(
        bundle=bundle,
        cache_key=cache_key,
        npz_path=npz_path,
        metadata_path=metadata_path,
        config_root=config_root,
        diagnostics={"cache_hit": False, "elapsed_seconds": round(perf_counter() - started, 6)},
    )


def replay_bundle_inputs(bundle: TargetTensorBundle) -> dict[str, Any]:
    return {
        "dates": bundle.dates,
        "assets": bundle.assets,
        "open_prices": bundle.open_prices,
        "pct_changes": bundle.pct_changes,
        "target_weights": bundle.target_weights,
        "candidate_names": bundle.candidate_names,
    }


def _advance_official_portfolio(
    *,
    cash: float,
    holdings: Mapping[str, float],
    assets: tuple[str, ...],
    open_row: np.ndarray,
    pct_row: np.ndarray,
    target_weights: np.ndarray,
    planner_config: OrderPlannerConfig,
    commission_rate: float,
) -> tuple[float, dict[str, float]]:
    holdings_out = {asset: float(holdings.get(asset, 0.0)) for asset in assets}
    portfolio = portfolio_payload(cash, holdings_out, assets, open_row)
    targets = {asset: float(target_weights[index]) for index, asset in enumerate(assets)}
    plan = plan_orders_from_target_weights(
        targets,
        current_portfolio=portfolio,
        current_open_by_fund=open_payload(assets, open_row),
        fund_pool=assets,
        config=planner_config,
    )
    for index, asset in enumerate(assets):
        if holdings_out.get(asset, 0.0) > 0:
            holdings_out[asset] *= 1.0 + float(pct_row[index]) / 100.0
    for trade in list(plan.trades):
        asset = str(trade.get("fund_id"))
        if asset not in holdings_out:
            continue
        if trade.get("action") == "buy":
            amount = float(trade.get("amount", 0.0) or 0.0)
            if amount <= 0 or cash + 1e-2 < amount:
                continue
            cash = max(0.0, cash - amount)
            holdings_out[asset] = holdings_out.get(asset, 0.0) + amount * (1.0 - commission_rate)
        elif trade.get("action") == "sell":
            percentage = max(0.0, min(1.0, float(trade.get("percentage", 0.0) or 0.0)))
            if percentage <= 0 or holdings_out.get(asset, 0.0) <= 0:
                continue
            value_to_sell = holdings_out[asset] * percentage
            holdings_out[asset] = max(0.0, holdings_out.get(asset, 0.0) - value_to_sell)
            cash += value_to_sell * (1.0 - commission_rate)
    return float(cash), holdings_out


def _leakage_summary(checks: list[dict[str, Any]]) -> dict[str, Any]:
    if not checks:
        return {"checked_days": 0}
    return {
        "checked_days": len(checks),
        "all_current_day_close_masked": all(bool(item.get("current_day_close_masked")) for item in checks),
        "all_current_day_open_available": all(bool(item.get("current_day_open_available")) for item in checks),
        "news_cutoff_hour": NEWS_CUTOFF_HOUR,
        "forbidden_current_fields": ("close", "high", "low", "change", "pct_change"),
    }


NEWS_CUTOFF_HOUR = 15
