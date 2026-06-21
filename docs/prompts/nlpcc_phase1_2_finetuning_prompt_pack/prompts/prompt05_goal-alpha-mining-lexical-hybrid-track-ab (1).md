# Prompt05 — Goal Mode Alpha Mining on Lexical+BGE/FinBERT Hybrid for Track A/B

You are GPT-5.5 xHigh. Act as senior quant alpha researcher, Chinese financial NLP engineer, 
official-agent integration engineer, and evidence-quality auditor.

## Goal
Starting from the current fork after Prompt04, mine and validate small alpha factors on top of the existing lexical/entity + BGE + FinBERT news tensor path. Do this separately for Track A and Track B. Finish with frozen 2025 evaluation, official-platform/HTTP path check, agent-port update if justified, repo cleanup audit, tests, and dense presented artifacts.

Main root has moved to:
`outputs/reports/next_phase_finetuning_phase12/`

Output folder:
`outputs/reports/next_phase_finetuning_phase12/prompt05_goal_alpha_mining_lexical_hybrid/`

## Hard rules
Use rtk, rtk python, rtk git. No hidden 2026. No 2025 tuning. No online API. No model download. Do not train LoRA. Do not replace final A2/B2 policy unless evidence says branch is rejected and must remain report-only. A0/B0 are reference controls. Any package such as qlib, alphalens, vectorbt, pandas-ta, ta-lib, or ta may be used only if already installed or safely optional; if missing, implement minimal pandas/numpy equivalents and record package_missing_not_blocking.

## Required presented folder
Create dense monitor files, not many tiny files:
- `presented/implementation_log.md`
- `presented/progress_dashboard.md`
- `presented/essential_results.md`
- `presented/blockers_and_decisions.md`
- `presented/final_alpha_mining_report.md`
- `presented/submission_gap_summary.md`
- `presented/run_csv_manifest.csv`
- `presented/run_csv/` with all key CSVs copied

## Stage 0 — Intake
Read Prompt01/02/03a/03b/04 artifacts, Prompt11 configs, actual agent files, data loader, current phase12 final agent, and source maps. Create:
- `reference/input_artifact_manifest.csv`
- `reference/package_availability_audit.csv`
- `reference/current_final_candidate_status.csv`

Audit available packages: qlib, alphalens, vectorbt, pandas-ta, ta, sklearn, scipy, statsmodels. Do not install unless project policy already allows.

## Stage 1 — Build alpha factor library
Create factor families using only decision-time-visible data.

Common factors:
- lexical/entity relevance score
- base BGE relevance score
- fine-tuned BGE relevance score
- hybrid lexical+BGE score
- FinBERT sentiment_score, confidence, entropy
- news count, event persistence, repeated-theme support, novelty
- rolling/decayed versions: 1d, 3d, 5d, 10d half-life
- price trend, reversal, volatility, drawdown, correlation, momentum, turnover-pressure controls

Track A-specific factors:
- macro risk-on/risk-off news intensity
- liquidity/easing/tightening factor
- property/credit stress factor
- bond/equity/gold cross-asset regime factor
- macro news persistence x price regime interaction

Track B-specific factors:
- cross-sectional sector relevance rank
- sector event breadth/count
- event persistence by sector
- FinBERT tone x sector relevance
- lexical vs BGE disagreement factor
- sector momentum/reversal/volatility factor
- rank-IC stability shrinkage and evidence-count calibration

Use operations: lag, zscore, winsorize, rank, cross-sectional rank, rolling mean/sum/std, EMA decay, interaction, neutralize-by-track, turnover penalty, cap/shrink. Create:
- `factors/factor_catalog.csv`
- `factors/factor_daily_panel.parquet` or `.csv`
- `factors/factor_build_manifest.csv`
- `presented/run_csv/factor_catalog.csv`

## Stage 2 — Factor diagnostics on 2024 only
Use 2024 train/dev only. Evaluate each factor by track.

Required diagnostics:
- IC / rank-IC by horizon
- quantile spread return
- hit rate
- turnover impact
- drawdown impact
- active-vs-zeroed-vs-shuffled factor tests
- correlation/clustering/redundancy
- stability train vs dev

Use alphalens-like tearsheets if available; otherwise implement pandas equivalent. Create:
- `diagnostics/factor_ic_table_2024.csv`
- `diagnostics/factor_quantile_spread_2024.csv`
- `diagnostics/factor_correlation_cluster_2024.csv`
- `diagnostics/factor_ablation_2024.csv`
- `presented/run_csv/factor_ic_table_2024.csv`

