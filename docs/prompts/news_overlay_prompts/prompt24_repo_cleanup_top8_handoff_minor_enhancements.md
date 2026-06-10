# Prompt24 — Repo Cleanup, Top-8 Candidate Status Export, and Minor-Enhancement Research Handoff

## Role

You are a senior research-code auditor, repository-cleanup engineer, reproducibility reviewer, quantitative research lead, and AI-workflow documentation architect.

You are continuing after Prompt23 in the News Overlay workflow for NLPCC 2026 Shared Task 4.

Prompt23 completed the full fresh transformer-inference matrix, but the next step is **not another full grid**. The next step is to clean the repo, preserve the current top-8 candidates, export a precise current-status dossier, and prepare a research-engine context pack for a next round of minor candidate enhancements.

This prompt is intentionally practical and cleanup-oriented.

---

## Recommended Agent Mode

Use:

```text
GPT-5.5 High
```

`GPT-5.5 Medium` is acceptable if only generating reports and manifests. Use `GPT-5.5 XHigh` only if repo state is inconsistent or the candidate evidence is hard to reconcile.

---

## Goal

Clean and organise the repository after Prompt23, preserve the current top-8 candidates, and create a handoff package for:

```text
1. 2024-only tuning preparation;
2. frozen 2025 test preparation;
3. official-server parity preparation;
4. minor enhancement research on the current top-8 candidates;
5. external/deep-research engine context.
```

This is not a new model-development prompt.

Do **not** run another full 4–5 hour fresh-inference grid.

---

## Workflow Structure

Follow the structured AI-usage workflow style:

```text
Stage 1 — Discuss / Freeze Current State
Stage 2 — Research Context Export
Stage 3 — Project Initialisation / Repo Cleanup
Stage 4 — Execution Preparation
Stage 5 — Manual Check, Log Review, and Fixes
```

Use this structure in the final status dossier and research-engine handoff.

---

## Current Candidate Set to Preserve

Treat these as the current Prompt23 top-8 candidate set unless repo artifacts prove otherwise.

### Track A — 3 research-only candidates

```yaml
track_a_top3:
  - run_id: P23_G11A_s025_i00_c00_v00_capmedium_ddoff
    family: G11A
    method_stack: N13/I6/S13
    architecture: FinBERT/aspect-tone hybrid + aspect-impact aggregator + Track A sensitivity/risk overlay
    status: research_only
    note: best Track A fresh 2024 selection score, but not promotion-ready

  - run_id: P23_G12A_s025_i00_c00_v00_capmedium_ddoff
    family: G12A
    method_stack: N2345/I256/S13
    architecture: composite BGE/FinBERT transformer news stack + composite impact stack + Track A sensitivity/risk overlay
    status: research_only
    note: most complete Track A transformer-composite candidate

  - run_id: P23_G10A_s050_i25_c00_v00_caplow_ddmild
    family: G10A
    method_stack: N2/I2/S3
    architecture: BGE bi-encoder relevance + base impact + macro risk/sensitivity gate
    status: research_only
    note: simplest Track A real-local transformer candidate
```

### Track B — 5 candidates for parity/research review

```yaml
track_b_top5:
  - run_id: P23_G21B_s100_i25_c00_v00_caplow_ddmild
    family: G21B
    method_stack: N2345/I256/S5
    architecture: full composite transformer news stack + composite impact stack + BL/sector overlay
    status: research_continue
    note: best fresh 2024 Track B score but Prompt23 marks research_continue

  - run_id: P23_G14B_s100_i00_c00_v00_capmedium_ddoff
    family: G14B
    method_stack: N5/I5/S2
    architecture: sector-query attention + impact-gated attention + Rank-IC sector gate
    status: parity_review_candidate
    note: frozen-2025-supported candidate

  - run_id: P23_G10B_s050_i25_c00_v00_caplow_ddmild
    family: G10B
    method_stack: N2/I2/S2
    architecture: BGE bi-encoder relevance + base impact + Rank-IC sector gate
    status: parity_review_candidate
    note: simple frozen-2025-supported candidate

  - run_id: P23_G12B_s050_i25_c00_v00_caplow_ddmild
    family: G12B
    method_stack: N2345/I256/S126
    architecture: full composite transformer stack + composite impact + composite sensitivity gate
    status: research_continue
    note: complex backup/research candidate

  - run_id: P23_G15B_s025_i00_c00_v00_capmedium_ddoff
    family: G15B
    method_stack: N4/I6/S2
    architecture: BGE event-label / label-attention + FinBERT aspect-impact + Rank-IC sector gate
    status: parity_review_candidate
    note: strongest simple Track B frozen-2025-supported candidate
```

Do not reduce the handoff to one candidate per track.

---

