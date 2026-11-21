"""Tests for RFC 8785 canonical JSON, receipt hashing, and manifest signing."""

import json

from app.core.canonical import (
    canonical_json_bytes,
    chain_hash,
    compute_sha256_hex,
    receipt_hash,
)
from app.core.manifest import (
    generate_signing_keypair,
    sign_manifest,
    verify_manifest,
)
from app.domain.receipt import build_canonical_receipt_dict, create_finalized_receipt
from app.domain.units import Bp, Mg, PaisePerG, Permille
from app.domain.valuation import calculate_valuation_band


def test_canonical_json_key_order_invariance() -> None:
    """Ensure RFC 8785 guarantees identical bytes regardless of key insertion order."""
    dict_a = {"z": 100, "a": "hello", "m": [3, 2, 1], "sub": {"k2": 2, "k1": 1}}
    dict_b = {"sub": {"k1": 1, "k2": 2}, "m": [3, 2, 1], "a": "hello", "z": 100}

    bytes_a = canonical_json_bytes(dict_a)
    bytes_b = canonical_json_bytes(dict_b)

    assert bytes_a == bytes_b
    assert compute_sha256_hex(bytes_a) == compute_sha256_hex(bytes_b)


def test_hash_chain_tamper_sensitivity() -> None:
    """A single bit flip in any audit event must break the hash chain."""
    genesis_hash = "0" * 64
    event_1 = canonical_json_bytes({"action": "INTAKE", "gross_mg": 30800})
    event_2 = canonical_json_bytes({"action": "EVIDENCE", "purity": 905})

    hash_1 = chain_hash(genesis_hash, event_1)
    hash_2 = chain_hash(hash_1, event_2)

    # Tampered event 1
    tampered_event_1 = canonical_json_bytes({"action": "INTAKE", "gross_mg": 30799})
    tampered_hash_1 = chain_hash(genesis_hash, tampered_event_1)
    tampered_hash_2 = chain_hash(tampered_hash_1, event_2)

    assert tampered_hash_1 != hash_1
    assert tampered_hash_2 != hash_2


def test_manifest_ed25519_signature() -> None:
    """Verify Ed25519 signing and verification of daily audit manifests."""
    priv_key, pub_key = generate_signing_keypair()

    manifest = sign_manifest(
        private_key=priv_key,
        shop_id="shop-123",
        date_iso="2026-11-20",
        seq_start=1,
        seq_end=150,
        event_count=150,
        last_event_hash="f" * 64,
    )

    # Valid verification
    assert verify_manifest(manifest, pub_key) is True

    # Tamper with event count
    tampered_manifest = type(manifest)(
        shop_id=manifest.shop_id,
        date_iso=manifest.date_iso,
        seq_start=manifest.seq_start,
        seq_end=manifest.seq_end,
        event_count=151,  # Altered
        last_event_hash=manifest.last_event_hash,
        manifest_hash=manifest.manifest_hash,
        signature_hex=manifest.signature_hex,
    )
    assert verify_manifest(tampered_manifest, pub_key) is False


def test_receipt_tamper_detection() -> None:
    """Verify that any modification of receipt values breaks the canonical hash."""
    band = calculate_valuation_band(
        net_mg=30800,
        nominal_permille=905,
        tolerance_permille=10,
        deduction_bp=200,
        rate_paise_per_g=1300000,
    )

    receipt_dict = build_canonical_receipt_dict(
        exchange_id="ex-1",
        shop_id="shop-1",
        is_demo=False,
        customer_ref="cust-ref-abc",
        timestamp_iso="2026-11-20T10:00:00Z",
        gross_mg=Mg(30800),
        stones_mg=Mg(0),
        net_mg=Mg(30800),
        witness_customer_mg=Mg(30800),
        witness_mode="OWN_DEVICE",
        nominal_permille=Permille(905),
        tolerance_permille=Permille(10),
        deduction_bp=Bp(200),
        rate_paise_per_g=PaisePerG(1300000),
        valuation_band=band,
        rule_aggregate="CONSISTENT",
        coverage_ratio="11/11",
        attested_rules=[],
    )

    _, orig_hash, _ = create_finalized_receipt(receipt_dict)

    # 1. Tamper with settlement paise
    tampered_dict = json.loads(json.dumps(receipt_dict))
    tampered_dict["valuation"]["settlement_paise"] += 100
    assert receipt_hash(tampered_dict) != orig_hash

    # 2. Tamper with is_demo
    tampered_demo = json.loads(json.dumps(receipt_dict))
    tampered_demo["is_demo"] = True
    assert receipt_hash(tampered_demo) != orig_hash
