# Overnight Search Plan

| Stage | Scope | Candidate Modes | Date Limit Used | Runtime Guard | Status |
|---|---|---|---|---|---|
| Stage 0 | text-cache and parity smoke | no_news, rule_based, bge_small_zh, finbert_tone_chinese, hybrid_rule_bge_finbert | 3 dates | under 10 minutes | complete |
| Stage 1 | 2024 construction replay | no_news, rule_based | 20 dates | under 10 minutes | complete |
| Stage 2 | locked 2025 replay | top-k from Stage 1 | 10 dates | under 10 minutes | complete |
| Stage 3 | five-fold robustness | Stage 1 tensor slices | 5 folds | under 10 minutes | complete |

Full overnight execution can use the same script with larger `--stage1-dates`, `--stage2-dates`, and candidate text mode limits.
