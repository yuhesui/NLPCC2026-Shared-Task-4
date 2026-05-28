# prompt00 鈥?Repository Reset, Documentation Migration, Skeleton Creation, and Implementation Log Helper

## Role

You are a senior Python repository architect and quantitative research engineering lead.

## Objective

Prepare the repository for implementation without implementing strategy logic. Create the documentation layout, package skeleton, prompt archive, and `create_implementation_log` helper adapted from the draft currently stored at the repository root if present.

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

1. Inspect the current repository tree.
2. Preserve `NLPCC_tasks/` as official starter/reference code.
3. Reorganise existing documentation into the desired `docs/` structure shown in 
   `docs/REPO_STRUCTURE.md`. *If unedited
4. If a document category is unclear, move or keep it under `docs/archived/` and record it in `docs/archived/README.md`.
5. Create `docs/prompts/execution/` and place/copy the execution prompts there if not already present.
6. Create `AGENTS.md`, root `README.md`, root `METHODOLOGY.md`, root `WORKFLOW.md` if missing or stale.
7. Create `src/nlpcc/` skeleton with stage folders and `models/` subfolders.
8. Create `src/tools/` skeleton for data tools, backtesting, optimiser, experiments, reporting, verification, and utilities.
9. Create `configs/`, `tests/`, `data/`, `outputs/`, and `scripts/` skeletons.
10. Locate the draft implementation-log helper in the repository root if present.
11. Modify it to suit the current repo:
    - reusable helper at `src/tools/utils/implementation_log.py`;
    - CLI wrapper at `scripts/create_implementation_log.py`;
    - default output directory `docs/implementation_logs/`;
    - support fields: `prompt_id`, `phase`, `summary`, `files`, `tests`, `caveats`, `next_steps`, and optional artifact paths.
12. Ensure the CLI command name used in later prompts is `python scripts/create_implementation_log.py`.
13. Update docs that still reference `src/nlpcc4/` or flat `src/` to the new `src/nlpcc/` + `src/tools/` policy.
14. Do not implement trading algorithms, extractors, backtesters, or optimisers yet.
15. Run a basic import/syntax check for the implementation-log helper if possible.

## Deliverables

- `AGENTS.md`
- `README.md`
- `METHODOLOGY.md`
- `WORKFLOW.md`
- `docs/REPO_STRUCTURE.md`
- `docs/workflow/PROMPT_EXECUTION_PLAN.md`
- `docs/prompts/execution/`
- `src/nlpcc/` skeleton
- `src/tools/` skeleton
- `configs/`, `tests/`, `data/`, `outputs/`, `scripts/` skeletons
- `src/tools/utils/implementation_log.py`
- `scripts/create_implementation_log.py`
- implementation log under `docs/implementation_logs/`

## Success Criteria

- The repo structure matches `docs/REPO_STRUCTURE.md` at the skeleton level.
- `create_implementation_log` works or a clear blocker is logged.
- No implementation algorithms are added.
- Existing docs are preserved, moved, or archived with a manifest.
