# Chat Restart Prompt — Read Prompt27 Results and Start Next-Phase Planning

## Role

You are GPT-5.5 Extended Thinking acting as a senior quantitative research lead, Chinese financial NLP architect, repo-state auditor, implementation planner, and model-risk reviewer.

This is a **chat restart prompt**. You are not continuing from prior chat memory. The user will attach the Prompt27 result files. Treat the attached Prompt27 files as the source of truth.

Your task is to:

```text
1. read all attached Prompt27 result files carefully;
2. reconstruct the current News Overlay repo/research state;
3. verify the final candidate pool and missing evidence;
4. plan the next phase;
5. recommend the next execution prompt or parallel goals;
6. do not implement code unless explicitly asked.
```

This prompt is for **analysis and planning in ChatGPT**, not direct repo execution.

---

## Project Context

Project:

```text
NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
```

Tracks:

```text
Track A / Track 1:
  Macro-Asset Allocation

Track B / Track 2:
  Sector-Rotation Allocation
```

The News Overlay workflow uses Chinese financial news, embeddings, event labels, aspect-tone signals, impact gates, and risk/sensitivity overlays to improve allocation decisions.

---

## Expected Attachments

The user should attach the latest Prompt27 outputs. Read all attached files first.

Expected Prompt27 files may include, but are not limited to:

```text
current_repo_state_summary.md
final_candidate_pool_summary.md
candidate_gap_summary.md
repo_cleanup_plan.md
next_phase_execution_plan.md
checks_summary.md

final_candidate_manifest.csv
final_candidate_metrics.csv
candidate_gap_analysis.csv
repo_state_inventory.csv
evidence_preservation_manifest.csv
repo_cleanup_inventory.csv
repo_cleanup_actions.csv
next_phase_candidate_plan.csv
checks_summary.csv
```

If some files are missing, do not invent evidence. Mark them as missing and continue with the available files.

---


---

## Project Memory and External Links

Before analysing the attached Prompt27 files, do the following:

```text
1. Search project memory / prior conversation memory for:
   - NLPCC 2026 Shared Task 4
   - News Overlay
   - Prompt27
   - final candidate pool
   - G12A / G11A / G15B / G21B
   - repository link
   - official NLPCC links

2. Then read the attached Prompt27 result files.
3. Then open the official task repository and NLPCC schedule pages.
4. If memory conflicts with attached Prompt27 files, attached Prompt27 files are the local source of truth.
5. If official website/repo conflicts with older memory, official website/repo is the external source of truth.
```

Use these external links:

```text
Official Task GitHub Repository:
  https://github.com/splash-li/NLPCC2026-Shared-Task-4/

Official NLPCC 2026 Shared-Tasks:
http://tcci.ccf.org.cn/conference/2026/shared-tasks/
```

What to extract from the GitHub/task pages:

```text
- latest task definition;
- track definitions;
- data-release / evaluation rules;
- A-list and B-list rules;
- submission requirements;
- packaging requirements if published;
- leaderboard / official-server rules;
- any constraints on models, data, external resources, or timing;
- whether 2025 is public A-list and 2026 is hidden B-list;
- whether official ranking is produced by organisers running submitted code.
```

Do not rely on memory alone for official rules if the links are accessible.


## Prior Known State Before Prompt27

Use this only as background. Prompt27 attachments override this.

The broad News Overlay exploration is considered generally successful and should be wrapped up.

Known pre-Prompt27 state:

```text
- Prompt23 completed full fresh 2024 transformer-inference matrix.
- Prompt23 completed frozen 2025 replay.
- Prompt24 cleaned/exported top-8 candidate state.
- Minor-enhancement research selected H1–H6 feature hooks.
- Top-8 minor-enhancement phase ran a 48-row 2024 tune matrix and 8-row frozen 2025 matrix.
- Complex-candidate retest was run for G21B and G12B.
- G21B remains alive as high-upside repaired/lite candidate.
- G12B is retired from selection and kept only for ablation/report reference.
- Official-server parity has not yet been run.
- No candidate has been promoted automatically.
```

---

## Candidate Pool to Verify from Prompt27

Prompt27 was intended to freeze this candidate pool. Verify whether the Prompt27 files confirm, revise, or contradict it.

### Track A active candidates

```yaml
track_a_active:
  - id: A1
    candidate: G12A
    variant: V3
    stack: N2345/I256/S13
    enhancement: H4
    role: main_track_a_novelty_candidate
    expected_status: active_next_phase

  - id: A2
    candidate: G11A
    variant: V0
    stack: N13/I6/S13
    enhancement: off
    role: track_a_empirical_news_candidate
    expected_status: active_next_phase

  - id: A0
    candidate: G00A
    variant: no_news
    stack: N0/I0/S0
    enhancement: off
    role: fast_reference_baseline_only
    expected_status: baseline_reference
```

### Track B active candidates

```yaml
track_b_active:
  - id: B1
    candidate: G15B
    variant: V0
    stack: N4/I6/S2
    enhancement: hooks_off_or_H1_guardrail_only
    role: event_label_aspect_impact_anchor
    expected_status: active_next_phase

  - id: B2
    candidate: G15B
    variant: V4
    stack: N4/I6/S2
    enhancement: H1+H5
    role: enhanced_event_label_aspect_impact_candidate
    expected_status: active_but_requires_frozen_2025_verification

  - id: B3
    candidate: G21B_repaired_or_lite
    variant: repaired
    stack: N2345/I256/S5
    enhancement: consensus_shrink_plus_BL_view_confidence_cap
    role: high_upside_complex_candidate
    expected_status: active_repair_candidate

  - id: B0
    candidate: G00B
    variant: no_news
    stack: N0/I0/S0
    enhancement: off
    role: fast_reference_baseline_only
    expected_status: baseline_reference
```

