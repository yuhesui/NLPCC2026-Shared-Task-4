/goal Finish NLPCC Phase 1-2 end-to-end: integrate branches, optimize on 2024 only, run frozen 2025 evaluation, clean repo, port final candidates to actual agent path, test official server/platform, and write final dense report.

You are GPT-5.5 xHigh in Codex Goal mode. Act as research-code lead, official-agent engineer, validation auditor, repo-cleanup operator, and methodology writer.

Root output folder:
`outputs/reports/next_phase_finetuning_phase12/prompt04_goal_integrate_optimize_official_clean/`

Dense monitor folder:
`presented/` with `implementation_log.md`, `progress_dashboard.md`, `essential_results.md`, `blockers_and_decisions.md`, `final_methodology_report.md`, `submission_gap_summary.md`, `run_csv_manifest.csv`, `run_csv/`.

Context to read first:
- AGENTS.md, README.md, RTK instructions.
- Prompt00/01/02 under `outputs/reports/next_phase_finetuning_phase12/`.
- Prompt03a and Prompt03b branch folders if present.
- Prompt11 A2/B2 configs, source maps, official traces.

Hard rules:
Use `rtk`, `rtk python`, `rtk git`. Verify RTK env. No hidden 2026. No 2025 tuning. No online API. No model download. A2_real/B2_real stay selected; A0/B0 reference only. No proxy/fake news, fixed replay, or heuristic production fallback. If a branch is missing/blocked, use best valid fallback and state why.

Main goal:
Finish the run, not just research. Select best valid frozen variant per track from Prompt02/03a/03b, optimize only on 2024, evaluate frozen on 2025, run official server/platform, port to actual agent location, clean repo safely, run tests, and write final report.

Required stages:
1. Intake: build branch manifest for Prompt02, Prompt03a, Prompt03b. Classify each artifact as valid, blocked, partial, or unsafe.
2. Candidate assembly: create final candidate configs for A2_real and B2_real variants: base Prompt11, Prompt02 shallow-fusion, BGE branch if valid, event/aspect branch if valid, and combined branch if both valid.
3. Optimize: tune overlay/calibration/gates on 2024 only. No 2025 checkpoint/config/threshold selection. Record all trials and frozen config hashes.
4. Frozen test: run 2025 public evaluation once per frozen candidate/config. Include A0/B0 reference rows.
5. Ablations: active, zeroed, shuffled-date, branch-disabled, confidence-gate-disabled, and turnover-guard-disabled for final A2/B2.
6. Official path: port selected configs/code to actual agent location, usually `NLPCC_tasks/agent_platform/agents/` and wrapper. Ensure real local model path, no proxy/fixed replay. Run local official server/platform; strict HTTP if available, else closest official path and explain.
7. Repo cleanup: quarantine stale files only when safe. Do not silently delete. Update docs/AGENTS/README with final paths if needed.
8. Tests: run news_overlay, tests_nlpcc, and full tests if feasible. Run compileall/pip check if feasible; mark environment_blocked if not.
9. Final report: write dense methodology, code-vs-intent, results, ablations, official-server status, allowed/not-allowed claims, and next actions.

Required outputs:
- `reference/branch_artifact_manifest.csv`
- `configs/final_phase12_candidate_manifest.csv`
- `optimiser/final_2024_trials.csv`
- `reference/frozen_2025_results.csv`
- `reference/final_ablation_results.csv`
- `server_run/official_server_or_http_results.csv`
- `repo_cleanup/repo_cleanup_manifest.csv`
- `tests/test_results_summary_prompt04.csv`
- `presented/final_methodology_report.md`
- `presented/submission_gap_summary.md`
- copy key CSVs to `presented/run_csv/`.

Completion criteria:
Pass if final A2/B2 configs are ported to actual agent path, 2024 optimization and frozen 2025 evaluation are evidenced, official run is attempted/logged, tests are run or honestly blocked, and report is complete. Final answer must give selected variants, official path status, tests, hidden 2026=no, 2025 tuning=no, and best next action.
