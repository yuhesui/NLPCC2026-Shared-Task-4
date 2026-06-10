# Prompt24 News Overlay Research Context

Stage 2 - Research Context Export

This repository implements NLPCC 2026 Shared Task 4 research extensions for a transformer-first News Overlay pipeline. Prompt23 completed a full fresh local-transformer inference matrix. The next research step is minor enhancement planning for the current top-8 candidates, not a new architecture or full grid.

Rules: tune only on 2024; use 2025 only as frozen test; do not use hidden 2026 data; do not download models; do not call online APIs; keep official runtime untouched.

## Top-8
| track | rank | run_id | family | method_stack | current_status | recommended_next_use |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1 | P23_G11A_s025_i00_c00_v00_capmedium_ddoff | G11A | N13/I6/S13 | research_only | Track A research candidate; do not parity-prep unless it improves against local and preserved controls. |
| A | 2 | P23_G12A_s025_i00_c00_v00_capmedium_ddoff | G12A | N2345/I256/S13 | research_only | Track A composite research candidate; useful for ablation-guided minor tuning. |
| A | 3 | P23_G10A_s050_i25_c00_v00_caplow_ddmild | G10A | N2/I2/S3 | research_only | Simplest Track A transformer candidate; keep as low-complexity comparator. |
| B | 1 | P23_G21B_s100_i25_c00_v00_caplow_ddmild | G21B | N2345/I256/S5 | research_continue | Best fresh 2024 Track B score, but Prompt23 equivalence is material_difference. |
| B | 2 | P23_G14B_s100_i00_c00_v00_capmedium_ddoff | G14B | N5/I5/S2 | parity_review_candidate | Frozen-2025-supported Track B candidate for human shortlist review. |
| B | 3 | P23_G10B_s050_i25_c00_v00_caplow_ddmild | G10B | N2/I2/S2 | parity_review_candidate | Simple frozen-2025-supported Track B candidate for human shortlist review. |
| B | 4 | P23_G12B_s050_i25_c00_v00_caplow_ddmild | G12B | N2345/I256/S126 | research_continue | Complex Track B backup; Prompt23 equivalence is material_difference. |
| B | 5 | P23_G15B_s025_i00_c00_v00_capmedium_ddoff | G15B | N4/I6/S2 | parity_review_candidate | Strong simple Track B frozen-2025-supported candidate. |
