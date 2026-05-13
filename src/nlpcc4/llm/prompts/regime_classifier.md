# Regime Classifier Prompt Placeholder

PLANNED - not implemented yet.

The final prompt must require valid JSON output, a bounded regime label, a normalized confidence score, and a concise evidence field.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not use future data or imply access to unavailable information.
- Return low confidence when uncertain.
- Trigger deterministic fallback to S1 when the JSON is invalid, uncertain, or out of schema.
