# Final Candidate Pool

This is the frozen News Overlay next-phase pool. It is not an official runtime promotion.

## Active Candidates
| candidate_id | track | candidate | variant | stack | enhancement | role | status | 2025_sharpe | evidence_status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | G12A | V3 | N2345/I256/S13 | H4 | main_track_a_novelty_candidate | active_next_phase | 2.025192 | complete | complete |
| A2 | A | G11A | V0 | N13/I6/S13 | off | track_a_empirical_news_candidate | active_next_phase | 2.033851 | complete | complete |
| A0 | A | G00A | no_news | N0/I0/S0 | off | fast_reference_baseline_only | baseline_reference | 2.072983 | baseline_reference_only | Reference baseline only, not final news method. |
| B1 | B | G15B | V0 | N4/I6/S2 | H1_or_hooks_off | event_label_aspect_impact_anchor | active_next_phase | 1.619708 | complete | complete |
| B2 | B | G15B | V4 | N4/I6/S2 | H1+H5 | active_enhancement_diagnostic_candidate | active_but_requires_frozen_2025_verification | missing_requires_rerun | missing_requires_rerun | G15B V4 has 2024 Stage-1 evidence but no exact frozen 2025 V4 row found. |
| B3 | B | G21B_repaired_or_lite | repaired | N2345/I256/S5 | consensus_shrink_plus_BL_view_confidence_cap | high_upside_complex_candidate | active_repair_candidate | missing_requires_rerun | missing_requires_rerun | Prompt26 gives synthetic/lite diagnostics only; real repaired 2024/2025 rows still required. |
| B0 | B | G00B | no_news | N0/I0/S0 | off | fast_reference_baseline_only | baseline_reference | 1.619708 | baseline_reference_only | Reference baseline only, not final news method. |

## Archived / Retired
| group | candidate | variant | stack | enhancement | status |
| --- | --- | --- | --- | --- | --- |
| fallback_archive | G14B | V4 | N5/I5/S2 | H1+H5 | archived_fallback |
| fallback_archive | G10B | V5 | N2/I2/S2 | H1+H2+H4+H5 | archived_fallback |
| retired_from_selection | G12B/G12B_lite | all | N2345/I256/S126 | diagnostic only | retired_ablation_reference |
| retired_from_selection | G10A | all | N2/I2/S3 | simple Track A reference | retired_ablation_reference |

## Evidence Gaps
| candidate_id | candidate | variant | gap_category | required_action |
| --- | --- | --- | --- | --- |
| A1 | G12A | V3 | complete | use in next phase |
| A2 | G11A | V0 | complete | use in next phase |
| A0 | G00A | no_news | baseline_reference_only | use only for fast control deltas |
| B1 | G15B | V0 | requires_overlay_contribution_check | inspect trace metrics and rerun if overlay is zero |
| B2 | G15B | V4 | requires_frozen_2025_verification | run frozen 2025 for exact variant before final treatment |
| B3 | G21B_repaired_or_lite | repaired | requires_real_2024_2025_retest | run real 2024 tune and frozen 2025 test |
| B0 | G00B | no_news | baseline_reference_only | use only for fast control deltas |
| fallback_archive | G14B | V4 | complete | keep archived; use only if selected candidate fails |
| fallback_archive | G10B | V5 | complete | keep archived; use only if selected candidate fails |
| retired_from_selection | G12B/G12B_lite | all | retired_from_selection | do not select; ablation/report reference only |
| retired_from_selection | G10A | all | retired_from_selection | do not select; ablation/report reference only |
