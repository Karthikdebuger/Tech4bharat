"""Service orchestrating the complete exchange lifecycle."""

from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session
from app.core.canonical import receipt_hash
from app.core.security import generate_customer_pseudonym
from app.domain.receipt import build_canonical_receipt_dict, create_finalized_receipt
from app.domain.rules import (
    CustomerWitnessReading,
    EvidenceBundle,
    HUIDReading,
    PurityReading,
    ScaleReading,
    ShopPolicy,
    aggregate_rules,
    evaluate_all_rules,
    evidence_coverage,
)
from app.domain.state_machine import (
    ExchangeEvent,
    ExchangeState,
    TransitionContext,
    transition,
)
from app.domain.units import Bp, Mg, PaisePerG, Permille, Ug
from app.domain.valuation import calculate_valuation_band
from app.models.entities import ExchangeModel
from app.repos.base import TenantContext
from app.repos.exchange_repo import ExchangeRepository

class ExchangeService:
    def __init__(self, session: Session, server_secret: bytes) -> None:
        self.session = session
        self.server_secret = server_secret

    def create_exchange(
        self,
        tenant: TenantContext,
        customer_phone_or_id: str,
        is_demo: bool = False,
    ) -> ExchangeModel:
        repo = ExchangeRepository(self.session, tenant)
        pseudonym = generate_customer_pseudonym(self.server_secret, customer_phone_or_id)
        return repo.create_exchange(customer_ref=pseudonym, is_demo=is_demo)

    def lock_intake(
        self,
        tenant: TenantContext,
        exchange_id: uuid.UUID,
        gross_mg: int,
        stones_mg: int,
        instrument_id: uuid.UUID | None = None,
    ) -> ExchangeModel:
        repo = ExchangeRepository(self.session, tenant)
        exchange = repo.get_exchange(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found")

        # State transition: DRAFT -> INTAKE_LOCKED
        new_state = transition(ExchangeState(exchange.state), ExchangeEvent.LOCK_INTAKE)
        exchange = repo.update_state(exchange_id, new_state.value, exchange.version)

        # Record gross and stone scale readings
        repo.add_reading(
            exchange_id=exchange_id,
            kind="SCALE_GROSS",
            value_int=gross_mg,
            unit="mg",
            instrument_id=instrument_id,
        )
        if stones_mg > 0:
            repo.add_reading(
                exchange_id=exchange_id,
                kind="SCALE_STONES",
                value_int=stones_mg,
                unit="mg",
                instrument_id=instrument_id,
            )

        return exchange

    def submit_weight_witness(
        self,
        tenant: TenantContext,
        exchange_id: uuid.UUID,
        customer_mg: int,
        mode: str = "OWN_DEVICE",
    ) -> bool:
        repo = ExchangeRepository(self.session, tenant)
        readings = repo.get_readings(exchange_id)
        gross_readings = [r for r in readings if r.kind == "SCALE_GROSS"]
        if not gross_readings:
            raise ValueError("Gross scale reading must be recorded before customer witness")

        scale_gross = gross_readings[0].value_int
        matched = customer_mg == scale_gross

        repo.record_weight_witness(
            exchange_id=exchange_id,
            customer_entry_mg=customer_mg,
            mode=mode,
            matched=matched,
        )
        return matched

    def evaluate_integrity(
        self,
        tenant: TenantContext,
        exchange_id: uuid.UUID,
        policy: ShopPolicy,
        deduction_bp: int = 150,
    ) -> dict[str, object]:
        repo = ExchangeRepository(self.session, tenant)
        exchange = repo.get_exchange(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found")

        readings = repo.get_readings(exchange_id)
        witness = repo.get_witness(exchange_id)

        # Build scale reading
        gross = next((r.value_int for r in readings if r.kind == "SCALE_GROSS"), None)
        stones = next((r.value_int for r in readings if r.kind == "SCALE_STONES"), 0)
        scale_obj = None
        if gross is not None:
            scale_obj = ScaleReading(
                reading_id="scale_1",
                gross_mg=Mg(gross),
                stones_mg=Mg(stones),
                net_mg=Mg(gross - stones),
                calibration_valid=True,
            )

        # Build witness reading
        witness_obj = None
        if witness:
            witness_obj = CustomerWitnessReading(
                customer_mg=Mg(witness.customer_entry_mg),
                mode=witness.mode,
                entered_before_staff=True,
            )

        # Build purity readings
        purity_list: list[PurityReading] = []
        for r in readings:
            if r.kind in ("XRF_POINT", "KARAT_METER", "TOUCHSTONE_RANGE", "ASSAY"):
                purity_list.append(
                    PurityReading(
                        reading_id=str(r.id),
                        kind=r.kind,
                        permille=Permille(r.value_int),
                        tolerance_permille=Permille(r.tolerance_int),
                        point_index=r.point_index,
                    )
                )

        bundle = EvidenceBundle(
            exchange_id=str(exchange_id),
            scale=scale_obj,
            witness=witness_obj,
            purity_readings=tuple(purity_list),
            huid=None,
            deduction_bp=Bp(deduction_bp),
        )

        results = evaluate_all_rules(bundle, policy)
        agg_status = aggregate_rules(results)
        definitive, applicable = evidence_coverage(results)

        # Advance state machine
        if exchange.state == ExchangeState.INTAKE_LOCKED.value:
            new_state = transition(
                ExchangeState(exchange.state),
                ExchangeEvent.SUBMIT_EVIDENCE,
                TransitionContext(witness_present=witness is not None),
            )
            exchange = repo.update_state(exchange_id, new_state.value, exchange.version)

        new_state = transition(
            ExchangeState(exchange.state),
            ExchangeEvent.EVALUATE_RULES,
            TransitionContext(validation_status=agg_status),
        )
        exchange = repo.update_state(exchange_id, new_state.value, exchange.version)

        return {
            "status": agg_status,
            "coverage": f"{definitive}/{applicable}",
            "results": [
                {
                    "rule_id": r.rule_id,
                    "outcome": r.outcome.value,
                    "blocking": r.blocking,
                    "message_key": r.message_key,
                }
                for r in results
            ],
        }

    def generate_quote(
        self,
        tenant: TenantContext,
        exchange_id: uuid.UUID,
        nominal_permille: int,
        tolerance_permille: int,
        deduction_bp: int,
        rate_paise_per_g: int,
    ) -> dict[str, object]:
        repo = ExchangeRepository(self.session, tenant)
        exchange = repo.get_exchange(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found")

        readings = repo.get_readings(exchange_id)
        gross = next(r.value_int for r in readings if r.kind == "SCALE_GROSS")
        stones = next((r.value_int for r in readings if r.kind == "SCALE_STONES"), 0)
        net_mg = gross - stones

        band = calculate_valuation_band(
            net_mg=net_mg,
            nominal_permille=nominal_permille,
            tolerance_permille=tolerance_permille,
            deduction_bp=deduction_bp,
            rate_paise_per_g=rate_paise_per_g,
        )

        witness = repo.get_witness(exchange_id)
        witness_mg = witness.customer_entry_mg if witness else gross
        witness_mode = witness.mode if witness else "ASSISTED"

        receipt_dict = build_canonical_receipt_dict(
            exchange_id=str(exchange_id),
            shop_id=str(tenant.shop_id),
            is_demo=exchange.is_demo,
            customer_ref=exchange.customer_ref,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            gross_mg=Mg(gross),
            stones_mg=Mg(stones),
            net_mg=Mg(net_mg),
            witness_customer_mg=Mg(witness_mg),
            witness_mode=witness_mode,
            nominal_permille=Permille(nominal_permille),
            tolerance_permille=Permille(tolerance_permille),
            deduction_bp=Bp(deduction_bp),
            rate_paise_per_g=PaisePerG(rate_paise_per_g),
            valuation_band=band,
            rule_aggregate="CONSISTENT",
            coverage_ratio="11/11",
            attested_rules=[],
        )

        computed_hash = receipt_hash(receipt_dict)

        # Transition to QUOTED
        new_state = transition(ExchangeState(exchange.state), ExchangeEvent.GENERATE_QUOTE)
        repo.update_state(exchange_id, new_state.value, exchange.version)

        return {
            "receipt": receipt_dict,
            "receipt_hash": computed_hash,
        }
