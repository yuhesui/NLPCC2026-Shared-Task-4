# prompt06 — Stage 2 Quantified Text Store MVP

## Role

You are a data modelling engineer for text-to-quant state representation.

## Objective

Build the simplest useful quantified text storage layer: flat feature table, event table, BL view store, confidence matrix, and decayed event memory.

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

1. Implement Stage 2 schema, pipeline, registry, and validators.
2. Implement flat feature table, event table, BL view store, confidence matrix, and decayed event memory models.
3. Keep retrieval index, knowledge graph, and causal event graph as stubs or deferred modules unless trivial.
4. Add configs under `configs/stage2_text_store/`.
5. Ensure Stage 2 can consume Stage 1 outputs and emit deterministic state for Stage 4.
6. Add tests for missing data, duplicate events, confidence bounds, and deterministic decay.
7. Use `create_implementation_log` before finishing.

## Deliverables

- Stage 2 modules under `src/nlpcc/stage2_text_store/`
- configs under `configs/stage2_text_store/`
- tests under `tests/test_nlpcc/test_stage2_text_store/`
- implementation log

## Success Criteria

- Stage 2 accepts Stage 1 outputs.
- BL view store and confidence matrix are usable by robust BL.
- Decayed memory is deterministic and ablatable.