## Non-Negotiable Constraints

```text
- Do not modify frozen official runtime configs.
- Do not promote candidates automatically.
- Do not run full fresh-inference grid.
- Do not tune on 2025.
- 2024 may be used for tuning/preparation only.
- 2025 may be used only as frozen test.
- Do not use hidden 2026 data.
- Do not download models.
- Do not call online APIs.
- Do not copy Hugging Face model binaries into repo or packages.
- Do not delete raw official data.
- Do not delete source code, configs, tests, docs, official starter files, or implementation logs.
- Archive questionable generated clutter instead of deleting it.
- Preserve Prompt18/19 official runtime evidence separately from Prompt21–23 News Overlay research evidence.
```

---

## RTK Usage

Use RTK for high-verbosity operations if available:

```bash
rtk --version
rtk git status
rtk git diff
rtk find "*.md" .
rtk grep "pattern"
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If RTK is unavailable, fall back to normal commands and record this.

Do not let RTK hide evidence. Material results must be written to CSV/MD artifacts.

---

## Output Directory

Store Prompt24 outputs under:

```text
outputs/reports/news_overlay/prompt24/presented/
outputs/reports/news_overlay/prompt24/reference/
outputs/reports/news_overlay/prompt24/progress/
```

Also create or update durable docs under:

```text
docs/news_overlay/
docs/implementation_logs/
docs/research_handoffs/news_overlay/
```

---

# Stage 1 — Freeze Current State

## Objective

Freeze and document the current repo/candidate state after Prompt23.

## Tasks

1. Verify Prompt23 artifacts exist.
2. Verify top-8 candidate rows are present.
3. Verify Prompt23 freshness audit status and unresolved blockers.
4. Verify official runtime configs are unchanged.
5. Verify Prompt18/19 official runtime evidence is preserved separately.
6. Verify 2024-only tune / 2025 frozen-test discipline is documented.
7. Verify no model binaries or raw data are being included in any package/handoff.

## Required Outputs

```text
outputs/reports/news_overlay/prompt24/reference/current_state_inventory.csv
outputs/reports/news_overlay/prompt24/reference/top8_candidate_manifest.csv
outputs/reports/news_overlay/prompt24/presented/current_state_summary.md
outputs/reports/news_overlay/prompt24/presented/top8_candidate_summary.md
```

`top8_candidate_manifest.csv` must include:

```text
track
rank
run_id
family
method_stack
architecture_summary
frozen_parameters
2024_return
2024_sharpe
2024_selection_score
2025_return
2025_sharpe
delta_vs_G00
delta_vs_G01
delta_vs_preserved_primary
delta_vs_preserved_fallback
prompt23_equivalence_status
freshness_audit_status
current_status
recommended_next_use
```

---

# Stage 2 — Research Context Export

## Objective

Create a compact context pack for external/deep-research engines to propose **minor enhancements** for the current top-8 candidates.

This is not an implementation stage.

## Research Scope

Ask research engines to focus on small, implementable modifications to the current top-8 candidates, not new large architectures.

Allowed enhancement themes:

```text
1. better threshold schedules for overlay_strength / impact_threshold / turnover_cap;
2. event magnitude smoothing and decay;
3. confidence damping for ambiguous news;
4. sector-specific sensitivity calibration;
5. Rank-IC gate stability;
6. low-turnover overlay clipping;
7. Track A risk-scaling improvements;
8. Track B sector-rank tilt improvements;
9. candidate-specific ablation suggestions;
10. official-runtime dependency minimisation.
```

Disallowed enhancement themes:

```text
- new end-to-end neural allocator;
- online LLM calls;
- hidden 2026 data use;
- 2025 tuning;
- large new model downloads;
- unconstrained strategy override;
- adding opaque methods that cannot be ablated.
```

## Required Outputs

```text
docs/research_handoffs/news_overlay/prompt24_research_context.md
docs/research_handoffs/news_overlay/prompt24_top8_candidate_cards.md
docs/research_handoffs/news_overlay/prompt24_minor_enhancement_questions.md
docs/research_handoffs/news_overlay/prompt24_external_research_prompt.md

