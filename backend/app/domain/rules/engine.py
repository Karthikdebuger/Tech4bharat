"""Pure domain rule engine and rules E01-E13 for Gold Trust AI.

Per §6.2:
- Each rule is a pure function (EvidenceBundle, ShopPolicy) -> RuleResult
- Results are deterministic, versioned, and replayable
- Aggregation computes CONSISTENT, INCOMPLETE, or CONFLICT
- Zero free-form text: deterministic i18n keys + parameters
"""

import re
from collections.abc import Sequence

from app.domain.rules.models import (
    EvidenceBundle,
    Outcome,
    RuleResult,
    ShopPolicy,
)

HUID_REGEX = re.compile(r"^[A-Z0-9]{6}$")


def rule_e01_scale_calibration(bundle: EvidenceBundle, policy: ShopPolicy) -> RuleResult:
    """E01: Scale calibration validity check."""
    if not bundle.scale:
        return RuleResult(
            rule_id="E01",
            rule_version=1,
            outcome=Outcome.UNKNOWN,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e01.scale_missing",
            params={},
        )
    if policy.scale_calibration_required and not bundle.scale.calibration_valid:
        return RuleResult(
            rule_id="E01",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(bundle.scale.reading_id,),
            message_key="rule.e01.calibration_expired",
            params={"reading_id": bundle.scale.reading_id},
        )
    return RuleResult(
        rule_id="E01",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(bundle.scale.reading_id,),
        message_key="rule.e01.pass",
        params={"reading_id": bundle.scale.reading_id},
    )


def rule_e02_net_weight_sanity(bundle: EvidenceBundle, _policy: ShopPolicy) -> RuleResult:
    """E02: Net weight mathematical sanity: gross >= stones and net > 0."""
    if not bundle.scale:
        return RuleResult(
            rule_id="E02",
            rule_version=1,
            outcome=Outcome.UNKNOWN,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e02.scale_missing",
            params={},
        )
    scale = bundle.scale
    if scale.gross_mg < scale.stones_mg or scale.net_mg <= 0:
        return RuleResult(
            rule_id="E02",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(scale.reading_id,),
            message_key="rule.e02.negative_net_weight",
            params={"gross_mg": int(scale.gross_mg), "stones_mg": int(scale.stones_mg)},
        )
    if scale.net_mg != (scale.gross_mg - scale.stones_mg):
        return RuleResult(
            rule_id="E02",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(scale.reading_id,),
            message_key="rule.e02.arithmetic_mismatch",
            params={
                "net_mg": int(scale.net_mg),
                "expected_mg": int(scale.gross_mg - scale.stones_mg),
            },
        )
    return RuleResult(
        rule_id="E02",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(scale.reading_id,),
        message_key="rule.e02.pass",
        params={"net_mg": int(scale.net_mg)},
    )


def rule_e03_purity_variance(bundle: EvidenceBundle, policy: ShopPolicy) -> RuleResult:
    """E03: Variance among multiple points (e.g. XRF) must not exceed policy threshold."""
    xrf_readings = [r for r in bundle.purity_readings if r.kind == "XRF_POINT"]
    if len(xrf_readings) < 2:
        return RuleResult(
            rule_id="E03",
            rule_version=1,
            outcome=Outcome.NOT_APPLICABLE if len(xrf_readings) == 0 else Outcome.UNKNOWN,
            blocking=len(xrf_readings) == 1,
            evidence_refs=tuple(r.reading_id for r in xrf_readings),
            message_key="rule.e03.insufficient_points",
            params={"count": len(xrf_readings)},
        )

    values = [int(r.permille) for r in xrf_readings]
    min_v, max_v = min(values), max(values)
    spread = max_v - min_v

    if spread > int(policy.xrf_max_variance_permille):
        return RuleResult(
            rule_id="E03",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=tuple(r.reading_id for r in xrf_readings),
            message_key="rule.e03.variance_exceeded",
            params={
                "spread_permille": spread,
                "max_allowed": int(policy.xrf_max_variance_permille),
            },
        )

    return RuleResult(
        rule_id="E03",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=tuple(r.reading_id for r in xrf_readings),
        message_key="rule.e03.pass",
        params={"spread_permille": spread},
    )


