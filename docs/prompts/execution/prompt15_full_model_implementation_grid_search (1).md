# Prompt 15 — Full Model Implementation, Offline Text-Model Integration, Grid Search, and Top-5 Pipeline Selection

## Role

You are a senior quantitative research engineer, LLM-systems architect, portfolio-construction specialist, and shared-task final-integration lead.

You are working on the NLPCC 2026 Shared Task 4 repository after Prompt14 repaired the official wrapper, portfolio adapter, order planner, trade validator, and SystemRunner.

This prompt is **not** merely a validation pass.

Your task is to implement the remaining high-priority model families as functional MVPs, wire the already-downloaded Hugging Face models into Stage 1 as offline local text models, run a broad grid search over modular four-stage combinations, and select the **Top 5 complete candidate pipelines** for final submission/report consideration.

The final repository after this prompt should contain a complete working modular research system, not only baselines and placeholders.

---

## 0. Mandatory Context to Read First

Before coding, read the latest audit and repair artifacts:

```text
outputs/reports/prompt13/full_audit_report.md
outputs/reports/prompt13/final_recommendation.md
outputs/reports/prompt13/official_local_parity_report.md
outputs/reports/prompt13/stage1_trace_report.md
outputs/reports/prompt13/module_maturity_matrix.md
outputs/reports/prompt13/full_year_ablation_report.md
outputs/reports/prompt13/public_a_2025_evaluation_report.md
outputs/reports/prompt13/submission_wrapper_audit.md

outputs/reports/prompt14/final_recommendation.md
outputs/reports/prompt14/pipeline_repair_report.md
outputs/reports/prompt14/track_status_matrix.md
outputs/reports/prompt14/stage_status_matrix.md
outputs/reports/prompt14/model_status_matrix.md
outputs/reports/prompt14/official_wrapper_repair_report.md
outputs/reports/prompt14/official_local_parity_rerun_report.md
outputs/reports/prompt14/huggingface_model_audit.md
outputs/reports/prompt14/package_rebuild_report.md

docs/strategy/B_LIST_HARDENING.md
docs/implementation_logs/20260530_112225_prompt14_pipeline_repair.md
```

Also inspect:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/runtime/system_runner.py
src/nlpcc/execution/official_adapter.py
src/nlpcc/execution/order_planner.py
src/nlpcc/execution/trade_validator.py
src/nlpcc/stage1_news/
src/nlpcc/stage2_text_store/
src/nlpcc/stage3_trade/
src/nlpcc/stage4_agent/
src/nlpcc/portfolio/
src/nlpcc/runtime/
src/tools/optimiser/
src/tools/experiments/
src/tools/reporting/
configs/
scripts/
tests/
outputs/submissions/
```

If any file is missing, report it and continue with the closest current repo convention.

---

## 1. Current Ground Truth from Prompt14

Treat the following as the current status unless the repository proves otherwise:

```text
Readiness verdict:
  Not ready, but close.

Track A / Macro:
  current default candidate = robust_bl_track1
  fallback = s1_macro
  status = best local candidate, but still needs full wrapper-based 2024/2025 validation and robust BL parity closure.

Track B / Sector:
  current default candidate = s1_sector
  experimental = sector_rotation_track2
  fallback = s1_sector
  status = keep S1 as default unless new construction-period evidence improves.

Official parity:
  s0_equal_weight_macro = pass
  s1_macro = pass
  s1_sector = pass
  robust_bl_track1 = small mismatch remains
  sector_rotation_track2 = still fails trade/value parity

Stage 1:
  deterministic rule-based default exists.
  LLM extraction exists only as optional/debug callable.
  Hugging Face models were previously disabled by default.

Prompt15 change:
  BAAI/bge-small-zh-v1.5 and yiyanghkust/finbert-tone-chinese have now been downloaded by the user using:
    hf download BAAI/bge-small-zh-v1.5
    hf download yiyanghkust/finbert-tone-chinese
  Therefore, Prompt15 must implement offline local model integration for these models.
