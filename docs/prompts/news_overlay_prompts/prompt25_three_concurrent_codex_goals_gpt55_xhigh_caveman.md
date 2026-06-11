# Three Standalone Concurrent Codex Goal Prompts — Top-8 News Overlay Minor Enhancements

Use each section below as a **separate standalone Codex goal-mode prompt**.  
All three goals are designed to run concurrently from the same Prompt23/Prompt24 repo state.

---

# Prompt A — Track A Research Candidates

## Model and Style

Use **GPT-5.5 XHigh**. Think carefully before editing.  
Use **caveman English** in logs and final answer: short, direct, clear pass/fail.  
Use **RTK commands** whenever available.

## Role

You are Codex acting as a research-code engineer, reproducibility auditor, and quantitative NLP implementation agent.

You work only on the **Track A research candidates** for the News Overlay workflow of NLPCC 2026 Shared Task 4.

## Read First

Read the latest local research/context docs first:

```text
docs/research/new_research_phase_top8_prompt_pack/
```

Use these docs as source of truth for:

```text
- H1-H6 enhancement meanings;
- top-8 candidate roles;
- 2024 tune / frozen 2025 test discipline;
- no-promotion rule;
- current Track A research-only status.
```

## Global Rules

```text
Do not run the full Prompt23 212-row grid.
Do not modify official runtime.
Do not modify raw data.
Do not modify model files.
Do not delete or move preserved evidence.
Do not call online APIs.
Do not download new large models.
Do not tune on 2025.
Do not use hidden 2026 data.
Do not promote any candidate.
```

Use 2024 for tuning only.  
Use 2025 only after 2024 freeze, as frozen reporting only.

## Candidate Scope

You own exactly these Track A candidates:

```text
G11A / P23_G11A_s025_i00_c00_v00_capmedium_ddoff / N13-I6-S13
G12A / P23_G12A_s025_i00_c00_v00_capmedium_ddoff / N2345-I256-S13
G10A / P23_G10A_s050_i25_c00_v00_caplow_ddmild / N2-I2-S3
```

Do not run Track B candidates.

## Clear Goal

Test whether Track A top-3 can be improved safely with minor feature-flagged enhancements.

Track A should remain **research-only** unless it clearly beats controls and passes clean evidence checks.

## Success Criteria

```text
1. Stage 0 smoke runs for 3 Track A candidates.
2. Stage 1 2024 tune runs 18 rows = 3 candidates x 6 variants.
3. One frozen variant per Track A candidate is selected using 2024 only.
4. Stage 2 frozen 2025 runs 3 rows with no parameter change.
5. Final report says improve / no improve / blocked for each candidate.
6. No 2025 metric is used in freeze decisions.
7. No official runtime/raw/model/evidence files are changed.
```

## Enhancement Families

Use only these enhancement families:

```text
H1: parity guard + preserved-control delta
H2: confidence / ambiguity damping
H3: short-horizon decay / event smoothing
H4: turnover cap / weak-signal deadband / temperature
H5: Rank-IC stability / evidence count
H6: composite consensus / dominance control
```

## Candidate Enhancement Map

```text
G11A:
  Use H2 + H3 + optional H4.
  Focus: FinBERT/aspect-tone confidence, asymmetric short decay, macro overlay discipline.

G12A:
  Use H6 + H2 + optional H3.
  Focus: composite consensus shrinkage, substage dominance cap, confidence damping.

G10A:
  Use H2 BGE margin + H3 short relevance decay + H4 deadband/cap.
  Focus: simple BGE relevance hygiene and weak-signal filtering.
```

## Stage Layout

Use this row layout:

```text
V0: baseline, hooks off
V1: H2 confidence / ambiguity damping
V2: H3 short decay / smoothing
V3: H4 turnover cap / deadband
V4: candidate-specific stability, mainly H6 for G12A
V5: best combo from V1-V4 only
```

Run:

```text
Stage 0:
  3 smoke rows
  10 dates
  2024 only

Stage 1:
  18 tune rows
  2024 only

Stage 2:
  3 frozen 2025 rows
  no knob change
```

## RTK Commands

Run or explain blocker:

```bash
rtk --version
rtk git status
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

Use existing repo commands for the actual news-overlay runner. If command names differ, adapt and record exact commands.

## Output Folder

Write all artifacts under:

```text
outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_a/
```

Required files:

```text
track_a_stage0_smoke_summary.md
track_a_stage1_2024_tune_matrix.csv
track_a_stage1_2024_tune_summary.md
track_a_ablation_evidence.csv
track_a_freeze_decisions.md
track_a_stage2_2025_frozen_results.csv
track_a_final_status.md
```

## Required Evidence

For each candidate, report:

```text
baseline vs selected variant;
2024 score / Sharpe / drawdown / turnover;
overlay-active days;
fallback/no-trade days;
confidence bucket if H2 used;
decay attribution if H3 used;
composite attribution if H6 used;
frozen 2025 result;
final Track A status.
```

## Final Response Format

```text
Goal A status:
  pass / partial / fail

