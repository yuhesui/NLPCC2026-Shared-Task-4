# Prompt10 — Final Candidate Selection, Methodology Audit, and Code-vs-Intent Report

## Role

You are GPT-5.5 Extended Thinking in a **fresh Codex session**.

Act as:

```text
senior quantitative research lead
official-server validation engineer
Chinese financial NLP system auditor
transformer news-overlay auditor
portfolio-risk methodology reviewer
research history reconstruction analyst
single implementation-log writer
```

Your job is to decide the **final candidate to keep for Track A and Track B**, while also testing the main alternate candidate for each track and writing a full methodology report.

This is not a broad new modelling phase.

This is a **final candidate-selection and methodology-audit phase**.

---

## Core Objective

Produce one rigorous final answer to:

```text
For Track A, should we keep A0 no-news or A2_real transformer-news overlay?
For Track B, should we keep B0 no-news or B2_real transformer-news overlay?
What exactly is implemented in code?
How does actual code differ from the originally intended N/I/S transformer architecture?
Which previous hypotheses/fixes/enhancements were tested?
Why were they kept, rejected, or not used?
What should be claimed in the system report?
What should not be claimed?
```

Important decision rule:

```text
Beating the no-news baseline is NOT a strict hard guard.
```

A news candidate may still be kept if it gives:

```text
better robustness;
lower turnover;
lower drawdown;
better regime behaviour;
better interpretability;
credible transformer-news usage;
stable near-baseline performance;
strong system-report value.
```

But if the news candidate is weaker, noisier, fails ablation, or is not production-clean, say so.

Do not overclaim.

---

## Phase

Use exact phase name:

```text
Prompt10 — Final Candidate Selection and Methodology Audit
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt10_final_candidate_methodology_audit/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
server_run/
methodology/
code_audit/
history_audit/
tests/
report/
```

All important run CSVs must be copied to:

```text
presented/run_csv/
```

The main final methodology report must be a single Markdown file:

```text
presented/final_methodology_and_candidate_selection_report.md
```

This report is the key artifact.

---

## One Implementation Log Only

