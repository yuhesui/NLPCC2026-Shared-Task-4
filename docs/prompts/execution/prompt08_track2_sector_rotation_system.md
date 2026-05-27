# prompt08 — Track 2 Sector-Rotation System

## Role

You are a sector-rotation and graph-aware allocation engineer.

## Objective

Build the Track 2 system using sector impact extraction, sector trend state, and optional KG-MoE-Lite as a report-friendly secondary module.

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

1. Strengthen sector impact extraction and entity/sector/ETF mapping.
2. Implement sector impact panel or lightweight graph store in Stage 2.
3. Implement sector trend and correlation graph features in Stage 3.
4. Implement `sector_rotation_agent.py`.
5. Implement `kg_moe_lite_agent.py` only if it can remain simple, deterministic, and ablatable.
6. Add Track 2 configs.
7. Run Track 2 local smoke/backtest against sector trend baseline.
8. Add ablations: no news, trend-only, no graph, equal-sector.
9. Use `create_implementation_log` before finishing.

## Deliverables

- Stage 1 sector mapping/extraction modules
- Stage 2 sector impact / graph modules
- Stage 3 sector trend / correlation modules
- Stage 4 sector rotation / KG-MoE-Lite agents
- Track 2 configs
- tests and outputs
- implementation log

## Success Criteria

- Track 2 system runs locally.
- Trend-only baseline is preserved.
- News/graph contributions are ablatable.
