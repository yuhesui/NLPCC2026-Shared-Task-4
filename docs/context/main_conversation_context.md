# Main Conversation Context 鈥?NLPCC 2026 Shared Task 4

## A. Project Objective

This project is for **NLPCC 2026 Shared Task 4: LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market**.

The objective is to build a **modular, leakage-safe, reproducible, and report-worthy investment-advisor agent** for two tracks:

1. **Track 1 鈥?Macro-Asset Allocation**: daily allocation across broad macro ETF/index instruments, including equity indices, treasury bonds, gold, and major style/thematic baskets.
2. **Track 2 鈥?Sector-Rotation Allocation**: daily allocation across industry/thematic ETFs, with stronger sensitivity to sector policy, supply-chain narratives, and thematic rotations.

The project should not become a generic 鈥淟LM says buy/sell鈥?system. The working thesis is:

> A competitive LLM investment advisor should convert financial hot news into bounded, auditable, structured signals; deterministic portfolio mathematics should make the final allocation and execution decision.

This chat should act as the **central control line** for future work. It should preserve the research state, prevent repeated reopening of settled architecture decisions, generate bounded implementation prompts, and maintain a conservative distinction between:

- **official facts** from task materials and Q&A;
- **research-report claims** from deep-research documents;
- **current synthesis decisions** made by this project.

## B. Official Task Constraints

The following items should be treated as **official or near-official constraints** when supported by the uploaded README, starter-kit README, dataset README, and Q&A/demo notes.

### Core task setting

- The task is a daily-frequency Chinese-market asset-allocation competition.
- Agents receive:
  - daily **Top-20 financial hot news**;
  - historical ETF/index price data;
  - portfolio state through the official platform.
- Agents produce daily rebalancing / trading instructions for predefined ETF pools.
- The competition has two tracks:
  - **Track 1: Macro-Asset Allocation**;
  - **Track 2: Sector-Rotation Allocation**.

### Data split

- **2024**: public training / construction period.
- **2025**: public A-list / Phase A evaluation period.
- **2026-01-01 to 2026-06-01**: hidden B-list evaluation period.
- B-list is run centrally by the organisers using submitted code.

### Leakage constraints

- At decision time, the agent must not use current-day `close`, `high`, `low`, `change`, `pctchange`, or return.
- The official DataLoader exposes full historical data for prior trading days and only current-day open for the current decision date.
- Same-day news is usable only under the official timestamp cutoff; the uploaded dataset documentation and Q&A repeatedly state the **15:00 same-day news cutoff**.
- Participants are strongly encouraged to reuse the official DataLoader instead of hand-writing date/news slicing logic.
- External signals, training labels, knowledge bases, or forecasts that would only be available after the decision timestamp are prohibited.

### Trading and execution constraints

- Initial capital is **100,000 CNY**.
- Transaction friction is **0.01%** per trade.
- Trading frequency is daily.
- Execution price is the same trading day close / adjusted close where applicable.
- The official trade abstraction is not direct target weights:
  - buys are by **cash amount**;
  - sells are by **percentage of current holding**.
- The Q&A/demo notes state that same-day sale proceeds cannot be used for same-day buys; buys use currently available cash only.
- The trade adapter must therefore account for buy-before-sell or delayed-cash semantics and should not assume exact instantaneous target-weight tracking.

### Evaluation and submission constraints

- Evaluation emphasises:
  - Sharpe ratio;
  - cumulative return;
  - maximum drawdown;
  - turnover categories or turnover-aware comparison.
- If using training, fine-tuning, retrieval, or knowledge construction, the full data, preprocessing, dependencies, and reproducible environment must be submitted.
- External models, datasets, and knowledge bases must be available before 2026.
- The final system report / shared-task paper may include not only top-ranked systems but also selected reports that are creative or especially informative.

### Items requiring official verification

The following should not be treated as fully settled unless confirmed from official repo materials or participant-group announcements:

- exact turnover bucket definitions;
- exact packaging format and Docker requirements;
- exact final system-report deadline and template requirements;
- whether multiple submissions, dual-track entries, or joint Track 1 + Track 2 participation are allowed;
- exact treatment of unavailable/deprecated ETF data or hidden-period ETF universe changes;
- whether closed API calls are acceptable at B-list runtime if the model existed before 2026.

## C. Completed Research Stage Summary

The initial research and planning stage has been completed. The following uploaded documents were available and reviewed as project sources:

- `DeepResearch_ChatGPT.md`
- `DeepResearch_Gemini-_21.md`
- `DeepResearch_Perplexity1.md`
- `DeepResearch_Perplexity2.md`
- `DeepResearch_Perplexity3.md`
- `nlpcc2026_task4_strategy_synthesis.md`
- `nlpcc2026_task4_four_stage_modular_strategy.md`
- `repo_structure_analysis.md`
- `Workflow.md`
- `README.md` uploaded as dataset/DataLoader README
- `README (1).md` uploaded as starter-kit README
- `NLPCCSharedTask4婕旂ず涓庣瓟鐤?md` uploaded as official/demo Q&A notes