def rule_e04_cross_method_consistency(bundle: EvidenceBundle, _policy: ShopPolicy) -> RuleResult:
    """E04: Cross-method purity agreement (e.g. Karat meter vs touchstone)."""
    km_readings = [r for r in bundle.purity_readings if r.kind == "KARAT_METER"]
    ts_readings = [r for r in bundle.purity_readings if r.kind == "TOUCHSTONE_RANGE"]

    if not km_readings or not ts_readings:
        return RuleResult(
            rule_id="E04",
            rule_version=1,
            outcome=Outcome.NOT_APPLICABLE,
            blocking=False,
            evidence_refs=(),
            message_key="rule.e04.not_applicable",
            params={},
        )

    km = km_readings[0]
    ts = ts_readings[0]
    diff = abs(int(km.permille) - int(ts.permille))
    combined_tolerance = int(km.tolerance_permille) + int(ts.tolerance_permille)

    if diff > combined_tolerance:
        return RuleResult(
            rule_id="E04",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(km.reading_id, ts.reading_id),
            message_key="rule.e04.cross_method_conflict",
            params={"diff_permille": diff, "allowed_tolerance": combined_tolerance},
        )

    return RuleResult(
        rule_id="E04",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(km.reading_id, ts.reading_id),
        message_key="rule.e04.pass",
        params={"diff_permille": diff},
    )


def rule_e05_declared_vs_measured(bundle: EvidenceBundle, _policy: ShopPolicy) -> RuleResult:
    """E05: Measured purity must not be materially lower than declared HUID/hallmark purity."""
    if not bundle.huid or bundle.huid.declared_purity_permille is None:
        return RuleResult(
            rule_id="E05",
            rule_version=1,
            outcome=Outcome.NOT_APPLICABLE,
            blocking=False,
            evidence_refs=(),
            message_key="rule.e05.no_declared_purity",
            params={},
        )

    if not bundle.purity_readings:
        return RuleResult(
            rule_id="E05",
            rule_version=1,
            outcome=Outcome.UNKNOWN,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e05.no_readings",
            params={},
        )

    declared = int(bundle.huid.declared_purity_permille)
    # Average of measured purities
    avg_measured = sum(int(r.permille) for r in bundle.purity_readings) // len(
        bundle.purity_readings
    )
    max_tolerance = max(int(r.tolerance_permille) for r in bundle.purity_readings)

    if avg_measured < (declared - max_tolerance):
        return RuleResult(
            rule_id="E05",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=tuple(r.reading_id for r in bundle.purity_readings),
            message_key="rule.e05.measured_below_declared",
            params={"declared": declared, "measured": avg_measured, "tolerance": max_tolerance},
        )

    return RuleResult(
        rule_id="E05",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=tuple(r.reading_id for r in bundle.purity_readings),
        message_key="rule.e05.pass",
        params={"declared": declared, "measured": avg_measured},
    )


def rule_e06_minimum_evidence(bundle: EvidenceBundle, policy: ShopPolicy) -> RuleResult:
    """E06: Minimum independent evidence sources requirement."""
    # Count distinct measurement kinds or assay
    distinct_kinds = {r.kind for r in bundle.purity_readings}
    has_assay = "ASSAY" in distinct_kinds

    if has_assay or len(distinct_kinds) >= policy.min_independent_purity_sources:
        return RuleResult(
            rule_id="E06",
            rule_version=1,
            outcome=Outcome.PASS,
            blocking=True,
            evidence_refs=tuple(r.reading_id for r in bundle.purity_readings),
            message_key="rule.e06.pass",
            params={"source_count": len(distinct_kinds)},
        )

    return RuleResult(
        rule_id="E06",
        rule_version=1,
        outcome=Outcome.UNKNOWN,
        blocking=True,
        evidence_refs=tuple(r.reading_id for r in bundle.purity_readings),
        message_key="rule.e06.insufficient_sources",
        params={"current": len(distinct_kinds), "required": policy.min_independent_purity_sources},
    )


