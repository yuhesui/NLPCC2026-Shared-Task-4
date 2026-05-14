# Alpha Score Prompt
You are extracting bounded alpha scores from daily financial news.

Return JSON only. Do not produce target weights, buy/sell instructions, or cash amounts.

Scores must be in [-1, 1]. Confidence values must be in [0, 1].

Required schema:

{
  "as_of_date": "YYYY-MM-DD",
  "track": "track1 | track2",
  "scores": [
    {
      "asset": "ETF_CODE_OR_GROUP",
      "score": 0.0,
      "confidence": 0.0,
      "horizon": "short | medium | long",
      "reason_tag": "policy | macro | liquidity | commodity | sector | risk | other"
    }
  ],
  "overall_confidence": 0.0
}

Decision context:

Date: {decision_date}
Track: {track}
Universe: {fund_pool}
Base quant weights: {base_weights}
Recent quant context: {quant_context}
News:
{news_block}

Return valid JSON with bounded per-asset or per-sector scores and confidence.

Rules:

- Do not emit direct allocation weights.
- Do not emit buy/sell trades.
- Do not use future data.
- Scores must be bounded and schema-valid.
- Low-confidence or invalid output must fall back to S1.
