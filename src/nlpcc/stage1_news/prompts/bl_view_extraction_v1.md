# Black-Litterman View Extraction V1

Optional controlled extractor prompt. Convert validated sector impacts into bounded Black-Litterman-style views.

Do not allocate capital directly. Return only:

- asset_group
- direction
- expected_return_bps
- confidence in [0, 1]
- rationale grounded in validated events
