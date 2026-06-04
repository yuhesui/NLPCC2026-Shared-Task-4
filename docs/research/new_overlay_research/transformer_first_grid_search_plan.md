# Transformer-First News Overlay Grid Search Plan

    ## Transformer-First Grid Search Table

Every implementation and testing prompt must update this table.

| Run ID | Section | Track | N Method | I Method | S Method | Base Config | Transformer Used? | Local Model Required? | Cache Required? | Purpose | Implementation Status | Test Status | 2024 Tune Status | 2025 Frozen Status | GPU Used | Runtime | Sharpe | CumRet | MaxDD | Turnover | Zero-News Pass | Shuffled-News Pass | Lexical Baseline Beat? | Decision | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|

### Mandatory Core Grid

| Run ID | Section | Track | N | I | S | Purpose |
|---|---|---|---|---|---|---|
| G00A | baseline | A | N0 | I0 | S0 | Track A preserved base |
| G00B | baseline | B | N0 | I0 | S0 | Track B preserved base |
| G01A | lexical_control | A | N1 | I1 | S3 | deterministic-only Track A control |
| G01B | lexical_control | B | N1 | I1 | S2 | deterministic-only Track B control |
| G10A | transformer_core | A | N2 | I2 | S3 | BGE relevance + NAI + macro gate |
| G11A | transformer_core | A | N13 | I6 | S13 | aspect-tone + transformer impact + macro sensitivity |
| G12A | transformer_core | A | N2345 | I256 | S13 | full transformer news stack + macro gate |
| G10B | transformer_core | B | N2 | I2 | S2 | BGE relevance + NAI + Rank-IC |
| G11B | transformer_core | B | N12 | I23 | S12 | hybrid relevance + NAI/ESC + CAR/Rank-IC |
| G12B | transformer_core | B | N2345 | I256 | S126 | full transformer/attention Track B stack |
| G13B | transformer_core | B | N6 | I23 | S12 | cross-encoder reranker + impact/sensitivity |
| G14B | transformer_core | B | N5 | I5 | S2 | sector-query attention pooling + Rank-IC |
| G15B | transformer_core | B | N4 | I6 | S2 | label-attention event tagger + aspect impact |
| G20B | higher_capacity | B | N2345 | I256 | S4 | transformer stack + sparse sensitivity |
| G21B | higher_capacity | B | N2345 | I256 | S5 | transformer stack + Black-Litterman views |
| G22B | ablation | B | N7 | I7 | S6 | temporal narrative attention ablation |
| G23B | ablation | B | N8 | I2 | S6 | graph-attention relevance ablation |

### Required Comparison Rule

A transformer/attention candidate must be compared against its lexical-control counterpart:

```text
G10A/G11A/G12A must beat or explain failure relative to G01A.
G10B/G11B/G12B/G13B/G14B/G15B must beat or explain failure relative to G01B.
```

Deterministic-only candidates may remain as fallback, but cannot be declared the Section 1 success condition unless all transformer methods are blocked by unavailable local assets or fail ablation tests.


    ## Search Discipline

    ```text
    1. Run base/null rows.
    2. Run deterministic lexical controls.
    3. Build transformer caches.
    4. Run transformer core rows.
    5. Compare transformer rows against lexical controls.
    6. Only then run frozen 2025 evaluation.
    ```

    ## Success Criteria

    A transformer implementation stage is successful if:

    ```text
    - transformer methods are registered;
    - model availability handling is correct;
    - caches are deterministic;
    - at least one transformer stack can run locally or is honestly blocked by missing local assets;
    - lexical control comparisons are produced;
    - zero-news and shuffled-news ablations exist;
    - no online model downloads occur;
    - 2025 is not used for tuning.
    ```
