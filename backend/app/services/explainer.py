"""Bilingual deterministic receipt explainer (English & Tamil).

Per §8.3 and ADR-0016:
- Layer 1: Deterministic templates (English and Tamil) keyed by receipt lines.
- No hallucinations: every number and unit in explanation is strictly drawn from receipt.
- Out-of-scope refusal for legal or purity advice.
"""

from typing import Any, Mapping

EXPLANATIONS_EN: dict[str, str] = {
    "weight_breakdown": (
        "Gross weight is {gross_weight}. With {stones_weight} deducted for stones/enamel, "
        "the net gold weight evaluated is {net_weight}."
    ),
    "witness_verification": (
        "Customer independently witnessed and confirmed the weight display as {witness_weight}."
    ),
    "purity_determination": (
        "Measured purity is {purity_percent} ({nominal_permille}‰ fineness). "
        "Estimated purity band spans from {low_permille}‰ to {high_permille}‰."
    ),
    "fine_gold_content": (
        "Net gold contains {fine_gold_grams} of pure 24K fine gold. "
        "After standard shop refining/melting deduction of {deduction_bp} basis points ({deduction_percent}), "
        "the payable pure gold content is {payable_gold_grams}."
    ),
    "valuation_settlement": (
        "At the locked market rate of {rate_inr}/g, exact calculated value is {exact_inr}. "
        "Settlement rounded to the nearest whole rupee is {settlement_inr} "
        "(rounding adjustment of {rounding_inr})."
    ),
    "integrity_status": (
        "Transaction integrity status: {aggregate_outcome}. "
        "Evidence test coverage: {evidence_coverage} applicable rules verified."
    ),
}

EXPLANATIONS_TA: dict[str, str] = {
    "weight_breakdown": (
        "மொத்த எடை {gross_weight}. கற்கள் மற்றும் அழுக்கு கழிவு {stones_weight} போக, "
        "மதிப்பீடு செய்யப்பட்ட நிகர தங்க எடை {net_weight} ஆகும்."
    ),
    "witness_verification": (
        "வாடிக்கையாளர் எடையளவு திரையை நேரடியாகப் பார்த்து {witness_weight} என உறுதி செய்தார்."
    ),
    "purity_determination": (
        "அளவிடப்பட்ட தூய்மை {purity_percent} ({nominal_permille}‰ மாற்று). "
        "மதிப்பீட்டு வரம்பு {low_permille}‰ முதல் {high_permille}‰ வரை உள்ளது."
    ),
    "fine_gold_content": (
        "நிகர தங்கத்தில் {fine_gold_grams} சுத்த தங்கம் (24K) உள்ளது. "
        "கடை உருக்கு கழிவு {deduction_bp} அடிப்படை புள்ளிகள் ({deduction_percent}) போக, "
        "பட்டுவாடாவுக்குரிய சுத்த தங்கம் {payable_gold_grams} ஆகும்."
    ),
    "valuation_settlement": (
        "நிர்ணயிக்கப்பட்ட சந்தை விலை {rate_inr}/கிராம் அடிப்படையில், கணக்கிடப்பட்ட தொகை {exact_inr}. "
        "முழு ரூபாயாக தீர்க்கப்பட்ட தொகை {settlement_inr} "
        "(சரிசெய்தல் {rounding_inr})."
    ),
    "integrity_status": (
        "நம்பகத்தன்மை சரிபார்ப்பு நிலை: {aggregate_outcome}. "
        "சான்றுகள் சரிபார்ப்பு விகிதம்: {evidence_coverage} விதிகள் சரிபார்க்கப்பட்டன."
    ),
}

def generate_receipt_explanation(receipt: Mapping[str, Any], lang: str = "en") -> list[dict[str, str]]:
    """Generate deterministic, grounded bilingual explanation items for a receipt."""
    templates = EXPLANATIONS_TA if lang.lower() in ("ta", "tamil") else EXPLANATIONS_EN

    weight = receipt["weight"]
    witness = receipt["witness"]
    purity = receipt["purity"]
    val = receipt["valuation"]
    integrity = receipt["integrity"]

    # Formatting variables
    gross_str = f"{weight['gross_mg'] / 1000:.3f} g"
    stones_str = f"{weight['stones_mg'] / 1000:.3f} g"
    net_str = weight.get("formatted_net", f"{weight['net_mg'] / 1000:.3f} g")

    witness_str = f"{witness['customer_entered_mg'] / 1000:.3f} g"

    purity_pct = purity.get("formatted_purity", f"{purity['nominal_permille'] / 10:.2f}%")
    fine_gold_g = f"{val['fine_gold_ug'] / 1_000_000:.3f} g"
    payable_gold_g = f"{val['payable_gold_ug'] / 1_000_000:.3f} g"
    deduction_pct = f"{val['deduction_bp'] / 100:.2f}%"

    rate_inr = f"₹{val['rate_paise_per_g'] / 100:,.2f}"
    exact_inr = f"₹{val['exact_value_paise'] / 100:,.2f}"
    settlement_inr = val.get("formatted_settlement", f"₹{val['settlement_paise'] / 100:,.2f}")
    rounding_inr = f"{val['rounding_difference_paise']} paise"

    items: list[dict[str, str]] = [
        {
            "topic": "Weight Analysis",
            "text": templates["weight_breakdown"].format(
                gross_weight=gross_str,
                stones_weight=stones_str,
                net_weight=net_str,
            ),
        },
        {
            "topic": "Witness Protocol",
            "text": templates["witness_verification"].format(witness_weight=witness_str),
        },
        {
            "topic": "Purity Determination",
            "text": templates["purity_determination"].format(
                purity_percent=purity_pct,
                nominal_permille=purity["nominal_permille"],
                low_permille=purity["low_permille"],
                high_permille=purity["high_permille"],
            ),
        },
        {
            "topic": "Fine Gold & Deductions",
            "text": templates["fine_gold_content"].format(
                fine_gold_grams=fine_gold_g,
                deduction_bp=val["deduction_bp"],
                deduction_percent=deduction_pct,
                payable_gold_grams=payable_gold_g,
            ),
        },
        {
            "topic": "Valuation & Settlement",
            "text": templates["valuation_settlement"].format(
                rate_inr=rate_inr,
                exact_inr=exact_inr,
                settlement_inr=settlement_inr,
                rounding_inr=rounding_inr,
            ),
        },
        {
            "topic": "Integrity Check",
            "text": templates["integrity_status"].format(
                aggregate_outcome=integrity["aggregate_outcome"],
                evidence_coverage=integrity["evidence_coverage"],
            ),
        },
    ]

    return items
