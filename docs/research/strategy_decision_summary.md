# Strategy Decision Summary

This is the cleaned implementation-oriented summary for S0-S4. It replaces brainstorming notes with decisions that should guide coding.

## Final Strategy Stack

- S0: Baseline Battery for sanity checks, performance floors, and regression tests.
- S1: Robust Quant Core Allocator. This is the first real strategy and the default fallback.
- S2: Structured LLM Regime-to-Rules Allocator. The LLM emits bounded regime JSON only.
- S3: Risk-Budgeted LLM Alpha-Tilt Optimizer. The LLM emits bounded alpha scores that tilt S1.
- S4: Event-to-Exposure Sector Mapper. Mainly a Track 2 overlay after core infrastructure is stable.

## Track Separation

- Track 1 is macro-asset allocation across broad assets, bond/gold-like defensive assets, and macro categories.
- Track 2 is sector rotation across industry-themed ETFs.
- Shared portfolio construction, risk controls, metrics, LLM schemas, and trade conversion should live in shared modules.
- Track-specific universe definitions, regime maps, and exposure matrices should remain separate.

## Baseline Requirements

S0 must include:

- equal weight,
- inverse-volatility,
- momentum-only,
- sector trend-following,
- persistence,
- rule-based macro/sector rotation,
- news sentiment only,
- random constrained allocation.

Baselines must run before any LLM performance claim is accepted.

## S1 Requirements

S1 should be implemented first and should output target weights. Core components:

- inverse-volatility allocation,
- multi-horizon momentum,
- momentum breadth,
- defensive sleeve for Track 1 if allowed by task mechanics,
- sector trend-following for Track 2,
- no-trade zone,
- turnover cap.

If S1 cannot beat simple baselines in robust validation, refine S1 before building S2 or S3.

## LLM Strategy Requirements

S2 and S3 may use LLMs only through structured bounded JSON. Invalid, low-confidence, contradictory, or out-of-schema output must fall back to S1.

Before using LLM signals, validate:

- schema validity rate,
- confidence calibration,
- no direct trade or final-weight authority,
- no future-data leakage,
- incremental value over S1 and non-LLM ablations,
- turnover and cost robustness,
- reproducibility with cached prompts and deterministic parsing.

## S4 Requirements

S4 should be attempted only after S1-S3 infrastructure is stable. Before Track 2 event mapping, validate:

- a fixed event taxonomy,
- deterministic event-to-sector or event-to-ETF exposure matrix,
- confidence gating,
- fallback to sector trend-following,
- improvement over Track 2 baselines after transaction costs.

## Required Ablations

- no LLM,
- LLM scores only,
- quant features only,
- no news input,
- no regime classifier,
- fallback only,
- doubled friction cost,
- stricter turnover cap,
- Track 1 and Track 2 separate evaluations.

## Rejected or Deferred Approaches

Do not implement in early phases:

- pure LLM end-to-end allocation,
- direct LLM trade generation,
- multi-agent debate,
- heavy RAG,
- leaderboard-tuned prompt hacks,
- supervised ETF ranking model,
- ensemble submission layer.

These can be revisited only after S1-S4 evidence shows a reproducible need.

## Build Order

1. Repository structure, logging, docs, and artifact policy.
2. S0 baselines and target-weight contract tests.
3. S1 robust quant core for Track 1, then Track 2.
4. Trade converter and official API integration.
5. S2 structured regime JSON with fallback to S1.
6. S3 bounded alpha tilts if S2/S1 infrastructure is stable.
7. S4 Track 2 event overlay only if sector baselines leave room.

## Final Submission Policy

- Prefer the simplest strategy that passes validation and ablations.
- Use S1 as the fallback and reproducibility anchor.
- Include S2/S3/S4 only if each improves risk-adjusted performance after costs without excessive turnover or leakage risk.
- Package only executable, reproducible code and required documentation.
- Keep raw LLM outputs, caches, generated run artifacts, and submission zips out of Git.
