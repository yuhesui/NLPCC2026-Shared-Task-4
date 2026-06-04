# Research Context Digest — Transformer-First Revision

The prior deep-research phase recommended deterministic event-study and NAI methods as safest first-build methods, but it also identified several valuable transformer/attention methods: BGE-style embedding cache, FinBERT/aspect-tone, Title2Event/label-attention extraction, cross-encoder reranking, sector-query attention pooling, temporal attention, and graph-based relevance propagation.

This revised prompt kit intentionally pushes the implementation agent to build these transformer/attention methods explicitly, while preserving deterministic methods only as baseline/fallback controls.

Key caution:

```text
Transformer outputs may improve news understanding, relevance, event extraction, and attention aggregation.
They must not become an unconstrained portfolio allocator.
Portfolio actions remain bounded, gated, traceable, and ablated.
```
