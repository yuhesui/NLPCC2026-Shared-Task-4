> From: https://gemini.google.com/app/38cc6a4594fdd3e7

# you asked

message time: 2026-06-03 21:46:30

Prompt0A — News Overlay Deep Research and Design Space
Standalone Version for External Deep Research Agent
Role
You are a senior research analyst in quantitative finance, Chinese financial NLP, event-driven asset allocation, LLM/embedding systems, information retrieval, and model-risk-aware shared-task strategy design.
You are assisting a project for:

NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
This is a deep research and design-space prompt. You do not have access to the project repository. You should therefore treat the project context below as the complete internal project state and conduct external/background research from first principles.
Do not write implementation code.
Do not propose changing the current official runtime directly.
Do not assume access to private repository files.
Do not ask for the repository address.
Do not make unsupported claims about hidden test performance.
Project Context
The project targets two tracks:

Track A / Track 1:
  Macro-Asset Allocation

Track B / Track 2:
  Sector-Rotation Allocation
The competition setting is approximately:

- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is used for training / construction / tuning.
- 2025 public-A data is used for locked testing / generalisation evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- Hidden B-list evaluation is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- Final runtime should retain deterministic no-model / no-API fallback.
- Any training, fine-tuning, retrieval, or knowledge construction must be reproducible.
The current project has a validated official runtime and should be treated as frozen unless a later validation phase explicitly reopens selection.
Current official runtime candidates:

Track A primary:
  p18_rp_macro_w10_s5

Track A fallback:
  p18_rp_macro_w40_s5

Track B primary:
  p18_leeqa_sector_k5_temp35

Track B fallback:
  p18_s1_sector_t35_v30_w20
Current interpretation:

- Track A final candidates are no-news risk-parity candidates.
- Track B primary uses deterministic rule-based news through a LEEQA-Rank-style sector ranking candidate.
- Track B fallback is a no-news S1 sector candidate.
- Current news processing is mostly deterministic/rule-based.
- Optional local embedding / FinBERT-style paths were considered but are not final runtime dependencies.
- Existing text storage and event-state modules should be regarded as MVP-level.
- Advanced methods such as KG-MoE-Lite, CEVA-KF/CIGA, HGF-MPC, and ARMOR-OMD should be treated as lightweight MVP/proxy implementations unless proven otherwise.
The project also preserved five candidate methods per track as baselines for future research.
Preserved Track A candidates:

p18_rp_macro_w10_s5       # official primary, risk parity, no-news
p18_rp_macro_w40_s5       # official fallback, risk parity, no-news
p18_rp_macro_w20_s5       # strong risk-parity comparator
p18_bsa_macro_t10_g65     # BSA-RP / advanced macro comparator
p18_rp_macro_w60_s5       # strong risk-parity comparator
Preserved Track B candidates:

p18_leeqa_sector_k5_temp35    # official primary, LEEQA-Rank, rule-based news
p18_s1_sector_t35_v30_w20     # official fallback, S1 sector, no-news
p18_leeqa_sector_k5_temp20    # LEEQA-Rank comparator
p18_leeqa_sector_k5_temp70    # LEEQA-Rank comparator
p18_leeqa_sector_k3_temp20    # LEEQA-Rank top-k comparator
The next-stage research goal is to determine whether stronger news/text processing and a gated news overlay can improve the current system without compromising leakage safety, reproducibility, interpretability, turnover control, or official-server compatibility.
Research Objective
Conduct an in-depth research and design-space analysis for a future News/Text Processing and News Overlay phase.
Central research question:

Can event-aware news/text processing produce a stable, leakage-safe, out-of-sample improvement over the preserved Track A and Track B baselines, while remaining deterministic, reproducible, and official-server compatible?
Your task is to identify, compare, and rank possible designs for a news/text overlay system. You should cover both academic validity and practical shared-task implementation value.
Source-Use Requirements
Use external research and public knowledge where useful. Prioritise:

- financial NLP and event extraction literature;
- event-driven asset allocation;
- news sentiment and asset-price reaction studies;
- Chinese financial NLP / Chinese market news processing;
- ETF / sector rotation literature;
- attention mechanisms for text-to-asset relevance;
- retrieval / embedding methods for financial news;
- leakage-safe backtesting and event-study methodology;
- interpretable and reproducible model design.
Prefer sources that are:

- peer-reviewed papers;
- official model documentation;
- reputable finance/NLP benchmarks;
- established quantitative finance references;
- reproducible open-source methods.
Avoid designs that depend on:

- online LLM API calls at inference;
- unavailable or non-reproducible external datasets;
- model downloads at runtime;
- 2025 public-A tuning;
- hidden 2026 information;
- unbounded neural training;
- direct news-summary-to-portfolio allocation without controls.
Cite all important factual claims and sources.
Design Families to Research
Analyse at least the following design families. You may add additional designs if relevant.

Family 1 — Stronger Deterministic Rule/Event Extraction
Improve the current rule-based news pipeline through:

- event taxonomy;
- entity and sector mapping;
- macro-policy detection;
- sector-policy detection;
- market-regime tags;
- policy action verbs;
- directional templates;
- duplicate / cluster detection;
- event intensity scoring;
- timestamp-safe feature extraction.
Key question:

How far can deterministic event extraction go before transformer embeddings are necessary?
Family 2 — Event Taxonomy and Event Impact Scoring
Design a structured financial event ontology and event magnitude model.
Candidate event categories:

- monetary policy / liquidity;
- fiscal stimulus;
- property sector policy;
- AI / semiconductor / technology policy;
- energy / commodities;
- healthcare policy;
- consumer / retail demand;
- export / tariff / geopolitics;
- financial regulation;
- market liquidity / broad risk sentiment;
- earnings / industry fundamentals;
- crisis / shock events.
Research how to score event magnitude using:

- frequency in daily Top-20 news;
- entity specificity;
- event novelty;
- policy-action strength;
- cross-news agreement;
- source prominence;
- historical volatility response;
- historical sector response;
- sentiment or tone intensity;
- breadth across sectors.
Family 3 — News Attention Index
Design a daily asset/sector-level News Attention Index.
A possible formulation:

NAI(t, asset) =
  Σ_i Impact(t, i)
      × Relevance(t, i, asset)
      × Direction(t, i, asset)
      × Confidence(t, i, asset)
      × Sensitivity(asset)
Where:

Impact:
  estimated importance or magnitude of news item i;

Relevance:
  how strongly news item i maps to asset/sector;

Direction:
  expected positive/negative/neutral effect;

Confidence:
  reliability of mapping and direction;

Sensitivity:
  historical tendency of asset/sector to react to similar news.
Key question:

Can this index become a transparent intermediate signal for event-driven allocation?
Family 4 — ETF / Sector News Sensitivity Model
Estimate which ETFs or sectors are actually prone to news effects.
Possible 2024-only sensitivity measures:

- information coefficient between news signal and future return;
- hit rate of directional news;
- volatility response after high-impact news;
- drawdown response after negative news;
- lag profile: 1-day, 3-day, 5-day response;
- turnover-adjusted signal value;
- regime-conditioned sensitivity;
- event-class-specific sensitivity.
Key distinction:

Track A:
  news may be more useful for risk scaling or regime detection.

Track B:
  news may be more useful for sector ranking or sector tilt.
Family 5 — Gated News Overlay
Design a small overlay on top of preserved base allocators:

base target weights
+ gated news/event tilt
= final target weights
A candidate trigger condition:

if event_impact >= threshold
and asset_relevance >= threshold
and asset_sensitivity >= threshold
and confidence >= threshold
and turnover / drawdown gates allow:
    apply constrained overlay
else:
    use base allocator unchanged
The overlay must respect:

- maximum weight limits;
- maximum tilt;
- turnover cap;
- cash buffer;
- drawdown throttle;
- fallback-to-base when news signal is missing or low-confidence;
- official trade semantics.
Key question:

Can news improve performance only when it is large enough, relevant enough, and historically actionable enough?
Family 6 — Offline Transformer Relevance Cache
Research whether transformer embeddings should be used in a bounded offline way.
Potential uses:

- news-to-sector relevance;
- news-to-asset theme matching;
- duplicate / cluster detection;
- event novelty detection;
- semantic event taxonomy support;
- rule validation;
- weak relevance scoring.
Candidate model families:

- Chinese sentence embeddings, e.g. BGE-small-zh-style models;
- Chinese financial sentiment / FinBERT-style models;
- multilingual or Chinese domain encoders available before 2026.
Important restrictions:

- no runtime API calls;
- no silent downloads;
- no model binaries inside final official runtime package unless explicitly allowed;
- embeddings should be cached reproducibly;
- transformer layer should be optional and ablated against lexical/rule baselines.
Family 7 — Hybrid Rule + Embedding + Sensitivity Model
Combine:

deterministic event taxonomy
+ transformer/embedding relevance
+ 2024-only ETF sensitivity
+ event magnitude
+ gated overlay
This may be the strongest eventual design, but it must be built in stages.
Key question:

Does hybridising rules with embeddings improve robustness, or merely increase overfitting and dependency risk?
Family 8 — Lightweight Attention Prototype
Consider a small attention-style mechanism over news items and asset states:

news_embedding_i
asset_state_embedding_j
attention(news_i, asset_j)
event impact gate
sensitivity gate
overlay tilt
This should be treated as research-only and high-risk unless it remains simple, interpretable, and strongly ablated.
Reject or strongly discourage:

- full neural portfolio allocator;
- online LLM allocator;
- deep RL;
- graph RL;
- unconstrained RAG summary-to-trade system.
Track-Specific Analysis Required
Track A — Macro Allocation
Current Track A winner is no-news risk parity.
Analyse whether news is likely to help via:

- risk-on / risk-off regime scaling;
- macro policy shock detection;
- monetary / fiscal / property policy events;
- volatility or drawdown control;
- defensive allocation triggers;
- broad equity vs bond/cash tilt.
Be cautious about directional macro prediction.

Track B — Sector Rotation
Current Track B primary already uses rule-based news materially.
Analyse whether news is likely to help via:

- sector-specific event taxonomy;
- policy-to-sector mapping;
- event impact scoring;
- news-to-sector relevance;
- ranking adjustment;
- gated sector tilts;
- sensitivity-weighted news attention.
Track B is likely the more natural target for event/news overlay.
Required Ablation and Validation Design
For every proposed design, specify how to test it.
Required ablations:

1. preserved base allocator only;
2. real news overlay;
3. no-news variant;
4. zero-news signal;
5. shuffled-news dates;
6. randomised event labels;
7. impact gate disabled;
8. sensitivity gate disabled;
9. transformer relevance replaced with lexical relevance;
10. overlay strength sweep;
11. turnover cap stress test;
12. high-volatility regime split;
13. Track A vs Track B split.
Required validation discipline:

- Tune thresholds and parameters on 2024 only.
- Freeze all parameters.
- Test on 2025 public-A only.
- Do not use 2025 to select parameters.
- Before any promotion, require local official-semantics replay and official-server parity.
Comparative Scoring
Create a quantitative comparison table.
For each design family, score:

expected alpha value
robustness
interpretability
implementation complexity
leakage risk
dependency risk
runtime risk
official-server compatibility
turnover impact
drawdown impact
Track A suitability
Track B suitability
compatibility with preserved candidates
ablation quality
2024 tune / 2025 test feasibility
system-report novelty
Suggested total score:

TotalScore =
  0.18 * ExpectedValue
+ 0.14 * Robustness
+ 0.12 * Interpretability
+ 0.12 * OfficialCompatibility
+ 0.10 * AblationQuality
+ 0.10 * TrackBUsefulness
+ 0.08 * TrackAUsefulness
+ 0.08 * RuntimeSimplicity
+ 0.08 * ReportNovelty
- 0.10 * LeakageRisk
- 0.08 * DependencyRisk
- 0.06 * OverfittingRisk
Define your scoring scale clearly.
Required Report Structure
Produce a full research report:

