"""Comprehensive unit tests for integrity rules E01-E13 and rule engine."""

from app.domain.rules import (
    CustomerWitnessReading,
    EvidenceBundle,
    HUIDReading,
    Outcome,
    PurityReading,
    ScaleReading,
    ShopPolicy,
    aggregate_rules,
    evaluate_all_rules,
    evidence_coverage,
    rule_e01_scale_calibration,
    rule_e02_net_weight_sanity,
    rule_e03_purity_variance,
    rule_e04_cross_method_consistency,
    rule_e05_declared_vs_measured,
    rule_e06_minimum_evidence,
    rule_e09_huid_format,
    rule_e10_huid_verification_status,
    rule_e11_blind_customer_weight_witness,
    rule_e12_policy_margin_cap,
    rule_e13_day_close_melt_variance,
)
from app.domain.units import Bp, Mg, Permille, Ug

DEFAULT_POLICY = ShopPolicy(
    max_deduction_bp=Bp(300),
    xrf_max_variance_permille=Permille(15),
    scale_calibration_required=True,
    min_independent_purity_sources=2,
    day_close_max_variance_ug=Ug(100_000),
)


DEFAULT_TEST_DEDUCTION_BP: Bp = Bp(150)


def make_bundle(
    scale: ScaleReading | None = None,
    witness: CustomerWitnessReading | None = None,
    purity_readings: tuple[PurityReading, ...] = (),
    huid: HUIDReading | None = None,
    deduction_bp: Bp = DEFAULT_TEST_DEDUCTION_BP,
) -> EvidenceBundle:
    return EvidenceBundle(
        exchange_id="ex-101",
        scale=scale,
        witness=witness,
        purity_readings=purity_readings,
        huid=huid,
        deduction_bp=deduction_bp,
    )


def test_rule_e01_calibration() -> None:
    bundle_valid = make_bundle(
        scale=ScaleReading("s1", Mg(10000), Mg(0), Mg(10000), calibration_valid=True)
    )
    assert rule_e01_scale_calibration(bundle_valid, DEFAULT_POLICY).outcome == Outcome.PASS

    bundle_expired = make_bundle(
        scale=ScaleReading("s1", Mg(10000), Mg(0), Mg(10000), calibration_valid=False)
    )
    res_expired = rule_e01_scale_calibration(bundle_expired, DEFAULT_POLICY)
    assert res_expired.outcome == Outcome.FAIL
    assert res_expired.blocking is True

    bundle_no_scale = make_bundle(scale=None)
    assert rule_e01_scale_calibration(bundle_no_scale, DEFAULT_POLICY).outcome == Outcome.UNKNOWN


def test_rule_e02_net_weight_sanity() -> None:
    # Valid
    bundle_valid = make_bundle(
        scale=ScaleReading("s1", Mg(30800), Mg(800), Mg(30000), calibration_valid=True)
    )
    assert rule_e02_net_weight_sanity(bundle_valid, DEFAULT_POLICY).outcome == Outcome.PASS

    # Arithmetic mismatch
    bundle_arith_error = make_bundle(
        scale=ScaleReading("s1", Mg(30800), Mg(800), Mg(29000), calibration_valid=True)
    )
    assert rule_e02_net_weight_sanity(bundle_arith_error, DEFAULT_POLICY).outcome == Outcome.FAIL

    # Negative net
    bundle_negative = make_bundle(
        scale=ScaleReading("s1", Mg(1000), Mg(2000), Mg(0), calibration_valid=True)
    )
    assert rule_e02_net_weight_sanity(bundle_negative, DEFAULT_POLICY).outcome == Outcome.FAIL


def test_rule_e03_purity_variance() -> None:
    # Under tolerance (910 and 918 -> spread 8 <= 15)
    r1 = PurityReading("p1", "XRF_POINT", Permille(910), Permille(5), 1)
    r2 = PurityReading("p2", "XRF_POINT", Permille(918), Permille(5), 2)
    b_pass = make_bundle(purity_readings=(r1, r2))
    assert rule_e03_purity_variance(b_pass, DEFAULT_POLICY).outcome == Outcome.PASS

    # Exceeds tolerance (910 and 930 -> spread 20 > 15)
    r3 = PurityReading("p3", "XRF_POINT", Permille(930), Permille(5), 2)
    b_fail = make_bundle(purity_readings=(r1, r3))
    res = rule_e03_purity_variance(b_fail, DEFAULT_POLICY)
    assert res.outcome == Outcome.FAIL
    assert res.blocking is True


def test_rule_e04_cross_method_consistency() -> None:
    km = PurityReading("p1", "KARAT_METER", Permille(916), Permille(5))
    ts_match = PurityReading("p2", "TOUCHSTONE_RANGE", Permille(910), Permille(10))
    ts_conflict = PurityReading("p3", "TOUCHSTONE_RANGE", Permille(880), Permille(10))

    b_match = make_bundle(purity_readings=(km, ts_match))
    assert rule_e04_cross_method_consistency(b_match, DEFAULT_POLICY).outcome == Outcome.PASS

    b_conflict = make_bundle(purity_readings=(km, ts_conflict))
    assert rule_e04_cross_method_consistency(b_conflict, DEFAULT_POLICY).outcome == Outcome.FAIL


def test_rule_e05_declared_vs_measured() -> None:
    huid = HUIDReading("AB1234", "VERIFIED", declared_purity_permille=Permille(916))
    r_pass = PurityReading("p1", "XRF_POINT", Permille(914), Permille(5))
    r_fail = PurityReading("p2", "XRF_POINT", Permille(890), Permille(5))

    b_pass = make_bundle(huid=huid, purity_readings=(r_pass,))
    assert rule_e05_declared_vs_measured(b_pass, DEFAULT_POLICY).outcome == Outcome.PASS

    b_fail = make_bundle(huid=huid, purity_readings=(r_fail,))
    assert rule_e05_declared_vs_measured(b_fail, DEFAULT_POLICY).outcome == Outcome.FAIL


