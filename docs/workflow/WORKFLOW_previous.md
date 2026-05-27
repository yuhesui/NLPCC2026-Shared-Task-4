# Workflow.md — NLPCC 2026 Shared Task 4 AI-Assisted Build Workflow

## 0. Purpose

This document defines a structured AI-assisted workflow for building the **NLPCC 2026 Shared Task 4** project:

> **LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market**

The workflow is designed for a one-student quant/LLM-systems build, where AI is used not as an uncontrolled coder, but as a structured research, planning, implementation, verification, and documentation assistant.

The project goal is to build a modular, reproducible, leakage-safe, and report-worthy competition system for:

1. **Track 1 — Macro-Asset Allocation**
2. **Track 2 — Sector-Rotation Allocation**

The current recommended architecture is:

```text
News Processing
→ Quantified Text Data Storage Medium
→ Trade Data Processing
→ Final Trading Agent
```

The current recommended repository policy is:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable implementation package:
  src/nlpcc4/

Project documentation:
  docs/

Prompts:
  docs/prompts/

Generated outputs:
  outputs/
```

This document should be treated as the central workflow reference for future AI-assisted implementation prompts.

---

## 1. Current Project Status

### 1.1 Completed Research and Planning Stage

The initial research and synthesis stage has already been completed.

The following research and strategy documents have been produced or reviewed:

```text
docs/
  DeepResearch_ChatGPT.md
  DeepResearch_Gemini-_21.md
  DeepResearch_Perplexity1.md
  DeepResearch_Perplexity2.md
  DeepResearch_Perplexity3.md
  nlpcc2026_task4_strategy_synthesis.md
  nlpcc2026_task4_four_stage_modular_strategy.md
  prompt_02_synthesis_final_strategy_selection.md
  prompt_03_four_stage_modular_reorganisation.md
  prompt00_repo_structure_analysis_and_main_code_placement.md
  repo_structure_analysis.md
```

The completed research stage produced the following high-level conclusions.

#### Strategy-Level Conclusions

The strategy universe has been consolidated from full-system names into modular components:

| Original Strategy Family | Current Interpretation |
|---|---|
| DRO-BL / DRO-BL-RP | Robust Black-Litterman final allocation engine using structured views and confidence matrices. |
| BSA-RP | Belief-state / regime-aware risk-parity allocator. |
| HGF-MPC | Latent drift / Kalman-HMM / model-predictive allocation controller. |
| KG-MoE | Track 2 graph-based sector allocator with mixture-of-experts routing. |
| TEMA / RAMA-T | Transformer-style event memory or retrieval memory system. |
| ARMOR-SPO / OMD-RAG | Retrieval analogue + online meta-allocation / mirror descent system. |
| OCO-Bandit / OCO-Ensemble | Conservative online ensemble and fallback controller. |
| LEEQA | Structured LLM event extraction + learning-to-rank allocator. |
| CEVA-KF / CIRM / CIGA | Causal/invariant event-impact modelling family. |
| Regime-HMM-RP | Simple HMM or hidden-regime risk-parity allocator. |
| Pure LLM allocator | Rejected baseline only. |
| Simple BL with LLM views | Baseline/ablation only unless made robust. |
| Generic RAG summariser | Rejected or ablation only. |
| Deep RL / graph RL | Deferred due to implementation and overfit risk. |

#### Modular Architecture Conclusions

The previous strategy names should not be implemented as isolated monoliths. Instead, they should be decomposed into four stages:

```text
Stage 1 — News Processing
Stage 2 — Quantified Text Data Storage Medium
Stage 3 — Trade Data Processing
Stage 4 — Final Trading Agent
```

This is preferable because:

1. modules become swappable;
2. ablations become clean;
3. implementation can proceed stage by stage;
4. the final report becomes more convincing;
5. hidden B-list failure risk is reduced by fallback paths;
6. each module has a separate input, output, benchmark, and test surface.

#### Current Build Priority

The current recommended build priority is:

```text
1. Official starter reproduction
2. Repo skeleton and import boundary
3. Data contract and leakage guard
4. Stage 3 trade processing + S0/S1 baselines
5. Official trade adapter
6. Stage 1 news processing MVP
7. Stage 2 text storage MVP
8. Robust BL Track 1 system
9. Track 2 sector-rotation system
10. OCO / conservative ensemble fallback
11. Ablation suite and report artifacts
12. B-list hardening and final packaging
```

#### Current First Complete System

The first complete innovative system should be:

```text
News Processing:
  Event extraction + Black-Litterman view extraction

