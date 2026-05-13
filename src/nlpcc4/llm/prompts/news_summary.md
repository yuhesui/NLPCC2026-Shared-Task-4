# News Summary Prompt Placeholder

PLANNED - not implemented yet.

The final prompt must require valid JSON output with compact news facts, confidence, source-date awareness, and no future claims.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not infer unavailable future market moves.
- Mark uncertainty explicitly.
- Invalid JSON must not reach strategy logic.
