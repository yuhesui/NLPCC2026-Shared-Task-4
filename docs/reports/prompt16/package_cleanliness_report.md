# Prompt16 Package Cleanliness Report

Package dry-run was written to `.var/prompt16/packages/nlpcc_task4_candidate_prompt16_clean.zip`. Archive audit: 214 entries, no issues. Raw official data, datasets, outputs, `.var`, pycache, and model files were excluded.

| Package Item | Required? | Included? | Status | Notes |
|---|---|---|---|---|
| `NLPCC_tasks/agent_platform/agents/build_agent.py` | yes | yes | pass | Thin official wrapper included. |
| `src/nlpcc/` | yes | yes | pass | Runtime implementation included. |
| `src/tools/` | optional | no | pass | Research helpers are not required for B-list runtime package by default. |
| `configs/` | yes | yes | pass | Includes Prompt16 optimisation configs because package helper includes all configs. |
| requirements files | yes | yes | pass | `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`. |
| README / submission notes | yes | yes | pass | Package helper generated `README_SUBMISSION.md`. |
| raw official data | no | no | pass | `data/` and `NLPCC_tasks/dataset/` excluded. |
| `outputs/` | no | no | pass | Excluded. |
| `.var/` | no | no | pass | Excluded. |
| HF model files | no | no | pass | `models/` and cache paths excluded. |
| `__pycache__` / `.pyc` | no | no | pass | Archive audit found none. |

If the accelerated backtester or optimiser must ship for a research artifact, update the package include list deliberately; do not include `src/tools/` silently in the competition runtime package.
