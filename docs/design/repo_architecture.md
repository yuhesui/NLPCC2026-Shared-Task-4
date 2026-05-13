# NLPCC 2026 Shared Task 4 — Repository Architecture Reference

## Phase-0 Canonical Init Scope

This repository is initialized for clean S0-S4 development while preserving the official starter kit under `NLPCC_tasks/`.

Active implementation scope:

- `NLPCC_tasks/` remains official starter-kit/vendor code.
- custom code lives under `src/nlpcc4/`.
- strategy modules output target weights, not final official API trade payloads.
- `src/nlpcc4/execution/trade_converter.py` owns target-weight-to-trade conversion.
- durable configs live under `configs/track1/` and `configs/track2/`.
- implementation logs live under `docs/reports/implementation_logs/`.
- local runtime artifacts live under ignored directories such as `.var/`, `outputs/`, `logs/`, `cache/`, `artifacts/`, and `references_tmp/`.

Only S0-S4 are active early-phase strategy systems. Any older notes about supervised ETF rankers, ensemble submission layers, heavy RAG, multi-agent debate, pure LLM allocation, or direct LLM trade generation are deferred and must not be implemented during the initialization or first strategy-coding phases.

## 1. Purpose

This document defines the recommended repository structure for developing strategies for **NLPCC 2026 Shared Task 4: LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market**.

The architecture is designed for implementing and comparing:

- **S1 — Robust Quant Core Allocator**
- **S2 — Structured LLM Regime-to-Rules Allocator**
- **S3 — Risk-Budgeted LLM Alpha-Tilt Optimizer**
- **S4 — Event-to-Exposure Sector Mapper**

The structure must satisfy the following objectives:

1. Keep the official starter kit intact and easy to compare against.
2. Separate Track 1 and Track 2 strategy logic cleanly.
3. Keep reusable quant, execution, risk, and metric code shared.
4. Prevent temporary data, logs, caches, raw LLM outputs, and one-time scripts from being pushed.
5. Store implementation reports generated after every run.
6. Preserve cleaned reports and final submission documentation in committed locations.
7. Support reproducible backtests, ablations, and final submission packaging.
8. Reduce future-data leakage and public-leaderboard overfitting risk.

---

## 2. Design Principles

### 2.1 Official Starter Kit Is Treated as Vendor Code

The official starter kit should remain under:

```text
NLPCC_tasks/
````

This directory should be treated as an official reference implementation containing the competition server, data loader, dataset, API client, demo agent, and starter instructions.

Avoid modifying official files unless necessary. If modifications are required, keep them minimal and document them in:

```text
docs/reports/implementation_logs/
```

Recommended rule:

```text
Do not place custom research code inside NLPCC_tasks/ unless it is required for official API compatibility.
```

---

### 2.2 All Custom Implementation Lives Under `src/nlpcc4/`

Custom implementation code should live under:

```text
src/nlpcc4/
```

This makes the boundary between official starter-kit code and custom participant code explicit.

---

### 2.3 Strategy Output Should Be Target Weights

All strategies should produce target portfolio weights, not direct API trade payloads.

The recommended pipeline is:

```text
market data + news
        ↓
strategy signal
        ↓
target weights
        ↓
constraint projection
        ↓
turnover control
        ↓
trade conversion
        ↓
