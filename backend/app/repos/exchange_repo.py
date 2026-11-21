"""Tenant-isolated exchange and evidence repository."""

from datetime import datetime, timezone
from typing import Any
import uuid
from sqlalchemy import select
from app.models.entities import (
    AuditEventModel,
    ExchangeModel,
    ReadingModel,
    ReceiptModel,
    WeightWitnessModel,
)
from app.repos.base import BaseTenantRepository

class ExchangeRepository(BaseTenantRepository):
    def create_exchange(
        self,
        customer_ref: str,
        is_demo: bool = False,
    ) -> ExchangeModel:
        if not self.tenant.staff_id:
            raise ValueError("Staff ID required in TenantContext to create an exchange")

        exchange = ExchangeModel(
            id=uuid.uuid4(),
            shop_id=self.shop_id,
            state="DRAFT",
            is_demo=is_demo,
            customer_ref=customer_ref,
            created_by=self.tenant.staff_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(exchange)
        self.session.flush()
        return exchange

    def get_exchange(self, exchange_id: uuid.UUID) -> ExchangeModel | None:
        stmt = select(ExchangeModel).where(
            ExchangeModel.id == exchange_id,
            ExchangeModel.shop_id == self.shop_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def update_state(
        self,
        exchange_id: uuid.UUID,
        new_state: str,
        expected_version: int,
    ) -> ExchangeModel:
        exchange = self.get_exchange(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found for tenant")
        if exchange.version != expected_version:
            raise ValueError(f"Concurrency conflict: expected version {expected_version}, got {exchange.version}")

        exchange.state = new_state
        exchange.version += 1
        exchange.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return exchange

    def add_reading(
        self,
        exchange_id: uuid.UUID,
        kind: str,
        value_int: int,
        unit: str,
        tolerance_int: int = 0,
        instrument_id: uuid.UUID | None = None,
        point_index: int = 1,
        source_kind: str = "MANUAL",
        evidence_blob_sha256: str | None = None,
    ) -> ReadingModel:
        if not self.tenant.staff_id:
            raise ValueError("Staff ID required to record a reading")

        reading = ReadingModel(
            id=uuid.uuid4(),
            exchange_id=exchange_id,
            shop_id=self.shop_id,
            kind=kind,
            value_int=value_int,
            unit=unit,
            tolerance_int=tolerance_int,
            instrument_id=instrument_id,
            point_index=point_index,
            source_kind=source_kind,
            evidence_blob_sha256=evidence_blob_sha256,
            captured_by=self.tenant.staff_id,
            captured_at=datetime.now(timezone.utc),
        )
        self.session.add(reading)
        self.session.flush()
        return reading

    def record_weight_witness(
        self,
        exchange_id: uuid.UUID,
        customer_entry_mg: int,
        mode: str,
        matched: bool,
    ) -> WeightWitnessModel:
        witness = WeightWitnessModel(
            exchange_id=exchange_id,
            shop_id=self.shop_id,
            customer_entry_mg=customer_entry_mg,
            mode=mode,
            entered_at=datetime.now(timezone.utc),
            matched=matched,
        )
        self.session.merge(witness)
        self.session.flush()
        return witness

    def get_readings(self, exchange_id: uuid.UUID) -> list[ReadingModel]:
        stmt = (
            select(ReadingModel)
            .where(
                ReadingModel.exchange_id == exchange_id,
                ReadingModel.shop_id == self.shop_id,
            )
            .order_by(ReadingModel.captured_at)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_witness(self, exchange_id: uuid.UUID) -> WeightWitnessModel | None:
        stmt = select(WeightWitnessModel).where(
            WeightWitnessModel.exchange_id == exchange_id,
            WeightWitnessModel.shop_id == self.shop_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def save_receipt(
        self,
        exchange_id: uuid.UUID,
        receipt_hash: str,
        canonical_payload: dict[str, Any],
        is_demo: bool,
        supersedes_receipt_hash: str | None = None,
    ) -> ReceiptModel:
        receipt = ReceiptModel(
            id=uuid.uuid4(),
            exchange_id=exchange_id,
            shop_id=self.shop_id,
            receipt_hash=receipt_hash,
            canonical_payload=canonical_payload,
            supersedes_receipt_hash=supersedes_receipt_hash,
            is_demo=is_demo,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(receipt)
        self.session.flush()
        return receipt

    def record_audit_event(
        self,
        action: str,
        object_type: str,
        object_id: uuid.UUID,
        payload: dict[str, Any],
        prev_hash: str,
        this_hash: str,
    ) -> AuditEventModel:
        if not self.tenant.staff_id:
            raise ValueError("Staff ID required to record audit event")

        event = AuditEventModel(
            shop_id=self.shop_id,
            at=datetime.now(timezone.utc),
            actor=self.tenant.staff_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            payload=payload,
            prev_hash=prev_hash,
            this_hash=this_hash,
        )
        self.session.add(event)
        self.session.flush()
        return event
