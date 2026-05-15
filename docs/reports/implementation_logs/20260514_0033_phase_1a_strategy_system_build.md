# Phase 1a Strategy System Build

## Summary

Implemented a runnable Phase 1a target-weight-first strategy system under `src/nlpcc4/`, with S0-S4 MVP strategies, config loading, official-compatible data access, leakage checks, execution/trade conversion, metrics, CLI scripts, tests, and Phase 1a documentation.

Initial inspection results:

```text
Get-Location -> D:\Projects\NLPCC2026-Shared-Task-4
git status --short --untracked-files=all -> pre-existing .idea change, phase_a/phase_0 docs rename/delete
git status --short -- NLPCC_tasks -> clean
```

`rg --files` failed with `Access is denied`, so PowerShell listing and direct file reads were used.

## Read-First Evidence Table

| File | Exists? | Key facts extracted | Phase 1a implication | Action taken |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Yes | Official starter kit is vendor code; custom code under `src/nlpcc4/`; strategies output target weights first; trade conversion belongs in execution layer. | Preserve `NLPCC_tasks/`; keep strategy/execution separation. | No edit. |
| `README.md` | Yes | Task uses daily news and historical prices; Track 1/2 ETF pools; 0.01% friction; Sharpe focus. | Implement daily target-weight and metric artifacts. | No edit. |
| `NLPCC_tasks/README.md` | Yes | Official no-leakage rules: previous full price history plus current open; current close/high/low hidden; same-day news before 15:00; close execution. | Mirror official-compatible interfaces and document timing. | No edit. |
| `docs/design/repo_architecture.md` | Yes | `.var/` is runtime sink; custom code under `src/nlpcc4/`; S1 first; LLMs bounded. | Follow existing architecture. | No edit. |
| `docs/research/phase0-init.md` | Yes | Canonical strategy policy: S1 first, S2/S3 bounded JSON, S4 mostly Track 2, no direct LLM trades. | Implement S2-S4 as structured overlays only. | No edit. |
| `docs/research/strategy_decision_summary.md` | Yes | S0 baselines required before LLM claims; S1 is backup/core; S3 primary if validated. | Added baseline battery and S1/S2/S3/S4 MVPs. | No edit. |
| latest implementation log | Yes | Phase 0 cleanup left official starter kit clean and listed Phase 1 fixes. | Address target-weight converter, S0/S1, leakage, metrics, manual LLM. | No edit. |
| `docs/command_reference.md` | Yes | Commands were marked planned. | Replace with runnable Phase 1a commands. | Modified. |
| `.gitignore` | Yes | `.var/` and runtime folders ignored; dataset ignored. | Keep runtime artifacts under `.var/`. | No edit. |
| `pyproject.toml` | Yes | Python >=3.13, no project dependencies. | Use stdlib where possible; PyYAML/pandas/numpy available in environment. | No edit. |
| `NLPCC_tasks/config.py` | Yes | Server base URL localhost:6207; data dirs under `dataset`; default capital 100000. | Use same capital/friction defaults. | No edit. |
| `NLPCC_tasks/start_server.py` | Yes | Starts FastAPI server; data loader init happens via app/server path. | Official server smoke remains environment-sensitive. | No edit. |
| `NLPCC_tasks/server_platform/app/core/data_loader.py` | Yes | Current historical price hides same-day close/high/low/change/pct_change; same-day news before 15:00 is included despite stale comment. | Default custom news policy is conservative `previous_day_only`; support `official_available`. | No edit. |
| `NLPCC_tasks/server_platform/app/core/backtest.py` | Yes | Holdings are monetary values; submit updates holdings by same-day pct_change, then buys first and sells second; commission 0.0001. | Trade converter limits buys to current cash and documents sell-proceeds ambiguity. | No edit. |
| `NLPCC_tasks/server_platform/app/api/backtest.py` | Yes | API exposes start/trade/status/next_day/day_data/historical_prices/news/results; Sharpe helper and aligned history exist. | Custom scripts write local artifacts and include official client health helper. | No edit. |
| `NLPCC_tasks/agent_platform/client/platform_client.py` | Yes | Official client submits trades and decisions; uses bearer auth and official payloads. | Custom converter emits official-compatible payload shape only in execution layer. | No edit. |
| `NLPCC_tasks/agent_platform/demo_backtest.py` | Yes | Demo defines Track 1/2 universes and uses LLM agent to produce trades. | Reused public universe lists in custom modules. | No edit. |
| `NLPCC_tasks/dataset/README.md` | Yes | Dataset docs confirm price fields and same-day news before 15:00. | Document code/comment ambiguity and default conservatively. | No edit. |
| `NLPCC_tasks/dataset/dataloader_eval.py` | Yes | Offline DataLoader mirrors official price visibility and news filtering. | Official-compatible wrapper follows same method names. | No edit. |