official trade API
```

This prevents strategy logic from being mixed with execution mechanics.

---

### 2.4 Temporary Artifacts Must Stay Out of Git

All generated run outputs, raw logs, LLM caches, raw LLM responses, temporary scripts, temporary references, and one-time experiments must be placed under ignored directories such as:

```text
.var/
outputs/
artifacts/
logs/
cache/
references_tmp/
```

Only cleaned and selected results should be copied into committed documentation directories.

---

### 2.5 Track 1 and Track 2 Are Separate Strategy Domains

Track 1 and Track 2 should share infrastructure but not domain-specific mapping logic.

Track 1 focuses on macro-asset allocation.

Track 2 focuses on sector-rotation allocation.

Therefore:

```text
src/nlpcc4/strategies/track1_macro/
src/nlpcc4/strategies/track2_sector/
```

should be separate.

---

## 3. Full Recommended Repository Structure

```text
NLPCC2026-Shared-Task-4/
├── README.md
├── README-CN.md
├── .gitignore
├── .env.example
├── requirements.txt
├── pyproject.toml
├── Makefile
│
├── NLPCC_tasks/
│   ├── agent_platform/
│   │   ├── agents/
│   │   ├── client/
│   │   └── demo_backtest.py
│   │
│   ├── dataset/
│   │   ├── README.md
│   │   ├── dataloader_eval.py
│   │   └── ...
│   │
│   ├── server_platform/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   └── main.py
│   │   └── ...
│   │
│   ├── config.py
│   ├── logs.py
│   ├── README.md
│   ├── README-CN.md
│   ├── requirements.txt
│   └── start_server.py
│
├── src/
│   └── nlpcc4/
│       ├── __init__.py
│       │
│       ├── common/
│       │   ├── __init__.py
│       │   ├── constants.py
│       │   ├── types.py
│       │   ├── dates.py
│       │   ├── io.py
│       │   ├── logging.py
│       │   ├── paths.py
│       │   ├── seed.py
│       │   └── hashing.py
│       │
│       ├── data/
│       │   ├── __init__.py
│       │   ├── official_loader.py
│       │   ├── price_panel.py
│       │   ├── news_panel.py
│       │   ├── features.py
│       │   ├── validators.py
│       │   ├── splits.py
│       │   └── leakage_checks.py
│       │
│       ├── execution/
│       │   ├── __init__.py
│       │   ├── portfolio_state.py
│       │   ├── target_weights.py
│       │   ├── trade_converter.py
│       │   ├── constraints.py
│       │   ├── turnover.py
│       │   ├── cash_buffer.py
│       │   └── order_validator.py
│       │
│       ├── metrics/
│       │   ├── __init__.py
│       │   ├── performance.py
│       │   ├── sharpe.py
│       │   ├── drawdown.py
│       │   ├── turnover.py
│       │   ├── attribution.py
│       │   ├── cost_analysis.py
│       │   └── report_cards.py
│       │
│       ├── strategies/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   │
│       │   ├── shared/
│       │   │   ├── __init__.py
│       │   │   ├── equal_weight.py
│       │   │   ├── inverse_vol.py
│       │   │   ├── momentum.py
│       │   │   ├── mean_reversion.py
│       │   │   ├── risk_budget.py
│       │   │   ├── smoothing.py
│       │   │   ├── fallback.py
│       │   │   ├── score_to_weight.py
│       │   │   └── ensemble.py
│       │   │
│       │   ├── track1_macro/
│       │   │   ├── __init__.py
│       │   │   ├── universe.py
│       │   │   ├── regimes.py
│       │   │   ├── macro_blocks.py
│       │   │   ├── s1_quant_core.py
│       │   │   ├── s2_llm_regime.py
│       │   │   ├── s3_llm_alpha_tilt.py
│       │   │   ├── s4_event_exposure.py
│       │   │   └── config.yaml
│       │   │
│       │   └── track2_sector/
│       │       ├── __init__.py
│       │       ├── universe.py
│       │       ├── sector_groups.py
│       │       ├── event_taxonomy.py
│       │       ├── s1_quant_core.py
│       │       ├── s2_llm_regime.py
│       │       ├── s3_llm_alpha_tilt.py
│       │       ├── s4_event_exposure.py
│       │       └── config.yaml
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── schemas.py
│       │   ├── parsers.py
│       │   ├── validators.py
│       │   ├── cache.py
│       │   ├── prompt_runner.py
│       │   └── prompts/
│       │       ├── regime_classifier.md
│       │       ├── alpha_score.md
│       │       ├── event_exposure.md
│       │       ├── news_summary.md
│       │       └── prompt_style.md
│       │
│       ├── backtest/
│       │   ├── __init__.py
│       │   ├── runner.py
│       │   ├── batch_runner.py
│       │   ├── session_manager.py
│       │   ├── official_client.py
│       │   ├── result_parser.py
│       │   ├── run_registry.py
│       │   └── replay.py
│       │
│       ├── experiments/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   ├── configs.py
│       │   ├── grid.py
│       │   ├── compare.py
│       │   ├── ablations.py
│       │   ├── promotion.py
│       │   └── robustness.py
│       │
│       ├── reports/
│       │   ├── __init__.py
│       │   ├── implementation_report.py
│       │   ├── markdown.py
│       │   ├── tables.py
│       │   ├── figures.py
│       │   └── templates/
│       │       ├── implementation_report.md.j2
│       │       ├── ablation_report.md.j2
│       │       └── final_report.md.j2
│       │
│       └── submission/
│           ├── __init__.py
│           ├── run_agent.py
│           ├── package_submission.py
│           ├── check_reproducibility.py
│           ├── manifest.py
│           └── Dockerfile.template
│
├── configs/
│   ├── base.yaml
│   ├── paths.yaml
│   ├── logging.yaml
│   ├── backtest_2024_train.yaml
│   ├── backtest_2025_phase_a.yaml
│   │
│   ├── track1/
│   │   ├── s0_baselines.yaml
│   │   ├── s1_quant_core.yaml
│   │   ├── s2_llm_regime.yaml
│   │   ├── s3_llm_alpha_tilt.yaml
│   │   └── s4_event_exposure.yaml
│   │
│   └── track2/
│       ├── s0_baselines.yaml
│       ├── s1_quant_core.yaml
│       ├── s2_llm_regime.yaml
│       ├── s3_llm_alpha_tilt.yaml
│       └── s4_event_exposure.yaml
│
├── scripts/
│   ├── run_server.ps1
│   ├── run_server.sh
│   ├── run_backtest.py
│   ├── run_batch.py
│   ├── run_strategy.py
│   ├── run_ablation.py
│   ├── compare_runs.py
│   ├── make_report.py
│   ├── validate_no_leakage.py
│   └── package_submission.py
│
├── tests/
│   ├── test_data_no_leakage.py
│   ├── test_price_panel.py
│   ├── test_news_panel.py
│   ├── test_trade_converter.py
│   ├── test_constraints.py
│   ├── test_turnover.py
│   ├── test_metrics.py
│   ├── test_track1_universe.py
│   ├── test_track2_universe.py
│   ├── test_llm_schema.py
│   ├── test_report_generation.py
│   └── test_submission_package.py
│
├── docs/
│   ├── design/
│   │   ├── repo_architecture.md
│   │   ├── data_contract.md
│   │   ├── execution_contract.md
│   │   ├── strategy_s1_s4.md
│   │   ├── track1_vs_track2.md
│   │   ├── leakage_policy.md
│   │   ├── experiment_policy.md
│   │   └── submission_plan.md
│   │
│   ├── reports/
│   │   ├── implementation_logs/
│   │   │   ├── README.md
│   │   │   └── .gitkeep
│   │   │
│   │   ├── ablations/
│   │   │   ├── README.md
│   │   │   └── .gitkeep
│   │   │
│   │   ├── phase_a/
│   │   │   ├── README.md
│   │   │   └── .gitkeep
│   │   │
│   │   └── final_submission/
│   │       ├── README.md
│   │       └── .gitkeep
│   │
│   ├── references/
│   │   ├── README.md
│   │   ├── official_task_notes.md
│   │   ├── starter_kit_api_notes.md
│   │   ├── evaluation_rules_summary.md
│   │   └── leakage_rules_summary.md
│   │
│   ├── examples/
│   │   ├── example_llm_regime_output.json
│   │   ├── example_alpha_score_output.json
│   │   └── example_event_exposure_output.json
│   │
│   └── figures/
│       └── .gitkeep
│
├── notebooks/
│   ├── README.md
│   ├── 00_data_inspection.ipynb
│   ├── 01_baselines.ipynb
│   └── 02_llm_signal_diagnostics.ipynb
│
├── references_tmp/
│   ├── papers/
│   ├── screenshots/
│   ├── copied_repo_notes/
│   ├── official_pages/
│   ├── web_clips/
│   └── misc/
│
├── outputs/
├── artifacts/
├── logs/
├── cache/
├── tmp/
│
└── .var/
    ├── README.md
    ├── tmp/
    ├── scratch/
    │   ├── one_off_py/
    │   ├── notebooks/
    │   └── dumps/
    │
    ├── runs/
    │   └── <run_id>/
    │       ├── config_used.yaml
    │       ├── implementation_report.md
    │       ├── metrics.json
    │       ├── daily_portfolio.csv
    │       ├── daily_holdings.csv
    │       ├── daily_trades.csv
    │       ├── turnover.csv
    │       ├── drawdown.csv
    │       ├── raw_stdout.log
    │       ├── raw_stderr.log
    │       ├── diagnostics/
    │       ├── references/
    │       └── raw_llm_outputs/
    │
    ├── implementation_reports/
    ├── llm_cache/
    ├── raw_llm_outputs/
    ├── official_runs/
    ├── batch_runs/
    ├── submissions/
    └── reference_tmp/
