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
