## Your Role

You are GPT-5.5 High Thinking acting as:

```text
senior quantitative research engineer
official-runner porting engineer
Optuna hyperparameter tuning lead
time-split validation auditor
NLPCC LNCS system-report writer
evidence-quality auditor
single implementation-log writer
```

Your job is to finish **Prompt06** by combining:

```text
1. multi-strategy hyperparameter tuning;
2. corrected same-window Type-D actual runs;
3. porting top candidates into the official runner / trading-agent location;
4. retesting through the official-facing local runner;
5. drafting Track-A and Track-B 2-page NLPCC system reports using the official template.
```

Keep this prompt short and result-focused. Do not write long generic reports. Every claimed run must have CSV evidence.

---

## Phase

```text
Prompt06 — Multi-Strategy Tuning, Official Runner Port, and System Report Draft
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt06_tuning_official_runner_report/
```

Use only needed subfolders:

```text
presented/
reference/
logs/
traces/
optimiser/
configs/
runner_port/
report/
```

---

## One Implementation Log Only

Write exactly one Prompt06 implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt06_tuning_official_runner_report/presented/implementation_log.md
```

Do not write a `docs/implementation_logs/` copy.  
Do not create duplicate Prompt06 logs.  
If further edits happen in Prompt06, update this same log in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt06_logs_created = false
```

---

## Hard Rules

```text
Use rtk, rtk python, rtk git, rtk python -m pytest.
Use project .venv RTK Python.
No hidden 2026.
No online API for model inference.
No new model download.
No official-server submission.
No official runtime promotion.
Do not delete prior evidence.
Do not call a proxy run actual.
Do not reuse Prompt05 tables as new Prompt06 runs.
Do not overwrite official starter code broadly.
Use thin adapters/wrappers for official runner integration.
```

Package checks:

```text
Run tests and compileall.
Run pip check; if it fails from known environment conflicts, record environment_blocked and continue.
```

---

## Input State

Read Prompt05 outputs first.

Known best research branches:

```text
Track A research: A2 G11A V0
Track B research: B2 G15B V4
References: A0 G00A, B0 G00B
Secondary if useful: A1 G12A V3, B3 G21B repaired_lite
```

Prompt05 gaps to fix:

```text
same-window Type-D correction still needed;
top configs need official-facing runner replay;
system report needs direct LNCS draft, not just outline.
```

Official template/reference locations to inspect:

```text
docs/NLPCC2026 - Template/
  llncs.cls
  splncs04.bst
  samplepaper.tex
  llncsdoc.pdf
  readme.txt
```

Also inspect official starter/runner files:

```text
NLPCC_tasks/
agent_platform/agents/
agent_platform/demo_backtest.py
server_platform/
config.py
start_server.py
runner/ or runners/ if present
```

If both `runner/` and `agent_platform/agents/` exist, identify which is the official trading-agent location and explain choice.

---

## Candidate Pool

Primary run set:

```text
A0 G00A
A2 G11A V0
B0 G00B
B2 G15B V4
```

Secondary if runtime allows:

```text
A1 G12A V3
B3 G21B repaired_lite
```

Do not run the full 212-row matrix.

---

## Stage 1 — Environment Check

Run:

```bash
rtk --version
rtk python -c "import sys, optuna; print(sys.executable); print(optuna.__version__)"
rtk git status
rtk git diff --name-only
```

If Optuna is not visible, stop and mark `blocked_optuna_env`.

Write:

```text
reference/environment_verification.csv
presented/environment_summary.md
```

---

## Stage 2 — Multi-Strategy Tuning

Compare at least three tuning strategies for A2 and B2:

```text
S1_optuna_tpe:
  TPESampler, robust scalar objective.

S2_optuna_random:
  RandomSampler, same budget, same objective.

S3_stability_first:
  TPESampler with stronger stability + turnover penalties.

Optional S4_pruned_tpe:
  TPE with pruner if already available and safe.
```

Budget:

```text
minimum 100 trials per primary news branch per strategy
same seed policy
same train/test definitions
```

Objective components:

