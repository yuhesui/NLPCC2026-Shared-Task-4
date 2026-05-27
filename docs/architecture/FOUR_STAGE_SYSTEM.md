# FOUR_STAGE_SYSTEM.md

## Stage 1 — News Processing

Raw Top-20 news becomes structured textual signals.

Candidate models live under `src/nlpcc/stage1_news/models/`.

| Candidate | Status |
|---|---|
| rule-based extraction | fallback / no-LLM baseline |
| sentiment classification | ablation only |
| event tuple extraction | core |
| BL view extraction | core for robust BL |
| sector impact extraction | core for Track 2 |
| LLM event extraction | secondary, controlled |
| direct news-to-weight generation | rejected |

## Stage 2 — Quantified Text Store

Structured text becomes quantitative state.

| Candidate | Status |
|---|---|
| flat feature table | core MVP |
| BL view store | core for robust BL |
| confidence matrix | core support |
| decayed event memory | secondary |
| retrieval index | secondary/deferred |
| knowledge graph | Track 2 secondary/report |
| causal graph | report-centrepiece/deferred |

## Stage 3 — Trade Data Processing

Official price/portfolio data becomes risk state.

| Candidate | Status |
|---|---|
| equal weight | S0 baseline |
| inverse volatility | core baseline |
| momentum | core baseline |
| sector trend | Track 2 core baseline |
| covariance / shrinkage covariance | core |
| drawdown / breadth / turnover state | core |
| price HMM state | secondary |

## Stage 4 — Final Trading Agent

Text state and trade state become target weights and official trades.

| Candidate | Status |
|---|---|
| smoke one-unit agent | smoke test only |
| S0 equal weight | baseline |
| S1 quant core | core fallback |
| robust BL | first serious Track 1 engine |
| risk parity | core component |
| sector rotation | Track 2 build |
| KG-MoE-Lite | Track 2 report/secondary |
| OCO ensemble | fallback/meta-allocator |
| causal invariant | report/deferred |
| direct LLM allocator | rejected |