```

---

## 2. Official Constraints to Preserve

Preserve:

- Track A / Track 1: Macro-Asset Allocation.
- Track B / Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / construction.
- 2025 data is public A-list / Phase A evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- Any training/fine-tuning/retrieval/model construction must be reproducible and submitted if used.
- Raw official data must not be modified or redistributed.
- Final runtime must retain a deterministic no-model / no-API fallback.

---

## 3. High-Priority Method Families That Must Be Implemented

The following method families were previously evaluated as important. Prompt15 must implement **functional MVPs** for all of them, not leave them as empty placeholders.

Use the prior research ranking as motivation:

| Method | Competition Score | Research / Report Score | Prior Interpretation |
|---|---:|---:|---|
| DRO-BL-RP | 7.37 | 7.89 | Best final submission candidate; high competition value with adequate report signal. |
| BSA-RP | 7.01 | 8.14 | Strong conservative/report hybrid; useful if regime plots validate. |
| ARMOR-OMD | 7.08 | 7.84 | Safest adaptive fallback and strongest meta-allocation story. |
| LEEQA-Rank | 6.26 | 7.35 | Track 2 practical extension; not full centrepiece. |
| KG-MoE-Lite | 5.37 | 8.24 | Best visual / Track 2 report candidate, but weak immediate ROI. |
| HGF-MPC | 6.14 | 8.09 | Macro-theory-rich, implementation-heavy. |
| CEVA-KF / CIGA | 5.40 | 8.44 | Best research thesis; not first production engine. |

## Strict Implementation Requirement

For every method above:

1. create or complete a real code path;
2. create or complete a config file;
3. create or complete tests;
4. make it runnable through the modular pipeline;
5. make it usable in the grid search;
6. label maturity honestly as MVP / prototype / production candidate;
7. avoid empty placeholder logic;
8. if a full mathematically sophisticated version is too large, implement a **minimal but functional version** that captures the intended mathematical engine.

Do **not** leave any of these seven methods as a pure stub after Prompt15.

---

# Part A — Stage 1 Offline Text-Model Integration

## Objective

Implement offline Stage 1 model-backed text processing using the already-downloaded Hugging Face models:

```text
BAAI/bge-small-zh-v1.5
yiyanghkust/finbert-tone-chinese
```

The models were downloaded by the user using:

```bash
hf download BAAI/bge-small-zh-v1.5
hf download yiyanghkust/finbert-tone-chinese
```

## Required Behavior

Add Stage 1 modules for:

```text
1. rule_based_extractor
2. bge_small_zh_embedding_extractor
3. finbert_tone_chinese_sentiment_extractor
4. hybrid_rule_bge_finbert_extractor
5. no_llm_fallback
```

The hybrid extractor should combine:

```text
rule-based event/entity/sector tags
+ FinBERT Chinese sentiment/intensity
+ BGE-small Chinese embeddings for event similarity / sector relevance
```

## Required Files

Use current repo conventions, likely:

```text
src/nlpcc/stage1_news/models/bge_small_zh_extractor.py
src/nlpcc/stage1_news/models/finbert_tone_chinese_extractor.py
src/nlpcc/stage1_news/models/hybrid_local_text_extractor.py
src/nlpcc/stage1_news/local_model_loader.py
src/nlpcc/stage1_news/text_model_config.py
configs/stage1_news/bge_small_zh.yaml
configs/stage1_news/finbert_tone_chinese.yaml
configs/stage1_news/hybrid_local_text.yaml
tests/test_nlpcc/test_stage1_news/test_prompt15_local_text_models.py
```

Adjust names if the current repo uses different conventions.

## Local Model Path Handling

Do not assume a hard-coded user-specific cache path.

Implement path discovery in this order:

```text
1. config local_path if provided;
2. environment variable NLPCC_HF_MODEL_DIR;
3. Hugging Face cache if model already exists locally;
4. fail with clear message and exact download command.
```

Do not silently download models during tests or default runtime unless explicitly configured.

## Required Config

Example:

```yaml
text_model:
  enabled: true
  provider: local_huggingface
  model_name: BAAI/bge-small-zh-v1.5
  local_path: null
  offline_only: true
  fallback: rule_based