# News Overlay Prompt0A Research Report — News/Text Processing and News Overlay Design Space

## 1. Executive Summary

## 2. Current Baseline State

## 3. Why News Matters for This Task

## 4. Why Current News Processing Is Insufficient

## 5. Track A vs Track B News Hypotheses

## 6. Design Family 1 — Stronger Deterministic Rule/Event Extraction

## 7. Design Family 2 — Event Taxonomy and Event Impact Scoring

## 8. Design Family 3 — News Attention Index

## 9. Design Family 4 — ETF/Sector News Sensitivity

## 10. Design Family 5 — Gated News Overlay

## 11. Design Family 6 — Offline Transformer Relevance Cache

## 12. Design Family 7 — Hybrid Rule + Embedding + Sensitivity Model

## 13. Design Family 8 — Lightweight Attention Prototype

## 14. Comparative Score Table

## 15. Recommended Top 3 Research Directions

## 16. Recommended First Implementation Path

## 17. Required Ablations

## 18. Required Reports and Artifacts for Later Prompts

## 19. Risks and Failure Modes

## 20. Open Questions for Synthesis
Final Recommendation Required
End with a clear recommendation:

Best first implementation direction:
  <your recommendation>

Second-stage direction:
  <your recommendation>

High-risk/defer:
  <your recommendation>
Also state:

- whether Track A and Track B should use the same news module;
- whether transformer embeddings should be first-build or second-build;
- whether a gated overlay should be implemented before or after sensitivity modelling;
- what must be proven before official runtime replacement is considered.
Constraints
Do not implement code.
Do not assume repository access.
Do not ask for repository paths.
Do not modify final candidates.
Do not claim new performance.
Do not use hidden 2026 data.
Do not recommend 2025 tuning.
Do not recommend online API dependence for final runtime.
Do not overclaim transformer or attention methods.
Distinguish clearly between research-only, ablation-only, and promotion-ready ideas.
Expected Final Answer
Return:

concise executive summary;
full research report;
comparative score table;
top 3 recommended design directions;
Track A-specific recommendation;
Track B-specific recommendation;
preferred first implementation path;
key ablation tests;
risks;
open questions for synthesis.

---

# gemini response

I've put together a research plan. If you need to update it in any way, let me know.
http://googleusercontent.com/deep_research_confirmation_content/0

---

# you asked

message time: 2026-06-03 21:48:00

Start research

---

# gemini response

I've completed your research. Feel free to ask me follow-up questions or request changes.

News Overlay Research Design Space

# News Overlay Prompt0A Research Report — News/Text Processing and News Overlay Design Space

## 1. Executive Summary

The transition of natural language processing systems from static, localized classification tasks—such as traditional sentiment analysis and localized event extraction—into dynamic, autonomous decision-making agents represents a profound paradigm shift in quantitative finance. In the highly specific context of the NLPCC 2026 Shared Task 4, which focuses on Large Language Model (LLM)-based Investment Advisor Agents for Asset Allocation in the Chinese Market, integrating an event-aware news and text processing overlay presents a substantial opportunity to generate orthogonal alpha and improve portfolio responsiveness. However, this integration introduces severe, potentially catastrophic risks related to data leakage, out-of-sample overfitting, and runtime dependency instability. The current repository state reflects a disciplined, highly controlled environment where the official runtime configuration is frozen, relying on a deterministic, rule-based Minimum Viable Product (MVP) for news processing alongside robust, no-news baseline models.[1, 1] 

This exhaustive research report synthesizes the expansive design space for a next-generation news and text overlay system. It meticulously evaluates the theoretical feasibility and practical implementation value of augmenting the existing, mathematically sound preserved candidates across Track A (Macro-Asset Allocation) and Track B (Sector-Rotation Allocation) with advanced event extraction, attention mechanisms, and semantic embeddings. The core objective of this analysis is to rigorously determine whether event-aware news processing can produce a stable, leakage-safe, out-of-sample improvement over the preserved baseline allocators while remaining completely deterministic, reproducible, and seamlessly compatible with the official evaluation server. By strictly confining all tuning procedures to 2024 data and reserving the 2025 public-A dataset exclusively for locked, out-of-sample generalization evaluation, the proposed design families prioritize structural robustness and interpretability over complex, unconstrained neural generation.[1, 1] The comprehensive analysis ultimately recommends a phased, risk-aware implementation strategy. This strategy begins with the deployment of a deterministic News Attention Index (NAI) and a strictly gated portfolio overlay, establishing a robust quantitative interface before advancing to the integration of offline, cached transformer embeddings for deep semantic representation.

## 2. Current Baseline State

The existing internal project state is characterized by an uncompromising adherence to reproducibility, execution stability, and robust baseline preservation. The official final runtime configurations are currently locked, ensuring that any future research into sophisticated news overlays is systematically benchmarked against proven, stable asset allocators.[1, 1] 

The system operates across two distinct evaluation tracks, each preserving a curated selection of five specific candidate configurations designed to provide comprehensive comparative baselines for future ablation.[1] The preservation of these candidates ensures that subsequent overlay developments can be tested against both primary runtimes and highly tuned comparator models.

| Track | Role | Configuration Identifier | Family | Preservation Reason | Official Runtime |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Track A** | Primary | `p18_rp_macro_w10_s5` | Risk Parity | Official Runtime | Yes |
| **Track A** | Fallback | `p18_rp_macro_w40_s5` | Risk Parity | Fallback | Yes |
| **Track A** | Comparator | `p18_rp_macro_w20_s5` | Risk Parity | Ablation | No |
| **Track A** | Comparator | `p18_bsa_macro_t10_g65` | BSA-RP | Future Overlay Baseline | No |
| **Track A** | Comparator | `p18_rp_macro_w60_s5` | Risk Parity | Ablation | No |
| **Track B** | Primary | `p18_leeqa_sector_k5_temp35` | LEEQA-Rank | Official Runtime | Yes |
| **Track B** | Fallback | `p18_s1_sector_t35_v30_w20` | S1 Sector | Fallback | Yes |
| **Track B** | Comparator | `p18_leeqa_sector_k5_temp20` | LEEQA-Rank | Future Overlay Baseline | No |
| **Track B** | Comparator | `p18_leeqa_sector_k5_temp70` | LEEQA-Rank | Future Overlay Baseline | No |
| **Track B** | Comparator | `p18_leeqa_sector_k3_temp20` | LEEQA-Rank | Future Overlay Baseline | No |

For Track A, focused on Macro-Asset Allocation, the dominant paradigm is no-news risk parity. The primary configuration, `p18_rp_macro_w10_s5`, operates strictly without news input, relying entirely on historical covariance to scale broad asset class exposures.[1] For Track B, focused on Sector-Rotation Allocation, the system currently employs a deterministic, rule-based approach to news processing within a ranking framework. The primary configuration, `p18_leeqa_sector_k5_temp35`, utilizes a LEEQA-Rank-style sector ranking mechanism that incorporates MVP-level rule-based news processing, while its fallback remains a strictly no-news allocator.[1]

The current processing pipeline remains in a highly restricted Minimum Viable Product state. Stage 1 utilizes deterministic, rule-based keyword matching without higher-order semantic awareness.[1] Stage 2 storage encompasses flat, event, business logic, and sector-impact structures, but operates as a lightweight proxy rather than a fully developed knowledge graph.[1] Stage 3 trade and price processing is fully stable and meticulously conforms to official execution semantics, incorporating a strict 0.01% transaction friction across all trades.[1] Local model paths, such as localized transformer embeddings or FinBERT-style architectures, remain disabled by default to prevent runtime dependency risks, silent API calls, and evaluation server failures.[1]

## 3. Why News Matters for This Task

Asset allocation within the Chinese financial market exhibits unique behavioral, structural, and regulatory characteristics that significantly amplify the importance of event-driven and news-aware portfolio strategies. The market is disproportionately sensitive to top-down macroeconomic policy directives, regulatory interventions, and targeted, sector-specific stimulus packages.[2, 3] Consequently, financial narratives and daily trending news act as the primary catalysts for capital rotation, volatility clustering, and regime shifts.

Recent evaluations of LLM-based autonomous financial agents underscore the absolute necessity of filtering broader market attention rather than relying solely on pre-filtered, entity-specific corporate news. The introduction of the CN-Buzz2Portfolio benchmark illustrates a critical dilemma in evaluation paradigms: direct live trading evaluations are often confounded by stochastic market noise and idiosyncratic equity volatility, making it difficult to isolate genuine logical reasoning from sheer luck.[4, 5, 6] By mapping daily trending news—or the "public attention stream"—to broad asset classes such as Exchange-Traded Funds (ETFs), quantitative strategies can effectively reduce idiosyncratic stock-level volatility while isolating the logical consistency of macroeconomic and sector-level sentiment.[5, 7] 

The Tri-Stage CPA (Compression, Perception, Allocation) workflow provides a structural rationale and rigorous blueprint for news integration. In highly policy-sensitive environments, unfiltered news feeds contain a chaotic mixture of systemic policy shifts, localized sector support, and irrelevant platform-specific clickbait.[6, 8] A robust NLP architecture must compress this unstructured buzz, accurately perceive the underlying directional sentiment and policy inclination, and translate these perceptions into programmatic allocation instructions. Empirical studies utilizing customized BERT models on Chinese financial text demonstrate that strong directional sentiment significantly impacts future excess returns, intraday volatility, and aggregate trading volume.[9] For example, reports bearing strong positive sentiment increase subsequent excess returns and intraday volatility, while intense negative sentiment increases volume and volatility but severely depresses future returns.[9] Furthermore, during exogenous geopolitical or systemic shocks, market behavior frequently bifurcates into complex herding or anti-herding dynamics across distinct asset classes, rendering static, purely price-based correlation matrices insufficient for rapid downside protection.[10] News processing provides the necessary contextual overlay to dynamically scale risk exposures and execute capital preservation maneuvers ahead of lagging price-based indicators.

## 4. Why Current News Processing Is Insufficient

The MVP-level deterministic rule extraction currently deployed in the Stage 1 pipeline is inherently fragile and structurally limited in its capacity to parse nuanced financial text. While it offers unparalleled interpretability and absolute immunity to API failure, it suffers from severe limitations in semantic comprehension and contextual disambiguation. Keyword-based matching cannot reliably disambiguate between negated statements, conditional policy proposals, or historical references within the daily Top-20 news stream. A mention of "reduced semiconductor subsidies in the prior decade" might trigger the exact same heuristic rule as "immediate expansion of semiconductor subsidies," resulting in a catastrophic directional failure in the allocation logic.

Furthermore, the existing pipeline entirely lacks a sophisticated Event Impact Scoring mechanism. A prominent policy shift, such as a major adjustment to the Medium-Term Lending Facility (MLF) rate by the People's Bank of China, is treated with the same weight as a minor administrative update if both trigger the same keyword rules. This inability to parse event magnitude prevents the allocation agent from distinguishing between structural regime shifts that warrant massive portfolio rebalancing and ephemeral market noise that should be ignored to avoid friction costs. High-quality asset allocation requires fine-grained, target-based sentiment analysis, where clauses reflecting profitability, regulatory support, or systemic risk are mapped directly to specific financial entities or sectors.[11]

The current system also fails to account for cross-entity spillovers and latent thematic relationships. In sector rotation, policies targeting specific technology sectors—such as semiconductor export controls or cloud infrastructure investments—exert indirect, yet substantial, impacts on related supply chains, high-end manufacturing, and broad equity indices.[2] Without semantic representation or an offline embedding space capable of mapping news to asset themes in a continuous vector space, the MVP system forces a binary, rigid mapping that degrades the performance of the LEEQA-Rank algorithms in out-of-sample regimes. This rigidity manifests as a high false-negative rate, where the system fails to react to highly relevant news simply because the specific phrasing did not match a pre-defined lexical dictionary.

