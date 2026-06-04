# News Overlay Restart Context

Use this file when the context window is compressed or a fresh session starts
inside the Prompt1-x News Overlay phase.

## Restart Packet

Project: NLPCC 2026 Shared Task 4, LLM-based Investment Advisor Agents for
Asset Allocation in the Chinese Market.

Tracks:

- Track A / Track 1: Macro-Asset Allocation.
- Track B / Track 2: Sector-Rotation Allocation.

Frozen official runtime to preserve:

- Track A primary: `p18_rp_macro_w10_s5`.
- Track A fallback: `p18_rp_macro_w40_s5`.
- Track B primary: `p18_leeqa_sector_k5_temp35`.
- Track B fallback: `p18_s1_sector_t35_v30_w20`.

News Overlay status after Prompt1-0:

- Documentation policy exists under `docs/news_overlay/`.
- Method table path: `docs/news_overlay/method_table.md`.
- Transformer architecture table path:
  `docs/news_overlay/transformer_architecture_table.md`.
- Grid table path: `docs/news_overlay/grid_search_table.md`.
- Prompt1x reference artifacts live under
  `outputs/reports/news_overlay/prompt1x/reference/`.
- No production code was implemented by Prompt1-0.

## Read-First Order After Restart

1. `AGENTS.md`
2. `README.md`
3. `docs/news_overlay/README.md`
4. `docs/news_overlay/method_table.md`
5. `docs/news_overlay/transformer_architecture_table.md`
6. `docs/news_overlay/grid_search_table.md`
7. `outputs/reports/news_overlay/prompt1x/reference/`
8. `outputs/reports/prompt20/presented/current_repo_status_report.md`
9. `outputs/reports/prompt20/presented/current_repo_status_table.md`
10. `outputs/reports/prompt20/presented/preserved_candidate_summary.md`
11. `configs/preserved_candidates/manifest.json`
12. Current prompt file under `docs/prompts/news_overlay_prompts/`

## Non-Negotiable Constraints

- Do not change frozen official runtime configs.
- Do not promote News Overlay candidates automatically.
- Tune and select only on 2024.
- Treat 2025 as frozen evaluation only.
- Do not use hidden 2026 data.
- Do not use current-day close, high, low, or return before decision time.
- Same-day news must obey the official timestamp cutoff.
- Do not add online API dependency.
- Do not silently download models.
- Do not add unpinned transformer/model dependencies.
- Do not put model binaries in the official runtime package unless a later
  prompt explicitly approves it.
- All transformer methods need deterministic fallback or unavailable-state
  handling.
- Official-server parity is required before any promotion recommendation.

## Next Prompt

Run:

```text
prompt1_1_section1_transformer_pipeline_scaffold.md
```

Expected focus:

- scaffold `src/nlpcc/news_overlay/`;
- add N/I/S registries and config placeholders;
- add local model availability reporting;
- add deterministic cache interfaces;
- add offline/no-silent-download tests;
- update the Prompt1x method, transformer status, cache, dependency, and grid
  status tables.
