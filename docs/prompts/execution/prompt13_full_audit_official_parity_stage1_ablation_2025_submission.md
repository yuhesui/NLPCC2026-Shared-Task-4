# Prompt 13 — Full Audit: Official Parity, Stage 1 Trace, Ablations, 2025 Evaluation, and Submission Readiness

## Role

You are a senior quantitative research engineering auditor, LLM-systems architect, and shared-task submission reviewer.

You are auditing the current NLPCC 2026 Shared Task 4 repository after multiple implementation phases have already been completed.

This is a **verification-heavy audit task**, not a new feature-building task.

Your objective is to determine whether the current repository is ready to be treated as a serious candidate submission, and if not, exactly what must be fixed before proceeding.

---

## Project Context

This repository is for **NLPCC 2026 Shared Task 4: LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market**.

The project targets:

1. **Track 1 — Macro-Asset Allocation**
2. **Track 2 — Sector-Rotation Allocation**

The intended architecture is a four-stage modular system:

```text
Stage 1 — News Processing
Stage 2 — Quantified Text Data Storage Medium
Stage 3 — Trade Data Processing
Stage 4 — Final Trading Agent
```

The current repository policy is:

```text
Official-facing submitted agent:
  NLPCC_tasks/agent_platform/agents/build_agent.py
  or the actual official-compatible wrapper currently used in the repo

Reusable implementation:
  src/nlpcc/

Configuration:
  configs/

Tools:
  src/tools/

Tests:
  tests/

Docs:
  docs/

Prompts:
  docs/prompts/

Generated outputs:
  outputs/
```

Note: earlier planning docs may refer to `src/nlpcc4/`, but the implemented package appears to use `src/nlpcc/`. Treat `src/nlpcc/` as the current implementation package unless the repo proves otherwise. Update documentation references if necessary.

---

## Official Constraints to Preserve

Preserve and audit against the following task constraints:

- Track 1 is Macro-Asset Allocation.
- Track 2 is Sector-Rotation Allocation.
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
- Official data must not be redistributed or modified in place.
- The final B-list submission should have a no-API or cached/reproducible fallback path.

---

## Current Known Repository Status

From the implementation logs, the repository appears to have completed these phases:

```text
prompt00 — repo reset, skeleton, docs, implementation log helper
prompt01 — environment/data smoke pipeline, manifests, synthetic smoke dataset
prompt02 — data contracts, leakage guard, metrics, compatibility docs
prompt03 — Stage 3 trade processing and S0/S1 baselines
prompt03-real-data — real 2024/2025 S0/S1 baseline rerun
prompt04 — tools layer: backtester, optimiser, experiments, reporting, verification
prompt06 — Stage 2 text store MVP
prompt09 — OCO fallback / conservative ensemble
prompt10 — ablation experiment suite
prompt11 — verification and fix pass
prompt12 — full pipeline run summary, package, final smoke/full-year local checks
```

The current known full-year 2024 local results appear to be:

| Run | Track | Status | Final value | Cum. return | Sharpe | Max drawdown | Turnover |
|---|---|---|---:|---:|---:|---:|---:|
| s0_macro | macro | ok | 110436.493784 | 0.104473 | 0.583667 | 0.152666 | 0.004398 |
| s1_macro | macro | ok | 109192.657160 | 0.092032 | 0.659196 | 0.111177 | 0.049553 |
| s1_sector | sector | ok | 113811.635342 | 0.138227 | 0.691019 | 0.166679 | 0.080896 |
| robust_bl_track1 | macro | ok | 111119.900438 | 0.111307 | 0.858352 | 0.109300 | 0.024054 |
| sector_rotation_track2 | sector | ok | 112589.361340 | 0.126003 | 0.641026 | 0.178251 | 0.116766 |
| oco_fallback_macro | macro | ok | 110533.776524 | 0.105445 | 0.788352 | 0.109046 | 0.026486 |

Treat these as **reported local-backtester results**, not official facts, until official/local parity is verified.

Current preliminary interpretation:

```text
Primary Track 1 candidate:
  robust_bl_track1

Track 1 fallback:
  oco_fallback_macro or s1_macro

Current Track 2 candidate:
  s1_sector, because sector_rotation_track2 does not yet beat S1 sector

Methods not yet promoted:
  sector_rotation_track2
  KG-MoE
  causal graph
  transformer event memory
  deep RL / graph RL
```

---

## Audit Objective

Perform a full repository audit covering:

