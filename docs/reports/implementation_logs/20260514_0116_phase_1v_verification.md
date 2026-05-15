# Phase 1v Verification

## Summary

Verified the Phase 1a S0-S4 strategy system skeptically, fixed Phase 1v-scope defects, expanded edge-case tests, and wrote Phase 1v evidence reports.

Initial status:

```text
Get-Location -> D:\Projects\NLPCC2026-Shared-Task-4
git status --short -- NLPCC_tasks -> clean
```

## Read-First Evidence Table

| File | Exists? | Key facts extracted | Phase 1v implication | Action taken |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Yes | Official starter kit is vendor code; strategies output target weights first; custom code under `src/nlpcc4/`. | Audit boundary and target-weight contract. | No edit. |
| `README.md` | Yes | Task uses daily news/prices, target weights/rebalancing, Sharpe focus, 0.01% friction. | Verify metrics, data, strategy outputs. | No edit. |
| `NLPCC_tasks/README.md` | Yes | Official mechanics: current open visible, current close/high/low hidden, same-day news before 15:00, close execution. | Re-inspect official mechanics and leakage assumptions. | No edit. |
| `docs/design/repo_architecture.md` | Yes | `.var/` is runtime sink; trade converter owns official payload conversion. | Audit runtime and direct-trade boundaries. | No edit. |
| `docs/research/strategy_decision_summary.md` | Yes | S1 first; S2/S3 bounded JSON only; S4 mainly Track 2; no direct LLM trades. | Verify strategy policy compliance. | No edit. |
| `docs/reports/implementation_logs/20260514_0033_phase_1a_strategy_system_build.md` | Yes | Phase 1a claimed runnable S0-S4, manual LLM, tests, docs, official starter kit clean. | Primary Phase 1a claims to verify. | No edit. |
| `docs/reports/phase_1a/official_mechanics_notes.md` | Yes | Notes match official code: current-day hidden fields, buy-before-sell, monetary holdings. | Cross-check mechanics. | No edit. |
| `docs/reports/phase_1a/phase_1a_strategy_system.md` | Yes | Documents target-weight-first architecture and `.var/runs` artifacts. | Verify outputs and contract. | No edit. |
| `docs/reports/phase_1a/manual_llm_workflow.md` | Yes | Manual requests/responses paths and validation behavior documented. | Verify prompt export and response ingestion. | No edit. |
| `docs/command_reference.md` | Yes | Lists validation and strategy commands. | Validate documented command shape. | No edit. |
| `.gitignore` | Yes | `.var/`, root runtime folders, secrets, archives ignored. | Runtime audit target. | No edit. |
| `src/nlpcc4/strategies/base.py` | Yes | Strategy protocol returns target weights through `StrategyOutput`. | Contract baseline. | No edit. |
| `src/nlpcc4/execution/trade_converter.py` | Yes | Converts target weights into official buy/sell payloads and limits buys to cash. | Edge-case tests added. | Tests expanded. |
| `src/nlpcc4/llm/manual_io.py` | Yes | Writes prompts, reads matching response JSON, raises missing/invalid errors. | Verify manual round-trip and bad-file behavior. | Tests expanded. |
| `src/nlpcc4/llm/schemas.py` | Yes | Bounded regime, alpha, and event schemas. | Schema validation remained in place. | No edit. |
| `src/nlpcc4/data/leakage_checks.py` | Yes | Checks no future rows and no current close/high/low/change/pct_change. | Leakage validator exercised. | No edit. |
| `src/nlpcc4/metrics/performance.py` | Yes | Summarizes cumulative return, Sharpe, drawdown, turnover, cost, concentration. | Hand examples added. | Tests expanded. |
| `tests/*.py` | Yes | Phase 1a had 30 passing tests but limited edge coverage. | Add Phase 1v adversarial coverage. | Modified tests. |
| official `data_loader.py` | Yes | Current history hides same-day close/high/low/change/pct_change; news before 15:00 retained. | Same-day news remains unresolved but conservative default is correct. | No edit. |
| official `backtest.py` | Yes | Holdings are values; same-day settlement before trades; buys before sells; commission 0.0001. | Trade converter assumption verified as conservative. | No edit. |
| official `api/backtest.py` | Yes | API trade/status/day-data/results endpoints and aligned history helpers. | Official server smoke remains dependency-bound. | No edit. |
| official `platform_client.py` | Yes | Client submits official trades via API. | Strategies must not call it directly. | No edit. |
| official `dataloader_eval.py` | Yes | Mirrors hidden current-day price fields and same-day news filter. | Confirms official-compatible leakage policy. | No edit. |