```

---

## 4. Directory Responsibilities

### 4.1 `NLPCC_tasks/`

Official starter-kit directory.

Expected contents:

```text
NLPCC_tasks/
├── agent_platform/
├── dataset/
├── server_platform/
├── config.py
├── logs.py
├── requirements.txt
└── start_server.py
```

Use this directory as the source of truth for:

* official server behavior,
* official dataset access,
* official DataLoader behavior,
* official API interface,
* official demo agent behavior,
* starter-kit documentation.

Do not place custom strategy modules here unless required for compatibility.

---

### 4.2 `src/nlpcc4/common/`

Shared low-level utilities.

Recommended contents:

| File           | Purpose                                                                  |
| -------------- | ------------------------------------------------------------------------ |
| `constants.py` | Global constants such as default capital, default friction, track names. |
| `types.py`     | Dataclasses and type aliases.                                            |
| `dates.py`     | Trading-date helpers and date parsing.                                   |
| `io.py`        | Safe JSON/YAML/CSV reading and writing.                                  |
| `logging.py`   | Project logging configuration.                                           |
| `paths.py`     | Central path resolver.                                                   |
| `seed.py`      | Reproducibility seed control.                                            |
| `hashing.py`   | Config/run hashing.                                                      |

---

### 4.3 `src/nlpcc4/data/`

Leakage-safe data access layer.

Recommended contents:

| File                 | Purpose                                                      |
| -------------------- | ------------------------------------------------------------ |
| `official_loader.py` | Wrapper around official DataLoader/API.                      |
| `price_panel.py`     | Converts official price API outputs into clean panel format. |
| `news_panel.py`      | Converts daily news API outputs into structured records.     |
| `features.py`        | Computes legal historical features.                          |
| `validators.py`      | Schema and missing-data validation.                          |
| `splits.py`          | 2024 train / 2025 Phase A / validation split definitions.    |
| `leakage_checks.py`  | Explicit no-future-data tests.                               |

Rules:

1. Never compute features using unavailable same-day close/high/low/return.
2. Never use future labels inside live decision functions.
3. All strategy contexts should be built through this layer.
4. If any custom slicing is added, write a leakage test immediately.

---

### 4.4 `src/nlpcc4/execution/`

Portfolio and execution layer.

Recommended contents:

| File                 | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `portfolio_state.py` | Holdings, cash, portfolio value state.                    |
| `target_weights.py`  | Target weight normalization and validation.               |
| `trade_converter.py` | Converts target weights into official buy/sell actions.   |
| `constraints.py`     | Weight caps, cash constraints, concentration constraints. |
| `turnover.py`        | Turnover calculation and turnover caps.                   |
| `cash_buffer.py`     | Cash buffer handling.                                     |
| `order_validator.py` | Final validation before sending API trades.               |

Design rule:

```text
Strategies return target weights.
Only execution/trade_converter.py creates official trade actions.
```

---

### 4.5 `src/nlpcc4/metrics/`

Metric and diagnostic layer.

Recommended contents:

| File               | Purpose                                           |
| ------------------ | ------------------------------------------------- |
| `performance.py`   | Cumulative return, daily return, portfolio value. |
| `sharpe.py`        | Sharpe calculation.                               |
| `drawdown.py`      | Max drawdown and drawdown series.                 |
| `turnover.py`      | Daily and cumulative turnover.                    |
| `attribution.py`   | Asset-level contribution.                         |
| `cost_analysis.py` | Cost drag and friction stress test.               |
| `report_cards.py`  | Unified strategy summary tables.                  |

All strategies must be compared through the same metric code.

---

### 4.6 `src/nlpcc4/strategies/`

Strategy layer.

#### 4.6.1 `base.py`

All strategies should inherit from a common interface.

Recommended interface:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class StrategyDecision:
    target_weights: dict[str, float]
    diagnostics: dict[str, Any]


class BaseStrategy(ABC):
    name: str
    track: str

    @abstractmethod
    def decide(self, context: dict[str, Any]) -> StrategyDecision:
        """
        Return target weights and diagnostics using only leakage-safe context.
        """
        raise NotImplementedError
```

All strategy outputs must include:

```text
target_weights
diagnostics
```

Recommended diagnostics:

```text
signal_scores
volatility_estimates
momentum_scores
llm_scores
llm_confidence
regime_label
raw_target_weights
post_constraint_weights
turnover_estimate
fallback_triggered
```

---

## 5. Strategy Module Layout

### 5.1 Shared Strategy Components

```text
src/nlpcc4/strategies/shared/
├── equal_weight.py
├── inverse_vol.py
├── momentum.py
├── mean_reversion.py
├── risk_budget.py
├── smoothing.py
├── fallback.py
├── score_to_weight.py
└── ensemble.py
```

