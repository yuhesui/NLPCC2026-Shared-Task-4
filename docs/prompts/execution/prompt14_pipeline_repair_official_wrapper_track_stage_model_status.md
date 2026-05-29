# Prompt 14 — Pipeline Repair, Official Wrapper Closure, Track Status Separation, and Optional Local Model Audit

## Role

You are a senior quantitative research engineer, competition submission architect, and LLM-systems reliability auditor.

You are working on the NLPCC 2026 Shared Task 4 repository after Prompt13 completed a full audit.

Your task is **not** to add new strategy families. Your task is to **repair the current pipelines**, close official-wrapper/parity blockers, clearly separate Track A vs Track B status, classify all four stages and all implemented/deferred models, and audit whether any local Hugging Face models should be downloaded for optional offline text processing.

This is a **repair, integration, and status-clarification prompt**.

---

## 0. Mandatory Context to Read First

Read the Prompt13 audit artifacts before making any code changes:

```text
outputs/reports/prompt13/full_audit_report.md
outputs/reports/prompt13/final_recommendation.md
outputs/reports/prompt13/official_local_parity_report.md
outputs/reports/prompt13/submission_wrapper_audit.md
outputs/reports/prompt13/stage1_trace_report.md
outputs/reports/prompt13/module_maturity_matrix.md
outputs/reports/prompt13/full_year_ablation_report.md
outputs/reports/prompt13/public_a_2025_evaluation_report.md
docs/implementation_logs/20260529_172513_prompt13_full_audit.md
```

Also inspect:

```text
AGENTS.md
README.md
METHODOLOGY.md
WORKFLOW.md
docs/REPO_STRUCTURE.md
docs/architecture/
docs/strategy/
configs/
src/nlpcc/
src/tools/
scripts/
tests/
NLPCC_tasks/
NLPCC_tasks/agent_platform/
NLPCC_tasks/agent_platform/agents/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/server_platform/
NLPCC_tasks/dataset/
outputs/submissions/
```

If some files are missing, record that explicitly and continue.

---

## 1. Prompt13 Findings to Treat as Ground Truth Unless the Repo Proves Otherwise

Prompt13 concluded that the repository is **not ready**.

Known blockers:

1. `NLPCC_tasks/agent_platform/agents/build_agent.py` is missing.
2. Official/local parity failed for S0, S1, and robust BL.
3. Official portfolio holdings expose holding value, while internal agents expect share-like holdings.
4. `official_adapter`, `order_planner`, and `system_runner` are missing or placeholders.
5. The prompt12 package lacked the official-facing wrapper.
6. Stage 1 is deterministic and rule-based by default; LLM extraction is not the default implemented path.
7. Track 1 robust BL is the strongest local candidate, but remains local-only until parity is repaired.
8. Track 2 should currently fall back to S1 sector because `sector_rotation_track2` does not beat S1 sector on 2024.
9. KG-MoE, causal graph, transformer memory, retrieval memory, HMM/Kalman/MPC, learning-to-rank, direct LLM allocator, deep RL, and graph RL should remain deferred/stub/rejected unless explicitly proven otherwise.

Do not reopen these conclusions unless the repo provides new evidence.

---

## 2. Official Constraints to Preserve

Preserve these task constraints:

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
- If using training, fine-tuning, retrieval, or knowledge construction, the full data, preprocessing, dependencies, and reproducible environment must be submitted.
- Creative or especially informative system reports may be selected even if not top-ranked.
- Raw official data must not be modified or redistributed.
- Final execution must have a no-API deterministic fallback.

---

## 3. Main Objective

Repair the repository so that it has a clean, auditable, official-compatible execution path:

```text
Official daily input
→ official-facing build_agent.py wrapper
→ runtime system runner
→ Stage 1 news processing
→ Stage 2 text state
→ Stage 3 trade state
→ Stage 4 final agent
→ target weights
→ official adapter / order planner
→ official buy amount + sell percentage trades
→ decision trace and fallback logs
```

Then rerun official/local parity until at least S0 and S1 match server semantics closely enough to trust the local backtester.

---

## 4. Required Deliverables

Create or update these reports:

```text
docs/implementation_logs/<timestamp>_prompt14_pipeline_repair.md

outputs/reports/prompt14/pipeline_repair_report.md
outputs/reports/prompt14/track_status_matrix.md
outputs/reports/prompt14/stage_status_matrix.md
outputs/reports/prompt14/model_status_matrix.md
outputs/reports/prompt14/official_wrapper_repair_report.md
outputs/reports/prompt14/official_local_parity_rerun_report.md
outputs/reports/prompt14/huggingface_model_audit.md
outputs/reports/prompt14/package_rebuild_report.md
outputs/reports/prompt14/final_recommendation.md
```

If a report cannot be fully completed, create it anyway and mark blockers clearly.

