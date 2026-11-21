"""Strongly typed integer units and range validation for Gold Trust AI.

Per ADR-0004 and the architectural specification:
- Gross/Stone/Net Weight: Milligrams (Mg, 10^-3 g)
- Fine Gold: Micrograms (Ug, 10^-6 g)
- Fineness/Purity: Permille (parts per thousand, 0..1000)
- Deductions: Basis points (Bp, 0..10000)
- Gold Rate: Paise per gram (PaisePerG, > 0)
- Currency: Paise (Paise, 1 INR = 100 paise)

All quantities are strictly 64-bit signed integers. Floating point operations are forbidden.
"""

from typing import NewType

from app.domain.exceptions import UnitRangeError

# Strict integer newtypes
Mg = NewType("Mg", int)
Ug = NewType("Ug", int)
Permille = NewType("Permille", int)
PaisePerG = NewType("PaisePerG", int)
Bp = NewType("Bp", int)
Paise = NewType("Paise", int)

# Bounds
MAX_WEIGHT_MG: int = 1_000_000_000  # 1 tonne in milligrams
MAX_PURITY_PERMILLE: int = 1_000  # 1000‰ = 100% fine gold
MAX_DEDUCTION_BP: int = 10_000  # 10,000 bp = 100.00%
MAX_SANITY_RATE_PAISE_PER_G: int = 100_000_000  # ₹1,000,000 / g sanity limit


def validate_mg(value: int, field_name: str = "weight_mg") -> Mg:
    """Validate and construct an Mg (milligram) integer value."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise UnitRangeError(
            f"{field_name} must be an integer, got {type(value).__name__}", field_name, 0
        )
    if value < 0 or value > MAX_WEIGHT_MG:
        raise UnitRangeError(
            f"{field_name} must be between 0 and {MAX_WEIGHT_MG} mg (inclusive), got {value}",
            field_name,
            value,
        )
    return Mg(value)


def validate_ug(value: int, field_name: str = "fine_gold_ug") -> Ug:
    """Validate and construct an Ug (microgram) integer value."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise UnitRangeError(
            f"{field_name} must be an integer, got {type(value).__name__}", field_name, 0
        )
    if value < 0:
        raise UnitRangeError(f"{field_name} must be non-negative, got {value}", field_name, value)
    return Ug(value)


def validate_permille(value: int, field_name: str = "fineness_permille") -> Permille:
    """Validate and construct a Permille (parts per thousand) integer value."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise UnitRangeError(
            f"{field_name} must be an integer, got {type(value).__name__}", field_name, 0
        )
    if value < 0 or value > MAX_PURITY_PERMILLE:
        raise UnitRangeError(
            f"{field_name} must be between 0 and {MAX_PURITY_PERMILLE} (inclusive), got {value}",
            field_name,
            value,
        )
    return Permille(value)


def validate_bp(value: int, field_name: str = "deduction_bp") -> Bp:
    """Validate and construct a Bp (basis points) integer value."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise UnitRangeError(
            f"{field_name} must be an integer, got {type(value).__name__}", field_name, 0
        )
    if value < 0 or value > MAX_DEDUCTION_BP:
        raise UnitRangeError(
            f"{field_name} must be between 0 and {MAX_DEDUCTION_BP} bp (inclusive), got {value}",
            field_name,
            value,
        )
    return Bp(value)


def validate_rate(value: int, field_name: str = "rate_paise_per_g") -> PaisePerG:
    """Validate and construct a PaisePerG integer value."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise UnitRangeError(
            f"{field_name} must be an integer, got {type(value).__name__}", field_name, 0
        )
    if value <= 0 or value > MAX_SANITY_RATE_PAISE_PER_G:
        msg = f"{field_name} must be > 0 and <= {MAX_SANITY_RATE_PAISE_PER_G}, got {value}"
        raise UnitRangeError(msg, field_name, value)
    return PaisePerG(value)


def validate_paise(value: int, field_name: str = "amount_paise") -> Paise:
    """Validate and construct a Paise integer value."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise UnitRangeError(
            f"{field_name} must be an integer, got {type(value).__name__}", field_name, 0
        )
    # Check 64-bit signed integer bounds
    if value < -9_223_372_036_854_775_808 or value > 9_223_372_036_854_775_807:
        raise UnitRangeError(
            f"{field_name} exceeds 64-bit signed integer bounds", field_name, value
        )
    return Paise(value)
