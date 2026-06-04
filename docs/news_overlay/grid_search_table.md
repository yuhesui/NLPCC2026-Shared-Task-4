# Transformer-First Grid Search Table

Every implementation and testing prompt in the Prompt1-x News Overlay phase
must update this table and the CSV mirror under
`outputs/reports/news_overlay/prompt1x/reference/grid_search_status_table.csv`.

## Full Status Table

| Run ID | Section | Track | N Method | I Method | S Method | Base Config | Transformer Used? | Local Model Required? | Cache Required? | Purpose | Implementation Status | Test Status | 2024 Tune Status | 2025 Frozen Status | GPU Used | Runtime | Sharpe | CumRet | MaxDD | Turnover | Zero-News Pass | Shuffled-News Pass | Lexical Baseline Beat? | Decision | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|
| G00A | baseline | A | N0 | I0 | S0 | p18_rp_macro_w10_s5 | no | no | no | Track A preserved base | documented_not_run | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | keep_base | Overlay disabled; official runtime unchanged. |
| G00B | baseline | B | N0 | I0 | S0 | p18_leeqa_sector_k5_temp35 | no | no | no | Track B preserved base | documented_not_run | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | keep_base | Overlay disabled; official runtime unchanged. |
| G01A | lexical_control | A | N1 | I1 | S3 | p18_rp_macro_w10_s5 | no | no | optional | deterministic-only Track A control | documented_not_run | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | comparator_only | Cannot be Section 1 success condition by itself. |
| G01B | lexical_control | B | N1 | I1 | S2 | p18_leeqa_sector_k5_temp35 | no | no | optional | deterministic-only Track B control | documented_not_run | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | n/a | comparator_only | Lexical hurdle for transformer rows. |
| G10A | transformer_core | A | N2 | I2 | S3 | p18_rp_macro_w10_s5 | yes | yes | yes | BGE relevance + NAI + macro gate | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01A | build | If local BGE missing, mark blocked, do not omit. |
| G11A | transformer_core | A | N13 | I6 | S13 | p18_rp_macro_w10_s5 | yes | yes | yes | aspect-tone + transformer impact + macro sensitivity | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01A | build | Requires FinBERT-style aspect-tone path or blocked row. |
| G12A | transformer_core | A | N2345 | I256 | S13 | p18_rp_macro_w10_s5 | yes | yes | yes | full transformer news stack + macro gate | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01A | build_primary_stack | Primary Track A transformer stack. |
| G10B | transformer_core | B | N2 | I2 | S2 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | BGE relevance + NAI + Rank-IC | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | Main embedding relevance Track B row. |
| G11B | transformer_core | B | N12 | I23 | S12 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | hybrid relevance + NAI/ESC + CAR/Rank-IC | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | Robust hybrid comparator. |
| G12B | transformer_core | B | N2345 | I256 | S126 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | full transformer/attention Track B stack | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build_primary_stack | Primary transformer-first Track B stack. |
| G13B | transformer_core | B | N6 | I23 | S12 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | cross-encoder reranker + impact/sensitivity | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build_if_feasible | If cross-encoder missing, row must be blocked, not omitted. |
| G14B | transformer_core | B | N5 | I5 | S2 | p18_leeqa_sector_k5_temp35 | yes | depends | yes | sector-query attention pooling + Rank-IC | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | Attention pooling row. |
| G15B | transformer_core | B | N4 | I6 | S2 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | label-attention event tagger + aspect impact | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | build | Event tagging and aspect impact row. |
| G20B | higher_capacity | B | N2345 | I256 | S4 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | transformer stack + sparse sensitivity | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | defer_until_core | Higher-capacity after core rows. |
| G21B | higher_capacity | B | N2345 | I256 | S5 | p18_leeqa_sector_k5_temp35 | yes | yes | yes | transformer stack + Black-Litterman views | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | defer_until_core | Bayesian overlay after core rows. |
| G22B | ablation | B | N7 | I7 | S6 | p18_leeqa_sector_k5_temp35 | yes | depends | yes | temporal narrative attention ablation | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | ablation_only | Narrative persistence ablation. |
| G23B | ablation | B | N8 | I2 | S6 | p18_leeqa_sector_k5_temp35 | yes | optional | yes | graph-attention relevance ablation | planned_transformer | not_run_docs_only | pending | pending | 0 | 0 |  |  |  |  | pending | pending | pending_vs_G01B | ablation_only | Graph attention deferred unless time permits. |

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
