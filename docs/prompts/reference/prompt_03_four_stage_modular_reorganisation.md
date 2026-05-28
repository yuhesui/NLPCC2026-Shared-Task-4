# Prompt 03 鈥?Four-Stage Modular Strategy Reorganisation

## Role and Objective

You are a senior quantitative research lead and LLM-systems architect.

You have already reviewed several deep-research reports for **NLPCC 2026 Shared Task 4: 鈥淟LM-based Investment Advisor Agents for Asset Allocation in the Chinese Market.鈥?*

Your new task is **not** to propose another undifferentiated list of complete strategies.

Your task is to reorganise all proposed strategies into a modular four-stage architecture:

1. **News Processing**
2. **Quantified Text Data Storage Medium**
3. **Trade Data Processing**
4. **Final Trading Agent**

You must compare candidate methods separately within each stage, then synthesize the best stage-wise combinations into final buildable systems.

The goal is to move from strategy-name brainstorming to an implementation architecture where each module has a clear input, output, benchmark, ablation, and replacement policy.

---

## Official Task Context

Preserve the official task constraints:

- Track 1: Macro-Asset Allocation.
- Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / agent construction.
- 2025 data is public A-list / Phase A evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- If using training, fine-tuning, retrieval, or knowledge construction, the full data, preprocessing, dependencies, and reproducible environment must be submitted.
- Creative or especially informative system reports may be selected even if not top-ranked.

Do not convert uncertain report claims into official facts unless supported by official sources.

---

## Key Reorganisation Requirement

The previous reports describe many full-strategy names:

- DRO-BL / DRO-BL-RP
- BSA-RP
- HGF-MPC
- KG-MoE
- TEMA / RAMA-T
- ARMOR-SPO / OMD-RAG
- OCO-Bandit / OCO-Ensemble
- LEEQA
- CEVA-KF / CIRM / CIGA
- Regime-HMM-RP
- Pure LLM allocator
- Simple BL with LLM views
- Generic RAG summariser
- Deep RL / graph RL

You must decompose these into stage-level components.

For example:

- **TEMA** is mainly:
  - News Processing: event extraction
  - Quantified Text Storage: event memory / transformer-style KV memory
  - Final Agent: event-memory allocator

- **DRO-BL** is mainly:
  - News Processing: view extraction
  - Quantified Text Storage: view matrix and confidence matrix
  - Trade Data Processing: covariance / prior-return estimation
  - Final Agent: robust Black-Litterman optimiser

- **KG-MoE** is mainly:
  - News Processing: entity and sector relation extraction
  - Quantified Text Storage: dynamic knowledge graph
  - Trade Data Processing: sector volatility / correlation / momentum
  - Final Agent: graph MoE allocator

- **ARMOR-SPO / OMD-RAG** is mainly:
  - News Processing: embedding / event tagging
  - Quantified Text Storage: retrieval index / analogue memory
  - Trade Data Processing: base allocator performance states
  - Final Agent: online meta-allocator

Do this decomposition explicitly.

---

## Required Output Sections

Use exactly the following sections:

A. Four-Stage Architecture Definition  
B. Stage-Level Candidate Map  
C. Stage-Level Quantitative Comparison  
D. Cross-Stage Compatibility Matrix  
E. Final Modular System Designs  
F. Stage-Specific Ablation Plan  
G. Implementation Repository Mapping  
H. Recommended Build Order  
I. Final Decision  

---

## A. Four-Stage Architecture Definition

Define the four stages precisely.

For each stage, include:

- purpose,
- input,
- output,
- allowed data,
- forbidden data,
- leakage risks,
- reproducibility risks,
- success metric,
- fallback behavior.

Use this table:

| Stage | Purpose | Input | Output | Main Risk | Fallback |
|---|---|---|---|---|---|

The four stages are:

### Stage 1 鈥?News Processing

Raw Top-20 news 鈫?structured textual signals.

Candidate outputs may include:

- event tuples,
- news summaries,
- sector tags,
- macro regime tags,
- direction scores,
- confidence scores,
- horizon labels,
- source reliability scores,
- uncertainty flags.

### Stage 2 鈥?Quantified Text Data Storage Medium

Structured textual signals 鈫?a persistent or queryable quantitative representation.

Candidate storage media may include:

- daily event table,
- decayed event memory,
- key-value memory,
- embedding index,
- retrieval analogue database,
- belief-state vector,
- regime posterior,
- ETF-sector-policy knowledge graph,
- Black-Litterman view matrix,
- causal event-impact graph,
- factor exposure panel.

