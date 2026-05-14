# Command Reference

Commands assume PowerShell from the repository root.

## Environment

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
```

## Official Starter Kit

```powershell
cd .\NLPCC_tasks
python .\start_server.py
```

```powershell
cd .\NLPCC_tasks
python .\agent_platform\demo_backtest.py --track macro --model gpt-5 --start-date 2025-01-02 --end-date 2025-01-31
```

## Local Strategy Runs

```powershell
python scripts/run_strategy.py --track track1 --strategy s0_equal_weight --config configs/track1/s0_baselines.yaml --start-date 2024-01-02 --end-date 2024-01-31 --llm-mode off --dry-run
```

```powershell
python scripts/run_strategy.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-03-31 --llm-mode off
```

```powershell
python scripts/run_strategy.py --track track2 --strategy s1_quant_core --config configs/track2/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-03-31 --llm-mode off
```

## Manual LLM

```powershell
python scripts/export_llm_prompts.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-05
```

```powershell
python scripts/run_strategy.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-05 --llm-mode manual
```

## Validation

```powershell
python -B -m compileall src scripts tools
python -m pytest -q tests -p no:cacheprovider
python scripts/validate_no_leakage.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --start-date 2024-01-02 --end-date 2024-01-10 --llm-mode off --dry-run
git diff --check
git status --short -- NLPCC_tasks
```

## Reports And Comparison

```powershell
python scripts/compare_runs.py --run-dir .var/runs --metric annualized_sharpe --output .var/outputs/run_comparison.csv
```

```powershell
python scripts/make_report.py --run-id RUN_ID --output docs/reports/implementation_logs
```

## Submission Draft

```powershell
python scripts/package_submission.py --track track1 --strategy s1_quant_core --config configs/track1/s1_quant_core.yaml --output-dir .var/submissions
```
