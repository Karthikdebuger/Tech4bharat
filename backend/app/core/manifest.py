"""Ed25519 asymmetric manifest signing and cryptographic verification.

Per §6.4:
A hash chain per shop links events; a nightly job verifies the chain and writes
a daily manifest (last hash, event count) signed with an Ed25519 private key
held outside the database.
"""

from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from app.core.canonical import canonical_json_bytes, compute_sha256_hex


@dataclass(frozen=True, slots=True)
class DailyManifest:
    shop_id: str
    date_iso: str
    seq_start: int
    seq_end: int
    event_count: int
    last_event_hash: str
    manifest_hash: str
    signature_hex: str


def generate_signing_keypair() -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """Generate a new Ed25519 keypair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def sign_manifest(
    private_key: ed25519.Ed25519PrivateKey,
    shop_id: str,
    date_iso: str,
    seq_start: int,
    seq_end: int,
    event_count: int,
    last_event_hash: str,
) -> DailyManifest:
    """Create and sign an immutable daily audit manifest."""
    payload: dict[str, Any] = {
        "shop_id": shop_id,
        "date_iso": date_iso,
        "seq_start": seq_start,
        "seq_end": seq_end,
        "event_count": event_count,
        "last_event_hash": last_event_hash,
    }
    canonical_bytes = canonical_json_bytes(payload)
    manifest_hash = compute_sha256_hex(canonical_bytes)
    signature = private_key.sign(canonical_bytes)

    return DailyManifest(
        shop_id=shop_id,
        date_iso=date_iso,
        seq_start=seq_start,
        seq_end=seq_end,
        event_count=event_count,
        last_event_hash=last_event_hash,
        manifest_hash=manifest_hash,
        signature_hex=signature.hex(),
    )


def verify_manifest(manifest: DailyManifest, public_key: ed25519.Ed25519PublicKey) -> bool:
    """Verify an Ed25519 signature over a daily audit manifest."""
    payload: dict[str, Any] = {
        "shop_id": manifest.shop_id,
        "date_iso": manifest.date_iso,
        "seq_start": manifest.seq_start,
        "seq_end": manifest.seq_end,
        "event_count": manifest.event_count,
        "last_event_hash": manifest.last_event_hash,
    }
    canonical_bytes = canonical_json_bytes(payload)
    expected_hash = compute_sha256_hex(canonical_bytes)
    if expected_hash != manifest.manifest_hash:
        return False

    try:
        public_key.verify(bytes.fromhex(manifest.signature_hex), canonical_bytes)
        return True
    except (InvalidSignature, ValueError):
        return False
