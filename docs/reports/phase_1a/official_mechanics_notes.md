# Official Mechanics Notes

## Price Visibility

Inspected `NLPCC_tasks/server_platform/app/core/data_loader.py`.

- `get_historical_prices(...)` returns full OHLC/change/pct_change rows for previous trading days.
- The current decision day is appended with `open` only.
- Current-day `close`, `high`, `low`, `change`, and `pct_change` are explicitly set to `None`.
- `get_price_data(...)` can return current-day close and pct_change, but that path is used by the backtest engine for settlement/execution, not by custom strategy features.

Phase 1a conservative assumption: strategy features use visible historical close rows only and ignore the current open except as diagnostic context.

## News Timing

Inspected `DataLoader.get_news(...)` and `NLPCC_tasks/dataset/README.md`.

- The current code filters a trading-day window from `pre_k_days` before `current_date` through `current_date`.
- Same-day news is retained only when `PUBLISH_TIME.hour < 15`.
- A stale comment says current-day news should not be included, so there is a code/comment mismatch.

Phase 1a default: custom config uses `data.same_day_news_policy: previous_day_only`. `official_available` is supported for later verification against concrete examples.

## Cash And Holdings

Inspected `NLPCC_tasks/server_platform/app/core/backtest.py`.

- Portfolio holdings are stored as monetary values, not share quantities.
- `capital` is cash.
- `get_portfolio_status()` reports cash, holdings values, and total value.
- `submit_trades(...)` first updates current holdings by current-day `pct_change`, then executes trades at the current close.

## Buy/Sell Ordering

Official `submit_trades(...)` separates trades by action and executes buys before sells. This means buys cannot rely on proceeds from same-call sells.

Phase 1a trade converter assumption: buy amounts are limited to already available cash after cash buffer. Sells may create residual cash because the official engine processes them after buys.

## Commission

Official `execute_trade(...)` applies `0.0001` commission to buy amount and sold value. The starter README describes this as `0.01%` friction.

## Official Trade Payload Shape

Inspected `NLPCC_tasks/server_platform/app/models/backtest.py`.

- Buy: `{"fund_id": "...", "action": "buy", "amount": positive_float}`
- Sell: `{"fund_id": "...", "action": "sell", "percentage": fraction_in_(0,1]}`
- Hold actions are not submitted.

Custom strategies never emit these payloads. Conversion is centralized in `src/nlpcc4/execution/trade_converter.py`.

## Known Ambiguities

- Whether same-day news before 15:00 should be used for final competition runs needs concrete date examples.
- Whether target weights should be interpreted before or after daily settlement needs verification against an official server run.
- The public dataset directories in this checkout are empty/ignored, so Phase 1a offline verification used a deterministic official-compatible synthetic loader.