1. official/local parity;
2. Stage 1 news-processing maturity and traceability;
3. full-year 2024 ablation coverage;
4. locked 2025 public A evaluation coverage;
5. submission wrapper readiness;
6. module maturity labelling;
7. method execution quality;
8. package and reproducibility readiness;
9. report-readiness and overclaim risk.

You may add small audit scripts, report generators, or tests if needed. Do **not** add new strategy features unless required to expose or fix audit failures.

---

## Required Inputs to Inspect

Inspect the current repository, especially:

```text
AGENTS.md
README.md
METHODOLOGY.md
WORKFLOW.md
docs/
docs/REPO_STRUCTURE.md
docs/architecture/
docs/strategy/
docs/prompts/
docs/implementation_logs/
configs/
src/nlpcc/
src/tools/
tests/
scripts/
outputs/reports/
outputs/backtests/
outputs/experiments/
outputs/submissions/
NLPCC_tasks/
NLPCC_tasks/README.md
NLPCC_tasks/README-CN.md
NLPCC_tasks/agent_platform/
NLPCC_tasks/agent_platform/agents/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/server_platform/
NLPCC_tasks/dataset/
```

If paths are missing, state clearly and continue.

---

## Required Output Files

Create the following audit outputs:

```text
docs/implementation_logs/<timestamp>_prompt13_full_audit.md

outputs/reports/prompt13/full_audit_report.md
outputs/reports/prompt13/full_audit_report.json
outputs/reports/prompt13/official_local_parity_report.md
outputs/reports/prompt13/stage1_trace_report.md
outputs/reports/prompt13/module_maturity_matrix.md
outputs/reports/prompt13/full_year_ablation_report.md
outputs/reports/prompt13/public_a_2025_evaluation_report.md
outputs/reports/prompt13/submission_wrapper_audit.md
outputs/reports/prompt13/final_recommendation.md
```

If a report cannot be completed due to missing data/server/state, create the file anyway and clearly mark it as incomplete with blockers and next actions.

---

# Audit Part A — Repository Status Inventory

## Task

Produce a concise repository inventory.

Check:

- current source package name;
- whether `src/nlpcc/` or `src/nlpcc4/` is used;
- whether official-facing agent wrapper exists;
- whether configs exist for S0/S1, robust BL, sector rotation, and OCO fallback;
- whether Stage 1, Stage 2, Stage 3, Stage 4 modules exist;
- whether outputs contain backtests, experiments, reports, and submissions;
- whether docs are consistent with the actual code structure.

## Required Table

Include this table in `full_audit_report.md`:

| Area | Expected | Found | Status | Notes |
|---|---|---|---|---|

Use status values:

```text
ok
partial
missing
inconsistent
blocked
```

---

# Audit Part B — Official / Local Parity

## Purpose

The highest-priority audit is whether local backtest results can be trusted relative to official server semantics.

The current implementation has official server smoke, but official/local metric parity beyond smoke is still not fully proven.

## Required Work

Select a short deterministic date range from 2024 training data, for example 10-30 trading days.

Run the same strategy over the same date span using:

```text
1. local backtester
2. official HTTP server / official server runner
```

Start with simple strategies:

```text
s0_equal_weight_macro
s1_macro
```

If robust BL can be run through the official wrapper, also test:

```text
robust_bl_track1
```

Compare:

```text
daily portfolio value
cash
holdings
submitted trades
accepted/rejected trades
transaction costs
final value
cumulative return
Sharpe
max drawdown
turnover
```

## Required Output

Write:

```text
outputs/reports/prompt13/official_local_parity_report.md
```

Use this table:

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

## Critical Rule

If official server is not running or cannot be reached, do not fake parity. Mark the audit as blocked and state the exact command needed to rerun.

---

# Audit Part C — Stage 1 News Processing Trace

## Purpose

The current implementation seems stronger in Stage 2/3/4 than in Stage 1. The system report should not overclaim LLM/news-processing sophistication unless the Stage 1 path is real and traceable.

## Required Work

Identify the implemented Stage 1 modules.

Check whether the repo has:

```text
news schema
rule-based extraction
LLM extraction or cached extraction
event tuple extraction
BL view extraction
sector impact extraction
news denoising / relevance filtering
prompt/version metadata
input hash / cache key
same-day cutoff handling
no-LLM fallback
```

For at least 3 representative dates, trace:

