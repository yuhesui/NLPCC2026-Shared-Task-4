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
- the current discussion about putting the official-facing agent in `NLPCC_tasks/agent_platform/agents/` and reusable implementation in `src/nlpcc/`.

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
Stage 1 鈥?News Processing
Stage 2 鈥?Quantified Text Data Storage Medium
Stage 3 鈥?Trade Data Processing
Stage 4 鈥?Final Trading Agent
```

Current placement policy:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable implementation:
  src/nlpcc/

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
  Prompt 01 鈥?analyse all docs into main conversation context
  Prompt 02 鈥?generate starter-kit Markdown documentation

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