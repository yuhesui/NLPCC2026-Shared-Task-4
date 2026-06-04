# Transformer-First Grid Search Table

Every implementation and testing prompt in the Prompt1-x News Overlay phase
must update this table and the CSV mirror under
`outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv`.

## Full Status Table

| Run ID | Section | Track | N Method | I Method | S Method | Base Config | Transformer Used? | Local Model Required? | Cache Required? | Purpose | Implementation Status | Test Status | 2024 Tune Status | 2025 Frozen Status | GPU Used | Runtime | Sharpe | CumRet | MaxDD | Turnover | Zero-News Pass | Shuffled-News Pass | Lexical Baseline Beat? | Decision | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|
| G00A | baseline | A | N0 | I0 | S0 | p18_rp_macro_w10_s5 | no | no | no | Track A preserved base | pipeline_integrated | prompt06_grid_runner_passed | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | keep_base | Official runtime unchanged; v2 trace and cache/runtime reports written. |
| G00B | baseline | B | N0 | I0 | S0 | p18_leeqa_sector_k5_temp35 | no | no | no | Track B preserved base | pipeline_integrated | prompt06_grid_runner_passed | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | keep_base | Official runtime unchanged; v2 trace and cache/runtime reports written. |
| G01A | lexical_control | A | N1 | I1 | S3 | p18_rp_macro_w10_s5 | no | no | optional | deterministic-only Track A control | pipeline_integrated | prompt06_grid_runner_passed | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | comparator_only | Deterministic control with bounded macro risk gate and v2 trace. |
| G01B | lexical_control | B | N1 | I1 | S2 | p18_leeqa_sector_k5_temp35 | no | no | optional | deterministic-only Track B control | pipeline_integrated | prompt06_grid_runner_passed | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | comparator_only | Deterministic control with Rank-IC gate and v2 trace. |
| G10A | transformer_core | A | N2 | I2 | S3 | p18_rp_macro_w10_s5 | yes | yes | yes | BGE relevance + NAI + macro gate | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01A | build | I2 PT-NAI plus S3 macro gate integrated; local N2 asset missing. |
| G11A | transformer_core | A | N13 | I6 | S13 | p18_rp_macro_w10_s5 | yes | yes | yes | aspect-tone + transformer impact + macro sensitivity | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01A | build | N13/I6/S13 integrated; local transformer assets missing. |
| G12A | transformer_core | A | N2345 | I256 | S13 | p18_rp_macro_w10_s5 | yes | yes | yes | full transformer news stack + macro gate | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01A | build_primary_stack | Full N/I stack plus S13 integrated; local transformer assets missing. |
| G10B | transformer_core | B | N2 | I2 | S2 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | BGE relevance + NAI + Rank-IC | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | I2 Track B NAI plus S2 integrated; local N2 asset missing. |
| G11B | transformer_core | B | N12 | I23 | S12 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | hybrid relevance + NAI/ESC + CAR/Rank-IC | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | I23 plus S12 integrated; local N12 asset missing. |
| G12B | transformer_core | B | N2345 | I256 | S126 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | full transformer/attention Track B stack | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build_primary_stack | S126 integrated with visible `blocked_missing_local_model` state; no promotion. |
| G13B | transformer_core | B | N6 | I23 | S12 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | cross-encoder reranker + impact/sensitivity | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build_if_feasible | N6 cross-encoder interface remains asset-blocked; S12 integrated. |
| G14B | transformer_core | B | N5 | I5 | S2 | p18_leeqa_sector_k5_temp35 | yes | depends | yes | sector-query attention pooling + Rank-IC | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | I5 attention pooling plus S2 integrated; local N5/I5 assets missing. |
| G15B | transformer_core | B | N4 | I6 | S2 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | label-attention event tagger + aspect impact | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | I6 aspect-impact plus S2 integrated; local N4/I6 assets missing. |
| G20B | higher_capacity | B | N2345 | I256 | S4 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | transformer stack + sparse sensitivity | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | defer_until_core | S4 sparse sensitivity proxy integrated; requires later grid evidence. |
| G21B | higher_capacity | B | N2345 | I256 | S5 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | transformer stack + Black-Litterman views | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | defer_until_core | S5 BL news-view proxy integrated; requires later grid evidence. |
| G22B | ablation | B | N7 | I7 | S6 | p18_leeqa_sector_k5_temp35 | yes | depends | yes | temporal narrative attention ablation | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | ablation_only | S6 attention pooling integrated with `blocked_missing_local_model` fallback state. |
| G23B | ablation | B | N8 | I2 | S6 | p18_leeqa_sector_k5_temp35 | yes | optional | yes | graph-attention relevance ablation | pipeline_integrated_local_model_blocked | prompt06_grid_runner_blocked_missing_local_model | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | ablation_only | S6 can consume graph/attention impact rows; local assets still missing. |

## Required Comparison Rule

Transformer candidates must be compared against their lexical-control
counterparts:

```text
G10A/G11A/G12A must beat or explain failure relative to G01A.
G10B/G11B/G12B/G13B/G14B/G15B must beat or explain failure relative to G01B.
```

Deterministic-only candidates may remain fallback and comparators, but cannot
be declared the Section 1 success condition unless all transformer methods are
blocked by unavailable local assets or fail ablation tests.