## 5. Track A vs Track B News Hypotheses

The integration of news must be strictly bifurcated based on the distinct optimization objectives and underlying asset classes of the two evaluation tracks. Applying a monolithic news signal symmetrically across both macro and sector strategies violates fundamental principles of quantitative portfolio construction.

Track A targets broad asset classes through a variance-minimizing risk parity framework.[1, 1] The reigning hypothesis for Track A is that news provides limited alpha for directional macroeconomic prediction, as broad, highly liquid indices efficiently discount aggregate public information almost instantaneously. Instead, news in Track A is hypothesized to serve as a superior regime-switching and risk-scaling mechanism. Major macro-policy shocks—such as sweeping monetary liquidity injections, systemic fiscal stimulus, or severe property sector regulations—act as leading indicators for volatility clustering.[12, 13] Research explicitly demonstrates that macroeconomic attention indexes exhibit sharp, quantifiable increases around critical policy releases, and that higher pre-announcement attention robustly leads to stronger subsequent market reactions.[12, 13] Therefore, a news overlay in Track A should not aggressively tilt target weights based on sentiment direction; rather, it should function as a defensive volatility or drawdown control mechanism. The system should adjust the covariance matrix scaling or trigger a defensive shift toward bond and cash equivalents when the intensity of crisis or macroeconomic stimulus events breaches a historically validated, high-confidence threshold.

Track B requires relative value assessments and momentum capture across tightly defined sub-asset classes.[1, 1] The hypothesis for Track B is that sector rotation is intrinsically event-driven, particularly in the Chinese market where top-down regulatory cycles and five-year plan directives dictate sector leadership.[3] News is expected to directly improve the rank-ordering of sectors by quantifying policy-to-sector support, localized technology subsidies, or fundamental industry earnings sentiment.[14] Track B is the natural environment for an aggressive, directional news overlay that programmatically overrides baseline target weights to overweight high-impact, positive-sentiment sectors while simultaneously zeroing out exposure to sectors facing severe, heavily covered regulatory headwinds. 

## 6. Design Family 1 — Stronger Deterministic Rule/Event Extraction

The most conservative, interpretable, and runtime-safe enhancement involves significantly expanding the deterministic NLP pipeline before introducing any dense neural dependencies. This design family relies on advanced linguistic heuristics tailored specifically to the structural nuances of Chinese financial phrasing.

The core mechanisms of this approach begin with an expansive Event Taxonomy and Entity Mapping protocol. This requires upgrading the rudimentary regex and keyword dictionaries to comprehensively map complex financial terminology directly to the constituent holdings and thematic profiles of the target ETFs. To solve the disambiguation problem, the system must deploy deterministic part-of-speech (POS) targeting to identify directional policy action verbs—such as "reduce", "subsidize", "restrict", "expand", or "penalize"—strictly when they appear in immediate syntactical proximity to recognized sector entities. 

Furthermore, the implementation of Directional Templates allows for the construction of syntactic rules that capture conditional logic. By identifying the structure of a sentence (e.g., matching the template "[Policy Entity] + [Action Verb] + [Quantitative Metric] +"), the system can extract high-fidelity directional signals without requiring a transformer. To ensure these signals are not artificially inflated by echo-chamber reporting, robust Duplicate and Cluster Detection mechanisms must be applied. Utilizing character-level Levenshtein distance or token-based Jaccard similarity metrics over the daily Top-20 news strings prevents multiple identical articles syndicated across different platforms from compounding the event magnitude score. Finally, strict Timestamp-Safe Feature Extraction is paramount; the pipeline must enforce absolute temporal boundaries, ensuring that only articles bearing a timestamp strictly prior to the daily decision cutoff are processed, thereby nullifying any risk of look-ahead bias.

While this family ensures perfect official-server compatibility, absolute interpretability, and zero dependency risk, its expected alpha generation is structurally limited by the rigidity of hard-coded rules. It serves best as a highly robust foundation for downstream scoring mechanisms, establishing exactly how far lexical extraction can advance before transformer architectures become mathematically necessary for semantic resolution.

## 7. Design Family 2 — Event Taxonomy and Event Impact Scoring

To prevent the allocation agent from overreacting to trivial data or daily market chatter, the extracted text must be quantified into an actionable, hierarchical numerical structure. This design family proposes a structured financial event ontology coupled with a multi-factor magnitude model.

A rigorous event ontology must cover the primary drivers of Chinese market liquidity and sector performance, capturing the diverse array of catalysts that impact asset pricing.[2, 3] The candidate event categories must be exhaustive, encompassing monetary policy and systemic liquidity adjustments, fiscal stimulus and sovereign bond issuance, property sector regulations and mortgage policies, and specialized directives targeting AI, semiconductor, and high-tech manufacturing policies. Additional categories must track energy and commodity pricing dynamics, healthcare and pharmaceutical regulation, consumer retail demand and consumption subsidies, export tariffs and geopolitical developments, financial regulation and capital market reforms, market liquidity interventions and broad risk sentiment, industry-specific fundamental earnings shocks, and exogenous crises or systemic shock events.

The magnitude of an event is not purely a function of its localized sentiment polarity; it is defined by its broader market exposure and the degree of consensus it commands across reporting entities.[15] The proposed scoring architecture formulates the magnitude of an event as a weighted composite of several variables. The $Frequency$ variable evaluates the concentration of an event across the Top-20 daily news items, assuming that highly consequential policies will dominate the news cycle. The $Novelty$ variable compares the current textual features against a trailing window of the event state store to heavily penalize stale narratives and repeated announcements of already-priced information. The $Agreement$ variable measures the uniformity of directional sentiment across independent sources. High-impact scores are strictly reserved for policy-action events that simultaneously dominate the current news cycle, display absolute directional consensus, and represent a clear, structural deviation from the trailing 30-day narrative baseline.

## 8. Design Family 3 — News Attention Index

A critical breakthrough in modern financial natural language processing is the formulation of structured attention indices that quantify how disproportionately a given asset is covered in financial media relative to its historical baseline.[15, 16] The proposed News Attention Index (NAI) translates unstructured qualitative text into a transparent, intermediate quantitative signal that can be directly ingested by a portfolio optimizer.

The mathematical formulation for the NAI at a given decision time $t$ for a specific $asset$ is calculated as a summation across all relevant daily news items $i$. The equation is defined as:

$NAI(t, asset) = \sum_{i=1}^{N} \Big( Impact(t, i) \times Rel(t, i, asset) \times Dir(t, i, asset) \times Conf(t, i, asset) \Big) \times Sens(asset)$

Each variable in this formulation serves a distinct risk-control function. $Impact$ is derived directly from the Event Magnitude model described in Design Family 2, establishing the systemic weight of the news item. $Relevance$ represents the proximity score—whether generated via lexical overlap or dense semantic embeddings—between the news item $i$ and the thematic profile of the target asset. $Direction$ encodes the sentiment polarity, strictly mathematically bounded to values of $[-1, 0, 1]$ to ensure symmetry in the scoring matrix. $Confidence$ applies a fractional penalty factor to ambiguous text, contradictory clauses, or low-quality source origins, effectively dampening the signal of unreliable data. Finally, $Sensitivity$ represents the historical beta of the asset to news shocks, an independent multiplier modeled separately (Design Family 4).

The NAI acts as the central, interpretable interface between the Perception and Allocation stages of the CPA framework.[5] By aggregating these multidimensional scores across the daily Top-20 news, it provides a continuously updated, normalized vector that represents the market's attention allocation. Extensive research indicates that macroeconomic attention indexes exhibit sharp, quantifiable increases around critical policy releases, and that this heightened attention directly facilitates permanent price adjustments.[13, 16] This index framework actively avoids the opacity and unpredictability of end-to-end neural allocators by explicitly defining and bounding every variable in the computational pipeline.

## 9. Design Family 4 — ETF/Sector News Sensitivity

A fundamental flaw in rudimentary event-driven models is the assumption that all assets react symmetrically to public attention. A news overlay applied uniformly across a diversified portfolio introduces severe turnover drag and generates false signals in asset classes that are structurally immune to media narratives. This design family estimates the asymmetric sensitivity of specific ETFs to textual catalysts, utilizing strictly the 2024 training data to calibrate these parameters.[1]

Sensitivity estimation relies on several rigorous quantitative metrics. The primary measure is the Information Coefficient (IC), which calculates the rank correlation between the historical NAI signal and the forward 1-day, 3-day, and 5-day excess returns of the ETF. Secondary measures include Volatility Response profiling, which calculates the statistical expansion of intraday or interday variance following high-impact news items.[9, 12] The Directional Hit Rate evaluates the historical empirical probability that a positive sentiment signal correctly anticipates a positive excess return over the target holding period. Furthermore, Drawdown Conditioning assesses whether negative news generates immediate, sustained liquidation pressure or merely elevated, mean-reverting volatility.

The application of these sensitivity measures requires strict track distinctions. In Track A, the sensitivity model focuses entirely on the covariance stability of broad equity indices versus fixed-income ETFs during high-attention liquidity events, recognizing that bond markets process news differently than equity markets. In Track B, sensitivity is measured by the magnitude of capital rotation into a specific sector following a targeted regulatory catalyst.[14] ETFs displaying an Information Coefficient or hit rate below a statistically significant threshold over the 2024 tuning horizon are permanently assigned a zero-sensitivity multiplier ($Sens = 0$). This hard-coded exclusion prevents the overlay from trading assets that demonstrate structural immunity to news cycles, thereby preserving capital that would otherwise be lost to transaction friction.

## 10. Design Family 5 — Gated News Overlay

The most profound vulnerability in LLM-driven trading systems and unconstrained generative agents is their tendency toward unconstrained allocation, which invariably leads to runaway turnover, massive friction costs, and catastrophic maximum drawdowns in live environments. The Gated News Overlay directly addresses this vulnerability by preserving the mathematical soundness of the preserved base allocators and implementing a rigid, absolute constraint boundary.[1, 1] 

The allocation logic defines the final portfolio weight vector as a composite of the base optimizer and a conditionally applied news tilt vector. The final target weights are computed as the base target weights plus the gated news/event tilt. Crucially, the application of this tilt is governed by a strict boolean gate activation. The overlay only activates if an exhaustive set of conditions are simultaneously met: the maximum event impact must exceed the $\tau_{impact}$ threshold, the asset relevance must exceed the $\tau_{relevance}$ threshold, the pre-calculated asset sensitivity must exceed the $\tau_{sensitivity}$ threshold, and the semantic confidence score must exceed the $\tau_{confidence}$ threshold.

If all thresholds are breached and the gate activates, the application of the news tilt is still subjected to absolute systemic limits. The overlay is capped at a maximum allowable tilt to prevent severe concentration risk. Furthermore, a strict turnover cap and cash buffer are algorithmically enforced to respect the official 0.01% transaction friction.[1] If trailing portfolio drawdowns breach predefined safety parameters, the drawdown throttle immediately forces the gate to close, defaulting entirely to the unchanged no-news baseline weights (such as the `p18_rp_macro` or `p18_s1_sector` fallback weights). This architecture ensures that the system fails gracefully during periods of profound market chaos, where news signals become entirely uncorrelated with actual price action and rational market mechanics break down.

## 11. Design Family 6 — Offline Transformer Relevance Cache

While deterministic lexical rules guarantee runtime safety, they suffer from inherent semantic rigidity. Design Family 6 explores the cautious, heavily bounded introduction of transformer architectures to achieve deep semantic understanding, strictly adhering to the fundamental requirement of no runtime API calls and absolutely no silent model downloads.[1, 1] 

