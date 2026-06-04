# Implementation Log: prompt10 - ablation_experiment_suite

**Created:** 2026-05-28 23:55:24

## Summary

Implemented reproducible experiment configs, ablation suite generation, broad agent experiment runner, result hashing/storage, report tables/figures, CLI wrappers, and ran a 14-run real train_2024 prompt10 suite.

## Files Changed

src/tools/backtesting/local_backtester.py,src/tools/experiments/experiment_config.py,src/tools/experiments/runner.py,src/tools/experiments/ablations.py,src/tools/experiments/result_store.py,src/tools/reporting/tables.py,src/tools/reporting/figures.py,src/tools/reporting/report_builder.py,src/tools/reporting/experiment_report.py,scripts/run_experiment.py,scripts/generate_report.py,configs/tools/experiments/prompt10_ablation_suite.json,tests/test_tools/test_experiments/test_prompt10_ablation_suite.py,tests/test_tools/test_reporting/test_prompt10_experiment_report.py,outputs/experiments/prompt10,outputs/reports/prompt10

## Tests / Checks

PYTHONPATH=src python -B -c import checks for experiments/reporting modules; python -B -m pytest tests/test_tools/test_experiments tests/test_tools/test_reporting -p no:cacheprovider; python -B -m pytest tests/test_tools/test_backtesting tests/test_tools/test_experiments tests/test_tools/test_reporting -p no:cacheprovider; python -B scripts/run_experiment.py --config configs/tools/experiments/prompt10_ablation_suite.json --output-dir outputs/experiments/prompt10 --report-dir outputs/reports/prompt10; python -B scripts/generate_report.py --input-dir outputs/experiments/prompt10 --report-dir outputs/reports/prompt10_regenerated

## Caveats

The prompt10 suite uses the first 30 trading dates from real 2024 training data for speed, not a full-year selection run. Text ablations use deterministic no-LLM extraction because no external API is required or used. Generated prompt10_regenerated artifacts are a CLI verification duplicate of the main report outputs.

## Artifacts

- None

## Next Steps

Run the same suite over the full 2024 training year and then the locked 2025 public A-list once prompt11 verification passes.