## Official Mechanics Inspected

See `docs/reports/phase_1a/official_mechanics_notes.md`.

Key findings:

- Current-day close/high/low/change/pct_change are hidden in `get_historical_prices`.
- Current-day open is visible.
- Same-day news before 15:00 is available in current official code, but custom default is `previous_day_only`.
- Holdings are monetary values.
- Buys execute before sells.
- Commission is 0.0001.
- Official trades use buy `amount` and sell `percentage`.

## Files Created

- `src/nlpcc4/common/config.py`
- `src/nlpcc4/data/features.py`
- `src/nlpcc4/data/news_features.py`
- `src/nlpcc4/llm/manual_io.py`
- `src/nlpcc4/llm/client.py`
- `src/nlpcc4/strategies/shared/persistence.py`
- `src/nlpcc4/strategies/shared/random_constrained.py`
- `src/nlpcc4/strategies/shared/sector_trend.py`
- `src/nlpcc4/strategies/track1_macro/rule_based_macro.py`
- `scripts/export_llm_prompts.py`
- `docs/reports/phase_1a/*`
- Phase 1a test files listed below.

## Files Modified

- Core common/data/execution/metrics/backtest/experiments/reports modules under `src/nlpcc4/`.
- S0/S1/S2/S3/S4 strategy modules under `src/nlpcc4/strategies/`.
- LLM schema/parser/validator/prompt modules.
- CLI scripts under `scripts/`.
- Required configs under `configs/`.
- `docs/command_reference.md`.
- Existing tests were updated where placeholders became real implementations.

## Files Intentionally Not Touched

- `NLPCC_tasks/` was not modified.
- Raw LLM outputs, caches, generated runs, and submission archives were not committed.
- Public dataset files were not created under `NLPCC_tasks/dataset/`.

## Strategy Implementations

- S0: equal weight, inverse volatility, momentum, sector trend, persistence, rule-based macro, news sentiment, deterministic random constrained.
- S1: Track 1 inverse-vol/momentum/breadth/defensive/drawdown/turnover system; Track 2 sector trend top-k/cap/turnover system.
- S2: bounded regime JSON classifier with off/manual/api modes, schema validation, deterministic mapping, confidence-gated blend, S1 fallback.
- S3: bounded alpha-score JSON with confidence shrinkage, risk-budget weighting, max deviation from S1, S1 fallback.
- S4: Track 2 event-to-sector exposure mapper with confidence/trend checks; Track 1 documented S1 fallback.

## Manual LLM Workflow

- Requests: `.var/manual_llm/requests/<run_id>/YYYYMMDD_<track>_<strategy>_<decision_id>.md`
- Responses: `.var/manual_llm/responses/<run_id>/YYYYMMDD_<track>_<strategy>_<decision_id>.json`
- Prompt export command implemented in `scripts/export_llm_prompts.py`.
- Manual missing responses fail with explicit response paths.
- JSON responses are parsed from raw JSON or markdown fences and validated against schemas.

## Configs Implemented

Implemented valid YAML with required sections:

- `configs/base.yaml`
- `configs/paths.yaml`
- `configs/logging.yaml`
- `configs/track1/s0_baselines.yaml`
- `configs/track1/s1_quant_core.yaml`
- `configs/track1/s2_llm_regime.yaml`
- `configs/track1/s3_llm_alpha_tilt.yaml`
- `configs/track1/s4_event_exposure.yaml`
- `configs/track2/s0_baselines.yaml`
- `configs/track2/s1_quant_core.yaml`
- `configs/track2/s2_llm_regime.yaml`
- `configs/track2/s3_llm_alpha_tilt.yaml`
- `configs/track2/s4_event_exposure.yaml`