## Stage 3 — Compare FinBERT vs BGE vs lexical
Run explicit side-by-side families:
1. lexical only
2. base BGE only
3. fine-tuned BGE only
4. lexical + base BGE
5. lexical + fine-tuned BGE
6. FinBERT only
7. lexical + FinBERT
8. BGE + FinBERT
9. lexical + fine-tuned BGE + FinBERT
10. factor-mined ensemble

For Track A and Track B separately, report which family works and why. Create:
- `diagnostics/news_model_family_comparison_2024.csv`
- `diagnostics/finbert_vs_bge_error_analysis.csv`
- `presented/run_csv/news_model_family_comparison_2024.csv`

## Stage 4 — Alpha selection and bounded overlay optimization
Build candidate overlays from top stable factors. Optimize on 2024 train only; select on 2024 dev only. Do not use 2025 for selection.

Track A objective: improve Sharpe/drawdown with low turnover using macro regime news factors. Favor stability and low L1 changes.
Track B objective: improve sector ranking and rank-IC stability. Penalize high turnover, concentration, and factors that lose to shuffled news.

Create variants:
- `A2_alpha_lexical_hybrid`
- `A2_alpha_macro_regime`
- `B2_alpha_sector_rankic`
- `B2_alpha_event_persistence`
- `B2_alpha_lexical_bge_finbert`

Create:
- `optimiser/alpha_overlay_trials_2024.csv`
- `optimiser/alpha_overlay_best_configs.csv`
- `configs/A2_alpha_best.yaml`
- `configs/B2_alpha_best.yaml`
- `presented/run_csv/alpha_overlay_best_configs.csv`

## Stage 5 — Frozen 2025 test and ablation
Freeze configs. Run 2025 public evaluation once per candidate family; no reselection.

Minimum rows:
A0, A2_phase12_current, A2_alpha_best, B0, B2_phase12_current, B2_alpha_best.

Ablations for A2_alpha_best and B2_alpha_best:
- active
- zeroed
- date_shuffled with at least 5 seeds
- lexical_disabled
- BGE_disabled
- FinBERT_disabled
- price_factor_disabled
- event_persistence_disabled

Create:
- `reference/frozen_2025_alpha_results.csv`
- `reference/frozen_2025_alpha_ablation.csv`
- `presented/run_csv/frozen_2025_alpha_results.csv`
- `presented/run_csv/frozen_2025_alpha_ablation.csv`

## Stage 6 — Official agent port and server check
If alpha branch beats current phase12 by meaningful epsilon or improves risk robustness, port only the selected frozen config into actual agent path behind `strategy='phase12_alpha'`. If not, leave as report-only. Run direct official-platform replay and strict HTTP probe if possible. Create:
- `server_run/official_server_or_http_alpha_results.csv`
- `repo_cleanup/source_config_hash_manifest.csv`
- `presented/run_csv/official_server_or_http_alpha_results.csv`

## Stage 7 — Tests and cleanup
Run:
- `rtk python -m pytest tests/test_nlpcc/test_news_overlay -q`
- `rtk python -m pytest tests/test_nlpcc -q`
- `rtk python -m pytest tests -q`
- `rtk python -m compileall src NLPCC_tasks tests` if feasible
- `rtk python -m pip check` if feasible
Record environment-blocked separately from code failure.

## Final decision rules
Promote a branch only if:
- no hidden 2026 and no 2025 tuning
- active beats zeroed and mean shuffled by meaningful margin
- improves current phase12 or gives clearly better drawdown/turnover with near-equal Sharpe
- official-platform path works
- proxy/fake/fixed-target replay is false

If not, mark report_only_alpha_mining and keep current phase12.

## Final response format
Prompt05 status: <pass/partial/fail/blocked>
Best Track A alpha: <candidate/none>
Best Track B alpha: <candidate/none>
Track A decision: <promote/keep_current/report_only>
Track B decision: <promote/keep_current/report_only>
FinBERT vs BGE verdict: <summary>
Lexical hybrid verdict: <summary>
Frozen 2025 rows: <n> csv: <path>
Ablation status: <pass/partial/fail> csv: <path>
Official path: <complete/partial/blocked>
Tests: <summary>
Hidden 2026 used? no
2025 tuning used? no
Main caveats: <list>
Best next action: <one action>
