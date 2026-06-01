# Prompt16 Optimisation Engine Report

| Component | Status | Path | Test | Notes |
|---|---|---|---|---|
| Strategy parameter catalog | pass | `src/tools/optimiser/parameter_space.py` | Prompt16 optimiser tests | Covers DRO-BL-RP, BSA-RP, ARMOR-OMD, LEEQA, KG-MoE-Lite, HGF-MPC, CEVA, and text toggles. |
| Five-fold 80/20 splitter | pass | `src/tools/optimiser/five_fold_split.py` | Prompt16 optimiser tests | Chronological 5 chunks over combined 2024-2025 dates. |
| Cross-validation runner | pass | `src/tools/optimiser/cross_validation.py` | Prompt16 optimiser tests | Generic objective interface. |
| Successive halving | pass | `src/tools/optimiser/successive_halving.py` | Prompt16 optimiser tests | Bounded early-stop helper. |
| Optimisation facade | pass | `src/tools/optimiser/optimisation_engine.py` | Prompt16 optimiser tests | Grid, random, five-fold, and halving entry points. |
| Runtime estimator | pass | `src/tools/optimiser/runtime_estimator.py` | Prompt16 optimiser tests | Scales sample candidate-date cost with folds and HF multipliers. |
| Search config | pass | `configs/tools/optimisation/prompt16_search_space.yaml` | static check | Research-only parameter ranges. |
| Five-fold config | pass | `configs/tools/optimisation/prompt16_five_fold.yaml` | static check | Explicitly labels 2025 use as research CV only. |
| Smoke runner | pass | `scripts/run_optimisation.py` | command smoke | Wrote `.var/prompt16/smoke_results/optimisation_smoke.json`. |

The optimiser is ready for bounded smoke/medium runs. It has not yet been wired to generate leakage-safe full target tensors for every strategy family, so a full search should wait until the target-generation adapters are added.
