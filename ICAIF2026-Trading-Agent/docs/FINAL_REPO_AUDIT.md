# Final repository audit — 2026-10-03

Scope: first build of `icaif-trading-agent` (≈7.3k LOC in `src/`, 1.7k in `tests/`, 0.4k in
`scripts/`). Official kit pinned at `ad237b07` (2026-09-21). Validation starts 2026-10-08.

## Checks run

| Check | Result |
|---|---|
| `ruff check src tests scripts` | all checks passed |
| `python -m compileall src scripts tests` | ok |
| `python -m pytest` (kit present) | **159 passed** (unit 8, integration 21, leakage 19, competition 37, nlp 30, portfolio 30, runtime 14) |
| `ICAIF_KIT_ROOT=/nonexistent pytest tests/competition` | 27 passed, 10 official-kit parity tests skipped (clean degradation) |
| `scripts/experiments/run_matrix.py` (synthetic) | 77/77 ok, strict mode, 0 fallback rounds (+12 planted-signal runs) |
| `scripts/live/rehearse_paper.py` | 14/14 rounds uploaded once each to the local paper session; second polls `ALREADY_DECIDED` |
| `scripts/backtest/run_backtest.py`, `scripts/train/build_relevance_pairs.py --synthetic` | ok |
| Not run | `scripts/live/run_live.py` (needs credentials/profile + data), `scripts/data/check_sec_ciks.py` (network, needs `SEC_USER_AGENT`), GPU/transformer paths (no local models), CI workflow (`.github/` only runs once this directory is its own repository) |

## Implemented (working, tested)

* **Competition layer**: constants/universe (parity with `universe.json`/`competition.json`); schedule parser
  and standard-calendar generator (identical to all 119 bundled rounds); window/deadline guard; exact
  decision.json build/quantise/encode; independent validator that agrees with the official one on a test
  battery; submission ledger (one intent per round, restart-safe); official metrics (match the kit
  calculator to 1e-12); rank scoring with ties/tie-breaks; strict portfolio-payload parser.
* **Point-in-time contracts**: records with event/published/available/retrieved times and provenance;
  `PITStore`, vintage-aware `MacroStore`, amendment-safe `FilingStore`; `MarketPanel.as_of` (partial
  bars never visible); model-cutoff and label-purge guards; temporal splits with embargo and locked test.
* **Quant core**: returns/momentum (1h…20d), vol-scaled momentum, trend, realised/EWMA vol, covariance
  (sample, fixed-α, Ledoit-Wolf, constant-correlation, EWMA, PSD repair), regime descriptors; IV, ERC (CCD),
  turnover-penalised optimizer (FISTA + exact prox), top-k / top-k-softmax with hysteresis, score tilt.
* **Gross exposure** as a model output (fixed, vol target, regime, drawdown; min-composition, traced).
* **Turnover control**: two-sided L1, min-change HOLD, no-trade band, sparse changes, per-round cap, per-day
  budget (persisted), fee cash buffer, fee-funding in the simulator.
* **Bounded overlay**: zero-sum Δw with L1 budget, 6 transforms, confidence/event/vol/regime budgets,
  per-asset caps, deadband, gross preserved, realised vs intended Δw, news-driven turnover.
* **NLP (lexical/deterministic tier)**: visible-text extraction, Unicode/zero-width cleaning, language
  heuristic, exact + near-duplicate clustering, novelty; ticker/company linking with ambiguity rules;
  `score_relevance` interface with lexical, dense (any encoder), hybrid and cross-encoder classes; lexicon
  tone with negation; event schema + rule extractor + label-attention matcher; event priors; recency
  (wall/trading clock); evidence aggregation into `TextState`; training-pair builder with 6 negative types;
  ridge text model with cutoff.
* **LLM abstraction**: organizer-family policy check, call recording (prompt, model, temperature, seed,
  tokens, latency), replay client, validated structured tasks; direct allocation refused by default.
* **Runtime**: `DecisionContext`/`AgentState` (checkpointed), agent with ordered fallback chain and
  HOLD terminal, input/output safety checks, secret-free per-round traces, live runner (dry-run / paper /
  live) wrapping the official `OriginalSession`, local paper session for rehearsals.
* **Backtester** with ICAIF period accounting, valuation points and cost lock; diagnostics (gross, names,
  HHI, round/daily turnover, fees, news- vs price-driven turnover).
* **Experiments**: deterministic IDs, evidence grades, duplicate-result refusal, YAML matrix expansion
  (15 runnable families, 89 experiments), 9 ablations + component variants + source removal, reports.

## Ported from NLPCC (re-implemented with fresh tests)

