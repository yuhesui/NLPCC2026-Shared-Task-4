# Overnight Search Results

Bounded command:

```powershell
python scripts\run_prompt17_overnight_search.py --stage0-dates 3 --stage1-dates 20 --stage2-dates 10 --max-candidates-per-track 12 --candidate-text-modes no_news,rule_based --backend numpy
```

| Item | Value |
|---|---|
| Candidate count | 24 |
| Backend | NumPy |
| Runtime | 85.56 seconds |
| Detailed artifact | `.var/prompt17/prompt17_results.json` |
| 2024 scores | `.var/prompt17/candidate_scores_2024.csv` |
| 2025 locked scores | `.var/prompt17/candidate_scores_2025.csv` |

Top bounded-run Track A candidate: `bsa_rp_macro_tilt25`.

Top bounded-run Track B candidate: `sector_rotation_graph15`.
