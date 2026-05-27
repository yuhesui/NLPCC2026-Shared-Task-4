# prompt07 — Robust Black-Litterman and Risk-Parity Engine

## Role

You are a quantitative portfolio construction engineer.

## Objective

Build the first serious Track 1 system: robust BL with risk-parity/S1 fallback and turnover control.

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

1. Implement portfolio modules: constraints, target weights, risk parity, Black-Litterman, robust optimiser, turnover control, position sizing.
2. Implement `robust_bl_agent.py` and `risk_parity_agent.py` under Stage 4 models.
3. Integrate Stage 1 BL view extraction, Stage 2 BL view store/confidence matrix, Stage 3 covariance/risk state, and Stage 4 robust allocation.
4. Add configs for robust BL and risk parity.
5. Enforce long-only, concentration limits, turnover constraints, and fallback to S1 on infeasibility.
6. Run small local backtests and ablations against S1.
7. Add tests for weight validity, constraints, and fallback behaviour.
8. Use `create_implementation_log` before finishing.

## Deliverables

- `src/nlpcc/portfolio/`
- `src/nlpcc/stage4_agent/models/robust_bl_agent.py`
- `src/nlpcc/stage4_agent/models/risk_parity_agent.py`
- configs under `configs/stage4_agent/` and `configs/systems/`
- tests under `tests/test_nlpcc/test_portfolio/` and `tests/test_nlpcc/test_stage4_agent/`
- outputs under `outputs/backtests/`
- implementation log

## Success Criteria

- Robust BL system runs locally.
- Invalid views or optimiser failures fall back to S1.
- Turnover and concentration constraints are enforced.
