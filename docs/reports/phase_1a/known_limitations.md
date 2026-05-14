# Known Limitations

- Public CSV data is absent in this checkout, so Phase 1a dry-runs use the deterministic official-compatible synthetic loader.
- The target-weight-to-trade converter is based on inspected official semantics but still needs direct official backtest reconciliation.
- Same-day news before 15:00 is supported by official code but defaulted off in custom configs until concrete examples confirm the intended competition policy.
- S2/S3/S4 prompts and schemas are implemented, but manual round-trip quality has not been judged with real model outputs.
- S4 Track 1 is a documented S1 fallback because sector event mapping is mainly a Track 2 concept.
- Metrics are deterministic reproducer basics, not yet reconciled line-by-line with official visualization alignment.