## Phase 1a Claims Verified

- S0/S1/S2/S3/S4 dry-runs execute without API keys in `off` mode.
- Manual prompt export works for S2, S3, and S4.
- Valid pasted manual JSON is ingested.
- Missing manual response fails clearly.
- Invalid manual response now fails clearly after Phase 1v fix.
- Target-weight-first boundary holds in static audit.
- Runtime artifacts are under `.var/`.
- Official starter kit remains clean.

## Static Contract Audit

Searches over `src/` and `docs/` found no strategy modules emitting final official trade payloads and no official API calls inside strategy modules. Buy/sell payload creation remains in `src/nlpcc4/execution/trade_converter.py` and local backtest simulation code. `OPENAI_API_KEY` appears only as an environment lookup in `src/nlpcc4/llm/client.py`.

## Tests Run

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python -B -m compileall src scripts tools
python -m pytest -q tests -p no:cacheprovider
python scripts/run_strategy.py --help
python scripts/run_batch.py --help
python scripts/run_ablation.py --help
python scripts/export_llm_prompts.py --help
python scripts/validate_no_leakage.py --config configs/track1/s1_quant_core.yaml --dry-run
python scripts/validate_no_leakage.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
```

Results:

- `compileall`: passed with approved filesystem access. Sandbox-only runs failed on Windows `.pyc` rename permission errors.
- `pytest`: `37 passed`.
- CLI help commands: passed.
- All 15 YAML configs loaded.
- Leakage validator: passed for minimal and explicit command forms.

## Dry-Runs Run

```powershell
python scripts/run_strategy.py --track track1 --strategy s0_equal_weight --config configs/track1/s0_baselines.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
python scripts/run_strategy.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
python scripts/run_strategy.py --track track2 --strategy s1_quant_core --config configs/track2/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
python scripts/run_strategy.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-03 --llm-mode off --dry-run
python scripts/run_strategy.py --track track1 --strategy s3_llm_alpha_tilt --config configs/track1/s3_llm_alpha_tilt.yaml --start-date 2024-01-02 --end-date 2024-01-03 --llm-mode off --dry-run
python scripts/run_strategy.py --track track2 --strategy s4_event_exposure --config configs/track2/s4_event_exposure.yaml --start-date 2024-01-02 --end-date 2024-01-03 --llm-mode off --dry-run
```

All passed. Required output files were present for checked runs under `.var/runs/<run_id>/`.

## Manual LLM Workflow Verification

Prompt export passed for:

- `phase1v_manual_s2`
- `phase1v_manual_s3`
- `phase1v_manual_s4`

Prompt inspection confirmed:

- JSON schemas are included.
- Direct allocation/trading is prohibited.
- Exact response file paths are printed.
- Prompt/response files stay under `.var/manual_llm/`.

Valid pasted JSON:

- `phase1v_manual_s2` one-day manual run passed with a dummy neutral regime response.

Missing response:

- `phase1v_missing_s2` failed with the exact missing response path.

Invalid response:

- Initially fell back to S1, which was a Phase 1v defect.
- Fixed by re-raising `ManualResponseInvalid` in manual mode for S2/S3/S4.
- Final invalid-response command failed clearly with the invalid response path.

## Target-Weight and Trade-Conversion Verification

Added tests for:

- cap binding with cash residual,
- zero portfolio value,
- tiny no-trade differences,
- buy scaling to cash after buffer,
- no use of same-call sell proceeds for buys.

Remaining official assumption: the converter is conservative about buy cash because the official engine executes buys before sells.

## Metrics Verification

Added hand-computable tests for:

- daily returns,
- cumulative return,
- max drawdown,
- zero-volatility Sharpe,
- turnover totals,
- concentration,
- cost drag.

## Leakage Audit

Official code confirms current-day close/high/low/change/pct_change are hidden from decision-time historical prices. Same-day news before 15:00 is retained in current official code, but the custom default remains:

```yaml
data:
  same_day_news_policy: previous_day_only
