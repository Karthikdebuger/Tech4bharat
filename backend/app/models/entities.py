"""SQLAlchemy 2.0 ORM entities for Gold Trust AI.

Per ADR-0003 and §5.2:
- All financial and physical values are BigInteger (µg, mg, paise, bp, permille).
- UUIDv4/UUIDv7 primary keys.
- Timestamps are timezone-aware UTC.
- Zero floating-point types in column definitions.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base model class."""

    pass


class ShopModel(Base):
    __tablename__ = "shop"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    license_no: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    staff_members: Mapped[list["StaffModel"]] = relationship(back_populates="shop")
    exchanges: Mapped[list["ExchangeModel"]] = relationship(back_populates="shop")


class StaffModel(Base):
    __tablename__ = "staff"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    username: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    shop: Mapped["ShopModel"] = relationship(back_populates="staff_members")


class InstrumentModel(Base):
    __tablename__ = "instrument"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    serial_no: Mapped[str] = mapped_column(Text, nullable=False)
    make_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    calibration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    calibration_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class ShopPolicyModel(Base):
    __tablename__ = "shop_policy"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_deduction_bp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    xrf_max_variance_permille: Mapped[int] = mapped_column(BigInteger, nullable=False)
    scale_calibration_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_independent_purity_sources: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    day_close_max_variance_ug: Mapped[int] = mapped_column(
        BigInteger, default=100000, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class RateSnapshotModel(Base):
    __tablename__ = "rate_snapshot"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    rate_paise_per_g: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class ExchangeModel(Base):
    __tablename__ = "exchange"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    state: Mapped[str] = mapped_column(Text, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    customer_ref: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    shop: Mapped["ShopModel"] = relationship(back_populates="exchanges")
    readings: Mapped[list["ReadingModel"]] = relationship(back_populates="exchange")
    receipt: Mapped["ReceiptModel | None"] = relationship(back_populates="exchange", uselist=False)


class ReadingModel(Base):
    __tablename__ = "reading"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exchange.id"), nullable=False
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    value_int: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    tolerance_int: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("instrument.id"), nullable=True
    )
    point_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_kind: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_blob_sha256: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reading.id"), nullable=True
    )

    exchange: Mapped["ExchangeModel"] = relationship(back_populates="readings")


class WeightWitnessModel(Base):
    __tablename__ = "weight_witness"

    exchange_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exchange.id"), primary_key=True
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    customer_entry_mg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mode: Mapped[str] = mapped_column(Text, nullable=False)
    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    matched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ReceiptModel(Base):
    __tablename__ = "receipt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exchange.id"), nullable=False
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    receipt_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    canonical_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    supersedes_receipt_hash: Mapped[str | None] = mapped_column(
        Text, ForeignKey("receipt.receipt_hash"), nullable=True
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    exchange: Mapped["ExchangeModel"] = relationship(back_populates="receipt")


class AuditEventModel(Base):
    __tablename__ = "audit_event"

    seq: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    actor: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    object_type: Mapped[str] = mapped_column(Text, nullable=False)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    prev_hash: Mapped[str] = mapped_column(Text, nullable=False)
    this_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)


class GoldJournalEntryModel(Base):
    __tablename__ = "gold_journal_entry"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    exchange_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exchange.id"), nullable=True
    )
    receipt_hash: Mapped[str | None] = mapped_column(
        Text, ForeignKey("receipt.receipt_hash"), nullable=True
    )
    entry_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reverses_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gold_journal_entry.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    lines: Mapped[list["GoldJournalLineModel"]] = relationship(back_populates="entry")


class GoldJournalLineModel(Base):
    __tablename__ = "gold_journal_line"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gold_journal_entry.id"), nullable=False
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    account: Mapped[str] = mapped_column(Text, nullable=False)
    side: Mapped[str] = mapped_column(String(1), nullable=False)
    amount_ug: Mapped[int] = mapped_column(BigInteger, nullable=False)

    entry: Mapped["GoldJournalEntryModel"] = relationship(back_populates="lines")


class MoneyJournalEntryModel(Base):
    __tablename__ = "money_journal_entry"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    exchange_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exchange.id"), nullable=True
    )
    receipt_hash: Mapped[str | None] = mapped_column(
        Text, ForeignKey("receipt.receipt_hash"), nullable=True
    )
    entry_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reverses_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("money_journal_entry.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    lines: Mapped[list["MoneyJournalLineModel"]] = relationship(back_populates="entry")


class MoneyJournalLineModel(Base):
    __tablename__ = "money_journal_line"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("money_journal_entry.id"), nullable=False
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    account: Mapped[str] = mapped_column(Text, nullable=False)
    side: Mapped[str] = mapped_column(String(1), nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)

    entry: Mapped["MoneyJournalEntryModel"] = relationship(back_populates="lines")


class JobModel(Base):
    __tablename__ = "job"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="PENDING", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    run_after: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