---

## Part A — Fix the Official-Facing Wrapper

Create or repair:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
```

If the repo already has a different official-facing wrapper, either:

1. make `build_agent.py` import and expose that wrapper, or
2. explain why a different path is required and update all docs/configs accordingly.

The wrapper must:

1. import the reusable implementation from `src/nlpcc/`;
2. load a frozen config from `configs/`;
3. support Track A / macro and Track B / sector;
4. select the default strategy per track;
5. select a safe fallback per track;
6. receive official daily data / portfolio state;
7. convert official portfolio fields into the internal schema correctly;
8. run the modular system;
9. convert target weights into official trade instructions;
10. return server-compatible buy/sell instructions;
11. record a decision trace if possible;
12. catch exceptions and fall back to S1 or conservative fallback;
13. avoid external API dependency by default.

Default strategy policy unless the repo has stronger evidence:

```text
Track A / macro:
  primary: robust_bl_track1
  fallback: oco_fallback_macro or s1_macro

Track B / sector:
  primary: s1_sector
  experimental: sector_rotation_track2
  fallback: s1_sector
```

Do not promote `sector_rotation_track2` as the default Track B candidate unless new evidence shows it beats S1 sector robustly.

Required tests:

```text
build_agent.py imports successfully
build_agent.py can select macro config
build_agent.py can select sector config
wrapper falls back on internal exception
wrapper does not require external APIs by default
wrapper emits official-compatible trades
```

---

## Part B — Fix Portfolio State Conversion

Prompt13 found that official portfolio holdings expose holding value, while internal agents expect share-like holdings. This caused official/local parity failure.

Implement or repair a robust portfolio-state adapter, using current repo conventions.

Possible paths:

```text
src/nlpcc/execution/official_adapter.py
src/nlpcc/execution/portfolio_state_adapter.py
src/nlpcc/execution/order_planner.py
```

The adapter must correctly convert official portfolio state into internal state:

```text
official holdings
official cash
official fund universe
current open / previous close / available execution price
internal asset values
internal weights
internal cash
internal tradable universe
```

Be explicit about whether the internal state uses:

```text
shares
holding value
weight
cash amount
```

Do not mix these silently.

Include in `official_wrapper_repair_report.md`:

| Field | Official Meaning | Internal Meaning | Conversion Rule | Tested? | Notes |
|---|---|---|---|---|---|

---

## Part C — Fix Target-Weight to Official Trade Conversion

Implement or repair the order planner.

The planner should convert target weights into official server trades:

```text
buy:
  amount in available cash

sell:
  percentage of current holding
```

Critical rule: do **not** assume same-day sell proceeds can be used for same-day buys.

The planner should:

1. compute sells from current holdings;
2. compute buys using current available cash only;
3. avoid overspending;
4. apply turnover caps;
5. respect per-asset max weights;
6. handle tiny residuals;
7. avoid invalid sell percentages;
8. validate all trades before submission;
9. log rejected or clipped intended trades.

Required tests:

```text
buy uses only available cash
sell uses percentage of current holding
same-day sell proceeds are not used for buys
max weight is respected
turnover cap is respected
zero/empty holdings do not crash
invalid trades are rejected before server submission
```

---

## Part D — Fix Runtime System Runner

Implement or repair the runtime system runner.

Possible path:

```text
src/nlpcc/runtime/system_runner.py
```

The runner should be the single path used by both local backtests and official wrapper.

The system runner should orchestrate:

```text
Stage 1 news processing
Stage 2 text storage
Stage 3 trade processing
Stage 4 agent decision
execution adapter
fallback manager
decision trace
dependency guard
```

It should return:

```text
target_weights
official_trades
decision_trace
fallback_status
stage_outputs_summary
```

Keep the runner modular:

```text
SystemRunner
  run_day(input) -> SystemDecision
```

Do not hard-code strategy logic inside the wrapper.

---

## Part E — Separate Track A vs Track B Status Clearly

Create:

```text
outputs/reports/prompt14/track_status_matrix.md
```

Use this table:

| Track | Current Default | Best Local Candidate | Fallback | 2024 Evidence | 2025 Evidence | Official Parity | Submission Status | Next Required Fix |
|---|---|---|---|---|---|---|---|---|
| Track A / Macro | | | | | | | | |
| Track B / Sector | | | | | | | | |

Expected starting point:

```text
Track A:
  best local candidate = robust_bl_track1
  fallback = oco_fallback_macro or s1_macro
  blocker = official parity/wrapper

Track B:
  best safe candidate = s1_sector
  experimental = sector_rotation_track2
  blocker = sector_rotation does not beat S1 sector and wrapper/parity must be fixed
