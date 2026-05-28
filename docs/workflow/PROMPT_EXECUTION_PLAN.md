# PROMPT_EXECUTION_PLAN.md - NLPCC Task 4 Build Sequence

## 1. Purpose

This document defines the numbered prompt execution sequence for turning the current research/documentation project into an implementation-ready repository.

## 2. Architectural Decisions

```text
Official-facing wrapper:
  NLPCC_tasks/agent_platform/agents/build_agent.py

Reusable competition package:
  src/nlpcc/

Research/development tools:
  src/tools/

Execution prompts:
  docs/prompts/execution/
```

Each stage keeps orchestration separate from candidate models:

```text
stageX_*/pipeline.py
stageX_*/models/
```

## 3. Prompt Sequence

| Prompt | Focus | Main Deliverable |
|---:|---|---|
| `prompt00` | Repo reset, docs migration, skeleton, `create_implementation_log` | Clean repo foundation |
| `prompt01` | Environment, data setup, official/local smoke pipeline | First executable smoke run |
| `prompt02` | Data contracts, leakage guard, metrics, backtesting foundation | Safe shared contracts |
| `prompt03` | Stage 3 trade processing + S0/S1 baselines | Quant baseline floor |
| `prompt04` | Tools: backtester, optimiser, experiments, reporting, verification | Research infrastructure |
| `prompt05` | Stage 1 news processing MVP | Rule-based + structured extraction |
| `prompt06` | Stage 2 text store MVP | Flat features + BL view store |
| `prompt07` | Robust BL / risk parity engine | First serious Track 1 system |
| `prompt08` | Track 2 sector system | Sector rotation prototype |
| `prompt09` | OCO fallback / conservative ensemble | Production safety layer |
| `prompt10` | Ablation and experiment suite | Evidence package |
| `prompt11` | Verification and repair | Leakage/import/docs/test fixes |
| `prompt12` | Full pipeline run and packaging | Final run artifacts and submission draft |

## 4. Universal Completion Rule

Every prompt execution must end by using `create_implementation_log`.

The helper is created or repaired in `prompt00`. Expected command:

```bash
python scripts/create_implementation_log.py --prompt-id "promptXX" --phase "phase_name" --summary "Summary" --files "changed_file_1,changed_file_2" --tests "pytest ... / smoke run ..." --caveats "Known caveats" --next-steps "Next action"
```