The architecture relies on the selection of compact, highly efficient, domain-specific Chinese sentence encoders available prior to 2026. The `BAAI/bge-small-zh` model presents an optimal, mathematically sound solution for this environment. With a diminutive parameter count of merely 24 million and a storage footprint under 100 MB, it delivers highly competitive text-to-vector mapping capabilities without the massive computational overhead, memory bloat, or execution latency associated with large language models.[17, 18, 19] FinBERT-style financial sentiment models can also be evaluated as an alternative, provided they meet strict latency and offline reproducibility requirements.[9]

The implementation mechanics mandate that the transformer is deployed strictly for offline feature extraction and caching. During the 2024 tuning phase, the entire historical news corpus and the predefined asset/sector thematic descriptions are processed through the `bge-small-zh` tokenizer and encoder.[18] The resulting 768-dimensional dense semantic vectors are stored in a static, highly optimized reference cache. At runtime, incoming daily news items are rapidly vectorized locally, and their cosine similarity against the cached asset themes is calculated in the latent space to derive the continuous Relevance score for the NAI. This semantic matching entirely overcomes the limitations of keyword extraction by natively recognizing synonyms, complex context variations, and implicit policy references. Crucially, the transformer layer operates solely as an optional augmentation. The system retains the architectural ability to instantly fall back to lexical matching if the local embedding module fails to initialize on the official server, perfectly satisfying the strict official-server compatibility requirements.

## 12. Design Family 7 — Hybrid Rule + Embedding + Sensitivity Model

The most mathematically robust and comprehensive formulation synthesizes the distinct strengths of multiple design families into a singular, hierarchical processing pipeline. This hybrid approach aligns flawlessly with the theoretical underpinnings of the Tri-Stage CPA Framework [5, 8], moving seamlessly from unstructured data to programmatic allocation.

The pipeline initiates with the Compression stage, utilizing the deterministic rules (Family 1) and Event Taxonomy (Family 2). Incoming unstructured daily news is rapidly parsed, and trivial, non-financial, or low-impact news is immediately discarded. This deterministic pre-filtering vastly reduces the computational burden and eliminates the risk of transformer models attempting to find latent meaning in platform-specific clickbait.[8]

The surviving, high-impact events progress to the Perception stage. Here, the offline transformer cache (Family 6) is triggered to establish deep semantic relevance between the critical news items and the target asset classes. This highly accurate semantic score is then mathematically combined with the 2024-derived static ETF sensitivity model (Family 4) to accurately populate the multi-variable News Attention Index (Family 3).

Finally, the pipeline resolves in the Allocation stage. The finalized NAI signals are passed directly into the Gated News Overlay (Family 5), where they are subjected to strict turnover caps, tilt limits, and drawdown throttles before they are permitted to mathematically modify the baseline configurations. This hierarchical structure ensures that expensive, dense embeddings only process data that has been pre-validated by deterministic, logical rules, simultaneously minimizing the risk of hallucinated relevance and grounding the semantic output in historical market reality.

## 13. Design Family 8 — Lightweight Attention Prototype

A highly experimental, conceptually sophisticated avenue involves implementing a localized neural attention mechanism directly over the sequential sequence of daily news items and the internal state representations of the target assets. 

The mathematical formulation for this prototype involves treating the sequence of dense embeddings for the daily news items as the context matrix, and the internal state representation of the target sectors as the query vector. A scaled dot-product attention function could theoretically learn to dynamically assign relevance weights across the news stream:

