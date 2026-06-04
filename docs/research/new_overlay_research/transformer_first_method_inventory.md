# Transformer-First News Overlay Method Inventory

    ## Method Codes — Transformer-First Three-Substage Architecture

### Substage N — News Analysis / Embedding / Relevance

| Code | Method | Priority | Role |
|---|---|---|---|
| N0 | no-news / base-only input | control | base/null |
| N1 | deterministic taxonomy + entity/BM25 relevance | fallback | lexical baseline only |
| N2 | BGE-style bi-encoder text-to-sector relevance cache | required | main transformer relevance method |
| N3 | frozen FinBERT-style aspect-tone classifier | required | contextual tone/aspect feature |
| N4 | label-attention / Title2Event-inspired event tagger | required | transformer event typing and argument extraction |
| N5 | sector-query attention daily news pooling | required | attention aggregation over daily Top-20 news |
| N6 | cross-encoder sector reranker gate | recommended | high-precision second-stage relevance |
| N7 | temporal lagged-news attention encoder | recommended | narrative persistence over lagged news |
| N8 | entity-sector graph-attention propagation | ablation/defer | indirect sector relevance |
| N12 | N1 + N2 lexical/embedding hybrid | required | robust hybrid relevance |
| N13 | N1 + N3 lexical/aspect-tone hybrid | required | robust hybrid tone |
| N2345 | N2 + N3 + N4 + N5 transformer-stack | required | primary transformer-first stack |

### Substage I — News Impact Estimation

| Code | Method | Priority | Role |
|---|---|---|---|
| I0 | zero impact | control | null |
| I1 | deterministic event magnitude | fallback | baseline only |
| I2 | Permutation-Tested News Attention Index, PT-NAI | required | transparent index |
| I3 | event-study calibrated impact | required | CAR/CAAR impact calibration |
| I4 | decay-weighted event persistence | required | persistence and novelty control |
| I5 | impact-gated attention pooling | required | attention impact aggregation |
| I6 | transformer aspect-impact aggregator | required | FinBERT/aspect-aware impact score |
| I7 | temporal narrative impact encoder | recommended | lagged narrative impact |
| I23 | I2 + I3 NAI plus event-study impact | required | robust impact core |
| I256 | I2 + I5 + I6 attention/aspect impact stack | required | transformer-impact stack |

### Substage S — ETF / Sector News Sensitivity and Overlay Use

| Code | Method | Priority | Role |
|---|---|---|---|
| S0 | no sensitivity / uniform sensitivity | control | null |
| S1 | CAR/CAAR event-study sensitivity matrix | required | event-class sensitivity |
| S2 | Rank-IC Gated Sector News Momentum | required | Track B signal validation |
| S3 | Volatility-Scaled Macro News Risk Gate | required | Track A risk gate |
| S4 | Sparse Event-Sensitivity Regression Overlay | required | data-driven sensitivity |
| S5 | Black-Litterman News View Overlay | recommended | Bayesian view overlay |
| S6 | attention-weighted asset sensitivity pooling | required | transformer/attention sensitivity |
| S7 | cross-sectional transformer score-to-tilt gate | ablation | learned score-to-overlay |
| S12 | S1 + S2 event-study sensitivity + Rank-IC | required | Track B first robust gate |
| S13 | S1 + S3 event-study sensitivity + macro risk | required | Track A first robust gate |
| S126 | S1 + S2 + S6 sensitivity stack | required | transformer-aware Track B gate |


    ## Main Revision

    Deterministic methods are not removed, but they are demoted to fallback and controls. The actual Section 1 implementation target is:

    ```text
    N2345 + I256 + S126
    ```

    where:

    ```text
    N2345 = BGE/bi-encoder relevance + FinBERT aspect tone + label-attention event tagger + sector-query attention pooling
    I256 = PT-NAI + impact-gated attention pooling + transformer aspect-impact aggregator
    S126 = CAR/CAAR sensitivity + Rank-IC gate + attention-weighted asset sensitivity
    ```

    ## Primary Candidate Stacks

    | Stack | Track | Purpose |
    |---|---|---|
    | N2-I2-S3 | A | BGE relevance + macro NAI risk gate |
    | N13-I6-S13 | A | aspect-tone + transformer impact + macro sensitivity |
    | N2345-I256-S13 | A | full transformer news stack + macro risk gate |
    | N2-I2-S2 | B | BGE relevance + NAI + Rank-IC |
    | N12-I23-S12 | B | hybrid lexical/embedding + event-study sensitivity |
    | N2345-I256-S126 | B | full transformer/attention sector stack |
    | N6-I23-S12 | B | cross-encoder reranker + event-study gate |
    | N5-I5-S2 | B | sector-query attention pooling + Rank-IC |