Text Storage:
  View matrix P_t, view vector q_t, confidence matrix Ω_t

Trade Processing:
  Shrinkage covariance, inverse-volatility anchor, momentum/risk state

Final Agent:
  Robust Black-Litterman with risk-parity/S1 anchor and turnover control
```

#### Current Second Complete System

The second complete system should be:

```text
News Processing:
  Sector impact extraction + ETF/sector mapping

Text Storage:
  Sector impact panel or lightweight sector event table

Trade Processing:
  Sector momentum, volatility, correlation graph

Final Agent:
  Sector top-k allocator with risk scaling and optional graph regularisation
```

#### Current Safe Fallback

The safe fallback should be:

```text
S1 quant core
+ conservative turnover control
+ OCO / ensemble wrapper
+ no-LLM or cached-LLM execution path
```

---

## 2. Workflow Philosophy

### 2.1 Main Conversation as the Control Line

This project should be run through one main strategic conversation.

The main conversation is responsible for:

1. deciding the next phase;
2. generating prompts;
3. reviewing implementation logs;
4. identifying missing tests;
5. judging whether a phase should be promoted, fixed, or abandoned;
6. maintaining architectural consistency;
7. preventing over-expansion into fragile systems;
8. ensuring that more candidate methods are considered before narrowing.

The main conversation should not directly become a messy implementation chat. It should operate as the project controller.

### 2.2 Specialist Chat Prompts as Work Units

Each work unit should be a prompt saved under:

```text
docs/prompts/
```

Each prompt should tell the AI assistant or coding agent to:

```text
1. read the relevant docs;
2. inspect the current repo;
3. implement or write only the requested bounded artifact;
4. avoid unsupported assumptions;
5. produce an implementation log;
6. state what was changed;
7. state what was not changed;
8. state tests run;
9. state caveats and next steps.
```

For early planning and document-generation stages, use **chat prompts** rather than coding prompts.

For coding implementation stages, use Codex/coding-agent prompts later.

### 2.3 Prefer Breadth Before Narrowing

At the current stage, **including more methods is preferred**.

This does not mean implementing every method. It means the documentation and starter kit should preserve a broad method universe so that later implementation decisions are informed.

Therefore:

- the methodology document should include more methods rather than only the first implementation target;
- the architecture document should show optional modules even if not built first;
- the README should explain the long-term system plan, not only the minimal baseline;
- the prompts should ask AI to compare and organise methods before pruning;
- rejected/deferred methods should still be documented as ablations, baselines, or future work.

This is especially important because system-report value may reward informative and creative designs, even if the final submitted agent is conservative.

---

## 3. AI Usage Levels

### 3.1 Light Prompting

Use light prompting for quick local decisions.

Examples:

```text
Should this module be under src/nlpcc4/agents or src/nlpcc4/portfolio?
Should Track 1 and Track 2 be separated by folders or configs?
Is this leakage-safe?
```

### 3.2 Mid Prompting

Use mid prompting for documentation and architecture planning.

Examples:

```text
Generate repo_structure_analysis.md.
Generate architecture.md.
Generate methodology.md.
Generate implementation plan.
Generate prompt packs.
```

### 3.3 Heavy Prompting

Use heavy prompting for actual implementation and verification.

Examples:

```text
Implement leakage guard + tests.
Implement Stage 3 price features + S1 baseline.
Implement official trade adapter + tests.
Implement robust BL agent + ablations.
Audit the repo for leakage and B-list reproducibility.
```

The current request belongs to **mid prompting**, because it generates planning documentation and starter prompts.

---

## 4. Repository and Agent Placement Policy

### 4.1 Official-Facing Agent

The official-facing build agent should live in:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
```

This file should be thin.

It should:

1. receive official daily inputs;
2. load configuration;
3. call the reusable `src/nlpcc4/` package;
4. convert target weights into official trades;
5. return server-compatible instructions;
6. log decisions if allowed.

It should not contain the full model implementation.

### 4.2 Reusable Development Package

Reusable code should live in:

```text
src/nlpcc4/
```

Recommended package structure:

```text
src/nlpcc4/
  core/
    data_contracts.py
    fund_universe.py
    leakage_guard.py

  news_processing/
    schema.py
    extractors.py
    relevance_filter.py
    view_extractor.py
    sector_mapper.py

  text_store/
    event_table.py
    view_matrix.py
    belief_state.py
    retrieval_index.py
    knowledge_graph.py

  trade_processing/
    price_features.py
    volatility.py
    covariance.py
    momentum.py
    drawdown.py
    breadth.py
    correlation_graph.py

  portfolio/
    constraints.py
    risk_parity.py
    black_litterman.py
    robust_optimizer.py
    turnover_control.py

  agents/
    baseline_s1.py
    robust_bl_agent.py
    belief_rp_agent.py
    graph_moe_agent.py
    oco_fallback_agent.py
    ensemble_agent.py

  execution/
    official_adapter.py
    target_weights.py
    trade_validator.py

  tracks/
    macro.py
    sector.py

  reports/
    artifacts.py
    metrics.py

  utils/
    io.py
    dates.py
    seeds.py
```

### 4.3 Track Separation Policy

Use a **stage-first structure** inside `src/nlpcc4/`, not a track-first structure.

Do not do this as the main layout:

```text
src/nlpcc4/
  track1/
    news_processing/
    trade_processing/
    agents/
  track2/
    news_processing/
    trade_processing/
    agents/
```

Instead, use shared stage modules and track-specific configs:

```text
configs/tracks/
  track1_macro.yaml
  track2_sector.yaml

configs/systems/
  s1_macro.yaml
  s1_sector.yaml
  robust_bl_track1.yaml
  sector_rotation_track2.yaml
  fallback_oco.yaml
```

Track-specific logic should only be placed under:

```text
src/nlpcc4/tracks/
  macro.py
  sector.py
```

or in specific final agents where the method is materially track-specific.

---

## 5. Detailed Phase Plan

## Phase 0R — Completed Research and Context Consolidation

### Status

Completed.

### Completed Inputs

```text
Deep research reports
Final strategy synthesis
Four-stage modular strategy document
Repo structure analysis
Q&A / official starter notes
Current conversation decisions
```

### Completed Outputs

```text
docs/nlpcc2026_task4_strategy_synthesis.md
docs/nlpcc2026_task4_four_stage_modular_strategy.md
docs/repo_structure_analysis.md
docs/prompts/prompt00_repo_structure_analysis_and_main_code_placement.md
```

### Main Decisions Reached

```text
1. Use four-stage modular architecture.
2. Put official-facing agent wrapper in NLPCC_tasks/agent_platform/agents/.
3. Put reusable implementation in repo-root src/nlpcc4/.
4. Build Stage 3 and S1 baselines before fancy news.
5. Build robust BL Track 1 first.
6. Build simplified sector Track 2 second.
7. Keep OCO/S1 fallback for production safety.
8. Defer KG-MoE, TEMA, causal graph, and deep RL until baseline is strong.
```

### Next Action

Generate starter project documentation and prompt pack.

---

## Phase 1R — Main Conversation Document Analysis

### Purpose

Use a chat model to analyse all current uploaded/project documents and produce a consolidated project context.

This should become the **main conversation context** for future implementation.

### Prompt File

```text
docs/prompts/prompt01_main_conversation_doc_analysis.md
```

### Output Documents

```text
docs/context/main_conversation_context.md
docs/context/current_decisions.md
docs/context/open_questions.md
docs/context/source_inventory.md
```

### Success Criterion

The main conversation can use the produced context to generate consistent future implementation prompts without re-reading all source documents every time.

---

## Phase 2R — Starter Kit Documentation Generation

### Purpose

Generate starter-kit Markdown files that explain the actual methodology, architecture, README, repo policy, and build plan.

This should be done in chat first, before asking a coding agent to implement code.

### Prompt File

```text
docs/prompts/prompt02_starter_kit_documentation_generation.md
```

### Output Documents

Recommended outputs:

```text
docs/starter_kit/
  README.md
  METHODOLOGY.md
  ARCHITECTURE.md
  IMPLEMENTATION_PLAN.md
  REPO_POLICY.md
  OFFICIAL_COMPATIBILITY.md
  FOUR_STAGE_SYSTEM.md
  TRACK_DESIGN.md
  ABLATION_PLAN.md
  B_LIST_HARDENING.md
```

If preferred, these may later be moved into:

```text
docs/architecture/
docs/strategy/
docs/reports/
```

but the starter-kit directory is useful as an initial clean documentation bundle.

### Success Criterion

A new AI assistant or coding agent can read these documents and understand:

1. the official task;
2. the four-stage architecture;
3. repo placement policy;
4. candidate methods;
5. first implementation target;
6. fallback strategy;
7. B-list reproducibility rules.

---

## Phase 3R — Official Starter Reproduction

### Purpose

Run and document the official starter before custom implementation.

### Key Actions

```text
1. Install dependencies.
2. Start official server.
3. Run demo backtest for Track 1.
4. Run demo backtest for Track 2.
5. Record logs and caveats.
6. Confirm trade schema and execution order.
```

