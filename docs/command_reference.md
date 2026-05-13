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
python .\scripts\run_strategy.py --track track1 --strategy s1_quant_core --config .\configs\track1\s1_quant_core.yaml
```

Status: PLANNED - not implemented yet.

Run future batch experiments:

```powershell
python .\scripts\run_batch.py --config .\configs\track1\s1_quant_core.yaml --output-dir .\.var\runs
```

Status: PLANNED - not implemented yet.

## Tests and Validation

Run lightweight tests:

```powershell
python -m pytest tests
```

Run future no-leakage checks:

```powershell
python .\scripts\validate_no_leakage.py --track track1 --config .\configs\track1\s1_quant_core.yaml
```

Status: PLANNED - not implemented yet.

## Reports

Create an implementation log:

```powershell
python .\tools\create_impl_log.py "repo init"
```

Generate future implementation reports:

```powershell
python .\scripts\make_report.py --run-id RUN_ID --output-dir .\docs\reports\implementation_logs
```

Status: PLANNED - not implemented yet.

Compare future runs:

```powershell
python .\scripts\compare_runs.py --runs-dir .\.var\runs --metric sharpe
```

Status: PLANNED - not implemented yet.

## Submission Packaging

Package a future submission:

```powershell
python .\scripts\package_submission.py --track track1 --run-id RUN_ID --output-dir .\.var\submissions
```

Status: PLANNED - not implemented yet.

## Safe Local Cleanup

Remove selected ignored runtime artifacts after inspecting `.var/` contents:

```powershell
Remove-Item -LiteralPath .\.var\cache,.\.var\outputs,.\.var\logs,.\.var\artifacts -Recurse -Force
```

Use only for local generated artifacts. Do not run cleanup against `NLPCC_tasks/`, `src/`, `configs/`, `scripts/`, `tests/`, `tools/`, or `docs/`.