```

---

## Part F — Separate All Four Stage Statuses Clearly

Create:

```text
outputs/reports/prompt14/stage_status_matrix.md
```

Use this table:

| Stage | Implemented Components | Missing / Placeholder Components | Used by Track A? | Used by Track B? | Tests | Maturity | Main Risk | Required Fix |
|---|---|---|---|---|---|---|---|---|

Stages:

```text
Stage 1 — News Processing
Stage 2 — Quantified Text Storage
Stage 3 — Trade Data Processing
Stage 4 — Final Trading Agent
Execution / Adapter Layer
Runtime / Fallback Layer
Tools / Experiments / Reporting
```

Be explicit that:

- Stage 1 default path is deterministic/rule-based unless LLM is actually wired.
- Stage 2 includes real BL view/confidence structures but retrieval/KG/causal components may be stubs.
- Stage 3 is comparatively mature.
- Stage 4 has production candidates and prototypes.
- Execution/adapters are the critical repair area.

---

## Part G — Separate All Model / Method Statuses Clearly

Create:

```text
outputs/reports/prompt14/model_status_matrix.md
```

Use this table:

| Model / Method | Track A Status | Track B Status | Stage(s) | Code Path | Config Path | Maturity | Evidence | Default? | Claim Allowed? | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|

Include at least:

```text
S0 equal weight
S1 quant core
inverse volatility
momentum
sector trend-following
risk parity
robust Black-Litterman
belief-state risk parity
HMM / Kalman / MPC
sector impact model
KG-MoE-Lite
retrieval analogue memory
transformer-style event memory
OCO / online mirror descent ensemble
learning-to-rank
causal/invariant event-impact model
rule-based news extraction
LLM event extraction
no-LLM fallback
generic RAG summariser
pure LLM direct allocator
deep RL / graph RL
```

Use maturity values:

```text
production_candidate
working_prototype
debug_only
research_stub
documented_only
rejected
missing
```

Do not overstate maturity.

---

## Part H — Hugging Face / Local Model Audit

## Purpose

Decide whether the repo should download any local Hugging Face models for optional offline text processing.

This is an audit and optional preparation step. Do **not** make the final system dependent on a model download unless the model is small, pre-2026, license-compatible, reproducible, and has a no-model fallback.

Candidate model categories:

```text
Chinese financial sentiment classification
Chinese general text classification / encoding
multilingual or Chinese embedding retrieval
financial text embedding
reranking
keyword/entity extraction
```

Possible candidates to audit include, but are not limited to:

```text
yiyanghkust/finbert-tone-chinese
hfl/chinese-roberta-wwm-ext
hfl/chinese-roberta-wwm-ext-large
BAAI/bge-m3
BAAI/bge-small-zh-v1.5 or related BGE Chinese embedding models if available
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
FinBERT-style English models only if they are useful for translated/English news, otherwise deprioritise
```

Before downloading anything, verify:

```text
model release / update date is before 2026
license allows intended academic use
model size is manageable
model can run offline
model can be pinned by revision hash
dependencies are acceptable
model is useful for Chinese financial news
model has a deterministic no-model fallback
```

Create:

```text
outputs/reports/prompt14/huggingface_model_audit.md
```

Use this table:

| Candidate Model | Task | Language | Pre-2026 Available? | Size / Runtime Risk | License Risk | Useful For | Download? | Runtime Default? | Fallback | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

Download policy: only download a model if all are true:

```text
1. It is clearly available before 2026.
2. It has a compatible license or at least no obvious academic-use blocker.
3. It is not required for the default final agent.
4. It is saved outside raw official data directories.
5. It is recorded with model name, revision hash, date, and checksum if possible.
6. The system can run without it.
```

Recommended local storage if downloaded:

```text
models/huggingface/<model_name_sanitized>/
```

or:

```text
outputs/models/huggingface/<model_name_sanitized>/
```

Do **not** store downloaded models under:

```text
NLPCC_tasks/dataset/
docs/
src/
```

If a local model is used, add or verify config flags:

```yaml
text_model:
  enabled: false
  provider: local_huggingface
  model_name: null
  local_path: null
  revision: null
  offline_only: true
  fallback: rule_based
```

Default should remain:

```yaml
enabled: false
fallback: rule_based
```

unless explicitly justified.

---

## Part I — Rerun Official / Local Parity After Repairs

After wrapper, portfolio adapter, order planner, and system runner are repaired, rerun parity.

Use the same short deterministic 2024 span from Prompt13:

```text
2024-01-02 to 2024-01-31
```

Run at least:

```text
s0_equal_weight_macro
s1_macro
robust_bl_track1
```

If Track B official pathway is easy to test, also run:

```text
s1_sector
sector_rotation_track2
```

Create:

```text
outputs/reports/prompt14/official_local_parity_rerun_report.md
```

Use:

| Strategy | Track | Date Range | Local Final Value | Official Final Value | Abs Diff | Rel Diff | Metric Match? | Trade Match? | Status | Notes |
|---|---|---|---:|---:|---:|---:|---|---|---|---|

Status values:

```text
pass
minor_diff
fail
blocked
not_run
```

Pass criteria:

```text
S0 macro and S1 macro should pass or have only small explainable differences.
```

Robust BL should not be trusted until S0/S1 parity is fixed.

If parity still fails:

1. do not tune models;
2. inspect trade conversion and portfolio-state conversion;
3. write exact remaining mismatch;
4. recommend another repair prompt.

---

## Part J — Rebuild Submission Package

After repairs, rebuild a candidate package.

The package must include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
configs/
requirements.txt or dependency file
README or submission notes
minimal smoke script if allowed
```