### Stage 3 鈥?Trade Data Processing

Official price and portfolio data 鈫?quantitative market state.

Candidate outputs may include:

- returns,
- volatility,
- covariance,
- momentum,
- drawdown,
- breadth,
- liquidity proxies,
- correlation graph,
- risk budgets,
- previous weights,
- turnover capacity,
- current cash / holdings state.

### Stage 4 鈥?Final Trading Agent

Text state + trade state 鈫?target weights / official trades.

Candidate final agents may include:

- risk parity allocator,
- robust Black-Litterman optimiser,
- distributionally robust optimiser,
- HMM / Kalman / belief-state controller,
- graph MoE allocator,
- retrieval analogue meta-allocator,
- OCO / mirror descent allocator,
- learning-to-rank allocator,
- causal invariant allocator,
- conservative ensemble.

---

## B. Stage-Level Candidate Map

Create four separate candidate tables, one for each stage.

For each stage-level candidate, include:

| Candidate | Originating Full Strategy | Mathematical Object | Output Schema | Track 1 Fit | Track 2 Fit | Keep / Merge / Reject | Reason |
|---|---|---|---|---:|---:|---|---|

You must include at least the following candidates.

### Stage 1 鈥?News Processing Candidates

- simple news summarisation,
- sentiment classification,
- event tuple extraction,
- macro regime classification,
- sector impact extraction,
- view extraction for Black-Litterman,
- causal shock extraction,
- entity / sector / ETF mapping,
- news denoising and relevance filtering,
- LLM self-consistency / verifier-based extraction.

### Stage 2 鈥?Quantified Text Storage Candidates

- daily flat feature table,
- decayed event memory,
- transformer-style key-value event memory,
- retrieval analogue index,
- regime posterior / belief state,
- Black-Litterman view store,
- ETF-sector-policy knowledge graph,
- causal event-impact graph,
- text-managed factor panel,
- uncertainty / confidence matrix.

### Stage 3 鈥?Trade Data Processing Candidates

- equal weight state,
- inverse-volatility state,
- multi-horizon momentum,
- sector trend state,
- covariance / shrinkage covariance,
- drawdown state,
- breadth state,
- HMM regime state from prices,
- graph correlation state,
- turnover and cash feasibility state,
- baseline allocator performance state.

### Stage 4 鈥?Final Trading Agent Candidates

- S1 quant core,
- risk parity,
- robust Black-Litterman,
- distributionally robust optimiser,
- belief-state risk parity,
- Kalman/HMM MPC,
- graph MoE,
- retrieval meta-allocator,
- online mirror descent / OCO,
- learning-to-rank allocator,
- causal invariant allocator,
- conservative ensemble,
- direct LLM allocator as rejected baseline.

---

## C. Stage-Level Quantitative Comparison

Compare candidates within each stage separately.

Do **not** use the same criteria for every stage.

### Stage 1 鈥?News Processing Scoring

Use:

| Candidate | Extraction Accuracy | Prompt Stability | Schema Validity | Financial Specificity | Noise Filtering | Track 1 Fit | Track 2 Fit | Cost | Reproducibility | Overall Stage 1 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### Stage 2 鈥?Quantified Text Storage Scoring

Use:

| Candidate | Information Retention | Temporal Memory | Mathematical Cleanliness | Queryability | Robustness | Interpretability | Reproducibility | Track 1 Fit | Track 2 Fit | Overall Stage 2 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### Stage 3 鈥?Trade Data Processing Scoring

Use:

| Candidate | Predictive Usefulness | Leakage Safety | Risk Relevance | Turnover Usefulness | Robustness | Simplicity | Track 1 Fit | Track 2 Fit | Overall Stage 3 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### Stage 4 鈥?Final Trading Agent Scoring

Use:

| Candidate | Sharpe Potential | Drawdown Control | Turnover Efficiency | B-list Robustness | Mathematical Depth | Interpretability | Feasibility | Report Signal | Overfit Risk | Overall Stage 4 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

Use 0鈥?0 scoring.

Higher is better except:

- Cost,
- Overfit Risk.

Be conservative.

---

## D. Cross-Stage Compatibility Matrix

Create a compatibility matrix.

Rows: Stage 2 storage media.  
Columns: Stage 4 final trading agents.

Score compatibility from 0鈥?0.

Must include at least:

### Stage 2 Rows

