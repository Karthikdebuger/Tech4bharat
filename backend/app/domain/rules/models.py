"""Rule engine models and evidence bundles for Gold Trust AI."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from app.domain.units import Bp, Mg, Permille, Ug


class Outcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ATTESTED = "ATTESTED"


@dataclass(frozen=True, slots=True)
class RuleResult:
    """Deterministic result of evaluating an integrity rule."""

    rule_id: str
    rule_version: int
    outcome: Outcome
    blocking: bool
    evidence_refs: tuple[str, ...]
    message_key: str
    params: Mapping[str, str | int]


@dataclass(frozen=True, slots=True)
class ScaleReading:
    reading_id: str
    gross_mg: Mg
    stones_mg: Mg
    net_mg: Mg
    calibration_valid: bool


@dataclass(frozen=True, slots=True)
class CustomerWitnessReading:
    customer_mg: Mg
    mode: str  # "OWN_DEVICE" | "ASSISTED"
    entered_before_staff: bool


@dataclass(frozen=True, slots=True)
class PurityReading:
    reading_id: str
    kind: str  # "XRF_POINT" | "KARAT_METER" | "TOUCHSTONE_RANGE" | "ASSAY"
    permille: Permille
    tolerance_permille: Permille
    point_index: int = 1


@dataclass(frozen=True, slots=True)
class HUIDReading:
    huid_code: str | None
    status: str  # "NOT_PRESENT" | "ATTESTED" | "VERIFIED" | "MISMATCH"
    declared_purity_permille: Permille | None = None


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    """Complete immutable collection of evidence for an exchange."""

    exchange_id: str
    scale: ScaleReading | None
    witness: CustomerWitnessReading | None
    purity_readings: tuple[PurityReading, ...]
    huid: HUIDReading | None
    deduction_bp: Bp


DEFAULT_DAY_CLOSE_MAX_VARIANCE_UG: Ug = Ug(100_000)


@dataclass(frozen=True, slots=True)
class ShopPolicy:
    """Configured shop operating policy limits."""

    max_deduction_bp: Bp
    xrf_max_variance_permille: Permille
    scale_calibration_required: bool = True
    min_independent_purity_sources: int = 2
    day_close_max_variance_ug: Ug = DEFAULT_DAY_CLOSE_MAX_VARIANCE_UG  # 0.1 g default