These should be track-agnostic.

Examples:

| Module               | Purpose                                        |
| -------------------- | ---------------------------------------------- |
| `equal_weight.py`    | Equal-weight baseline.                         |
| `inverse_vol.py`     | Inverse-volatility allocation.                 |
| `momentum.py`        | Multi-horizon momentum scores.                 |
| `risk_budget.py`     | Volatility-adjusted risk budget allocation.    |
| `smoothing.py`       | Target-weight smoothing.                       |
| `fallback.py`        | Baseline fallback and no-trade logic.          |
| `score_to_weight.py` | Softmax, rank-weight, top-k conversion.        |
| `ensemble.py`        | Conservative blending of candidate strategies. |

---

### 5.2 Track 1 Strategy Directory

```text
src/nlpcc4/strategies/track1_macro/
├── universe.py
├── regimes.py
├── macro_blocks.py
├── s1_quant_core.py
├── s2_llm_regime.py
├── s3_llm_alpha_tilt.py
├── s4_event_exposure.py
└── config.yaml
```

#### `universe.py`

Defines Track 1 asset universe.

Example:

```python
TRACK1_MACRO_UNIVERSE = {
    "000300.SH": "CSI 300",
    "000905.SH": "CSI 500",
    "399006.SZ": "ChiNext Index",
    "000688.SH": "STAR 50",
    "000932.SH": "CSI Consumer",
    "000941.SH": "New Energy Index",
    "399971.SZ": "CSI Media",
    "000819.SH": "Nonferrous Metals Index",
    "000928.SH": "CSI Energy Index",
    "000012.SH": "Treasury Bond Index",
    "518880.SH": "Gold ETF",
}

DEFENSIVE_ASSETS = {"000012.SH", "518880.SH"}
RISK_ASSETS = set(TRACK1_MACRO_UNIVERSE) - DEFENSIVE_ASSETS
```

#### Strategy meanings for Track 1

| Strategy | Track 1 Meaning                                                                       |
| -------- | ------------------------------------------------------------------------------------- |
| S1       | Quant macro allocator using inverse volatility, momentum, breadth, gold/bond defense. |
| S2       | LLM regime classifier mapping news into macro regimes.                                |
| S3       | LLM alpha scores tilt S1 base weights within risk budget.                             |
| S4       | Macro event-to-asset exposure mapping.                                                |

---

### 5.3 Track 2 Strategy Directory

```text
src/nlpcc4/strategies/track2_sector/
├── universe.py
├── sector_groups.py
├── event_taxonomy.py
├── s1_quant_core.py
├── s2_llm_regime.py
├── s3_llm_alpha_tilt.py
├── s4_event_exposure.py
└── config.yaml
```

#### `universe.py`

Defines Track 2 sector ETF universe.

Example:

```python
TRACK2_SECTOR_UNIVERSE = {
    "512880.SH": "Securities ETF",
    "512800.SH": "Banking ETF",
    "512070.SH": "Insurance ETF",
    "159995.SZ": "Semiconductor ETF",
    "159819.SZ": "AI ETF",
    "515880.SH": "Communication Equipment ETF",
    "159852.SZ": "Software ETF",
    "512010.SH": "Pharma ETF",
    "512170.SH": "Healthcare ETF",
    "159992.SZ": "Innovative Drug ETF",
    "515170.SH": "Food & Beverage ETF",
    "512690.SH": "Liquor ETF",
    "512400.SH": "Nonferrous Metals ETF",
    "515220.SH": "Coal ETF",
    "159870.SZ": "Chemicals ETF",
    "512200.SH": "Real Estate ETF",
}
```

#### Strategy meanings for Track 2

| Strategy | Track 2 Meaning                                               |
| -------- | ------------------------------------------------------------- |
| S1       | Sector trend-following with inverse-volatility risk scaling.  |
| S2       | LLM sector-regime classifier.                                 |
| S3       | LLM sector alpha scores tilt sector trend-following baseline. |
| S4       | Event-to-sector ETF exposure matrix.                          |

---

## 6. Strategy Architecture: S1–S4

## 6.1 S1 — Robust Quant Core Allocator

### Purpose

Create the strongest non-LLM strategy and backup submission.

### Inputs

* Historical ETF returns.
* Rolling volatility.
* Multi-horizon momentum.
* Drawdown.
* Previous portfolio weights.
* Current holdings and cash.
* Track-specific ETF universe.
* Risk and turnover constraints.

### Processing

```text
historical prices
    ↓
returns / volatility / momentum
    ↓
inverse-volatility base allocation
    ↓
momentum tilt
    ↓
defensive or sector-breadth adjustment
    ↓
weight smoothing
    ↓
constraint projection
    ↓
target weights
```

### LLM Role

None.

### Quant Role

Primary.

### Recommended File Locations

```text
src/nlpcc4/strategies/track1_macro/s1_quant_core.py
src/nlpcc4/strategies/track2_sector/s1_quant_core.py
src/nlpcc4/strategies/shared/inverse_vol.py
src/nlpcc4/strategies/shared/momentum.py
src/nlpcc4/strategies/shared/risk_budget.py
src/nlpcc4/strategies/shared/smoothing.py
```

---

## 6.2 S2 — Structured LLM Regime-to-Rules Allocator

### Purpose

Use the LLM only for bounded regime classification.

### Inputs

* Daily Top-20 news.
* Recent historical returns.
* Momentum breadth.
* Volatility state.
* Previous weights.
* Regime taxonomy.
* Risk limits.

### Processing

```text
daily news
    ↓
LLM regime classifier
    ↓
validated JSON regime output
    ↓
deterministic regime-to-weight rule table
    ↓
blend with S1 baseline
    ↓
turnover cap
    ↓
target weights
```

### LLM Role

* Regime classification.
* Confidence scoring.
* Optional short structured explanation.

### LLM Must Not Do

