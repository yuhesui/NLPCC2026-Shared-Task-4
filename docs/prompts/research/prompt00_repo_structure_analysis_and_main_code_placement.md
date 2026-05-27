# Prompt 00 — Repository Structure Analysis and Main Code Placement

## Role

You are a senior software architect and quantitative research engineering lead.

## Objective

Analyse the current repository structure and generate a clear Markdown document that explains:

1. what the current repo contains;
2. what each major directory/file is responsible for;
3. where the main strategy code should be placed;
4. where supporting modules should be placed;
5. what files should be created or reorganised next;
6. how the current documentation under the root-level `docs/` directory should be preserved and extended.

The output should be a single Markdown file:

```text
docs/repo_structure_analysis.md
```

---

## Context

This repository is for **NLPCC 2026 Shared Task 4: LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market**.

The project should follow a four-stage modular architecture:

1. **News Processing**  
   Raw Top-20 financial news → structured event/view/sector/regime signals.

2. **Quantified Text Storage Medium**  
   Structured text signals → event table, view matrix, belief state, retrieval index, or knowledge graph.

3. **Trade Data Processing**  
   Official price/portfolio data → returns, volatility, covariance, momentum, drawdown, turnover capacity, and risk state.

4. **Final Trading Agent**  
   Text state + trade state → target weights / official executable trades.

The repository should remain compatible with official backtesting and hidden B-list central execution. Avoid future leakage, avoid current-day close/high/low/return before decision time, and keep all main logic reproducible.

Important repository assumption:

- All current project documentation is stored under the root-level `docs/` directory.
- Do **not** move or overwrite existing documentation unless clearly justified.
- New documentation should also be placed under `docs/`.
- If there are existing architecture, research, report, prompt, or planning documents under `docs/`, identify them and propose a clean subfolder organisation while preserving their content.

---

## Task

Please inspect the full repository and produce:

```text
docs/repo_structure_analysis.md
```

The Markdown document must include exactly these sections:

---

## A. Current Repository Overview

Summarise the current directory structure.

Include a tree view such as:

```text
repo/
  docs/
  src/
  configs/
  data/
  tests/
```

Only include files/directories that actually exist.

Explicitly inspect the root-level `docs/` directory and summarise what types of documentation are currently stored there, such as:

- architecture notes;
- strategy reports;
- prompts;
- research summaries;
- implementation plans;
- generated reports;
- miscellaneous notes.

Do not assume the exact contents of `docs/`; inspect and report them.

---

## B. Existing File and Directory Responsibilities

Create a table:

| Path | Current Role | Importance | Keep / Move / Refactor / Delete | Notes |
|---|---|---:|---|---|

Be specific. Do not describe everything generically.

For files under `docs/`, classify them into meaningful documentation groups. Examples:

| Documentation Group | Existing Path(s) | Current Role | Recommended Location | Notes |
|---|---|---|---|---|

Use this only if the current `docs/` directory contains enough files to justify grouping.

---

## C. Recommended Target Repository Structure

Propose a clean target structure such as:

```text
src/nlpcc4/
  news_processing/
  text_store/
  trade_processing/
  agents/
  portfolio/
  execution/
  reports/
  utils/

configs/
  news_processing/
  text_store/
  trade_processing/
  agents/
  systems/

tests/
  test_news_processing/
  test_text_store/
  test_trade_processing/
  test_agents/
  test_execution/

docs/
  repo_structure_analysis.md
  architecture/
  strategy/
  research/
  prompts/
  reports/
  implementation_logs/
```

Modify this target structure if the current repository already has a better convention.

The target structure must respect this documentation policy:

- root-level `docs/` remains the home for all project documentation;
- architecture documents go under `docs/architecture/`;
- strategy decision documents go under `docs/strategy/`;
- research syntheses go under `docs/research/`;
- prompts go under `docs/prompts/`;
- generated system/report drafts go under `docs/reports/`;
- implementation logs go under `docs/implementation_logs/`;
- `docs/repo_structure_analysis.md` should remain the high-level repo map.

Do not place main executable strategy logic under `docs/`.

---

## D. Where the Main Code Should Be Placed

Explain exactly where each category of code should go.

Use this table:

| Code Type | Recommended Location | Reason | Example Files |
|---|---|---|---|
| News event extraction | | | |
| BL view extraction | | | |
| Event memory / text storage | | | |
| Price feature processing | | | |
| Covariance / volatility estimation | | | |
| Baseline S0/S1 allocators | | | |
| Robust Black-Litterman agent | | | |
| Risk parity agent | | | |
| OCO / ensemble fallback | | | |
| Target-weight to trade conversion | | | |
| Backtest runner | | | |
| Report artifact generation | | | |

Rules:

- Main reusable Python code should live under `src/`, preferably `src/nlpcc4/`.
- Configuration should live under `configs/`.
- Tests should live under `tests/`.
- Generated outputs should live under `outputs/`.
- Documentation should live under root-level `docs/`.
- Notebooks, if any, should remain exploratory and must not contain official submission logic.

---

## E. Four-Stage Architecture Mapping

Map the four-stage architecture to the repository.

Use this table:

| Stage | Source Directory | Config Directory | Input | Output | Tests | Report Artifacts |
|---|---|---|---|---|---|---|
| Stage 1 — News Processing | | | | | | |
| Stage 2 — Text Storage | | | | | | |
| Stage 3 — Trade Data Processing | | | | | | |
| Stage 4 — Final Trading Agent | | | | | | |

Be explicit about where documentation for each stage should be placed under `docs/`.

---

## F. Main Entry Points

Identify or propose the main entry points.

Include:

1. official-compatible agent entry point;
2. local backtest entry point;
3. experiment runner;
4. report generation script;
5. configuration loading path;
6. prompt/documentation generation path, if prompts are stored in `docs/prompts/`.

Use a table:

| Entry Point | Path | Purpose | Required Inputs | Expected Outputs |
|---|---|---|---|---|

---

## G. Files to Create Next

Give a prioritised list of files to create.

Use this table:

| Priority | File | Purpose | Depends On | Minimal Contents |
|---:|---|---|---|---|

Focus on a minimum viable implementation first.

The list must include at least:

- a main package initializer;
- a leakage-safe data contract module;
- Stage 3 price feature processor;
- S0/S1 baseline allocator;
- target-weight-to-official-trade adapter;
- local backtest runner;
- Stage 1 news extraction schema;
- `docs/repo_structure_analysis.md`;
- at least one prompt file under `docs/prompts/`.

---

## H. Refactor / Cleanup Recommendations

Identify:

- duplicate logic;
- unclear file placement;
- files that mix research, execution, and reporting;
- files that may cause leakage risk;
- files that should not be imported by official submission code;
- large artifacts or generated outputs that should be moved out of source code;
- documentation files under `docs/` that should be grouped into clearer subdirectories.

Do not delete or move files automatically. Only recommend actions.

---

## I. Implementation Policy

State concrete repository rules.

Include at least:

- source code lives under `src/`;
- configuration lives under `configs/`;
- all documentation remains under root-level `docs/`;
- prompts are stored under `docs/prompts/`;
- generated backtest outputs live under `outputs/`;
- raw official data is never modified;
- no current-day close/high/low/return is used before decision time;
- final agents must be deterministic given the same inputs/config/seed;
- LLM extraction must be cached or reproducible;
- official submission code must not depend on notebooks;
- notebooks are exploratory only;
- `docs/` must not contain executable production logic;
- official submission code should have a small, auditable dependency surface.

---

## J. Final Recommendation

End with a decisive recommendation:

```text
## Final Repo Placement Recommendation

- Main package:
- Main official agent file:
- Main local backtest runner:
- Main Stage 1 directory:
- Main Stage 2 directory:
- Main Stage 3 directory:
- Main Stage 4 directory:
- Main execution/trade adapter:
- Main configs:
- Main documentation directory:
- Main prompt directory:
- First files to implement:
- Files/directories to avoid placing main logic in:
```

---

## Constraints

- Do not rewrite the whole repository.
- Do not create implementation code yet unless absolutely necessary.
- Do not delete files.
- Do not make unsupported assumptions; mark uncertain items clearly.
- Prefer a structure that is simple enough for one student to maintain.
- Prioritise reproducibility, official backtest compatibility, leakage safety, and clear separation between documentation and executable code.
- The final answer should be the full content of `docs/repo_structure_analysis.md`.
