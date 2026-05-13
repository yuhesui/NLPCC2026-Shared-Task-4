# Command Reference

Commands assume PowerShell from the repository root unless noted.

## Environment

Create a local environment:

```powershell
py -3.13 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install official starter-kit dependencies:

```powershell
pip install -r .\NLPCC_tasks\requirements.txt
```

Install local package in editable mode, after project dependencies are defined:

```powershell
pip install -e .
```

## Official Starter Kit

Start the official server:

```powershell
cd .\NLPCC_tasks
python .\start_server.py
```

Run the official demo agent:

```powershell
cd .\NLPCC_tasks
python .\agent_platform\demo_backtest.py --track macro --model gpt-5 --start-date 2025-01-02 --end-date 2025-01-31
```

Run the offline DataLoader smoke check:

```powershell
cd .\NLPCC_tasks
python .\dataset\dataloader_eval.py
```

## Custom Strategy Runs

Run a future strategy once:

```powershell
python -m nlpcc4.experiments.run_strategy --track track1 --strategy s1_quant_core --config .\configs\track1\s1_quant_core.yaml
```

Status: PLANNED - not implemented yet.

Run future batch experiments:

```powershell
python -m nlpcc4.experiments.run_batch --config .\configs\track1\s1_quant_core.yaml --output .\.var\runs
```

Status: PLANNED - not implemented yet.

## Tests and Validation

Run lightweight tests:

```powershell
$env:PYTHONPATH = "$PWD\src"
pytest
```

Run future no-leakage checks:

```powershell
python -m nlpcc4.data.leakage_checks --track track1 --start-date 2025-01-02 --end-date 2025-01-31
```

Status: PLANNED - not implemented yet.

## Reports

Create an implementation log:

```powershell
python .\tools\create_impl_log.py "repo init"
```

Generate future implementation reports:

```powershell
python -m nlpcc4.reports.generate_report --run-id RUN_ID --output .\docs\reports\implementation_logs
```

Status: PLANNED - not implemented yet.

Compare future runs:

```powershell
python -m nlpcc4.reports.compare_runs --runs-dir .\.var\runs --metric sharpe
```

Status: PLANNED - not implemented yet.

## Submission Packaging

Package a future submission:

```powershell
python -m nlpcc4.submission.package_submission --track track1 --run-id RUN_ID --output .\submissions
```

Status: PLANNED - not implemented yet.

## Safe Local Cleanup

Remove ignored runtime artifacts:

```powershell
Remove-Item -LiteralPath .\.var,.\outputs,.\logs,.\cache,.\artifacts -Recurse -Force
```

Use only for local generated artifacts. Do not run cleanup against `NLPCC_tasks/`, `src/`, `configs/`, `scripts/`, `tests/`, or `docs/`.
