# prompt11 — Verification and Fix Pass

## Role

You are an independent verification and repair agent.

## Objective

Audit the repository after implementation phases, fix critical issues, and ensure docs match the actual code structure.

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

1. Run import audit.
2. Run leakage audit.
3. Run official/local consistency checks if possible.
4. Run raw-data immutability audit.
5. Run dependency and reproducibility audit.
6. Run tests.
7. Check docs for stale references, especially `src/nlpcc4/` or flat `src/` references.
8. Confirm docs consistently state: `src/nlpcc/` for competition implementation and `src/tools/` for tools.
9. Fix critical and major issues.
10. Record unresolved caveats.
11. Use `create_implementation_log` before finishing.

## Deliverables

- verification outputs under `outputs/logs/` or `outputs/reports/`
- fixed code/docs where necessary
- updated tests if needed
- implementation log

## Success Criteria

- No known critical leakage issue remains.
- Tests and smoke checks either pass or blockers are precisely documented.
- Documentation matches actual repository layout.
