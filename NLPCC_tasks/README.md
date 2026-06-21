# NLPCC 2026 Shared Task 4 Submission Package

## Overview

This is a standalone, local-only submission package for NLPCC 2026 Shared Task 4. It contains the selected Phase12 agents, a minimal vendored runtime, the official-style server, and the two required transformer artifacts. It does not load parent workspace code, report folders, user caches, Prompt06 alpha mining, or Prompt07b factor-panel research.

The package is an academic shared-task system, not investment advice. Candidate selection is fixed: 2024 was used for fitting/selection, 2025 is frozen public evaluation only, and hidden 2026 data is never accessed by the agents.

## Included Agents

- **News Track A best candidate:** risk parity + local BGE/FinBERT news overlay (`A2_real / G11A`).
- **Track A no-news reference:** shrinkage risk parity only.
- **News Track B best candidate:** S1 sector core + local BGE/FinBERT news overlay (`B2_real / G15B`).
- **Track B no-news reference:** S1 sector core only.

`agent_platform/agents/build_agent.py` defaults to the selected `phase12_final` path. Track A and Track B wrappers pin the fixed candidate IDs and reject cross-track calls.

## Model Architecture

Visible Top-20 news is ranking-sorted, content-deduplicated, and cutoff-safe. A local fine-tuned BGE-compatible four-layer BERT encoder creates L2-normalized relevance embeddings. A local Chinese FinBERT sequence classifier produces positive/negative sentiment, confidence, and normalized uncertainty. Per-fund relevance, event, aspect, sentiment, and recency fields form a centered bounded overlay.

Track A uses a shrinkage covariance risk-parity base. Track B uses an S1 sector core blending inverse volatility, momentum, and sector trend, followed by drawdown and breadth adjustment. Both agents enforce long-only target weights, a 0.97 invested target, per-fund caps, L1 overlay caps, turnover caps, local-only model loading, and fail-closed missing-model behavior.

## Folder Structure

```text
agent_platform/       selected agent wrappers, client, and local runner
nlpcc/                vendored selected-runtime implementation closure
package/configs/      package-relative Phase12 configuration
package/models/       bundled BGE and Chinese FinBERT artifacts
server_platform/      official-style local API server and DataLoader
dataset/              organizer-provided public data location (not committed)
tests/                selected-runtime package tests
submission_audit/     scope, model, LFS, dependency, and readiness evidence
```

## Environment Setup

Use a clean virtual environment without system site packages. The dependency lock is intentionally separate from the project-wide development environment.

```powershell
cd <PACKAGE_ROOT>
py -3 -m venv .venv_submission_check
.\.venv_submission_check\Scripts\python.exe -m pip install --upgrade pip
.\.venv_submission_check\Scripts\python.exe -m pip install -r requirements-submission-lock.txt
.\.venv_submission_check\Scripts\python.exe -m pip check
```

For offline installation, use an approved wheelhouse containing the exact lock versions. Do not replace the local model paths with an online download fallback.

## Model Artifacts

The two runtime model directories are package-relative:

```text
package/models/bge_contrastive_finetuned_2024_dev_best/
package/models/finbert_tone_chinese_e91b1a3/
```

They are checked by `submission_audit/model_artifact_audit.csv`. Both are loaded using `local_files_only=True`. Git LFS is required for the FinBERT safetensors file.

## Run Track A

```powershell
python -m agent_platform.demo_backtest --track macro --start-date 2025-01-02 --end-date 2025-12-31 --lookback-days 60
```

This runs the fixed A2_real/G11A local agent against the official-style server. Use `RUN_GUIDE.md` for the server startup sequence and expected files.

## Run Track B

```powershell
python -m agent_platform.demo_backtest --track sector --start-date 2025-01-02 --end-date 2025-12-31 --lookback-days 60
```

This runs the fixed B2_real/G15B local agent. B2 is packaged because policy is fixed and runtime parity is verified; it must not be claimed to beat B0 or the zeroed/shuffled controls.

## Run HTTP Official-Style Server

```powershell
python start_server.py
```

The default local address is `http://localhost:6207`. Start the server in one terminal and run a selected track in another. The matched-input HTTP/direct parity evidence and exact criteria are recorded in `RUN_GUIDE.md` and `submission_audit/http_direct_parity_audit.csv`.

## Reproduce A-list Predictions

Run the selected Track A or B command with the organizer-specified 2025 dates. The runner writes result JSON and decision traces inside this package. Export daily trade/allocation rows only in the organizer-required format after confirming the current official submission contract. The starter-kit README requests code, daily 2025 logs, raw decision outputs, and final results; it does not specify one canonical A-list filename in the local materials.

## Expected Outputs

```text
runtime_logs/<track>_phase12_final/*.jsonl
agent_platform/demo_outputs/<track>_phase12_final_<session>.json
backtest_results_* / <organizer-configured result directory>
```

These are ignored by Git because they can contain participant-local session data. Keep only sanitized organizer-required files in the upload bundle.

## Validation Checklist

Run the commands in `SUBMISSION_CHECKLIST.md`. The current scope, model, dependency, compiler, test, parity, A-list, and log evidence is under `submission_audit/`.

## GitHub / Git LFS Notes

The FinBERT model weight exceeds GitHub's 100 MiB normal Git limit. Use Git LFS for 
`package/models/**`, `*.safetensors`, `*.bin`, and `*.pt`. Please install the FinBERT model 
through huggingface directly.


## Academic Use Disclaimer

This code is for the NLPCC shared task and reproducible research. It is not investment advice, an investment product, or a recommendation to trade any instrument.