### Deliverables

```text
docs/implementation_logs/phase03_official_starter_reproduction.md
outputs/backtests/phase03_official_starter/
```

### Success Criterion

At least one short Track 1 and one short Track 2 demo backtest run end-to-end.

### Stop Criterion

Do not implement custom strategy before starter reproduction works.

---

## Phase 4R — Repo Skeleton and Import Boundary

### Purpose

Create a clean package structure while preserving the official starter kit.

### Key Actions

```text
1. Create src/nlpcc4/ package skeleton.
2. Create official-facing build_agent.py wrapper.
3. Create configs/ skeleton.
4. Create tests/ skeleton.
5. Ensure imports work from official agent wrapper.
```

### Deliverables

```text
src/nlpcc4/
NLPCC_tasks/agent_platform/agents/build_agent.py
configs/
tests/
docs/implementation_logs/phase04_repo_skeleton.md
```

### Success Criterion

`build_agent.py` can import from `src/nlpcc4/` without fragile path hacks.

---

## Phase 5R — Data Contract and Leakage Guard

### Purpose

Prevent invalid features before any serious modelling.

### Key Files

```text
src/nlpcc4/core/data_contracts.py
src/nlpcc4/core/leakage_guard.py
tests/test_core/test_leakage_guard.py
```

### Required Rules

```text
1. No current-day close before decision time.
2. No current-day high before decision time.
3. No current-day low before decision time.
4. No current-day return before decision time.
5. Same-day news must respect official timestamp cutoff.
6. Strategy code should not bypass official DataLoader contracts.
7. Raw official data should never be modified.
```

### Success Criterion

Tests fail if future price fields are used as features before decision time.

---

## Phase 6R — Stage 3 Trade Processing and S0/S1 Baselines

### Purpose

Build the quantitative baseline before news/LLM modules.

### Key Files

```text
src/nlpcc4/trade_processing/price_features.py
src/nlpcc4/trade_processing/volatility.py
src/nlpcc4/trade_processing/covariance.py
src/nlpcc4/trade_processing/momentum.py
src/nlpcc4/trade_processing/drawdown.py
src/nlpcc4/agents/baseline_s1.py
configs/systems/s0_equal_weight.yaml
configs/systems/s1_macro.yaml
configs/systems/s1_sector.yaml
```

### Baselines

```text
S0 equal weight
Inverse volatility
Momentum-only
Track 1 S1 macro allocator
Track 2 S1 sector trend allocator
Persistence / low-turnover baseline
```

### Success Criterion

There are reproducible baseline metrics for 2024 and 2025:

```text
Sharpe
Cumulative return
Max drawdown
Turnover
Trade rejection count
Cash utilisation
```

---

## Phase 7R — Official Trade Adapter

### Purpose

Convert target weights into official buy/sell instructions safely.

### Key Files

```text
src/nlpcc4/execution/target_weights.py
src/nlpcc4/execution/official_adapter.py
src/nlpcc4/execution/trade_validator.py
tests/test_execution/test_official_adapter.py
```

### Important Rule

Do not assume same-day sells finance same-day buys.

The adapter should use only currently available cash for buy orders.

### Success Criterion

No invalid trades under baseline backtests, or all invalid trades are caught before server submission.

---

## Phase 8R — Stage 1 News Processing MVP

### Purpose

Convert Top-20 news into structured signals.

### Key Files

```text
src/nlpcc4/news_processing/schema.py
src/nlpcc4/news_processing/relevance_filter.py
src/nlpcc4/news_processing/event_extractor.py
src/nlpcc4/news_processing/view_extractor.py
src/nlpcc4/news_processing/sector_mapper.py
docs/prompts/news_event_extraction_v1.md
docs/prompts/bl_view_extraction_v1.md
```

### Candidate Methods to Document and Possibly Implement

At this stage, more methods should be listed than implemented.

Include:

```text
simple summarisation
sentiment classification
event tuple extraction
macro regime classification
sector impact extraction
BL view extraction
causal shock extraction
entity / sector / ETF mapping
news denoising and relevance filtering
LLM self-consistency / verifier-based extraction
rule-based no-LLM fallback
local embedding-based tagging
```

### Initial Implementation

Implement:

```text
1. schema validation
2. rule-based relevance filtering
3. event tuple schema
4. BL view extraction schema
5. cached LLM extraction interface if feasible
```

### Success Criterion

Every trading day produces valid structured news records or a clean empty/fallback state.

---

## Phase 9R — Stage 2 Quantified Text Storage MVP

