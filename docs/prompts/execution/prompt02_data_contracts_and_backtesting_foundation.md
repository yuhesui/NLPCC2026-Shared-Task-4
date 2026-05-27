# prompt02 — Data Contracts, Leakage Guard, and Backtesting Foundation

## Role

You are a core-systems engineer responsible for safe data contracts and evaluation foundations.

## Objective

Create canonical internal objects and safety checks shared by official-compatible agents and local tools.

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

1. Create data contracts under `src/nlpcc/core/data_contracts.py`.
2. Create leakage guard under `src/nlpcc/core/leakage_guard.py`.
3. Define canonical objects for raw news, price panels, daily decision input, portfolio state, target weights, official trades, and decision traces.
4. Encode visibility rules: past days may expose full OHLCV; current decision day may expose open only; same-day news must satisfy official cutoff.
5. Create metrics under `src/tools/backtesting/metrics.py`.
6. Create official-local comparison utilities under `src/tools/backtesting/compare_official_local.py`.
7. Add tests for leakage guard and metrics.
8. Update `docs/architecture/OFFICIAL_COMPATIBILITY.md` if implementation details refine the assumptions.
9. Use `create_implementation_log` before finishing.

## Deliverables

- `src/nlpcc/core/data_contracts.py`
- `src/nlpcc/core/leakage_guard.py`
- `src/tools/backtesting/metrics.py`
- `src/tools/backtesting/compare_official_local.py`
- tests under `tests/test_nlpcc/test_core/` and `tests/test_tools/test_backtesting/`
- implementation log

## Success Criteria

- Leakage tests fail if current-day close/high/low/return appear in decision features.
- Metrics compute Sharpe, cumulative return, drawdown, volatility, and turnover.
- Contracts can be imported by both `src/nlpcc/` and `src/tools/`.
