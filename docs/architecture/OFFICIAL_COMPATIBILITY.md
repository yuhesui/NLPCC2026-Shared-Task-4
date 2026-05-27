# OFFICIAL_COMPATIBILITY.md

## Official Compatibility Assumptions

- Use the official starter kit as the reference for data access, server execution, and trade schema.
- The official-facing submitted wrapper should be thin and should call `src/nlpcc/`.
- Local tools should be validated against official server behaviour where possible.

## Leakage Safety

Do not use current-day close, high, low, change, or return before decision time. Same-day news must respect the official timestamp cutoff.

## Trade Execution

The official environment uses buy-by-cash and sell-by-holding-percentage semantics. Same-day sell proceeds should not be assumed available for same-day buys. The adapter must validate cash feasibility before submitting orders.

## Dependency Policy

Avoid runtime dependency on external LLM APIs for final B-list execution. If LLM extraction is used, provide cached/frozen/reproducible alternatives and no-LLM fallback.