* Direct final allocation.
* Direct buy/sell trade generation.
* Free-form discretionary position sizing.

### Recommended File Locations

```text
src/nlpcc4/strategies/track1_macro/s2_llm_regime.py
src/nlpcc4/strategies/track2_sector/s2_llm_regime.py
src/nlpcc4/llm/prompts/regime_classifier.md
src/nlpcc4/llm/schemas.py
src/nlpcc4/llm/parsers.py
src/nlpcc4/llm/validators.py
```

---

## 6.3 S3 — Risk-Budgeted LLM Alpha-Tilt Optimizer

### Purpose

Use S1 as the robust base and apply bounded LLM-driven alpha tilts.

### Inputs

* S1 baseline weights.
* Historical ETF features.
* Daily news.
* LLM ETF/block alpha scores.
* LLM confidence.
* Rolling volatility.
* Turnover and concentration limits.

### Processing

```text
S1 base weights
    +
LLM alpha score vector
    +
volatility estimates
    ↓
confidence-shrunk alpha scores
    ↓
risk-budgeted score-to-weight conversion
    ↓
convex blend with S1
    ↓
constraint projection
    ↓
turnover cap
    ↓
target weights
```

### Core Formula

```text
final_weight = projection(
    (1 - lambda) * S1_weight
    + lambda * LLM_tilt_weight
)
```

### LLM Role

* Structured ETF/block scoring.
* Confidence estimation.
* No direct final trade authority.

### Recommended File Locations

```text
src/nlpcc4/strategies/track1_macro/s3_llm_alpha_tilt.py
src/nlpcc4/strategies/track2_sector/s3_llm_alpha_tilt.py
src/nlpcc4/llm/prompts/alpha_score.md
src/nlpcc4/strategies/shared/score_to_weight.py
src/nlpcc4/strategies/shared/risk_budget.py
```

---

## 6.4 S4 — Event-to-Exposure Sector Mapper

### Purpose

Extract structured news events and map them to asset or sector ETF exposures.

### Inputs

* Daily news.
* Event taxonomy.
* Track-specific exposure matrix.
* Historical returns.
* Rolling volatility.
* Previous weights.

### Processing

```text
daily news
    ↓
LLM event extraction
    ↓
event tuples:
    category, affected sector, direction, confidence, horizon
    ↓
event-to-ETF exposure matrix
    ↓
event score aggregation and decay
    ↓
combine with trend signal
    ↓
top-k or risk-budget allocation
    ↓
target weights
```

### LLM Role

* Event extraction.
* Event classification.
* Direction and confidence tagging.

### Quant Role

* Exposure matrix.
* Event score decay.
* Trend confirmation.
* Risk budgeting.
* Turnover control.

### Recommended File Locations

```text
src/nlpcc4/strategies/track1_macro/s4_event_exposure.py
src/nlpcc4/strategies/track2_sector/s4_event_exposure.py
src/nlpcc4/strategies/track2_sector/event_taxonomy.py
src/nlpcc4/llm/prompts/event_exposure.md
```

---

## 7. LLM Layer

### 7.1 Directory

```text
src/nlpcc4/llm/
├── client.py
├── schemas.py
├── parsers.py
├── validators.py
├── cache.py
├── prompt_runner.py
└── prompts/
    ├── regime_classifier.md
    ├── alpha_score.md
    ├── event_exposure.md
    ├── news_summary.md
    └── prompt_style.md
```

### 7.2 LLM Design Rules

1. LLM outputs must be structured JSON.
2. All outputs must pass schema validation.
3. Invalid outputs must trigger fallback logic.
4. Raw LLM outputs must be stored under `.var/`, not committed.
5. Parsed compact features may be cached locally but not pushed.
6. Prompt versions should be recorded in run-level reports.
7. No direct LLM-generated portfolio weights in final systems unless explicitly used as an ablation.

---

## 8. Configuration Structure

### 8.1 Directory

```text
configs/
├── base.yaml
├── paths.yaml
├── logging.yaml
├── backtest_2024_train.yaml
├── backtest_2025_phase_a.yaml
├── track1/
│   ├── s0_baselines.yaml
│   ├── s1_quant_core.yaml
│   ├── s2_llm_regime.yaml
│   ├── s3_llm_alpha_tilt.yaml
│   └── s4_event_exposure.yaml
└── track2/
    ├── s0_baselines.yaml
    ├── s1_quant_core.yaml
    ├── s2_llm_regime.yaml
    ├── s3_llm_alpha_tilt.yaml
    └── s4_event_exposure.yaml
```

### 8.2 Example S1 Config

```yaml
strategy:
  name: s1_quant_core
  track: track1

data:
  start_date: "2024-01-02"
  end_date: "2024-12-31"
  lookback_days: 60

signals:
  momentum_windows: [5, 20, 60]
  volatility_window: 20
  use_inverse_vol: true

portfolio:
  max_single_weight: 0.30
  max_daily_turnover: 0.20
  no_trade_band: 0.02
  cash_buffer: 0.01
  smoothing_rho: 0.30

risk:
  weak_breadth_threshold: 0.40
  defensive_weight_when_weak: 0.40
```

### 8.3 Example S3 Config

```yaml
strategy:
  name: s3_llm_alpha_tilt
  track: track1

base_strategy:
  name: s1_quant_core
  config_path: configs/track1/s1_quant_core.yaml

llm:
  enabled: true
  prompt_path: src/nlpcc4/llm/prompts/alpha_score.md
  temperature: 0.0
  max_retries: 2
  confidence_threshold: 0.55

alpha_tilt:
  lambda_tilt: 0.20
  max_weight_deviation_from_base: 0.15
  score_clip: [-1.0, 1.0]

portfolio:
  max_single_weight: 0.30
  max_daily_turnover: 0.20
  no_trade_band: 0.02
  smoothing_rho: 0.25

fallback:
  fallback_strategy: s1_quant_core
  trigger_on_invalid_llm_json: true
  trigger_on_low_confidence: true
```

---

