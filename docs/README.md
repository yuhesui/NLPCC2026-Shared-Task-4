# docs/ — Documentation Index

This folder is the documentation control centre for the NLPCC 2026 Shared Task 4 implementation workspace.

## Key Files

- `REPO_STRUCTURE.md` — exact target repository structure.
- `workflow/PROMPT_EXECUTION_PLAN.md` — prompt-by-prompt execution plan.
- `prompts/execution/` — prompts to execute the build sequence.
- `context/` — main project context and decisions.
- `architecture/` — architecture, repo policy, official compatibility, track design.
- `strategy/` — methodology, ablation, B-list hardening, and implementation plan.
- `research/` — prior deep research reports.
- `implementation_logs/` — logs created by `create_implementation_log`.

## Documentation Rule

Do not place executable production logic under `docs/`. Prompts and documentation are allowed; Python modules and scripts should live under `src/` or `scripts/`.
