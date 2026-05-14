# Phase 1a Strategy System

## Architecture

All strategies output target weights first:

```text
data + news
-> strategy signal
-> target weights
-> constraint projection
-> turnover control
-> trade conversion
-> official trade API payload
```

The only official trade-payload converter is `src/nlpcc4/execution/trade_converter.py`.

## Strategies

- S0 implements equal weight, inverse volatility, momentum, sector trend, persistence, rule-based macro rotation, news sentiment, and deterministic random constrained baselines.
- S1 implements Track 1 inverse-vol/momentum/breadth/defensive allocation and Track 2 top-k sector trend-following.
- S2 classifies bounded LLM regimes and blends deterministic regime weights with S1.
- S3 consumes bounded LLM alpha scores, shrinks by confidence, risk-budgets by volatility, and caps deviation from S1.
- S4 maps bounded event tuples to Track 2 sector exposure; Track 1 intentionally falls back to S1 in Phase 1a.

## Data

`src/nlpcc4/data/official_loader.py` prefers the official DataLoader when CSVs exist. If the ignored public dataset is absent, it uses a deterministic official-compatible synthetic loader for offline tests and dry-runs.

The default news policy is conservative:

```yaml
data:
  same_day_news_policy: previous_day_only
```

## Outputs

Each run writes:

```text
.var/runs/<run_id>/config_resolved.yaml
.var/runs/<run_id>/target_weights.csv
.var/runs/<run_id>/trades.csv
.var/runs/<run_id>/holdings.csv
.var/runs/<run_id>/diagnostics.json
.var/runs/<run_id>/metrics.json
.var/runs/<run_id>/run_summary.md
```
