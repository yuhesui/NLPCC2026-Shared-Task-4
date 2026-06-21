# Prompt08 — Major Production Hardening for Phase12 Final Candidates

You are GPT-5.5 Extended Thinking acting as a senior research-code auditor, production-readiness engineer, NLPCC official-runtime tester, and repo-safety reviewer.

## Objective

Harden the current `phase12_final` production path for NLPCC 2026 Shared Task 4.

Default decision: **keep current `phase12_final`**.

Prompt05/06/07b research artifacts are evidence only. Do not promote them unless all explicit production gates below pass. If unsure, keep current production path unchanged.

## Must Read First

Read and summarize before editing:

- `AGENTS.md`
- `README.md`
- `rtk-optimized.md` if present
- `NLPCC_tasks/agent_platform/agents/build_agent.py`
- `NLPCC_tasks/agent_platform/agents/phase12_final_agent.py`
- `NLPCC_tasks/agent_platform/agents/phase12_final_candidate_config.json`
- `NLPCC_tasks/agent_platform/agents/prompt09_real_transformer_agent.py`
- `src/nlpcc/news_overlay/production_tensor.py`
- Prompt04 presented results
- Prompt06 rerun consolidated results
- Prompt07b BGE repair results
- Prompt11 final A2/B2 configs and candidate evidence

## Hard Rules

- Use `rtk python` and `rtk git` where possible.
- No hidden 2026 data.
- No 2025 tuning. 2025 is frozen evaluation only.
- No online API/model download.
- No fake rows, proxy news, fixed target replay, or target leakage.
- A0/B0 are reference controls only.
- Selected final candidates remain:
  - Track A: `A2_real / G11A`
  - Track B: `B2_real / G15B`
- Do not promote Prompt06 alpha branch unless every promotion gate passes.
- Do not modify production agent behavior without writing source/config hash evidence before and after.
- If strict HTTP cannot run, record exact blocker and keep direct official-platform replay separate.

## Output Root

Write all new outputs under:

```text
outputs/reports/next_phase_finetuning_phase12/prompt08_major_production_hardening_phase12/
```

Required subfolders:

```text
presented/
reference/
server_run/
tests/
repo_cleanup/
configs/
logs/
submission_package/
```

## Tasks

### 1. Source and Config Audit

Create:

- `repo_cleanup/source_config_hash_manifest.csv`
- `reference/production_path_source_map.csv`
- `reference/final_candidate_config_audit.csv`

Must show:

- exact files used by `phase12_final`;
- Track A/B routing through `build_agent(strategy='phase12_final')`;
- final candidate IDs, caps, gates, BGE path, and fallback behavior;
- whether Prompt06/07b artifacts are referenced by production code;
- whether production behavior changed in this prompt.

### 2. Official Runtime / HTTP Parity

Try strict HTTP/server decision endpoint replay if available.

Create:

- `server_run/strict_http_parity_results.csv`
- `server_run/direct_official_platform_replay_results.csv`
- `server_run/http_vs_direct_diff.csv`

If strict HTTP is blocked, do not guess. Record:

- command attempted;
- failure type;
- missing dependency/port/path;
- whether direct platform replay still passed.

### 3. Frozen 2025 Production Replay

Run frozen 2025 replay for:

- A0 reference
- B0 reference
- A2_real current `phase12_final`
- B2_real current `phase12_final`

Create:

- `reference/frozen_2025_phase12_production_results.csv`
- `reference/frozen_2025_vs_prompt04_prompt06.csv`

Do not tune on 2025.

### 4. Production-Safe Ablations

Run ablations for A2/B2 current production path:

- active
- zeroed news
- date-shuffled news, at least 5 seeds
- week-block shuffled news
- month-block shuffled news
- branch disabled
- confidence gate disabled
- turnover guard disabled if implemented

Create:

- `reference/production_ablation_results.csv`
- `reference/production_ablation_summary.csv`

Mark whether each ablation is a true rerun or bounded reuse. Do not hide reused rows.

### 5. Optional Research-Artifact Gate Check

Check Prompt06/07b only as research artifacts.

Create:

- `reference/research_artifact_gate_check.csv`

Prompt06/07b can be promoted only if all are true:

- frozen 2025 Sharpe beats current phase12 for same track;
- active beats zeroed;
- active beats mean shuffled;
- active beats block-shuffled;
- official/local production path can load the branch;
- strict HTTP or direct official-platform replay passes;
- no hidden 2026;
- no 2025 tuning.

Expected default: not promoted.

### 6. Package and Environment Checks

Run:

```text
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
rtk python -m compileall src NLPCC_tasks tests
rtk python -m pip check
```

Create:

- `tests/test_results_summary_prompt08.csv`
- `tests/package_check_summary.csv`

If `compileall` or `pip check` is environment-blocked, record exact error type. Do not mark pass.

### 7. Final Submission Package Dry-Run

Create a dry-run manifest only. Do not submit remotely.

Create:

- `submission_package/final_submission_file_manifest.csv`
- `submission_package/submission_readiness_checklist.csv`
- `submission_package/known_submission_gaps.csv`

Checklist must include:

- production agent path;
- config files;
- local model path handling;
- HTTP/direct official path status;
- package checks;
- leakage check;
- reproducibility status;
- remaining blockers.

### 8. Dense Presented Reports

Write:

- `presented/essential_results.md`
- `presented/implementation_log.md`
- `presented/blockers_and_decisions.md`
- `presented/progress_dashboard.md`
- `presented/final_production_hardening_report.md`
- `presented/run_csv_manifest.csv`

## Required Final Response

End with these sections:

```text
A. Production Decision
B. What Changed
C. What Did Not Change
D. Official Runtime / HTTP Status
E. Frozen 2025 Results
F. Ablation Verdict
G. Tests and Package Status
H. Repo Safety
I. Submission Readiness
J. Blockers
K. Next Action
```

## Promotion / Stop Rule

If no branch beats current `phase12_final` with clear frozen 2025 and ablation evidence, stop and keep production unchanged.

If strict HTTP is blocked, do not claim official HTTP parity.

If package checks are environment-blocked, do not claim package-clean.

If Prompt06/07b is not production-loaded, do not claim it is production-ready.