The following files were referenced by project docs but were **not uploaded as standalone sandbox files** in this turn:

- `docs/prompts/prompt00_repo_structure_analysis_and_main_code_placement.md`
- `docs/prompts/prompt_02_synthesis_final_strategy_selection.md`
- `docs/prompts/prompt_03_four_stage_modular_reorganisation.md`

Their conclusions were available indirectly through `Workflow.md`, `repo_structure_analysis.md`, and the four-stage modular strategy document. They should be recovered from the repo in a future repo-inspection pass if exact prompt text is needed.

A root-level official `README.md` also appears in the parsed uploaded-file search results, but the local sandbox path `README.md` corresponds to the dataset/DataLoader README because of duplicate filename upload behaviour. Treat the root README content as available from the parsed file-search context, but not as a distinct local sandbox file in this turn.

### Research-stage synthesis

The deep-research reports broadly converge on the following conclusions:

1. **Direct LLM allocation is a rejected production design.** It is too prompt-sensitive, poorly risk-controlled, difficult to reproduce, and weakly aligned with the official execution semantics.
2. **The LLM should be a controlled extractor/verifier, not the final allocator.** Its best roles are event extraction, denoising, entity/sector mapping, regime classification, view confidence estimation, and explanation generation.
3. **The final allocator should be quantitative.** Robust Black-Litterman, risk parity, belief-state models, OCO/online mirror descent, learning-to-rank, graph systems, and causal/invariant filters remain the principal method families.
4. **The first production-quality system should be conservative.** It should be able to collapse to S1/no-LLM baselines if text signals are weak.
5. **Report value matters.** The system should log interpretable daily states, confidence matrices, view construction, regime beliefs, graph activations, expert weights, and fallback decisions where possible.

The synthesis document gives the highest immediate build priority to **DRO-BL-RP**, followed by **ARMOR-OMD**, **BSA-RP**, and then Track-2-specific LEEQA/KG-style methods.

## D. Current Strategy Conclusions

### Current first-build decision

The first complete innovative system should be:

```text
News Processing:
  denoising + event extraction + Black-Litterman view extraction

Quantified Text Storage:
  view matrix P_t, view vector q_t, confidence / uncertainty matrix 惟_t

Trade Data Processing:
  shrinkage covariance, inverse-volatility anchor, momentum, breadth, drawdown, turnover/cash feasibility

Final Trading Agent:
  robust Black-Litterman + risk-parity/S1 anchor + turnover control + hard fallback
```

This is the **DRO-BL-RP / M1 robust BL** path. It is preferred because it is mathematically serious, one-student feasible, compatible with the official trade engine, interpretable, and easy to ablate.

### Current second-build decision

The second major system should be one of:

1. **ARMOR-OMD**: retrieval analogue + online mirror descent / OCO ensemble over baseline sleeves, robust BL, defensive sleeves, and sector trend sleeves.
2. **BSA-RP**: belief-state / regime-aware risk-parity allocation using news as noisy observations of latent regimes.

The exact second-build order should depend on the first backtest evidence:

- choose **ARMOR-OMD** if multiple baseline sleeves show different regime strengths;
- choose **BSA-RP** if regime plots from news/price features are stable and interpretable.

### Current Track 2 conclusion

For Track 2, do not jump immediately to full KG-MoE. The practical path is:

1. build sector trend-following S1;
2. add sector impact extraction + ETF/sector mapping;
3. build **LEEQA-Rank** or **KG-MoE-Lite** only after S1 and DRO infrastructure are stable;
4. use KG-MoE-Lite as a report/visual centrepiece if time remains.

### Current report-centrepiece conclusion

The strongest research/report ideas are:

- **CEVA-KF / CIGA / causal-invariant event-impact maps**;
- **KG-MoE-Lite** graph activations and policy-to-sector transmission;
- **BSA-RP** belief trajectories;
- **ARMOR-OMD** expert weights and regret curves.

These should not consume first-cycle production time unless the baseline stack is already stable.

## E. Four-Stage Modular Architecture

All designs should be decomposed into the same four-stage interface:

```text
News Processing
鈫?Quantified Text Data Storage Medium
鈫?Trade Data Processing
鈫?Final Trading Agent
```

