# Synthesis Prompt — Top-8 News Overlay Minor-Enhancement Research Synthesis

## Role

You are a senior quantitative research lead, Chinese financial NLP architect, model-risk auditor, and implementation planner.

This is a **new research phase**. There is no prompt number. You do not have repository access unless explicitly provided. You will receive the seven Prompt24-rendered files and several external research reports generated from the standalone research prompts.

Your task is to synthesise the external research into one implementation-ready plan.

Do not write code.

# Standalone Project Context

You are working on a new research phase for the News Overlay workflow of the NLPCC 2026 Shared Task 4 project:

```text
Task:
  LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market

Track A / Track 1:
  Macro-Asset Allocation

Track B / Track 2:
  Sector-Rotation Allocation
```

This research phase does **not** assume access to previous repo files, prior prompt history, or hidden project state.

You will be given exactly these seven Prompt24-rendered files as local context:

```text
current_state_summary.md
final_recommendation.md
manual_review_checklist.md
repo_cleanup_summary.md
research_handoff_summary.md
top8_2024_tune_2025_test_plan.md
top8_candidate_summary.md
```

Read those seven files carefully first. Treat them as the local source of truth. The embedded context below is provided so that the prompt remains self-contained if a research engine has limited file-reading ability.

---

## Current State Summary

The latest recorded state says:

```text
- Prompt23 fresh 2024 rows: 212 total, 212 passed.
- Prompt23 frozen 2025 rows: 12 total, 12 passed.
- Prompt22 vs Prompt23 equivalence:
    confirmed: 46
    minor_numeric_drift: 71
    material_difference: 95
- Freshness audit: partial / material-equivalence differences remain.
- Dependency audit: pass.
- Package audit: pass.
- Official-server parity is not run.
- No candidate is promoted.
- Prompt18/19 official runtime evidence is preserved under configs/preserved_candidates/.
```

Readiness from the latest recommendation:

```text
ready_for_research_engine_handoff
ready_for_top8_minor_enhancement_planning
```

Do not promote candidates automatically. Track B parity preparation may begin only after human review of material Prompt22-vs-Prompt23 differences and preserved-control deltas.

---

## Current Top-8 Candidate Set

### Track A — research-only candidates

```yaml
track_a_top3:
  - rank: 1
    run_id: P23_G11A_s025_i00_c00_v00_capmedium_ddoff
    family: G11A
    method_stack: N13/I6/S13
    architecture: FinBERT/aspect-tone hybrid + aspect-impact aggregator + Track A sensitivity/risk overlay
    current_status: research_only
    prompt23_equivalence_status: minor_numeric_drift
    2024_selection_score: 0.852792
    2025_sharpe: 2.033851

  - rank: 2
    run_id: P23_G12A_s025_i00_c00_v00_capmedium_ddoff
    family: G12A
    method_stack: N2345/I256/S13
    architecture: composite BGE/FinBERT transformer news stack + composite impact stack + Track A sensitivity/risk overlay
    current_status: research_only
    prompt23_equivalence_status: minor_numeric_drift
    2024_selection_score: 0.830065
    2025_sharpe: 2.025192

  - rank: 3
    run_id: P23_G10A_s050_i25_c00_v00_caplow_ddmild
    family: G10A
    method_stack: N2/I2/S3
    architecture: BGE bi-encoder relevance + base impact + macro risk/sensitivity gate
    current_status: research_only
    prompt23_equivalence_status: minor_numeric_drift
    2024_selection_score: 0.737792
    2025_sharpe: 2.024915
```

### Track B — parity-review / research candidates

