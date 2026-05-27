# prompt01 — Environment, Data Setup, and Smoke Pipeline

## Role

You are a quantitative research engineer implementing the first executable smoke pipeline.

## Objective

Set up environment/data foundations and verify that both official-server and local-backtester paths can run a tiny deterministic strategy.

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

1. Inspect `NLPCC_tasks/dataset/` and official README files.
2. Create data manifests for available price/news files.
3. Copy or symlink 2024 training data into `data/train_2024/`.
4. Copy or symlink 2025 public A-list data into `data/public_a_2025/`.
5. Never modify raw official data in place.
6. Create a minimal smoke-test subset under `data/sample/smoke_test/`.
7. Create or update data catalog utilities under `src/tools/data_tools/`.
8. Create minimal data adapter stubs under `src/nlpcc/core/` or `src/nlpcc/stage3_trade/` only as needed.
9. Implement the simplest smoke strategy under `src/nlpcc/stage4_agent/models/smoke_one_unit_agent.py`.
10. Smoke strategy behaviour: choose the first asset in the selected track; buy a tiny fixed amount / safe notional unit equivalent; read news and price input; do not use current-day close/high/low/return in decision logic.
11. Create minimal local backtester under `src/tools/backtesting/local_backtester.py`.
12. Create placeholder vectorised/CUDA backend interfaces under `src/tools/backtesting/` without over-engineering.
13. Create official server smoke runner under `scripts/run_official_server_smoke.py`.
14. Create local smoke runner under `scripts/run_local_smoke.py`.
15. Run both smoke paths if the environment allows; otherwise log exact blockers.
16. Save outputs under `outputs/smoke_tests/`.
17. Write tests under `tests/test_integration/`.
18. Use `create_implementation_log` before finishing.

## Deliverables

- data manifests under `data/train_2024/manifests/` and `data/public_a_2025/manifests/`
- `src/tools/data_tools/` utilities
- `src/nlpcc/stage4_agent/models/smoke_one_unit_agent.py`
- `src/tools/backtesting/local_backtester.py`
- `src/tools/backtesting/vectorized_backtester.py`
- `src/tools/backtesting/cuda_backend.py`
- `scripts/run_official_server_smoke.py`
- `scripts/run_local_smoke.py`
- smoke outputs under `outputs/smoke_tests/`
- tests under `tests/test_integration/`
- implementation log

## Success Criteria

- Data manifests exist and record source paths/hashes/date ranges where possible.
- Local smoke backtester runs or logs a precise blocker.
- Official smoke runner exists and either runs or logs a precise blocker.
- Smoke strategy does not use forbidden current-day fields in decision logic.
