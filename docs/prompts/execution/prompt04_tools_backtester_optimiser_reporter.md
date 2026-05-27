# prompt04 — Tools Layer: Backtester, Optimiser, Experiment Runner, Reporter, Verification

## Role

You are a research infrastructure engineer.

## Objective

Build the local tools layer under `src/tools/` without polluting the production package under `src/nlpcc/`.

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

1. Strengthen `src/tools/backtesting/local_backtester.py`.
2. Add or refine `vectorized_backtester.py`, `cuda_backend.py`, `official_server_runner.py`, `replay.py`, and `compare_official_local.py`.
3. Build optimiser tools: search space, grid search, random search, walk-forward, scorer, promotion.
4. Build experiment tools: runner, ablations, experiment config, result store.
5. Build reporting tools: artifacts, tables, figures, report builder.
6. Build verification tools: leakage audit, dependency audit, reproducibility audit, submission audit.
7. Keep `src/tools/` allowed to import `src/nlpcc/`, but do not make `src/nlpcc/` depend on tools by default.
8. Add tests under `tests/test_tools/`.
9. Use `create_implementation_log` before finishing.

## Deliverables

- `src/tools/backtesting/`
- `src/tools/optimiser/`
- `src/tools/experiments/`
- `src/tools/reporting/`
- `src/tools/verification/`
- tests under `tests/test_tools/`
- implementation log

## Success Criteria

- Tools can run S0/S1 experiments on small subsets.
- Metrics and result storage are deterministic.
- Production package remains clean and importable without heavy tool dependencies.