### Purpose

Store structured news in a quantitative representation.

### Key Files

```text
src/nlpcc4/text_store/event_table.py
src/nlpcc4/text_store/view_matrix.py
src/nlpcc4/text_store/confidence_matrix.py
src/nlpcc4/text_store/belief_state.py
```

### Candidate Storage Media to Document

Include more methods than immediately implemented:

```text
daily flat feature table
decayed event memory
transformer-style key-value event memory
retrieval analogue index
regime posterior / belief state
Black-Litterman view store
ETF-sector-policy knowledge graph
causal event-impact graph
text-managed factor panel
uncertainty / confidence matrix
```

### Initial Implementation

Implement:

```text
1. daily event table
2. BL view matrix
3. confidence matrix
4. decayed belief state
```

### Success Criterion

For any date, the system can reconstruct:

```text
event records
P_t view matrix
q_t view vector
Ω_t confidence matrix
belief state
```

---

## Phase 10R — Stage 4 First Complete Agent: Robust BL Track 1

### Purpose

Build the first serious innovative system.

### Pipeline

```text
News Processing:
  event extraction + BL view extraction

Text Storage:
  P_t, q_t, Ω_t

Trade Processing:
  shrinkage covariance + momentum/risk state

Final Agent:
  robust BL + S1/risk-parity anchor + turnover control
```

### Key Files

```text
src/nlpcc4/portfolio/black_litterman.py
src/nlpcc4/portfolio/robust_optimizer.py
src/nlpcc4/portfolio/constraints.py
src/nlpcc4/portfolio/turnover_control.py
src/nlpcc4/agents/robust_bl_agent.py
configs/systems/robust_bl_track1.yaml
```

### Promotion Criterion

Promote if it:

```text
1. beats S1 on 2024 walk-forward, or
2. gives strong report-value ablations without worsening risk materially;
3. does not materially worsen turnover-adjusted Sharpe;
4. remains stable across subwindows;
5. can run without external unavailable API dependency.
```

---

## Phase 11R — Second System: Track 2 Sector Rotation

### Purpose

Build a simpler Track 2 system before full KG-MoE.

### Pipeline

```text
News Processing:
  sector impact extraction + ETF mapping

Text Storage:
  sector impact panel

Trade Processing:
  sector momentum + volatility + correlation graph

Final Agent:
  top-k sector allocator + risk scaling + turnover control
```

### Key Files

```text
src/nlpcc4/news_processing/sector_mapper.py
src/nlpcc4/text_store/sector_impact_panel.py
src/nlpcc4/trade_processing/correlation_graph.py
src/nlpcc4/agents/sector_rotation_agent.py
configs/systems/sector_rotation_track2.yaml
```

### Promotion Criterion

Promote only if it beats:

```text
equal weight
inverse volatility
sector momentum
S1 sector baseline
```

---

## Phase 12R — OCO / Conservative Ensemble Fallback

### Purpose

Make the final system safer under hidden B-list conditions.

### Key Files

```text
src/nlpcc4/agents/oco_ensemble.py
src/nlpcc4/agents/fallbacks.py
configs/systems/conservative_ensemble.yaml
```

### Base Allocators

```text
S0 equal weight
S1 macro
S1 sector
inverse volatility
momentum
robust BL
sector rotation
cash/defensive sleeve
```

### Success Criterion

The ensemble should reduce catastrophic failure risk and support fallback to S1 if text signals are weak.

---

## Phase 13R — Experiment and Ablation Suite

### Purpose

Produce competition and report evidence.

### Required Ablations

```text
S0 equal weight
S1 quant core
S1 + simple sentiment
S1 + event extraction
S1 + BL views
robust BL without robustness
robust BL without turnover control
robust BL no-LLM / rule-based views
Track 2 sector momentum
Track 2 sector impact panel
OCO ensemble
S1 fallback only
```

### Outputs

```text
outputs/experiments/
outputs/reports/
docs/reports/system_report_draft.md
docs/reports/ablation_summary.md
```

### Success Criterion

Each experiment has:

```text
config snapshot
date range
track
seed
metrics
output path
known caveats
```

---

## Phase 14R — B-List Hardening and Final Packaging

### Purpose

Prepare for blind central execution.

### Checklist

```text
No leakage
No current-day hidden price use
No same-day news cutoff violation
No unavailable API dependency
No invalid trades
No same-day-sell-funded buys
Deterministic configs and seeds
Docker or reproducible environment
Fallback-to-S1 behaviour
Complete logs and report artifacts
```

