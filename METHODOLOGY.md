# METHODOLOGY.md - Method Universe and Execution Stance

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
| belief-state risk parity | Functional MVP / ablation candidate (`bsa_rp`) |
| HMM / Kalman / MPC | Functional one-step MVP / ablation candidate (`hgf_mpc`) |
| sector impact model | Core Track 2 information module |
| KG-MoE / KG-MoE-Lite | Functional lightweight prototype / report candidate unless promoted by full-year evidence |
| retrieval analogue memory | Functional deterministic retrieval-index MVP for ARMOR-OMD support |
| transformer-style event memory | Deferred high-novelty method |
| OCO / online mirror descent ensemble | ARMOR-OMD exponentiated-weight MVP; persistent state optional, not a full OCO proof |
| learning-to-rank | LEEQA-Rank deterministic rank-scoring MVP; not a trained LTR model by default |
| causal/invariant event-impact model | CEVA-KF/CIGA stable-effect graph MVP; not full causal discovery |
| rule-based news extraction | Stage 1 default and no-LLM baseline |
| LLM event extraction | Optional injected callable only; not default |
| offline local text models | Optional BGE-small / FinBERT Chinese extractors; disabled by default with rule-based fallback |
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

Prompt15 added runnable MVPs for the previously deferred high-priority families. Their current evidence is still preliminary unless a report explicitly states full-year 2024 coverage and official-wrapper parity.
