# ABLATION_PLAN.md

## Baseline Suite

| Baseline | Purpose |
|---|---|
| S0 equal weight | sanity lower bound |
| inverse volatility | risk-adjusted baseline |
| momentum | simple price signal |
| sector trend | Track 2 hurdle |
| S1 quant core | main fallback and benchmark |
| no-news | tests whether text adds value |
| no-LLM | tests dependency-free performance |

## Required Ablations

| System | Ablation |
|---|---|
| robust BL | no BL views; no confidence matrix; no turnover control; no risk parity anchor |
| sector rotation | no sector news; no graph; trend-only; equal-sector weights |
| OCO ensemble | no text sleeves; no S1 sleeve; no turnover penalty |
| news extraction | rule-based only; sentiment only; no denoising; no LLM |
| text store | flat table only; no memory; no confidence; no retrieval |

## Report Tables

Generate tables for:

- cumulative return;
- Sharpe;
- max drawdown;
- annualised volatility;
- turnover;
- fallback frequency;
- ablation delta versus S1;
- official-local consistency.