```yaml
track_b_top5:
  - rank: 1
    run_id: P23_G21B_s100_i25_c00_v00_caplow_ddmild
    family: G21B
    method_stack: N2345/I256/S5
    architecture: full composite transformer news stack + composite impact stack + BL/sector overlay
    current_status: research_continue
    prompt23_equivalence_status: material_difference
    2024_selection_score: 0.845581
    2025_sharpe: 1.570887

  - rank: 2
    run_id: P23_G14B_s100_i00_c00_v00_capmedium_ddoff
    family: G14B
    method_stack: N5/I5/S2
    architecture: sector-query attention + impact-gated attention + Rank-IC sector gate
    current_status: parity_review_candidate
    prompt23_equivalence_status: minor_numeric_drift
    2024_selection_score: 0.774186
    2025_sharpe: 1.539189

  - rank: 3
    run_id: P23_G10B_s050_i25_c00_v00_caplow_ddmild
    family: G10B
    method_stack: N2/I2/S2
    architecture: BGE bi-encoder relevance + base impact + Rank-IC sector gate
    current_status: parity_review_candidate
    prompt23_equivalence_status: minor_numeric_drift
    2024_selection_score: 0.598217
    2025_sharpe: 1.553354

  - rank: 4
    run_id: P23_G12B_s050_i25_c00_v00_caplow_ddmild
    family: G12B
    method_stack: N2345/I256/S126
    architecture: full composite transformer stack + composite impact + composite sensitivity gate
    current_status: research_continue
    prompt23_equivalence_status: material_difference
    2024_selection_score: 0.560891
    2025_sharpe: 1.531809

  - rank: 5
    run_id: P23_G15B_s025_i00_c00_v00_capmedium_ddoff
    family: G15B
    method_stack: N4/I6/S2
    architecture: BGE event-label / label-attention + FinBERT aspect-impact + Rank-IC sector gate
    current_status: parity_review_candidate
    prompt23_equivalence_status: confirmed
    2024_selection_score: 0.474186
    2025_sharpe: 1.619708
```

---

## Current Planned Execution Shape

The latest plan proposes a small top-8-only workflow:

```text
Stage 0 — smoke:
  candidate_scope: top8
  rows_planned: 8
  date_scope: 10
  allowed_data: 2024 only
  purpose: config/check only; no selection

Stage 1 — quick 2024 tune:
  candidate_scope: top8
  rows_planned: 48
  date_scope: 242
  allowed_data: 2024 only
  purpose: minor bounded variations on 2024 only

Stage 2 — frozen 2025 test:
  candidate_scope: top8
  rows_planned: 8
  date_scope: 243
  allowed_data: 2025 frozen test / official parity prep
  purpose: frozen from Stage 1 only; no parameter changes

Stage 3 — parity preparation:
  candidate_scope: Track B shortlist
  rows_planned: 3
  date_scope: 243
  allowed_data: 2025 frozen test / official parity prep
  purpose: Track B shortlist unless Track A improves versus controls
```

Estimated runtime from the latest plan:

```text
Stage 0 smoke:
  ~0.41 minutes

Stage 1 quick 2024 tune:
  ~58.89 minutes

Stage 2 frozen 2025 test:
  ~9.85 minutes

Stage 3 parity preparation:
  ~3.7 minutes
```

---

## Hard Research Constraints

```text
- Research all 8 methods together.
- Propose different enhancement methods, but keep them minor and ablatable.
- Do not assume repository access.
- Do not write implementation code.
- Do not ask for previous prompt history.
- Use only the seven provided Prompt24-rendered files plus the embedded context in this prompt.
- Do not propose new large architectures.
- Do not propose online LLM/API calls.
- Do not propose hidden 2026 usage.
- Do not propose 2025 tuning.
- Do not propose large new model downloads.
- Do not propose opaque methods that cannot be ablated.
- Preserve the 2024 tune / 2025 frozen-test discipline.
```

---

## Terminology

Use these method-stage interpretations:

```text
N2:
  BGE bi-encoder relevance / dense news relevance.

N3:
  FinBERT/aspect-tone or encoder-aspect proxy.

N4:
  BGE event-label / label-attention scoring.

N5:
  sector-query attention pooling.

N13:
  N1 + N3 hybrid, lexical/base relevance plus aspect-tone.

N2345:
  composite N-stage using BGE relevance, FinBERT/aspect tone, event-label/label attention, and sector-query attention.

I2:
  base/simple impact stage.

I5:
  impact-gated attention pooling.

I6:
  aspect-impact aggregator.

I256:
  composite impact stack using I2 + I5 + I6.

S2:
  Rank-IC sector gate.

S3:
  macro risk/sensitivity gate.

S5:
  BL/sector overlay.

S13:
  Track A sensitivity/risk overlay.

S126:
  composite sensitivity/overlay stack.
```


---

## Inputs to Read

Read the seven Prompt24-rendered files:

```text
current_state_summary.md
final_recommendation.md
manual_review_checklist.md
repo_cleanup_summary.md
research_handoff_summary.md
top8_2024_tune_2025_test_plan.md
top8_candidate_summary.md
```

Then read all external research reports from this new research phase, especially:

```text
- broad minor enhancement research;
- robustness / parity-safe enhancement research;
- candidate-specific micro-enhancement research.
```

If reports disagree, preserve the disagreement and make a reasoned decision.

---

## Synthesis Objective

Produce one concise implementation-ready plan for the next repo execution prompt.

The plan must:

```text
1. keep all 8 candidates visible;
2. select 3–7 minor enhancements total;
3. avoid large architecture changes;
4. define exact parameters to tune on 2024 only;
5. define frozen 2025 tests;
6. define ablations;
7. define parity-prep criteria;
8. decide which candidates are implementation targets, research-only, backups, or rejected.
```

---

## Hard Constraints

```text
- Do not tune on 2025.
- Do not use hidden 2026 data.
- Do not propose online LLM/API calls.
- Do not propose new large model downloads.
- Do not modify official runtime before parity review.
- Do not promote candidates automatically.
- Do not collapse to one candidate per track.
- Do not propose vague enhancements.
```

---

## Required Output Sections

Use exactly these sections:

```text
A. Executive Summary
B. Research Inputs Compared
C. Top-8 Candidate Status
D. Enhancement Shortlist
E. Candidate-to-Enhancement Mapping
F. 2024 Tune / 2025 Frozen Test Plan
G. Ablation Plan
H. Parity-Prep Criteria
I. Rejected Ideas
J. Implementation Prompt Draft
```

---

## Required Tables

### 1. Research Report Comparison

| Source | Main Recommendations | Strength | Weakness | Decision |
|---|---|---|---|---|

### 2. Candidate Status

| Candidate | Track | Current Status | Main Risk | Keep / Enhance / Backup / Reject |
|---|---|---|---|---|

### 3. Final Enhancement Shortlist

| ID | Enhancement | Applies To | Parameters | Expected Benefit | Ablation | Priority |
|---|---|---|---|---|---|---|

### 4. Candidate-to-Enhancement Map

| Candidate | Enhancements to Apply | Tune Parameters | Do Not Change |
|---|---|---|---|

### 5. 2024/2025 Test Matrix

| Stage | Data | Candidates | Rows | Purpose | Pass Criterion |
|---|---|---|---:|---|---|

### 6. Parity-Prep Candidate List

| Rank | Candidate | Reason | Required Evidence Before Parity |
|---:|---|---|---|

### 7. Rejected Ideas

| Idea | Rejected Because | Risk |
|---|---|---|

---

## Implementation Prompt Draft

At the end, draft a compact next implementation prompt titled:

```text
Top-8 Minor Enhancement Implementation and 2024/2025 Validation
```

The draft prompt should include:

```text
- exact enhancement list;
- candidate scope;
- 2024-only tune rule;
- frozen 2025 test rule;
- required CSV/MD outputs;
- no official promotion;
- no full 212-row fresh grid rerun unless necessary;
- final response format.
```

Keep the implementation prompt concise and directly usable.