## 9. Temporary and Generated Files Policy

## 9.1 `.var/`

`.var/` is the main local runtime directory.

It is ignored by Git.

Recommended structure:

```text
.var/
├── README.md
├── tmp/
├── scratch/
│   ├── one_off_py/
│   ├── notebooks/
│   └── dumps/
│
├── runs/
│   └── <run_id>/
│       ├── config_used.yaml
│       ├── implementation_report.md
│       ├── metrics.json
│       ├── daily_portfolio.csv
│       ├── daily_holdings.csv
│       ├── daily_trades.csv
│       ├── turnover.csv
│       ├── drawdown.csv
│       ├── raw_stdout.log
│       ├── raw_stderr.log
│       ├── diagnostics/
│       ├── references/
│       └── raw_llm_outputs/
│
├── implementation_reports/
├── llm_cache/
├── raw_llm_outputs/
├── official_runs/
├── batch_runs/
├── submissions/
└── reference_tmp/
```

---

## 9.2 `.var/tmp/`

Use for temporary intermediate files.

Examples:

```text
.var/tmp/tmp_prices_head.csv
.var/tmp/tmp_news_sample.json
.var/tmp/tmp_api_response.json
```

These files should be disposable.

---

## 9.3 `.var/scratch/one_off_py/`

Use for one-time Python scripts.

Examples:

```text
.var/scratch/one_off_py/inspect_raw_dataset_once.py
.var/scratch/one_off_py/debug_api_trade_payload.py
.var/scratch/one_off_py/quick_check_turnover_bug.py
.var/scratch/one_off_py/tmp_plot_sector_corr.py
```

Rule:

```text
If a one-time script is used more than twice, promote it to scripts/ or src/nlpcc4/experiments/.
```

---

## 9.4 `.var/runs/<run_id>/`

Every official or internal run gets one folder.

Required files:

```text
.var/runs/<run_id>/
├── config_used.yaml
├── implementation_report.md
├── metrics.json
├── daily_portfolio.csv
├── daily_holdings.csv
├── daily_trades.csv
├── turnover.csv
├── drawdown.csv
├── raw_stdout.log
├── raw_stderr.log
└── diagnostics/
```

Optional files:

```text
.var/runs/<run_id>/
├── raw_llm_outputs/
├── references/
├── figures/
├── ablations/
└── replay/
```

---

## 9.5 `.var/implementation_reports/`

Stores a flat chronological archive of auto-generated implementation reports.

Example:

```text
.var/implementation_reports/
├── 20260513_1530_t1_s1_quant_core.md
├── 20260514_0115_t1_s2_llm_regime.md
├── 20260516_2300_t1_s3_alpha_tilt.md
└── 20260518_2040_t2_s4_event_exposure.md
```

These are not committed.

Important reports should be manually cleaned and copied to:

```text
docs/reports/implementation_logs/
```

---

## 9.6 `references_tmp/`

Use for temporary reference material.

Examples:

```text
references_tmp/
├── papers/
├── screenshots/
├── copied_repo_notes/
├── official_pages/
├── web_clips/
└── misc/
```

Examples of files:

```text
references_tmp/screenshots/task_page_20260513.png
references_tmp/official_pages/nlpcc_schedule_copy.md
references_tmp/copied_repo_notes/data_loader_notes.md
references_tmp/papers/news_driven_asset_allocation_tmp.pdf
```

These files are not committed.

---

## 9.7 `docs/references/`

Use for curated permanent reference notes.

Examples:

```text
docs/references/
├── official_task_notes.md
├── starter_kit_api_notes.md
├── evaluation_rules_summary.md
└── leakage_rules_summary.md
```

These files may be committed.

---

## 10. Implementation Report Policy

### 10.1 Auto-Generated Per-Run Report

Every run should automatically generate:

```text
.var/runs/<run_id>/implementation_report.md
```

The same report may also be copied to:

```text
.var/implementation_reports/<timestamp>_<track>_<strategy>.md
```

### 10.2 Cleaned Reports

Important reports should be manually reviewed, cleaned, and copied to:

```text
docs/reports/implementation_logs/
```

### 10.3 Recommended Report Template

Each implementation report should contain:

```markdown
# Implementation Report: <run_id>

## 1. Run Metadata

- Run ID:
- Timestamp:
- Git commit:
- Track:
- Strategy:
- Config path:
- Config hash:
- Start date:
- End date:
- Data source:
- Official server version:
- Random seed:

## 2. Strategy Summary

- Strategy family:
- Main signal:
- LLM used:
- Quant components:
- Turnover control:
- Risk control:
- Fallback logic:

## 3. Inputs Used

- Price fields:
- News fields:
- Historical lookback:
- Current-day fields used:
- Current-day fields explicitly not used:

## 4. Leakage Check

- Historical prices are previous-day only:
- Current-day close/high/low/return hidden:
- Same-day news cutoff respected:
- No future labels used:
- External data used:
- Notes:

## 5. Portfolio Construction

- Raw signal:
- Score normalization:
- Weight generation:
- Constraint projection:
- Turnover cap:
- Trade conversion:

## 6. Performance Summary

| Metric | Value |
|---|---:|
| Cumulative return | |
| Sharpe ratio | |
| Max drawdown | |
| Average daily turnover | |
| Total turnover | |
| Number of trading days | |
| Number of trades | |
| Cost drag | |

## 7. Benchmark Comparison

| Strategy | Sharpe | Return | Max DD | Turnover |
|---|---:|---:|---:|---:|
| Equal weight | | | | |
| Inverse vol | | | | |
| Momentum only | | | | |
| Persistence | | | | |
| Current run | | | | |

## 8. Diagnostics

- Top positive allocations:
- Top negative/zero allocations:
- Fallback count:
- LLM invalid-output count:
- Average LLM confidence:
- Turnover cap binding count:
- Constraint projection binding count:

## 9. Failure Modes Observed

-
-
-

## 10. Decision

- Keep / reject / rerun:
- Reason:
- Next action:
```