```

Default production config should still support:

```yaml
text_model:
  enabled: false
  fallback: rule_based
```

## Required Stage 1 Output Schema

Make sure Stage 1 outputs can include:

```text
event tuples
macro tags
sector tags
asset tags
sentiment label
sentiment score
embedding vector or embedding hash/reference
relevance score
confidence score
horizon label
source reliability
model metadata
cache key
fallback flag
```

If embeddings are large, store references or compressed vectors rather than bloating every daily artifact.

## Required Report

Create:

```text
outputs/reports/prompt15/stage1_local_model_integration_report.md
```

Use:

| Extractor | Model | Local Path Source | Offline? | Runtime Default? | Output Fields | Fallback | Status | Notes |
|---|---|---|---|---|---|---|---|---|

---

# Part B — Implement / Complete Stage 2 Storage for All Top Methods

## Objective

Ensure each top method has a compatible Stage 2 storage representation.

Required Stage 2 objects:

```text
flat feature table
BL view store
confidence matrix
decayed event memory
belief-state vector
retrieval analogue index
knowledge graph / sector-policy graph
causal event-impact graph
rank feature panel
```

## Required Mapping

| Method | Required Stage 2 Storage |
|---|---|
| DRO-BL-RP | BL view store + confidence matrix + risk-parity anchor state |
| BSA-RP | belief-state vector + decayed event memory |
| ARMOR-OMD | retrieval analogue index + base allocator performance state |
| LEEQA-Rank | rank feature panel |
| KG-MoE-Lite | ETF-sector-policy graph + sector impact panel |
| HGF-MPC | hidden-state posterior / Kalman state |
| CEVA-KF / CIGA | causal event-impact graph + invariant feature panel |

## Required Behavior

If an existing module is stubbed, implement a minimal functional version.

Examples:

```text
retrieval analogue index:
  store event embeddings and historical next-period returns;
  retrieve k nearest prior event states by cosine similarity;
  output analogue return/risk estimate.

knowledge graph:
  store nodes for assets/sectors/entities/policies;
  store weighted edges from extracted events;
  output graph activation scores per asset/sector.

causal graph:
  store event type → sector/asset impact edges;
  estimate stable impact using 2024 subwindow consistency;
  output causal/invariant confidence scores.

rank feature panel:
  combine momentum, volatility, sentiment, sector tags, graph score, analogue score;
  output cross-sectional rank features for Track B.