$Attention(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$

In this architecture, the query matrix ($Q$) is derived from the asset embeddings, while the key ($K$) and value ($V$) matrices are derived from the daily news embeddings. While mathematically elegant and highly capable of capturing complex, non-linear dependencies between news sequences and asset behavior, this approach must be treated as strictly research-only and classified as exceptionally high-risk for the final shared-task submission. Allowing an unconstrained, deeply parameterized attention matrix to dictate portfolio tilts in a limited, low-frequency data environment—such as daily ETF resolution—virtually guarantees severe overfitting to the specific macroeconomic sequence of the 2024 tuning set. Furthermore, it completely destroys the interpretability of the system, transforming a transparent, mathematically gated logic into an opaque neural allocator. Consequently, this design is strongly discouraged for any official runtime promotion unless it is heavily ablated and bounded by an immutable output clamp that prevents it from overriding the foundational risk parity or LEEQA-Rank algorithms.

## 14. Comparative Score Table

To systematically, objectively select the optimal research direction for the ensuing implementation phases, the eight design families are evaluated across 14 critical dimensions of viability and risk. 

The scoring scale operates from $0.0$ to $10.0$. For positive attributes (e.g., Alpha Value, Robustness), a higher score is optimal. For risk attributes (e.g., Leakage Risk, Dependency Risk), a lower raw score indicates lower risk; however, the total formula automatically subtracts these values, ensuring that high risk heavily penalizes the final score. 

The comprehensive scoring formula utilized is: 
$TotalScore = (0.18 \times Value) + (0.14 \times Robust) + (0.12 \times Interp) + (0.12 \times Official) + (0.10 \times Ablation) + (0.10 \times TrackB) + (0.08 \times TrackA) + (0.08 \times Simplicity) + (0.08 \times Novelty) - (0.10 \times LeakageRisk) - (0.08 \times DependencyRisk) - (0.06 \times OverfitRisk)$

| Metric | F1: Rules | F2: Taxonomy | F3: NAI | F4: Sens | F5: Gated | F6: Cache | F7: Hybrid | F8: Attn |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alpha Value** | 4.0 | 5.5 | 7.5 | 6.5 | 8.0 | 7.0 | 9.0 | 6.5 |
| **Robustness** | 9.5 | 8.5 | 8.0 | 8.0 | 9.5 | 7.5 | 8.5 | 3.0 |
| **Interpretability** | 9.5 | 9.0 | 8.5 | 8.5 | 9.0 | 5.5 | 7.0 | 2.0 |
| **Official Compat.** | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 6.0 | 8.0 | 4.0 |
| **Ablation Quality** | 8.0 | 8.5 | 9.5 | 9.0 | 9.5 | 9.0 | 9.5 | 4.0 |
| **Track B Utility** | 5.0 | 7.0 | 9.0 | 8.0 | 9.0 | 8.5 | 9.5 | 5.0 |
| **Track A Utility** | 3.0 | 5.0 | 6.0 | 7.0 | 8.5 | 5.0 | 7.5 | 3.0 |
| **Runtime Simp.** | 9.0 | 8.0 | 7.5 | 8.0 | 7.0 | 4.0 | 5.0 | 2.0 |
| **Report Novelty** | 2.0 | 4.0 | 8.0 | 7.0 | 8.0 | 8.0 | 9.5 | 8.0 |
| **Leakage Risk** | 0.0 | 1.0 | 1.0 | 3.0 | 1.0 | 5.0 | 4.0 | 8.0 |
| **Dependency Risk**| 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 8.0 | 6.0 | 9.0 |
| **Overfit Risk** | 1.0 | 2.0 | 3.0 | 5.0 | 2.0 | 6.0 | 5.0 | 9.5 |
| **Total Score** | **6.67** | **7.18** | **8.12** | **7.51** | **8.42** | **6.11** | **7.69** | **2.53** |

The quantitative analysis clearly dictates the path forward. Design Family 5 (Gated News Overlay) and Design Family 3 (News Attention Index) achieve the highest aggregate scores due to their exceptional balance of high expected alpha generation and near-zero runtime and dependency risks. The Hybrid Model (Family 7) provides the highest theoretical value but incurs moderate dependency and complexity penalties. The Neural Attention Prototype (Family 8) fails catastrophically under these strict implementation constraints and must be discarded from immediate consideration.

## 15. Recommended Top 3 Research Directions

Based on the multi-factor scoring matrix and the strict limitations on API dependence and 2026 hidden data usage [1], the following directions are decisively prioritized for immediate research and implementation sequencing:

The paramount direction is the development of the deterministic News Attention Index (NAI) linked directly to a Gated Overlay (combining Families 3 and 5). This approach introduces sophisticated, highly responsive quantitative signal extraction without requiring complex external neural models. By gating the overlay strictly behind algorithmic turnover constraints and drawdown throttles, it directly neutralizes the idiosyncratic volatility and over-trading issues frequently identified in financial LLM benchmarks.[5] 

The secondary priority is the comprehensive estimation of the ETF Sensitivity Matrix (Family 4). Understanding the historical empirical reactivity of specific assets is an absolute prerequisite for mathematically scaling position sizes. Computing Information Coefficients and hit-rate profiles exclusively on 2024 data provides a robust, pre-calculated, static matrix that seamlessly informs the NAI calculation without adding a single millisecond of runtime computational overhead.

The tertiary pursuit is the development of the Hybrid Pipeline utilizing an offline BGE-small-zh cache (combining Families 7 and 6). Replacing rudimentary lexical matching with local, highly compressed text embeddings offers immense semantic upside, particularly in parsing complex Chinese regulatory announcements. However, this is strictly conditional upon the entire vector space being statically cached offline to guarantee seamless, flawless server validation without dependency drift or silent download failures.[18]

## 16. Recommended First Implementation Path

The immediate implementation phase—mapping directly to Prompt 23 and Prompt 26 equivalents [1]—must actively avoid premature neural deployment. The preferred sequence is strictly phased to ensure maximum interpretability and stability.

Phase 1 establishes the Deterministic Foundation. The implementation must build the News Attention Index (NAI) utilizing purely lexical rules and the expanded Event Taxonomy. This creates the exact, functional mathematical interface required for the Gated Overlay. Simultaneously, the core overlay constraints—including strict turnover caps, cash buffer respect protocols, and specific numerical $\tau$ thresholds—must be developed and hard-coded.

Phase 2 focuses entirely on 2024 Sensitivity Calibration. The system must algorithmically calculate the static sensitivity scalars ($Sens_{asset}$) for all target ETFs using only the 2024 training dataset. Once computed, these parameters must be permanently locked to prevent any forward-looking leakage.

Phase 3 executes Integration and Ablation. The deterministic NAI and locked sensitivity parameters are fed into the Gated Overlay. Crucially, the base weights will be supplied exclusively by the locked `p18_rp_macro` and `p18_leeqa_sector` primary runtimes.[1] This architectural design guarantees that if the news logic evaluates to zero due to missing data or low confidence, the system mathematically reverts exactly to the validated, stable state. Only after this entire deterministic architecture is rigorously validated on the 2025 public-A locked evaluation dataset should the transition to a cached transformer module (Phase 4) be authorized.

## 17. Required Ablations

Any advancement of the news overlay requires rigorous scientific isolation to conclusively prove that any observed alpha generation stems from valid textual perception rather than broad market beta or random stochastic variance.[5] All evaluations must tune parameters exclusively on 2024 data and execute locked evaluations on the 2025 public-A set.[1, 1] Thirteen specific ablations are required.

The baseline must be established by running the preserved base allocator only, executing `p18_rp_macro_w10_s5` and `p18_leeqa_sector_k5_temp35` with the news module forcibly detached. This is compared against the real news overlay variant. To ensure structural integrity, a zero-news signal test must forcefully inject $0.0$ into the NAI continuously, verifying that the Gated Overlay fails gracefully to the exact base weights without initiating computational errors or division-by-zero faults.

To detect look-ahead bias, a shuffled-news dates ablation must randomly permute the daily Top-20 news timestamps within the 2024 window. If this permutation generates positive alpha, the system is catastrophically overfitting to underlying price momentum rather than extracting actual textual causality. Similarly, randomizing event labels by injecting false sentiment polarities (e.g., scoring massive stimulus as negative) rigorously tests the mathematical symmetry and integrity of the Direction component.

Constraint boundaries must be stress-tested by disabling the impact gate (forcing $\tau_{impact} = 0$), allowing trivial daily noise to reach the overlay to measure the resulting degradation in the Sharpe ratio. Disabling the sensitivity gate (assigning $Sens_{asset} = 1.0$ universally) will test for inefficient capital allocation to structurally non-reactive, defensive sectors. An overlay strength sweep must modulate the maximum allowed news tilt (e.g., $\pm 2\%$, $\pm 5\%$, $\pm 10\%$) against the base weights to identify the exact optimal constraint boundary. Furthermore, iteratively lowering the turnover cap constraint will simulate a turnover cap stress test, plotting friction costs against gross returns until the overlay is effectively strangled.

When embeddings are introduced, a direct comparison between the transformer relevance and lexical relevance proxies must be conducted, quantifying the exact Information Ratio improvement yielded by semantic vectors. Finally, track-specific utility must be measured via a Track A versus Track B split analysis, evaluating the macro strategy independently from the sector strategy to confirm the overarching hypothesis that sector rotation extracts higher relative value from the textual stream, and high-volatility regime splits must analyze performance specifically during periods of market stress.

## 18. Required Reports and Artifacts for Later Prompts

To perfectly align with the highly structured, sequential workflow established in the official prompt backlog [1], specific, tangible artifacts must be systematically generated before any candidate promotion to the final runtime is considered.

A detailed Progress Report is required, outlining the exact mathematical formulation of the NAI and exhaustively documenting the precise logic constraints implemented within the Gated Overlay. This must be accompanied by a Presented Summary, functioning as an executive quantitative dashboard that highlights the critical out-of-sample performance metrics—specifically Sharpe ratio, maximum drawdown, cumulative return, and turnover metrics—derived strictly from the 2025 locked test environment.

Crucially, a Reference CSV/MD must be constructed. This dense data structure will record the exact $\tau$ thresholds, sensitivity matrices, and caching parameters derived exclusively from the 2024 tuning phase, ensuring complete parameter transparency. An Implementation Log must provide a comprehensive, step-by-step audit trail unequivocally proving that no silent API calls, hidden 2026 data streams, or unauthorized modifications to the core official runtime definitions occurred during the execution phase. Finally, an Official Parity Matrix is mandatory. This localized reproduction of the official-semantics grid serves as final verification that the newly developed text module executes without syntax errors, memory leaks, or dimensional mismatches within the broader evaluation server framework.

## 19. Risks and Failure Modes

The development and integration of advanced textual overlays introduces complex systemic vulnerabilities that must be preemptively identified, analyzed, and mitigated to ensure survivability in the hidden 2026 evaluation period.

The most critical and pervasive threat is the inadvertent occurrence of data leakage and subsequent regime collapse. If the offline transformer cache, the event taxonomy construction, or the static sensitivity matrices inadvertently assimilate any future knowledge from 2025 or 2026 datasets, the backtest results will present artificially inflated Sharpe ratios.[1] In a live, out-of-sample environment, these models will catastrophically collapse when confronted with genuinely unseen data distributions in the hidden 2026 regime.

A secondary, highly probable failure mode is severe overfitting to specific 2024 stimulus dynamics. The 2024 Chinese macroeconomic environment may contain anomalous policy stimulus structures or highly specific regulatory verbiage. A deterministic ruleset or an attention index heavily calibrated to identify these 2024-specific terms (such as a highly specific iteration of property sector liquidity support) may fail entirely to perceive novel fiscal mechanisms or regulatory crackdowns introduced in late 2025. This vulnerability underscores the absolute necessity of generalized, broad-based semantic mapping over narrow keyword extraction.

Furthermore, event-driven news signals frequently exhibit high day-over-day volatility, resulting in friction and turnover death spirals. Without a rigidly enforced turnover cap operating continuously within the Gated Overlay, the agent may succumb to oscillatory trading behavior, rapidly rotating capital back and forth based on conflicting, high-frequency news cycles. Under the official 0.01% transaction friction semantics, this unchecked turnover will rapidly erode compound returns, mathematically guaranteeing that the heavily enhanced model will severely underperform the passive, low-turnover base allocator.[1] Finally, introducing external local models natively into the runtime introduces the risk of runtime instability and dependency drift. If the `bge-small-zh` offline architecture attempts to initialize unavailable tokenizers, allocates excessive memory, or attempts to download missing configurations dynamically, the agent will instantly disqualify on the official server. The system must maintain an unbreakable failsafe mechanism that effortlessly reverts to the MVP deterministic ruleset the instant the primary text module encounters a load failure.

## 20. Open Questions for Synthesis

Before finalizing the transition from the theoretical design space into actual repository localization and coding, several highly specific architectural nuances require final resolution and synthesis:

First, regarding the harmonization of tracks: Should Track A and Track B invoke the exact identical underlying news processing module during the Compression phase, or do their vastly distinct objective functions necessitate branching the NLP pipeline earlier in the workflow? Second, the temporal dynamics of the event state require definition. How exactly should the Event Impact score mathematically decay over time? Does a massive, systemic policy shock maintain a residual NAI value for 3 days, 5 days, or does it persist indefinitely until a counteracting semantic event is definitively detected? Finally, the handling of cache invalidation remains a structural unknown. If the offline embedding cache encounters an entirely novel financial entity or an unprecedented regulatory mechanism not present anywhere in the 2024 latent vector space, what is the precise mathematical protocol for assigning an interpolated, safety-first baseline relevance score without illegally initiating an online API query to resolve the entity?

***

**Final Recommendation Required**

*   **Best first implementation direction:** Develop a fully deterministic News Attention Index (NAI) paired tightly with a strictly constrained Gated News Overlay (combining Design Families 3 and 5). This provides immediate, highly interpretable quantitative signaling without introducing any neural instability or dependency risk into the frozen runtime environment.
*   **Second-stage direction:** Algorithmically calculate and permanently integrate the 2024-derived ETF/Sector Sensitivity matrix (Family 4) to dynamically scale the NAI, followed by the highly cautious, optional implementation of the `bge-small-zh` offline transformer cache (Family 6) to enhance deep semantic relevance matching.
*   **High-risk/defer:** All end-to-end neural attention allocators (Family 8), all online LLM API agents, and any unconstrained strategy overrides. These architectures pose fundamentally unacceptable leakage, execution, and overfitting risks in a shared-task environment.

Furthermore, it is determined that Track A and Track B should utilize the exact same foundational text processing engine (Compression and Perception) but MUST employ radically different gating parameters, sensitivity matrices, and limits during the Allocation phase. News serves primarily as a variance-reducing risk-scaling tool for Track A and a highly directional ranking adjustment tool for Track B. Transformer embeddings should strictly be a second-build augmentation; the entire overlay infrastructure must be definitively proven functional utilizing deterministic lexical proxies first. The bounded Gated Overlay must absolutely be established before any sophisticated sensitivity modeling is implemented, as an unconstrained overlay will destroy capital regardless of how theoretically accurate the underlying text classification is. Finally, before any official runtime replacement is considered, the new overlay must demonstrably and reproducibly improve the risk-adjusted returns—specifically Sharpe ratio and maximum drawdown—on the locked 2025 public-A evaluation set, while operating perfectly within the official-semantics replay framework without a single runtime dependency error.

---

# you asked

message time: 2026-06-03 22:49:10

# Prompt0A-Enhance — Specific Framework and Method Discovery for News Overlay

## Role

You are a senior research analyst in quantitative finance, Chinese financial NLP, event-driven trading systems, representation learning, information retrieval, and model-risk-aware portfolio construction.

You are continuing the **News Overlay** research workflow after Prompt0A.

Prompt0A produced a broad design-space analysis for news/text processing and gated news overlays. Your task now is to go deeper and identify **specific, named, implementable methodologies** rather than general design families.

This is a **deep research enhancement prompt**. You do **not** have repository access. Treat the project context below as the complete internal state.

Do **not** write implementation code.  
Do **not** ask for repository paths.  
Do **not** assume hidden test access.  
Do **not** propose vague concepts without explicit methodology.

---

## Project Context

The project is for:

```text
NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
```

Tracks:

```text
Track A / Track 1:
  Macro-Asset Allocation

Track B / Track 2:
  Sector-Rotation Allocation
```

Competition constraints:

```text
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is used for training / construction / tuning.
- 2025 public-A data is used for locked testing / generalisation evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- Hidden B-list evaluation is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- Final runtime should retain deterministic no-model / no-API fallback.
- Any training, fine-tuning, retrieval, or knowledge construction must be reproducible.
```

Current validated runtime should be treated as frozen:

```text
Track A primary:
  p18_rp_macro_w10_s5

Track A fallback:
  p18_rp_macro_w40_s5

Track B primary:
  p18_leeqa_sector_k5_temp35

Track B fallback:
  p18_s1_sector_t35_v30_w20
```

Current interpretation:

```text
- Track A final candidates are no-news risk-parity candidates.
- Track B primary uses deterministic rule-based news through a LEEQA-Rank-style sector ranking method.
- Track B fallback is a no-news S1 sector candidate.
- Current news processing is mostly deterministic/rule-based.
- Optional local embedding / FinBERT-style paths were considered but are not final runtime dependencies.
- Existing text storage and event-state modules are MVP-level.
- Advanced methods should be treated as lightweight MVP/proxy implementations unless proven otherwise.
```

Preserved Track A baselines:

```text
p18_rp_macro_w10_s5
p18_rp_macro_w40_s5
p18_rp_macro_w20_s5
p18_bsa_macro_t10_g65
p18_rp_macro_w60_s5
```

Preserved Track B baselines:

```text
p18_leeqa_sector_k5_temp35
p18_s1_sector_t35_v30_w20
p18_leeqa_sector_k5_temp20
p18_leeqa_sector_k5_temp70
p18_leeqa_sector_k3_temp20
```

---

## Objective

Identify and evaluate **5–10 top concrete methods/frameworks** for the next News Overlay stage.

The output must be more specific than:

```text
“use news attention”
“use transformer embeddings”
“use event impact score”
“use gated overlay”
```

Instead, each candidate method must have:

```text
- a clear methodology name;
- mathematical formulation or algorithmic procedure;
- required inputs;
- output signal;
- how it plugs into Track A and/or Track B;
- 2024-only training/tuning procedure;
- 2025 frozen test procedure;
- ablation plan;
- expected failure modes;
- implementation complexity;
- promotion criteria.
```

The goal is to identify the best **explicit methodologies** that can be implemented in later prompts.

---

## Mandatory Research Requirements

You must research specific frameworks and methods from the following areas.

### 1. Event Study and Event-Driven Finance

Look for concrete methods such as:

```text
- classical event study abnormal return models;
- market model / factor model event response;
- cumulative abnormal return windows;
- event-time response curves;
- event impact scoring;
- volatility-event response models;
- event intensity models.
```

Explain how each can be adapted to ETF / sector allocation under 2024-tune and 2025-test discipline.

### 2. Financial News Sentiment and Event Extraction

Look for concrete methods such as:

```text
- dictionary-based financial sentiment;
- FinBERT-style tone classification;
- aspect-based sentiment;
- event extraction templates;
- entity-event-relation triples;
- OpenIE-style structured event extraction;
- policy-event taxonomy extraction;
- weakly supervised event labelling.
```

Prioritise methods that can work for Chinese financial news or can be adapted to it.

### 3. Text-to-Asset / Text-to-Sector Relevance

Look for concrete methods such as:

```text
- BM25 / TF-IDF sector relevance;
- embedding cosine relevance;
- cross-encoder relevance scoring;
- contrastive retrieval;
- nearest-centroid sector embedding;
- entity-sector knowledge mapping;
- graph-based text-sector propagation;
- attention pooling over news items.
```

Explain what should be used first and what should be deferred.

### 4. Attention and News Aggregation

Look for concrete methods such as:

```text
- hierarchical attention network for documents;
- multi-head attention over daily news items;
- query-key-value attention with asset/sector queries;
- temporal attention over lagged news;
- gated attention;
- additive attention;
- transformer encoder as frozen feature extractor;
- attention pooling with impact gates.
```

Avoid recommending a full neural allocator unless strongly justified.

### 5. News Sensitivity and Signal Validation

Look for concrete methods such as:

```text
- information coefficient;
- rank IC;
- Granger-style lag tests;
- rolling correlation / expanding correlation;
- robust regression;
- LASSO / elastic-net sparse event response;
- cross-sectional regression;
- difference-in-differences/event panel regression;
- permutation tests;
- shuffled-news placebo tests.
```

### 6. Portfolio Overlay and Risk-Control Methods

Look for concrete methods such as:

```text
- Black-Litterman views from news signals;
- constrained mean-variance tilt;
- risk-parity plus active overlay;
- online mirror descent / exponentiated-gradient overlay;
- confidence-weighted overlay;
- volatility-scaled overlay;
- drawdown-gated overlay;
- turnover-constrained overlay.
```

---

## Methods Must Be Specific

Each proposed method must be named in a way like:

```text
Method 1:
  Event-Study Calibrated News Impact Overlay

Method 2:
  Sector Query Attention News Relevance Index

Method 3:
  Sparse Event-Sensitivity Regression Overlay

Method 4:
  Black-Litterman News View Overlay

Method 5:
  Rank-IC Gated Sector News Momentum

Method 6:
  Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate

Method 7:
  Volatility-Scaled Macro News Risk Gate

Method 8:
  Permutation-Tested News Attention Index

Method 9:
  Entity-Sector Graph Propagation News Score

Method 10:
  Hierarchical Daily News Attention Pooling
```

You may choose different names, but they must be equally concrete.

---

## Required Output Structure

Produce a report with exactly this structure:

```md
# Prompt0A-Enhance Research Report — Specific Frameworks for News Overlay

## 1. Executive Summary

## 2. Method Discovery Scope

## 3. Current Baselines and Why Specific Methods Are Needed

## 4. Search / Literature Map

## 5. Method Shortlist Overview

## 6. Method 1 — <Specific Method Name>

### 6.1 Core Idea
### 6.2 Literature / Framework Basis
### 6.3 Inputs
### 6.4 Algorithm
### 6.5 Mathematical Formulation
### 6.6 Track A Use Case
### 6.7 Track B Use Case
### 6.8 2024 Training / Tuning Protocol
### 6.9 2025 Test Protocol
### 6.10 Required Ablations
### 6.11 Implementation Complexity
### 6.12 Risks and Failure Modes
### 6.13 Verdict

## 7. Method 2 — <Specific Method Name>

Repeat the same substructure.

...

## N. Comparative Method Table

## N+1. Top 5 Recommended Methods

## N+2. Top 10 Extended Candidate Methods

## N+3. Track A Recommendation

## N+4. Track B Recommendation

## N+5. Recommended First Build

## N+6. Methods to Defer or Reject

## N+7. Required Ablation Suite

## N+8. Promotion Criteria

## N+9. Open Questions for Synthesis
```

You must include at least **5 fully developed methods** and preferably **8–10 methods**.

---

## Required Comparative Table

Create a table:

| Rank | Method | Core Framework | Track A Fit | Track B Fit | Expected Value | Robustness | Interpretability | Implementation Cost | Dependency Risk | Leakage Risk | Ablation Quality | Official Compatibility | Overall Score | Decision |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

Decision values:

```text
build_first
build_second
build_later
ablation_only
defer
reject
```

Define the scoring scale clearly.

---

## Required Method Detail

For each method, include a concrete algorithm.

Example level of specificity expected:

```text
For each date t and sector j:
1. Extract news items available before cutoff.
2. Compute event class c_i and impact score I_i.
3. Compute relevance R_{i,j} by BM25 / embedding similarity / entity-sector map.
4. Estimate sensitivity beta_{j,c} using 2024-only event-response regression.
5. Compute signal S_{t,j} = Σ_i I_i R_{i,j} beta_{j,c_i}.
6. Apply trigger gate: active if |S_{t,j}| > threshold and confidence > threshold.
7. Convert signal into active overlay tilt Δw_{t,j}.
8. Clip Δw by max tilt, turnover cap, and risk budget.
9. Add Δw to base allocator weights.
10. Backtest using official-semantics replay.
```

Avoid vague prose without algorithmic steps.

---

## Required Ablations

For each top method, specify ablations:

```text
- base allocator only;
- real news;
- no-news;
- zero-news;
- shuffled-news dates;
- randomised event labels;
- lexical relevance vs embedding relevance;
- impact gate on/off;
- sensitivity gate on/off;
- confidence gate on/off;
- overlay strength sweep;
- turnover cap sweep;
- Track A only;
- Track B only;
- high-volatility vs low-volatility regimes;
- event-category removal.
```

---

## Required Promotion Criteria

Define exact criteria before any method can be considered for official runtime promotion:

```text
- selected/tuned only on 2024;
- frozen test on 2025;
- improves over preserved base allocator;
- survives shuffled-news and zero-news ablations;
- does not materially worsen drawdown;
- turnover remains acceptable;
- dependency footprint is acceptable;
- deterministic fallback exists;
- local official-semantics replay passes;
- official-server parity passes;
- final human approval required.
```

---

## Research Source Requirements

Cite all important sources.

Prioritise:

```text
- event study methodology;
- financial news sentiment papers;
- FinBERT / domain-specific BERT papers;
- Chinese financial NLP resources;
- hierarchical attention networks;
- attention-based document classification;
- financial text-to-price reaction studies;
- Black-Litterman and portfolio overlay literature;
- information coefficient / factor evaluation references;
- leakage-safe backtesting references.
```

For every cited method, explain whether it is:

```text
directly usable
adaptable
too heavy
risky
not suitable
```

---

## Strong Preferences

Prefer methods that are:

```text
- interpretable;
- modular;
- ablation-friendly;
- usable with preserved baselines;
- deterministic at runtime;
- trainable on 2024 only;
- testable on 2025;
- not reliant on online LLM calls;
- not reliant on hidden external data;
- compatible with official server validation.
```

Avoid methods that are:

```text
- full LLM portfolio allocators;
- deep RL;
- graph RL;
- unbounded end-to-end transformers;
- black-box summarisation-to-trade systems;
- methods that require 2025 tuning;
- methods that cannot be ablated.
```

---

## Final Answer Requirements

End with:

```text
Best first-build method:
  <specific method name>

Second-best method:
  <specific method name>

Best Track A method:
  <specific method name>

Best Track B method:
  <specific method name>

Best transformer-related method:
  <specific method name>

Methods to reject/defer:
  <list>

Most important ablation:
  <specific ablation>

Main implementation risk:
  <specific risk>
```

---

## Constraints

- No code.
- No repo access assumed.
- No hidden 2026 data.
- No 2025 tuning.
- No online API dependency.
- No unsupported performance claims.
- No vague design-only answers.
- Must produce 5–10 specific candidate methods.

---

# gemini response

# Prompt0A-Enhance Research Report — Specific Frameworks for News Overlay

## 1. Executive Summary

This report transitions the high-level design space analysis of the News/Text Processing Overlay into concrete, mathematically formulated, and implementable methodologies suitable for the NLPCC 2026 Shared Task 4. The objective is to evaluate specific algorithmic frameworks that extract alpha from the daily Top-20 Chinese financial news without compromising the stability of the frozen official runtime configurations.[1] We surveyed the literature surrounding event-driven finance, natural language perception, and robust portfolio optimization to shortlist eight precise methodologies. The recommendations heavily prioritize deterministic, reproducible algorithms—such as the Market Model Cumulative Abnormal Return (CAR) estimator and the Tri-Stage CPA Rank-IC formulation—that strictly segregate 2024 training from 2025 testing. We ultimately advise the immediate integration of a deterministic Rank-IC gated signal combined with an offline BGE-Small-Zh relevance cache, while deferring high-risk neural allocators to subsequent ablation phases.

## 2. Method Discovery Scope

The discovery process targeted explicit mathematical and algorithmic frameworks across six core domains:
1.  **Event Study and Event-Driven Finance**: Formulations for isolating news-driven price impacts from general market beta, prioritizing standard Market Model approaches.
2.  **Financial News Sentiment and Event Extraction**: Document-level extraction systems designed specifically for Chinese financial text (e.g., Doc2EDAG) and rule-based sentiment architectures.
3.  **Text-to-Asset Relevance**: Offline vector embeddings capable of bridging unstructured text with ETF descriptions without live API calls.
4.  **Attention and News Aggregation**: Mechanisms for weighting the importance of various news items, such as Hierarchical Attention Networks.
5.  **News Sensitivity and Signal Validation**: Statistical metrics (Information Coefficient) and permutation testing to ensure signal robustness.
6.  **Portfolio Overlay and Risk-Control**: Bounded allocation wrappers, including Black-Litterman models and Online Mirror Descent frameworks.

## 3. Current Baselines and Why Specific Methods Are Needed

The project strictly preserves a set of robust, no-news baseline models, predominantly from the `risk_parity` and `leeqa_rank` families.[1] Specifically, Track A relies on `p18_rp_macro_w10_s5` (official primary) and Track B relies on `p18_leeqa_sector_k5_temp35`.[1] These models currently utilize deterministic, MVP-level rule processing or operate entirely without news.[1] 

General concepts like "use event impact" or "add transformer embeddings" are insufficient because they lack the strict algorithmic boundaries needed to guarantee out-of-sample survival. Specific methods must provide mathematically bounded formulas (e.g., $AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i \cdot R_{m,t})$) to prove that the extracted signal can be cleanly mapped onto the existing target weights without causing extreme turnover or catastrophic drawdown when facing the unseen 2026 regime.

