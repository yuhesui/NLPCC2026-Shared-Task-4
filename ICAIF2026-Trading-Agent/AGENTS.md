# AGENTS.md — rules for AI coding agents (and humans)

## Read first
`README.md` → `docs/architecture/SYSTEM_ARCHITECTURE.md` → `docs/competition/ICAIF_RULES_AND_PROTOCOL.md`
→ the research plan relevant to your change. The official starter kit (`third_party/`, fetched by
`scripts/setup/fetch_official_kit.sh`) is authoritative over our docs.

## Hard rules
1. **Point-in-time.** Decision code reads data only through `MarketPanel.as_of`, `PITStore.as_of`/`window`,
   `MacroStore`, `FilingStore`, or a `TextStateBuilder`. Every new record type has `available_at`.
   Never catch `LeakageViolation` to continue.
2. **No silent fallbacks.** Fallbacks are explicit, recorded in traces, and limited to anticipated
   error classes (`runtime/fallback.py`). Don't add `except Exception: pass`.
3. **No downloads or online calls at runtime.** Models load from configured local paths only;
   network sources are opt-in scripts. Never add an auto-downloading default.
4. **Fees are always on** (0.001). Never weaken `BacktestConfig` cost checks.
5. **Competition rules.** Weights: 30 symbols, 0 ≤ w ≤ 0.30, Σ ≤ 1, finite numbers. Use
   `competition/submission.py` and the official validator. One intended upload per round (ledger).
6. **LLMs/encoders**: generative LLMs must be organizer-listed families. Non-LLM encoders are allowed when
   the model is public and runs locally (team ruling 2026-10-03); paid/hosted APIs are not. Anything
   ambiguous is `requires_rule_confirmation: true`. LLMs extract information; they do not allocate in production.
7. **Secrets** never appear in code, configs, traces or logs (`.env`, `.icaif/`, `private/` are ignored).
8. **Do not vendor the official kit** (no licence); reference it via `official_adapter.py`.

## Conventions
* Package code in `src/icaif/<area>/`; scripts are thin CLIs; docs contain no executable logic.
* Configs are YAML with `extends`; experiments are defined in `configs/experiments/` and run through
  `experiments/runner.py` so they get deterministic IDs and evidence grades. No ad-hoc result files.
* No prompt-numbered files or directories; no Track A/B terminology; no machine-specific paths.
* Every non-trivial change ships tests (`python -m pytest`) and passes `ruff check src tests scripts`.
* Do not delete files silently; update `docs/FINAL_REPO_AUDIT.md` when status changes.
