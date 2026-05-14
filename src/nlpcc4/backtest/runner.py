"""Offline-safe local strategy runner for Phase 1a."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from nlpcc4.common.config import write_yaml_file
from nlpcc4.common.hashing import deterministic_run_id
from nlpcc4.common.paths import ensure_runtime_dirs, run_dir
from nlpcc4.common.types import DecisionContext
from nlpcc4.data.leakage_checks import run_leakage_checks
from nlpcc4.data.official_loader import OfficialDataPortal, load_official_data_loader
from nlpcc4.data.validators import validate_date_range
from nlpcc4.execution.target_weights import validate_target_weights
from nlpcc4.execution.trade_converter import TradeConversionRequest, convert_target_weights_to_trades
from nlpcc4.execution.turnover import estimate_turnover
from nlpcc4.experiments.registry import build_strategy, get_default_universe
from nlpcc4.llm.manual_io import ManualResponseMissing
from nlpcc4.metrics.performance import summarize_performance


def _format_date(day_int: int) -> str:
    text = str(day_int)
    return f"{text[:4]}-{text[4:6]}-{text[6:8]}"


@dataclass(frozen=True)
class RunRequest:
    track: str
    strategy_name: str
    config: Mapping[str, Any]
    config_path: str
    start_date: str
    end_date: str
    llm_mode: str = "off"
    run_id: str | None = None
    output_dir: str | None = None
    dry_run: bool = False
    prompt_only: bool = False


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _apply_trades(
    trades: list[dict[str, Any]],
    *,
    cash: float,
    holdings: dict[str, float],
    friction: float,
) -> tuple[float, dict[str, float], list[dict[str, Any]]]:
    executed: list[dict[str, Any]] = []
    # Match official engine semantics: buys are effectively processed before sells.
    for trade in [t for t in trades if t.get("action") == "buy"] + [t for t in trades if t.get("action") == "sell"]:
        asset = str(trade.get("fund_id"))
        if trade.get("action") == "buy":
            amount = max(0.0, min(float(trade.get("amount", 0.0)), cash))
            if amount <= 1e-8:
                continue
            commission = amount * friction
            cash -= amount
            holdings[asset] = holdings.get(asset, 0.0) + amount - commission
            executed.append({**trade, "commission": commission, "success": True})
        elif trade.get("action") == "sell":
            current = holdings.get(asset, 0.0)
            pct = max(0.0, min(1.0, float(trade.get("percentage", 0.0))))
            amount = current * pct
            if amount <= 1e-8:
                continue
            commission = amount * friction
            holdings[asset] = max(0.0, current - amount)
            cash += amount - commission
            executed.append({**trade, "amount_sold": amount, "commission": commission, "success": True})
    return cash, holdings, executed


def run_strategy_request(request: RunRequest) -> dict[str, Any]:
    """Run a strategy locally and write Phase 1a artifacts."""
    validate_date_range(request.start_date, request.end_date)
    config = dict(request.config)
    run_id = request.run_id or deterministic_run_id(
        track=request.track,
        strategy=request.strategy_name,
        start_date=request.start_date,
        end_date=request.end_date,
        llm_mode=request.llm_mode,
        config=config,
    )
    out_dir = Path(request.output_dir) if request.output_dir else run_dir(run_id)
    ensure_runtime_dirs(run_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    fund_pool = tuple(config.get("data", {}).get("fund_pool") or get_default_universe(request.track))
    data_cfg = config.get("data", {})
    portal = OfficialDataPortal(
        load_official_data_loader(),
        same_day_news_policy=str(data_cfg.get("same_day_news_policy", "previous_day_only")),
    )
    trading_dates = portal.trading_dates(request.start_date, request.end_date)
    if not trading_dates:
        raise RuntimeError("No trading dates available for requested range")

    strategy = build_strategy(request.track, request.strategy_name, config)
    initial_capital = float(config.get("execution", {}).get("initial_capital", 100000.0))
    friction = float(config.get("execution", {}).get("transaction_friction", 0.0001))
    lookback = int(data_cfg.get("lookback_days", 60))
    news_sources = tuple(data_cfg.get("news_sources", ("caixin", "tiantian", "sinafinance", "tencent")))
    top_rank = int(data_cfg.get("top_rank", 20))
    pre_k_days = int(data_cfg.get("pre_k_days", 1))

    cash = initial_capital
    holdings = {asset: 0.0 for asset in fund_pool}
    previous_weights = {asset: 0.0 for asset in fund_pool}
    equity_curve = [initial_capital]
    turnovers: list[float] = []
    target_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []
    holding_rows: list[dict[str, Any]] = []
    daily_diagnostics: list[dict[str, Any]] = []
    missing_manual: list[str] = []

    for day_int in trading_dates:
        decision_date = _format_date(day_int)
        historical = portal.historical_prices(fund_pool, day_int, lookback)
        run_leakage_checks(historical, day_int)
        news = portal.news(news_sources, day_int, top_rank, pre_k_days)
        context = DecisionContext(
            decision_date=decision_date,
            track=request.track,
            fund_pool=fund_pool,
            historical_prices=historical,
            news=tuple(news),
            current_portfolio={"cash": cash, "holdings": dict(holdings), "total_value": cash + sum(holdings.values())},
            previous_weights=previous_weights,
            config=config,
            run_id=run_id,
            llm_mode=request.llm_mode,
            dry_run=request.dry_run,
        )
        try:
            output = strategy.compute_target_weights(context)
        except ManualResponseMissing as exc:
            missing_manual.append(str(exc))
            daily_diagnostics.append({"date": decision_date, "error": str(exc), "manual_response_missing": True})
            if request.prompt_only:
                continue
            raise RuntimeError(str(exc)) from exc
        validate_target_weights(output.target_weights)

        for asset, weight in output.target_weights.items():
            target_rows.append({"date": decision_date, "asset": asset, "weight": weight})

        if request.prompt_only:
            daily_diagnostics.append({"date": decision_date, "prompt_only": True, "diagnostics": output.diagnostics})
            continue

        market_data = portal.market_data(fund_pool, day_int)
        for asset in fund_pool:
            pct_change = market_data.get(asset, {}).get("pct_change")
            if pct_change is not None and holdings.get(asset, 0.0) > 0:
                holdings[asset] *= 1.0 + float(pct_change) / 100.0
        portfolio_value = cash + sum(holdings.values())
        current_weights = {asset: (holdings.get(asset, 0.0) / portfolio_value if portfolio_value > 0 else 0.0) for asset in fund_pool}
        trades = convert_target_weights_to_trades(
            TradeConversionRequest(
                target_weights=output.target_weights,
                current_weights=current_weights,
                current_values=holdings,
                portfolio_value=portfolio_value,
                cash=cash,
                no_trade_band=float(config.get("execution", {}).get("trade_converter_band", 0.0) or 0.0),
                cash_buffer=float(config.get("portfolio", {}).get("cash_buffer", 0.01)),
            )
        )
        cash, holdings, executed = _apply_trades(trades, cash=cash, holdings=holdings, friction=friction)
        total_value = cash + sum(holdings.values())
        final_weights = {asset: (holdings.get(asset, 0.0) / total_value if total_value > 0 else 0.0) for asset in fund_pool}
        turnover = estimate_turnover(previous_weights, output.target_weights)
        turnovers.append(turnover)
        previous_weights = dict(output.target_weights)
        equity_curve.append(total_value)
        for trade in executed:
            trade_rows.append({"date": decision_date, **trade})
        holding_rows.append({"date": decision_date, "asset": "CASH", "value": cash, "weight": cash / total_value if total_value else 0.0})
        for asset, value in holdings.items():
            holding_rows.append({"date": decision_date, "asset": asset, "value": value, "weight": final_weights.get(asset, 0.0)})
        daily_diagnostics.append({"date": decision_date, "diagnostics": output.diagnostics, "turnover": turnover, "trade_count": len(executed)})

    metrics = summarize_performance(equity_curve, turnovers=turnovers, friction=friction, final_weights=previous_weights)
    metrics.update({"run_id": run_id, "track": request.track, "strategy": request.strategy_name})

    write_yaml_file(out_dir / "config_resolved.yaml", config)
    _write_csv(out_dir / "target_weights.csv", target_rows, ["date", "asset", "weight"])
    _write_csv(out_dir / "trades.csv", trade_rows, ["date", "fund_id", "action", "amount", "percentage", "amount_sold", "commission", "success"])
    _write_csv(out_dir / "holdings.csv", holding_rows, ["date", "asset", "value", "weight"])
    (out_dir / "diagnostics.json").write_text(json.dumps({"daily": daily_diagnostics, "missing_manual": missing_manual}, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = [
        f"# Run Summary: {run_id}",
        "",
        f"- Track: {request.track}",
        f"- Strategy: {request.strategy_name}",
        f"- Period: {request.start_date} to {request.end_date}",
        f"- LLM mode: {request.llm_mode}",
        f"- Prompt only: {request.prompt_only}",
        f"- Cumulative return: {metrics['cumulative_return']:.6f}",
        f"- Annualized Sharpe: {metrics['annualized_sharpe']:.6f}",
        f"- Max drawdown: {metrics['max_drawdown']:.6f}",
    ]
    if missing_manual:
        summary.append(f"- Missing manual responses: {len(missing_manual)}")
    (out_dir / "run_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    return {"run_id": run_id, "output_dir": str(out_dir), "metrics": metrics, "missing_manual": missing_manual}
