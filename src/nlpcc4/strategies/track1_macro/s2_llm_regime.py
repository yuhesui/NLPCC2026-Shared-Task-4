"""S2 Track 1 structured LLM regime-to-rules allocator.

The LLM may emit bounded regime JSON only; deterministic rules produce target
weights and fallback to S1 on invalid or uncertain output.
"""


def build_strategy() -> object:
    """Build the Track 1 S2 strategy once implemented."""
    raise NotImplementedError("Track 1 S2 is planned.")
