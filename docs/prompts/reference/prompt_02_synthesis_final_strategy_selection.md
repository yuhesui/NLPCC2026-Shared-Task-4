# Prompt 02 — Synthesis: Final Strategy Selection from Deep Research Reports

## Role and Objective

You are a senior quantitative research lead, LLM-systems architect, and shared-task strategy judge.

You are given several independent deep-research reports for **NLPCC 2026 Shared Task 4: “LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market.”**

Your task is to synthesize the reports into a final, implementation-ready, award-oriented strategy decision document.

Do **not** redo the full research from scratch.  
Do **not** merely average the reports.  
Do **not** reward rhetorical sophistication without implementability.  
Do **not** blindly prefer strong LLM APIs.  
Do **not** keep a design just because it sounds novel.

You must identify which designs should actually be built, which should be used only for report narrative or ablation, and which should be rejected.

The synthesis must explicitly compare:

1. competition value,
2. research / system-report value,
3. hidden B-list robustness,
4. one-student implementation feasibility,
5. report quality and reliability of the input reports.

---

## Input Reports

Read all attached reports carefully:

1. `DeepResearch_ChatGPT.md`
2. `DeepResearch_Perplexity1.md`
3. `DeepResearch_Perplexity2.md`
4. `DeepResearch_Perplexity3.md`
5. `DeepResearch_Gemini-_21.md`

Treat the reports as research inputs, not authoritative truth.

Some reports may:

- overstate novelty,
- use inconsistent notation,
- contain weak citations,
- hallucinate paper details,
- understate implementation cost,
- overfit to the prompt wording,
- make unsupported performance claims,
- or recommend different first-build priorities.

Your job is to audit them, weight them, consolidate them, and produce a final strategy plan.

---

## Official Task Context to Preserve

The official task constraints must remain central:

- Track 1: Macro-Asset Allocation.
- Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / agent construction.
- 2025 data is public A-list / Phase A evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by the organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is only usable under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- If using training, fine-tuning, retrieval, or knowledge construction, the full data, preprocessing, dependencies, and reproducible environment must be submitted.
- Creative or especially informative system reports may be selected even if not top-ranked.

Do not convert uncertain or report-specific claims into official facts unless supported by official sources.

---

## Designs to Consolidate

The reports use different names for overlapping ideas. Consolidate carefully.

You must explicitly consider the following design families:

1. DRO-BL / DRO-BL-RP / robust Black-Litterman.
2. BSA-RP / belief-state risk-parity allocator.
3. HGF-MPC / hidden Gaussian drift / Kalman-HMM model-predictive control.
4. KG-MoE / graph mixture-of-experts sector allocator.
5. TEMA / TEMA-RP / RAMA-T / transformer event memory.
6. ARMOR-SPO / OMD-RAG / retrieval analogue + online update.
7. OCO-Bandit / OCO-Ensemble / online mirror descent allocator.
8. LEEQA / LLM event extraction + learning-to-rank allocator.
9. CEVA-KF / CIRM / CIGA / causal invariant event-impact model.
10. Regime-HMM-RP / hidden-regime risk-parity allocator.
11. Pure LLM direct allocator.
12. Simple BL with LLM views but no robustness.
13. Heavy deep RL or end-to-end graph RL.
14. Generic RAG summariser.

You may merge names where the mathematical engine is effectively the same.

---

## Required Output Sections

Use exactly these sections:

A. Input Report Quality Audit  
B. Cross-Report Consensus and Disagreement  
C. Design Consolidation Map  
D. Final Design Shortlist  
E. Quantitative Strategy Benchmark  
F. Report / Paper Quality Benchmark  
G. Competition vs Research Frontier  
H. Recommended Final Architecture Stack  
I. Implementation Priority and Phase Plan  
J. Rejection, Deferral, and Ablation-Only List  
K. Final Recommendation  

---

## A. Input Report Quality Audit

Create a quantitative quality audit of each input report.

Use this table:

| Report | Official-Source Fidelity | Research-Citation Quality | Mathematical Specificity | Implementation Realism | Novelty Insight | Robustness Awareness | Scoring Discipline | Overclaiming Risk | Synthesis Utility | Suggested Weight |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

Use 0–10 scores.

Definitions:

- Official-Source Fidelity: correctly reflects task mechanics, data split, leakage rules, execution, submission constraints.
- Research-Citation Quality: uses credible and relevant papers rather than vague references.
- Mathematical Specificity: states variables, update rules, portfolio objective, risk control, turnover logic.
- Implementation Realism: feasible for one strong student and compatible with organiser-run B-list.
- Novelty Insight: provides genuinely distinctive architecture ideas.
- Robustness Awareness: handles 2026 hidden B-list, prompt instability, turnover, data compliance, and fallback.
- Scoring Discipline: uses conservative scoring and does not cluster everything too high.
- Overclaiming Risk: higher means worse.
- Synthesis Utility: how useful the report is for final decision-making.
- Suggested Weight: how much weight this report should receive in the final synthesis, summing to 1.00.

After the table, explain:

1. Which report is most reliable.
2. Which report is most creative.
3. Which report is most implementation-realistic.
4. Which report is most likely to overclaim.
5. Which report contributes the best mathematical ideas.
6. Which report contributes the best roadmap.

---

## B. Cross-Report Consensus and Disagreement

Create a table:

| Topic | Consensus | Disagreement | Final Synthesis Decision |
|---|---|---|---|

Topics must include:

- Best Track 1 design.
- Best Track 2 design.
- Best one-student design.
- Best performance-first design.
- Best research/award design.
- Whether DRO-BL should be built first.
- Whether BSA-RP should be built first.
- Whether KG-MoE is worth implementing.
- Whether TEMA/RAMA-T is implementation-worthy.
- Whether causal/invariant models should be core or report-only.
- Whether online learning/OCO should be a core fallback.
- Whether direct LLM allocation should be rejected.
- Whether API-heavy systems should be avoided for B-list.

Use the reports’ own recommendations explicitly.

---

## C. Design Consolidation Map

Create a table:

| Original Design Name(s) | Source Report(s) | Consolidated Name | Status | Reason |
|---|---|---|---|---|

Status must be one of:

- Core build,
- Secondary build,
- Track-specific build,
- Report-centrepiece,
- Baseline only,
- Ablation only,
- Defer,
- Reject.

Consolidate overlapping names. For example:

- DRO-BL, DRO-BL-RP, robust BL → one consolidated design.
- TEMA, TEMA-RP, RAMA-T → one consolidated design unless retrieval and transformer-memory are materially different.
- CEVA-KF, CIRM, CIGA → one causal/invariant event-impact family.
- OMD-RAG, ARMOR-SPO, retrieval analogue meta-allocator → one retrieval/meta-allocation family unless the report gives a strong reason to separate them.
- BSA-RP, Regime-HMM-RP, HGF-MPC should be separated only if their mathematical engines differ enough:
  - BSA-RP: belief-state + risk parity.
  - HGF-MPC: latent drift/Kalman/HMM + MPC.
  - Regime-HMM-RP: simple HMM + allocation templates.

---

## D. Final Design Shortlist

Produce 5–7 final designs only.

For each final design, include:

- final name,
- thesis,
- mathematical engine,
- LLM role,
- portfolio engine,
- track fit,
- competition edge,
- research/report edge,
- implementation burden,
- main failure risk,
- one-student feasibility,
- final status.

Use this table:

| Final Design | Thesis | Engine | LLM Role | Track 1 Fit | Track 2 Fit | Competition Edge | Report Edge | Burden | Main Risk | Status |
|---|---|---|---|---:|---:|---|---|---:|---|---|

The shortlist should include:

- at least one performance-first design,
- at least one Track 1 design,
- at least one Track 2 design,
- at least one report/award-centrepiece design,
- at least one safe fallback.

---

## E. Quantitative Strategy Benchmark

Create a strategy scoring table.

Required columns:

| Design | Track 1 Fit | Track 2 Fit | Sharpe Potential | Drawdown Control | Turnover Efficiency | B-list Robustness | Novelty | Mathematical Depth | Interpretability | Reproducibility | Feasibility | Baseline-Beating Probability | Report/Paper Signal | Overfit Risk | Tool Dependency Risk | Data Compliance Risk | Competition Score | Research/Award Score | Overall ROI | Final Rank |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

Use 0–10 scoring.

Higher is better except:

- Overfit Risk,
- Tool Dependency Risk,
- Data Compliance Risk.

Use these formulas:

```text
Competition Score =
0.18 * SharpePotential
+ 0.14 * DrawdownControl
+ 0.12 * TurnoverEfficiency
+ 0.20 * BListRobustness
+ 0.16 * BaselineBeatingProbability
+ 0.10 * Reproducibility
+ 0.10 * Feasibility
- 0.10 * OverfitRisk
- 0.05 * ToolDependencyRisk
- 0.05 * DataComplianceRisk
```

```text
Research/Award Score =
0.18 * Novelty
+ 0.16 * MathematicalDepth
+ 0.14 * Interpretability
+ 0.12 * ReportPaperSignal
+ 0.10 * Reproducibility
+ 0.10 * BListRobustness
+ 0.08 * Feasibility
+ 0.06 * max(Track1Fit, Track2Fit)
+ 0.06 * BaselineBeatingProbability
- 0.06 * OverfitRisk
- 0.04 * ToolDependencyRisk
- 0.02 * DataComplianceRisk
```

```text
Overall ROI =
0.45 * Competition Score
+ 0.40 * Research/Award Score
+ 0.15 * Feasibility
- 0.05 * OverfitRisk
- 0.03 * ToolDependencyRisk
- 0.02 * DataComplianceRisk
```

Do not cluster all final designs between 7 and 9.

Use the full scoring range where justified.

Penalise high implementation burden, 2025-overfit risk, API dependency, and vague novelty.

Reward deterministic post-processing, fallback-to-S1 ability, clean ablations, and report clarity.

After the table, explain:

1. Why the top-ranked design is top-ranked.
2. Why the best research design may differ from the best competition design.
3. Which designs are likely to beat S1.
4. Which designs are unlikely to justify implementation.
5. Which designs should be implemented only if the baseline is already strong.

---

## F. Report / Paper Quality Benchmark

This section is mandatory and should be separate from strategy scoring.

Evaluate each final design as a potential system-report or shared-task-paper contribution.

Use this table:

| Design | Core Paper Thesis | Visualisability | Ablation Cleanliness | Mathematical Explainability | Novelty Beyond Baselines | Failure-Case Insight | Reproducibility Narrative | Likelihood of Being Selected as Creative/Informative | Report Quality Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

Use 0–10 scoring.

Definitions:

- Core Paper Thesis: whether the design can be expressed as a concise, compelling thesis.
- Visualisability: whether the design can produce good plots/tables, such as belief trajectories, graph activations, view-confidence maps, event-memory attention, or regret curves.
- Ablation Cleanliness: whether the design supports strong no-news / no-LLM / no-risk / no-memory / no-graph ablations.
- Mathematical Explainability: how cleanly the design can be presented with formulas.
- Novelty Beyond Baselines: how clearly it differs from simple momentum, sentiment, or S1.
- Failure-Case Insight: whether failures teach something interesting.
- Reproducibility Narrative: whether the report can explain full Docker/log/config reproducibility.
- Likelihood of Being Selected: estimate based on creativity, informativeness, and clarity.
- Report Quality Score: weighted aggregate.

Use this formula:

```text
Report Quality Score =
0.16 * CorePaperThesis
+ 0.12 * Visualisability
+ 0.14 * AblationCleanliness
+ 0.14 * MathematicalExplainability
+ 0.16 * NoveltyBeyondBaselines
+ 0.10 * FailureCaseInsight
+ 0.10 * ReproducibilityNarrative
+ 0.08 * SelectionLikelihood
```

Then identify:

