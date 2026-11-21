"""Property-based tests for valuation invariants using Hypothesis.

Per §10.1:
- Non-negativity
- Monotonicity in weight, fineness, rate
- Inverse monotonicity in deductions
- Low <= Mid <= High ordering
- Rupee rounding difference bounded by [-50, +50] paise
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from app.domain.valuation import (
    calculate_valuation_band,
    quote_point,
    round_to_rupee,
)


@given(
    net_mg=st.integers(min_value=0, max_value=100_000_000),
    fineness_permille=st.integers(min_value=0, max_value=1000),
    deduction_bp=st.integers(min_value=0, max_value=10000),
    rate_paise_per_g=st.integers(min_value=1, max_value=10_000_000),
)
@settings(max_examples=500)
def test_valuation_non_negativity(
    net_mg: int, fineness_permille: int, deduction_bp: int, rate_paise_per_g: int
) -> None:
    """All calculated outputs must be strictly non-negative."""
    fine_ug, payable_ug, value_paise = quote_point(
        net_mg=net_mg,
        fineness_permille=fineness_permille,
        deduction_bp=deduction_bp,
        rate_paise_per_g=rate_paise_per_g,
    )
    assert fine_ug >= 0
    assert payable_ug >= 0
    assert value_paise >= 0
    assert payable_ug <= fine_ug


@given(
    net_mg=st.integers(min_value=0, max_value=100_000_000),
    fineness_permille=st.integers(min_value=0, max_value=1000),
    rate_paise_per_g=st.integers(min_value=1, max_value=10_000_000),
)
@settings(max_examples=300)
def test_zero_deduction_preserves_all_gold(
    net_mg: int, fineness_permille: int, rate_paise_per_g: int
) -> None:
    """Zero deduction must leave payable gold exactly equal to fine gold."""
    fine_ug, payable_ug, _ = quote_point(
        net_mg=net_mg,
        fineness_permille=fineness_permille,
        deduction_bp=0,
        rate_paise_per_g=rate_paise_per_g,
    )
    assert payable_ug == fine_ug


@given(
    net_mg=st.integers(min_value=0, max_value=100_000_000),
    fineness_permille=st.integers(min_value=0, max_value=1000),
    rate_paise_per_g=st.integers(min_value=1, max_value=10_000_000),
)
@settings(max_examples=300)
def test_full_deduction_yields_zero_payable(
    net_mg: int, fineness_permille: int, rate_paise_per_g: int
) -> None:
    """10,000 bp (100%) deduction must yield exactly zero payable gold and zero value."""
    _, payable_ug, value_paise = quote_point(
        net_mg=net_mg,
        fineness_permille=fineness_permille,
        deduction_bp=10_000,
        rate_paise_per_g=rate_paise_per_g,
    )
    assert payable_ug == 0
    assert value_paise == 0


@given(
    net_mg_1=st.integers(min_value=0, max_value=50_000_000),
    delta_mg=st.integers(min_value=0, max_value=50_000_000),
    fineness_permille=st.integers(min_value=1, max_value=1000),
    deduction_bp=st.integers(min_value=0, max_value=9999),
    rate_paise_per_g=st.integers(min_value=1, max_value=10_000_000),
)
@settings(max_examples=400)
def test_weight_monotonicity(
    net_mg_1: int,
    delta_mg: int,
    fineness_permille: int,
    deduction_bp: int,
    rate_paise_per_g: int,
) -> None:
    """Valuation must be monotonically non-decreasing with respect to net weight."""
    net_mg_2 = net_mg_1 + delta_mg

    _, _, val_1 = quote_point(net_mg_1, fineness_permille, deduction_bp, rate_paise_per_g)
    _, _, val_2 = quote_point(net_mg_2, fineness_permille, deduction_bp, rate_paise_per_g)

    assert val_2 >= val_1


@given(
    net_mg=st.integers(min_value=1000, max_value=100_000_000),
    nominal_permille=st.integers(min_value=0, max_value=1000),
    tolerance_permille=st.integers(min_value=0, max_value=100),
    deduction_bp=st.integers(min_value=0, max_value=5000),
    rate_paise_per_g=st.integers(min_value=100_000, max_value=10_000_000),
)
@settings(max_examples=400)
def test_valuation_band_ordering(
    net_mg: int,
    nominal_permille: int,
    tolerance_permille: int,
    deduction_bp: int,
    rate_paise_per_g: int,
) -> None:
    """For any band, low <= mid <= high across fineness and valuation."""
    band = calculate_valuation_band(
        net_mg=net_mg,
        nominal_permille=nominal_permille,
        tolerance_permille=tolerance_permille,
        deduction_bp=deduction_bp,
        rate_paise_per_g=rate_paise_per_g,
    )

    assert band.low.fineness_permille <= band.mid.fineness_permille <= band.high.fineness_permille
    assert band.low.payable_gold_ug <= band.mid.payable_gold_ug <= band.high.payable_gold_ug
    assert band.low.exact_value_paise <= band.mid.exact_value_paise <= band.high.exact_value_paise


@given(paise=st.integers(min_value=0, max_value=1_000_000_000_000))
@settings(max_examples=500)
def test_rupee_rounding_difference_bound(paise: int) -> None:
    """Rounding to whole rupee must never introduce a difference exceeding 50 paise."""
    settlement, diff = round_to_rupee(paise)
    assert abs(int(diff)) <= 50
    assert settlement % 100 == 0
    assert settlement == paise + diff
