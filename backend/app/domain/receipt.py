"""Canonical Gold Trust AI receipt structure and generator.

Per §6.4:
- All values are strictly integers, strings, booleans, or lists/mappings of them.
- No floats, no non-deterministic timestamps.
- is_demo flag is hashed directly into the receipt, preventing demo receipts
  from verifying as valid production records.
- Names and phone numbers stay in private vault; only pseudonymous customer_ref
  is recorded on the receipt.
"""

from typing import Any

from app.core.canonical import receipt_canonical_bytes, receipt_hash
from app.domain.units import Bp, Mg, PaisePerG, Permille
from app.domain.valuation import (
    ValuationBand,
    format_mg_as_grams,
    format_paise_as_inr,
    format_permille_as_percent,
)


def build_canonical_receipt_dict(
    exchange_id: str,
    shop_id: str,
    is_demo: bool,
    customer_ref: str,
    timestamp_iso: str,
    gross_mg: Mg,
    stones_mg: Mg,
    net_mg: Mg,
    witness_customer_mg: Mg,
    witness_mode: str,
    nominal_permille: Permille,
    tolerance_permille: Permille,
    deduction_bp: Bp,
    rate_paise_per_g: PaisePerG,
    valuation_band: ValuationBand,
    rule_aggregate: str,
    coverage_ratio: str,
    attested_rules: list[str],
    supersedes_receipt_hash: str | None = None,
) -> dict[str, Any]:
    """Construct deterministic dictionary representation of an exchange receipt."""
    target = valuation_band.settlement_target

    receipt: dict[str, Any] = {
        "receipt_version": 1,
        "is_demo": bool(is_demo),
        "exchange_id": exchange_id,
        "shop_id": shop_id,
        "customer_ref": customer_ref,
        "timestamp_utc": timestamp_iso,
        "supersedes_receipt_hash": supersedes_receipt_hash,
        "weight": {
            "gross_mg": int(gross_mg),
            "stones_mg": int(stones_mg),
            "net_mg": int(net_mg),
            "formatted_net": format_mg_as_grams(int(net_mg)),
        },
        "witness": {
            "customer_entered_mg": int(witness_customer_mg),
            "mode": witness_mode,
            "matched": int(witness_customer_mg) == int(gross_mg),
        },
        "purity": {
            "nominal_permille": int(nominal_permille),
            "tolerance_permille": int(tolerance_permille),
            "low_permille": int(valuation_band.low.fineness_permille),
            "high_permille": int(valuation_band.high.fineness_permille),
            "formatted_purity": format_permille_as_percent(int(nominal_permille)),
        },
        "valuation": {
            "rate_paise_per_g": int(rate_paise_per_g),
            "deduction_bp": int(deduction_bp),
            "fine_gold_ug": int(target.fine_gold_ug),
            "payable_gold_ug": int(target.payable_gold_ug),
            "retained_gold_ug": int(target.retained_deduction_ug),
            "exact_value_paise": int(target.exact_value_paise),
            "settlement_paise": int(target.settlement_paise),
            "rounding_difference_paise": int(target.rounding_difference_paise),
            "formatted_settlement": format_paise_as_inr(int(target.settlement_paise)),
        },
        "integrity": {
            "aggregate_outcome": rule_aggregate,
            "evidence_coverage": coverage_ratio,
            "attested_rules": sorted(attested_rules),
        },
    }
    return receipt


def create_finalized_receipt(
    receipt_dict: dict[str, Any],
) -> tuple[dict[str, Any], str, bytes]:
    """Calculate canonical hash and bytes for a completed receipt."""
    r_bytes = receipt_canonical_bytes(receipt_dict)
    r_hash = receipt_hash(receipt_dict)
    return receipt_dict, r_hash, r_bytes