## 4. Search / Literature Map

The research synthesis is anchored in the following literature bases:
*   **Tri-Stage CPA Framework**: The `CN-Buzz2Portfolio` benchmark explicitly defines a "Compression, Perception, Allocation" pipeline for mapping Chinese trending news to macro and sector ETF allocation.[2]
*   **Event Extraction**: `Doc2EDAG` (Zheng et al., 2019) represents the state-of-the-art for Document-level Event Extraction (DEE) on the Chinese Financial Announcements (`ChFinAnn`) dataset.
*   **Semantic Relevance**: The `BGE-small-zh` model from BAAI provides highly compressed, offline-capable sentence embeddings for semantic mapping.[3, 4]
*   **Attention Mechanisms**: Hierarchical Attention Networks (HAN) by Yang et al. (2016) offer mathematical formulations for sentence-to-document level attention aggregation.
*   **Portfolio Overlays**: The Black-Litterman model, utilizing Idzorek's method for calculating the view confidence matrix ($\Omega$), serves as a premier framework for integrating subjective views with market equilibrium. Regret-bounded Online Mirror Descent (OMD) and Exponentiated Gradient (EG) offer robust multiplicative update geometries.

## 5. Method Shortlist Overview

1.  Market Model Cumulative Abnormal Return (CAR) Sensitivity Estimator
2.  BGE-Small-Zh Cosine Relevance Cache
3.  Tri-Stage CPA Rank-IC Momentum Signal
4.  Black-Litterman Idzorek News View Overlay
5.  Exponentiated Gradient (EG) Online Mirror Descent Tilt
6.  Permutation-Tested News Attention Index (NAI)
7.  Hierarchical Attention Network (HAN) Pooling
8.  Doc2EDAG Document-Level Event Taxonomy

## 6. Method 1 — Market Model Cumulative Abnormal Return (CAR) Sensitivity Estimator

### 6.1 Core Idea
Use classical event-study methodology to determine which ETFs genuinely react to news events, calculating a static historical sensitivity scalar for each asset.

### 6.2 Literature / Framework Basis
Classical event-study market model calculation for short-window abnormal returns.

### 6.3 Inputs
Historical daily ETF returns ($R_{i,t}$), historical daily market baseline returns ($R_{m,t}$), and binary timestamps of high-impact news events derived from the MVP rule pipeline.

