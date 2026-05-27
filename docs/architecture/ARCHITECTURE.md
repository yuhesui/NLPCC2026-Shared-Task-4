# ARCHITECTURE.md

## High-Level Graph

```text
Official DataLoader / Server APIs
        │
        ▼
src/nlpcc/core/                    src/tools/data_tools/
        │                                  │
        ▼                                  ▼
Stage 1 — News Processing          Local manifests / dataset checks
        │
        ▼
Stage 2 — Quantified Text Store
        │
        ▼
Stage 3 — Trade Data Processing
        │
        ▼
Stage 4 — Final Trading Agent
        │
        ▼
src/nlpcc/execution/official_adapter.py
        │
        ▼
Official trade payloads / local backtester orders
```

## Deterministic vs Agentic Components

| Component | Deterministic? | Notes |
|---|---:|---|
| leakage guard | Yes | Must be deterministic. |
| price features | Yes | No LLM dependency. |
| optimiser / allocator | Yes | Deterministic given config/seed. |
| rule-based extraction | Yes | Preferred fallback. |
| LLM extraction | No / controlled | Must be cached, versioned, and replaceable. |
| direct LLM allocation | Rejected | Allowed only as rejected baseline / ablation. |
