# REPO_POLICY.md

## Main Policy

- `NLPCC_tasks/` is official starter/reference code.
- `src/nlpcc/` is the reusable competition implementation.
- `src/tools/` is local research/development infrastructure.
- `docs/` is documentation only.
- `outputs/` is generated artifacts.
- `data/` stores copied/symlinked datasets, manifests, and derived data. Raw official data must remain immutable.

## Import Boundary

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
  may import src/nlpcc/

src/nlpcc/
  should not depend on src/tools/ by default

src/tools/
  may import src/nlpcc/ for experiments, reporting, and verification
```

## Track Separation

Use shared stage modules and track-specific configs. Put only truly track-specific logic under `src/nlpcc/tracks/` or specific final-agent models.