```

## Required Files

Likely paths:

```text
src/nlpcc/stage2_text_store/models/retrieval_index.py
src/nlpcc/stage2_text_store/models/knowledge_graph.py
src/nlpcc/stage2_text_store/models/causal_event_graph.py
src/nlpcc/stage2_text_store/models/rank_feature_panel.py
src/nlpcc/stage2_text_store/models/belief_state.py
src/nlpcc/stage2_text_store/models/hidden_state_store.py
configs/stage2_text_store/retrieval_index.yaml
configs/stage2_text_store/knowledge_graph.yaml
configs/stage2_text_store/causal_event_graph.yaml
configs/stage2_text_store/rank_feature_panel.yaml
configs/stage2_text_store/belief_state.yaml
tests/test_nlpcc/test_stage2_text_store/test_prompt15_top_method_stores.py
```

---

# Part C — Implement / Complete Stage 3 States for All Top Methods

## Objective

Ensure Stage 3 supports all top model families.

Required Stage 3 states:

```text
returns
volatility
shrinkage covariance
momentum
drawdown
breadth
cash feasibility
turnover capacity
risk budgets
price-HMM regime state
Kalman drift state
base allocator performance state
rank labels / cross-sectional future-free ranking targets for training only
```

## Method Mapping

| Method | Required Stage 3 State |
|---|---|
| DRO-BL-RP | covariance, volatility, risk budgets, turnover/cash |
| BSA-RP | volatility, drawdown, belief-conditioned risk budgets |
| ARMOR-OMD | base allocator performance state, regret/update state |
| LEEQA-Rank | cross-sectional price features and ranking labels for 2024 training only |
| KG-MoE-Lite | sector momentum, volatility, correlation graph |
| HGF-MPC | Kalman drift state, price-HMM regime state |
| CEVA-KF / CIGA | stable subwindow effect estimates and robustness statistics |

## Critical Leakage Rule

Any labels or future returns used for training/ranking must be generated only inside training/evaluation tooling and must never be available at decision time.

At decision time, Stage 3 may use only:

```text
past complete trading days
current-day open only
current portfolio/cash/holdings
officially available same-day news before cutoff
```

## Required Files

Likely:

```text
src/nlpcc/stage3_trade/models/price_hmm_state.py
src/nlpcc/stage3_trade/models/kalman_drift.py
src/nlpcc/stage3_trade/models/base_allocator_performance.py
src/nlpcc/stage3_trade/models/rank_training_labels.py
src/nlpcc/stage3_trade/models/stable_effect_estimator.py
configs/stage3_trade/price_hmm_state.yaml
configs/stage3_trade/kalman_drift.yaml
configs/stage3_trade/base_allocator_performance.yaml
tests/test_nlpcc/test_stage3_trade/test_prompt15_top_method_states.py
```

---

# Part D — Implement / Complete Stage 4 Agents for All Top Methods

## Objective

Implement functional MVP final agents for all top method families.

## Required Agents

### 1. DRO-BL-RP

Implement as:

```text
Stage 1 views + confidence
→ Stage 2 P, q, Ω
→ Stage 3 covariance / risk budgets
→ robust BL posterior return
→ risk-parity or S1 anchor
→ turnover-controlled target weights
```

Required path:

```text
src/nlpcc/stage4_agent/models/dro_bl_rp_agent.py
configs/systems/dro_bl_rp_track1.yaml
```

### 2. BSA-RP

Implement as:

```text
belief-state vector over regimes
→ regime-conditioned risk budgets
→ risk parity allocation
→ drawdown / turnover guard
```

Required path:

```text
src/nlpcc/stage4_agent/models/bsa_rp_agent.py
configs/systems/bsa_rp_track1.yaml
```

### 3. ARMOR-OMD

Implement as:

```text
base allocator pool
+ retrieval analogue score
+ online mirror descent / exponentiated-weight update
+ transaction-cost-aware penalty
+ fallback to S1
```

If persistent state is difficult, implement a functional deterministic persisted-state MVP with a state file or in-memory backtest state. Do not call it full online learning unless it updates over days.

Required path:

```text
src/nlpcc/stage4_agent/models/armor_omd_agent.py
configs/systems/armor_omd_macro.yaml
configs/systems/armor_omd_sector.yaml
```

### 4. LEEQA-Rank

Implement as:

```text
Stage 1 event/sector/sentiment features
+ Stage 2 rank feature panel
+ Stage 3 momentum/volatility features
→ cross-sectional ranking model or deterministic rank scorer
→ top-k / softmax allocator
→ risk and turnover controls
```

If no ML model is trained, implement a deterministic rank scorer with clear feature weights and grid-searchable parameters.

Required path:

```text
src/nlpcc/stage4_agent/models/leeqa_rank_agent.py
configs/systems/leeqa_rank_track2.yaml
```

### 5. KG-MoE-Lite

Implement as:

```text
ETF-sector-policy graph activations
+ sector impact panel
+ base experts:
    momentum expert
    inverse-vol expert
    defensive expert
    news-impact expert
