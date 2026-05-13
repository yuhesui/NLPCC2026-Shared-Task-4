"""Small hashing helpers for run metadata and config fingerprints."""

from hashlib import sha256


def stable_text_hash(text: str) -> str:
    """Return a deterministic SHA-256 hash for text."""
    return sha256(text.encode("utf-8")).hexdigest()
