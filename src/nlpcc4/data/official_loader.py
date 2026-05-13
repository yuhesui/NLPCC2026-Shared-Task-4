"""Adapters around the official leakage-safe DataLoader.

Do not replace official date slicing here without tests against
`NLPCC_tasks/server_platform/app/core/data_loader.py`.
"""


def load_official_data_loader() -> object:
    """Return the official DataLoader once integration is implemented."""
    raise NotImplementedError("Official DataLoader adapter is planned.")