→ softmax router / gating weights
→ expert mixture target weights
```

This is KG-MoE-Lite, not full GNN/MoE.

Required path:

```text
src/nlpcc/stage4_agent/models/kg_moe_lite_agent.py
configs/systems/kg_moe_lite_track2.yaml
```

### 6. HGF-MPC

Implement as:

```text
hidden Gaussian drift / Kalman state
+ optional HMM regime state
→ short-horizon expected return path
→ constrained model-predictive allocation
→ turnover and drawdown controls
```

MVP can be one-step MPC with Kalman-smoothed drift.

Required path:

```text
src/nlpcc/stage4_agent/models/hgf_mpc_agent.py
configs/systems/hgf_mpc_track1.yaml
```

### 7. CEVA-KF / CIGA

Implement as:

```text
causal event-impact graph
+ invariant subwindow stability score
+ Kalman-filtered impact estimates
→ causal confidence-adjusted asset tilt
→ conservative allocation overlay on S1
```

MVP can use stable event-type impact estimates across 2024 subwindows.

Required path:

```text
src/nlpcc/stage4_agent/models/ceva_kf_ciga_agent.py
configs/systems/ceva_kf_ciga_track1.yaml
configs/systems/ceva_kf_ciga_track2.yaml
```

## Required Agent Registry

Update the agent/system registry so all methods are runnable by config.

Likely:

```text
src/nlpcc/stage4_agent/registry.py
configs/systems/
```

## Required Tests

Add:

```text
tests/test_nlpcc/test_stage4_agent/test_prompt15_top_methods.py
```

Tests must verify each agent:

```text
imports
runs on minimal synthetic input
emits valid target weights or official trades through SystemRunner
does not use future price fields
respects max weights
respects no-same-day-sell-proceeds rule through order planner
falls back safely on missing Stage 1/2 signals
```

---

# Part E — System Combination Grid Search

## Objective

Run a grid search across modular four-stage combinations to identify the Top 5 complete candidate systems.

This is required.

## Search Space

At minimum include:

### Stage 1 Candidates

```text
rule_based
finbert_tone_chinese
bge_small_zh
hybrid_rule_bge_finbert
no_news
```

### Stage 2 Candidates

```text
flat_feature_table
bl_view_confidence
decayed_event_memory
belief_state
retrieval_analogue_index
knowledge_graph_lite
causal_event_graph
rank_feature_panel
```

### Stage 3 Candidates

```text
s1_trade_state
shrinkage_covariance
risk_budget_state
hmm_regime_state
kalman_drift_state
base_allocator_performance
stable_effect_state
```

### Stage 4 Candidates

```text
s0_equal_weight
s1_quant_core
dro_bl_rp
bsa_rp
armor_omd
leeqa_rank
kg_moe_lite
hgf_mpc
ceva_kf_ciga
oco_fallback
sector_rotation
```

Do not attempt every impossible Cartesian product blindly if it is too large. Instead:

1. define compatibility rules;
2. generate all valid combinations;
3. run a broad grid on 2024 construction data;
4. include at least one valid configuration for each top method family;
5. select the top 5 candidates by robust score.

## Required Compatibility Rules

Examples:

```text
DRO-BL-RP requires BL view/confidence storage and covariance/risk budget state.
BSA-RP requires belief state and risk budget state.
ARMOR-OMD requires base allocator performance state; retrieval index optional but preferred.
LEEQA-Rank requires rank feature panel.
KG-MoE-Lite requires knowledge graph or sector impact panel.
HGF-MPC requires Kalman drift or HMM regime state.
CEVA-KF/CIGA requires causal graph and stable effect state.
S1 can run with no text.
S0 can run with no text.
```

## Scoring Formula

Use a robust grid-search score:

```text
competition_score =
  0.30 * sharpe_rank_score
+ 0.20 * cumulative_return_rank_score
+ 0.20 * drawdown_rank_score
+ 0.15 * turnover_rank_score
+ 0.10 * parity_or_wrapper_score
+ 0.05 * simplicity_score

research_score =
  0.25 * method_novelty
+ 0.20 * interpretability
+ 0.20 * ablation_cleanliness
+ 0.15 * visualisability
+ 0.10 * reproducibility
+ 0.10 * report_signal

