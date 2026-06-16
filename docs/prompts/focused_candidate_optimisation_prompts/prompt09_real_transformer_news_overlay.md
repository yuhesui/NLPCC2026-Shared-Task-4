# Prompt09 — Production Real-Transformer News Overlay, No-Proxy Port, and Official-Agent Verification

## Role

You are GPT-5.5 ExtraHigh Thinking in a **fresh Codex session**.

Act as:

```text
senior transformer NLP production engineer
Chinese financial NLP engineer
official trading-agent integration engineer
portfolio risk-control engineer
model-provenance auditor
server-run validation engineer
single implementation-log writer
```

This is a strict implementation and verification phase.

Your job is to implement and verify **production real-NLP transformer news overlay** for the top candidates.

You must remove / disable proxy and heuristic news fallbacks for the production path.

If real local transformer assets are missing, the run must fail closed as:

```text
blocked_missing_local_model
```

Do **not** silently fall back to lexical, deterministic, proxy, fake tensor, fixed CSV target replay, or old research target-weight tables.

---

## Core Objective

Implement and verify a real transformer-style continuous tensor news overlay.

The implementation must:

```text
1. read the docs/news_overlay architecture documents;
2. map the intended N/I/S transformer architecture to the current top candidates;
3. verify whether the transformer architecture was ported into the official trading-agent path;
4. port it if missing;
5. use real local transformer inference only;
6. produce continuous tensor news features, not discrete-only sentiment;
7. run official local server/platform validation;
8. prove the news tensor is actually used through ablation;
9. provide analysis-ready CSVs under presented/run_csv/.
```

This phase is **not** about improving heuristic fallback performance.  
This phase is **not** about synthetic-only results.  
This phase is **not** about packaging/env cleanup.  
This phase is **not** about broad candidate search.

---

## Phase

Use this exact phase name:

```text
Prompt09 — Production Real-Transformer News Overlay
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt09_real_transformer_news_overlay/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
server_run/
model_audit/
news_audit/
features/
configs/
ablations/
tests/
runner_port/
```

All important result CSVs must be copied to:

```text
presented/run_csv/
```

---

## One Implementation Log Only