### Final Package Should Include

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc4/
configs/systems/final_submission.yaml
requirements.txt or dependency lock
Dockerfile or equivalent environment
docs/reports/system_report_draft.md
outputs/reports/final_ablation_tables/
```

---

## 6. Prompt Pack

Recommended prompt files:

```text
docs/prompts/
  prompt01_main_conversation_doc_analysis.md
  prompt02_starter_kit_documentation_generation.md
  prompt03_official_starter_reproduction.md
  prompt04_repo_skeleton_and_agent_boundary.md
  prompt05_data_contract_and_leakage_guard.md
  prompt06_stage3_trade_processing_and_s1.md
  prompt07_official_trade_adapter.md
  prompt08_stage1_news_processing_mvp.md
  prompt09_stage2_text_store_mvp.md
  prompt10_robust_bl_track1_agent.md
  prompt11_sector_rotation_track2_agent.md
  prompt12_oco_ensemble_fallback.md
  prompt13_experiment_ablation_suite.md
  prompt14_blist_hardening_and_final_audit.md
```

The first two prompts should be **chat prompts**, not coding prompts.

---

# Prompt 01 — Main Conversation Document Analysis

Save as:

```text
docs/prompts/prompt01_main_conversation_doc_analysis.md
```

```md
# Prompt 01 — Main Conversation Document Analysis

## Role

You are the main strategic conversation for this project.

Act as a senior quantitative research lead, LLM-systems architect, and repository planning reviewer.

This is a chat-only analysis task. Do not write implementation code.

## Objective

Analyse all uploaded and available project documents for the NLPCC 2026 Shared Task 4 project and produce a consolidated project context that can serve as the main conversation memory for all future work.

The goal is to make this chat the central control line for the project.

## Required Inputs to Read

Read all available project documents, especially:

- `docs/DeepResearch_ChatGPT.md`
- `docs/DeepResearch_Gemini-_21.md`
- `docs/DeepResearch_Perplexity1.md`
- `docs/DeepResearch_Perplexity2.md`
- `docs/DeepResearch_Perplexity3.md`
- `docs/nlpcc2026_task4_strategy_synthesis.md`
- `docs/nlpcc2026_task4_four_stage_modular_strategy.md`
- `docs/repo_structure_analysis.md`
- `docs/prompts/prompt00_repo_structure_analysis_and_main_code_placement.md`
- `docs/prompts/prompt_02_synthesis_final_strategy_selection.md`
- `docs/prompts/prompt_03_four_stage_modular_reorganisation.md`
- any official Q&A / demo notes if present
- any README files in the repo root and `NLPCC_tasks/`

If some files are missing, state that clearly and continue with available documents.

## Context to Preserve

The project is for NLPCC 2026 Shared Task 4:

- Track 1: Macro-Asset Allocation.
- Track 2: Sector-Rotation Allocation.
- Inputs: daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / construction.
- 2025 is public A-list / Phase A evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- If using training, fine-tuning, retrieval, or knowledge construction, the full data, preprocessing, dependencies, and reproducible environment must be submitted.
- Creative or especially informative system reports may be selected even if not top-ranked.

Do not convert uncertain report claims into official facts unless supported by official docs.

## Current Architectural Decision

The current intended architecture is four-stage modular:

```text
News Processing
→ Quantified Text Data Storage Medium
→ Trade Data Processing
→ Final Trading Agent
```

The current intended repo policy is:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable implementation:
  src/nlpcc4/

Docs:
  docs/

Prompts:
  docs/prompts/

Outputs:
  outputs/