overall_score =
  0.55 * competition_score
+ 0.30 * research_score
+ 0.15 * robustness_score
```

Also compute a conservative final score:

```text
conservative_score =
  overall_score
- 0.10 * overfit_risk
- 0.08 * dependency_risk
- 0.08 * parity_risk
- 0.05 * implementation_complexity
```

## Required Outputs

Create:

```text
outputs/experiments/prompt15_grid_search/
outputs/reports/prompt15/grid_search_summary.md
outputs/reports/prompt15/grid_search_results.csv
outputs/reports/prompt15/top5_candidate_pipelines.md
```

Use this table for top 5:

| Rank | Pipeline Name | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Track | 2024 Sharpe | 2024 Return | Drawdown | Turnover | Competition Score | Research Score | Conservative Score | Promote? | Notes |
|---:|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|

## Critical Rule

Do not tune on 2025. Use 2025 only after selecting candidate families from 2024.

---

# Part F — 2025 Locked Evaluation for Top 5 Only

After selecting top 5 from 2024 construction data, run locked 2025 public A evaluation for those top 5 only.

Create:

```text
outputs/reports/prompt15/top5_2025_evaluation.md
outputs/reports/prompt15/top5_2025_evaluation.csv
```

Use:

| Rank | Pipeline Name | Track | 2024 Rank | 2025 Final Value | 2025 Return | 2025 Sharpe | 2025 Drawdown | 2025 Turnover | Generalisation | Promote? | Notes |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|---|

Generalisation values:

```text
strong
acceptable
weak
failed
not_run
```

Do not adjust parameters based on 2025.

---

# Part G — Wrapper-Based Validation and Parity

Run wrapper-based validation for the top candidates.

At minimum:

```text
S0 macro
S1 macro
S1 sector
best Track A candidate
best Track B candidate
top overall candidate
```

If official server runtime is too expensive, run short deterministic official parity windows and full local-wrapper backtests.

Create:

```text
outputs/reports/prompt15/wrapper_parity_validation.md
```

Use:

| Pipeline | Track | Date Range | Local Wrapper Value | Official Value | Abs Diff | Rel Diff | Trade Match? | Value Match? | Status | Notes |
|---|---|---|---:|---:|---:|---:|---|---|---|---|

Do not promote a final candidate if parity fails materially.

---

# Part H — Full Pipeline Evidence Pack

Create:

```text
outputs/reports/prompt15/final_system_evidence_pack.md
outputs/reports/prompt15/final_metrics_summary.csv
outputs/reports/prompt15/final_ablation_summary.md
outputs/reports/prompt15/final_decision_trace_examples.md
outputs/reports/prompt15/model_implementation_status.md
```

The evidence pack must include:

```text
implemented method list
stage-by-stage implementation status
Track A top 3
Track B top 3
overall top 5
2024 construction results
2025 locked evaluation results
wrapper/parity status
decision trace examples
Stage 1 local model usage
fallback behavior
known caveats
```

---

# Part I — Final Package Rebuild

Rebuild the candidate package after implementing all top methods and selecting top candidates.

Package should include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
configs/
requirements.txt or lock file
README / submission notes
minimal smoke runner if appropriate
```

Package should exclude:

```text
raw official data
NLPCC_tasks/dataset/
outputs/cache/
outputs/models/
models/
__pycache__
.pyc
large logs
notebooks unless explicitly needed
```

Do not include Hugging Face model files inside the default package unless explicitly required and documented.

Create:

```text
outputs/reports/prompt15/final_package_report.md
```

Use:

| Package Item | Required? | Included? | Status | Notes |
|---|---|---|---|---|

---

# Part J — Documentation Updates

Update docs honestly.

At minimum update:

```text
README.md
METHODOLOGY.md
docs/strategy/B_LIST_HARDENING.md
docs/architecture/OFFICIAL_COMPATIBILITY.md
docs/strategy/METHODOLOGY.md
```

Ensure documentation states:

