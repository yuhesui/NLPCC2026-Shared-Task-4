# Implementation Log: track_b_research_minor_enhancement - g21b_g12b_stabilization_tuner_audit

**Created:** 2026-06-11 12:25:19

## Summary

Ran scoped blocked Track B research for G21B and G12B: Stage 0 local smoke, 12-row 2024 variant matrix from Prompt23 fresh-real rows, 2024-only freeze, frozen 2025 lookup, material-difference review, preserved-control delta check, ablation evidence, and tuner capability audit.

## Files Changed

scripts/run_track_b_research.py,outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_research,tests/test_nlpcc/test_news_overlay/test_scaffold.py

## Tests / Checks

rtk --version; rtk git status; rtk grep optuna|bayes|random_search|coordinate_search|hyperopt|tpe .; rtk python scripts/run_track_b_research.py --stage reports --skip-smoke; rtk python scripts/run_track_b_research.py --stage stage0 --device auto --batch-size 64; rtk python -m pytest tests/test_nlpcc/test_news_overlay -q; rtk git diff --name-only -- NLPCC_tasks configs/systems configs/tracks

## Caveats

Stage 1 uses Prompt23 fresh-real 2024 row evidence for the 12 scoped variants rather than rerunning full-year transformer inference again. Stage 0 rerun needed a short .var/tbr cache path to avoid Windows long-path cache write failures. Both candidates remain blocked from parity because material differences are identified but not fully explained and preserved-control deltas do not all pass.

## Artifacts

- `outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_research/track_b_research_final_status.md`
- `outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_research/track_b_research_stage1_2024_tune_matrix.csv`
- `outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_research/tuner_capability_audit.md`

## Next Steps

Human review should decide whether to explain Prompt22-vs-Prompt23 material drift or drop G21B/G12B from parity consideration; do not tune on 2025 or change official runtime.
