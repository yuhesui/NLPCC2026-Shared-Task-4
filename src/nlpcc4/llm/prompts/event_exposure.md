# Event Exposure Prompt
You are extracting bounded market events from daily financial news and mapping them to sector exposure categories.

Return JSON only. Do not produce target weights or trades.

Required schema:

{
  "as_of_date": "YYYY-MM-DD",
  "events": [
    {
      "event_type": "policy | macro | earnings | commodity | regulation | liquidity | risk | other",
      "affected_sector": "string",
      "direction": -1,
      "magnitude": 0.0,
      "confidence": 0.0,
      "horizon": "short | medium | long",
      "summary": "short explanation"
    }
  ],
  "overall_confidence": 0.0
}

Decision context:

Date: {decision_date}
Track: {track}
Sector groups: {sector_groups}
Recent trend context: {quant_context}
News:
{news_block}

Return valid JSON with structured events, affected sectors, direction, and confidence.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not use future data.
- Event labels must come from a fixed taxonomy.
- Uncertain or invalid output must fall back to deterministic Track 2 trend-following.