Rows:
  Stage 0:
  Stage 1:
  Stage 2:

Frozen variants:
  G11A:
  G12A:
  G10A:

Track A decision:
  improve / no improve / blocked
  still research-only? yes/no, reason

Tests:
  commands + pass/fail

Files:
  changed files
  report files

Blockers:
  exact blockers
```

---

# Prompt B — Track B Clean Parity Candidates

## Model and Style

Use **GPT-5.5 XHigh**. Think carefully before editing.  
Use **caveman English** in logs and final answer: short, direct, clear pass/fail.  
Use **RTK commands** whenever available.

## Role

You are Codex acting as a research-code engineer, parity-prep auditor, and quantitative NLP implementation agent.

You work only on the **clean Track B parity-review candidates**.

## Read First

Read:

```text
docs/research/new_research_phase_top8_prompt_pack/
```

Use these docs as source of truth for:

```text
- H1-H6 enhancement meanings;
- Track B candidate roles;
- parity-review shortlist logic;
- 2024 tune / frozen 2025 test discipline;
- no-promotion rule.
```

## Global Rules

```text
Do not run the full Prompt23 212-row grid.
Do not modify official runtime.
Do not modify raw data.
Do not modify model files.
Do not delete or move preserved evidence.
Do not call online APIs.
Do not download new large models.
Do not tune on 2025.
Do not use hidden 2026 data.
Do not promote any candidate.
```

## Candidate Scope

You own exactly these clean Track B candidates:

```text
G15B / P23_G15B_s025_i00_c00_v00_capmedium_ddoff / N4-I6-S2
G14B / P23_G14B_s100_i00_c00_v00_capmedium_ddoff / N5-I5-S2
G10B / P23_G10B_s050_i25_c00_v00_caplow_ddmild / N2-I2-S2
```

Do not run Track A.  
Do not run G21B or G12B.

## Clear Goal

Improve the clean Track B candidates and produce a parity-prep shortlist.

Default shortlist should remain:

```text
1. G15B
2. G14B
3. G10B
```

Change this only if evidence clearly says no.

## Success Criteria

```text
1. Stage 0 smoke runs for 3 candidates.
2. Stage 1 2024 tune runs 18 rows = 3 candidates x 6 variants.
3. One frozen variant per candidate is selected using 2024 only.
4. Stage 2 frozen 2025 runs 3 rows with no parameter change.
5. Parity shortlist is written with reasons.
6. No 2025 metric is used in freeze decisions.
7. No official runtime/raw/model/evidence files are changed.
```

## Enhancement Families

Use only:

```text
H1: parity guard + preserved-control delta
H2: confidence / ambiguity damping
H3: short-horizon decay / event smoothing
H4: turnover cap / weak-signal deadband / temperature
H5: Rank-IC stability / evidence count
H6: composite consensus / dominance control
```

## Candidate Enhancement Map

```text
G15B:
  Use H3 + H2 + H5.
  Focus: event-label smoothing, duplicate compression, aspect-impact confirmation, Rank-IC shrink.

G14B:
  Use H5 + H4.
  Focus: sector evidence-count, Rank-IC stability, sector tilt temperature, turnover cap.

G10B:
  Use H2 + H5 + H4.
  Focus: BGE margin damping, Rank-IC shrink, weak-signal deadband, turnover cap.
```

## Stage Layout

Use:

```text
V0: baseline, hooks off
V1: H2 confidence / ambiguity damping
V2: H3 short decay / smoothing
V3: H4 turnover cap / deadband / rank temperature
V4: H5 Rank-IC / evidence-count stability
V5: best combo from V1-V4 only
```

Run:

```text
Stage 0:
  3 smoke rows
  10 dates
  2024 only

Stage 1:
  18 tune rows
  2024 only

Stage 2:
  3 frozen 2025 rows
  no knob change
```

## RTK Commands

Run or explain blocker:

```bash
rtk --version
rtk git status
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

## Output Folder

Write all artifacts under:

```text
outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_parity/
```

Required files:

```text
track_b_parity_stage0_smoke_summary.md
track_b_parity_stage1_2024_tune_matrix.csv
track_b_parity_stage1_2024_tune_summary.md
track_b_parity_ablation_evidence.csv
track_b_parity_freeze_decisions.md
track_b_parity_stage2_2025_frozen_results.csv
track_b_parity_prep_shortlist.md
track_b_parity_final_status.md
```

## Required Evidence

For each candidate, report:

```text
baseline vs selected variant;
2024 score / Sharpe / drawdown / turnover;
overlay-active days;
fallback/no-trade days;
Rank-IC bucket report;
sector concentration;
confidence or BGE relevance bucket if applicable;
frozen 2025 result;
parity-prep status.
```

## Final Response Format

```text
Goal B status:
  pass / partial / fail

Rows:
  Stage 0:
  Stage 1:
  Stage 2:

Frozen variants:
  G15B:
  G14B:
  G10B:

Parity shortlist:
  1.
  2.
  3.

Tests:
  commands + pass/fail

Files:
  changed files
  report files

Blockers:
  exact blockers
```

