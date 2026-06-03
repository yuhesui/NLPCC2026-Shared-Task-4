"""Generate leakage-safe target-weight tensors through SystemRunner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

import numpy as np

from nlpcc.core.fund_universe import TrackName
from nlpcc.execution.order_planner import OrderPlannerConfig, plan_orders_from_target_weights
from nlpcc.runtime.system_runner import SystemRunner, _planner_config_from_system_config
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
        "data_version": _data_version_fingerprint(request.data_root),
        "start_date": request.start_date,
        "end_date": request.end_date,
        "max_dates": request.max_dates,
        "lookback_days": request.lookback_days,
        "news_lookback_calendar_days": request.news_lookback_calendar_days,
        "initial_capital": request.initial_capital,
        "commission_rate": request.commission_rate,
        "generation_semantics_version": "candidate_planner_trades_official_news_v4",
        "candidates": [
            {
                "name": candidate.name,
                "system_name": candidate.system_name,
                "family": candidate.family,
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
    candidate_planner_configs = [_planner_config_from_system_config(candidate.config) for candidate in request.candidates]
    target_tensor = np.zeros((len(request.candidates), len(arrays.dates), len(arrays.assets)), dtype=float)
    candidate_diagnostics: list[dict[str, Any]] = []
    leakage_checks: list[dict[str, Any]] = []
    trace_sample_path = request.output_root / "target_tensors" / "decision_traces" / request.track / f"{cache_key}.jsonl"
    trace_sample_path.parent.mkdir(parents=True, exist_ok=True)
    trace_samples: list[dict[str, Any]] = []
    sample_date_indices = {0, max(0, len(arrays.dates) - 1)}

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
            planned_trades: tuple[dict[str, float | str], ...] = ()
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
                planned_trades = decision.official_trades
                target_row = np.asarray(
                    [max(0.0, float(decision.target_weights.get(asset, 0.0))) for asset in arrays.assets],
                    dtype=float,
                )
                if date_index in sample_date_indices:
                    trace_samples.append(
                        {
                            "candidate": candidate.name,
                            "track": request.track,
                            "date": decision_date,
                            "fallback_status": decision.fallback_status,
                            "decision_trace": decision.decision_trace,
                            "stage_outputs_summary": decision.stage_outputs_summary,
                            "target_weight_sum": float(target_row.sum()),
                        }
                    )
            except Exception:
                failed_days += 1
                target_row = np.zeros((len(arrays.assets),), dtype=float)
                if date_index in sample_date_indices:
                    trace_samples.append(
                        {
                            "candidate": candidate.name,
                            "track": request.track,
                            "date": decision_date,
                            "fallback_status": {"fallback_used": True, "reason": "target_generation_exception"},
                            "decision_trace": {"runner": "SystemRunner_target_tensor_generator", "exception": True},
                            "stage_outputs_summary": {},
                            "target_weight_sum": 0.0,
                        }
                    )
            target_tensor[candidate_index, date_index, :] = target_row
            cash, holdings = _advance_official_portfolio(
                cash=cash,
                holdings=holdings,
                assets=arrays.assets,
                open_row=open_row,
                pct_row=arrays.pct_changes[date_index],
                target_weights=target_row,
                planner_config=candidate_planner_configs[candidate_index],
                planned_trades=planned_trades,
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
            "planner_config_mode": "candidate_config_planned_trades",
            "candidate_planner_configs": [asdict(config) for config in candidate_planner_configs],
            "candidate_metadata": [candidate.as_dict() for candidate in request.candidates],
            "candidate_diagnostics": candidate_diagnostics,
            "leakage_summary": _leakage_summary(leakage_checks),
            "tensor_shape": list(target_tensor.shape),
            "target_weight_axis_order": ["candidate", "date", "asset"],
            "tensor_fingerprint": "",
            "decision_trace_sample_path": str(trace_sample_path),
            "decision_trace_sample_count": len(trace_samples),
            "elapsed_seconds": round(perf_counter() - started, 6),
            "engine": "SystemRunner_target_tensor_generator",
        },
    )
    bundle.metadata["tensor_fingerprint"] = tensor_fingerprint(bundle)
    trace_sample_path.write_text(
        "".join(json.dumps(sample, ensure_ascii=False, sort_keys=True, default=str) + "\n" for sample in trace_samples),
        encoding="utf-8",
    )
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
    planned_trades: tuple[dict[str, float | str], ...] | list[dict[str, float | str]] | None = None,
    commission_rate: float,
) -> tuple[float, dict[str, float]]:
    holdings_out = {asset: float(holdings.get(asset, 0.0)) for asset in assets}
    if planned_trades is None:
        portfolio = portfolio_payload(cash, holdings_out, assets, open_row)
        targets = {asset: float(target_weights[index]) for index, asset in enumerate(assets)}
        plan = plan_orders_from_target_weights(
            targets,
            current_portfolio=portfolio,
            current_open_by_fund=open_payload(assets, open_row),
            fund_pool=assets,
            config=planner_config,
        )
        trades = list(plan.trades)
    else:
        trades = list(planned_trades)
    for index, asset in enumerate(assets):
        if holdings_out.get(asset, 0.0) > 0:
            holdings_out[asset] *= 1.0 + float(pct_row[index]) / 100.0
    for trade in trades:
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


def _data_version_fingerprint(data_root: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    sources: list[dict[str, Any]] = []
    manifest_candidates = [data_root / "manifest.json", *(data_root / "manifests").glob("*.json")]
    for path in sorted((candidate for candidate in manifest_candidates if candidate.exists()), key=lambda item: item.as_posix()):
        relative = path.relative_to(data_root).as_posix()
        payload = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(payload)
        sources.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": path.stat().st_size})
    if not sources:
        for child in sorted(data_root.glob("*")):
            digest.update(child.name.encode("utf-8"))
            digest.update(str(child.stat().st_mtime_ns).encode("utf-8"))
            digest.update(str(child.stat().st_size).encode("utf-8") if child.is_file() else b"directory")
        sources.append({"path": str(data_root), "mode": "directory_stat_fallback"})
    return {"sha256": digest.hexdigest(), "sources": sources}


NEWS_CUTOFF_HOUR = 15
