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

## Prompt07 Bounded Grid Evidence

Prompt07 added a bounded dated evaluator that runs the News Overlay N/I/S
pipeline against local 2024/2025 news and price slices, then replays emitted
target weights through `reference_official_semantics`.

- Stage 0 2024 controls (`G00A/G00B/G01A/G01B`) passed on 10 bounded dates.
- No-proxy 2024 mandatory grid rows kept missing local models explicit:
  controls passed, 11 rows were `partial_blocked`, and 2 rows were
  `blocked_missing_local_model`.
- Proxy-mode 2024 mandatory grid passed all 17 rows as research-only
  interface/cache evidence; these rows are not real local transformer
  inference and cannot be promoted.
- 2025 evaluation was controls-only because no real transformer candidate was
  selected from 2024. A 2025 calibration-row attempt was refused by the
  2024-only S2 guard, then the runner was fixed to suppress calibration rows
  outside 2024 construction periods.

Latest CSV mirror:
`outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv`.

## Prompt08 Audit Verdict

Prompt08 classified all News Overlay transformer candidates as
`no_promotion` for the current repository state.

- Real local transformer inference remains `blocked_missing_local_model`.
- Proxy-mode rows are useful interface/cache and ablation evidence only.
- Shuffled-news evidence is mixed and several required ablation toggles or
  sweeps are still missing.
- 2025 evaluation was controls-only because no real 2024-selected transformer
  candidate exists.
- Official-server parity and human approval remain mandatory before any later
  promotion.

Audit artifacts:
`outputs/reports/news_overlay/prompt01_11/reference/prompt08_promotion_gate_audit.csv`
and
`outputs/reports/news_overlay/prompt01_11/reference/prompt08_ablation_audit.csv`.

## Prompt09 Verification Note

Prompt09 fixed a bounded grid-evaluator alignment risk and updated the CSV
mirror with Prompt09 verification columns. No grid row was promoted.

- `G10B` was rerun as a two-date 2024 proxy smoke with shuffled-news enabled
  and passed as research-only proxy evidence.
- `N3` was corrected in the method-status table as component-level proxy
  evidence through `N13` and `N2345`; this does not change its
  `blocked_missing_local_model` real-asset status.
- Real local transformer assets, full ablation sweeps, frozen 2025
  transformer evaluation, and official-server parity remain open blockers.

Prompt09 artifacts:
`outputs/reports/news_overlay/prompt01_11/reference/prompt09_error_inventory.csv`
and
`outputs/reports/news_overlay/prompt01_11/reference/prompt09_rerun_status.csv`.

## Prompt20 Local-Only Transformer Asset Smoke

Prompt20 replaced the asset-smoke grid with no-proxy local-only rows backed by
the pinned `BAAI/bge-small-zh-v1.5` snapshot. The latest CSV mirror is
`outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv`.

- 9 of 10 Prompt20 asset-smoke rows passed as `real_model_executed`.
- `P20N6B` remained `blocked_missing_model` because the true cross-encoder
  reranker path is still unimplemented and no reranker snapshot is enabled.
- `network_attempted=false` for all local-only check/run/grid rows after the
  explicit download step.
- The grid cache report recorded 30 cacheable method rows and 9 cache hits,
  confirming real-model cache identity and repeated-run behavior.
- No Prompt20 grid row changes the frozen official runtime or promotes a News
  Overlay candidate.

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