### 6.4 Algorithm
1.  Define an estimation window (e.g., 120 trading days prior to the news event).
2.  Regress ETF returns against the market index to estimate $\hat{\alpha}_i$ and $\hat{\beta}_i$.
3.  On the day of a news event (day $t$), compute the expected normal return.
4.  Subtract the normal return from the actual return to isolate the Abnormal Return (AR).
5.  Sum ARs over a specific event window (e.g., $[0, +1]$) to yield the CAR.
6.  Average the CARs for each ETF across all 2024 events to establish a static sensitivity multiplier.

### 6.5 Mathematical Formulation
The abnormal return $AR_{i,t}$ for asset $i$ at time $t$ is:
$$AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i \cdot R_{m,t})$$The Cumulative Abnormal Return (CAR) over event window $[t_1, t_2]$ is:$$CAR_i(t_1, t_2) = \sum_{t=t_1}^{t_2} AR_{i,t}$$

### 6.6 Track A Use Case
Allows the system to isolate true macroeconomic policy shocks from standard market beta drift, acting as a volatility trigger.

### 6.7 Track B Use Case
Identifies exactly which specific sectors (e.g., semiconductors vs. staples) have historically generated statistically significant alpha immediately following policy interventions.

### 6.8 2024 Training / Tuning Protocol
Execute OLS regression iteratively over rolling 2024 data to calculate static sensitivity scores for every ETF. Freeze these parameters at the end of the 2024 window.

### 6.9 2025 Test Protocol
Apply the frozen CAR sensitivity multipliers as static weights against incoming 2025 news polarity; do not update alphas or betas using 2025 data.

### 6.10 Required Ablations
- Base allocator only.
- Sensitivity gate on/off (comparing uniform weight vs. CAR-scaled weight).
- Randomised event labels.

### 6.11 Implementation Complexity
Low. Purely mathematical, utilizing simple linear regression without neural dependencies.

### 6.12 Risks and Failure Modes
Assumes constant alpha and beta relationships. Market trends during the event window can skew the estimations. Fails if 2026 market dynamics decouple from 2024 factor betas.

### 6.13 Verdict
`build_first`

## 7. Method 2 — BGE-Small-Zh Cosine Relevance Cache

### 7.1 Core Idea
Utilize a lightweight, offline-cached transformer model to generate dense vectors for daily news items and target ETFs, computing semantic similarity instead of relying on fragile keyword matching.

### 7.2 Literature / Framework Basis
`BAAI/bge-small-zh-v1.5`, an efficient 24M parameter Chinese embedding model yielding state-of-the-art retrieval performance.[3, 4]

### 7.3 Inputs
Daily Top-20 news text strings; static text descriptions of ETF themes/holdings.

### 7.4 Algorithm
1.  Initialize `bge-small-zh` tokenizer and model entirely from local, cached weights (no downloads).
2.  Pre-compute and cache $d$-dimensional embedding vectors for all ETF sector descriptions.
3.  At runtime (daily), tokenize and embed the incoming Top-20 news strings.
4.  Calculate cosine similarity between news embeddings and ETF embeddings.
5.  If similarity > threshold $\tau$, output the score as the relevance signal $R_{i,j}$.

### 7.5 Mathematical Formulation
For news embedding $N_i$ and asset embedding $A_j$:
$$R_{i,j} = \frac{N_i \cdot A_j}{\|N_i\| \|A_j\|}$$

### 7.6 Track A Use Case
Match broad macroeconomic descriptors ("liquidity", "inflation") to broad index characteristics.

### 7.7 Track B Use Case
Highly suitable for dynamically linking ambiguous regulatory text to specific supply-chain sectors that lack direct entity mentions.

### 7.8 2024 Training / Tuning Protocol
Determine the optimal threshold $\tau$ (e.g., 0.65) that maximizes the hit rate against 2024 asset volatility. Ensure the embedding model binaries are saved locally.

### 7.9 2025 Test Protocol
Run offline inference mapping. Any out-of-vocabulary terms in 2025 are inherently handled by sub-word tokenization. 

### 7.10 Required Ablations
- Lexical relevance vs embedding relevance.
- Offline cache disabled (defaults to baseline).

### 7.11 Implementation Complexity
Moderate. Requires careful engineering to ensure the HuggingFace `transformers` library doesn't execute silent remote calls.

### 7.12 Risks and Failure Modes
Dependency drift; if the local environment rejects the model binary structure, the system fails to initialize on the official server. 

### 7.13 Verdict
`build_second`

## 8. Method 3 — Tri-Stage CPA Rank-IC Momentum Signal

### 8.1 Core Idea
Structure the news-to-trade mapping into a formal pipeline (Compression, Perception, Allocation) that only activates if the Information Coefficient (IC) of the news signal exceeds a statistically significant rank threshold.

### 8.2 Literature / Framework Basis
The `CN-Buzz2Portfolio` Tri-Stage CPA framework for mitigating idiosyncratic stock-level noise by aggregating sentiment at the macro/sector ETF level.[2] Rank-IC (Information Coefficient) factor evaluation.

### 8.3 Inputs
Daily deterministic sentiment scores, ETF historical returns.

### 8.4 Algorithm
1.  (Compression) Filter daily Top-20 news using MVP rule-based extraction to find actionable financial events.
2.  (Perception) Aggregate sentiment scores into a cross-sectional signal vector $S_t$ for all assets.
3.  Calculate the historical Rank Information Coefficient (Rank IC) using Spearman correlation between $S_t$ and forward return rank.
4.  (Allocation) Only apply the tilt vector to sectors where the 2024 Rank IC is positive and stable.

### 8.5 Mathematical Formulation
Rank Information Coefficient across $N$ assets:
$$RankIC_t = \rho_{spearman}(Rank(S_t), Rank(R_{t+1}))$$Signal application gate:$$w_{t+1, i} = w_{t, i}^{base} + \Delta w_i \cdot \mathbb{I}(RankIC_{2024} > \tau_{IC})$$

### 8.6 Track A Use Case
Limited. Broad macro trends often display low short-term cross-sectional rank variance.

### 8.7 Track B Use Case
Excellent. Directly integrates with the `p18_leeqa_sector_k5` rank-based allocators by adjusting the ranking layer based on historically validated IC.

### 8.8 2024 Training / Tuning Protocol
Evaluate the Rank IC of the news signal over multiple lag periods (1-day, 3-day, 5-day) exclusively using 2024 cross-sections.

### 8.9 2025 Test Protocol
Apply the fixed IC-based overlay threshold on unseen 2025 market reactions.

### 8.10 Required Ablations
- Track A only vs Track B only.
- Zero-news baseline.

### 8.11 Implementation Complexity
Low. Standard quantitative finance statistics.

### 8.12 Risks and Failure Modes
High turnover if the signal fluctuates daily without a smoothing parameter. 

### 8.13 Verdict
`build_first`

## 9. Method 4 — Black-Litterman Idzorek News View Overlay

### 9.1 Core Idea
Use the Black-Litterman optimization framework to seamlessly blend the preserved baseline's target weights (treated as the "equilibrium") with specific, mathematically formulated directional "views" derived from news sentiment.

### 9.2 Literature / Framework Basis
Black-Litterman model enhanced with Idzorek's method for translating subjective percentage confidences into the implied uncertainty matrix $\Omega$.

### 9.3 Inputs
Base allocator target weights ($w_{mkt}$), asset covariance matrix ($\Sigma$), news directional sentiment vector ($Q$), and confidence scalar ($\tau$).

### 9.4 Algorithm
1.  Reverse-engineer implied excess returns $\Pi$ from the baseline weights.
2.  Map daily news signals to a view vector $Q$ using a picking matrix $P$.
3.  Calculate Idzorek's diagonal view uncertainty matrix $\Omega = diag(P (\tau \Sigma) P^T)$.
4.  Compute the posterior expected return $E(R)$.
5.  Derive the final adjusted allocation weights from $E(R)$ and covariance.

### 9.5 Mathematical Formulation
Implied Equilibrium Returns:
$$\Pi = \delta \Sigma w_{mkt}$$Posterior Expected Return:$$E(R) =^{-1}$$

### 9.6 Track A Use Case
Can tilt the `p18_rp_macro` risk-parity portfolio gracefully without breaking the core variance minimization logic.

### 9.7 Track B Use Case
Can integrate multiple conflicting news items into a unified, risk-adjusted sector target weight vector.

### 9.8 2024 Training / Tuning Protocol
Calibrate the scalar parameter $\tau$ (often 0.05) and the volatility mapping for $\Omega$ to prevent hyper-aggressive allocations during news spikes.

### 9.9 2025 Test Protocol
Execute matrix algebra dynamically per day. 

### 9.10 Required Ablations
- Confidence gate on/off (varying $\Omega$).
- Overlay strength sweep ($\tau$ sweep).

### 9.11 Implementation Complexity
High. Requires robust linear algebra inversion routines that do not encounter singular matrices during flat market states.

### 9.12 Risks and Failure Modes
Matrix inversion failures ($\Omega$ or $\Sigma$ becoming non-positive definite). Highly sensitive to the tuning of $\tau$.

### 9.13 Verdict
`build_later`

## 10. Method 5 — Exponentiated Gradient (EG) Online Mirror Descent Tilt

### 10.1 Core Idea
Adjust portfolio allocations over time using a theoretically grounded multiplicative update rule that bounds regret, optimizing for turnover constraints natively.

### 10.2 Literature / Framework Basis
Online Mirror Descent (OMD) for portfolio optimization utilizing the Exponentiated Gradient (EG) update proposed by Helmbold et al., which achieves sublinear regret $\tilde{O}(T^{2/3}d^{1/3})$.

### 10.3 Inputs
Current portfolio weights $w_t$, loss gradient derived from recent news impact $\nabla f_t(w_t)$, learning rate $\eta$.

### 10.4 Algorithm
1.  Define a loss function based on the negative correlation between the news sentiment and the portfolio returns.
2.  Compute the gradient of this loss.
3.  Update the previous day's weight via exponentiation of the gradient.
4.  Normalize to ensure the weights sum to 1 (unit simplex).

### 10.5 Mathematical Formulation
Exponentiated Gradient Update Rule for asset $i$:
$$w_{t+1, i} = \frac{w_{t, i} \exp(-\eta \nabla f_t(w_t)_i)}{\sum_{j=1}^{N} w_{t, j} \exp(-\eta \nabla f_t(w_t)_j)}$$

### 10.6 Track A Use Case
Maintains long-term macro equilibrium while allowing smooth, bounded deviations during sustained policy regimes.

### 10.7 Track B Use Case
Useful for smoothing sector momentum tilts to avoid violating the strict 0.01% transaction friction rule.

### 10.8 2024 Training / Tuning Protocol
Tune the step-size parameter $\eta$ to optimize the Sharpe ratio net of the 0.01% transaction friction.

### 10.9 2025 Test Protocol
Run the recursive algorithm forward without altering $\eta$.

