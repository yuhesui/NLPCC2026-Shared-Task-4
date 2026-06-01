# Prompt16 Method Implementation Audit

Focused smoke tests passed for Prompt15 top methods, local text extractors, SystemRunner, and Prompt16 helper additions. Official parity remains proven only for S0/S1 from Prompt14; advanced candidates are local-wrapper runnable but still need official-server parity.

| Method | Code Path | Config | Registry | Tests | Minimal Run | Wrapper Run | Future-Leakage Check | Maturity | Status | Fix Needed |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 equal weight | `src/nlpcc/stage4_agent/models/s0_equal_weight_agent.py` | `configs/systems/s0_equal_weight.yaml` | SystemRunner alias | pass | pass | Prompt14 official parity pass | current-day open only | production_candidate | pass | none |
| S1 quant core | `src/nlpcc/stage4_agent/models/s1_quant_core.py` | `s1_macro.yaml`, `s1_sector.yaml` | SystemRunner alias | pass | pass | Prompt14 macro/sector parity pass | current-day open only | production_candidate | pass | none |
| DRO-BL-RP | `dro_bl_rp_agent.py` | `dro_bl_rp_track1.yaml` | stage4 registry + runner | pass | pass | local wrapper pass | metadata reports no forbidden fields | functional_mvp | partial | official parity rerun |
| BSA-RP | `bsa_rp_agent.py` | `bsa_rp_track1.yaml` | stage4 registry + runner | pass | pass | local wrapper pass | metadata reports no forbidden fields | functional_mvp | partial | full-year evidence |
| ARMOR-OMD | `armor_omd_agent.py` | `armor_omd_macro.yaml`, `armor_omd_sector.yaml` | stage4 registry + runner | pass | pass | local wrapper pass | metadata reports no forbidden fields | functional_mvp | partial | label as OMD proxy |
| LEEQA-Rank | `leeqa_rank_agent.py` | `leeqa_rank_track2.yaml` | stage4 registry + runner | pass | pass | local wrapper path exists | deterministic ranker | functional_mvp | partial | full Track B evidence |
| KG-MoE-Lite | `kg_moe_lite_agent.py` | `kg_moe_lite_track2.yaml` | stage4 registry + runner | pass | pass | local wrapper path exists | deterministic graph-lite inputs | working_prototype | partial | do not claim full GNN/MoE |
| HGF-MPC | `hgf_mpc_agent.py` | `hgf_mpc_track1.yaml` | stage4 registry + runner | pass | pass | local wrapper pass | uses historical price windows | functional_mvp | partial | full-year evidence |
| CEVA-KF/CIGA | `ceva_kf_ciga_agent.py` | `ceva_kf_ciga_track1.yaml`, `ceva_kf_ciga_track2.yaml` | stage4 registry + runner | pass | pass | local wrapper pass | stable-effect MVP only | functional_mvp | partial | avoid causal-discovery overclaim |
| risk parity | `risk_parity_agent.py` | `risk_parity_track1.yaml` | stage4 registry + runner | pass | pass | local wrapper path exists | current-day open only | working_prototype | pass | keep as component |
| sector rotation | `sector_rotation_agent.py` | `sector_rotation_track2.yaml` | stage4 registry + runner | pass | pass | Prompt14 local/official mismatch | current-day open only | ablation_candidate | partial | keep Track B default as S1 |
| OCO fallback | `oco_ensemble_agent.py` | `oco_fallback.yaml` | stage4 registry + runner | pass | pass | local wrapper path exists | current-day open only | working_prototype | partial | label OCO-inspired |
| rule-based Stage 1 | `rule_based_extractor.py` | `rule_based.yaml` | stage1 pipeline | pass | pass | used by runner | 15:00 news cutoff | production_candidate | pass | none |
| BGE-small extractor | `bge_small_zh_extractor.py` | `bge_small_zh.yaml` | stage1 config | pass | pass/fallback | optional only | no silent download | optional_mvp | pass | keep disabled by default |
| FinBERT Chinese extractor | `finbert_tone_chinese_extractor.py` | `finbert_tone_chinese.yaml` | stage1 config | pass | pass/fallback | optional only | no silent download | optional_mvp | pass | keep disabled by default |
| hybrid local text extractor | `hybrid_local_text_extractor.py` | `hybrid_local_text.yaml` | stage1 config | pass | pass/fallback | optional only | no silent download | optional_mvp | pass | cache before large runs |
| no-LLM fallback | `no_llm_fallback.py` | `rule_based.yaml` | stage1 fallback | pass | pass | default-safe path | no external dependency | production_candidate | pass | none |