---

## 11. Run ID Convention

Use deterministic and readable run IDs.

Format:

```text
{track}_{strategy}_{yyyymmdd}_{hhmm}_{short_hash}
```

Examples:

```text
t1_s1_quant_core_20260513_1530_a13f92
t1_s2_llm_regime_20260514_0115_b7720d
t1_s3_alpha_tilt_20260516_2300_90ee1a
t2_s4_event_exposure_20260518_2040_8c71fb
```

Recommended contents:

```text
.var/runs/t1_s3_alpha_tilt_20260516_2300_90ee1a/
├── config_used.yaml
├── implementation_report.md
├── metrics.json
├── daily_portfolio.csv
├── daily_holdings.csv
├── daily_trades.csv
├── turnover.csv
├── drawdown.csv
├── raw_stdout.log
├── raw_stderr.log
├── diagnostics/
├── raw_llm_outputs/
└── references/
```

---

## 12. Baseline and Ablation Structure

### 12.1 Baselines

Baselines should be implemented under:

```text
src/nlpcc4/strategies/shared/
```

Required baselines:

| Baseline                      | Module                            |
| ----------------------------- | --------------------------------- |
| Equal weight                  | `equal_weight.py`                 |
| Inverse volatility            | `inverse_vol.py`                  |
| Momentum only                 | `momentum.py`                     |
| Persistence                   | `fallback.py` or `persistence.py` |
| Sector trend-following        | Track 2 `s1_quant_core.py`        |
| Random constrained allocation | `random_baseline.py` if needed    |

### 12.2 Ablation Reports

Generated ablation outputs:

```text
.var/runs/<run_id>/ablations/
```

Cleaned ablation summaries:

```text
docs/reports/ablations/
```

Required ablations:

```text
no_llm
llm_scores_only
quant_features_only
no_turnover_control
no_volatility_scaling
no_news_input
no_momentum_input
no_regime_classifier
baseline_fallback_only
public_tuned_vs_untuned
```

---

## 13. Commands

### 13.1 Start Official Server

Windows PowerShell:

```powershell
.\scripts\run_server.ps1
```

Unix shell:

```bash
bash scripts/run_server.sh
```

Or directly:

```bash
cd NLPCC_tasks
python start_server.py
```

---

### 13.2 Run One Strategy

```bash
python scripts/run_strategy.py \
  --track track1 \
  --strategy s1_quant_core \
  --config configs/track1/s1_quant_core.yaml \
  --start-date 2024-01-02 \
  --end-date 2024-12-31
```

---

### 13.3 Run S3 on Track 1 Phase A

```bash
python scripts/run_strategy.py \
  --track track1 \
  --strategy s3_llm_alpha_tilt \
  --config configs/track1/s3_llm_alpha_tilt.yaml \
  --start-date 2025-01-02 \
  --end-date 2025-12-31
```

---

### 13.4 Run S4 on Track 2

```bash
python scripts/run_strategy.py \
  --track track2 \
  --strategy s4_event_exposure \
  --config configs/track2/s4_event_exposure.yaml \
  --start-date 2025-01-02 \
  --end-date 2025-12-31
```

---

### 13.5 Compare Runs

```bash
python scripts/compare_runs.py \
  --run-dir .var/runs \
  --output .var/tmp/comparison_table.csv
```

---

### 13.6 Generate Clean Report

```bash
python scripts/make_report.py \
  --run-id t1_s3_alpha_tilt_20260516_2300_90ee1a \
  --output docs/reports/implementation_logs/20260516_S3_Alpha_Tilt.md
```

---

### 13.7 Package Submission

```bash
python scripts/package_submission.py \
  --strategy s3_llm_alpha_tilt \
  --track track1 \
  --config configs/track1/s3_llm_alpha_tilt.yaml \
  --output .var/submissions/t1_s3_submission.zip
```

---

## 14. `.gitignore`

Recommended `.gitignore`:

```gitignore
# =========================
# Environment / secrets
# =========================
.env
.env.*
!.env.example
*.key
*.pem
secrets/
credentials/
api_keys/

# =========================
# Python
# =========================
__pycache__/
*.py[cod]
*.pyo
*.pyd
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/

# =========================
# Virtual environments
# =========================
.venv/
venv/
env/
ENV/

# =========================
# Local runtime state
# =========================
.var/
outputs/
artifacts/
logs/
cache/
tmp/
temp/

# =========================
# Temporary references
# =========================
references_tmp/
docs/references_tmp/

# =========================
# One-time scripts / scratch work
# =========================
scratch/
.var/scratch/
*_tmp.py
tmp_*.py
debug_once_*.py
inspect_once_*.py

# =========================
# Backtest / experiment outputs
# =========================
runs/
sessions/
batch_runs/
official_runs/
submissions/
leaderboard_runs/
*.session
*.sqlite
*.db

# =========================
# Generated implementation reports
# =========================
.var/implementation_reports/
.var/runs/
.var/batch_runs/

# Keep curated reports
!docs/reports/
!docs/reports/**/*.md
!docs/reports/**/*.png
!docs/reports/**/*.csv

# =========================
# LLM outputs / cache
# =========================
.var/llm_cache/
.var/raw_llm_outputs/
raw_llm_outputs/
llm_cache/
prompt_cache/
*.jsonl
*.ndjson

# Allow curated examples if deliberately added
!docs/examples/*.json
!docs/examples/*.jsonl

# =========================
# Jupyter
# =========================
.ipynb_checkpoints/

# =========================
# OS / IDE
# =========================
.DS_Store
Thumbs.db
.idea/
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json

# =========================
# Local binary / large derived data
# =========================
*.parquet
*.feather
*.h5
*.pkl
*.pickle

# =========================
# Archives
# =========================
*.zip
*.tar
*.tar.gz
*.7z

# =========================
# Do not ignore official starter kit source
# =========================
!NLPCC_tasks/
!NLPCC_tasks/**/*.py
!NLPCC_tasks/**/*.md
!NLPCC_tasks/**/*.txt
!NLPCC_tasks/**/*.csv
```

