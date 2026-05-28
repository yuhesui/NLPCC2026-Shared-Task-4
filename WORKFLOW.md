# WORKFLOW.md - Prompt-Controlled Execution Workflow

This project is controlled through execution prompts stored under:

```text
docs/prompts/execution/
```

The current prompt sequence is:

```text
prompt00 - repo reset, docs migration, skeleton, AGENTS.md, create_implementation_log
prompt01 - environment, data setup, official/local smoke pipeline
prompt02 - data contracts, leakage guard, backtesting foundation
prompt03 - Stage 3 trade processing and S0/S1 baselines
prompt04 - tools: backtester, optimiser, experiments, reporting, verification
prompt05 - Stage 1 news processing MVP
prompt06 - Stage 2 text store MVP
prompt07 - robust BL / risk parity engine
prompt08 - Track 2 sector rotation system
prompt09 - OCO fallback / conservative ensemble
prompt10 - ablation and experiment suite
prompt11 - verification and repair pass
prompt12 - full pipeline run and packaging
```

Each prompt must end by using `create_implementation_log`.

See `docs/workflow/PROMPT_EXECUTION_PLAN.md` for the full plan and `docs/REPO_STRUCTURE.md` for the exact target repository structure.
