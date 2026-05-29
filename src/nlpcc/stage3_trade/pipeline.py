"""Stage 3 orchestration for leakage-safe price/risk state."""

from __future__ import annotations

from typing import Any

from nlpcc.stage3_trade.models.breadth import breadth_score
from nlpcc.stage3_trade.models.covariance import sample_covariance
from nlpcc.stage3_trade.models.correlation_graph import build_correlation_graph
from nlpcc.stage3_trade.models.drawdown import max_drawdown_from_prices
from nlpcc.stage3_trade.models.equal_weight_state import cap_and_redistribute, equal_weight
from nlpcc.stage3_trade.models.inverse_volatility import inverse_volatility_weights, sample_volatility
from nlpcc.stage3_trade.models.momentum import blended_momentum_score, momentum_weights
from nlpcc.stage3_trade.models.sector_trend import sector_trend_weights
from nlpcc.stage3_trade.models.shrinkage_covariance import shrink_covariance
from nlpcc.stage3_trade.schema import AssetTradeState, Stage3Config, Stage3State
from nlpcc.stage3_trade.validators import assert_safe_price_inputs


def _date_int(row: dict[str, Any]) -> int:
    value = row.get("date_int", row.get("date"))
    return int(str(value).replace("-", "")[:8])


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _infer_decision_date(historical_prices: dict[str, list[dict[str, Any]]]) -> int:
    dates: list[int] = []
    for rows in historical_prices.values():
        dates.extend(_date_int(row) for row in rows if row.get("date_int", row.get("date")) not in (None, ""))
    if not dates:
        raise ValueError("Cannot infer decision_date from empty historical_prices.")
    return max(dates)


def _returns_from_closes(closes: tuple[float, ...]) -> tuple[float, ...]:
    returns: list[float] = []
    for previous, current in zip(closes, closes[1:]):
        if previous > 0:
            returns.append((current / previous) - 1.0)
    return tuple(returns)


def build_stage3_state(
    *,
    historical_prices: dict[str, list[dict[str, Any]]],
    fund_pool: list[str] | tuple[str, ...],
    decision_date: int | None = None,
    config: Stage3Config | dict[str, Any] | None = None,
) -> Stage3State:
    cfg = config if isinstance(config, Stage3Config) else Stage3Config.from_mapping(config)
    resolved_date = decision_date if decision_date is not None else _infer_decision_date(historical_prices)
    assert_safe_price_inputs(historical_prices, resolved_date)

    pool = tuple(dict.fromkeys(fund_pool))
    assets: dict[str, AssetTradeState] = {}
    returns_by_fund: dict[str, tuple[float, ...]] = {}
    close_by_fund: dict[str, tuple[float, ...]] = {}

    for fund_id in pool:
        rows = sorted(historical_prices.get(fund_id, []), key=_date_int)
        if not rows:
            continue
        current_row = next((row for row in reversed(rows) if _date_int(row) == resolved_date), None)
        current_open = _float_or_none(current_row.get("open")) if current_row else None
        prior_rows = [row for row in rows if _date_int(row) < resolved_date and row.get("close") not in (None, "")]
        closes = tuple(float(row["close"]) for row in prior_rows if float(row["close"]) > 0)
        returns = _returns_from_closes(closes)
        last_close = closes[-1] if closes else None
        returns_window = returns[-cfg.volatility_window :] if cfg.volatility_window > 0 else returns
        asset = AssetTradeState(
            fund_id=fund_id,
            current_open=current_open,
            last_close=last_close,
            prior_closes=closes,
            prior_returns=returns,
            volatility=sample_volatility(returns_window),
            momentum=blended_momentum_score(closes, cfg.momentum_windows),
            drawdown=max_drawdown_from_prices(closes, window=cfg.drawdown_window),
            breadth=breadth_score(returns, window=cfg.breadth_window),
        )
        assets[fund_id] = asset
        returns_by_fund[fund_id] = returns
        close_by_fund[fund_id] = closes

    available = tuple(fund_id for fund_id in pool if fund_id in assets)
    eq = equal_weight(available)
    inv_vol = cap_and_redistribute(inverse_volatility_weights(returns_by_fund), cfg.max_weight)
    mom = cap_and_redistribute(momentum_weights(close_by_fund, windows=cfg.momentum_windows), cfg.max_weight)
    sector = cap_and_redistribute(
        sector_trend_weights(
            close_by_fund,
            returns_by_fund,
            trend_window=cfg.sector_trend_window,
            breadth_window=cfg.breadth_window,
        ),
        cfg.max_weight,
    )
    covariance = sample_covariance({fund_id: list(values) for fund_id, values in returns_by_fund.items()})
    shrunk = shrink_covariance(covariance, alpha=cfg.shrinkage_alpha)
    correlation_edges = build_correlation_graph(returns_by_fund)
    diagnostics = {
        "available_funds": list(available),
        "missing_funds": [fund_id for fund_id in pool if fund_id not in assets],
        "uses_current_day_fields": ["open"],
        "correlation_edge_count": len(correlation_edges),
    }
    return Stage3State(
        decision_date=resolved_date,
        fund_pool=pool,
        assets=assets,
        equal_weight=eq,
        inverse_volatility_weight=inv_vol,
        momentum_weight=mom,
        sector_trend_weight=sector,
        covariance=covariance,
        shrinkage_covariance=shrunk,
        correlation_graph=tuple(edge.as_dict() for edge in correlation_edges),
        diagnostics=diagnostics,
    )
