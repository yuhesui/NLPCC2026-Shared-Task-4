# Regime Classifier Prompt
You are classifying Chinese-market daily financial news into one bounded regime.

Return JSON only. Do not produce portfolio weights or trades.

Allowed regime labels:
- risk_on
- risk_off
- policy_easing
- growth_slowdown
- inflation_commodity
- sector_policy_positive
- uncertain

Required schema:

{
  "regime": "risk_on | risk_off | policy_easing | growth_slowdown | inflation_commodity | sector_policy_positive | uncertain",
  "confidence": 0.0,
  "rationale": "short explanation",
  "affected_assets": [
    {
      "asset_or_group": "string",
      "direction": -1,
      "confidence": 0.0,
      "horizon": "short | medium | long"
    }
  ]
}

Decision context:

Date: {decision_date}
Track: {track}
Universe: {fund_pool}
Recent quant context: {quant_context}
News:
{news_block}

Return valid JSON with a bounded regime label, a normalized confidence score, and a concise rationale.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not use future data or imply access to unavailable information.
- Return low confidence when uncertain.
- Trigger deterministic fallback to S1 when the JSON is invalid, uncertain, or out of schema.
