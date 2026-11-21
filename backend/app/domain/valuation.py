"""Pure domain valuation engine for Gold Trust AI.

Per ADR-0004 and the architectural specification (§6.1):
- All calculations operate strictly on integers.
- Exact unit relationships:
    net_mg * fineness_permille = fine_gold_ug  (since mg * 10^-3 = 10^-3 mg = 1 µg)
- Rounding: round half-up integer arithmetic: (2 * n + d) // (2 * d)
- Rounding differences are isolated into RoundingDifference in the financial ledger,
  never into the physical gold ledger.
"""

from dataclasses import dataclass
from typing import Final

from app.domain.exceptions import InvalidRoundingError
from app.domain.units import (
    Bp,
    Mg,
    Paise,
    PaisePerG,
    Permille,
    Ug,
    validate_bp,
    validate_mg,
    validate_paise,
    validate_permille,
    validate_rate,
    validate_ug,
)

BP_DENOMINATOR: Final[int] = 10_000
GRAM_TO_UG_FACTOR: Final[int] = 1_000_000
PAISE_PER_RUPEE: Final[int] = 100


def div_round_half_up(n: int, d: int) -> int:
    """Perform integer division of n / d with half-up rounding (ties away from zero).

    Args:
        n: Non-negative numerator.
        d: Strictly positive denominator.

    Returns:
        Integer result rounded to the nearest integer, ties rounded up.
    """
    if n < 0 or d <= 0:
        raise InvalidRoundingError(f"div_round_half_up requires n >= 0 and d > 0, got n={n}, d={d}")
    return (2 * n + d) // (2 * d)


def quote_point(
    net_mg: Mg | int,
    fineness_permille: Permille | int,
    deduction_bp: Bp | int,
    rate_paise_per_g: PaisePerG | int,
) -> tuple[Ug, Ug, Paise]:
    """Calculate fine gold content, payable gold content, and monetary valuation for a single point.

    Formula:
      fine_ug = net_mg * fineness_permille
      payable_ug = div_round_half_up(fine_ug * (10_000 - deduction_bp), 10_000)
      value_paise = div_round_half_up(payable_ug * rate_paise_per_g, 1_000_000)

    Returns:
      (fine_gold_ug, payable_gold_ug, value_paise)
    """
    validated_net_mg = validate_mg(int(net_mg))
    validated_permille = validate_permille(int(fineness_permille))
    validated_bp = validate_bp(int(deduction_bp))
    validated_rate = validate_rate(int(rate_paise_per_g))

    # Exact product: mg * (parts per thousand) = micrograms (µg)
    fine_ug_raw = int(validated_net_mg) * int(validated_permille)
    fine_ug = validate_ug(fine_ug_raw)

    # Net payable gold after deducting melting/refining margin
    retained_factor = BP_DENOMINATOR - int(validated_bp)
    payable_ug_raw = div_round_half_up(fine_ug_raw * retained_factor, BP_DENOMINATOR)
    payable_ug = validate_ug(payable_ug_raw)

    # Valuation in paise: (payable_ug * paise_per_g) / 1_000_000 µg/g
    value_paise_raw = div_round_half_up(int(payable_ug) * int(validated_rate), GRAM_TO_UG_FACTOR)
    value_paise = validate_paise(value_paise_raw)

    return fine_ug, payable_ug, value_paise


def round_to_rupee(paise: Paise | int) -> tuple[Paise, Paise]:
    """Round a monetary amount in paise to the nearest whole rupee (100 paise).

    Returns:
        tuple of (settlement_paise, rounding_difference_paise)
        where rounding_difference_paise = settlement_paise - paise.
    """
    p = int(paise)
    if p < 0:
        # For negative paise (e.g. adjustments), symmetric rounding
        abs_p = abs(p)
        rounded_abs = div_round_half_up(abs_p, PAISE_PER_RUPEE) * PAISE_PER_RUPEE
        settlement = -rounded_abs
    else:
        settlement = div_round_half_up(p, PAISE_PER_RUPEE) * PAISE_PER_RUPEE

    diff = settlement - p
    return validate_paise(settlement), validate_paise(diff)


@dataclass(frozen=True, slots=True)
class ValuationQuotePoint:
    """Full detail for an evaluated purity point."""

    fineness_permille: Permille
    fine_gold_ug: Ug
    retained_deduction_ug: Ug
    payable_gold_ug: Ug
    exact_value_paise: Paise
    settlement_paise: Paise
    rounding_difference_paise: Paise


