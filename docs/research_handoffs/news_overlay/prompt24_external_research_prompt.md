# External Research Prompt - Prompt24 News Overlay Top-8

You are advising on minor, implementable, ablatable enhancements to an existing Chinese financial News Overlay system for NLPCC 2026 Shared Task 4.

Do not propose new large architectures, online LLM calls, hidden 2026 data use, 2025 tuning, large model downloads, unconstrained strategy overrides, or opaque methods that cannot be ablated.

Strict rule: 2024 is the only tuning period. 2025 is a frozen test period. Official runtime configs must remain untouched.

Prompt23 caveat: fresh local-transformer inference revised Prompt22 replay results; equivalence counts were 46 confirmed, 71 minor numeric drift, and 95 material differences. Use Prompt23 fresh results as source of truth.

## Current Top-8
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

## Allowed Enhancement Themes
- threshold schedules
- event magnitude smoothing and decay
- confidence damping
- sector-specific sensitivity calibration
- Rank-IC gate stability
- low-turnover overlay clipping
- Track A risk scaling
- Track B sector-rank tilt
- candidate-specific ablations
- official-runtime dependency minimisation

## Required Research Output Tables

1. Candidate-specific minor changes: candidate, change, expected mechanism, implementation files, 2024-only tuning parameters, ablation plan.
2. Risk controls: leakage risk, turnover risk, drawdown risk, dependency risk, official-runtime impact.
3. Prioritised experiment queue: smoke, quick 2024 tune, frozen 2025 test, parity-prep shortlist.

Avoid vague suggestions. Every proposal must be small enough to implement and ablate against the current frozen parameters.
