# Implementation Log: prompt01 - env_data_smoke_pipeline

**Created:** 2026-05-28 10:35:03

## Summary

Added data manifest/mirror tooling, synthetic smoke dataset, deterministic one-asset smoke agent, local smoke backtester, official server smoke diagnostic runner, and integration tests.

## Files Changed

.gitignore,src/tools/data_tools/manifest_builder.py,src/tools/data_tools/dataset_mirror.py,src/tools/data_tools/local_data_catalog.py,src/tools/data_tools/dataset_validator.py,src/nlpcc/core/fund_universe.py,src/nlpcc/stage4_agent/models/smoke_one_unit_agent.py,src/tools/backtesting/local_backtester.py,src/tools/backtesting/vectorized_backtester.py,src/tools/backtesting/cuda_backend.py,scripts/run_local_smoke.py,scripts/run_official_server_smoke.py,tests/test_integration/test_prompt01_smoke.py,data/train_2024/manifests/,data/public_a_2025/manifests/,data/sample/smoke_test/,outputs/smoke_tests/

## Tests / Checks

python -m tools.data_tools.dataset_mirror; python scripts/run_local_smoke.py --track macro; python scripts/run_official_server_smoke.py; python -m pytest tests/test_tools/test_verification/test_implementation_log.py tests/test_integration/test_prompt01_smoke.py -p no:cacheprovider

## Caveats

Official dataset CSVs are Git LFS pointer files in this checkout, so 2024/2025 split copies are recorded as skipped_lfs_pointer in manifests. Official server smoke is blocked because localhost:6207 refused the connection. Local smoke uses a synthetic plumbing-only subset under data/sample/smoke_test/.

## Artifacts

- `outputs/smoke_tests/data_setup_summary.json`
- `outputs/smoke_tests/local_smoke.json`
- `outputs/smoke_tests/official_server_smoke.json`

## Next Steps

Hydrate official LFS data and start the official server, then rerun data setup and official smoke before prompt02 data-contract work.
