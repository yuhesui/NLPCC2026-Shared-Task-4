# Implementation Log: prompt08 - track2_sector_rotation_system

**Created:** 2026-05-28 17:59:26

## Summary

Implemented deterministic Track 2 sector rotation with strengthened sector-to-ETF mapping, Stage 2 sector impact panel and graph edges, Stage 3 correlation graph features, sector rotation and KG-MoE-Lite agents, configs, tests, and real 2024 Track 2 ablation outputs.

## Files Changed

src/nlpcc/stage1_news/models/entity_sector_mapper.py,src/nlpcc/stage1_news/models/sector_impact_extractor.py,src/nlpcc/stage2_text_store/schema.py,src/nlpcc/stage2_text_store/pipeline.py,src/nlpcc/stage2_text_store/registry.py,src/nlpcc/stage2_text_store/validators.py,src/nlpcc/stage2_text_store/__init__.py,src/nlpcc/stage2_text_store/models/sector_impact_panel.py,src/nlpcc/stage2_text_store/models/knowledge_graph.py,src/nlpcc/stage3_trade/models/correlation_graph.py,src/nlpcc/stage3_trade/schema.py,src/nlpcc/stage3_trade/pipeline.py,src/nlpcc/stage4_agent/models/sector_rotation_agent.py,src/nlpcc/stage4_agent/models/kg_moe_lite_agent.py,src/nlpcc/stage4_agent/registry.py,configs/stage2_text_store/sector_impact_panel.yaml,configs/stage2_text_store/sector_etf_graph.yaml,configs/stage4_agent/sector_rotation.yaml,configs/stage4_agent/kg_moe_lite.yaml,configs/systems/sector_rotation_track2.yaml,configs/systems/kg_moe_lite_track2.yaml,configs/tracks/track2_sector.yaml,tests/test_nlpcc/test_stage1_news/test_prompt08_sector_mapping.py,tests/test_nlpcc/test_stage2_text_store/test_prompt08_sector_store.py,tests/test_nlpcc/test_stage3_trade/test_prompt08_correlation_graph.py,tests/test_nlpcc/test_stage4_agent/test_prompt08_sector_agents.py,outputs/backtests/prompt08_train2024_s1_sector.json,outputs/backtests/prompt08_train2024_sector_rotation.json,outputs/backtests/prompt08_train2024_sector_rotation_trend_only.json,outputs/backtests/prompt08_train2024_sector_rotation_no_graph.json,outputs/backtests/prompt08_train2024_sector_rotation_equal_sector.json,outputs/backtests/prompt08_train2024_kg_moe_lite.json

## Tests / Checks

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -B -m pytest tests/test_nlpcc/test_stage1_news tests/test_nlpcc/test_stage2_text_store tests/test_nlpcc/test_stage3_trade tests/test_nlpcc/test_stage4_agent/test_prompt08_sector_agents.py -p no:cacheprovider; PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -B -m pytest tests/test_nlpcc/test_stage1_news tests/test_nlpcc/test_stage2_text_store tests/test_nlpcc/test_stage3_trade tests/test_nlpcc/test_portfolio tests/test_nlpcc/test_stage4_agent tests/test_tools/test_backtesting -p no:cacheprovider; real 2024 Track 2 local backtests for S1 sector, sector rotation, trend-only, no-graph, equal-sector, and KG-MoE-Lite

## Caveats

S1 sector remains the stronger Track 2 baseline on the first 2024 run; sector/news/graph variants are preserved as ablatable candidates rather than promoted. Local news loading uses bounded calendar-day lookback with 15:00 same-day cutoff; exact official trading-day pre_k parity should be checked against the official server.

## Artifacts

- `outputs/backtests/prompt08_train2024_s1_sector.json`
- `outputs/backtests/prompt08_train2024_sector_rotation.json`
- `outputs/backtests/prompt08_train2024_sector_rotation_trend_only.json`
- `outputs/backtests/prompt08_train2024_sector_rotation_no_graph.json`
- `outputs/backtests/prompt08_train2024_sector_rotation_equal_sector.json`
- `outputs/backtests/prompt08_train2024_kg_moe_lite.json`

## Next Steps

Tune Track 2 only via 2024 walk-forward, add promotion gates against S1 sector, and consider OCO blending over S1, equal-sector, sector rotation, and KG-MoE-Lite.
