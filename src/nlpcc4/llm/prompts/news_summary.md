# News Summary Prompt

Return valid JSON with compact news facts, confidence, source-date awareness, and no future claims.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not infer unavailable future market moves.
- Mark uncertainty explicitly.
- Invalid JSON must not reach strategy logic.
