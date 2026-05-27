# prompt05 — Stage 1 News Processing MVP

## Role

You are an LLM-systems and financial NLP engineer.

## Objective

Build schema-validated news processing with rule-based/no-LLM fallback before any API-heavy extraction.

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

1. Implement Stage 1 schema, pipeline, registry, validators, and cache.
2. Implement models: rule-based extractor, sentiment classifier, event tuple extractor, BL view extractor, sector impact extractor, entity/sector mapper, no-LLM fallback.
3. Keep LLM extractor as controlled/optional and do not require external API for tests.
4. Add prompt templates under `src/nlpcc/stage1_news/prompts/` if needed.
5. Add configs under `configs/stage1_news/`.
6. Ensure extraction output is valid even when news is missing or model fails.
7. Add tests with fixed toy news examples.
8. Use `create_implementation_log` before finishing.

## Deliverables

- Stage 1 modules under `src/nlpcc/stage1_news/`
- models under `src/nlpcc/stage1_news/models/`
- configs under `configs/stage1_news/`
- tests under `tests/test_nlpcc/test_stage1_news/`
- implementation log

## Success Criteria

- Rule-based and no-LLM extraction run deterministically.
- BL view extraction and sector impact extraction produce schema-valid outputs.
- Missing/invalid news falls back safely.
