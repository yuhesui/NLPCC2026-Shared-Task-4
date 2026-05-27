# IMPLEMENTATION_PLAN.md

## Completed

- Deep research reports.
- Strategy synthesis.
- Four-stage modular architecture.
- Starter documentation kit.
- Revised prompt execution plan with `src/nlpcc/` and `src/tools/` separation.

## Build Order

1. `prompt00` — repository reset, documentation migration, skeleton, implementation-log helper.
2. `prompt01` — environment/data setup and official/local smoke pipeline.
3. `prompt02` — contracts, leakage guard, metrics, official/local comparison.
4. `prompt03` — Stage 3 trade processing and S0/S1 baselines.
5. `prompt04` — tools layer: backtester, optimiser, experiments, reporting, verification.
6. `prompt05` — Stage 1 news processing MVP.
7. `prompt06` — Stage 2 text store MVP.
8. `prompt07` — robust BL/risk parity engine.
9. `prompt08` — Track 2 sector rotation system.
10. `prompt09` — OCO fallback and conservative ensemble.
11. `prompt10` — ablations and experiments.
12. `prompt11` — verification and fixes.
13. `prompt12` — full pipeline and packaging.

## Stop Criteria

Stop and repair if:

- official and local smoke paths disagree materially without explanation;
- leakage guard detects current-day close/high/low/return usage;
- raw official data is mutated;
- `create_implementation_log` is missing after `prompt00`;
- docs and actual package paths disagree.
