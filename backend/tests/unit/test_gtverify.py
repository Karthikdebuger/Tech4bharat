"""Tests for the gtverify independent receipt verification tool."""

from typing import Any

from app.core.canonical import receipt_hash
from app.domain.receipt import build_canonical_receipt_dict
from app.domain.units import Bp, Mg, PaisePerG, Permille
from app.domain.valuation import calculate_valuation_band
from tools.gtverify.main import verify_receipt_data


def get_valid_sample_receipt() -> dict[str, Any]:
    band = calculate_valuation_band(
        net_mg=30800,
        nominal_permille=905,
        tolerance_permille=10,
        deduction_bp=200,
        rate_paise_per_g=1300000,
    )

    return build_canonical_receipt_dict(
        exchange_id="ex-worked-example",
        shop_id="shop-madurai-1",
        is_demo=True,
        customer_ref="hmac-ref-xyz",
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


def test_gtverify_valid_receipt() -> None:
    receipt = get_valid_sample_receipt()
    expected_hash = receipt_hash(receipt)

    is_valid, logs = verify_receipt_data(receipt, expected_hash)
    assert is_valid is True
    assert any("Mathematical verification PASSED" in log for log in logs)
    assert any("MATCH: Expected hash matches" in log for log in logs)


def test_gtverify_detects_hash_tamper() -> None:
    receipt = get_valid_sample_receipt()
    wrong_hash = "0" * 64

    is_valid, logs = verify_receipt_data(receipt, wrong_hash)
    assert is_valid is False
    assert any("HASH] MISMATCH" in log for log in logs)


def test_gtverify_detects_valuation_tamper() -> None:
    receipt = get_valid_sample_receipt()
    # Malicious jeweller tampered settlement amount by ₹1,000 (100,000 paise)
    receipt["valuation"]["settlement_paise"] -= 100_000

    is_valid, logs = verify_receipt_data(receipt)
    assert is_valid is False
    assert any("Settlement paise mismatch" in log for log in logs)


def test_gtverify_detects_witness_tamper() -> None:
    receipt = get_valid_sample_receipt()
    # Customer entered 30000 mg instead of 30800 mg
    receipt["witness"]["customer_entered_mg"] = 30000

    is_valid, logs = verify_receipt_data(receipt)
    assert is_valid is False
    assert any("FAILED weight match" in log for log in logs)
