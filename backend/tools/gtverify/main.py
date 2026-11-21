"""gtverify - Independent CLI verifier for Gold Trust AI receipts.

Per §6.4:
Given a receipt JSON, gtverify:
1. Recomputes RFC 8785 canonical hash.
2. Re-derives valuation from embedded inputs.
3. Verifies weight witness and arithmetic integrity.
4. Prints an immutable cryptographic audit report.

Usage:
    python -m tools.gtverify.main <receipt.json> [--expected-hash <sha256>]
"""

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.core.canonical import receipt_hash
from app.domain.valuation import (
    calculate_quote_point_detail,
    format_mg_as_grams,
    format_paise_as_inr,
    format_permille_as_percent,
)


def verify_receipt_data(
    receipt: Mapping[str, Any],
    expected_hash: str | None = None,
) -> tuple[bool, list[str]]:
    """Perform independent verification on a receipt object.

    Returns:
        (is_valid, list of audit log messages)
    """
    logs: list[str] = []
    is_valid = True

    # 1. Canonical Hash Recomputation
    computed_hash = receipt_hash(receipt)
    logs.append(f"[HASH] Recomputed RFC 8785 canonical SHA-256: {computed_hash}")

    if expected_hash:
        if computed_hash.lower() == expected_hash.lower():
            logs.append("[HASH] MATCH: Expected hash matches computed hash.")
        else:
            logs.append(f"[HASH] MISMATCH: Expected {expected_hash} but got {computed_hash}")
            is_valid = False

    # 2. Demo Environment Detection
    is_demo = receipt.get("is_demo", False)
    logs.append(f"[ENV] is_demo = {is_demo} ({'DEMO RECORD' if is_demo else 'PRODUCTION RECORD'})")

    # 3. Independent Valuation Re-derivation
    try:
        weight_obj = receipt["weight"]
        purity_obj = receipt["purity"]
        val_obj = receipt["valuation"]

        net_mg = weight_obj["net_mg"]
        gross_mg = weight_obj["gross_mg"]
        stones_mg = weight_obj["stones_mg"]
        nominal_permille = purity_obj["nominal_permille"]
        deduction_bp = val_obj["deduction_bp"]
        rate_paise_per_g = val_obj["rate_paise_per_g"]

        # Net weight check
        if net_mg != (gross_mg - stones_mg):
            logs.append(
                f"[WEIGHT] Net weight arithmetic error: {gross_mg} - {stones_mg} != {net_mg}"
            )
            is_valid = False
        else:
            msg = (
                f"[WEIGHT] Validated: {format_mg_as_grams(net_mg)} net "
                f"({gross_mg} gross, {stones_mg} stones)"
            )
            logs.append(msg)

        # Re-derive exact valuation
        rederived = calculate_quote_point_detail(
            net_mg=net_mg,
            fineness_permille=nominal_permille,
            deduction_bp=deduction_bp,
            rate_paise_per_g=rate_paise_per_g,
        )

        # Check fine gold
        if int(rederived.fine_gold_ug) != val_obj["fine_gold_ug"]:
            msg = (
                f"[VALUATION] Fine gold mismatch: "
                f"{val_obj['fine_gold_ug']} vs {rederived.fine_gold_ug}"
            )
            logs.append(msg)
            is_valid = False

        # Check payable gold
        if int(rederived.payable_gold_ug) != val_obj["payable_gold_ug"]:
            msg = (
                f"[VALUATION] Payable gold mismatch: "
                f"{val_obj['payable_gold_ug']} vs {rederived.payable_gold_ug}"
            )
            logs.append(msg)
            is_valid = False

        # Check exact value paise
        if int(rederived.exact_value_paise) != val_obj["exact_value_paise"]:
            msg = (
                f"[VALUATION] Exact value mismatch: "
                f"{val_obj['exact_value_paise']} vs {rederived.exact_value_paise}"
            )
            logs.append(msg)
            is_valid = False

        # Check settlement paise
        if int(rederived.settlement_paise) != val_obj["settlement_paise"]:
            msg = (
                f"[VALUATION] Settlement paise mismatch: "
                f"{val_obj['settlement_paise']} vs {rederived.settlement_paise}"
            )
            logs.append(msg)
            is_valid = False

        # Check rounding difference
        if int(rederived.rounding_difference_paise) != val_obj["rounding_difference_paise"]:
            msg = (
                f"[VALUATION] Rounding diff mismatch: "
                f"{val_obj['rounding_difference_paise']} vs {rederived.rounding_difference_paise}"
            )
            logs.append(msg)
            is_valid = False

        if is_valid:
            logs.append(
                f"[VALUATION] Mathematical verification PASSED: "
                f"{format_permille_as_percent(nominal_permille)} @ "
                f"{format_paise_as_inr(rate_paise_per_g)}/g = "
                f"{format_paise_as_inr(int(rederived.settlement_paise))}"
            )

    except KeyError as e:
        logs.append(f"[SCHEMA] Missing required receipt field: {e}")
        is_valid = False

    # 4. Weight Witness Verification
    witness_obj = receipt.get("witness")
    if witness_obj:
        customer_entered = witness_obj.get("customer_entered_mg")
        gross = receipt["weight"]["gross_mg"]
        mode = witness_obj.get("mode")
        if customer_entered == gross:
            logs.append(f"[WITNESS] Verified blind weight match ({mode}): {customer_entered} mg")
        else:
            logs.append(
                f"[WITNESS] FAILED weight match: customer={customer_entered} mg vs scale={gross} mg"
            )
            is_valid = False

    return is_valid, logs


def main() -> None:
    parser = argparse.ArgumentParser(description="Gold Trust AI Independent Receipt Verifier")
    parser.add_argument("receipt_file", type=Path, help="Path to receipt JSON file")
    parser.add_argument("--expected-hash", type=str, default=None, help="Expected SHA-256 hash")
    parser.add_argument("--json", action="store_true", help="Output verification report as JSON")
    args = parser.parse_args()

    if not args.receipt_file.is_file():
        print(f"Error: file not found: {args.receipt_file}", file=sys.stderr)
        sys.exit(2)

    with open(args.receipt_file, encoding="utf-8") as f:
        receipt_data = json.load(f)

    is_valid, logs = verify_receipt_data(receipt_data, args.expected_hash)

    if args.json:
        report = {
            "valid": is_valid,
            "hash": receipt_hash(receipt_data),
            "logs": logs,
        }
        print(json.dumps(report, indent=2))
    else:
        print("=" * 60)
        print("GOLD TRUST AI — INDEPENDENT RECEIPT VERIFICATION REPORT")
        print("=" * 60)
        for log in logs:
            print(log)
        print("=" * 60)
        if is_valid:
            print("STATUS: VERIFIED (PASS)")
        else:
            print("STATUS: FAILED VERIFICATION (TAMPER DETECTED / MISMATCH)")
        print("=" * 60)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