```text
Sharpe
return
max drawdown penalty
turnover penalty
overlay magnitude sanity
same-window D1-H2 validation
baseline diagnostic delta
```

Required outputs:

```text
optimiser/tuning_strategy_manifest.csv
optimiser/tuning_strategy_trials.csv
optimiser/tuning_strategy_best_configs.csv
presented/tuning_strategy_comparison_summary.md
```

Presented summary must include top rows from the CSV.

---

## Stage 3 — Same-Window Type-D Correction

Run corrected Type-D on the same later-half 2025 test window.

```text
D1-H2:
  train/tune = 2024 only
  test = later-half 2025

D2-H2:
  train/tune = 2024 + first-half 2025
  test = same later-half 2025
```

Use exact split:

```text
first_half_2025 = earliest 50% trading dates in 2025
later_half_2025 = remaining 50% trading dates in 2025
```

Run for:

```text
A0, A2, B0, B2
optional A1, B3
```

Required outputs:

```text
reference/typed_same_window_d1_h2_results.csv
reference/typed_same_window_d2_h2_results.csv
reference/typed_same_window_more_data_comparison.csv
presented/typed_same_window_summary.md
traces/typed_same_window_<candidate_id>_<d1h2_or_d2h2>.csv
```

Each comparison row must include:

```text
candidate_id
track
d1_h2_sharpe
d2_h2_sharpe
d2_minus_d1_h2_sharpe
d1_h2_return
d2_h2_return
d2_minus_d1_h2_return
d1_h2_max_drawdown
d2_h2_max_drawdown
d1_h2_turnover
d2_h2_turnover
more_data_helped_sharpe
more_data_helped_return
actual_run
proxy_run
official_valid
research_only
interpretation
```

---

## Stage 4 — Port Top Candidates to Official Runner / Trading Agent

Goal: start moving from `src/` research code into the official-facing trading-agent location.

Do not broad-rewrite official starter kit. Use thin adapters.

Required work:

```text
1. Discover official trading-agent entrypoint.
2. Port A0, A2, B0, B2 into official-facing local runner.
3. Keep A1/B3 optional as secondary if simple.
4. Keep all candidate configs under Prompt06 output configs plus thin official adapter.
5. Ensure runner can select Track A vs Track B and candidate id.
6. Ensure no hidden 2026 and no same-day leakage.
```

Likely locations to inspect and use:

```text
NLPCC_tasks/agent_platform/agents/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/server_platform/
NLPCC_tasks/config.py
runner/ or runners/ if present
```

Required outputs:

```text
runner_port/official_runner_location_audit.csv
runner_port/ported_candidate_manifest.csv
runner_port/official_agent_adapter_summary.md
configs/official_runner_track_a_a0.yaml
configs/official_runner_track_a_a2.yaml
configs/official_runner_track_b_b0.yaml
configs/official_runner_track_b_b2.yaml
presented/official_runner_port_summary.md
```

If source files are modified, record exact paths and rollback plan.

Do not claim official readiness until official-facing local replay passes.

---

## Stage 5 — Official-Facing Local Replay

Run the ported candidates through the official-facing local runner / demo runner, not only the internal research backtester.

Minimum actual replay set:

```text
Track A:
  A0 no-news reference
  A2 best research branch

Track B:
  B0 no-news reference
  B2 best research branch
```

Use:

```text
2024 tune/selection config frozen;
2025 local public replay;
same official DataLoader / server semantics where available.
```

Required outputs:

```text
reference/official_runner_replay_results.csv
reference/official_runner_replay_metric_comparison.csv
presented/official_runner_replay_summary.md
traces/official_runner_<track>_<candidate_id>_daily.csv
logs/official_runner_<track>_<candidate_id>.log
```

Each row must include:

```text
track
candidate_id
candidate
runner_path
config_hash
date_start
date_end
return
sharpe
max_drawdown
turnover
mean_abs_overlay
delta_vs_no_news_sharpe
actual_official_runner_replay
official_server_run
official_valid
notes
```

Important labels:

```text
actual_official_runner_replay = true only if runner/demo/server path was used
official_server_run = false
official_valid = local_public_validation_only
```

If official runner replay fails, mark `blocked_official_runner_port` and give exact error.

---

## Stage 6 — System Report Drafts in Official Template

Write actual report drafts, not only outlines.

Use the LNCS/NLPCC template files in:

```text
docs/NLPCC2026 - Template/
```

Create separate Track A and Track B drafts:

```text
report/system_report_track_a_2page.tex
report/system_report_track_b_2page.tex
report/system_report_combined_short.tex
report/system_report_key_tables.md
report/system_report_requirements.md
presented/system_report_draft_summary.md
```

Use `llncs.cls` style and keep drafts intended for no more than 2 pages each.

Report content must include:

```text
agent architecture design
core innovation strategy: prompt/research workflow, news processing, risk control, tuning
experiments: Type-B, Type-C, corrected Type-D, official-facing local replay
reflection: news is useful as research/regime overlay; no-news reference remains strong unless CSV proves otherwise
future work: official parity, B-list robustness, regime gate, cache/logging
```

Report rules:

```text
Do not claim official results.
Do not claim news beats no-news unless CSV supports it.
Do not include hidden 2026.
Use compact tables only.
Use separate Track A and Track B evidence where appropriate.
```

Also create a plain-language abstract for each track:

```text
report/track_a_abstract.md
report/track_b_abstract.md
```

---

## Stage 7 — Final Candidate Synthesis

Create:

```text
reference/final_prompt06_candidate_synthesis.csv
reference/final_prompt06_decision_table.csv
presented/final_candidate_decision_summary.md
presented/final_next_phase_recommendation.md
```

Decision questions:

```text
Which tuning strategy worked best for A2?
Which tuning strategy worked best for B2?
Did same-window Type-D show more data helps?
Did official-facing local replay match research backtest?
Should A2/B2 stay research branches, become regime/ensemble candidates, or be dropped?
Are A0/B0 still safer submission references?
What exact run is needed before official parity prep?
```

Allowed statuses:

```text
no_news_reference
best_research_branch
official_runner_candidate
ensemble_candidate
regime_candidate
report_only_ablation
blocked_official_runner_port
blocked_run_failed
```

Do not use:

```text
official_promotion_ready
official_parity_ready
```

---

## Stage 8 — Tests and Checks

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
rtk python -m compileall src tests
rtk python -m pip check
```

Also run any official-runner smoke tests needed.

Write:

```text
reference/full_checks_summary.csv
presented/full_test_summary.md
logs/*.log
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
F. Environment / Optuna Status
G. Tuning Strategy Comparison
H. Same-Window Type-D Runs
I. Official Runner Port
J. Official-Facing Local Replay
K. System Report Drafts
L. Final Candidate Synthesis
M. Tests and Package Checks
N. Failed or Blocked Runs
O. Official Runtime Status
P. Hidden 2026 / Leakage Check
Q. Artifacts
R. Caveats
S. Next Steps
```

---

## Final Response Format

Use this exact structure:

```text
Prompt06 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Tuning strategies:
  status: <complete/partial/fail>
  strategies: <list>
  trials: <count>
  best A2 strategy: <id>
  best B2 strategy: <id>
  csv: <path>

Same-window Type-D:
  status: <complete/partial/fail>
  actual_run: <yes/no>
  rows: <n>
  more data helped:
    <yes/no/mixed>
  csv: <path>

Official runner port:
  status: <complete/partial/fail/blocked>
  runner path: <path>
  candidates ported: <list>

Official-facing local replay:
  status: <complete/partial/fail/blocked>
  rows: <n>
  csv: <path>

System report drafts:
  status: <complete/partial/fail>
  Track A draft: <path>
  Track B draft: <path>
  Combined draft: <path>

Best current research branches:
  Track A: <candidate + reason>
  Track B: <candidate + reason>

Submission-safe references:
  Track A: G00A
  Track B: G00B

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  compileall: <pass/fail/not_run>
  pip check: <pass/fail/environment_blocked/not_run>

Official runtime changed?
  no

Official server run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