---

# Prompt C — Track B Blocked Research Candidates + Tuner Audit

## Model and Style

Use **GPT-5.5 XHigh**. Think carefully before editing.  
Use **caveman English** in logs and final answer: short, direct, clear pass/fail.  
Use **RTK commands** whenever available.

## Role

You are Codex acting as a research-code engineer, material-difference auditor, and tuner-capability auditor.

You work only on the **blocked Track B research candidates** and the tuner audit.

## Read First

Read:

```text
docs/research/new_research_phase_top8_prompt_pack/
```

Use these docs as source of truth for:

```text
- H1-H6 enhancement meanings;
- material-difference rules;
- preserved-control delta rule;
- 2024 tune / frozen 2025 test discipline;
- no-promotion rule.
```

## Global Rules

```text
Do not run the full Prompt23 212-row grid.
Do not modify official runtime.
Do not modify raw data.
Do not modify model files.
Do not delete or move preserved evidence.
Do not call online APIs.
Do not download new large models.
Do not tune on 2025.
Do not use hidden 2026 data.
Do not promote any candidate.
Do not mark blocked candidates parity-ready unless material difference and preserved-control delta are explained.
```

## Candidate Scope

You own exactly these blocked Track B research candidates:

```text
G21B / P23_G21B_s100_i25_c00_v00_caplow_ddmild / N2345-I256-S5
G12B / P23_G12B_s050_i25_c00_v00_caplow_ddmild / N2345-I256-S126
```

Do not run Track A.  
Do not run G15B, G14B, or G10B.

## Clear Goal

Test whether the blocked high-potential candidates can be stabilized.

They may be researched and frozen-tested, but they must stay **blocked from parity** unless:

```text
material Prompt22-vs-Prompt23 difference is explained;
preserved-control delta passes;
no 2025 tuning is used;
official runtime remains untouched.
```

Also audit whether Bayesian/random/coordinate tuning exists in the repo.

## Success Criteria

```text
1. Stage 0 smoke runs for 2 candidates.
2. Stage 1 2024 tune runs 12 rows = 2 candidates x 6 variants.
3. One frozen variant per candidate is selected using 2024 only.
4. Stage 2 frozen 2025 runs 2 rows with no parameter change.
5. Material-difference review is written.
6. Preserved-control delta check is written.
7. Tuner capability audit is written.
8. Final status says blocked / eligible-after-review / failed.
```

## Candidate Enhancement Map

```text
G21B:
  Use H1 + H6 + H4 + optional H2.
  Focus: material-difference guardrail, composite sector consensus, turnover cap.

G12B:
  Use H1 + H6 + H4 + diagnostic H5.
  Focus: S126 simplification, conflict shrink, dominance cap, preserved-control check.
```

## Stage Layout

Use:

```text
V0: baseline, hooks off
V1: H2 confidence / ambiguity damping
V2: H3 short decay / smoothing if available
V3: H4 turnover cap / deadband
V4: H1/H6 material-difference and composite stability control
V5: best combo from V1-V4 only
```

Run:

```text
Stage 0:
  2 smoke rows
  10 dates
  2024 only

Stage 1:
  12 tune rows
  2024 only

Stage 2:
  2 frozen 2025 rows
  no knob change
```

## Tuner Audit

Search for:

```text
optuna
bayes
bayesian
hyperopt
tpe
random_search
coordinate_search
hyperband
asha
study
trial
suggest_float
```

Report:

```text
found / not found;
file path;
dependency status;
CLI/config status;
safe or unsafe;
used in this run: yes/no.
```

Do not use Bayesian tuning.  
Do not add dependencies.

## RTK Commands

Run or explain blocker:

```bash
rtk --version
rtk git status
rtk grep "optuna|bayes|random_search|coordinate_search|hyperopt|tpe" .
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

## Output Folder

Write all artifacts under:

```text
outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_research/
```

Required files:

```text
track_b_research_stage0_smoke_summary.md
track_b_research_stage1_2024_tune_matrix.csv
track_b_research_stage1_2024_tune_summary.md
track_b_research_ablation_evidence.csv
track_b_research_freeze_decisions.md
track_b_research_stage2_2025_frozen_results.csv
material_difference_review.md
preserved_control_delta_check.csv
tuner_capability_audit.md
track_b_research_final_status.md
```

## Final Response Format

```text
Goal C status:
  pass / partial / fail

Rows:
  Stage 0:
  Stage 1:
  Stage 2:

Frozen variants:
  G21B:
  G12B:

Material-difference review:
  blocked / explained / failed

Preserved-control delta:
  pass / partial / fail

Tuner audit:
  fixed grid:
  random search:
  coordinate search:
  Bayesian/Optuna/TPE:

Parity eligibility:
  G21B:
  G12B:

Tests:
  commands + pass/fail

Files:
  changed files
  report files

Blockers:
  exact blockers
```
