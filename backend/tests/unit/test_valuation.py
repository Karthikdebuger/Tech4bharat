"""Unit tests and Golden Vector verification for pure valuation engine."""

import json
from pathlib import Path

import pytest

from app.domain.exceptions import InvalidRoundingError, UnitRangeError
from app.domain.units import (
    validate_bp,
    validate_mg,
    validate_permille,
    validate_rate,
)
from app.domain.valuation import (
    calculate_quote_point_detail,
    calculate_valuation_band,
    div_round_half_up,
    format_mg_as_grams,
    format_paise_as_inr,
    format_permille_as_percent,
)


def test_golden_vectors() -> None:
    """Validate all golden test vectors from tests/vectors/valuation.json."""
    vector_path = Path(__file__).parent.parent / "vectors" / "valuation.json"
    with open(vector_path, encoding="utf-8") as f:
        vectors = json.load(f)

    for case in vectors:
        inputs = case["inputs"]
        expected = case["expected"]

        detail = calculate_quote_point_detail(
            net_mg=inputs["net_mg"],
            fineness_permille=inputs["fineness_permille"],
            deduction_bp=inputs["deduction_bp"],
            rate_paise_per_g=inputs["rate_paise_per_g"],
        )

        assert int(detail.fine_gold_ug) == expected["fine_gold_ug"], (
            f"Failed on {case['description']}: fine_gold_ug"
        )
        assert int(detail.payable_gold_ug) == expected["payable_gold_ug"], (
            f"Failed on {case['description']}: payable_gold_ug"
        )
        assert int(detail.exact_value_paise) == expected["exact_value_paise"], (
            f"Failed on {case['description']}: exact_value_paise"
        )
        assert int(detail.settlement_paise) == expected["settlement_paise"], (
            f"Failed on {case['description']}: settlement_paise"
        )
        assert int(detail.rounding_difference_paise) == expected["rounding_difference_paise"], (
            f"Failed on {case['description']}: rounding_diff"
        )
        assert format_paise_as_inr(int(detail.exact_value_paise)) == expected["formatted_inr"]
        assert (
            format_paise_as_inr(int(detail.settlement_paise))
            == expected["formatted_settlement_inr"]
        )


def test_div_round_half_up_spec() -> None:
    """Verify half-up integer rounding rules and edge cases."""
    # Exact divisions
    assert div_round_half_up(10, 2) == 5
    assert div_round_half_up(0, 5) == 0

    # Ties: 1/2 -> 1, 3/2 -> 2
    assert div_round_half_up(1, 2) == 1
    assert div_round_half_up(3, 2) == 2
    assert div_round_half_up(5, 2) == 3

    # Less than half rounds down: 4/10 -> 0, 14/10 -> 1
    assert div_round_half_up(4, 10) == 0
    assert div_round_half_up(14, 10) == 1

    # Greater than or equal to half rounds up: 5/10 -> 1, 15/10 -> 2, 16/10 -> 2
    assert div_round_half_up(5, 10) == 1
    assert div_round_half_up(15, 10) == 2
    assert div_round_half_up(16, 10) == 2

    # Negative numerator or non-positive denominator must raise InvalidRoundingError
    with pytest.raises(InvalidRoundingError):
        div_round_half_up(-1, 2)
    with pytest.raises(InvalidRoundingError):
        div_round_half_up(5, 0)
    with pytest.raises(InvalidRoundingError):
        div_round_half_up(5, -2)


def test_valuation_band_bounds() -> None:
    """Verify that valuation bands generate correct low/mid/high points with boundary clamping."""
    band = calculate_valuation_band(
        net_mg=10000,
        nominal_permille=916,
        tolerance_permille=10,
        deduction_bp=100,
        rate_paise_per_g=1300000,
    )

    assert int(band.low.fineness_permille) == 906
    assert int(band.mid.fineness_permille) == 916
    assert int(band.high.fineness_permille) == 926

    assert band.low.payable_gold_ug < band.mid.payable_gold_ug < band.high.payable_gold_ug
    assert band.low.exact_value_paise < band.mid.exact_value_paise < band.high.exact_value_paise

    # Test clamping at 1000‰
    clamped_high = calculate_valuation_band(
        net_mg=10000,
        nominal_permille=995,
        tolerance_permille=10,
        deduction_bp=0,
        rate_paise_per_g=1300000,
    )
    assert int(clamped_high.high.fineness_permille) == 1000

    # Test clamping at 0‰
    clamped_low = calculate_valuation_band(
        net_mg=10000,
        nominal_permille=5,
        tolerance_permille=10,
        deduction_bp=0,
        rate_paise_per_g=1300000,
    )
    assert int(clamped_low.low.fineness_permille) == 0


def test_unit_validations() -> None:
    """Verify strict domain range validations."""
    with pytest.raises(UnitRangeError):
        validate_mg(-1)
    with pytest.raises(UnitRangeError):
        validate_mg(1_000_000_001)

    with pytest.raises(UnitRangeError):
        validate_permille(-1)
    with pytest.raises(UnitRangeError):
        validate_permille(1001)

    with pytest.raises(UnitRangeError):
        validate_bp(-1)
    with pytest.raises(UnitRangeError):
        validate_bp(10001)

    with pytest.raises(UnitRangeError):
        validate_rate(0)
    with pytest.raises(UnitRangeError):
        validate_rate(-500)


def test_formatters() -> None:
    """Verify exact Indian currency and physical measurement formatting without floats."""
    assert format_paise_as_inr(0) == "₹0.00"
    assert format_paise_as_inr(50) == "₹0.50"
    assert format_paise_as_inr(100) == "₹1.00"
    assert format_paise_as_inr(100000) == "₹1,000.00"
    assert format_paise_as_inr(10000000) == "₹1,00,000.00"
    assert format_paise_as_inr(35511476) == "₹3,55,114.76"
    assert format_paise_as_inr(-2500) == "-₹25.00"

    assert format_mg_as_grams(0) == "0.000 g"
    assert format_mg_as_grams(5) == "0.005 g"
    assert format_mg_as_grams(500) == "0.500 g"
    assert format_mg_as_grams(30800) == "30.800 g"

    assert format_permille_as_percent(916) == "91.60%"
    assert format_permille_as_percent(905) == "90.50%"
    assert format_permille_as_percent(1000) == "100.00%"
    assert format_permille_as_percent(0) == "0.00%"