```

Status: unresolved; conservative default is `previous_day_only`.

No hardcoded 2025 leaderboard tuning or current-day return signal use was found during static audit.

## Runtime Artifact Audit

```powershell
git check-ignore -v .var/cache/x .var/runs/x .var/manual_llm/requests/x .var/manual_llm/responses/x logs/x outputs/x raw_llm_outputs/x .env .env.local test.zip test.pkl
git diff --check
root cleanliness check
```

Results:

- `.var/`, root runtime folders, secrets, archives, pickle files are ignored.
- Root cleanliness check found no unexpected top-level entries.
- `git diff --check` passed with line-ending warnings only.

## Official Starter-Kit Status

`git status --short -- NLPCC_tasks` returned no changes before and after Phase 1v.

Official server/demo smoke was not run because `fastapi` is missing:

```text
ModuleNotFoundError: No module named 'fastapi'
```

## Files Modified

- `configs/backtest_2024_train.yaml`
- `configs/backtest_2025_phase_a.yaml`
- `scripts/validate_no_leakage.py`
- `src/nlpcc4/llm/prompts/alpha_score.md`
- `src/nlpcc4/llm/prompts/event_exposure.md`
- `src/nlpcc4/llm/prompts/news_summary.md`
- `src/nlpcc4/llm/prompts/regime_classifier.md`
- `src/nlpcc4/strategies/track1_macro/s2_llm_regime.py`
- `src/nlpcc4/strategies/track1_macro/s3_llm_alpha_tilt.py`
- `src/nlpcc4/strategies/track2_sector/s2_llm_regime.py`
- `src/nlpcc4/strategies/track2_sector/s3_llm_alpha_tilt.py`
- `src/nlpcc4/strategies/track2_sector/s4_event_exposure.py`
- `tests/test_config_loading.py`
- `tests/test_constraints.py`
- `tests/test_llm_fallbacks.py`
- `tests/test_manual_llm_io.py`
- `tests/test_metrics.py`
- `tests/test_trade_converter.py`

## Bugs Found and Fixed

1. `scripts/validate_no_leakage.py` did not support the documented minimal `--config ... --dry-run` command.
   - Fixed by inferring track from config/path and defaulting date range from config.
2. Legacy backtest configs did not include all Phase 1a required sections, and YAML parsed unquoted `off` as boolean false.
   - Fixed by adding `llm.mode: "off"` and conservative news policy.
3. Manual invalid JSON was not rejected for S2 manual mode.
   - Fixed by re-raising `ManualResponseInvalid` for S2/S3/S4 manual paths.
4. LLM prompt templates still contained stale placeholder text.
   - Fixed by removing `PLANNED - not implemented yet.` language.
5. Phase 1a tests lacked several required edge checks.
   - Fixed with additional config, metrics, converter, constraint, and manual invalid-response tests.

## Remaining Issues

Blocking:

- None.

Important but non-blocking:

- Official server/demo smoke remains unverified until `fastapi`/server dependencies are installed.
- Official public CSV data is absent in this checkout; offline dry-runs used the deterministic synthetic loader.
- Same-day news policy needs concrete official-data examples.
- Trade converter needs reconciliation against official server behavior.
- Metrics should be compared against official result parsing after an official server smoke run.

Optional enhancement:

- Broader 2024 dry-runs for all S0 baselines.
- Manual pasted-response round-trip for S3/S4 in addition to S2.
- Longer-window fallback diagnostics.

## Required Fixes Before Phase 1b

Blocking:

- None.

Important but non-blocking:

- Install official server dependencies and run server/demo smoke.
- Verify trade converter against a real official session.
- Verify DataLoader same-day news policy with concrete examples.
- Compare local metrics against official result parser on a small official run.

Optional enhancement:

- Broaden dry-runs and add summarized fallback-rate diagnostics.

## Self-Review Checklist

- [x] Read the Phase 1a log.
- [x] Preserved official starter-kit files.
- [x] Ran syntax verification.
- [x] Ran tests.
- [x] Ran strategy dry-runs.
- [x] Tested manual LLM prompt generation.
- [x] Tested manual pasted-response ingestion.
- [x] Tested invalid and missing manual responses.
- [x] Verified runtime artifacts are ignored.
- [x] Verified no strategy emits direct official trade payloads.
- [x] Verified no strategy calls official API directly.
- [x] Verified metrics on small examples.
- [x] Checked target-weight constraints and trade converter edge cases.
- [x] Checked root cleanliness.
- [x] Ran `git diff --check`.
- [x] Created Phase 1v reports.
- [x] Listed unresolved issues honestly.

## Final Readiness Status

Ready for Phase 1b.