1. Best report centrepiece.
2. Best performance-paper hybrid.
3. Best visual system.
4. Best ablation story.
5. Best fallback report if performance is weak.
6. Designs that sound novel but would produce weak reports.

---

## G. Competition vs Research Frontier

Classify final designs into four quadrants:

1. High competition / high research.
2. High competition / low research.
3. Low competition / high research.
4. Low competition / low research.

Also create a second frontier using:

- x-axis: Competition Score,
- y-axis: Report Quality Score.

State:

- best final submission candidate,
- best report centrepiece,
- safest fallback,
- highest-upside/risk idea,
- best Track 1 candidate,
- best Track 2 candidate.

---

## H. Recommended Final Architecture Stack

Propose a final layered system.

Required layers:

### Layer 0 — Official Data and Leakage Layer

- official DataLoader only,
- date-split policy,
- same-day news cutoff,
- no current-day close/high/low/return,
- no 2026 resources,
- data compliance guard.

### Layer 1 — Baseline and Risk Core

- equal weight,
- inverse-volatility,
- momentum,
- sector trend-following,
- S1 quant core,
- drawdown control,
- turnover control,
- fallback-to-S1.

### Layer 2 — Information Engine

Choose exact components from the shortlisted designs:

- event extractor,
- view generator,
- belief-state updater,
- graph engine,
- retrieval analogue engine,
- causal verifier,
- or local text encoder.

### Layer 3 — Mathematical Allocation Engine

Choose exact components:

- risk parity,
- Black-Litterman,
- DRO,
- OCO,
- Kalman/HMM,
- MoE router,
- ranking model,
- causal/invariant model.

### Layer 4 — Explanation and Report Engine

- daily decision trace,
- belief-state plots,
- view-confidence maps,
- graph activation diagrams,
- event-to-asset attribution,
- turnover and drawdown diagnostics,
- ablation summaries.

### Layer 5 — Submission and Reproducibility Layer

- Docker,
- dependency lock,
- config freeze,
- deterministic seeds,
- local model weights or cached extraction,
- no external API dependency if possible,
- B-list crash fallback.

State exactly which parts are agentic and which parts must remain deterministic.

---

## I. Implementation Priority and Phase Plan

Give an implementation sequence:

### Phase 0R — Source/Data Reset

Deliverables, time estimate, success criterion, stop criterion.

### Phase 1R — Official Starter Reproduction

Deliverables, time estimate, success criterion, stop criterion.

### Phase 2R — S0/S1 Baseline Rebuild

Deliverables, time estimate, success criterion, stop criterion.

### Phase 3R — First Innovative Prototype

Select exactly one first prototype and justify it.

### Phase 4R — Second Prototype / Track Extension

Select exactly one second prototype and justify it.

### Phase 5R — A-list Evaluation and Ablation

Define controlled 2025 usage and overfit guard.

### Phase 6R — B-list Hardening and Report Draft

Define Docker, fallback, logging, and report deliverables.

For each phase, include:

| Phase | Build | Deliverable | Time | Promotion Criterion | Stop Criterion |
|---|---|---|---|---|---|

---

## J. Rejection, Deferral, and Ablation-Only List

Create a table:

| Design | Status | Reason | Condition for Revival |
|---|---|---|---|

Must include:

- pure LLM allocator,
- simple BL with LLM views but no robustness,
- generic RAG summariser,
- multi-agent debate,
- heavy fine-tuning,
- deep RL / graph RL,
- overly complex causal model,
- full KG-MoE if baseline is weak,
- transformer memory if event extraction is unstable.

Be critical.

---

## K. Final Recommendation

End with a concrete final build plan.

Use exactly this format:

```text
## Final Build Plan

- Primary competition candidate:
- Primary research / award candidate:
- Safe fallback:
- Best Track 1 design:
- Best Track 2 design:
- First prototype to implement:
- Second prototype to implement:
- Designs to reject:
- Designs to keep as ablations:
- Minimum ablation package:
- Final submission policy:
- System report thesis:
```

Be decisive. Do not end with vague alternatives.