```text
raw news input
→ Stage 1 extracted events/views/tags
→ Stage 2 stored text state
→ Stage 4 allocation impact
```

Use dates from 2024 training data where news exists.

If Stage 1 is missing or only stubbed, say so clearly.

## Required Output

Write:

```text
outputs/reports/prompt13/stage1_trace_report.md
```

Use this table:

| Date | News Count | Stage 1 Method | Extracted Signals | Stage 2 State | Allocation Impact | Trace Complete? | Notes |
|---|---:|---|---|---|---|---|---|

Also include:

| Stage 1 Component | Path | Implemented? | Used in Current Candidate? | Reproducible? | Notes |
|---|---|---|---|---|---|

## Important Instruction

If text views are deterministic/rule-based rather than LLM-based, describe them as such. Do not call them LLM extraction unless the implementation actually uses a model or cached model outputs.

---

# Audit Part D — Full-Year 2024 Ablation Suite

## Purpose

The current prompt10 ablation suite used a small real-data subset for speed. This is useful for debugging but not enough for final claims.

## Required Work

Run or prepare a full-year 2024 ablation suite.

At minimum include:

```text
s0_macro
s1_macro
robust_bl_track1
robust_bl_no_news
robust_bl_no_confidence
robust_bl_no_turnover_control
robust_bl_rule_based_views
oco_fallback_macro
s0_sector
s1_sector
sector_rotation_track2
sector_without_news
sector_without_graph
sector_momentum_only
```

If some configs are missing, create an audit table showing which ablations are unavailable and why.

## Required Output

Write:

```text
outputs/reports/prompt13/full_year_ablation_report.md
```

Use this table:

| Run | Track | Date Range | Final Value | Cum Return | Sharpe | Max Drawdown | Turnover | Beats S1? | Status | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|

Also include a ranking table:

| Rank | Run | Track | Primary Comparison | Sharpe | Cum Return | Max Drawdown | Turnover | Recommendation |
|---:|---|---|---|---:|---:|---:|---:|---|

## Important Instruction

If runtime is too high, run a smaller representative sample only if necessary, but mark it clearly as non-final.

---

# Audit Part E — Locked 2025 Public A Evaluation

## Purpose

2025 public A should be treated as evaluation, not aggressive tuning. However, current results need to be surfaced to assess generalisation.

## Required Work

Run or collect locked 2025 public A results for:

```text
s0_macro
s1_macro
robust_bl_track1
oco_fallback_macro
s0_sector
s1_sector
sector_rotation_track2
```

If 2025 data is missing or inaccessible, say so.

Do not tune parameters based on 2025 in this audit. This is evaluation-only.

## Required Output

Write:

```text
outputs/reports/prompt13/public_a_2025_evaluation_report.md
```

Use this table:

| Run | Track | Date Range | Final Value | Cum Return | Sharpe | Max Drawdown | Turnover | Beats S1? | Promote? | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|

Also include:

```text
2025 tuning policy:
  No parameter changes were made based on these results during this audit.
```

If any parameter changes are made, log them explicitly and mark the run as no longer a clean evaluation.

---

# Audit Part F — Method Execution Quality

## Purpose

Classify how mature each implemented or claimed method actually is.

## Required Work

Create a maturity matrix for all methods found in code/docs/configs.

Include at least:

```text
S0 equal weight
S1 quant core
inverse volatility
momentum
sector trend-following
robust Black-Litterman
risk parity
belief-state risk parity
HMM / Kalman / MPC
sector impact model
KG-MoE
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

Use maturity labels:

```text
production_candidate
working_prototype
debug_only
research_stub
documented_only
rejected
missing
```

## Required Output

Write:

```text
outputs/reports/prompt13/module_maturity_matrix.md
```

Use this table:

| Method | Code Path | Config Path | Tests | Current Maturity | Used in Full-Year Run? | Performance Evidence | Report Claim Allowed? | Notes |
|---|---|---|---|---|---|---|---|---|

## Important Rule

Do not allow methods that are stubs or wrappers to be described as fully implemented in README/system report.

---

# Audit Part G — Submission Wrapper and Runtime Readiness

## Purpose

Check whether there is an actual official-facing build agent and whether it is minimal, auditable, and compatible with the official Agent Platform.

## Required Work

Identify:

```text
official-facing wrapper path
import path into src/nlpcc/
config loading path
default strategy selected
fallback strategy selected
trade output schema
dependency guard
decision trace / logging path
crash fallback behavior
```

Check whether the wrapper:

- imports correctly;
- does not require notebooks;
- does not require unavailable external APIs by default;
- uses official-compatible trade schema;
- falls back to S1 or conservative ensemble if text/BL modules fail;
- does not read raw hidden fields;
- can run with the official server smoke path.

## Required Output

Write:

```text
outputs/reports/prompt13/submission_wrapper_audit.md
```

Use this table:

| Check | Expected | Found | Status | Notes |
|---|---|---|---|---|

Status values:

```text
pass
partial
fail
blocked
```

---

# Audit Part H — Documentation and Report Claim Audit

## Purpose

Ensure documents do not overclaim the maturity of methods.

## Required Work

Inspect:

```text
README.md
METHODOLOGY.md
WORKFLOW.md
docs/REPO_STRUCTURE.md
docs/strategy/
docs/architecture/
docs/reports/
```

Find claims that imply:

- full KG-MoE is implemented;
- causal graph is implemented;
- transformer event memory is implemented;
- OCO is persistent online mirror descent if it is only one-step gating;
- vectorized/CUDA backtester is truly accelerated if it is only a wrapper;
- LLM extraction is implemented if only deterministic extraction is used;
- Track 2 system is stronger than S1 if it is not.

## Required Output

Include in `full_audit_report.md`:

| Document | Claim | Current Evidence | Risk | Recommended Edit |
|---|---|---|---|---|

Risk values:

```text
low
medium
high
```

---

# Audit Part I — Reproducibility and Package Audit

## Purpose

Confirm that the package is close to B-list ready.

## Required Work

Inspect the latest package under:

```text
outputs/submissions/
```

Check:

```text
package exists
manifest exists
no raw official data included
no cache data included unless explicitly intended and allowed
no __pycache__
no .pyc
no notebooks required
requirements / dependency lock included
Dockerfile or equivalent included if available
configs included
official-facing agent included
src/nlpcc included
tests or minimal smoke script included
```

## Required Output

Include in `full_audit_report.md`:

| Package Item | Status | Evidence | Notes |
|---|---|---|---|

---

# Audit Part J — Final Recommendation

## Required Output

Write:

```text
outputs/reports/prompt13/final_recommendation.md
```

Use exactly this structure:

```md
# Prompt13 Final Recommendation

## 1. Submission Readiness Verdict

Choose exactly one:

- Ready for dry-run submission
- Not ready, but close
- Not ready

## 2. Primary Track 1 Candidate

State the recommended Track 1 candidate and why.

## 3. Primary Track 2 Candidate

State the recommended Track 2 candidate and why.

## 4. Safe Fallback

State the fallback system.

## 5. Methods to Promote

List methods that can be promoted as candidate systems.

## 6. Methods to Keep as Ablations

List methods that should remain ablation/report-only.

## 7. Methods to Reject or Defer

List methods that should not be developed further before final validation.

## 8. Required Fixes Before Next Phase

Give a numbered list.

## 9. Required Evidence Before Final Submission

Give a numbered list.

## 10. Recommended Next Prompt

Suggest the next prompt title and objective.
```

---

## Required Implementation Log

Create an implementation log:

```text
docs/implementation_logs/<timestamp>_prompt13_full_audit.md
```

The log must include:

```md
# Implementation Log: prompt13 - full_audit

## Created

<timestamp>

## Summary

<what was audited and what was produced>

## Files Changed

<list>

## Tests / Checks

<commands run and results>

## Key Findings

<bullet list>

## Caveats

<what could not be verified>

## Artifacts

<output report paths>

## Next Steps

<recommended next phase>
```

---

## Constraints

- Do not implement new strategy features unless necessary to expose an audit issue.
- Do not tune based on 2025 public A results.
- Do not fake official-server parity if the server is unavailable.
- Do not modify raw official data.
- Do not redistribute official data in the package.
- Do not delete existing outputs unless explicitly requested.
- Do not silently rename package paths; if docs/code disagree, report the inconsistency.
- Preserve deterministic execution by default.
- Prefer adding audit reports and tests over adding model complexity.
- Be explicit about blockers.
- Be honest if a method is only a stub or prototype.
- When in doubt, mark a result as local-only, not official.

---

## Expected Final Answer

After completing the audit, respond with:

1. a concise status summary;
2. the readiness verdict;
3. top 5 findings;
4. files created;
5. tests/checks run;
6. next recommended prompt.

Do not paste all report contents unless requested.
