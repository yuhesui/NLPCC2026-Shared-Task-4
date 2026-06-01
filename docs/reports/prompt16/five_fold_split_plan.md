# Prompt16 Five-Fold 80/20 Split Plan

Date source: combined `data/train_2024` and `data/public_a_2025` anchor trading dates. Total dates: 485. Label: research cross-validation / robustness analysis. This must not be described as final 2025 tuning.

| Fold | Train Chunks | Validation Chunk | Train Date Range(s) | Validation Date Range | Notes |
|---:|---|---|---|---|---|
| 1 | 2,3,4,5 | 1 | 20240531-20241024; 20241025-20250319; 20250320-20250808; 20250811-20251231 | 20240102-20240530 | 388 train / 97 validation dates |
| 2 | 1,3,4,5 | 2 | 20240102-20240530; 20241025-20250319; 20250320-20250808; 20250811-20251231 | 20240531-20241024 | 388 train / 97 validation dates |
| 3 | 1,2,4,5 | 3 | 20240102-20240530; 20240531-20241024; 20250320-20250808; 20250811-20251231 | 20241025-20250319 | 388 train / 97 validation dates |
| 4 | 1,2,3,5 | 4 | 20240102-20240530; 20240531-20241024; 20241025-20250319; 20250811-20251231 | 20250320-20250808 | 388 train / 97 validation dates |
| 5 | 1,2,3,4 | 5 | 20240102-20240530; 20240531-20241024; 20241025-20250319; 20250320-20250808 | 20250811-20251231 | 388 train / 97 validation dates |

Final-policy guardrail: choose final submission parameters from 2024 construction evidence unless a report explicitly marks later experiments as research-only robustness analysis.
