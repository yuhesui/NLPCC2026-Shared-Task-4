# METHODOLOGY.md — Method Universe and Execution Stance

## 1. Core Principle

At the current stage, preserve many plausible methods. Do not narrow prematurely. Methods should be classified as:

- core build;
- secondary build;
- fallback;
- ablation only;
- deferred;
- rejected.

## 2. Method Universe

| Method | Current Role |
|---|---|
| S0 equal weight | Baseline / smoke sanity check |
| S1 quant core | Core fallback and benchmark |
| inverse volatility | Stage 3 risk anchor |
| momentum | Stage 3 baseline signal |
| sector trend-following | Track 2 baseline / core comparator |
| robust Black-Litterman | First serious Track 1 allocation engine |
| risk parity | Robust allocation component and fallback |
| belief-state risk parity | Research stub / deferred |
| HMM / Kalman / MPC | Research stub / deferred |
| sector impact model | Core Track 2 information module |
| KG-MoE / KG-MoE-Lite | Lightweight prototype / ablation-only unless promoted by evidence |
| retrieval analogue memory | Research stub / deferred |
| transformer-style event memory | Deferred high-novelty method |
| OCO / online mirror descent ensemble | OCO-inspired deterministic gating fallback; no persistent online state yet |
| learning-to-rank | Research stub / deferred |
| causal/invariant event-impact model | Research stub / deferred |
| rule-based news extraction | Stage 1 default and no-LLM baseline |
| LLM event extraction | Optional injected callable only; not default |
| no-LLM fallback | Mandatory for B-list robustness |
| generic RAG summariser | Weak baseline / ablation only |
| pure LLM direct allocator | Rejected production design |
| deep RL / graph RL | High-risk deferred method |

## 3. Why Direct LLM Allocation Is Rejected

A direct LLM allocator is prompt-sensitive, difficult to reproduce, weakly risk-controlled, and poorly aligned with turnover/drawdown constraints. The LLM should be an extractor, verifier, mapper, or explainer; final capital allocation should be deterministic and quantitative.

## 4. Promotion Criteria

A method may be promoted only if it:

1. beats or materially complements S1 on 2024 walk-forward / 2025 public A-list tests;
2. does not materially worsen turnover-adjusted Sharpe;
3. has a no-news and no-LLM ablation;
4. has deterministic fallback behaviour;
5. does not depend on post-2025 data or online-only dependencies;
6. produces logs usable for a system report.