The package must not include:

```text
raw official data
NLPCC_tasks/dataset/
outputs/cache/
__pycache__/
.pyc
large downloaded models unless explicitly intended and documented
```

If local Hugging Face models are downloaded, do **not** include them in the default package unless explicitly required and allowed. Instead, include a documented download script or manifest if needed.

Create:

```text
outputs/reports/prompt14/package_rebuild_report.md
```

Use:

| Package Item | Required? | Included? | Status | Notes |
|---|---|---|---|---|

---

## Part K — Documentation Fixes

Update docs to match actual status.

At minimum, fix claims about:

```text
build_agent.py wrapper
official_adapter
order_planner
system_runner
official/local parity
Stage 1 LLM extraction
OCO maturity
vectorized / CUDA backtester maturity
KG-MoE / causal / retrieval / transformer memory status
Track A vs Track B default candidates
Hugging Face model usage
```

Do not rewrite the entire documentation pack. Make targeted edits.

Summarise doc edits in:

```text
outputs/reports/prompt14/pipeline_repair_report.md
```

Use:

| Document | Edit Made | Reason | Remaining Caveat |
|---|---|---|---|

---

## Part L — Final Recommendation

Create:

```text
outputs/reports/prompt14/final_recommendation.md
```

Use exactly this structure:

```md
# Prompt14 Final Recommendation

## 1. Readiness Verdict

Choose one:

- Ready for dry-run submission
- Not ready, but close
- Not ready

## 2. Track A / Macro Status

- Default candidate:
- Fallback:
- Evidence:
- Remaining blockers:

## 3. Track B / Sector Status

- Default candidate:
- Experimental candidate:
- Fallback:
- Evidence:
- Remaining blockers:

## 4. Stage Status Summary

| Stage | Status | Main Fix Completed | Remaining Risk |
|---|---|---|---|

## 5. Model / Method Status Summary

| Method Group | Promote | Fallback | Ablation Only | Reject / Defer |
|---|---|---|---|---|

## 6. Official Parity Status

State whether S0/S1 parity now passes.

## 7. Hugging Face / Local Model Decision

State whether any models were downloaded or recommended.

## 8. Package Status

State whether the rebuilt package includes the official wrapper and required runtime files.

## 9. Required Fixes Before Final Submission

Numbered list.

## 10. Recommended Next Prompt

Suggest the next prompt title and objective.
```

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt14_pipeline_repair.md
```

Use:

```md
# Implementation Log: prompt14 - pipeline_repair

## Created

<timestamp>

## Summary

<what was repaired>

## Files Changed

<list>

## Tests / Checks

<commands and results>

## Track A Status

<summary>

## Track B Status

<summary>

## Stage Status

<summary>

## Model Status

<summary>

## Hugging Face / Local Model Audit

<summary>

## Key Findings

<bullet list>

## Caveats

<remaining blockers>

## Artifacts

<report paths>

## Next Steps

<recommended next prompt>
```

---

## Constraints

- Do not implement new strategy families.
- Do not tune based on 2025.
- Do not make the default final agent dependent on Hugging Face downloads.
- Do not use any 2026-or-later model/data/information in the runtime system.
- Do not modify raw official data.
- Do not include official raw data in submission packages.
- Do not include caches or large models in the package unless explicitly documented and allowed.
- Do not overclaim LLM extraction if default Stage 1 remains rule-based.
- Do not overclaim OCO if there is no persistent online update state.
- Do not overclaim KG-MoE, causal, retrieval, transformer memory, HMM/Kalman/MPC, learning-to-rank, deep RL, or graph RL if they remain stubs.
- Fix wrapper, adapter, order planner, and parity before adding model complexity.
- If official server is unavailable, mark parity as blocked rather than fabricating results.
- If parity still fails, stop and explain the exact mismatch.

---

## Expected Final Assistant Response

After completing Prompt14, respond with:

1. readiness verdict;
2. Track A status;
3. Track B status;
4. official parity status;
5. wrapper/adapter repair status;
6. Hugging Face/local model decision;
7. package status;
8. files changed;
9. tests run;
10. next recommended prompt.
