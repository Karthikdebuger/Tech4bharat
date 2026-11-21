"""Differential testing for valuation engine against exact Fraction rational arithmetic.

Per §6.1 of the architecture specification:
An independent implementation using fractions.Fraction and explicit rounding
must equal quote_point on random inputs.
"""

import math
from fractions import Fraction

from hypothesis import given, settings
from hypothesis import strategies as st

from app.domain.valuation import (
    div_round_half_up,
    quote_point,
)


def fraction_reference_div_round_half_up(n: int, d: int) -> int:
    """Exact rational reference for half-up rounding."""
    frac = Fraction(n, d)
    return math.floor(frac + Fraction(1, 2))


def fraction_reference_quote_point(
    net_mg: int,
    fineness_permille: int,
    deduction_bp: int,
    rate_paise_per_g: int,
) -> tuple[int, int, int]:
    """Exact rational reference calculation."""
    fine_ug = net_mg * fineness_permille
    retained_factor = Fraction(10_000 - deduction_bp, 10_000)
    payable_ug_frac = Fraction(fine_ug) * retained_factor
    payable_ug = math.floor(payable_ug_frac + Fraction(1, 2))

    value_paise_frac = Fraction(payable_ug * rate_paise_per_g, 1_000_000)
    value_paise = math.floor(value_paise_frac + Fraction(1, 2))

    return fine_ug, payable_ug, value_paise


@given(
    n=st.integers(min_value=0, max_value=10_000_000_000),
    d=st.integers(min_value=1, max_value=10_000_000),
)
@settings(max_examples=1000)
def test_div_round_half_up_matches_fraction_reference(n: int, d: int) -> None:
    """Verify that integer div_round_half_up matches mathematical Fraction floor(n/d + 1/2)."""
    expected = fraction_reference_div_round_half_up(n, d)
    actual = div_round_half_up(n, d)
    assert actual == expected


@given(
    net_mg=st.integers(min_value=0, max_value=1_000_000_000),
    fineness_permille=st.integers(min_value=0, max_value=1000),
    deduction_bp=st.integers(min_value=0, max_value=10000),
    rate_paise_per_g=st.integers(min_value=1, max_value=10_000_000),
)
@settings(max_examples=1000)
def test_quote_point_matches_fraction_reference(
    net_mg: int,
    fineness_permille: int,
    deduction_bp: int,
    rate_paise_per_g: int,
) -> None:
    """Verify that integer quote_point produces identical results to exact Fraction arithmetic."""
    exp_fine, exp_payable, exp_val = fraction_reference_quote_point(
        net_mg=net_mg,
        fineness_permille=fineness_permille,
        deduction_bp=deduction_bp,
        rate_paise_per_g=rate_paise_per_g,
    )

    act_fine, act_payable, act_val = quote_point(
        net_mg=net_mg,
        fineness_permille=fineness_permille,
        deduction_bp=deduction_bp,
        rate_paise_per_g=rate_paise_per_g,
    )

    assert int(act_fine) == exp_fine
    assert int(act_payable) == exp_payable
    assert int(act_val) == exp_val
