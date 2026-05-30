# OFFICIAL_COMPATIBILITY.md

## Official Compatibility Assumptions

- Use the official starter kit as the reference for data access, server execution, and trade schema.
- The official-facing submitted wrapper should be thin and should call `src/nlpcc/`.
- Local tools should be validated against official server behaviour where possible.

## Leakage Safety

Do not use current-day close, high, low, change, or return before decision time. Same-day news must respect the official timestamp cutoff.

Prompt02 defines the internal safety contract in `src/nlpcc/core/data_contracts.py` and validates it in `src/nlpcc/core/leakage_guard.py`.

- Past trading days may expose complete OHLCV fields and should use `PriceVisibility.HISTORICAL_FULL`.
- The current decision day may expose only the opening price and should use `PriceVisibility.CURRENT_OPEN_ONLY`.
- Current-day `close`, `high`, `low`, `change`, `pct_change`, and `return` are treated as forbidden decision-time fields.
- Same-day news must have `publish_time` before the official 15:00 cutoff. Items at or after 15:00 are not visible for that decision.
- Future price bars and future news are invalid in `DailyDecisionInput`.

## Canonical Contracts

Canonical objects are shared by official-facing agents and local tooling:

- `RawNewsItem` for normalized official news records.
- `PriceBar` and `PricePanel` for decision-visible market data.
- `DailyDecisionInput` for one agent decision timestamp.
- `PortfolioState`, `TargetWeights`, and `OfficialTrade` for portfolio and order exchange.
- `DecisionTrace` for auditable decision metadata.

These contracts are dependency-free so they can be imported by both `src/nlpcc/` and `src/tools/` without binding production agents to local research tooling.

## Local Backtesting Parity

Local evaluation utilities should compare their outputs against official-server runs when that server is available. `src/tools/backtesting/metrics.py` computes cumulative return, volatility, Sharpe, drawdown, and turnover from local runs. `src/tools/backtesting/compare_official_local.py` compares official and local metric dictionaries with explicit tolerances so parity gaps are visible.

## Trade Execution

The official environment uses buy-by-cash and sell-by-holding-percentage semantics. Same-day sell proceeds should not be assumed available for same-day buys. The adapter must validate cash feasibility before submitting orders.

## Prompt14 Repair Status

The root official-facing wrapper now lives at `NLPCC_tasks/agent_platform/agents/build_agent.py` and calls `src/nlpcc/runtime/system_runner.py`.

Prompt14 made the portfolio semantics explicit:

- official `holdings[fund].value` is monetary holding value and must not be treated as shares;
- local share-like holdings are converted to value using current open only when needed;
- target weights are converted to official trades through `src/nlpcc/execution/order_planner.py`;
- buys use decision-time cash only, while same-day sell proceeds are excluded from the buy budget;
- invalid official trade payloads are rejected by `src/nlpcc/execution/trade_validator.py` before submission.

Read `outputs/reports/prompt14/official_local_parity_rerun_report.md` for current parity status. Local backtests and ablations remain local evidence unless explicitly marked as official-server parity runs.

## Dependency Policy

Avoid runtime dependency on external LLM APIs for final B-list execution. If LLM extraction is used, provide cached/frozen/reproducible alternatives and no-LLM fallback.
