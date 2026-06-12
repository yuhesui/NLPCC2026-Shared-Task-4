# Current News Overlay State

News Overlay phase is wrapped for next-phase preparation. Active pool is fixed; archived and retired candidates remain preserved for fallback or ablation only.

## Active Pool
| candidate_id | track | candidate | variant | status | 2025_sharpe | notes |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | A | G12A | V3 | active_next_phase | 2.025192 | complete |
| A2 | A | G11A | V0 | active_next_phase | 2.033851 | complete |
| A0 | A | G00A | no_news | baseline_reference | 2.072983 | Reference baseline only, not final news method. |
| B1 | B | G15B | V0 | active_next_phase | 1.619708 | complete |
| B2 | B | G15B | V4 | active_but_requires_frozen_2025_verification | missing_requires_rerun | G15B V4 has 2024 Stage-1 evidence but no exact frozen 2025 V4 row found. |
| B3 | B | G21B_repaired_or_lite | repaired | active_repair_candidate | missing_requires_rerun | Prompt26 gives synthetic/lite diagnostics only; real repaired 2024/2025 rows still required. |
| B0 | B | G00B | no_news | baseline_reference | 1.619708 | Reference baseline only, not final news method. |

## Blocking Gaps
| candidate_id | candidate | variant | gap_category | required_action |
| --- | --- | --- | --- | --- |
| B1 | G15B | V0 | requires_overlay_contribution_check | inspect trace metrics and rerun if overlay is zero |
| B2 | G15B | V4 | requires_frozen_2025_verification | run frozen 2025 for exact variant before final treatment |
| B3 | G21B_repaired_or_lite | repaired | requires_real_2024_2025_retest | run real 2024 tune and frozen 2025 test |
| retired_from_selection | G12B/G12B_lite | all | retired_from_selection | do not select; ablation/report reference only |
| retired_from_selection | G10A | all | retired_from_selection | do not select; ablation/report reference only |
