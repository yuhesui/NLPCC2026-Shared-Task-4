# Prompt03 — Implement Transformer News Architectures

    ## Role

    You are a senior Chinese financial NLP engineer, transformer retrieval engineer, attention-model architect, local-model integration engineer, and model-risk reviewer.

    ## Instructions

    Implement Substage N methods. Do not stop at deterministic taxonomy. N1 is only fallback and lexical baseline; the main target is N2/N3/N4/N5 and N2345 as real, cache-backed, traceable methods.

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

    ### Architecture Target
Substage N answers what the news says, what event type it is, which asset or sector it concerns, what aspect/tone it carries, and which daily news items deserve attention.

### N0 — No-News Control
Return empty features and allow base allocator to run unchanged.

### N1 — Deterministic Taxonomy + Entity/BM25 Relevance
Implement Chinese financial keyword/entity extraction, taxonomy rules, lexical/BM25 relevance, duplicate clustering, and fallback path.

### N2 — Bi-Encoder Relevance Cache
Implement BGE/sentence-transformer-style local bi-encoder support. Encode news and sector prototypes, compute cosine relevance, batch on GPU when available, cache outputs, and require explicit local model configuration.

### N3 — Frozen FinBERT-Style Aspect-Tone Classifier
Classify aspect-specific tone for policy, regulation, demand, liquidity, earnings, geopolitics, and risk. Cache probabilities and signed tone scores.

### N4 — Label-Attention / Title2Event-Inspired Event Tagger
Define event-label descriptions, score news against labels, infer event arguments where feasible, and output event probabilities and confidence.

### N5 — Sector-Query Attention Daily News Pooling
Construct sector queries and news keys/values. Compute attention over daily Top-20 news per sector and output attention weights.

### N6/N7/N8
Implement cross-encoder reranker interface, temporal lagged-news attention, and graph-attention propagation scaffold or lightweight implementation.

### Composite Methods
Implement N12, N13, and N2345 with component traces.

### Required Output Schema
Each feature row must include timestamp/cutoff safety, event probabilities, relevance by asset/sector, aspect tone, label attention scores, sector-query attention weights, cache key, model status, device, fallback flag, method code, and warnings.

### Tests
Test N1 extraction, N2 missing-model and cache, N3 aspect schema, N4 label scoring, N5 attention normalisation, N6 unavailable status, N7 short history, composite traces, and no network access in offline mode.


    ## Examples

    Synthetic headline:
```text
央行宣布降准释放长期流动性，券商与银行板块受关注
```
Expected rough behaviour:
```text
event_type = monetary_easing / liquidity_support
likely sectors = bank, brokerage, broad_market
tone = positive for liquidity-sensitive financial sectors
confidence = high if taxonomy and transformer labels agree
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
Substage N status: <pass/partial/fail>
Implemented transformer methods: <list>
Blocked or deferred methods: <list with reason>
Cache/model status: <pass/partial/fail>
Tests run: <commands and pass/fail>
Updated tables: <paths>
Next prompt: prompt04_transformer_impact_architectures.md
```
