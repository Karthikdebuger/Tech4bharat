"""RFC 8785 JSON Canonicalization and cryptographic hashing.

Per ADR-0010 and §6.4:
- Canonical JSON serialization conforms strictly to RFC 8785 (JCS).
- Receipts contain only strings and integers (no floats, no non-deterministic dates).
- Hashing is SHA-256 over canonical UTF-8 bytes.
"""

import hashlib
from collections.abc import Mapping
from typing import Any

import rfc8785


def canonical_json_bytes(obj: Mapping[str, Any] | list[Any]) -> bytes:
    """Serialize object to RFC 8785 canonical JSON UTF-8 byte sequence.

    Deterministic across platforms, key insertion orders, and implementations.
    """
    return rfc8785.dumps(obj)


def canonical_json_str(obj: Mapping[str, Any] | list[Any]) -> str:
    """Serialize object to RFC 8785 canonical JSON decoded string."""
    return canonical_json_bytes(obj).decode("utf-8")


def compute_sha256_hex(data: bytes) -> str:
    """Compute standard lowercase hex SHA-256 digest."""
    return hashlib.sha256(data).hexdigest()


def receipt_canonical_bytes(receipt: Mapping[str, Any]) -> bytes:
    """Produce canonical byte representation for a Gold Trust receipt."""
    return canonical_json_bytes(receipt)


def receipt_hash(receipt: Mapping[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of a canonical receipt."""
    return compute_sha256_hex(receipt_canonical_bytes(receipt))


def chain_hash(prev_hash: str, canonical_event_bytes: bytes) -> str:
    """Compute chained audit hash: SHA256(prev_hash_bytes + event_bytes)."""
    return hashlib.sha256(bytes.fromhex(prev_hash) + canonical_event_bytes).hexdigest()