Leakage-guard idea · capped water-filling projection · inverse-vol · ERC (legacy update kept for
comparison) · fixed-α shrinkage · turnover blending · decision trace + fallback events · fallback chain
pattern · bounded overlay (caps, deadband, turnover guard) · dedup/novelty · offline-model availability
statuses · approved-model registry schema · content-addressed feature cache · LEEQA top-k softmax ·
ARMOR-OMD-style expert weights · decayed event memory · purged folds · config hashing / result store ·
manifest hashing. Details: `docs/migration/NLPCC_TO_ICAIF_AUDIT.md`.

## Rewritten (behaviour deliberately changed)

ERC solver (CCD; legacy multiplicative update fails to converge under mixed-sign correlations) ·
turnover definition (two-sided) · leakage model (per-record `available_at`) · overlay normalisation
(no renormalise-to-1 / fixed 0.97) · recency (event-specific, raises on future items) · zero-signal
handling (explicit, not silent equal weight) · fallback scope (anticipated errors only; strict mode) ·
metrics (official ICAIF definitions) · execution semantics (target weights, 0.1% fee, HOLD).

## Stubbed / interface only

`UnconfiguredVendorSource` (live market data) · Yahoo Finance news and company IR RSS sources · hosted
and local LLM clients · `LocalSentenceEncoder` / `LocalCrossEncoderRelevance` / `LocalTransformerSentiment`
(implemented, untested against real weights) · `models/regime` learned models · optimizer-integrated text
alpha · Black-Litterman text views · official `watch` strategy adapter (the custom runner is used instead).

## Blocked

| Item | Blocker |
|---|---|
| Any real-market evidence (baselines, NLP value) | no point-in-time historical bars/news in the repo |
| Live trading | team registration/credentials, profile, a live intraday data job (TODO(data)) |
| Transformer encoders / rerankers / FinBERT | local model files (manual pinned download); policy cleared (Q1 resolved 2026-10-03) |
| Fine-tuning Stages A–C | labelled real data + base models |
| LLM experiments | client implementation, API credits, disclosure plan |

## Needs external data

Intraday bars (≤ 30-minute) for the 30 names with availability timestamps; news (GDELT / Yahoo /
IR feeds) with publication times; EDGAR filings (fetch script ready; CIK map unverified); ALFRED vintages.

## Needs organizer confirmation

Q1 resolved (non-LLM / public local encoders permitted) · Q2 official execution price source ·
Q3 fee funding at Σw≈1 · Q4 portfolio/ledger/round API response schemas · Q5 use of platform valuations
as inputs · Q6 GDELT / Yahoo automated access · Q7 model-knowledge-cutoff disclosure · Q8 exceptional
sessions (see `docs/competition/ICAIF_RULES_AND_PROTOCOL.md` §6).

## Known issues

* Synthetic world: momentum and event effects are planted; synthetic results are plumbing checks only.
* Backtest execution price is a proxy (open of the bar starting at execution time).
* `parse_portfolio_payload` shapes are guesses until checked against the live API (runner holds otherwise).
* EDGAR CIK map was written from reference knowledge and is unverified (`scripts/data/check_sec_ciks.py`).
* Language detection is a heuristic; entity aliases are hand-curated (no coverage study yet).
* Event priors are uncalibrated guesses.
* `PITStore.extend` is O(n) per insert (fine for current sizes); `MarketPanel.as_of` converts a tuple per call.
* Built as a directory on branch `claude/peaceful-cerf-3amyvl` of `yuhesui/NLPCC2026-Shared-Task-4`
  and extracted with `git subtree split --prefix=ICAIF2026-Trading-Agent` into `icaif-trading-agent`
  (history preserved).

## Recommended next experiments

1. **Real-data baseline sweep**: obtain ≤30-minute public bars (terms-reviewed) for a 6–12-month
   pre-period; run `quant_baselines`, `momentum_horizons`, `turnover_controls`, `exposure_policies` over
   15-day walk-forward windows; choose the Validation system from the rank-objective distribution.
2. **Rebalance cadence vs fees**: every round vs R1-only vs R1+R4 vs buy-and-hold, with the rank objective
   (turnover is 1 of 4 ranks) — likely the largest single lever.
3. **Lexical text overlay on real news** with the full ablation set (no_news, shuffled, wrong_asset,
   sign_flip, stale) and planted-signal power analysis calibrated to real noise.
4. **Encoder comparison E1/E3** (bge-small-en, MiniLM, Qwen3-Embedding-0.6B; policy cleared) —
   promote only on downstream PIT evidence.
5. **Event-study calibration** of half-lives and magnitudes per event type (replace the uncalibrated priors),
   then compare event-aware budgets against the fixed cap.
