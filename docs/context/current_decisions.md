# Current Decisions — NLPCC 2026 Shared Task 4

## A. Decisions Already Made

1. **Use a four-stage modular architecture.**

   ```text
   News Processing
   → Quantified Text Data Storage Medium
   → Trade Data Processing
   → Final Trading Agent
   ```

2. **Use a stage-first implementation layout, not a track-first layout.**

   Track 1 and Track 2 should share stage modules wherever possible. Track-specific logic should be handled through configs, track adapters, or small track-specific modules.

3. **Keep official starter materials preserved.**

   `NLPCC_tasks/` should be treated as upstream starter/reference code. Avoid changing official files unless required for compatibility.

4. **Use a thin official-facing submitted agent.**

   The submitted wrapper should live at:

   ```text
   NLPCC_tasks/agent_platform/agents/build_agent.py
   ```

   It should call reusable logic from `src/nlpcc4/`, not contain the whole model.

5. **Place reusable implementation under repo-root `src/nlpcc4/`.**

   The package should contain reusable stage modules, portfolio logic, execution adapters, metrics, and report tooling.

6. **Keep documentation under `docs/`, prompts under `docs/prompts/`, and generated outputs under `outputs/`.**

   Generated caches, logs, and backtest artifacts should not be committed into official dataset folders or mixed into source code.

7. **Build Stage 3 + S0/S1 before fancy news.**

   The market/risk state and baseline ladder must be correct before any text-aware method is meaningful.

8. **Build robust Black-Litterman first.**

   The first complete innovative prototype should be **DRO-BL-RP / M1 robust BL**, using structured news views, confidence matrix `Ω_t`, shrinkage covariance, risk-parity/S1 anchor, and turnover control.

9. **Keep S1 and no-LLM fallback mandatory.**

   The final system must be able to run without external LLM calls and must be able to fall back to conservative baseline allocation.

10. **Reject direct LLM allocation as a production architecture.**

    It remains useful only as a baseline or negative control.

11. **Preserve broad method coverage.**

    The project should document robust BL, risk parity, belief-state models, HMM/Kalman/MPC, graph/KG systems, retrieval memory, transformer-style memory, OCO, learning-to-rank, causal/invariant models, rule-based baselines, no-LLM baselines, rejected direct LLM allocation, and deferred deep RL/graph RL.

12. **Treat 2025 as public evaluation, not free training data.**

    The main tuning and model selection discipline should rely on 2024 walk-forward experiments and conservative validation logic.

## B. Decisions Still Tentative

1. **Second full innovative prototype.**

   Current candidates:

   - **ARMOR-OMD** if baseline sleeves show regime-dependent strengths;
   - **BSA-RP** if regime posterior signals are stable and interpretable.

2. **Track 2 second-wave architecture.**

   Current candidates:

   - **LEEQA-Rank** for a practical one-student sector-ranker extension;
   - **KG-MoE-Lite** for a stronger report/visual centrepiece after mappings are stable.

3. **Use of local LLM / open-source Chinese-finance model.**

   The final B-list path should avoid closed online API dependency if possible, but exact model choice remains open.

4. **How much causal/graph work to implement.**

   CEVA-KF/CIGA and KG-MoE-Lite are high-report-value ideas, but should remain lightweight until S1/DRO/OCO evidence justifies further build time.

5. **Amount of retrieval memory to include.**

   Retrieval analogue memory is useful inside ARMOR-OMD, but a full transformer-style event-memory system is deferred unless implementation bandwidth expands.

6. **Exact baseline promotion thresholds.**

   Promotion gates are conceptually decided, but numerical thresholds should be finalised after official starter reproduction and baseline backtests.

## C. Decisions That Should Not Be Reopened Without New Evidence

1. **Do not make direct LLM allocation the production strategy.**

   This should only be revisited if official evaluation or a controlled ablation shows surprisingly strong, stable, reproducible, turnover-controlled performance.

2. **Do not put reusable implementation inside `NLPCC_tasks/agent_platform/agents/` beyond the thin wrapper.**

   That location should remain official-facing compatibility code, not the core package.

3. **Do not start with full KG-MoE, full causal IRM, full TEMA, or deep RL.**

   These are not first-cycle production builds. They can be preserved as deferred/report-centrepiece modules.

4. **Do not bypass the official DataLoader or reconstruct current-day fields from raw CSVs.**

   All designs must centralise data access through a safe adapter that mirrors official behaviour.

5. **Do not use 2026 or post-2025 information, model weights, external data, or retrieval corpora.**

   This is a hard compliance boundary.

6. **Do not tune aggressively on 2025 A-list.**

   2025 should remain a quasi-out-of-sample public evaluation period to protect hidden B-list robustness.

7. **Do not rely on same-day sells to finance same-day buys.**

   Trade conversion must respect the official buy-cash / sell-percentage semantics and Q&A warning that sale proceeds are not immediately usable for same-day buys.

## D. Decisions That Require Official Verification

1. **Exact turnover categories and whether they are hard buckets or descriptive sub-rankings.**
2. **Exact final packaging requirements, Docker format, and dependency submission rules.**
3. **Whether closed LLM APIs are permitted during B-list central execution.**
4. **Whether multiple agents, multiple tracks, or both tracks may be joined by one team.**
5. **Exact system-report timeline and whether the report is mandatory, optional, or by invitation.**
6. **Exact accepted format for A-list prediction files and intermediate logs.**
7. **Whether the public Track 2 pool is 14 or 16 instruments in final evaluation; uploaded documents contain both approximations and explicit starter-kit pool listings.**
8. **Whether the hidden B-list fund universe can differ from the public candidate pool.**
9. **Whether official APIs expose any convenience fields that should be ignored for leakage safety.**
10. **Whether current-day portfolio valuation fields may contain current close values and must therefore be excluded from feature construction.**

## E. Recommended Next Actions

1. **Recover missing prompt documents from the repo.**

   Locate and inspect:

   ```text
   docs/prompts/prompt00_repo_structure_analysis_and_main_code_placement.md
   docs/prompts/prompt_02_synthesis_final_strategy_selection.md
   docs/prompts/prompt_03_four_stage_modular_reorganisation.md
   ```

2. **Create `docs/context/` in the actual repo and add these four context files.**

3. **Run official starter reproduction.**

   Confirm local environment, server startup, demo backtest execution, track selection, trade schema, result logs, and resume behaviour.

4. **Build the repo skeleton only after official starter reproduction is understood.**

   Add `src/nlpcc4/`, `configs/`, `tests/`, and `outputs/` without disturbing official starter files.

5. **Implement the data contract and leakage guard before any alpha logic.**

   Define safe fields, unsafe fields, date split rules, and timestamp rules.

6. **Implement Stage 3 and S0/S1 baselines.**

   Required baselines:

   - equal weight;
   - inverse-volatility;
   - momentum;
   - sector trend-following;
   - low-turnover persistence;
   - rule-based macro rotation;
   - no-news S1 quant core.

7. **Implement the official trade adapter.**

   Validate target-weight conversion into buy amounts and sell percentages, cash constraints, buy/sell order, and reconciliation logs.

8. **Only then build Stage 1 news MVP and Stage 2 text store.**

   Start with deterministic/rule-assisted extraction and flat stores, not heavy LLM systems.

9. **Build M1 robust BL first.**

   Add ablations before adding more sophisticated systems.

10. **Use a promotion gate.**

    If M1 does not beat or nearly match S1 after costs and drawdown, either fix view quality or keep S1/OCO as production and write the innovation as a negative-result report.