def rule_e07_outlier_detection(bundle: EvidenceBundle, _policy: ShopPolicy) -> RuleResult:
    """E07: Flag individual reading outlier beyond 3 sigma or 25‰ deviation from median."""
    if len(bundle.purity_readings) < 3:
        return RuleResult(
            rule_id="E07",
            rule_version=1,
            outcome=Outcome.NOT_APPLICABLE,
            blocking=False,
            evidence_refs=(),
            message_key="rule.e07.not_applicable",
            params={},
        )

    vals = sorted(int(r.permille) for r in bundle.purity_readings)
    median = vals[len(vals) // 2]
    outliers = [r for r in bundle.purity_readings if abs(int(r.permille) - median) > 25]

    if outliers:
        return RuleResult(
            rule_id="E07",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=False,  # Warning flag only
            evidence_refs=tuple(r.reading_id for r in outliers),
            message_key="rule.e07.outlier_detected",
            params={"outlier_count": len(outliers), "median": median},
        )

    return RuleResult(
        rule_id="E07",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=False,
        evidence_refs=(),
        message_key="rule.e07.pass",
        params={},
    )


def rule_e08_destructive_assay_trigger(bundle: EvidenceBundle, policy: ShopPolicy) -> RuleResult:
    """E08: Assay recommended when non-destructive tests disagree or core suspected."""
    xrf_readings = [r for r in bundle.purity_readings if r.kind == "XRF_POINT"]
    if len(xrf_readings) >= 2:
        spread = max(int(r.permille) for r in xrf_readings) - min(
            int(r.permille) for r in xrf_readings
        )
        if spread > int(policy.xrf_max_variance_permille):
            return RuleResult(
                rule_id="E08",
                rule_version=1,
                outcome=Outcome.UNKNOWN,
                blocking=True,
                evidence_refs=tuple(r.reading_id for r in xrf_readings),
                message_key="rule.e08.assay_required",
                params={"spread_permille": spread},
            )

    return RuleResult(
        rule_id="E08",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=False,
        evidence_refs=(),
        message_key="rule.e08.pass",
        params={},
    )


def rule_e09_huid_format(bundle: EvidenceBundle, _policy: ShopPolicy) -> RuleResult:
    """E09: Validate BIS Hallmark Unique Identification (HUID) format (6 alphanumeric)."""
    if not bundle.huid or not bundle.huid.huid_code:
        return RuleResult(
            rule_id="E09",
            rule_version=1,
            outcome=Outcome.NOT_APPLICABLE,
            blocking=False,
            evidence_refs=(),
            message_key="rule.e09.no_huid",
            params={},
        )

    code = bundle.huid.huid_code.strip().upper()
    if not HUID_REGEX.match(code):
        return RuleResult(
            rule_id="E09",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e09.invalid_format",
            params={"huid_code": code},
        )

    return RuleResult(
        rule_id="E09",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(),
        message_key="rule.e09.pass",
        params={"huid_code": code},
    )


def rule_e10_huid_verification_status(bundle: EvidenceBundle, _policy: ShopPolicy) -> RuleResult:
    """E10: Distinguish between official VERIFIED, operator ATTESTED, and MISMATCH."""
    if not bundle.huid or not bundle.huid.huid_code:
        return RuleResult(
            rule_id="E10",
            rule_version=1,
            outcome=Outcome.NOT_APPLICABLE,
            blocking=False,
            evidence_refs=(),
            message_key="rule.e10.no_huid",
            params={},
        )

    match bundle.huid.status:
        case "VERIFIED":
            return RuleResult(
                rule_id="E10",
                rule_version=1,
                outcome=Outcome.PASS,
                blocking=True,
                evidence_refs=(),
                message_key="rule.e10.verified",
                params={"huid_code": bundle.huid.huid_code},
            )
        case "ATTESTED":
            return RuleResult(
                rule_id="E10",
                rule_version=1,
                outcome=Outcome.ATTESTED,
                blocking=False,
                evidence_refs=(),
                message_key="rule.e10.operator_attested",
                params={"huid_code": bundle.huid.huid_code},
            )
        case "MISMATCH":
            return RuleResult(
                rule_id="E10",
                rule_version=1,
                outcome=Outcome.FAIL,
                blocking=True,
                evidence_refs=(),
                message_key="rule.e10.registry_mismatch",
                params={"huid_code": bundle.huid.huid_code},
            )
        case _:
            return RuleResult(
                rule_id="E10",
                rule_version=1,
                outcome=Outcome.UNKNOWN,
                blocking=True,
                evidence_refs=(),
                message_key="rule.e10.lookup_pending",
                params={"huid_code": bundle.huid.huid_code},
            )


def rule_e11_blind_customer_weight_witness(
    bundle: EvidenceBundle, _policy: ShopPolicy
) -> RuleResult:
    """E11: Blind customer weight witness entry protocol (§6.3).

    Customer enters the digits shown on the scale display.
    Server compares customer_entry_mg with staff_scale_gross_mg.
    """
    if not bundle.scale:
        return RuleResult(
            rule_id="E11",
            rule_version=1,
            outcome=Outcome.UNKNOWN,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e11.scale_missing",
            params={},
        )

    if not bundle.witness:
        return RuleResult(
            rule_id="E11",
            rule_version=1,
            outcome=Outcome.UNKNOWN,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e11.witness_missing",
            params={},
        )

    scale_gross = int(bundle.scale.gross_mg)
    customer_entered = int(bundle.witness.customer_mg)

    if scale_gross != customer_entered:
        return RuleResult(
            rule_id="E11",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(bundle.scale.reading_id,),
            message_key="rule.e11.weight_mismatch",
            params={"scale_gross_mg": scale_gross, "customer_entered_mg": customer_entered},
        )

    if bundle.witness.mode == "ASSISTED":
        return RuleResult(
            rule_id="E11",
            rule_version=1,
            outcome=Outcome.ATTESTED,
            blocking=False,
            evidence_refs=(bundle.scale.reading_id,),
            message_key="rule.e11.assisted_witness_pass",
            params={"weight_mg": scale_gross},
        )

    return RuleResult(
        rule_id="E11",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(bundle.scale.reading_id,),
        message_key="rule.e11.pass",
        params={"weight_mg": scale_gross},
    )


def rule_e12_policy_margin_cap(bundle: EvidenceBundle, policy: ShopPolicy) -> RuleResult:
    """E12: Verification that deduction basis points do not exceed policy cap."""
    deduction = int(bundle.deduction_bp)
    max_cap = int(policy.max_deduction_bp)

    if deduction > max_cap:
        return RuleResult(
            rule_id="E12",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e12.cap_exceeded",
            params={"deduction_bp": deduction, "max_cap_bp": max_cap},
        )

    return RuleResult(
        rule_id="E12",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(),
        message_key="rule.e12.pass",
        params={"deduction_bp": deduction},
    )


def rule_e13_day_close_melt_variance(
    physical_stock_ug: int,
    ledger_stock_ug: int,
    policy: ShopPolicy,
) -> RuleResult:
    """E13: Day-close stock reconciliation variance threshold check."""
    variance = abs(physical_stock_ug - ledger_stock_ug)
    allowed_variance = int(policy.day_close_max_variance_ug)

    if variance > allowed_variance:
        return RuleResult(
            rule_id="E13",
            rule_version=1,
            outcome=Outcome.FAIL,
            blocking=True,
            evidence_refs=(),
            message_key="rule.e13.variance_exceeded",
            params={"variance_ug": variance, "allowed_ug": allowed_variance},
        )

    return RuleResult(
        rule_id="E13",
        rule_version=1,
        outcome=Outcome.PASS,
        blocking=True,
        evidence_refs=(),
        message_key="rule.e13.pass",
        params={"variance_ug": variance},
    )


ALL_EXCHANGE_RULES = (
    rule_e01_scale_calibration,
    rule_e02_net_weight_sanity,
    rule_e03_purity_variance,
    rule_e04_cross_method_consistency,
    rule_e05_declared_vs_measured,
    rule_e06_minimum_evidence,
    rule_e07_outlier_detection,
    rule_e08_destructive_assay_trigger,
    rule_e09_huid_format,
    rule_e10_huid_verification_status,
    rule_e11_blind_customer_weight_witness,
    rule_e12_policy_margin_cap,
)


def evaluate_all_rules(bundle: EvidenceBundle, policy: ShopPolicy) -> list[RuleResult]:
    """Execute all active exchange rules against the evidence bundle and policy."""
    return [rule(bundle, policy) for rule in ALL_EXCHANGE_RULES]


def aggregate_rules(results: Sequence[RuleResult]) -> str:
    """Compute aggregate validation status per §6.2:

    - CONFLICT: If any applicable rule fails with blocking=True
    - INCOMPLETE: If any applicable rule is unknown with blocking=True
    - CONSISTENT: If all applicable blocking rules pass or are attested
    """
    if any(r.outcome == Outcome.FAIL and r.blocking for r in results):
        return "CONFLICT"
    if any(r.outcome == Outcome.UNKNOWN and r.blocking for r in results):
        return "INCOMPLETE"
    return "CONSISTENT"


def evidence_coverage(results: Sequence[RuleResult]) -> tuple[int, int]:
    """Calculate coverage fraction: (definitive_applicable_rules, total_applicable_rules).

    Reported to user as a fraction, never as an ungrounded 'confidence percentage'.
    """
    applicable = [r for r in results if r.outcome != Outcome.NOT_APPLICABLE]
    definitive = [
        r for r in applicable if r.outcome in (Outcome.PASS, Outcome.FAIL, Outcome.ATTESTED)
    ]
    return len(definitive), len(applicable)