```

## Important Instruction

At the current stage, including more methods is preferred.

Do not prematurely narrow the method universe. You should preserve a broad set of plausible methods, even if they are later marked as deferred, ablation-only, or rejected.

In particular, include and classify:

- robust Black-Litterman;
- risk parity;
- belief-state models;
- HMM / Kalman / MPC;
- sector graph systems;
- KG-MoE;
- retrieval analogue memory;
- transformer-style event memory;
- online mirror descent / OCO ensemble;
- learning-to-rank;
- causal/invariant event-impact models;
- rule-based baselines;
- no-LLM baselines;
- direct LLM allocator as rejected baseline;
- deep RL / graph RL as deferred or high-risk methods.

## Required Output

Produce the following Markdown files conceptually. If you can write files, write them. If not, output their full contents in chat.

```text
docs/context/main_conversation_context.md
docs/context/current_decisions.md
docs/context/open_questions.md
docs/context/source_inventory.md
```

## Required Structure for `main_conversation_context.md`

Use exactly these sections:

A. Project Objective  
B. Official Task Constraints  
C. Completed Research Stage Summary  
D. Current Strategy Conclusions  
E. Four-Stage Modular Architecture  
F. Repository Placement Decision  
G. Method Universe to Preserve  
H. Current Build Priority  
I. Known Risks and Hard Constraints  
J. How Future AI Prompts Should Use This Context  

## Required Structure for `current_decisions.md`

Use exactly these sections:

A. Decisions Already Made  
B. Decisions Still Tentative  
C. Decisions That Should Not Be Reopened Without New Evidence  
D. Decisions That Require Official Verification  
E. Recommended Next Actions  

## Required Structure for `open_questions.md`

Use exactly these sections:

A. Official-Task Questions  
B. Repository-Structure Questions  
C. Methodology Questions  
D. Implementation Questions  
E. B-list / Submission Questions  
F. Questions to Defer  

## Required Structure for `source_inventory.md`

Use this table:

| Source | Type | Current Location | What It Contributes | Reliability | How It Should Be Used |
|---|---|---|---|---|---|

## Style Requirements

- Be specific.
- Be conservative.
- Distinguish official facts, report claims, and current synthesis decisions.
- Preserve broad method coverage.
- Do not implement code.
- Do not delete or move files.
- Do not invent missing official facts.
- Mark uncertainty clearly.
```

---

# Prompt 02 — Starter Kit Documentation Generation

Save as:

```text
docs/prompts/prompt02_starter_kit_documentation_generation.md
```

```md
# Prompt 02 — Starter Kit Documentation Generation

## Role

You are a senior quantitative research lead, LLM-systems architect, and technical documentation architect.

This is a chat-only documentation task. Do not write implementation code.

## Objective

Generate a starter documentation kit for the NLPCC 2026 Shared Task 4 project.

The documentation should translate the current discussion, uploaded reports, repo analysis, and modular strategy plan into clear Markdown files that future coding agents can use.

The goal is to prepare the repository for implementation, not to implement the system yet.

## Required Inputs to Read

Read all available project context, especially:

- `docs/context/main_conversation_context.md` if available;
- `docs/context/current_decisions.md` if available;
- `docs/context/open_questions.md` if available;
- `docs/context/source_inventory.md` if available;
- `docs/repo_structure_analysis.md`;
- `docs/nlpcc2026_task4_strategy_synthesis.md`;
- `docs/nlpcc2026_task4_four_stage_modular_strategy.md`;
- all prior deep research reports under `docs/`;
- official task README files;
- official Q&A/demo notes if available;
- the current discussion about putting the official-facing agent in `NLPCC_tasks/agent_platform/agents/` and reusable implementation in `src/nlpcc4/`.

If some files are missing, state this clearly and proceed with available context.

## Core Context

This project is for NLPCC 2026 Shared Task 4:

- Track 1: Macro-Asset Allocation.
- Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / agent construction.
- 2025 data is public A-list / Phase A evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- If using training, fine-tuning, retrieval, or knowledge construction, the full data, preprocessing, dependencies, and reproducible environment must be submitted.
- Creative or especially informative system reports may be selected even if not top-ranked.

## Current Architecture

The project should use a four-stage architecture:

```text
Stage 1 — News Processing
Stage 2 — Quantified Text Data Storage Medium
Stage 3 — Trade Data Processing
Stage 4 — Final Trading Agent
```

Current placement policy:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable implementation:
  src/nlpcc4/

Configuration:
  configs/

Tests:
  tests/

Docs:
  docs/

Prompts:
  docs/prompts/

Generated outputs:
  outputs/
```

## Important Instruction

At the current stage, including more methods is preferred.

The starter documentation should preserve a broad method universe. Do not only document the first implementation target.

Include more candidate methods, then classify them as:

- core build;
- secondary build;
- fallback;
- ablation only;
- deferred;
- rejected.

Methods to include:

- S0 equal weight;
- S1 quant core;
- inverse volatility;
- momentum;
- sector trend-following;
- robust Black-Litterman;
- risk parity;
- belief-state risk parity;
- HMM / Kalman / MPC;
- sector impact model;
- KG-MoE;
- retrieval analogue memory;
- transformer-style event memory;
- OCO / online mirror descent ensemble;
- learning-to-rank;
- causal/invariant event-impact model;
- rule-based news extraction;
- LLM event extraction;
- no-LLM fallback;
- generic RAG summariser as weak baseline;
- pure LLM direct allocator as rejected baseline;
- deep RL / graph RL as high-risk deferred method.

## Required Output Files

Produce the full contents of the following Markdown files:

```text
docs/starter_kit/README.md
docs/starter_kit/METHODOLOGY.md
docs/starter_kit/ARCHITECTURE.md
docs/starter_kit/IMPLEMENTATION_PLAN.md
docs/starter_kit/REPO_POLICY.md
docs/starter_kit/OFFICIAL_COMPATIBILITY.md
docs/starter_kit/FOUR_STAGE_SYSTEM.md
docs/starter_kit/TRACK_DESIGN.md
docs/starter_kit/ABLATION_PLAN.md
docs/starter_kit/B_LIST_HARDENING.md
```

If writing files is available, create these files. If not, output the full Markdown contents in chat.

## File Requirements

### `README.md`

Must include:

- project purpose;
- official task summary;
- current architecture summary;
- quick start placeholder;
- repo layout;
- first build target;
- current method universe;
- documentation map.

### `METHODOLOGY.md`

Must include:

- broad candidate method universe;
- four-stage decomposition;
- Track 1 methods;
- Track 2 methods;
- fallback methods;
- rejected/deferred methods;
- why direct LLM allocation is rejected;
- why more methods are preserved at this stage;
- promotion criteria.

### `ARCHITECTURE.md`

Must include:

- high-level system graph;
- official-facing wrapper vs reusable package;
- stage-by-stage architecture;
- config flow;
- output flow;
- logging/reporting flow;
- deterministic vs agentic components.

### `IMPLEMENTATION_PLAN.md`

Must include:

- completed research stage;
- current phase plan;
- exact build order;
- success criteria;
- stop criteria;
- verification prompts to run after implementation phases.

### `REPO_POLICY.md`

Must include:

- where code belongs;
- where docs belong;
- where prompts belong;
- where outputs belong;
- what should not go under `docs/`;
- what should not go under official starter files;
- import boundary policy;
- track separation policy.

### `OFFICIAL_COMPATIBILITY.md`

Must include:

- official DataLoader assumptions;
- leakage safety rules;
- same-day news cutoff;
- trade execution rules;
- buy/sell conversion;
- dependency restrictions;
- B-list central execution assumptions;
- no-API fallback policy.

### `FOUR_STAGE_SYSTEM.md`

Must include:

- Stage 1 candidates;
- Stage 2 candidates;
- Stage 3 candidates;
- Stage 4 candidates;
- input/output schema per stage;
- replacement policy;
- stage-specific ablations.

### `TRACK_DESIGN.md`

Must include:

- Track 1 macro design;
- Track 2 sector design;
- shared modules;
- track-specific configs;
- track-specific risks;
- when to fork logic by track and when not to.

### `ABLATION_PLAN.md`

Must include:

- baseline suite;
- no-news ablation;
- no-LLM ablation;
- no-text-storage ablation;
- no-turnover-control ablation;
- no-risk-control ablation;
- robust BL ablations;
- sector system ablations;
- OCO/fallback ablations;
- report tables to generate.

### `B_LIST_HARDENING.md`

Must include:

- hidden B-list risk register;
- reproducibility checklist;
- Docker/environment checklist;
- cache and prompt versioning;
- no future data policy;
- crash fallback;
- final submission checklist.

## Style Requirements

- Formal and implementation-oriented.
- Use tables where useful.
- Preserve many methods rather than narrowing too early.
- Be explicit about what is core, secondary, deferred, rejected, and ablation-only.
- Avoid unsupported official claims.
- Mark uncertainty clearly.
- Do not implement code.
- Do not delete or move files.
- Assume future coding prompts will read these docs before writing code.
```

---

## 7. Final Workflow Recommendation

Use this workflow as the project control system:

```text
Completed:
  research reports
  strategy synthesis
  four-stage modular reorganisation
  repo structure analysis
  official-agent vs src placement decision

Now:
  Prompt 01 — analyse all docs into main conversation context
  Prompt 02 — generate starter-kit Markdown documentation

Next:
  official starter reproduction
  repo skeleton
  leakage guard
  Stage 3 baselines
  official trade adapter
  Stage 1 news MVP
  Stage 2 text store MVP
  robust BL Track 1
  simplified Track 2 sector system
  OCO fallback
  ablation suite
  B-list hardening
```

The immediate next two prompts should be run in chat, not as coding implementation tasks:

```text
Prompt 01:
  Analyse all uploaded/project docs and produce main conversation context.

Prompt 02:
  Produce starter-kit Markdown files: README, methodology, architecture, implementation plan, repo policy,
  official compatibility, four-stage system, track design, ablation plan, and B-list hardening.
```

After these two chat prompts are complete, implementation prompts can begin.
