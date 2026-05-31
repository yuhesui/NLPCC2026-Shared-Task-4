# B_LIST_HARDENING.md

## Risk Register

| Risk | Mitigation |
|---|---|
| hidden 2026 regime shift | conservative S1/OCO fallback, robust BL, low overfit tuning |
| prompt/API instability | no-LLM fallback, cached extraction, schema validation |
| future leakage | leakage guard, official DataLoader semantics, tests |
| dependency failure | Docker/environment lock, dependency audit |
| excessive turnover | turnover throttle, cash feasibility, rebalance bands |
| optimiser failure | fallback manager logs reason and returns S1 |
| raw data mutation | data manifests and read-only raw policy |

## Final Submission Checklist

- [ ] all prompts logged through `create_implementation_log`;
- [ ] full tests/smoke checks run;
- [ ] official server compatibility checked;
- [ ] local backtester checked;
- [ ] no current-day leakage;
- [ ] no post-2025 resources;
- [ ] configs frozen;
- [ ] fallback works without LLM/API;
- [ ] outputs and reports generated;
- [ ] package excludes unnecessary cache/temp files.

## Prompt14 Current Status

- The official wrapper, portfolio adapter, order planner, trade validator, and SystemRunner have been repaired.
- Stage 1 remains deterministic/rule-based by default; LLM and Hugging Face paths are optional and disabled.
- Track A default is `robust_bl_track1` with `s1_macro` fallback.
- Track B default is `s1_sector`; `sector_rotation_track2` is ablation/experimental until construction-period evidence improves.
- Remaining B-list blockers are wrapper-based full-year 2024/2025 validation, package dry-run from a clean extraction, and any organiser-required Docker/equivalent environment lock.

## Prompt15 Current Status

- DRO-BL-RP, BSA-RP, ARMOR-OMD, LEEQA-Rank, KG-MoE-Lite, HGF-MPC, and CEVA-KF/CIGA have functional MVP paths, configs, and focused tests.
- Offline BGE-small Chinese embeddings and FinBERT Chinese tone extraction are wired into Stage 1, but final runtime does not depend on them by default.
- Prompt15 grid results are construction-sample evidence because local text-model inference is expensive; full-year 2024 rerun remains required before final promotion.
- Official parity remains proven only for S0/S1 paths inherited from Prompt14. New MVP candidates need official-server parity or an accepted wrapper dry-run before submission.
