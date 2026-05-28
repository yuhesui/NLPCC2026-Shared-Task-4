# News Event Extraction V1

Optional controlled extractor prompt. The default Stage 1 MVP uses deterministic rules and does not require this prompt.

Return only schema-valid event tuples with:

- event_type
- entities
- sectors
- direction
- intensity in [0, 1]
- confidence in [0, 1]
- evidence copied from visible pre-cutoff news only