- daily flat feature table,
- decayed event memory,
- key-value event memory,
- retrieval analogue index,
- regime posterior / belief state,
- Black-Litterman view matrix,
- knowledge graph,
- causal event-impact graph.

### Stage 4 Columns

- S1 quant core,
- risk parity,
- robust Black-Litterman,
- belief-state risk parity,
- HMM / Kalman MPC,
- graph MoE,
- retrieval meta-allocator,
- OCO / mirror descent,
- learning-to-rank,
- causal invariant allocator.

After the matrix, identify:

1. Best high-performance pairings.
2. Best research-report pairings.
3. Best one-student pairings.
4. Incompatible pairings to avoid.
5. Pairings that sound good but are redundant.

---

## E. Final Modular System Designs

Construct 5鈥? final modular system designs.

Each design must be expressed as a four-stage pipeline:

```text
News Processing
鈫?Quantified Text Storage Medium
鈫?Trade Data Processing
鈫?Final Trading Agent
```

For each final system, include:

| System | Stage 1 News Processing | Stage 2 Text Storage | Stage 3 Trade Processing | Stage 4 Final Agent | Track Fit | Main Edge | Main Risk | Build Priority |
|---|---|---|---|---|---|---|---|---|

Required final systems:

1. Performance-first Track 1 system.
2. Performance-first Track 2 system.
3. Best one-student robust system.
4. Best research / award system.
5. Best fallback-safe system.
6. Highest-upside but risky system.
7. Ablation/control system.

For each system, explain:

- why the stage combination is coherent,
- what each stage contributes,
- what can be swapped out,
- how fallback to S1 works,
- how it should be evaluated.

---

## F. Stage-Specific Ablation Plan

Create an ablation matrix.

Rows should be systems.

Columns should be stage ablations:

- no news processing,
- simple sentiment instead of event extraction,
- no text storage / same-day only,
- flat feature table instead of memory / graph / view matrix,
- no trade-data processing except previous weights,
- no volatility scaling,
- no turnover control,
- no final optimiser, score-to-weight only,
- no LLM,
- S1 fallback only.

Use this table:

| System | Critical Stage | Required Ablation | Expected Effect | Red Flag if... |
|---|---|---|---|---|

Then define the minimum ablation package for:

1. competition submission,
2. system report,
3. debugging,
4. B-list hardening.

---

## G. Implementation Repository Mapping

Map the four stages to repo modules.

Propose a file/module structure such as:

```text
src/nlpcc/
  news_processing/
  text_store/
  trade_processing/
  agents/
  portfolio/
  execution/
  reports/
```

For each directory, specify:

- responsibility,
- inputs,
- outputs,
- what should not be placed there,
- test files,
- report artifacts.

Also map to configs:

```text
configs/
  news_processing/
  text_store/
  trade_processing/
  agents/
  systems/
```

Include a table:

| Stage | Source Directory | Config Directory | Tests | Reports |
|---|---|---|---|---|

---

## H. Recommended Build Order

Give a concrete build order.

The build order must respect the four-stage architecture.

Use:

### Phase 0R 鈥?Reset and Data Contract

### Phase 1R 鈥?Official Starter Reproduction

### Phase 2R 鈥?Stage 3 Trade Data Processing + S0/S1 Baselines

Build trade data processing before fancy news.

### Phase 3R 鈥?Stage 1 News Processing MVP

Build event extraction and schema validation.

### Phase 4R 鈥?Stage 2 Text Storage MVP

Build the simplest useful storage medium first.

### Phase 5R 鈥?Stage 4 Final Agent Prototype

Build the first final agent.

### Phase 6R 鈥?Integrated Modular Systems and Ablations

Compare modular combinations.

### Phase 7R 鈥?A-list Package and B-list Hardening

For each phase, include:

| Phase | Focus Stage | Deliverable | Time Estimate | Success Criterion | Stop Criterion |
|---|---|---|---|---|---|

---

## I. Final Decision

End with a decisive recommendation.

Use this exact format:

```text
## Final Modular Recommendation

- Best Stage 1 news processing method:
- Best Stage 2 quantified text storage medium:
- Best Stage 3 trade data processing method:
- Best Stage 4 final trading agent:
- First complete four-stage system to build:
- Second system to build:
- Best Track 1 system:
- Best Track 2 system:
- Best research / award system:
- Best fallback if text signal is weak:
- Modules to reject:
- Modules to keep only as ablations:
- System report thesis:
```
