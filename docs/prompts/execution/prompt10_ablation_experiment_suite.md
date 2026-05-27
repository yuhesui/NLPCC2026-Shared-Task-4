# prompt10 — Ablation and Experiment Suite

## Role

You are an empirical research engineer.

## Objective

Build controlled experiments and ablations that can support both competition selection and system-report writing.

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

1. Implement experiment runner and ablation matrix under `src/tools/experiments/`.
2. Define experiments for S0, S1, robust BL, Track 2 sector system, and OCO fallback.
3. Include ablations: no-news, no-LLM, no-text-store, no-turnover-control, no-risk-control, robust BL without confidence, sector without graph/news, OCO without text.
4. Save configs, outputs, metrics, and tables under `outputs/experiments/` and `outputs/reports/`.
5. Generate report tables and basic figures.
6. Add tests for experiment config parsing and result storage.
7. Use `create_implementation_log` before finishing.

## Deliverables

- `src/tools/experiments/`
- `src/tools/reporting/`
- experiment configs
- outputs under `outputs/experiments/` and `outputs/reports/`
- tests
- implementation log

## Success Criteria

- Ablation suite can run on a small subset.
- Results are reproducible and stored with config hashes.
- Report tables compare against S0/S1.
