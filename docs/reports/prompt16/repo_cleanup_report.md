# Prompt16 Repo Cleanup Report

No source, config, test, docs, official starter, or raw data files were deleted. `outputs/` is already partly tracked and contains prior prompt evidence, so Prompt16 did not remove it silently; new runtime outputs were redirected to `.var/prompt16/`.

| Path | Type | Action | Reason | Preserved Summary? | Notes |
|---|---|---|---|---|---|
| `outputs/` | generated/history | manual_review | Contains tracked Prompt04-Prompt15 evidence and package artifacts. | yes | 2058 visible files, about 64.8 MB visible; some pytest temp dirs denied enumeration. |
| `outputs/reports/prompt13` | prior evidence | keep | Mandatory Prompt16 context. | yes | Summarized in method/backtester/final reports. |
| `outputs/reports/prompt14` | prior evidence | keep | Contains latest S0/S1 parity evidence. | yes | Official server not rerun in Prompt16. |
| `outputs/reports/prompt15` | prior evidence | keep | Contains Prompt15 MVP grid and local-model integration evidence. | yes | Treated as bounded sample evidence only. |
| `.var/prompt16/benchmarks` | runtime temp | ignore_only | New bounded benchmark outputs belong outside tracked `outputs/`. | yes | Contains two small JSON benchmark files. |
| `.var/prompt16/smoke_results` | runtime temp | ignore_only | New optimisation smoke output belongs outside tracked `outputs/`. | yes | Contains `optimisation_smoke.json`. |
| `.var/prompt16/packages` | runtime temp | ignore_only | Clean package dry-run location. | yes | Archive audit reported no issues. |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.cache/` | cache | ignore_only | Generated local tool caches. | n/a | Added to `.gitignore`. |
| `__pycache__/`, `*.pyc` | cache | ignore_only | Python bytecode. | n/a | Already ignored and retained untouched. |
| `outputs/models/`, `models/huggingface/` | model cache | ignore_only | HF/model files must not enter the repo/package. | n/a | Added explicit ignore rules. |
| `tests/` | source tests | keep | Tests are source artifacts, not runtime outputs. | yes | Removed the broad `/tests/` ignore rule so new tests are visible. |

Cleanup manifest:

- Updated `.gitignore` for `.var/`, cache folders, pycache, `outputs/models/`, and `models/huggingface/`.
- Kept historical tracked `outputs/` evidence intact.
- Wrote all Prompt16 deliverables under `docs/reports/prompt16/`.
- Wrote new runtime artifacts only under `.var/prompt16/`.
