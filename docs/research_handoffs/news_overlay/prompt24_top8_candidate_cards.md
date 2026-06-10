# Prompt24 Top-8 Candidate Cards

## P23_G11A_s025_i00_c00_v00_capmedium_ddoff

- Track: A
- Rank: 1
- Method stack: N13/I6/S13
- Architecture: FinBERT/aspect-tone hybrid + aspect-impact aggregator + Track A sensitivity/risk overlay
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "off", "impact_threshold": 0.0, "overlay_strength": 0.25, "sensitivity_threshold": 0.0, "turnover_cap": "medium"}`
- 2024 Sharpe/return: 0.594177 / 0.106648
- 2025 Sharpe/return: 2.033851 / 0.329343
- Current status: research_only
- Next use: Track A research candidate; do not parity-prep unless it improves against local and preserved controls.

## P23_G12A_s025_i00_c00_v00_capmedium_ddoff

- Track: A
- Rank: 2
- Method stack: N2345/I256/S13
- Architecture: Composite BGE/FinBERT transformer news stack + composite impact stack + Track A sensitivity/risk overlay
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "off", "impact_threshold": 0.0, "overlay_strength": 0.25, "sensitivity_threshold": 0.0, "turnover_cap": "medium"}`
- 2024 Sharpe/return: 0.59062 / 0.105593
- 2025 Sharpe/return: 2.025192 / 0.32453
- Current status: research_only
- Next use: Track A composite research candidate; useful for ablation-guided minor tuning.

## P23_G10A_s050_i25_c00_v00_caplow_ddmild

- Track: A
- Rank: 3
- Method stack: N2/I2/S3
- Architecture: BGE bi-encoder relevance + base impact + macro risk/sensitivity gate
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "mild", "impact_threshold": 0.25, "overlay_strength": 0.5, "sensitivity_threshold": 0.0, "turnover_cap": "low"}`
- 2024 Sharpe/return: 0.583408 / 0.104316
- 2025 Sharpe/return: 2.024915 / 0.326434
- Current status: research_only
- Next use: Simplest Track A transformer candidate; keep as low-complexity comparator.

## P23_G21B_s100_i25_c00_v00_caplow_ddmild

- Track: B
- Rank: 1
- Method stack: N2345/I256/S5
- Architecture: Full composite transformer news stack + composite impact stack + BL/sector overlay
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "mild", "impact_threshold": 0.25, "overlay_strength": 1.0, "sensitivity_threshold": 0.0, "turnover_cap": "low"}`
- 2024 Sharpe/return: 0.627926 / 0.129154
- 2025 Sharpe/return: 1.570887 / 0.268965
- Current status: research_continue
- Next use: Best fresh 2024 Track B score, but Prompt23 equivalence is material_difference.

## P23_G14B_s100_i00_c00_v00_capmedium_ddoff

- Track: B
- Rank: 2
- Method stack: N5/I5/S2
- Architecture: Sector-query attention + impact-gated attention + Rank-IC sector gate
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "off", "impact_threshold": 0.0, "overlay_strength": 1.0, "sensitivity_threshold": 0.0, "turnover_cap": "medium"}`
- 2024 Sharpe/return: 0.555806 / 0.110667
- 2025 Sharpe/return: 1.539189 / 0.267742
- Current status: parity_review_candidate
- Next use: Frozen-2025-supported Track B candidate for human shortlist review.

## P23_G10B_s050_i25_c00_v00_caplow_ddmild

- Track: B
- Rank: 3
- Method stack: N2/I2/S2
- Architecture: BGE bi-encoder relevance + base impact + Rank-IC sector gate
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "mild", "impact_threshold": 0.25, "overlay_strength": 0.5, "sensitivity_threshold": 0.0, "turnover_cap": "low"}`
- 2024 Sharpe/return: 0.531861 / 0.103946
- 2025 Sharpe/return: 1.553354 / 0.275578
- Current status: parity_review_candidate
- Next use: Simple frozen-2025-supported Track B candidate for human shortlist review.

## P23_G12B_s050_i25_c00_v00_caplow_ddmild

- Track: B
- Rank: 4
- Method stack: N2345/I256/S126
- Architecture: Full composite transformer stack + composite impact + composite sensitivity gate
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "mild", "impact_threshold": 0.25, "overlay_strength": 0.5, "sensitivity_threshold": 0.0, "turnover_cap": "low"}`
- 2024 Sharpe/return: 0.544465 / 0.107973
- 2025 Sharpe/return: 1.531809 / 0.273087
- Current status: research_continue
- Next use: Complex Track B backup; Prompt23 equivalence is material_difference.

## P23_G15B_s025_i00_c00_v00_capmedium_ddoff

- Track: B
- Rank: 5
- Method stack: N4/I6/S2
- Architecture: BGE event-label / label-attention + FinBERT aspect-impact + Rank-IC sector gate
- Frozen parameters: `{"confidence_threshold": 0.0, "drawdown_throttle": "off", "impact_threshold": 0.0, "overlay_strength": 0.25, "sensitivity_threshold": 0.0, "turnover_cap": "medium"}`
- 2024 Sharpe/return: 0.507126 / 0.097399
- 2025 Sharpe/return: 1.619708 / 0.284992
- Current status: parity_review_candidate
- Next use: Strong simple Track B frozen-2025-supported candidate.

