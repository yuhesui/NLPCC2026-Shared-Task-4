# Event Exposure Prompt Placeholder

PLANNED - not implemented yet.

The final prompt must require valid JSON output with structured events, affected sectors, direction, and confidence.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not use future data.
- Event labels must come from a fixed taxonomy.
- Uncertain or invalid output must fall back to deterministic Track 2 trend-following.