outputs/reports/news_overlay/prompt24/presented/research_handoff_summary.md
outputs/reports/news_overlay/prompt24/reference/research_question_backlog.csv
```

The external research prompt must include:

```text
- project context;
- top-8 candidate table;
- strict 2024 tune / 2025 test rule;
- Prompt23 caveats;
- exact enhancement themes;
- required output tables;
- instruction not to propose vague new architectures.
```

---

# Stage 3 — Repo Cleanup

## Objective

Clean the repository and output folders without removing evidence.

## Tasks

1. Inventory large/stale `.var/` and `outputs/` folders.
2. Separate final evidence from temporary run caches.
3. Archive interrupted or superseded Prompt21/22/23 partial artifacts if safe.
4. Preserve final Prompt23 artifacts.
5. Preserve Prompt18/19 official evidence.
6. Preserve implementation logs.
7. Preserve packages.
8. Preserve configs and raw data.
9. Produce a cleanup plan before moving/deleting anything.
10. Archive rather than delete if uncertain.

## Required Outputs

```text
outputs/reports/news_overlay/prompt24/reference/repo_cleanup_inventory.csv
outputs/reports/news_overlay/prompt24/reference/repo_cleanup_actions.csv
outputs/reports/news_overlay/prompt24/reference/evidence_preservation_manifest.csv
outputs/reports/news_overlay/prompt24/presented/repo_cleanup_summary.md
```

`repo_cleanup_actions.csv` must include:

```text
path
type
size_mb
action
reason
safe_to_delete
archived_to
evidence_status
notes
```

Do not remove anything unless `safe_to_delete=true` and evidence is preserved elsewhere.

---

# Stage 4 — Prepare 2024 Tune / 2025 Test for Top 8

## Objective

Prepare the next tuning/evaluation round for the top-8 candidates, but do not launch a long grid.

## Tasks

1. Create a top-8-only tuning plan.
2. Limit enhancements to minor modifications.
3. Use 2024 only for tuning.
4. Use 2025 only for frozen testing.
5. Include Track A and Track B separately.
6. Define a small staged grid:
   - smoke;
   - quick 2024 tune;
   - locked 2025 test;
   - parity-prep shortlist.
7. Estimate runtime for each stage.
8. Prepare configs or config templates only if safe.
9. Do not run full tuning unless explicitly requested later.

## Required Outputs

```text
outputs/reports/news_overlay/prompt24/reference/top8_tune_test_plan.csv
outputs/reports/news_overlay/prompt24/reference/top8_runtime_estimate.csv
outputs/reports/news_overlay/prompt24/presented/top8_2024_tune_2025_test_plan.md
```

Required stages:

```text
Stage 0 — smoke:
  <= 8 candidates
  <= 10 dates
  purpose: config/check only

Stage 1 — quick 2024 tune:
  top-8 candidates
  bounded parameter variations
  2024 only

Stage 2 — frozen 2025 test:
  only candidates frozen from Stage 1
  no parameter changes

Stage 3 — parity preparation:
  Track B shortlist only unless Track A improves vs local and preserved controls
```

---

# Stage 5 — Manual Check, Log Review, and Fixes

## Objective

Create a review checklist for the human owner and future agents.

## Required Outputs

```text
outputs/reports/news_overlay/prompt24/presented/manual_review_checklist.md
outputs/reports/news_overlay/prompt24/presented/final_recommendation.md
docs/implementation_logs/<timestamp>_prompt24_repo_cleanup_top8_handoff.md
```

Checklist must include:

```text
- Prompt23 freshness audit failure reviewed?
- Prompt22-vs-Prompt23 material differences understood?
- Track A kept research-only unless improved?
- Track B parity-review shortlist chosen?
- Official runtime untouched?
- Raw data untouched?
- Model binaries excluded?
- 2024/2025 discipline preserved?
- Research engine handoff generated?
- Cleanup actions reviewed?
```

---

## Tests / Checks

Run only compact checks:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If full tests are too slow, run targeted News Overlay tests and record exact scope.

Do not run the 4–5 hour Prompt23 matrix again.

---

## Final Recommendation Rules

Classify readiness as one of:

```text
ready_for_research_engine_handoff
ready_for_top8_minor_enhancement_planning
ready_for_parity_prep_after_human_review
not_ready_cleanup_or_evidence_missing
```

Do not classify as official-promotion-ready.

---

## Required Final Response Format

```text
Prompt24 status:
  <pass/partial/fail>

Repo cleanup:
  <summary>

Top-8 candidate manifest:
  <path>

Current status dossier:
  <path>

Research handoff:
  <path>

2024 tune / 2025 test preparation:
  <path>

Top Track A candidates preserved:
  1. <run_id / method_stack / status>
  2. <run_id / method_stack / status>
  3. <run_id / method_stack / status>

Top Track B candidates preserved:
  1. <run_id / method_stack / status>
  2. <run_id / method_stack / status>
  3. <run_id / method_stack / status>
  4. <run_id / method_stack / status>
  5. <run_id / method_stack / status>

Freshness audit status:
  <summary>

Prompt22-vs-Prompt23 status:
  <summary>

Official runtime changed?
  <yes/no>

Tests/checks run:
  <commands and pass/fail>

Readiness:
  <one of the allowed readiness labels>

Next recommended prompt:
  <specific next prompt direction>
```
