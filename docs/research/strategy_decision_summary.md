# Strategy Decision Summary

## 1. Phase 0 Status

Phase 0 is repository scaffold, documentation, cleanup, validation, and pre-strategy setup. The canonical Phase 0 research source is `docs/research/phase0-init.md`.

No full trading strategy is implemented yet. All strategy work after this cleanup must preserve the target-weight-first contract.

## 2. Final Build Policy

Build the simplest reproducible system that passes baseline, leakage, turnover, and ablation checks. Strategies output target weights, not direct official trade payloads. Execution and target-weight-to-trade conversion belong in `src/nlpcc4/execution/trade_converter.py`.

If LLM signals fail ablations, the final submission falls back to S1.

## 3. Strategy Stack

- S0 = Baseline Battery.
- S1 = Robust Quant Core Allocator.
- S2 = Structured LLM Regime-to-Rules Allocator.
- S3 = Risk-Budgeted LLM Alpha-Tilt Optimizer.
- S4 = Event-to-Exposure Sector Mapper.

S1 is the first real strategy to implement after Phase 0 cleanup.

## 4. Track Separation

Track 1 is macro-asset allocation and is prioritized first. Track 2 is sector-rotation allocation and should be attempted only when infrastructure is reusable with low extra cost.

S4 is mainly a Track 2 overlay and should wait until S1-S3 infrastructure is stable.

## 5. Baselines Required Before LLM Work

S0 must establish at least equal weight, inverse-volatility, momentum-only, sector trend-following, persistence, rule-based macro/sector rotation, news sentiment only, and random constrained allocation baselines.

LLM work must not start until baseline runs, leakage checks, turnover reporting, and target-weight conversion tests are in place.

## 6. Ablations Required Before Promotion

Before promoting S2, S3, or S4, run no-LLM, no-news, LLM-scores-only, quant-features-only, fallback-only, higher-friction, and stricter-turnover ablations.

S2 and S3 may use LLMs only through structured bounded JSON signals with schema validation, confidence gating, and fallback to S1.

## 7. Rejected or Deferred Approaches

Do not build pure LLM allocation, multi-agent debate, direct LLM trade generation, early heavy RAG, or public-leaderboard prompt hacks.

Supervised ETF ranking and ensemble submission layers remain deferred until S1-S4 evidence justifies them.

## 8. Build Order

1. Finish Phase 0 cleanup and verification.
2. Confirm official server, demo agent, DataLoader semantics, and trade API semantics.
3. Implement S0 baselines.
4. Implement S1 for Track 1.
5. Add reusable Track 2 infrastructure only where low-cost.
6. Implement S2/S3 structured LLM systems only after S1 is stable.
7. Implement S4 only after S1-S3 infrastructure is stable.

## 9. Final Submission Policy

Submit S1 if structured LLM signals are weak or fail ablations. Submit S3 only if bounded LLM alpha tilts improve validated risk-adjusted performance without excessive turnover or leakage risk.

Submission artifacts must be reproducible and must not include committed raw LLM outputs, caches, generated backtest artifacts, or submission archives.

## 10. Immediate Next Implementation Task

Run official server/demo smoke checks, clarify DataLoader same-day news semantics and trade API cash timing, then implement S0 baselines and S1 infrastructure.