---

## 15. Commit Policy

### Commit

```text
src/
configs/
scripts/
tests/
docs/design/
docs/reports/implementation_logs/     # only cleaned selected reports
docs/reports/ablations/               # only cleaned selected reports
docs/reports/final_submission/
docs/references/                      # curated references only
.env.example
requirements.txt
pyproject.toml
Makefile
```

### Do Not Commit

```text
.env
.var/
outputs/
artifacts/
logs/
cache/
tmp/
references_tmp/
raw_llm_outputs/
llm_cache/
one-time scripts
submission zip files
large derived datasets
unreviewed generated reports
```

---

## 16. Development Order

Recommended build sequence:

```text
Phase 0:
  repo structure
  .gitignore
  config loader
  path resolver
  official API wrapper

Phase 1:
  data validation
  leakage checks
  target-weight representation
  trade converter
  metrics

Phase 2:
  S0 baselines
  S1 Track 1
  S1 Track 2

Phase 3:
  S2 Track 1
  S2 Track 2 if useful

Phase 4:
  S3 Track 1
  S3 Track 2 if S2/S1 are stable

Phase 5:
  S4 Track 2
  S4 Track 1 only if macro event mapping is useful

Phase 6:
  ablations
  robustness checks
  final reporting
  submission package
```

---

## 17. Leakage Checklist

Every strategy run must pass:

```text
[ ] Historical price features use only previous trading days.
[ ] Current-day close, high, low, and return are not used before decision.
[ ] Same-day news respects timestamp cutoff.
[ ] No future labels are injected.
[ ] Feature matrices are generated chronologically.
[ ] Public 2025 is not used as training data for final hyperparameter search unless explicitly documented.
[ ] LLM prompt does not include future performance.
[ ] Cached LLM outputs are indexed by date and prompt version.
[ ] Backtest start/end dates are recorded.
[ ] Config hash is recorded.
```

---

## 18. Promotion Policy

A strategy may be promoted only if it satisfies:

```text
[ ] Beats equal weight.
[ ] Beats inverse-volatility or explains why not.
[ ] Beats or matches momentum-only after costs.
[ ] Does not materially increase turnover without Sharpe improvement.
[ ] Survives cost-stress testing.
[ ] Has valid trade logs.
[ ] Has implementation report.
[ ] Has no known leakage issue.
[ ] Has reproducible config.
```

S3 and S4 require additional checks:

```text
[ ] LLM invalid-output rate is low.
[ ] Prompt paraphrase does not change rankings materially.
[ ] No-LLM ablation is weaker than full model.
[ ] LLM-only ablation does not dominate suspiciously.
[ ] Fallback to S1 works.
```

---

## 19. Final Submission Policy

Preferred hierarchy:

```text
1. Submit S3 if it robustly beats S1 and passes ablations.
2. Submit S1 if LLM signals are weak or unstable.
3. Submit S2 only if regime classification improves drawdown or Sharpe without increasing turnover materially.
4. Submit S4 mainly for Track 2 if event mapping clearly beats sector trend-following.
```

Do not submit a strategy only because it has the best single public leaderboard run.

Use median robustness across validation windows and ablations.

---

## 20. Quick Reference

### Source Code

```text
src/nlpcc4/
```

### Strategy Code

```text
src/nlpcc4/strategies/track1_macro/
src/nlpcc4/strategies/track2_sector/
```

### Shared Quant Code

```text
src/nlpcc4/strategies/shared/
src/nlpcc4/execution/
src/nlpcc4/metrics/
```

### LLM Code

```text
src/nlpcc4/llm/
```

### Reproducible Configs

```text
configs/
```

### Reusable Scripts

```text
scripts/
```

### Tests

```text
tests/
```

### Clean Documentation

```text
docs/
```

### Generated Run Outputs

```text
.var/runs/
```

### Generated Implementation Reports

```text
.var/implementation_reports/
```

### Cleaned Implementation Reports

```text
docs/reports/implementation_logs/
```

### One-Time Python Scripts

```text
.var/scratch/one_off_py/
```

### Temporary Reference Files

```text
references_tmp/
.var/reference_tmp/
```

### Final Submission Packaging

```text
src/nlpcc4/submission/
scripts/package_submission.py
.var/submissions/
```

---

## 21. Minimal First Commit Checklist

Initial commit should include:

```text
.gitignore
.env.example
pyproject.toml
requirements.txt
Makefile

src/nlpcc4/__init__.py
src/nlpcc4/common/
src/nlpcc4/data/
src/nlpcc4/execution/
src/nlpcc4/metrics/
src/nlpcc4/strategies/base.py
src/nlpcc4/strategies/shared/
src/nlpcc4/strategies/track1_macro/universe.py
src/nlpcc4/strategies/track2_sector/universe.py
src/nlpcc4/reports/

configs/base.yaml
configs/paths.yaml
configs/track1/s1_quant_core.yaml
configs/track2/s1_quant_core.yaml

scripts/run_strategy.py
scripts/validate_no_leakage.py

tests/test_data_no_leakage.py
tests/test_trade_converter.py
tests/test_metrics.py

docs/design/repo_architecture.md
docs/design/data_contract.md
docs/design/execution_contract.md
docs/reports/implementation_logs/README.md
docs/references/README.md
```

Do not wait for all strategies to be complete before committing the architecture.

---

## 22. Core Rule

Use the following rule throughout the project:

```text
If it is needed to reproduce the final system, commit it.
If it is generated by a run, put it in .var/runs/.
If it is an auto-generated implementation report, put it in .var/implementation_reports/.
If it is a cleaned report worth preserving, copy it to docs/reports/implementation_logs/.
If it is a one-time debugging script, put it in .var/scratch/one_off_py/.
If it is a temporary reference file, put it in references_tmp/.
If it contains secrets, never commit it.
```
