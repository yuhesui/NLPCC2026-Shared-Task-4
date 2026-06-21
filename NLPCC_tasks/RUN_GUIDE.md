# Run Guide

## 1. Prepare the Clean Environment

```powershell
cd D:\Projects\NLPCC2026-Shared-Task-4\NLPCC_tasks
py -3 -m venv .venv_submission_check
.\.venv_submission_check\Scripts\python.exe -m pip install --upgrade pip
.\.venv_submission_check\Scripts\python.exe -m pip install -r requirements-submission-lock.txt
.\.venv_submission_check\Scripts\python.exe -m pip check
```

If offline, replace the install command with an approved wheelhouse command. Do not use a user cache or online model download. A successful `pip check` must return exit code 0.

## 2. Verify Model Artifacts

```powershell
.\.venv_submission_check\Scripts\python.exe -c "from pathlib import Path; from nlpcc.news_overlay.production_tensor import BGE_SNAPSHOT, FINBERT_SNAPSHOT; print(BGE_SNAPSHOT, BGE_SNAPSHOT.exists()); print(FINBERT_SNAPSHOT, FINBERT_SNAPSHOT.exists())"
```

Expected result: both paths are under `package/models/` and both exist. Compare hashes with `submission_audit/model_artifact_audit.csv`.

## 3. Start the Official-Style Server

```powershell
.\.venv_submission_check\Scripts\python.exe start_server.py
```

Expected endpoint: `http://localhost:6207/api/health`. Keep this terminal open.

## 4. Run Track A

```powershell
.\.venv_submission_check\Scripts\python.exe -m agent_platform.demo_backtest --track macro --start-date 2025-01-02 --end-date 2025-12-31 --lookback-days 60
```

Expected agent: `A2_real / G11A`, labelled risk parity + local BGE/FinBERT news overlay. Expected local outputs: `runtime_logs/macro_phase12_final/` and `agent_platform/demo_outputs/`.

## 5. Run Track B

```powershell
.\.venv_submission_check\Scripts\python.exe -m agent_platform.demo_backtest --track sector --start-date 2025-01-02 --end-date 2025-12-31 --lookback-days 60
```

Expected agent: `B2_real / G15B`, labelled S1 sector core + local BGE/FinBERT news overlay. Preserve the fixed-policy caveat in any report of results.
