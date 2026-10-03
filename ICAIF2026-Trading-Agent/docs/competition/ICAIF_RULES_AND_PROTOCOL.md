# ICAIF 2026 rules and protocol

Derived from the official starter kit
(`DeepIntoStreams/2026ICAIF_Trading_Agent_Competition`, commit `ad237b07`, 2026-09-21):
`starter-kit/README.md`, `docs/{guide,rules,evaluation,llm_and_external_data,automatic_submission}.md`,
`competition.json`, `universe.json`, `schedule.json`, `kit/*.py`, `schemas/*.json`.
**The official repository and live schedule win over this file.** Re-pin with
`scripts/setup/fetch_official_kit.sh` and re-run `tests/competition/test_official_kit_parity.py`
whenever upstream changes.

## 1. Verified constraints

| Item | Official value | Where enforced here |
|---|---|---|
| Universe | 30 fixed US stocks, 6 sector labels × 5 (labels impose no quotas) | `core/universe.py` (parity test vs `universe.json`) |
| Direction | Long-only, no leverage, fractional shares | `portfolio/constraints.py` |
| Decision content | All 30 symbols, finite JSON numbers (not strings/bools), each in [0, 0.30] | `competition/submission.py` + official `validate_payload` |
| Gross | Σw ≤ 1 (backend tolerance 1e-10); residual is cash | same |
| Accounts | Validation and Official start independently at USD 1,000,000 | `core/constants.py` |
| Rounds | 7 per trading day; deadlines 09:10, 10:25, …, 15:25 ET; execution 09:30, 10:30, …, 15:30 ET | `competition/schedule.py` (generator equals bundled schedule, all 119 rounds) |
| Windows | Open = previous execution + 10 min (R1: previous trading day's last execution + 10 min, normally 15:40); open inclusive, deadline exclusive | `Round.window_contains`, `assert_submission_window` |
| Fee | 0.1% of buy + sell notional per rebalance; initial allocation included | `backtest/execution.py` (cannot be disabled in serious runs) |
| Persistence | Portfolio carries across rounds and overnight; no forced liquidation at the end | backtester state |
| Missing / invalid / late | No rebalance, no fee, holdings kept | HOLD action (no upload) |
| All-zero target | Explicit liquidation to cash | valid decision; tested |
| First attempt wins | Earliest attributable in-window upload consumes the round, even if invalid; duplicates cannot correct it | `SubmissionLedger` + server-side `round()` check before every upload |
| 16:00 close | Valuation only (drawdown point), no round | `backtest/engine.py` valuation points |
| Phases | Validation 2026-10-08..09 (14 rounds); Official 2026-10-12..30 (15 days, normally 105 rounds); Final materials 2026-10-30 16:00 → 2026-11-03 23:59 ET (one slot) | `core/constants.py` |
| Early close | Rounds at/after the adjusted close are cancelled; excluded from K | `Schedule.phase_rounds` skips `CANCELLED` |

## 2. Metrics (exactly as `docs/evaluation.md` / `kit/evaluation.py`)

Periods k = 1..K over non-cancelled rounds; `B_k` = NAV just before round k executes (pre-fee);
`E_k` = NAV just before the next included rebalance (last: phase's final close); `r_k = E_k/B_k − 1`.

* M1 cumulative return `E_K/B_1 − 1`
* M2 Sharpe `42 · mean(r) / sample_std(r)` (`42 = √(252·7)` fixed even with cancellations; 0 if K = 1 or zero std)
* M3 max drawdown over {initial NAV, every `E_k`, every official daily close}, deduplicated by timestamp
* M4 turnover `mean_k N_k / B_k` (N_k = buy + sell notional, **two-sided**)
* Ranking: rank per metric (ties → average rank), Overall Rank Score = mean of 4 ranks (lower is better);
  tie-breaks: higher CR, higher Sharpe, lower MDD, lower turnover.

`competition/evaluation.py` reimplements these with 40-digit decimals and matches the official
calculator to 1e-12 (parity test). `overall_rank_scores` reproduces ranking given a comparator population.

## 3. LLM and external data policy

* LLMs are optional. If used, only: Llama 4, Qwen3, DeepSeek-V3/R1, Gemma 3, Mistral Large (open-weight);
  GPT-5 / GPT-5-mini, Claude Opus 5 / Sonnet 5 / Haiku 4.5, Gemini 2.5 Pro/Flash, Grok 4 (hosted).
  Disclose model name, version, provider, prompts, inference settings, API configuration.
* External data must be freely and publicly accessible and available at or before the submission
  deadline. No private, paid, proprietary or non-public feeds. Yahoo Finance and SEC EDGAR are
  recommended references (not a whitelist). Document sources and access methods.
* Encoded in `llm/policy.py` (family patterns) and `configs/embeddings/registry.yaml`.

## 4. Execution semantics the agent must respect

1. Weights are **targets**; the backend computes trades from current holdings at the official execution
   price. Our `current_weights` are always the *drifted* weights of actual holdings.
2. HOLD (no upload) is the only way to avoid fees in a round. Re-submitting "current weights" still
   trades small amounts because prices move between our snapshot and execution.
3. Information cutoff: the platform upload time decides timeliness. Our AS_OF is frozen when the round is
   processed (live) or at `deadline − decision_lead` (backtests), and nothing available later can enter.
4. With hourly bars aligned to :30, the bar containing a deadline is incomplete at decision time; R2..R7
   see a one-hour-stale last bar unless finer bars are used.

## 5. Conflicts with AlphaAllocator (NLPCC) assumptions

| NLPCC assumption | ICAIF reality | Consequence |
|---|---|---|
| One decision per day; date-level masks; 15:00 CN news cutoff | 7 rounds/day; per-round timestamp cutoffs (ET) | Leakage guard rewritten around `available_at` |
| Fee 0.01% (`COMMISSION_RATE=0.0001`) | 0.1% (10×) | Turnover control and no-trade bands are first-order; NLPCC-tuned overlay caps are not transferable |
| Turnover = 0.5·L1 (one-way) | Ranking turnover = two-sided notional / NAV | All turnover code uses two-sided L1 |
| Max weight 0.35, ~3% cash reserve (0.97 invested) | Max 0.30; gross is free in [0,1] | Gross exposure is a model output |
| Buy-cash / sell-% order payloads | Target weights only | Order planner not ported |
| Track A / Track B fund pools | One fixed 30-stock universe | Track machinery dropped |
| Chinese news, Chinese encoders | US equities, English news | Chinese models/lexicons not ported |
| Fixed 2-day news half-life | Intraday + multi-day horizons | Event-specific τ |

## 6. Open questions for the organizers

| # | Question | Why it matters | Current handling |
|---|---|---|---|
| Q1 | Are non-LLM encoders (e.g. BERT-size sentence encoders, FinBERT, cross-encoders) restricted by the LLM list? Do Qwen3-/Gemma-3-derived embedding models (Qwen3-Embedding, EmbeddingGemma) count as their parent family? | Determines which NLP models are legal | `requires_rule_confirmation: true`; blocked live |
| Q2 | Exact official execution price: "hourly open" from which data vendor/feed, and for R1 the official opening auction price? | Backtest execution proxy (open of bar starting at execution time) | Proxy documented |
| Q3 | How is the fee funded when Σw is at/near 1 (cash after fees < 0)? Does the backend scale buys, reduce cash below zero, or "correct tolerated excess" some other way? | Edge-case accounting | We leave `fee_rate × turnover` cash buffer; simulator scales buys |
| Q4 | Response schemas of `/api/v1/me/portfolio`, `/ledger`, `/rounds/{id}` (field names for cash/positions/prices)? | Live portfolio parsing | Strict parser; unknown shape → HOLD; verify in Validation |
| Q5 | May the agent use the platform's own portfolio valuation/prices as model inputs? | Data-source legitimacy | Not used as alpha input |
| Q6 | Is GDELT (free, public) acceptable; are Yahoo Finance pages acceptable for automated retrieval under their terms? | News coverage | Parsers only; disabled by default |
| Q7 | Are pretrained model knowledge cutoffs a concern (LLM trained on data after a backtest period)? Only relevant for our own research validity, but should disclosures mention it? | Disclosure | Flagged in FINETUNING_PLAN |
| Q8 | Will exceptional sessions (early closes) be announced only via the live schedule? | Calendar | Live schedule always reloaded |