| Stage | Purpose | Inputs | Outputs | Main Risk | Fallback |
|---|---|---|---|---|---|
| Stage 1 鈥?News Processing | Convert raw Top-20 news into typed, validated financial observations. | Timestamp-safe official news before cutoff; frozen pre-2026 dictionaries/models. | Event tuples, macro tags, sector tags, relevance scores, BL views, regime observations, confidence flags. | Prompt instability, schema drift, hallucinated mapping, timestamp misuse. | Rule-based keyword tags, sentiment-only, or neutral no-news signals. |
| Stage 2 鈥?Quantified Text Data Storage Medium | Store structured news as numerical state for mathematical modules. | Stage 1 outputs across current and prior days. | Flat event panel, BL view store, confidence matrix, belief vector, decayed memory, retrieval index, KG, causal graph. | Over-complex stores that cannot be reproduced or ablated; hidden-period overfit. | Daily flat feature table + neutral confidence store. |
| Stage 3 鈥?Trade Data Processing | Convert official price and portfolio data into market/risk state. | Official historical prices, current-day open only, holdings, cash, previous weights/trades. | Returns, vol, covariance, momentum, drawdown, breadth, correlation graph, cash/turnover feasibility. | Future-price leakage; execution mismatch; wrong turnover/cost accounting. | S0/S1 quant core with inverse-vol, momentum, drawdown, turnover caps. |
| Stage 4 鈥?Final Trading Agent | Combine text and market state into target weights and executable official trades. | Stage 2 text state, Stage 3 market state, configs, previous portfolio. | Target weights, official buy/sell instructions, reason codes, fallback flags, logs. | Overfit optimiser, excessive turnover, direct LLM allocation, dependency failure. | Conservative ensemble or S1 fallback with low-turnover rebalancing. |

The architecture should remain **stage-first**, not track-first. Track 1 and Track 2 share most infrastructure but use separate configs, fund universes, and a small number of track-specific modules.

## F. Repository Placement Decision

The current repo policy is:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable implementation:
  src/nlpcc/

Local research/development tools:
  src/tools/

Documentation:
  docs/

Prompts:
  docs/prompts/

Generated outputs:
  outputs/
```

### Official-facing submitted agent

`NLPCC_tasks/agent_platform/agents/build_agent.py` should be a **thin compatibility wrapper**. It should:

1. receive official daily inputs;
2. load deterministic config;
3. call the reusable `src/nlpcc/` package;
4. convert target weights into official buy/sell trade schema;
5. return server-compatible instructions;
6. log bounded decision metadata where allowed.

It should not contain the model implementation.

### Reusable implementation package

The reusable competition system should live under `src/nlpcc/`, with stage-aligned modules:

```text
src/nlpcc/
  core/
  stage1_news/
  stage2_text_store/
  stage3_trade/
  stage4_agent/
  portfolio/
  execution/
  tracks/
  runtime/
```

Local research and development infrastructure should live under `src/tools/`:

```text
src/tools/
  data_tools/
  backtesting/
  optimiser/
  experiments/
  reporting/
  verification/
  utils/
```

### Config and tests

Use config separation rather than track-first source-code duplication:

```text
configs/
  stage1_news/
  stage2_text_store/
  stage3_trade/
  stage4_agent/
  systems/
  tracks/
  tools/

tests/
  test_nlpcc/
  test_tools/
  test_integration/
