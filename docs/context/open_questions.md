# Open Questions — NLPCC 2026 Shared Task 4

## A. Official-Task Questions

1. What are the exact turnover bucket definitions used in official evaluation?
2. Are turnover categories used as hard ranking divisions, secondary labels, or qualitative grouping for review?
3. Is the final official ranking based strictly on Sharpe ratio, or is there a composite rule involving return, drawdown, and turnover?
4. What is the exact B-list date range and whether `2026-01-01` to `2026-06-01` is inclusive on both ends?
5. Will the B-list fund universe exactly match the public candidate pools?
6. Can one team submit to both Track 1 and Track 2?
7. Are multiple candidate agents allowed, or must each team submit one final executable per track?
8. Are closed LLM APIs allowed at B-list runtime if the model existed before 2026?
9. Are participants expected to provide Docker images, lockfiles, full source code, model weights, or all of these?
10. What exact files are required for A-list submission: trades, target weights, holdings, raw model outputs, logs, or backtest result JSON?
11. What is the exact system-report schedule, format, length, and selection process?
12. Are system reports voluntary for selected teams or expected from all teams?
13. Are additional public datasets allowed if fully pre-2026 and submitted with preprocessing scripts?
14. How will organisers verify pre-2026 resource availability for model weights and retrieval indices?
15. Are cached LLM outputs from 2024/2025 news acceptable if generated after 2025 using a pre-2026 model?

## B. Repository-Structure Questions

1. In the actual repo, are the three prompt files present under `docs/prompts/`, or only referenced in `Workflow.md` and repo-analysis docs?
2. Should existing flat `docs/` files be physically moved into `docs/research/`, `docs/strategy/`, and `docs/prompts/`, or should movement wait until after starter reproduction?
3. Should `outputs/` be git-ignored entirely, or should selected report tables be committed under `docs/reports/`?
4. Should `configs/` use YAML, JSON, or Python dataclass-style configs?
5. Should official fund universes be imported/mirrored from `NLPCC_tasks/server_platform/app/core/fund_info.py`, or copied into versioned config files?
6. How should duplicated README filenames be resolved when syncing uploaded docs back into the repo?
7. Should local experiment scripts live under `scripts/` or `tools/`?
8. Should generated LLM extraction caches live under `outputs/cache/` or a separate `.var/cache/` style directory?
9. Should report generation live under `src/nlpcc4/reports/` or outside the package as scripts?
10. What is the minimum repo skeleton before asking a coding agent to implement Phase 1?

## C. Methodology Questions

1. How should the S1 quant core be exactly defined for Track 1 and Track 2?
2. Which volatility lookback windows should be used for inverse-vol and risk-parity baselines?
3. Which momentum horizons should be included: 20/60/120 trading days, or a smaller set for robustness?
4. Should robust BL use absolute views, relative views, or both?
5. How should news-derived confidence be mapped into `Ω_t` for Black-Litterman?
6. Should robust BL use Wasserstein DRO, ellipsoidal ambiguity, shrinkage of views, or a simpler confidence-capped posterior first?
7. Should the risk-parity anchor be equal risk contribution, inverse volatility, or a constrained risk-budget version?
8. Should ARMOR-OMD operate over raw ETF weights or over complete allocator sleeves?
9. Should retrieval analogues use text embeddings, event tuple features, market-state features, or a hybrid distance?
10. How should BSA-RP define regimes: macro regimes, volatility regimes, policy regimes, or mixed latent states?
11. Is HGF-MPC sufficiently different from BSA-RP to justify a separate build?
12. Should LEEQA-Rank train on forward returns, risk-adjusted forward returns, pairwise ETF rankings, or portfolio utility?
13. Should KG-MoE-Lite begin with a static hand-built ETF-sector-policy graph or a price-correlation graph?
14. How should causal/invariant models avoid overclaiming causality from observational data?
15. Which methods should be report-centrepiece modules versus production allocation modules?

## D. Implementation Questions

1. What exact input object should the official wrapper pass into `src/nlpcc4/` each day?
2. What should the canonical daily state schema be for news, market state, text state, and portfolio state?
3. How should target weights be translated into official buy-by-cash and sell-by-percentage instructions under cash constraints?
4. How should same-day sale proceeds be handled in the target-weight adapter?
5. How should failed or partially executed trades be detected and reconciled?
6. How should daily logs store:
   - raw news IDs;
   - extracted event records;
   - text-state vectors;
   - risk-state features;
   - target weights;
   - executed trades;
   - fallback reason codes?
7. Should the first implementation use pure deterministic rules before adding LLM extraction?
8. Should LLM extraction be cached by news ID / date / source / model / prompt hash?
9. What is the exact no-internet B-list fallback path?
10. What unit tests are mandatory before any model backtest is trusted?
11. Should the local evaluator call the official HTTP server or directly reuse `dataloader_eval.py` for faster experiments?
12. How should random seeds and deterministic sorting be enforced across modules?
13. What failure should trigger immediate fallback to S1?
14. How should performance metrics be computed independently from official minimal result objects?
15. How should ablations be automated without creating a fragile experiment framework too early?

## E. B-list / Submission Questions

1. What final package structure will organisers require?
2. Can the submitted code import modules from repo-root `src/`, or must everything be under `NLPCC_tasks/agent_platform/agents/`?
3. Does the organiser execution environment allow internet access?
4. Are GPU dependencies allowed or should the final package be CPU-only?
5. What is the maximum acceptable runtime per full B-list evaluation?
6. How should local caches be included or rebuilt in the submitted package?
7. If a local embedding model is used, must the model weights be included or can they be downloaded from a pre-2026 source at runtime?
8. Are pretrained models with post-2025 release dates prohibited even if they are not trained on market data?
9. Can a manually curated ETF-sector-policy taxonomy be submitted if created during the competition, provided it only uses pre-2026 public information?
10. How will organisers handle dependency conflicts with the starter kit?
11. Will organisers use exactly the same `DataLoader` and trade engine as the released starter kit?
12. Will B-list news contain the same columns and source names as public 2024/2025 data?
13. How should the system handle missing news, empty Top-20 lists, missing price rows, suspended assets, or zero-volume days?
14. What exact output logs are needed to support the system report?
15. Can final Track 1 and Track 2 submissions share one codebase with track-specific config?

## F. Questions to Defer

1. Whether to implement full KG-MoE with trainable GNN layers.
2. Whether to implement full transformer-style event memory / TEMA.
3. Whether to implement deep RL or graph RL.
4. Whether to fine-tune a Chinese financial LLM.
5. Whether to train a neural event encoder rather than use rule/embedding features.
6. Whether to build a full causal SCM rather than a causal/invariant diagnostic layer.
7. Whether to add a UI/dashboard for daily reasoning traces.
8. Whether to package polished report figures before a stable production candidate exists.
9. Whether to use GPU acceleration for experiments.
10. Whether to optimise for both tracks equally or specialise after early backtest evidence.
