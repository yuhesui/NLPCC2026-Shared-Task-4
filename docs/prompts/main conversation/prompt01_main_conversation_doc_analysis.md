# Prompt 01 鈥?Main Conversation Document Analysis

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
鈫?Quantified Text Data Storage Medium
鈫?Trade Data Processing
鈫?Final Trading Agent
```

The current intended repo policy is:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable implementation:
  src/nlpcc/

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