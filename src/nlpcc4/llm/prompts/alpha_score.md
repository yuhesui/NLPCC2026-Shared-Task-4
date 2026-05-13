# Alpha Score Prompt Placeholder

PLANNED - not implemented yet.

The final prompt must require valid JSON output with bounded per-asset or per-sector scores and confidence.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not use future data.
- Scores must be bounded and schema-valid.
- Low-confidence or invalid output must fall back to S1.