```text
all seven top methods now have functional MVP code paths;
which methods are production candidates vs prototypes;
Stage 1 supports rule-based, FinBERT, BGE, and hybrid local text extraction;
Hugging Face models are local/offline and not required unless enabled;
Track A top 3 and selected default;
Track B top 3 and selected default;
overall top 5 pipelines;
parity status;
package status;
known caveats;
no 2025 tuning policy.
```

Create:

```text
outputs/reports/prompt15/documentation_update_report.md
```

Use:

| Document | Updated Claim | Evidence | Remaining Caveat |
|---|---|---|---|

---

# Part K — Final Recommendation

Create:

```text
outputs/reports/prompt15/final_recommendation.md
```

Use exactly:

```md
# Prompt15 Final Recommendation

## 1. Readiness Verdict

Choose one:

- Ready for dry-run submission
- Not ready, but close
- Not ready

## 2. Complete Pipeline Status

State whether all required methods have functional MVP implementations and whether the wrapper-based pipeline works.

## 3. Track A / Macro Top 3

| Rank | Candidate | Evidence | Risk | Action |
|---:|---|---|---|---|

## 4. Track B / Sector Top 3

| Rank | Candidate | Evidence | Risk | Action |
|---:|---|---|---|---|

## 5. Overall Top 5 Candidate Pipelines

| Rank | Pipeline | Track | Conservative Score | Action |
|---:|---|---|---:|---|

## 6. Final Default Candidates

- Track A default:
- Track A fallback:
- Track B default:
- Track B fallback:

## 7. Hugging Face / Local Model Decision

- BGE-small status:
- FinBERT Chinese status:
- Runtime default:
- Fallback:
- Packaging decision:

## 8. Official / Local Parity Status

- S0:
- S1:
- DRO-BL-RP / robust BL:
- BSA-RP:
- ARMOR-OMD:
- LEEQA-Rank:
- KG-MoE-Lite:
- HGF-MPC:
- CEVA-KF/CIGA:
- Track B sector systems:

## 9. Package Status

State whether the package includes all required runtime code and excludes prohibited artifacts.

## 10. Honest System Report Thesis

State the final thesis without overclaiming.

## 11. Remaining Fixes Before Actual Submission

Numbered list.

## 12. Recommended Prompt 16

Suggest the next prompt if still needed.
```

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt15_full_model_grid_search.md
```

Use:

```md
# Implementation Log: prompt15 - full_model_grid_search

## Created

<timestamp>

## Summary

## Files Changed

## Models Implemented

## Stage 1 Local Model Integration

## Grid Search

## Top 5 Pipelines

## 2025 Evaluation

## Wrapper / Parity Status

## Package Status

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

## Constraints

- Do not leave any of the seven top method families as pure stubs.
- Do not tune based on 2025 public A.
- Do not use current-day close/high/low/return before decision time.
- Do not modify raw official data.
- Do not include raw official data in packages.
- Do not include downloaded Hugging Face model files in the default package unless explicitly documented and allowed.
- Do not silently download models during default runtime.
- Do not make external API calls in final default execution.
- Do not overclaim full GNN/MoE if only KG-MoE-Lite is implemented.
- Do not overclaim causal discovery if CEVA-KF/CIGA is a stable-effect graph MVP.
- Do not overclaim full MPC if HGF-MPC is a one-step constrained controller.
- Do not overclaim OMD if ARMOR-OMD is an exponentiated-weight MVP.
- Prefer functional MVP + honest maturity label over grand but non-running code.
- If grid search is too large, use compatibility-filtered grid search and document coverage.

---

## Expected Final Assistant Response

After completing Prompt15, respond with:

1. readiness verdict;
2. list of all seven top methods and their implementation status;
3. Stage 1 BGE/FinBERT integration status;
4. Track A top 3;
5. Track B top 3;
6. overall top 5 pipelines;
7. 2025 evaluation summary;
8. official/local parity status;
9. package status;
10. files changed;
11. tests/checks run;
12. remaining blockers or Prompt16 objective.
