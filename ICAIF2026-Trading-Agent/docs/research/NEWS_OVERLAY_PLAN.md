# News overlay plan

Research question: **does point-in-time public text add incremental, fee-adjusted value over a robust
quantitative core in a 7-round-per-day US-equity environment?**

## Mechanism (implemented: `portfolio/fusion.py`, `nlp/feature_store.py`)

```
w_base (quant core, gross g_t)  →  s_t (per-asset text score, NaN = no info)
   → direction d = transform(s)  (linear | rank | softmax | sigmoid | clipped z | sparse top-k), centred
   → Δw = d / ‖d‖₁ · η_t          (1'Δw = 0, ‖Δw‖₁ = η_t, optional per-asset cap, deadband)
   → w = Π(w_base + Δw)           exact projection onto 0 ≤ w ≤ 0.30, Σw = Σw_base
η_t = cap · conf^[confidence] · event_mult^[event] · vol_adj^[volatility] · regime^[regime], ≤ max_cap
```

Text score per asset at AS_OF: Σ relevance·decay(age; τ_e)·novelty·direction·confidence /
(Σ weights + prior_strength); NaN below `min_weight`. Direction modes: sentiment, event, attention,
sentiment×event. Relevance modes: weighted, binary (linked yes/no), uniform (market-wide).

## Improvements over AlphaAllocator

* event-specific half-lives τ_e (hours–days) instead of one 2-day half-life; wall or trading clock;
* novelty from causal near-duplicate clustering (repeats discounted, not double-counted);
* thin evidence shrinks to zero; missing information is NaN → exactly zero tilt;
* overlay budget can depend on confidence, event type, volatility, regime;
* exact zero-sum and L1 budget; gross exposure preserved; realised vs intended Δw reported;
* "news-driven turnover" is measured per round.

## Ablations (all runnable: `experiments/ablations.py`, matrix family `text_ablations`)

no_news · zeroed tensor · shuffled assets · wrong asset (other sector) · random scores · stale 24h / 120h ·
sign flip · relevance only (attention) · sentiment only (binary relevance) · market sentiment (uniform) ·
event only · relevance+sentiment · relevance+event · full structured · no recency · no novelty ·
no confidence · cap = 0 · source removal (filter articles by `source`) · frozen vs fine-tuned encoder (blocked).

Interpretation: a genuine signal must beat no_news and degrade under shuffled, wrong_asset, random and
sign_flip; stale variants show how fast information decays at 7 rounds/day.

## Experiment families

`nlp_relevance`, `nlp_components`, `overlay_caps` (0, 0.5%, 1%, 2%, 4% L1), `overlay_transforms`,
`overlay_recency` (event priors wall/trading clock, fixed 6h, fixed 48h = NLPCC 2-day, no decay),
`overlay_budget_modes`, `overlay_turnover_awareness`, `text_ablations`
(`configs/experiments/initial_matrix.yaml`).

## Event-prior calibration (to do on real data)

Event study per event type on the training segment: cumulative abnormal return path after
`available_at`, half-life of |CAR|, sign accuracy of tone, abnormal volume. Replace the priors file;
keep the old file as the "uncalibrated prior" comparator.

## Alternatives kept as experiments

Optimizer-integrated text alpha (`base: optimizer` with α = α_price + κ·s; TODO: not yet wired — the optimizer currently takes price alpha only); LLM structured events
(`llm/tasks.extract_event`) feeding the same aggregation; direct LLM allocation (refused by default).

## Status

Mechanism, ablations and matrix families run end-to-end on the **synthetic** world
(`docs/experiments/2026-10-03_synthetic_plumbing_run.md`). At the default planted strength the full
overlay did not beat no-news; shuffled/random/sign-flip were worse. In the planted-signal recovery
family the full overlay beats no-news by a margin that grows with the planted effect and the scrambled
controls stay below no-news, so the machinery can detect a real signal. **No real-data evidence exists yet.**
