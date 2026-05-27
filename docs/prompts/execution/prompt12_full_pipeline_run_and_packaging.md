# prompt12 — Full Pipeline Run and Packaging

## Role

You are a release and reproducibility engineer.

## Objective

Run the full available pipeline, generate report artifacts, and prepare a clean candidate submission package.

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

1. Run official server smoke test if available.
2. Run local smoke test.
3. Run S0/S1 baselines.
4. Run robust BL Track 1.
5. Run Track 2 sector system.
6. Run OCO fallback.
7. Run ablations if feasible.
8. Generate report artifacts.
9. Package a candidate submission under `outputs/submissions/`.
10. Exclude unnecessary cache/temp files.
11. Verify that no raw data is redistributed unless allowed by the task rules.
12. Write final run summary.
13. Use `create_implementation_log` before finishing.

## Deliverables

- outputs under `outputs/backtests/`, `outputs/experiments/`, `outputs/reports/`, `outputs/submissions/`
- final run summary under `docs/reports/` or `outputs/reports/`
- implementation log

## Success Criteria

- Full available pipeline runs or precise blockers are logged.
- Submission package is clean and reproducible.
- Final report artifacts exist.
