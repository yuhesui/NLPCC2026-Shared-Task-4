# Implementation Log: prompt07 - robust_bl_risk_parity_engine

**Created:** 2026-05-28 17:47:57

## Summary

Implemented NumPy-backed portfolio construction, risk parity, robust Black-Litterman with Stage 1/2/3 integration, turnover control, S1 fallback, configs, tests, and real 2024 Track 1 backtest artifacts.

## Files Changed

src/nlpcc/portfolio/constraints.py,src/nlpcc/portfolio/target_weights.py,src/nlpcc/portfolio/risk_parity.py,src/nlpcc/portfolio/black_litterman.py,src/nlpcc/portfolio/robust_optimizer.py,src/nlpcc/portfolio/turnover_control.py,src/nlpcc/portfolio/position_sizing.py,src/nlpcc/portfolio/__init__.py,src/nlpcc/stage4_agent/models/risk_parity_agent.py,src/nlpcc/stage4_agent/models/robust_bl_agent.py,src/nlpcc/stage4_agent/registry.py,src/tools/backtesting/local_backtester.py,configs/stage4_agent/robust_bl.yaml,configs/stage4_agent/risk_parity.yaml,configs/systems/robust_bl_track1.yaml,configs/systems/risk_parity_track1.yaml,tests/test_nlpcc/test_portfolio/test_portfolio_prompt07.py,tests/test_nlpcc/test_stage4_agent/test_prompt07_agents.py,outputs/backtests/prompt07_train2024_s1_macro.json,outputs/backtests/prompt07_train2024_risk_parity_macro.json,outputs/backtests/prompt07_train2024_robust_bl_macro.json

## Tests / Checks

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -B -m pytest tests/test_nlpcc/test_portfolio tests/test_nlpcc/test_stage4_agent -p no:cacheprovider; PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -B -m pytest tests/test_nlpcc/test_stage1_news tests/test_nlpcc/test_stage2_text_store tests/test_nlpcc/test_stage3_trade tests/test_nlpcc/test_portfolio tests/test_nlpcc/test_stage4_agent tests/test_tools/test_backtesting -p no:cacheprovider; real 2024 Track 1 local backtests for S1, risk parity, robust BL under outputs/backtests/

## Caveats

Robust BL is a first deterministic allocator, not tuned; 2024 real-data run shows RP outperforming robust BL in this pass. Local news loader now uses bounded calendar-day lookback and same-day 15:00 cutoff, while exact official trading-day pre_k semantics should still be checked against the official server before promotion.

## Artifacts

- `outputs/backtests/prompt07_train2024_s1_macro.json`
- `outputs/backtests/prompt07_train2024_risk_parity_macro.json`
- `outputs/backtests/prompt07_train2024_robust_bl_macro.json`

## Next Steps

Add formal ablation runner for no-news/no-BL/no-turnover variants, compare with official-server execution, and tune BL confidence/view scaling only on 2024 walk-forward.
