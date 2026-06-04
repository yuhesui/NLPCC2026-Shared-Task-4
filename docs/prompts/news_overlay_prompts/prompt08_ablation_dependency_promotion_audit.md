# Prompt08 — Ablation, Dependency, Leakage, and Promotion Audit

    ## Role

    You are a senior transformer model-risk auditor, quantitative validation lead, official-semantics parity reviewer, and dependency/security auditor.

    ## Instructions

    Audit transformer News Overlay candidates after grid execution. Determine which methods are useful, ablation-only, blocked by local assets, or rejected.

    ## Context

You are working on the next-stage **News Overlay** phase for the NLPCC 2026 Shared Task 4 repository.

Project:

```text
NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
```

Tracks:

```text
Track A / Track 1: Macro-Asset Allocation
Track B / Track 2: Sector-Rotation Allocation
```

Frozen official runtime must remain unchanged unless a later human-approved promotion prompt explicitly reopens it:

```text
Track A primary:   p18_rp_macro_w10_s5
Track A fallback:  p18_rp_macro_w40_s5
Track B primary:   p18_leeqa_sector_k5_temp35
Track B fallback:  p18_s1_sector_t35_v30_w20
```

This prompt set has two sections:

```text
Section 1: implement methods and integrate them into the pipeline.
Section 2: test methods, run grid pipelines, run ablations, verify/fix, and cross-check.
```

This stage is **transformer-first**. Deterministic methods remain required, but only as fallback, baseline, sanity-control, and ablation methods.


    ## Read-First Discovery Protocol

Do not blindly assume fixed file paths. First discover the repository structure, then read the latest equivalent files.

Prioritise these categories:

```text
1. current official runtime configs and preserved candidate configs;
2. Prompt20 current-state dossier and preserved-candidate summary;
3. Prompt0B / Prompt01–Prompt11 News Overlay design notes if present;
4. existing Stage 1 news-processing code;
5. existing Stage 2 text-store code;
6. existing Stage 3/4 trading and execution code;
7. existing official-semantics backtester and target-tensor tools;
8. existing scripts, tests, config conventions, and implementation-log utility.
```

Minimum items or equivalents to locate:

```text
AGENTS.md
README.md
docs/
docs/news_overlay/ if present
outputs/reports/prompt20/presented/current_repo_status_report.md
outputs/reports/prompt20/presented/preserved_candidate_summary.md
outputs/reports/prompt20/presented/next_stage_news_text_overlay_workflow.md
configs/preserved_candidates/
configs/prompt18_final_candidates.json
src/nlpcc/
src/tools/backtesting/
src/tools/experiments/
tests/
```

If a file is missing, use the nearest current equivalent and record the substitution in the progress report.




    ## Tasks

    ### Audit Questions
Answer whether transformer candidates beat deterministic controls, frozen 2025 generalises, shuffled-news degrades, zero-news collapses to base, transformer features materially change weights, Track A acts as risk control, Track B improves ranking, dependencies are explicit, CPU fallback works, and official-server parity is required before promotion.

### Required Ablations
Run or verify base-only, lexical control, transformer real-news, no-news, zero-news, shuffled-news, random labels, random embeddings, lexical-only, dense-only, aspect-tone off, label-attention off, sector-query attention off, temporal attention off, impact gate off, sensitivity gate off, confidence gate off, overlay strength sweep, and turnover cap sweep.

### Dependency Audit
Verify no silent downloads, offline mode, configurable local model paths, missing-model status, reproducible cache manifests, package exclusion of model binaries, and dependency manifest.

### Leakage Audit
Verify 2024-only training/selection, frozen 2025 testing, price-field masking, news cutoff, cache label safety, and target trace safety.

### Promotion Gate
Candidate may be labelled promotion_candidate only if it improves over preserved baseline and lexical control, survives ablations, does not materially worsen drawdown/turnover, has deterministic fallback, has acceptable dependencies, passes local official-semantics replay, and still requires human approval.


    ## Examples

    Classification examples:
```text
N2345-I256-S126 = research_continue if 2024 improves but 2025 is weak.
N12-I23-S12 = ablation_supported if embedding relevance improves mapping and shuffled-news degrades.
N6-I23-S12 = blocked_missing_local_reranker if interface exists but no local model asset is present.
```


    ## Artifact and Reporting Policy

Use this report tree unless the repository already has a compatible News Overlay report structure:

```text
outputs/reports/news_overlay/prompt01_11/
  README.md
  progress/
  presented/
  reference/
```

Required core artifacts:

```text
outputs/reports/news_overlay/prompt01_11/reference/method_implementation_table.csv
outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv
outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv
outputs/reports/news_overlay/prompt01_11/reference/cache_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv
outputs/reports/news_overlay/prompt01_11/reference/dependency_manifest.md
outputs/reports/news_overlay/prompt01_11/reference/leakage_audit.md
outputs/reports/news_overlay/prompt01_11/reference/error_log.md
```

Keep large generated files under:

```text
.var/news_overlay_prompt01_11/
  cache/
  target_tensors/
  grid_runs/
  checkpoints/
  benchmarks/
  logs/
```

Create an implementation log for every prompt:

```text
docs/implementation_logs/<timestamp>_news_overlay_prompt01_11_<short_name>.md
```


    ## Non-Negotiable Constraints

```text
- Do not change the frozen official runtime.
- Do not automatically promote a News Overlay candidate.
- Use 2024 only for construction, training, parameter selection, and threshold selection.
- Use 2025 only for frozen evaluation after 2024 selection is complete.
- Do not use hidden 2026 data.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must respect the official timestamp cutoff.
- Do not use online APIs.
- Do not silently download models.
- Do not include Hugging Face or other model binaries in the official runtime package.
- Keep a deterministic no-model fallback for every transformer method.
- Do not overclaim transformer value unless ablations prove it.
- Do not use legacy or non-official-semantics backtesters for final selection evidence.
- Do not modify raw official data.
```


    ## Expected Output

    End with:
```text
Ablation status: <pass/partial/fail>
Dependency audit status: <pass/partial/fail>
Leakage audit status: <pass/partial/fail>
Transformer methods with evidence: <list>
Ablation-only methods: <list>
Rejected/deferred/blocked methods: <list>
Promotion recommendation: <no_promotion / research_continue / parity_ready_but_human_review_required>
Next prompt: prompt09_verify_fix_transformer_errors.md or prompt10_external_cross_check.md
```