Write exactly one Prompt09 implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt09_real_transformer_news_overlay/presented/implementation_log.md
```

Do not write:

```text
docs/implementation_logs/*
any other Prompt09 implementation_log.md
```

If this file exists, update it in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt09_logs_created = false
```

---

## Required Context to Read First

Read the repository docs and tables before changing code.

Required docs/files to inspect:

```text
docs/news_overlay/**
docs/NLPCC2026 - Template/**
AGENTS.md
README.md
NLPCC_tasks/**
outputs/reports/news_overlay/prompt21/**
outputs/reports/news_overlay/prompt22/**
outputs/reports/focused_candidate_optimisation/prompt07_official_server_main_pipeline/**
outputs/reports/focused_candidate_optimisation/prompt08_transformer_news_tensor_enhancement/**
```

Also read these project reference tables if present:

```text
docs/news_overlay/transformer_architecture_table.md
docs/news_overlay/grid_search_table.md
transformer_architecture_table.md
grid_search_table.md
```

Use these architecture mappings as starting targets:

```text
Track A production base:
  A0 = G00A = no-news reference

Track A real transformer candidates:
  A2 = G11A = N13 / I6 / S13
  A1 = G12A = N2345 / I256 / S13

Track B production base:
  B0 = G00B = no-news reference

Track B real transformer candidates:
  B2 = G15B = N4 / I6 / S2
  B3 = G21B = N2345 / I256 / S5
```

Important architecture meanings:

```text
N2 = BGE / sentence-transformer bi-encoder relevance
N3/N13 = FinBERT-style aspect-tone classifier / aspect conditioning
N4 = label-attention / Title2Event-inspired event tagger
N5 = sector-query attention pooling
N6 = cross-encoder sector reranker
I6/I256 = transformer aspect-impact aggregation / composite impact
S2/S5/S13 = bounded score-to-overlay sensitivity / rank/BL/macro controls
```

Required comparison rule:

```text
A candidates G10A/G11A/G12A must compare against lexical/control G01A and no-news G00A.
B candidates G10B/G11B/G12B/G13B/G14B/G15B/G21B must compare against lexical/control G01B and no-news G00B.
```

---

## Non-Negotiable No-Proxy Rule

For Prompt09 production transformer path:

```text
proxy_mode = false
heuristic_news_fallback = false
deterministic_tone_proxy = false
lexical_event_fallback = false
fixed_target_csv_replay_as_news = false
old_research_weight_table_as_news = false
```

Allowed fallback behavior:

```text
If a local transformer model is missing:
  stop that candidate;
  emit blocked_missing_local_model;
  do not produce a fake candidate result.

If dependency missing:
  emit blocked_missing_dependency;
  do not produce fake candidate result.

If official adapter cannot call the transformer path:
  emit blocked_transformer_not_ported_to_official_agent;
  do not replay old targets.

If news file missing for a date:
  produce neutral zero tensor for that date only, with missing_news flag.
  This is not a model fallback.
```

Every result row must state:

```text
real_transformer_executed
proxy_mode
heuristic_fallback_used
blocked_reason
```

---

## Approved Local Model Assets

Use only local model assets already present on disk or in pinned HF cache.

Likely approved assets from prior phases:

```text
BAAI/bge-small-zh-v1.5
yiyanghkust/finbert-tone-chinese or equivalent local FinBERT classifier
BAAI/bge-reranker-v2-m3 if already cached
```

Rules:

```text
local_files_only = true
network_attempted = false
model_path must be recorded
model_sha_or_snapshot must be recorded if available
tokenizer_path must be recorded
device must be recorded: cuda/cpu
batch_size must be recorded
cache_key must include model id, snapshot, config hash, and input hash
```

If a model is absent, do not download in this prompt unless a local approved snapshot path already exists. Mark blocked.

---

## Stage 0 — Entrypoint and Prior Status Audit

Create a precise inventory of where the current code stands.

Required checks:

```text
1. Which docs/news_overlay architecture files exist?
2. Which N/I/S modules are implemented in src/?
3. Which modules use real model inference?
4. Which modules still allow proxy/heuristic fallback?
5. Which modules are currently used by A2/B2/A1/B3?
6. Which official trading-agent path is used?
7. Does the official trading-agent adapter call real transformer code?
8. Does any official server path replay frozen target CSVs instead of recomputing news?
```

Required outputs:

```text
news_audit/current_transformer_architecture_audit.csv
news_audit/current_proxy_fallback_inventory.csv
news_audit/current_official_agent_port_audit.csv
presented/current_real_nlp_status_summary.md
```

`current_proxy_fallback_inventory.csv` columns:

```text
file_path
function_or_class
fallback_type
candidate_affected
production_path_affected
must_remove_or_disable
safe_replacement
status
```

`current_official_agent_port_audit.csv` columns:

```text
candidate_id
track
official_agent_path
calls_real_transformer
replays_old_targets
uses_proxy
uses_heuristic
model_load_evidenced
news_tensor_evidenced
status
```

---

## Stage 1 — Model Asset Verification

Before implementing the overlay, prove local model assets.

Run local-only checks for all needed components:

```text
BGE encoder for N2/N5 relevance and embeddings
FinBERT/aspect-tone classifier for N3/N13/I6
Label-attention encoder/classifier for N4
Reranker N6 only if present and needed
```

Required outputs:

```text
model_audit/local_model_asset_manifest.csv
model_audit/model_load_smoke_results.csv
model_audit/model_inference_sample_outputs.csv
model_audit/model_cache_identity.csv
presented/model_asset_verification_summary.md
```

Each model row:

```text
model_role
required_for_methods
local_path
exists
local_files_only
network_attempted
loaded_successfully
device
dtype
sample_input_count
sample_output_shape
sample_output_hash
proxy_used
blocked_reason
```

Pass rule:

```text
For a candidate to run as real-transformer:
  all required model roles for its N/I/S path must be loaded or explicitly not required.
  proxy_used must be false.
```

---

## Stage 2 — Implement Real Continuous Transformer News Tensor

Implement the real tensor feature layer.

Target API:

```text
RealTransformerNewsTensorProvider.build(date, news_items, track, candidate_config) -> NewsTensorBatch
```

The tensor must be continuous-valued.

Minimum fields:

```text
embedding_vector
asset_or_sector_relevance
sentiment_score_continuous
sentiment_confidence
sentiment_entropy
aspect_scores
event_label_scores
event_confidence
sector_attention_weights
recency_decay_weight
source_or_cluster_support
novelty_score
uncertainty_score
```

For classifier logits:

```text
sentiment_score = p_positive - p_negative
confidence = max(p_positive, p_neutral, p_negative)
entropy = -sum(p_i log p_i)
intensity = abs(sentiment_score) * confidence
```

No final discrete-only sentiment is allowed.

Required outputs:

```text
features/real_news_tensor_schema.yaml
features/real_news_tensor_build_manifest.csv
features/real_news_tensor_daily_stats.csv
features/real_news_tensor_sample_rows.csv
features/real_news_tensor_cache_manifest.csv
presented/real_news_tensor_feature_summary.md
```

Required manifest columns:

```text
date
track
candidate_id
news_count
model_roles_used
real_transformer_executed
proxy_mode
heuristic_fallback_used
embedding_shape
tensor_shape
cache_hit
cache_key
missing_news
blocked_reason
```

---

## Stage 3 — Disable Production Proxy / Heuristic Backup

Do not delete research fallback code if it is needed for old tests.  
Instead create explicit production-mode guards.

Production mode must enforce:

```text
production_real_nlp = true
allow_proxy_news = false
allow_heuristic_news = false
allow_fixed_target_replay = false
allow_old_research_table_replay = false
```

Any attempt to use proxy in production mode must raise or emit:

```text
blocked_proxy_forbidden_in_production_real_nlp
```

Required outputs:

```text
reference/production_no_proxy_policy.yaml
reference/no_proxy_guard_test_results.csv
presented/no_proxy_policy_summary.md
```

Add or update tests proving:

```text
missing local model -> blocked, not proxy
disabled model path -> blocked, not proxy
heuristic fallback attempted -> blocked
fixed target replay attempted -> blocked
proxy_mode true row cannot become production candidate
```

---

## Stage 4 — Port Real Transformer Overlay to Official Trading Agent

Port the real transformer tensor path into the official trading-agent/server path.

Likely official paths:

```text
NLPCC_tasks/agent_platform/agents/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/server_platform/
NLPCC_tasks/start_server.py
runner/
runners/
```

Required behavior:

```text
official agent receives daily visible news;
official agent builds real transformer tensor online/local-only;
official agent computes bounded news overlay;
official agent outputs target weights;
official agent logs model hash, news tensor hash, output weight hash;
official agent refuses proxy mode;
official agent refuses hidden 2026;
official agent does not replay old target CSVs as news.
```

Required outputs:

```text
runner_port/real_transformer_agent_port_manifest.csv
runner_port/official_agent_source_diff_summary.md
runner_port/official_agent_real_nlp_trace_sample.csv
presented/official_agent_real_nlp_port_summary.md
```

`real_transformer_agent_port_manifest.csv` columns:

```text
candidate_id
track
official_agent_path
config_path
calls_real_news_tensor_provider
uses_fixed_target_replay
proxy_forbidden
model_load_at_runtime
news_tensor_hash_logged
output_weight_hash_logged
status
```

If the official agent cannot support live transformer inference due to runtime constraints, mark:

```text
blocked_transformer_not_ported_to_official_agent
```

Do not fake it with replayed weights.

---

## Stage 5 — Candidate Configs

Create production-real-NLP configs.

Minimum candidates:

```text
A0 no-news base
A2_real = G11A real N13/I6/S13
B0 no-news base
B2_real = G15B real N4/I6/S2
```

Optional if primary passes:

```text
A1_real = G12A real N2345/I256/S13
B3_real = G21B real N2345/I256/S5
```

Required outputs:

```text
configs/A2_real_transformer.yaml
configs/B2_real_transformer.yaml
configs/production_real_nlp_candidate_manifest.csv
presented/production_candidate_config_summary.md
```

Config must include:

```text
production_real_nlp: true
allow_proxy_news: false
allow_heuristic_news: false
local_files_only: true
required_model_roles
overlay_cap
turnover_cap
confidence_gate
deadband
drawdown_guard
```

---

## Stage 6 — Real Transformer Official Server Runs

Run the candidates through the local official server/platform path.

Minimum run set:

```text
A0
A2_real
B0
B2_real
```

Optional after primary passes:

```text
A1_real
B3_real
```

Run on public 2025 local official-server replay.

Required outputs:

```text
reference/official_server_real_transformer_results_prompt09.csv
reference/official_server_real_transformer_metric_comparison_prompt09.csv
presented/run_csv/official_server_real_transformer_results_prompt09.csv
presented/run_csv/official_server_real_transformer_metric_comparison_prompt09.csv
presented/official_server_real_transformer_summary.md
traces/official_server_real_<track>_<candidate_id>_daily.csv
logs/official_server_real_<track>_<candidate_id>.log
```

Each result row:

```text
track
candidate_id
candidate
method_stack
server_entrypoint
official_agent_path
config_hash
date_start
date_end
num_days
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero_days
real_transformer_executed
model_roles_executed
proxy_mode
heuristic_fallback_used
fixed_target_replay_used
network_attempted
local_files_only
news_tensor_hash_count
delta_vs_no_news_sharpe
delta_vs_no_news_return
actual_official_server_or_platform_run
official_submission_run
status
blocked_reason
notes
```

Do not mark a row as `complete` if real transformer execution did not happen.

---

## Stage 7 — Ablation: Active vs Zeroed vs Shuffled Real Tensor

Run ablations for each real candidate that completes:

```text
active_real_tensor
zeroed_tensor
date_shuffled_tensor
model_disabled_should_block
proxy_enabled_should_block
```

Required outputs:

```text
ablations/real_transformer_news_use_ablation.csv
ablations/real_tensor_zeroed_vs_active.csv
ablations/real_tensor_shuffled_vs_active.csv
presented/run_csv/real_transformer_news_use_ablation.csv
presented/real_transformer_ablation_summary.md
```

Required ablation columns:

```text
candidate_id
track
ablation_type
real_transformer_executed
news_tensor_active
news_tensor_zeroed
news_tensor_shuffled
model_disabled
proxy_attempted
proxy_blocked
return
sharpe
turnover
mean_abs_overlay
overlay_nonzero_days
delta_active_minus_zeroed_sharpe
delta_active_minus_shuffled_sharpe
shuffled_beats_active
leakage_suspected
actual_run
proxy_run
blocked_reason
notes
```

Interpretation:

```text
Active should beat or explain failure relative to zeroed.
Active should not lose clearly to shuffled if claiming real news value.
If shuffled beats active, do not promote.
If model_disabled does not block, production no-proxy guard failed.
If proxy_attempted is not blocked, production no-proxy guard failed.
```

---

## Stage 8 — Tests

Run tests relevant to real transformer production mode.

Required:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Also add/run targeted tests if safe:

```text
test_real_transformer_model_load
test_no_proxy_guard
test_official_agent_real_nlp_path
test_news_tensor_shape_and_cache
test_model_disabled_blocks
test_proxy_attempt_blocks
test_no_fixed_target_replay
```

Do not run:

```text
pip check
compileall
package build
LaTeX finalization
```

Required outputs:

```text
tests/test_command_manifest.csv
tests/test_results_summary.csv
presented/full_test_summary.md
logs/news_overlay_pytest.log
logs/full_pytest_tests_nlpcc.log
logs/full_pytest_tests.log
logs/real_transformer_targeted_tests.log
```

---

## Stage 9 — Decision and Submission Gap

Create final decision files:

```text
reference/final_prompt09_real_transformer_decision_table.csv
reference/final_prompt09_candidate_synthesis.csv
presented/run_csv/final_prompt09_real_transformer_decision_table.csv
presented/final_candidate_decision_summary.md
presented/production_real_nlp_readiness_assessment.md
presented/submission_gap_summary.md
presented/final_next_phase_recommendation.md
```

Decision statuses:

```text
production_safe_base
real_transformer_candidate
real_transformer_bounded_overlay_candidate
research_only_transformer
blocked_missing_local_model
blocked_missing_dependency
blocked_proxy_forbidden
blocked_transformer_not_ported_to_official_agent
rejected_shuffled_news_beats_active
rejected_no_material_news_use
```

Required decision questions:

```text
Did A2_real and B2_real run real transformer inference?
Was proxy/heuristic fallback fully disabled?
Was the transformer architecture ported to the official trading agent?
Did official server run use real news tensor rather than replayed targets?
Did active real tensor beat zeroed and shuffled?
Does any real transformer candidate justify production overlay?
Should final submission use A0/B0 only or A0/B0 plus real transformer overlay?
```

Do not use:

```text
submission_ready
official_promotion_ready
top3_ready
```

unless supported by real transformer server results, ablation, tests, and final package checks.

---

## Stage 10 — Presented CSV Package

Create:

```text
presented/run_csv_index.md
presented/run_csv_manifest.csv
```

Minimum files in `presented/run_csv/`:

```text
official_server_real_transformer_results_prompt09.csv
official_server_real_transformer_metric_comparison_prompt09.csv
real_transformer_news_use_ablation.csv
final_prompt09_real_transformer_decision_table.csv
test_results_summary.csv
```

Manifest columns:

```text
csv_path
row_count
candidate_ids
method_stacks
track_coverage
actual_run
proxy_run
real_transformer_executed
official_server_or_platform_run
why_it_matters
```

---

## Implementation Log Sections

The single implementation log must include:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Architecture Docs Read
G. Prior Proxy/Fallback Audit
H. Local Model Asset Verification
I. Real Transformer News Tensor Implementation
J. Production No-Proxy Guard
K. Official Trading-Agent Port
L. Official Server Real-Transformer Runs
M. Ablation Results
N. Tests
O. Presented CSV Package
P. Failed or Blocked Runs
Q. Official Runtime Status
R. Hidden 2026 / Leakage Check
S. Artifacts
T. Caveats
U. Next Steps
```

Every command entry:

```text
command
return_code
duration_seconds
log_path
```

Every source change:

```text
path
why modified
safety classification
rollback path
```

---

## Final Response Format

Use this exact structure:

```text
Prompt09 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Architecture docs read:
  <list>

Proxy/heuristic status before:
  <summary>

Local model assets:
  status: <complete/partial/blocked>
  models loaded:
    <list>
  blocked models:
    <list>
  network attempted:
    <yes/no>

Production no-proxy guard:
  status: <pass/partial/fail>
  proxy attempt blocked:
    <yes/no>
  disabled model blocked:
    <yes/no>

Real news tensor:
  status: <implemented/partial/blocked>
  tensor schema: <path>

Official trading-agent port:
  status: <complete/partial/blocked>
  path: <path>
  replays old targets:
    <yes/no>

Official server real-transformer run:
  status: <complete/partial/fail/blocked>
  rows: <n>
  csv:
    presented/run_csv/official_server_real_transformer_results_prompt09.csv

Ablation:
  status: <complete/partial/fail>
  active beats zeroed:
    Track A: <yes/no/mixed/not_run>
    Track B: <yes/no/mixed/not_run>
  active beats shuffled:
    Track A: <yes/no/mixed/not_run>
    Track B: <yes/no/mixed/not_run>

Best production-safe base:
  Track A: A0 G00A
  Track B: B0 G00B

Best real-transformer overlay:
  Track A: <candidate/none/blocked>
  Track B: <candidate/none/blocked>

Decision:
  <A0/B0 only | A0/B0 + real transformer overlay | research_only | blocked>

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  targeted real-transformer tests: <pass/fail/not_run>

Skipped by design:
  pip check
  compileall
  package build
  LaTeX finalization

Official submission run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