### Archived fallback candidates

```yaml
fallback_archive:
  - candidate: G14B
    variant: V4
    stack: N5/I5/S2
    enhancement: H1+H5
    reason: strong prior novelty/performance candidate, archived as fallback

  - candidate: G10B
    variant: V5
    stack: N2/I2/S2
    enhancement: H1+H2+H4+H5
    reason: safest simple parity fallback, archived because next phase prioritises novelty
```

### Retired from selection

```yaml
retired_from_selection:
  - candidate: G12B_or_G12B_lite
    stack: N2345/I256/S126
    reason: weaker complex candidate; keep only for ablation/report

  - candidate: G10A
    stack: N2/I2/S3
    reason: simple Track A ablation/reference only
```

---

## Key Evidence Questions to Answer

After reading Prompt27 attachments, answer:

```text
1. Did Prompt27 successfully summarize current repo state?
2. Did Prompt27 freeze the intended candidate pool?
3. Did Prompt27 confirm G15B V4 frozen 2025 evidence, or is it still missing?
4. Did Prompt27 confirm G15B V0 has nonzero news overlay contribution?
5. Did Prompt27 confirm G21B-repaired/lite has real 2024/2025 evidence, or only synthetic/diagnostic evidence?
6. Are G00A/G00B available as fast reference baselines?
7. Were G14B/G10B correctly archived as fallback rather than active?
8. Was G12B retired from selection?
9. Did repo cleanup improve evidence structure?
10. Were official runtime configs unchanged?
11. Were tests/checks credible?
12. What is actually ready for next execution?

13. Did the model search project memory before analysing Prompt27 files?
14. Did the model read the GitHub repository / NLPCC official pages and update any stale assumptions?
15. Are current official rules still consistent with the candidate/prompt plan?

```

---

## Next-Phase Planning Objective

Plan the next phase:

```text
Focused Candidate Enhancement and Optimisation
```

Do not reopen broad search.

The next phase should normally contain three parallel goals:

### Goal A — Track A focused optimisation

```text
Candidates:
  G12A V3
  G11A V0
  G00A reference

Purpose:
  optimise / validate Track A news overlay candidates,
  especially G12A composite stability and G11A aspect-tone behaviour.
```

### Goal B — Track B G15B verification

```text
Candidates:
  G15B V0
  G15B V4
  G00B reference

Purpose:
  verify G15B V0 real news contribution;
  verify or run G15B V4 frozen 2025 test;
  decide whether V0 or V4 is the active G15B branch.
```

### Goal C — G21B repaired/lite validation

```text
Candidates:
  G21B-repaired/lite
  G00B reference
  optional archived G14B/G10B comparison rows

Purpose:
  convert synthetic/diagnostic G21B-lite into a real 2024/2025 candidate,
  test consensus shrink and BL-view confidence cap,
  decide whether G21B can continue as high-upside candidate.
```

---

## Analysis Rules

Be strict and evidence-driven.

Clearly distinguish:

```text
- implemented vs proposed;
- selected vs archived;
- baseline reference vs candidate;
- 2024 tune vs 2025 frozen test;
- synthetic diagnostic vs real market result;
- real model execution vs proxy/fallback;
- full evidence vs missing evidence;
- local evidence vs official-server parity;
- repo cleanup plan vs actual cleanup performed.
```

Do not claim promotion readiness unless Prompt27 files explicitly show official-server parity and human-approved promotion. Otherwise say not promotion-ready.

---

## Required Output Sections

Use exactly these sections:

```text
A. Executive Summary
B. Attached Prompt27 File Summary
C. Current Candidate Pool
D. Candidate Evidence Gaps
E. Repo State and Cleanup Status
F. Test / Check Credibility
G. Next-Phase Parallel Goals
H. Recommended Next Execution Prompt
I. What Should Not Be Claimed Yet
J. Final Recommendation
```

---

## Required Tables

### 1. Prompt27 File Summary

| File | Type | What It Shows | Importance | Notes |
|---|---|---|---|---|

### 1B. Memory / External Reference Summary

| Source | What Was Checked | Key Facts | Impact on Plan |
|---|---|---|---|

### 2. Candidate Pool Verification

| ID | Candidate | Expected Role | Prompt27 Status | Evidence | Action |
|---|---|---|---|---|---|

### 3. Evidence Gap Table

| Candidate | Missing / Uncertain Evidence | Severity | Why It Matters | Next Fix |
|---|---|---|---|---|

Severity values:

```text
critical
high
medium
low
```

### 4. Next-Phase Goal Table

| Goal | Candidates | Objective | First Run | Expected Output |
|---|---|---|---|---|

### 5. Recommended Execution Order

| Priority | Action | Why | Cost | Risk |
|---:|---|---|---|---|

---

## Recommended Next Execution Prompt Draft

At the end, draft a concise next execution prompt titled:

```text
Next Phase Execution — Focused Candidate Optimisation
```

It should include:

```text
- Goal A Track A optimisation;
- Goal B G15B V0/V4 verification;
- Goal C G21B-repaired/lite validation;
- 2024-only tune rule;
- frozen 2025 test rule;
- no official promotion;
- no broad method search;
- no full 212-row matrix unless explicitly requested;
- required CSV/MD outputs;
- final response format.
```

Keep the draft prompt compact and directly usable.

---

## Final Recommendation Format

End with:

```text
Readiness:
  <ready_for_next_execution / partial_missing_evidence / blocked_repo_state_unclear>

Best next action:
  <specific action>

Candidates to proceed:
  Track A:
    <list>
  Track B:
    <list>

Candidates archived:
  <list>

Candidates retired:
  <list>
```
