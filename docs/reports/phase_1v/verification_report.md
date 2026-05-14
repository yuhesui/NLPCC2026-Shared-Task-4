# Phase 1v Verification Report

## Scope

Phase 1v audited the Phase 1a runnable strategy system for repository boundaries, target-weight-first strategy behavior, offline strategy execution, manual LLM workflow, leakage assumptions, config validity, runtime artifact policy, metrics edge cases, and implementation-log completeness.

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `python -B -m compileall src scripts tools` | Pass with elevated filesystem permission | Initial sandbox run failed on Windows `.pyc` rename permissions. The exact command passed when rerun with approved filesystem access. |
| `python -m pytest -q tests -p no:cacheprovider` | Pass | `37 passed`. |
| `python scripts/run_strategy.py --help` | Pass | CLI exposes required arguments. |
| `python scripts/run_batch.py --help` | Pass | CLI exposes required arguments. |
| `python scripts/run_ablation.py --help` | Pass | CLI exposes required arguments. |
| `python scripts/export_llm_prompts.py --help` | Pass | CLI exposes required arguments. |
| all YAML configs via `load_config` | Pass | `15` configs checked. |
| `python scripts/validate_no_leakage.py --config configs/track1/s1_quant_core.yaml --dry-run` | Pass | Phase 1v fixed track/date inference for this documented command shape. |

## Dry-Runs Run

| Strategy | Track | Date range | Result |
| --- | --- | --- | --- |
| `s0_equal_weight` | `track1` | 2024-01-02 to 2024-01-10 | Pass; artifacts under `.var/runs/track1_s0_equal_weight_20240102_20240110_off_54dc6f57/`. |
| `s1_quant_core` | `track1` | 2024-01-02 to 2024-01-10 | Pass; artifacts under `.var/runs/track1_s1_quant_core_20240102_20240110_off_a75fe359/`. |
| `s1_quant_core` | `track2` | 2024-01-02 to 2024-01-10 | Pass; artifacts under `.var/runs/track2_s1_quant_core_20240102_20240110_off_5ffdf51e/`. |
| `s2_llm_regime` | `track1` | 2024-01-02 to 2024-01-03 | Pass in `off` mode; S1 fallback/neutral behavior. |
| `s3_llm_alpha_tilt` | `track1` | 2024-01-02 to 2024-01-03 | Pass in `off` mode; S1 fallback/neutral behavior. |
| `s4_event_exposure` | `track2` | 2024-01-02 to 2024-01-03 | Pass in `off` mode; S1 fallback/neutral behavior. |

All checked runs contained `config_resolved.yaml`, `target_weights.csv`, `trades.csv`, `holdings.csv`, `diagnostics.json`, `metrics.json`, and `run_summary.md`.

## Static Contract Audit

- Strategy modules do not emit final official trade payloads.
- Strategy modules do not call the official API directly.
- Official payload generation remains centralized in `src/nlpcc4/execution/trade_converter.py`.
- Runtime outputs were written under `.var/`.
- No changes were detected under `NLPCC_tasks/`.
- No API keys or raw LLM outputs were found in committed-source paths.

## Target-Weight And Trade-Conversion Checks

Added or verified tests for:

- nonnegative target weights and sum <= 1.0,
- cap projection with cash residual when caps bind all assets,
- no-trade band,
- turnover cap,
- buy scaling to available cash after cash buffer,
- zero portfolio value,
- tiny differences,
- no use of sell proceeds for same-call buys.

Official reconciliation remains important before live official-server use because the server settles holdings with same-day returns before executing close-price trades.

## Metrics Checks

Added or verified hand-computable tests for:

- daily return conversion,
- cumulative return,
- zero-volatility Sharpe,
- max drawdown,
- turnover totals,
- concentration,
- cost drag.

## Leakage Audit

The official loader still hides current-day close/high/low/change/pct_change from decision-time history and exposes current-day open. Same-day news before 15:00 is available in official code, but the custom default remains conservative:

```yaml
data:
  same_day_news_policy: previous_day_only
```

Status: unresolved; conservative default is `previous_day_only`.

No hardcoded 2025 leaderboard tuning or current-day return signal use was found in the Phase 1a custom strategy modules during static audit.

## Runtime Artifact Audit

`git check-ignore -v` confirmed `.var/`, manual LLM request/response paths, root runtime folders, secrets, archives, and pickle files are ignored. Root cleanliness check found no unexpected top-level entries.

## Optional Official Smoke

Not verified. `python -c "import fastapi, uvicorn"` failed with `ModuleNotFoundError: No module named 'fastapi'`, so the official server/demo smoke test was not feasible in the active environment.