@dataclass(frozen=True, slots=True)
class ValuationBand:
    """Three-point valuation band (low, mid, high) with named settlement target."""

    net_weight_mg: Mg
    rate_paise_per_g: PaisePerG
    deduction_bp: Bp
    tolerance_permille: Permille
    low: ValuationQuotePoint
    mid: ValuationQuotePoint
    high: ValuationQuotePoint
    settlement_target: ValuationQuotePoint


def calculate_quote_point_detail(
    net_mg: Mg | int,
    fineness_permille: Permille | int,
    deduction_bp: Bp | int,
    rate_paise_per_g: PaisePerG | int,
) -> ValuationQuotePoint:
    """Compute detailed quote point including retained deduction and rupee settlement."""
    fine_ug, payable_ug, value_paise = quote_point(
        net_mg=net_mg,
        fineness_permille=fineness_permille,
        deduction_bp=deduction_bp,
        rate_paise_per_g=rate_paise_per_g,
    )
    settlement_paise, rounding_diff = round_to_rupee(value_paise)
    retained_ug = validate_ug(int(fine_ug) - int(payable_ug))

    return ValuationQuotePoint(
        fineness_permille=validate_permille(int(fineness_permille)),
        fine_gold_ug=fine_ug,
        retained_deduction_ug=retained_ug,
        payable_gold_ug=payable_ug,
        exact_value_paise=value_paise,
        settlement_paise=settlement_paise,
        rounding_difference_paise=rounding_diff,
    )


def calculate_valuation_band(
    net_mg: Mg | int,
    nominal_permille: Permille | int,
    tolerance_permille: Permille | int,
    deduction_bp: Bp | int,
    rate_paise_per_g: PaisePerG | int,
) -> ValuationBand:
    """Construct full low / mid / high valuation band clamped to [0, 1000] permille.

    Settlement target defaults to the nominal mid-point.
    """
    v_net = validate_mg(int(net_mg))
    v_nom = validate_permille(int(nominal_permille))
    v_tol = validate_permille(int(tolerance_permille))
    v_bp = validate_bp(int(deduction_bp))
    v_rate = validate_rate(int(rate_paise_per_g))

    low_permille = validate_permille(max(0, int(v_nom) - int(v_tol)))
    high_permille = validate_permille(min(1_000, int(v_nom) + int(v_tol)))

    low_pt = calculate_quote_point_detail(v_net, low_permille, v_bp, v_rate)
    mid_pt = calculate_quote_point_detail(v_net, v_nom, v_bp, v_rate)
    high_pt = calculate_quote_point_detail(v_net, high_permille, v_bp, v_rate)

    return ValuationBand(
        net_weight_mg=v_net,
        rate_paise_per_g=v_rate,
        deduction_bp=v_bp,
        tolerance_permille=v_tol,
        low=low_pt,
        mid=mid_pt,
        high=high_pt,
        settlement_target=mid_pt,
    )


def format_paise_as_inr(paise: int) -> str:
    """Format paise into standard Indian numbering system (e.g. ₹3,55,114.76).

    Pure string formatting, strictly zero floats.
    """
    is_negative = paise < 0
    abs_paise = abs(paise)
    rupees = abs_paise // 100
    sub_paise = abs_paise % 100

    rupee_str = str(rupees)
    if len(rupee_str) <= 3:
        formatted_rupees = rupee_str
    else:
        # Indian format: last 3 digits, then groups of 2 digits
        last_three = rupee_str[-3:]
        remaining = rupee_str[:-3]
        groups: list[str] = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        formatted_rupees = ",".join(reversed(groups)) + "," + last_three

    sign = "-" if is_negative else ""
    return f"{sign}₹{formatted_rupees}.{sub_paise:02d}"


def format_mg_as_grams(mg: int) -> str:
    """Format milligrams into grams with 3 decimal places (e.g. 30800 -> 30.800 g).

    Pure string formatting without floats.
    """
    is_negative = mg < 0
    abs_mg = abs(mg)
    whole_g = abs_mg // 1000
    fractional = abs_mg % 1000
    sign = "-" if is_negative else ""
    return f"{sign}{whole_g}.{fractional:03d} g"


def format_permille_as_percent(permille: int) -> str:
    """Format permille into percentage string (e.g. 916 -> 91.60%, 905 -> 90.50%)."""
    whole = permille // 10
    decimal = (permille % 10) * 10
    return f"{whole}.{decimal:02d}%"