```

Generated experiment logs, caches, feature matrices, report figures, and backtest results should go under `outputs/`, not under `src/`, `docs/`, or `NLPCC_tasks/dataset/`.

## G. Method Universe to Preserve

At the current stage, **including more methods is preferred**. This does not mean all methods should be implemented immediately. It means the project documentation, methodology, and prompt pack should preserve the broad method universe before later pruning.

| Method Family | Status | Intended Use |
|---|---|---|
| Equal weight / S0 | Core baseline | Sanity check, fallback floor. |
| Inverse volatility | Core baseline | Risk anchor and no-news comparator. |
| Momentum / breadth / defensive sleeve | Core baseline | S1 quant core, hard benchmark. |
| Sector trend-following | Core Track 2 baseline | Main hurdle for graph/rank/news systems. |
| Rule-based macro rotation | Baseline / fallback | Deterministic macro comparator. |
| News sentiment only | Baseline / negative control | Proves whether structured extraction beats simple sentiment. |
| No-LLM baseline | Core fallback | Required for reproducibility and B-list safety. |
| Robust Black-Litterman | Primary core build | First complete innovative system. |
| Risk parity | Core component | Anchor for BL, BSA, conservative fallback. |
| Belief-state risk parity | Secondary build | Interpretable regime/risk system. |
| HMM / Kalman / MPC | Secondary / report layer | Strong Track 1 mathematics; avoid first-cycle overbuild. |
| Sector graph systems | Secondary Track 2 build | Static graph / KG-MoE-Lite after baselines. |
| KG-MoE | Deferred / lite only first | Report visualisation and policy-to-sector routing; full GNN/MoE later. |
| Retrieval analogue memory | Secondary / OCO support | ARMOR-OMD retrieval prior, not generic RAG-to-weight. |
| Transformer-style event memory | Deferred / report ablation | Preserve as TEMA/RAMA-T concept; expensive as full core. |
| Online mirror descent / OCO ensemble | Core fallback / meta-allocator | Adaptive sleeve weights with turnover control. |
| Learning-to-rank | Secondary Track 2 | LEEQA-Rank after stable event extraction. |
| Causal / invariant event-impact model | Report-centrepiece / verifier | CEVA-KF/CIGA as narrative and gating layer; avoid overclaiming. |
| Generic RAG summariser | Rejected or ablation-only | Too weak without formal allocator. |
| Direct LLM allocator | Rejected baseline | Useful only to show what not to do. |
| Deep RL / graph RL | Deferred / high-risk | Preserve for future research only; not first-cycle production. |

## H. Current Build Priority

The current recommended build order is:

1. **Official starter reproduction**: run starter server/client; verify both tracks; save logs.
2. **Repo skeleton and import boundary**: create `src/nlpcc/`, `src/tools/`, configs, tests, and thin official wrapper.
3. **Data contract and leakage guard**: centralise all safe field definitions; prevent raw CSV bypass.
4. **Stage 3 trade processing + S0/S1 baselines**: equal weight, inverse-vol, momentum, sector trend, breadth, drawdown, covariance, turnover state.
5. **Official trade adapter**: target weights 鈫?buy amount / sell percentage; cash feasibility; no overspend.
6. **Stage 1 news processing MVP**: denoising, event tuples, entity/sector mapping, BL-view schema, validator.
7. **Stage 2 text storage MVP**: flat event table, BL view store, confidence/uncertainty matrix, decayed memory.
8. **DRO-BL-RP Track 1 system**: robust BL with RP/S1 anchor and turnover penalty.
9. **Track 2 sector system**: sector trend + rank/graph-lite tilt after baselines.
10. **OCO / conservative ensemble fallback**: adaptive weighting over S1/RP/BL/sector sleeves.
11. **Ablation suite and report artifacts**: no-news, no-LLM, no-DRO, no-turnover, fallback-only, etc.
12. **B-list hardening and final packaging**: deterministic seeds, dependency lock, no-internet test, crash fallback, Docker/package instructions.

## I. Known Risks and Hard Constraints

### Hard constraints

- No current-day close/high/low/return before decision time.
- Same-day news must respect the official timestamp cutoff.
- No post-2025 or 2026-aware external data, model weights, retrieval corpus, or manually added knowledge.
- The final system must be runnable by organisers on hidden B-list data.
- Runtime dependencies, model weights, retrieval indices, and preprocessing scripts must be reproducible if used.
- All trading decisions must be convertible to official buy-by-cash and sell-by-percentage semantics.

### Key risks

| Risk | Why It Matters | Mitigation |
|---|---|---|
| Future leakage | Invalidates results and likely disqualifies submission. | Central data contract, official DataLoader wrapper, tests for safe fields. |
| Same-day execution mismatch | Target weights may not be attainable because sale proceeds are not immediately available. | Conservative target-weight adapter, staged rebalancing, no-overspend checks. |
| Prompt instability | LLM outputs can drift and break schemas. | Schema validation, deterministic local extraction, caching, rule-based fallback. |
| Overfitting 2025 | Public A-list can become an implicit training set. | Treat 2025 as locked evaluation; tune on 2024 walk-forward; use simple hyperparameters. |
| Weak text value | News may not improve over S1. | Promotion gate; no-news and no-LLM ablations; fallback to S1/OCO. |
| Excessive turnover | Hurts Sharpe and turnover category. | Turnover penalty, rebalancing threshold, low-turnover persistence. |
| Tool dependency risk | B-list environment may not support heavy external APIs. | No-API execution path, local/frozen models, deterministic fallback. |
| Causal/graph overclaiming | Strong narrative may not be empirically justified. | Treat causal/KG modules as verifiers/visualisations until ablations validate them. |
| Deep RL fragility | Small sample, high overfit, hard reproducibility. | Defer; keep as future work only. |

## J. How Future AI Prompts Should Use This Context

Future AI prompts should:

1. read this context first;
2. treat official constraints as non-negotiable;
3. avoid reopening the four-stage architecture or repo placement decision unless new official evidence appears;
4. preserve broad method coverage in documentation even when implementation focuses on a small first build;
5. distinguish official facts, report claims, and project synthesis decisions;
6. prioritise leakage safety, reproducibility, ablation readiness, and B-list robustness;
7. avoid implementing code directly in the main strategic conversation;
8. create bounded specialist prompts for implementation phases;
9. require each implementation agent to report changed files, tests run, caveats, and next steps;
10. prefer a robust S1/DRO/OCO production system over a fragile but novel graph/causal/LLM-heavy submission.

The central operating principle is:

> Build the official-safe quantitative backbone first; add LLM/news modules only through validated, bounded, ablatable interfaces.
