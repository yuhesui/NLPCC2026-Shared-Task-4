# AGENTS.md - Repository Rules for AI Coding Agents

## 1. Read Order

Before any edit, read:

1. `AGENTS.md`
2. `README.md`
3. `docs/REPO_STRUCTURE.md`
4. `docs/workflow/PROMPT_EXECUTION_PLAN.md`
5. relevant files under `docs/context/`, `docs/architecture/`, and `docs/strategy/`
6. official README files under `NLPCC_tasks/`

## 2. Repository Boundaries

| Area | Rule |
|---|---|
| `NLPCC_tasks/` | Treat as official starter/reference code. Do not rewrite broadly. |
| `NLPCC_tasks/agent_platform/agents/build_agent.py` | Thin official-facing wrapper only. |
| `src/nlpcc/` | Main competition implementation. |
| `src/tools/` | Local development tools: backtesting, optimiser, experiments, reporting, verification. |
| `docs/` | Documentation only. No executable production logic. |
| `data/raw_official/` and official dataset paths | Read-only. Never mutate raw data in place. |
| `outputs/` | Generated artifacts, logs, reports, experiments, submissions. |

## 3. Stage Layout Rule

Each major stage should keep orchestration separate from candidate models:

```text
src/nlpcc/stageX_*/
  pipeline.py      # stage orchestration
  schema.py        # data structures / validation schemas
  validators.py    # safety checks
  models/          # alternative candidate methods
```

## 4. Leakage Rules

- Do not use current-day close/high/low/return before the decision timestamp.
- Same-day news must respect the official timestamp cutoff.
- Prefer official DataLoader semantics for date slicing and current-day masking.
- Do not introduce post-2025 / 2026 data, models, or knowledge into training, retrieval, prompts, or caches.

## 4A. News Overlay Transformer-First Rule

The Prompt1-x News Overlay stage is a research extension and must not silently
replace the frozen official runtime. The preserved official runtime remains:

- Track A primary: `p18_rp_macro_w10_s5`
- Track A fallback: `p18_rp_macro_w40_s5`
- Track B primary: `p18_leeqa_sector_k5_temp35`
- Track B fallback: `p18_s1_sector_t35_v30_w20`

For News Overlay work, deterministic news rules are required only as safety
fallbacks, lexical baselines, sanity controls, ablation comparators, and
official-runtime compatibility guards. They are not sufficient as the main
Section 1 target. Section 1 prompts must implement transformer/attention
interfaces and tests for BGE-style bi-encoder relevance, frozen FinBERT-style
aspect tone, label-attention event tagging, sector-query attention pooling,
cross-encoder reranking where feasible, temporal attention, and hybrid lexical
plus transformer fallback paths.

No prompt may silently download model files or add online API dependencies.
If local transformer assets are unavailable, keep the method interface, config
flags, cache manifest rows, unavailable-state handling, deterministic fallback,
and status rows marked `blocked_missing_local_model`.

## 5. Implementation Log Rule

Every prompt execution must write an implementation log using `create_implementation_log`.

Expected command:

```bash
python scripts/create_implementation_log.py --prompt-id "promptXX" --phase "short_phase_name" --summary "What changed" --files "file1,file2" --tests "tests/checks run" --caveats "known issues" --next-steps "next recommended action"
```

If the helper is missing, create or repair it before finishing the task.

## 6. Testing Rule

Every non-trivial change must include one of:

- tests created or updated;
- a documented smoke check;
- an explicit caveat explaining why testing was not possible.

## 7. No Silent Deletion

Do not silently delete files. If a file is obsolete or unclear, move it to `docs/archived/` only when the prompt asks for cleanup, and record the move in `docs/archived/README.md` and the implementation log.

## 8. Focused Candidate Optimisation Phase Rules

Current phase:

```text
Prompt01 — Pipeline Repair and Full Validation Run
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/
```

Must use:

```text
rtk
rtk python
rtk git
rtk python -m pytest
```

Style:

```text
caveman English for reports and final response
```

Must fix:

```text
G15B zero-overlay pipeline or prove blocked
exact G21B repaired/lite real 2024/2025 rerun
Track A overlay trace inconsistency
missing reference CSV artifacts
dirty-state manifest and no-touch config hashes
```

Do not:

```text
write new Prompt01 outputs under outputs/reports/news_overlay/
use hidden 2026
tune on 2025
edit official runtime configs
run full 212-row matrix
promote to official runtime
download new models
call online APIs
```
