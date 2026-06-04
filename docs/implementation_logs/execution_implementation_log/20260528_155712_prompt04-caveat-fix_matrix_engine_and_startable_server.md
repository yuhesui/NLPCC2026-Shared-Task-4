# Implementation Log: prompt04-caveat-fix - matrix_engine_and_startable_server

**Created:** 2026-05-28 15:57:12

## Summary

Replaced the batch-wrapper caveat with a NumPy matrix backtesting engine and upgraded the official server runner with start/probe/stop/startability support.

## Files Changed

src/tools/backtesting/vectorized_backtester.py,src/tools/backtesting/official_server_runner.py,tests/test_tools/test_backtesting/test_prompt04_backtesting_tools.py,outputs/backtests/real_train_2024_matrix_equal_weight_macro.json

## Tests / Checks

PYTHONPATH=src python -B -c OfficialServerRunner.start(wait_seconds=20) returned ready on /api/health/ready; PYTHONPATH=src python -B real 2024 matrix equal-weight macro run wrote outputs/backtests/real_train_2024_matrix_equal_weight_macro.json; PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -B -m pytest tests/test_tools/test_backtesting tests/test_tools/test_verification/test_prompt04_verification.py tests/test_tools/test_experiments tests/test_tools/test_optimiser tests/test_tools/test_reporting tests/test_nlpcc/test_stage3_trade tests/test_nlpcc/test_stage4_agent -p no:cacheprovider (27 passed)

## Caveats

The matrix engine evaluates target-weight matrices and is intended for vectorized research evaluation; official trade-cash semantics remain covered by LocalSmokeBacktester. The official server was already running, so start() verified readiness and did not spawn a duplicate process.

## Artifacts

- None

## Next Steps

Use matrix backtests for fast allocation sweeps and keep local/official parity checks on LocalSmokeBacktester or the official HTTP server.
