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
