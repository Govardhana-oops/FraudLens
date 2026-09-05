"""Cryptographic SHA-256 Tamper-Evident Hash Chaining Engine."""

import hashlib
import json
from typing import Dict, Any

class TamperEvidentHasher:
    """Computes deterministic SHA-256 hashes chained with the previous block hash."""

    @staticmethod
    def compute_entry_hash(prev_hash: str, entry_payload: Dict[str, Any]) -> str:
        """Computes H_n = SHA-256(prev_hash || Canonical_JSON(entry_payload))."""
        # Canonical JSON string with sorted keys
        canonical_str = json.dumps(entry_payload, sort_keys=True, separators=(',', ':'))
        data_to_hash = f"{prev_hash}::{canonical_str}".encode('utf-8')
        return hashlib.sha256(data_to_hash).hexdigest()

    @staticmethod
    def verify_chain_link(prev_hash: str, entry_payload: Dict[str, Any], current_hash: str) -> bool:
        """Verifies that current_hash matches the cryptographic signature of payload chained to prev_hash."""
        expected = TamperEvidentHasher.compute_entry_hash(prev_hash, entry_payload)
        return expected.lower() == current_hash.lower()
