# prompt09 — OCO Fallback and Conservative Ensemble

## Role

You are a robust systems engineer building the production safety layer.

## Objective

Build the fallback manager, OCO/meta-allocator, and conservative ensemble to make B-list execution safer.

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

1. Implement `oco_ensemble_agent.py` and `conservative_ensemble_agent.py`.
2. Implement runtime fallback manager, decision trace, and dependency guard.
3. Define failure triggers: invalid text state, optimiser infeasibility, high turnover, missing dependency, failed LLM/API, invalid weights.
4. Ensure fallback to S1 or conservative risk-parity works deterministically.
5. Log every fallback reason.
6. Add configs for OCO fallback and conservative ensemble.
7. Test fallback paths explicitly.
8. Use `create_implementation_log` before finishing.

## Deliverables

- `src/nlpcc/stage4_agent/models/oco_ensemble_agent.py`
- `src/nlpcc/stage4_agent/models/conservative_ensemble_agent.py`
- `src/nlpcc/runtime/fallback_manager.py`
- `src/nlpcc/runtime/decision_trace.py`
- `src/nlpcc/runtime/dependency_guard.py`
- configs and tests
- implementation log

## Success Criteria

- Any major module failure results in valid fallback weights/trades.
- Fallback reasons are captured in decision traces.
- No external API is required for fallback execution.
