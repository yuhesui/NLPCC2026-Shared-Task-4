# TRACK_DESIGN.md

## Track 1 — Macro-Asset Allocation

Primary build path:

```text
BL view extraction
→ BL view store + confidence matrix
→ covariance / inverse-vol / momentum / breadth
→ robust Black-Litterman + risk parity + S1 fallback
```

## Track 2 — Sector-Rotation Allocation

Primary build path:

```text
sector impact extraction
→ sector impact panel / lightweight graph
→ sector trend + volatility + correlation state
→ sector rotation agent + optional KG-MoE-Lite
```

## Shared Modules

- leakage guard;
- official data adapter;
- target-weight to official-trade adapter;
- local backtester;
- metrics;
- S0/S1 baselines;
- OCO/conservative fallback.

## When to Fork Logic

Fork by track only when the asset universe, feature semantics, or allocation rule is materially different. Prefer shared stage modules and track-specific configs.