## Scripts Implemented

- `scripts/run_strategy.py`
- `scripts/run_backtest.py`
- `scripts/run_batch.py`
- `scripts/run_ablation.py`
- `scripts/compare_runs.py`
- `scripts/make_report.py`
- `scripts/validate_no_leakage.py`
- `scripts/export_llm_prompts.py`
- `scripts/package_submission.py`

## Tests Added

- `tests/test_target_weights.py`
- `tests/test_constraints.py`
- `tests/test_turnover.py`
- `tests/test_trade_converter.py`
- `tests/test_s0_baselines.py`
- `tests/test_s1_quant_core.py`
- `tests/test_llm_schemas.py`
- `tests/test_manual_llm_io.py`
- `tests/test_config_loading.py`
- `tests/test_metrics.py`
- `tests/test_official_untouched.py`
- `tests/test_llm_fallbacks.py`

## Verification Commands

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python -B -m compileall src scripts tools
python -m pytest -q tests -p no:cacheprovider
python scripts/run_strategy.py --track track1 --strategy s0_equal_weight --config configs/track1/s0_baselines.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
python scripts/run_strategy.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
python scripts/export_llm_prompts.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-03
```

Final verification also included:

```powershell
python -c "import fastapi, uvicorn; print('official server dependencies available')"
python scripts/validate_no_leakage.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
python scripts/run_backtest.py --help
git diff --check
git status --short -- NLPCC_tasks
git status --short --untracked-files=all
```

## Verification Results

- `compileall` passed when rerun outside sandbox after sandbox denied `.pyc` rename operations.
- `pytest`: `30 passed`.
- S0 equal-weight dry-run passed and wrote `.var/runs/track1_s0_equal_weight_20240102_20240110_off_54dc6f57`.
- S1 Track 1 dry-run passed and wrote `.var/runs/track1_s1_quant_core_20240102_20240110_off_a75fe359`.
- Manual prompt export passed and wrote prompts under `.var/manual_llm/requests/track1_s2_llm_regime_20240102_20240103_manual_b9fcfe70`.
- Leakage validator passed for Track 1 S1 over 2024-01-02 to 2024-01-10.
- `scripts/run_backtest.py --help` passed after fixing direct-script import behavior.
- `git diff --check` passed with line-ending warnings only.
- `git status --short -- NLPCC_tasks` remained clean during implementation.
- Official server smoke was not feasible because `fastapi` is not installed in the active environment.

## Known Limitations

- Official CSV data is absent in this checkout, so offline runs use a deterministic official-compatible synthetic loader.
- Official server/demo smoke was not run because `fastapi` is missing and public CSV data is absent in this checkout.
- Trade converter needs reconciliation against official backtest behavior.
- Same-day news policy needs concrete official examples.
- Manual LLM prompt/response quality needs real pasted model outputs.
- Metrics are basic deterministic reproducers and need official alignment checks.

## Required Fixes Before Phase 1v

- Verify trade converter against official backtest behavior.
- Verify DataLoader same-day news policy with concrete examples.
- Run broader S0/S1 date-range tests.
- Verify manual LLM prompt/response round-trip.
- Check no accidental official starter-kit modifications.
- Check all run artifacts stay under `.var/`.
- Confirm metrics calculations against a hand-computed small example.

## Self-Review Checklist

- [x] Read all required files.
- [x] Preserved `NLPCC_tasks/`.
- [x] Implemented real S0 baselines.
- [x] Implemented S1 Track 1 and Track 2.
- [x] Implemented S2/S3 structured LLM systems with manual mode.
- [x] Implemented S4 mainly as Track 2 event overlay.
- [x] Kept all strategies target-weight-first.
- [x] Kept official trade conversion in execution layer.
- [x] Implemented no-leakage checks.
- [x] Implemented metric reproducer basics.
- [x] Avoided committed raw LLM outputs.
- [x] Wrote run artifacts under `.var/`.
- [x] Updated docs and command reference.
- [x] Ran tests and dry-runs.
- [x] Listed unresolved issues honestly.

## Final Readiness Status

Ready for Phase 1v.
