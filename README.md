# NLPCC 2026 Shared Task 4 Implementation Workspace

This repository is for building a reproducible, leakage-safe, and report-worthy system for **NLPCC 2026 Shared Task 4: LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market**.

This project is not investment advice. It is an academic shared-task implementation workspace.

## Current Execution Philosophy

The repository should be developed through a prompt execution sequence:

1. establish repository structure and documentation;
2. set up data/environment smoke tests;
3. build contracts, leakage guards, and backtesting foundations;
4. build Stage 3 price/trade baselines;
5. build research tools;
6. build Stage 1 and Stage 2 text modules;
7. build robust allocation engines;
8. build Track 2 sector systems;
9. add fallback/ensemble control;
10. run ablations, verification, and packaging.

## Repository Placement Policy

```text
Official-facing submitted wrapper:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable competition implementation:
  src/nlpcc/

Local research/development tools:
  src/tools/

Configuration:
  configs/

Tests:
  tests/

Documentation:
  docs/

Execution prompts:
  docs/prompts/execution/

Generated outputs:
  outputs/
```

## Four-Stage System

```text
Stage 1 - News Processing
Stage 2 - Quantified Text Data Storage Medium
Stage 3 - Trade Data Processing
Stage 4 - Final Trading Agent
```

Each stage has a `pipeline.py` for orchestration and a `models/` subfolder for alternative methods. This keeps the broad method universe available for comparison while preserving a clean production pathway.

## First Build Target

The first executable build should be a smoke pipeline:

```text
official data / copied sample data
-> read first track asset
-> buy a tiny fixed amount / one safe notional unit equivalent
-> run through official server if available
-> run through minimal local backtester
-> write logs and smoke-test outputs
```

The first serious strategy target remains:

```text
Stage 1: BL view extraction or rule-based fallback
Stage 2: BL view store + confidence matrix
Stage 3: covariance + inverse-volatility + momentum/risk state
Stage 4: robust Black-Litterman + risk parity + S1 fallback
```

## Prompt14 Runtime Status

- Official-facing wrapper path: `NLPCC_tasks/agent_platform/agents/build_agent.py`.
- Track A / Macro default: `robust_bl_track1`; fallback: `s1_macro`.
- Track B / Sector default: `s1_sector`; `sector_rotation_track2` remains experimental until it beats S1 sector on construction-period evidence.
- Stage 1 default is deterministic rule-based extraction with no external API requirement. LLM and local Hugging Face model paths are optional and disabled by default.
- Official/local parity must be read from the latest `outputs/reports/prompt14/official_local_parity_rerun_report.md`; older local backtests are local evidence, not official leaderboard facts.

## Documentation Map

- `docs/REPO_STRUCTURE.md` - exact desired repository structure.
- `docs/workflow/PROMPT_EXECUTION_PLAN.md` - full prompt execution sequence.
- `docs/prompts/execution/` - executable prompts for coding agents.
- `docs/architecture/` - architecture, official compatibility, repo policy, track design.
- `docs/strategy/` - methodology, ablation, B-list hardening, implementation plan.
- `docs/context/` - main conversation context and current decisions.
- `docs/research/` - prior deep research reports.
- `docs/implementation_logs/` - logs created by `create_implementation_log`.

## Exact Target Structure

See `docs/REPO_STRUCTURE.md`.