def test_rule_e06_minimum_evidence() -> None:
    r_xrf = PurityReading("p1", "XRF_POINT", Permille(916), Permille(5))
    r_km = PurityReading("p2", "KARAT_METER", Permille(916), Permille(5))

    # Single source -> UNKNOWN
    b_single = make_bundle(purity_readings=(r_xrf,))
    assert rule_e06_minimum_evidence(b_single, DEFAULT_POLICY).outcome == Outcome.UNKNOWN

    # Two distinct sources -> PASS
    b_two = make_bundle(purity_readings=(r_xrf, r_km))
    assert rule_e06_minimum_evidence(b_two, DEFAULT_POLICY).outcome == Outcome.PASS


def test_rule_e09_huid_format() -> None:
    b_valid = make_bundle(huid=HUIDReading("AB1234", "VERIFIED"))
    assert rule_e09_huid_format(b_valid, DEFAULT_POLICY).outcome == Outcome.PASS

    b_invalid_len = make_bundle(huid=HUIDReading("ABC12", "VERIFIED"))
    assert rule_e09_huid_format(b_invalid_len, DEFAULT_POLICY).outcome == Outcome.FAIL

    b_invalid_chars = make_bundle(huid=HUIDReading("AB-123", "VERIFIED"))
    assert rule_e09_huid_format(b_invalid_chars, DEFAULT_POLICY).outcome == Outcome.FAIL


def test_rule_e10_huid_status() -> None:
    b_verified = make_bundle(huid=HUIDReading("AB1234", "VERIFIED"))
    assert rule_e10_huid_verification_status(b_verified, DEFAULT_POLICY).outcome == Outcome.PASS

    b_attested = make_bundle(huid=HUIDReading("AB1234", "ATTESTED"))
    assert rule_e10_huid_verification_status(b_attested, DEFAULT_POLICY).outcome == Outcome.ATTESTED

    b_mismatch = make_bundle(huid=HUIDReading("AB1234", "MISMATCH"))
    assert rule_e10_huid_verification_status(b_mismatch, DEFAULT_POLICY).outcome == Outcome.FAIL


def test_rule_e11_blind_customer_witness() -> None:
    scale = ScaleReading("s1", Mg(30800), Mg(0), Mg(30800), calibration_valid=True)

    # Customer device exact match -> PASS
    b_match = make_bundle(
        scale=scale,
        witness=CustomerWitnessReading(
            customer_mg=Mg(30800), mode="OWN_DEVICE", entered_before_staff=True
        ),
    )
    assert rule_e11_blind_customer_weight_witness(b_match, DEFAULT_POLICY).outcome == Outcome.PASS

    # Assisted mode exact match -> ATTESTED
    b_assisted = make_bundle(
        scale=scale,
        witness=CustomerWitnessReading(
            customer_mg=Mg(30800), mode="ASSISTED", entered_before_staff=True
        ),
    )
    assert (
        rule_e11_blind_customer_weight_witness(b_assisted, DEFAULT_POLICY).outcome
        == Outcome.ATTESTED
    )

    # Mismatch -> FAIL (blocking)
    b_mismatch = make_bundle(
        scale=scale,
        witness=CustomerWitnessReading(
            customer_mg=Mg(30500), mode="OWN_DEVICE", entered_before_staff=True
        ),
    )
    res = rule_e11_blind_customer_weight_witness(b_mismatch, DEFAULT_POLICY)
    assert res.outcome == Outcome.FAIL
    assert res.blocking is True


def test_rule_e12_policy_margin_cap() -> None:
    # Within 300 bp cap
    b_ok = make_bundle(deduction_bp=Bp(200))
    assert rule_e12_policy_margin_cap(b_ok, DEFAULT_POLICY).outcome == Outcome.PASS

    # Exceeds 300 bp cap
    b_exceeded = make_bundle(deduction_bp=Bp(350))
    assert rule_e12_policy_margin_cap(b_exceeded, DEFAULT_POLICY).outcome == Outcome.FAIL


def test_rule_e13_melt_variance() -> None:
    # Allowed variance 100_000 ug (0.1g)
    assert (
        rule_e13_day_close_melt_variance(1_000_000, 1_050_000, DEFAULT_POLICY).outcome
        == Outcome.PASS
    )
    assert (
        rule_e13_day_close_melt_variance(1_000_000, 1_250_000, DEFAULT_POLICY).outcome
        == Outcome.FAIL
    )


def test_aggregation_and_coverage() -> None:
    scale = ScaleReading("s1", Mg(30800), Mg(0), Mg(30800), calibration_valid=True)
    witness = CustomerWitnessReading(
        customer_mg=Mg(30800), mode="OWN_DEVICE", entered_before_staff=True
    )
    r1 = PurityReading("p1", "XRF_POINT", Permille(916), Permille(5), 1)
    r2 = PurityReading("p2", "XRF_POINT", Permille(918), Permille(5), 2)
    r3 = PurityReading("p3", "KARAT_METER", Permille(916), Permille(5), 1)
    huid = HUIDReading("AB1234", "VERIFIED", declared_purity_permille=Permille(916))

    consistent_bundle = make_bundle(
        scale=scale,
        witness=witness,
        purity_readings=(r1, r2, r3),
        huid=huid,
        deduction_bp=Bp(150),
    )

    results = evaluate_all_rules(consistent_bundle, DEFAULT_POLICY)
    status = aggregate_rules(results)
    assert status == "CONSISTENT"

    definitive, applicable = evidence_coverage(results)
    assert definitive > 0
    assert applicable >= definitive