Write exactly one Prompt10 implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt10_final_candidate_methodology_audit/presented/implementation_log.md
```

Do not write:

```text
docs/implementation_logs/*
any other Prompt10 implementation_log.md
```

If the file exists, update it in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt10_logs_created = false
```

---

## Candidate Set

Focus on exactly two serious candidates per track.

### Track A

```text
A0 = G00A no-news production-safe base
A2_real = G11A real-transformer news overlay, N13/I6/S13
```

### Track B

```text
B0 = G00B no-news production-safe base
B2_real = G15B real-transformer news overlay, N4/I6/S2
```

Secondary / history-only candidates to audit, not necessarily rerun unless cheap:

```text
A1 = G12A V3 / N2345/I256/S13
B3 = G21B repaired_lite / N2345/I256/S5
A2 original pre-real-transformer
B2 original pre-real-transformer
A2_E1/E2/E3 from Prompt08
B2_E1/E2/E3 from Prompt08
```

Do not reopen the old full 212-row matrix.

---

## Current Prior Belief

Use this as initial context, then verify from repo/output files:

```text
Prompt07:
  A0/B0 were the strongest local official-server no-news references.
  A2/B2 were closest news candidates but still slightly below no-news.

Prompt08:
  attempted continuous tensor news enhancements.
  B2_E3 showed tiny local-server improvement, but news-use ablation was suspicious because shuffled news beat active.

Prompt09:
  implemented stricter production real-transformer path with no proxy/heuristic fallback.
  local BGE + FinBERT-style models were loaded local-only.
  A2_real appeared to beat A0 on local official-server Sharpe and return with lower turnover.
  B2_real nearly tied B0 on Sharpe but had lower return and worse drawdown.
  A2_real ablation passed basic active-vs-zeroed and barely active-vs-shuffled.
  B2_real failed active-vs-shuffled.
```

Do not trust these summaries blindly. Reconstruct from actual repo files and CSVs.

---

## Hard Rules

```text
Use rtk, rtk python, rtk git.
Use project .venv RTK Python.
No hidden 2026.
No online API for model inference.
No new model download.
No broad candidate search.
No fake/proxy results.
No stale summary reuse.
No remote official submission.
No final claim without CSV/log/source evidence.
```

Production real-NLP rule:

```text
A2_real and B2_real must use real local transformer inference.
proxy_mode must be false.
heuristic_fallback_used must be false.
fixed_target_replay_used must be false.
network_attempted must be false.
local_files_only must be true.
```

Package/env cleanup is not the main goal, but run the requested tests.

Skip unless trivial:

```text
pip check
compileall
package build
Docker build
LaTeX finalization
```

Those are final cleanup/submission phase.

---

## Stage 0 — Whole-Repo and Output Evidence Intake

Read the whole repo structure and previous output folders.

Required areas to inspect:

```text
src/**
NLPCC_tasks/**
docs/news_overlay/**
docs/NLPCC2026 - Template/**
outputs/reports/news_overlay/**
outputs/reports/focused_candidate_optimisation/**
tests/**
README.md
AGENTS.md
```

Create:

```text
reference/repo_evidence_manifest.csv
reference/previous_phase_artifact_manifest.csv
presented/repo_evidence_intake_summary.md
```

Manifest columns:

```text
path
type
phase_or_component
read_status
why_relevant
key_observation
```

The intake must identify:

```text
all final candidate result CSVs;
all official-server run outputs;
all real-transformer evidence outputs;
all ablation outputs;
all candidate configs;
all official adapter files;
all methodology/report drafts;
all relevant source files for A0/A2_real/B0/B2_real.
```

---

## Stage 1 — Previous Hypotheses / Fixes / Enhancements History Audit

Reconstruct what was tried across prior phases.

Create:

```text
history_audit/hypothesis_history_table.csv
history_audit/candidate_evolution_table.csv
history_audit/rejected_or_not_used_methods.csv
presented/history_audit_summary.md
```

`hypothesis_history_table.csv` columns:

```text
hypothesis_or_fix
phase_or_prompt
track
candidate_or_method
intended_effect
actual_implementation_status
evidence_file
result
kept_or_rejected
reason_kept_or_rejected
current_relevance
```

Must include at least:

```text
no-news baseline A0/B0
original A2/B2 news overlays
A1/B3 secondary candidates
Prompt04/05 Type-B/C/D studies
Prompt06 official runner port
Prompt07 official server/platform run
Prompt08 tensor E1/E2/E3 variants
Prompt09 real-transformer no-proxy implementation
synthetic stress tests
same-window Type-D
active-vs-zeroed ablation
active-vs-shuffled ablation
proxy/heuristic fallback removal
turnover/deadband/risk guard attempts
confidence/regime/shrink gates
candidate variants not kept
```

If evidence is missing for a historical item, mark:

```text
not evidenced
```

Do not invent results.

---

## Stage 2 — Intended Method vs Actual Code Audit

Compare intended architecture against actual implementation.

Create:

```text
code_audit/intended_vs_actual_method_table.csv
code_audit/final_candidate_source_map.csv
code_audit/official_agent_code_path_audit.csv
presented/code_vs_intended_method_summary.md
```

For each final candidate:

```text
A0
A2_real
B0
B2_real
```

audit:

```text
intended architecture
actual source files
actual classes/functions called
official server adapter path
model assets used
news tensor provider used
risk controls used
overlay formula
cache behavior
proxy/heuristic fallback status
fixed-target replay status
known deviations from intended method
```

`intended_vs_actual_method_table.csv` columns:

```text
track
candidate_id
intended_stack
intended_component
intended_behavior
actual_file_path
actual_function_or_class
actual_behavior
match_status
deviation
severity
evidence
```

Match statuses:

```text
matches
partial
implemented_differently
missing
not_used
not_evidenced
```

Severity:

```text
critical
high
medium
low
none
```

Special focus:

```text
Was real transformer architecture actually ported into the official trading agent?
Does A2_real really use N13/I6/S13?
Does B2_real really use N4/I6/S2?
Does official server call real transformer code or old target replay?
Does no-news A0/B0 avoid news entirely?
```

---

## Stage 3 — Final Candidate Test Runs

Run final side-by-side tests.

Minimum required run set:

```text
Track A:
  A0
  A2_real

Track B:
  B0
  B2_real
```

Use local official server/platform path.

Run:

```text
public 2025 full local official-server replay
same-window later-half 2025 replay if available
active/zeroed/shuffled ablation for A2_real and B2_real
```

Required outputs:

```text
reference/final_candidate_official_server_results.csv
reference/final_candidate_metric_comparison.csv
reference/final_candidate_ablation_results.csv
reference/final_candidate_robustness_summary.csv

presented/run_csv/final_candidate_official_server_results.csv
presented/run_csv/final_candidate_metric_comparison.csv
presented/run_csv/final_candidate_ablation_results.csv
presented/run_csv/final_candidate_robustness_summary.csv

presented/final_candidate_test_summary.md
traces/final_<track>_<candidate_id>_daily.csv
logs/final_<track>_<candidate_id>.log
```

Each server-result row:

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
proxy_mode
heuristic_fallback_used
fixed_target_replay_used
network_attempted
delta_vs_no_news_sharpe
delta_vs_no_news_return
delta_vs_no_news_drawdown
actual_official_server_or_platform_run
official_submission_run
status
notes
```

Each ablation row:

```text
track
candidate_id
ablation_type
active_real_tensor
zeroed_tensor
date_shuffled_tensor
return
sharpe
turnover
delta_active_minus_zeroed_sharpe
delta_active_minus_shuffled_sharpe
shuffled_beats_active
leakage_suspected
actual_run
notes
```

---

## Stage 4 — Multi-Criteria Final Candidate Decision

Do not use a hard no-news-beating gate.

Use this decision rubric:

```text
performance: Sharpe, return, drawdown
risk: turnover, drawdown, stability
evidence: actual server run, ablation, no-proxy proof
production safety: complexity, dependency, fallback behavior
report value: innovation, interpretability, methodology clarity
robustness: same-window Type-D, rolling/window evidence, active-vs-shuffled
```

Create:

```text
reference/final_candidate_decision_rubric.csv
reference/final_candidate_decision_table.csv
presented/run_csv/final_candidate_decision_table.csv
presented/final_candidate_decision_summary.md
```

Decision statuses:

```text
final_keep
fallback_keep
research_only
report_ablation
reject_for_submission
blocked_evidence_missing
```

Allowed final architecture recommendations:

```text
Track A = A0
Track A = A2_real
Track A = A0 with bounded A2_real overlay
Track B = B0
Track B = B2_real
Track B = B0 with bounded B2_real overlay
```

Decision must state:

```text
why kept
why not kept
what would change the decision
what to claim in report
what not to claim
```

---

## Stage 5 — Final Methodology Report

Write a single comprehensive methodology report:

```text
presented/final_methodology_and_candidate_selection_report.md
```

This report should be concise but complete.

Required sections:

```text
1. Executive Decision
2. Task and Evaluation Context
3. Candidate Families and Naming
4. Final Candidate Shortlist
5. Intended Architecture
6. Actual Code Implementation
7. Intended vs Actual Differences
8. History of Tested Hypotheses and Enhancements
9. Final Validation Results
10. News Tensor / Transformer Evidence
11. Ablation and Leakage Checks
12. Why Some Methods Were Not Used
13. Track A Final Recommendation
14. Track B Final Recommendation
15. Production / Submission Readiness
16. Claims Allowed in System Report
17. Claims Not Allowed
18. Remaining Cleanup Before Submission
```

The report must include compact tables for:

```text
candidate comparison;
intended vs actual method;
history of additions/fixes;
official server result;
ablation result;
final decision.
```

Important report tone:

```text
Evidence-driven.
Do not overclaim.
Clearly separate local public validation from official hidden evaluation.
Clearly say no-news beating is not a hard gate.
Clearly say if a news candidate is selected for robustness/report value rather than pure Sharpe.
```

---

## Stage 6 — System Report Methodology Extract

Create a short methodology extract for the final NLPCC system report:

```text
report/system_report_methodology_extract.md
report/system_report_track_a_final_notes.md
report/system_report_track_b_final_notes.md
```

These should be shorter than the full methodology report and ready to paste into the 2-page report draft.

Must include:

```text
final selected method per track;
concise architecture;
key evidence;
limitations;
do-not-claim warnings.
```

---

## Stage 7 — Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Also run targeted final candidate tests if available or created:

```text
test_final_candidate_server_path
test_real_transformer_no_proxy
test_no_fixed_target_replay
test_news_tensor_ablation
```

Do not run:

```text
pip check
compileall
package build
Docker build
LaTeX finalization
```

Create:

```text
tests/test_command_manifest.csv
tests/test_results_summary.csv
presented/full_test_summary.md
presented/run_csv/test_results_summary.csv
logs/news_overlay_pytest.log
logs/full_pytest_tests_nlpcc.log
logs/full_pytest_tests.log
logs/final_candidate_targeted_tests.log
```

---

## Stage 8 — Presented CSV Package

Create:

```text
presented/run_csv_index.md
presented/run_csv_manifest.csv
```

Minimum files in `presented/run_csv/`:

```text
final_candidate_official_server_results.csv
final_candidate_metric_comparison.csv
final_candidate_ablation_results.csv
final_candidate_robustness_summary.csv
final_candidate_decision_table.csv
test_results_summary.csv
```

`run_csv_manifest.csv` columns:

```text
csv_path
row_count
candidate_ids
tracks
date_range
actual_run
proxy_run
official_server_or_platform_run
real_transformer_executed
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
F. Whole-Repo Evidence Intake
G. History of Hypotheses / Fixes / Enhancements
H. Intended-vs-Actual Code Audit
I. Final Candidate Test Runs
J. Final Candidate Decision
K. Methodology Report
L. System Report Extract
M. Tests
N. Presented CSV Package
O. Failed or Blocked Runs
P. Official Runtime Status
Q. Hidden 2026 / Leakage Check
R. Artifacts
S. Caveats
T. Next Steps
```

Every command entry:

```text
command
return_code
duration_seconds
log_path
```

Every source file read/modified entry:

```text
path
why relevant
change status
```

---

## Final Response Format

Use this exact structure:

```text
Prompt10 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Final candidate decision:
  Track A:
    selected: <A0/A2_real/A0_plus_A2_real_overlay>
    alternate tested: <candidate>
    reason: <short>
  Track B:
    selected: <B0/B2_real/B0_plus_B2_real_overlay>
    alternate tested: <candidate>
    reason: <short>

No-news baseline rule:
  beating no-news as strict guard:
    no
  how no-news was used:
    <diagnostic/reference/fallback>

Actual code vs intended method:
  status: <complete/partial/fail>
  report: <path>

Hypothesis/history audit:
  status: <complete/partial/fail>
  report/table: <path>

Final methodology report:
  path:
    presented/final_methodology_and_candidate_selection_report.md

Final test runs:
  official server rows: <n>
  ablation rows: <n>
  csv package:
    presented/run_csv/

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  targeted final candidate tests: <pass/fail/not_run>

Official submission run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
