# System architecture

```
 point-in-time market bars (PIT store, MarketView @AS_OF)      public news / filings / macro (PITStore, MacroStore, FilingStore)
                 │                                                              │
        features/ (returns, momentum@1h..20d,                   nlp/ preprocessing → dedup/clusters → entity linking
        vol, Ledoit-Wolf cov, regime)                           → relevance (lexical | dense | cross | hybrid | LLM)
                 │                                              → tone, events (type, direction, τ_e), uncertainty
        models/alpha (scores, selection)                        → feature_store: TextState per asset @AS_OF
                 │                                                              │
                 └──────────────► portfolio/pipeline.py ◄───────────────────────┘
                         1 alpha  2 base (cash|equal|IV|ERC|tilt|top-k|optimizer, unit gross)
                         3 gross exposure g_t (fixed | vol target | regime | drawdown)
                         4 bounded overlay Δw (1'Δw=0, ‖Δw‖₁≤η_t)  ← text only enters here
                         5 turnover controller (min change, band, sparse, per-round, per-day)
                         6 finalise (fee cash buffer, exact projection onto 0≤w≤0.30, Σw≤g)
                                         │
                 runtime/agent.py: input checks → pipeline chain (primary → fallback → HOLD) → output checks
                                         │                         └─ decision trace (JSON, secret-free)
                 runtime/scheduler.py: schedule poll → active round → ledger/slot check → AS_OF freeze
                                         → decide → dual validation (ours + official kit) → ledger claim
                                         → private decision.json → official OriginalSession.decision() once
```

## Design principles

1. **Point-in-time by construction.** Every record has `available_at`; decision code only receives
   `MarketView`/`PITStore.as_of` slices. Violations raise `LeakageViolation` (never warn-and-continue).
2. **Quant core first; text is a bounded perturbation.** NLP can only change weights through
   `portfolio/fusion.apply_overlay` with an explicit L1 budget; `overlay.enabled: false` is the
   no-news control. Alternative designs (optimizer-integrated text alpha, LLM allocation) are
   supported as *experiments*, not defaults.
3. **Gross exposure is a decision**, not a constant.
4. **Costs and turnover are first-class**: two-sided L1, fee buffer, controls before finalisation;
   costs cannot be switched off in serious runs.
5. **Explicit, deterministic fallbacks.** Only anticipated failure classes trigger a fallback;
   unexpected exceptions are flagged (and re-raised in strict mode); the terminal action is HOLD.
6. **Wrap, don't fork, the official client.** Upload/auth/recovery remain in `kit/original_client.py`.
7. **Reproducibility.** Configs resolve to hashed mappings; experiment IDs are deterministic; every
   result carries an evidence grade so synthetic plumbing runs can never be mistaken for evidence.

## Package map

| Package | Responsibility |
|---|---|
| `core/` | constants, universe, timezone-strict time, PIT record schemas, leakage guard, config loader |
| `competition/` | schedule, decision.json build/validate/encode, submission ledger, portfolio state, official metrics, official-kit adapter |
| `data/` | PIT stores, manifests, market panel & loaders, synthetic world, news/SEC/macro parsers |
| `features/` | returns, momentum, volatility, covariance shrinkage, cross-sectional transforms, regime |
| `models/` | alpha signals and selection; text models (pairs, ridge); ensemble (expert weights) |
| `nlp/` | preprocessing, entity linking, relevance, embeddings, sentiment, events, priors, recency, uncertainty, feature store |
| `llm/` | policy, client/recording/replay, structured tasks |
| `portfolio/` | constraints, IV, ERC, optimizer, exposure, turnover, fusion, finalisation, pipeline |
| `runtime/` | decision context/state, agent, fallback, safety, traces, context builders, live scheduler |
| `backtest/` | execution simulator, engine, diagnostics, temporal splits |
| `experiments/` | registry, runner, matrix expansion, ablations, reporting |

## Decision trace contents (one JSON per round)

`information` (bars visible, last bar end, staleness, text summary, input issues, data source,
synthetic flag) · `quant` (alpha scores, unit-gross base, base after exposure, exposure components,
covariance shrinkage, ERC/optimizer diagnostics) · `nlp` (overlay budget and parts, intended vs
realised Δw, text evidence summary) · `portfolio` (previous weights, NAV, unconstrained proposal,
final target) · `constraints` (turnover steps, gross) · `costs` (expected turnover/fee,
news-driven turnover, realised fee in backtests) · `action`, `submitted_weights`,
`fallback_events`, `errors`. Credentials are redacted by key and by value.
