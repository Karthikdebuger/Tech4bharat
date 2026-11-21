"""Tests for dual-entry balanced ledger plans."""

import json
from pathlib import Path

from app.domain.ledger_plan import plan_postings
from app.domain.receipt import build_canonical_receipt_dict
from app.domain.units import Bp, Mg, PaisePerG, Permille
from app.domain.valuation import calculate_valuation_band


def test_ledger_plan_worked_example() -> None:
    """Validate postings for the specification worked example.

    Intake: 27,874,000 µg fine gold -> 27,316,520 µg customer + 557,480 µg retained.
    Money: Purchases 35,511,476p + Rounding 24p = 35,511,500p Payable.
    """
    band = calculate_valuation_band(
        net_mg=30800,
        nominal_permille=905,
        tolerance_permille=10,
        deduction_bp=200,
        rate_paise_per_g=1300000,
    )

    receipt = build_canonical_receipt_dict(
        exchange_id="ex-worked-example",
        shop_id="shop-1",
        is_demo=False,
        customer_ref="cust-ref-1",
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

    plan = plan_postings(receipt, payment_method="Bank")

    # Verify Gold Intake
    gold_lines = {line.account: (line.side, int(line.amount_ug)) for line in plan.gold_intake.lines}
    assert gold_lines["Stock:OldGold"] == ("D", 27_874_000)
    assert gold_lines["Customer:GoldPayable"] == ("C", 27_316_520)
    assert gold_lines["Retained:Deduction"] == ("C", 557_480)

    # Verify Gold Discharge
    dis_lines = {
        line.account: (line.side, int(line.amount_ug)) for line in plan.gold_discharge.lines
    }
    assert dis_lines["Customer:GoldPayable"] == ("D", 27_316_520)
    assert dis_lines["Settlement:GoldToCash"] == ("C", 27_316_520)

    # Verify Money Payable
    money_lines = {
        line.account: (line.side, int(line.amount_paise)) for line in plan.money_payable.lines
    }
    assert money_lines["Purchases:OldGold"] == ("D", 35_511_476)
    assert money_lines["RoundingDifference"] == ("D", 24)
    assert money_lines["Customer:CashPayable"] == ("C", 35_511_500)

    # Verify Money Discharge
    payout_lines = {
        line.account: (line.side, int(line.amount_paise)) for line in plan.money_payout.lines
    }
    assert payout_lines["Customer:CashPayable"] == ("D", 35_511_500)
    assert payout_lines["Bank"] == ("C", 35_511_500)


def test_ledger_plan_across_all_golden_vectors() -> None:
    """Verify that posting plans balance on every vector in tests/vectors/valuation.json."""
    vector_path = Path(__file__).parent.parent / "vectors" / "valuation.json"
    with open(vector_path, encoding="utf-8") as f:
        vectors = json.load(f)

    for case in vectors:
        inputs = case["inputs"]
        band = calculate_valuation_band(
            net_mg=inputs["net_mg"],
            nominal_permille=inputs["fineness_permille"],
            tolerance_permille=5,
            deduction_bp=inputs["deduction_bp"],
            rate_paise_per_g=inputs["rate_paise_per_g"],
        )
        receipt = build_canonical_receipt_dict(
            exchange_id="ex-vector",
            shop_id="shop-1",
            is_demo=False,
            customer_ref="cust-ref-1",
            timestamp_iso="2026-11-20T10:00:00Z",
            gross_mg=Mg(inputs["net_mg"]),
            stones_mg=Mg(0),
            net_mg=Mg(inputs["net_mg"]),
            witness_customer_mg=Mg(inputs["net_mg"]),
            witness_mode="OWN_DEVICE",
            nominal_permille=Permille(inputs["fineness_permille"]),
            tolerance_permille=Permille(5),
            deduction_bp=Bp(inputs["deduction_bp"]),
            rate_paise_per_g=PaisePerG(inputs["rate_paise_per_g"]),
            valuation_band=band,
            rule_aggregate="CONSISTENT",
            coverage_ratio="11/11",
            attested_rules=[],
        )

        # Must not raise LedgerBalanceError
        plan = plan_postings(receipt, payment_method="Cash")
        assert plan.gold_intake is not None
        assert plan.money_payable is not None
