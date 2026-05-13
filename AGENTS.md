# Repository Agent Instructions

This repository contains the official NLPCC 2026 Shared Task 4 starter kit and custom research code for LLM-based investment advisor agents.

## Read First

Before making non-trivial changes, read:

1. `README.md`
2. `NLPCC_tasks/README.md`
3. `docs/design/repo_architecture.md`
4. `docs/research/phase0-init.md`
5. the latest log under `docs/reports/implementation_logs/`

If strategy logic or data slicing is involved, also read:

1. `NLPCC_tasks/server_platform/app/core/data_loader.py`
2. `NLPCC_tasks/server_platform/app/core/backtest.py`
3. `NLPCC_tasks/server_platform/app/api/backtest.py`
4. `NLPCC_tasks/dataset/dataloader_eval.py`

## Repository Boundaries

- Treat `NLPCC_tasks/` as official starter-kit/vendor code.
- Do not mutate official starter-kit files unless the change is necessary, minimal, documented, and logged.
- Put custom implementation under `src/nlpcc4/`.
- Put durable configs under `configs/`.
- Keep scripts that are meant to be reused under `scripts/` or `tools/`.
- Keep temporary outputs under `.var/` or another ignored runtime directory.
- Treat `docs/research/phase0-init.md` as the canonical Phase 0 research source. Do not create a duplicate root-level `phase0-init.md`.

## Strategy Contract

All strategies must output target weights first:

```text
market data + news
-> strategy signal
-> target weights
-> constraint projection
-> turnover control
-> trade conversion
-> official trade API
```

Do not let strategy modules create final official trade payloads. Official API trade conversion belongs in `src/nlpcc4/execution/trade_converter.py`.

## Strategy Policy

- S1 is the first real strategy to implement.
- S2 and S3 may use LLMs only through structured bounded JSON signals.
- S4 is mainly a Track 2 overlay and should wait until S1-S3 infrastructure is stable.
- Do not build pure LLM allocation, multi-agent debate, early RAG, leaderboard-tuned prompt hacks, or direct LLM trade generation in early phases.

## Research and Evaluation Rules

- No future-data leakage.
- No public-leaderboard overfitting.
- Use configs instead of hardcoding strategy parameters.
- Baselines and ablations must run before LLM signal claims are accepted.
- Raw LLM outputs, caches, generated backtest artifacts, generated reports, and submission zips must not be committed.
- Never commit `.env`, API keys, secrets, raw LLM outputs, generated caches, generated backtest artifacts, or submission archives.

## Logging and Verification

- Update an implementation log after every non-trivial change.
- Use `tools/create_impl_log.py` for new implementation logs.
- Run tests or lightweight verification before declaring work ready.
- If verification is not run, explain why in the implementation log and final response.
