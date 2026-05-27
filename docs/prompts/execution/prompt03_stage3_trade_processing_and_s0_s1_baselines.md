# prompt03 — Stage 3 Trade Processing and S0/S1 Baselines

## Role

You are a quantitative strategy engineer building the no-news baseline floor.

## Objective

Build Stage 3 price/risk state and S0/S1 baseline agents before adding fancy news or LLM components.

## Common Execution Rules

Before changing anything, read:

- `AGENTS.md`
- `README.md`
- `docs/REPO_STRUCTURE.md`
- `docs/workflow/PROMPT_EXECUTION_PLAN.md`
- `docs/context/main_conversation_context.md` if present
- `docs/context/current_decisions.md` if present
- `docs/context/open_questions.md` if present
- `docs/architecture/OFFICIAL_COMPATIBILITY.md` if present
- `docs/architecture/FOUR_STAGE_SYSTEM.md` if present
- `docs/strategy/METHODOLOGY.md` if present
- official README files under `NLPCC_tasks/`

Hard rules:

- Keep `NLPCC_tasks/` as official starter/reference code unless the prompt explicitly requests a thin wrapper.
- Reusable competition logic belongs under `src/nlpcc/`.
- Local research/development tools belong under `src/tools/`.
- Do not put executable production logic under `docs/`.
- Do not modify raw official data in place.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must respect the official timestamp cutoff.
- Every non-trivial module needs tests or an explicit reason why tests were not run.
- Write a log using `create_implementation_log` before finishing.

Implementation log requirement:

At the end of the task, run the implementation-log helper created or maintained by `prompt00`, normally via:

```bash
python scripts/create_implementation_log.py   --prompt-id "<prompt-id>"   --phase "<phase-name>"   --summary "<short summary>"   --files "<comma-separated changed files>"   --tests "<tests or checks run>"   --caveats "<known caveats>"   --next-steps "<recommended next steps>"
```

If the helper is unavailable because the repository is still being bootstrapped, manually create a Markdown or JSON log under `docs/implementation_logs/`, then fix the helper as part of the task.

## Tasks

1. Implement `src/nlpcc/stage3_trade/schema.py`, `pipeline.py`, `validators.py`, and registry.
2. Implement Stage 3 models: equal weight state, inverse volatility, momentum, sector trend, covariance, shrinkage covariance, drawdown, breadth, turnover, cash feasibility.
3. Implement `src/nlpcc/stage4_agent/models/s0_equal_weight_agent.py`.
4. Implement `src/nlpcc/stage4_agent/models/s1_quant_core.py` for Track 1 and Track 2 configs.
5. Add configs for S0 and S1 under `configs/systems/` and `configs/stage3_trade/`.
6. Run local smoke backtests on a small subset.
7. Save baseline outputs under `outputs/backtests/`.
8. Add tests for features, baselines, and no-leakage behaviour.
9. Use `create_implementation_log` before finishing.

## Deliverables

- Stage 3 modules under `src/nlpcc/stage3_trade/`
- S0/S1 agents under `src/nlpcc/stage4_agent/models/`
- configs under `configs/stage3_trade/` and `configs/systems/`
- baseline outputs under `outputs/backtests/`
- tests under `tests/test_nlpcc/test_stage3_trade/` and `tests/test_nlpcc/test_stage4_agent/`
- implementation log

## Success Criteria

- S0 and S1 agents run in the local backtester.
- Track 1 and Track 2 configs both instantiate.
- No forbidden current-day fields are used.
- S1 becomes the fallback benchmark for later prompts.
