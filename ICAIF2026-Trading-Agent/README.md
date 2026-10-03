# ICAIF2026-Trading-Agent

Research + production workspace for the **ACM ICAIF 2026 Trading Agent Competition**
([Codabench 99](https://hackathon2.deepintomlf.ai/competitions/99/);
[official kit](https://github.com/DeepIntoStreams/2026ICAIF_Trading_Agent_Competition)):
30 fixed US stocks, long-only, 0 ≤ wᵢ ≤ 0.30, Σw ≤ 1, seven rounds per trading day, 0.1% fee,
ranked on the mean rank of cumulative return, Sharpe, max drawdown and turnover.

The system is a point-in-time quantitative core (risk parity / momentum / turnover-penalised
optimiser with explicit gross exposure) to which public text can contribute only through a
**bounded, auditable overlay**. Competing designs are configs, so the central research question —
*does text add point-in-time, fee-adjusted value over the quant core at 7 rounds/day?* — can be
answered with controlled ablations.

Reusable ideas come from the AlphaAllocator NLPCC 2026 system; see
[`docs/migration/NLPCC_TO_ICAIF_AUDIT.md`](docs/migration/NLPCC_TO_ICAIF_AUDIT.md).

## Quick start

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'                       # core: numpy + pyyaml only
scripts/setup/fetch_official_kit.sh           # official kit at a pinned commit -> third_party/ (git-ignored)
ruff check src tests scripts && python -m pytest

# backtest a baseline on the SYNTHETIC world (plumbing only, not evidence)
python scripts/backtest/run_backtest.py configs/systems/q3_shrinkage_erc.yaml
# run the experiment matrix (registry in outputs/experiments, report in outputs/reports)
python scripts/experiments/run_matrix.py --families quant_baselines,text_ablations
# rehearse the live loop offline (simulated clock, local paper session)
python scripts/live/rehearse_paper.py
```

Live operation: [`docs/operations/LIVE_RUNBOOK.md`](docs/operations/LIVE_RUNBOOK.md).

## Layout

```
configs/      competition, data, features, news, embeddings, models, portfolio, risk, execution,
              systems (Q0-Q8, N1-N2), experiments (initial matrix)
src/icaif/    core · competition · data · features · nlp · llm · models · portfolio · runtime · backtest · experiments
scripts/      setup · data · train · backtest · experiments · validation · live
tests/        unit · integration · leakage · competition · nlp · portfolio · runtime
docs/         architecture · competition · data · research · experiments · migration · operations · reproducibility
data/, outputs/, third_party/   git-ignored contents (skeleton only)
```

## Documentation

| Topic | File |
|---|---|
| Architecture | [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md) |
| Rules, protocol, open questions | [docs/competition/ICAIF_RULES_AND_PROTOCOL.md](docs/competition/ICAIF_RULES_AND_PROTOCOL.md) |
| Baselines | [docs/research/BASELINE_PLAN.md](docs/research/BASELINE_PLAN.md) |
| Embedding models | [docs/research/EMBEDDING_MODEL_PLAN.md](docs/research/EMBEDDING_MODEL_PLAN.md) |
| Fine-tuning | [docs/research/FINETUNING_PLAN.md](docs/research/FINETUNING_PLAN.md) |
| News overlay | [docs/research/NEWS_OVERLAY_PLAN.md](docs/research/NEWS_OVERLAY_PLAN.md) |
| Experiment matrix | [docs/research/EXPERIMENT_MATRIX.md](docs/research/EXPERIMENT_MATRIX.md) |
| Data provenance | [docs/data/DATA_PROVENANCE.md](docs/data/DATA_PROVENANCE.md) |
| Reproduction | [docs/reproducibility/REPRODUCTION_CHECKLIST.md](docs/reproducibility/REPRODUCTION_CHECKLIST.md) |
| Current state | [docs/FINAL_REPO_AUDIT.md](docs/FINAL_REPO_AUDIT.md) |

## Status in one paragraph

Everything needed to backtest, ablate and run the quant baselines and the lexical text overlay works
offline and is tested (official-kit parity included). **No real market or news data is bundled**, so
no strategy has real-market evidence yet; transformer encoders are interfaces until local model files
are registered and their competition status is confirmed. See the audit for what is stubbed or blocked.

## Rules for contributors (humans and agents)

See [`AGENTS.md`](AGENTS.md): point-in-time discipline, no silent fallbacks, no downloads at runtime,
fees always on, deterministic experiment IDs, no new top-level clutter.