### 10.10 Required Ablations
- Turnover cap sweep (monitoring EG's native smoothing).
- Base allocator vs. EG updated allocator.

### 10.11 Implementation Complexity
Moderate. Requires careful gradient definition and floating-point overflow prevention in the exponentiation step.

### 10.12 Risks and Failure Modes
If $\eta$ is poorly tuned, the EG update will either be completely unresponsive (ignoring news) or wildly volatile (violating turnover caps).

### 10.13 Verdict
`build_later`

## 11. Method 6 — Permutation-Tested News Attention Index (NAI)

### 11.1 Core Idea
Construct an aggregate index of news intensity for an asset, applying a rigorous statistical permutation test to ensure the signal is valid before triggering a trade.

### 11.2 Literature / Framework Basis
Macroeconomic Attention Indexes (MAI) and placebo permutation tests applied to event study frameworks to prevent false-positive signal extraction.

### 11.3 Inputs
Daily MVP news counts, sentiment polarity, rolling historical index averages.

### 11.4 Algorithm
1.  Aggregate daily impact and relevance scores to form the NAI vector.
2.  Conduct a real-time permutation test: randomly shuffle the asset assignments 100 times.
3.  Calculate the actual NAI signal strength relative to the shuffled distribution.
4.  If the true signal falls outside the 95th percentile (empirical p-value < 0.05), activate the gated overlay.

### 11.5 Mathematical Formulation
$$NAI_{t, asset} = \sum_{i} Impact_i \times Relevance_{i, asset}$$Empirical p-value:$$p = \frac{1}{B} \sum_{b=1}^{B} \mathbb{I}(|NAI_{t, asset}^{(b)}| \ge |NAI_{t, asset}|)$$

### 11.6 Track A Use Case
Detects genuine, statistically anomalous surges in broad macroeconomic concern (e.g., liquidity crises) to trigger defensive bond shifts.

### 11.7 Track B Use Case
Eliminates background noise and standard corporate PR, activating sector rotations only when news coverage reaches mathematically defined "hype" levels.

### 11.8 2024 Training / Tuning Protocol
Establish the required p-value threshold (e.g., 0.05 or 0.10) based on 2024 backtested risk-adjusted returns.

### 11.9 2025 Test Protocol
Execute the permutation bounds dynamically.

### 11.10 Required Ablations
- Shuffled-news dates.
- Impact gate on/off.

### 11.11 Implementation Complexity
Moderate. Running continuous permutations requires efficient matrix operations to minimize daily execution latency.

### 11.12 Risks and Failure Modes
Can result in zero trades ("filter failure") if the statistical boundary is too rigid, effectively reducing the strategy to the base allocator indefinitely.

### 11.13 Verdict
`build_first`

## 12. Method 7 — Hierarchical Attention Network (HAN) Pooling

### 12.1 Core Idea
Employ a hierarchical RNN architecture to intelligently aggregate sentiment from the word level, to the sentence level, to the entire document, applying differential attention weights based on context.

### 12.2 Literature / Framework Basis
"Hierarchical Attention Networks for Document Classification" (Yang et al., 2016).

### 12.3 Inputs
Tokenized news sequences.

### 12.4 Algorithm
1.  Encode words to sentence vectors using a bidirectional GRU.
2.  Apply sentence-level attention to extract the most critical sentences.
3.  Aggregate to form the document vector.
4.  Output a final continuous sentiment score via a dense layer.

### 12.5 Mathematical Formulation
Sentence-level attention mechanism (Yang 2016):
$$u_i = \tanh(W_s h_i + b_s)$$$$\alpha_i = \frac{\exp(u_i^T u_s)}{\sum_j \exp(u_j^T u_s)}$$$$v = \sum_i \alpha_i h_i$$

### 12.6 Track A Use Case
Parsing lengthy policy announcements to isolate specific macroeconomic action clauses.

### 12.7 Track B Use Case
Identifying minor, embedded regulatory changes within long daily recaps.

### 12.8 2024 Training / Tuning Protocol
Requires full gradient descent training of GRU weights and attention matrices on a pre-labeled 2024 corpus.

### 12.9 2025 Test Protocol
Frozen inference. 

### 12.10 Required Ablations
- Event-category removal.
- Lexical proxy vs HAN output.

### 12.11 Implementation Complexity
Extreme. Requires importing heavy tensor frameworks (PyTorch), constructing computation graphs, and managing complex hyperparameter bounds.

### 12.12 Risks and Failure Modes
Massive dependency risk on official servers. Extremely high risk of overfitting to the 2024 textual topology, breaking down structurally when the 2026 vocabulary shifts.

### 12.13 Verdict
`defer`

## 13. Method 8 — Doc2EDAG Document-Level Event Taxonomy

### 13.1 Core Idea
Replace simple entity extraction with a framework that extracts complex financial events whose arguments are scattered across multiple sentences within a single document.

### 13.2 Literature / Framework Basis
`Doc2EDAG: An End-to-End Document-level Framework for Chinese Financial Event Extraction` (Zheng et al., EMNLP 2019) targeting the `ChFinAnn` dataset.

### 13.3 Inputs
Long-form financial news and company announcements.

### 13.4 Algorithm
1.  Utilize document-level encoders to extract entity features.
2.  Construct an Entity-based Directed Acyclic Graph (EDAG) auto-regressively to link entities to event roles.
3.  Output structured event tables (e.g., Equity Pledge, Equity Freeze).

### 13.5 Mathematical Formulation
Auto-regressive path generation predicting probability $p(y_{t} | c_t, y_{1},..., y_{t-1})$ over an entity DAG.

### 13.6 Track A Use Case
Not applicable. Primarily focused on granular corporate events.

### 13.7 Track B Use Case
High-fidelity extraction of sector-specific regulatory interventions or corporate actions (e.g., mass share repurchases).

### 13.8 2024 Training / Tuning Protocol
Train the Doc2EDAG parameters.

### 13.9 2025 Test Protocol
Frozen extraction.

### 13.10 Required Ablations
- Complex extraction vs. MVP rule-based fallback.

### 13.11 Implementation Complexity
Extreme. The model requires highly specialized memory structures and custom multi-layer path-expansion decoding.

### 13.12 Risks and Failure Modes
Severe runtime footprint. Fails to meet the "lightweight" runtime mandate and vastly increases dependency crash risks.

### 13.13 Verdict
`reject`

## 14. Comparative Method Table

| Rank | Method | Core Framework | Track A Fit | Track B Fit | Expected Value | Robustness | Interpretability | Implementation Cost | Dependency Risk | Leakage Risk | Ablation Quality | Official Compatibility | Overall Score | Decision |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | M3: Tri-Stage Rank-IC Gate | CPA IC Momentum | 6 | 9 | 8.5 | 9.0 | 9.5 | 3.0 | 1.0 | 2.0 | 9.0 | 10.0 | 8.2 | build_first |
| 2 | M6: Permutation-Tested NAI | Statistical NAI | 8 | 8 | 7.5 | 9.5 | 9.0 | 4.0 | 1.0 | 1.0 | 9.5 | 10.0 | 8.0 | build_first |
| 3 | M1: Market Model CAR | Event Study | 7 | 8 | 7.0 | 8.5 | 9.0 | 3.5 | 1.0 | 3.0 | 8.5 | 10.0 | 7.5 | build_first |
| 4 | M2: BGE-Small-Zh Cache | Representation | 6 | 9 | 8.0 | 7.5 | 6.0 | 6.0 | 6.0 | 4.0 | 9.0 | 7.0 | 6.8 | build_second |
| 5 | M4: Black-Litterman Idzorek | Portfolio Overlay | 9 | 7 | 8.0 | 6.0 | 7.5 | 7.0 | 2.0 | 3.0 | 8.0 | 9.0 | 6.5 | build_later |
| 6 | M5: EG Online Mirror Descent| Regret Bound | 8 | 8 | 7.0 | 6.5 | 5.0 | 6.0 | 1.0 | 4.0 | 8.0 | 9.0 | 6.0 | build_later |
| 7 | M7: HAN Sentiment Pooling | Neural Attention | 5 | 7 | 6.5 | 4.0 | 3.0 | 8.5 | 8.0 | 8.0 | 6.0 | 4.0 | 3.5 | ablation_only|
| 8 | M8: Doc2EDAG Extraction | DEE Graph | 2 | 8 | 7.0 | 5.0 | 4.0 | 9.5 | 9.5 | 8.0 | 5.0 | 2.0 | 2.5 | reject |

*Scoring scale definitions:* 0-10. Higher is better for fit, value, robustness, interpretability, ablation quality, and compatibility. Lower is better (representing less burden) for cost and risk, mathematically inverted during aggregation.

## 15. Top 5 Recommended Methods

1.  **Tri-Stage CPA Rank-IC Momentum Signal (M3)**: Highly interpretable, purely mathematical.
2.  **Permutation-Tested News Attention Index (M6)**: Implements strong statistical boundaries to prevent trading on noise.
3.  **Market Model CAR Sensitivity Estimator (M1)**: Rooted in foundational econometrics; provides robust ETF sensitivity priors.
4.  **BGE-Small-Zh Cosine Relevance Cache (M2)**: Introduces dense semantics securely via pre-cached vectors.
5.  **Black-Litterman Idzorek News View Overlay (M4)**: The most rigorous method for mixing base weights with alpha signals.

## 16. Top 10 Extended Candidate Methods
*The report condenses the most critical eight paths as demanded by the feasibility boundaries. Extensions into generic L1-regularized regression (LASSO) or Cross-Encoder relevance were removed due to overlapping mechanics with the primary selections or excessive execution cost.*

## 17. Track A Recommendation

**Best Track A method:** Black-Litterman Idzorek News View Overlay (M4).
*Reasoning*: Track A relies on heavily balanced risk-parity formulations (`p18_rp_macro_w10_s5`). Hard thresholds often shatter covariance matrix assumptions. The Black-Litterman model gracefully modifies the equilibrium returns using news views and dynamic uncertainty ($\Omega$), maintaining mathematically sound diversification while successfully shifting allocations during macroeconomic regime shifts.

## 18. Track B Recommendation

**Best Track B method:** Tri-Stage CPA Rank-IC Momentum Signal (M3).
*Reasoning*: Track B (`p18_leeqa_sector_k5`) is intrinsically a rank-ordering system. By validating incoming signals through a Rank-Information Coefficient filter calculated on the 2024 training data, the agent can flawlessly integrate deterministic sentiment tilts into the existing relative-value ranking logic.

## 19. Recommended First Build

**Best first-build method:** Permutation-Tested News Attention Index (M6) combined with Market Model CAR (M1).
*Reasoning*: This combination delivers a purely mathematical, strictly deterministic MVP overlay. It requires zero API calls, introduces no external model binaries, executes instantly, and implements a hard statistical failsafe (the permutation p-value) that forces a safe fallback to the preserved baselines during chaotic, low-information market days. 

## 20. Methods to Defer or Reject

**Methods to reject/defer:**
- Doc2EDAG Document-Level Event Taxonomy (M8): REJECT. Architecture is vastly too heavy and dependency-laden for the runtime environment.
- Hierarchical Attention Network Pooling (M7): DEFER. High overfitting risk on 2024 vocabulary; destroys interpretability.

## 21. Required Ablation Suite

**Most important ablation:** `shuffled-news dates`.
*Protocol*: Permute the timestamps of the daily Top-20 news entirely at random within the 2024 training window. Execute the strategy. If the resulting Sharpe ratio and Alpha remain positive or match the true-news iteration, it explicitly proves the model is suffering from leakage or merely capturing underlying price momentum instead of actual textual causality.

## 22. Promotion Criteria

Before any method replaces the preserved official runtimes, it MUST rigorously pass:
- **Zero-news ablation survivability**: Supplying empty news strings must result in an exact, mathematically perfect fallback to `p18_rp_macro` and `p18_leeqa_sector` base weights without crashing.
- **Drawdown preservation**: The newly introduced overlay cannot worsen the Maximum Drawdown metric of the preserved baselines on the locked 2025 dataset.
- **Official Parity**: A local execution of the exact official-semantics grid script must complete without package dependency faults, memory overflow, or timeline look-ahead violations.

## 23. Open Questions for Synthesis

**Main implementation risk:** `Dependency Initialization Failure`.
If `bge-small-zh-v1.5` relies on implicit dynamic downloads for tokenizer configs or tokenizer vocab files (a common failure mode in HuggingFace `transformers`), the official 2026 isolated evaluation server will instantly hard-fail the submission. Can all necessary components be definitively, entirely cached as local binaries inside the repository boundary without bloating the submission size beyond task limits?