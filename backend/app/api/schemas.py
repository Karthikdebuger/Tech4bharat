"""Pydantic v2 request/response schemas for Gold Trust AI HTTP APIs."""

from typing import Any
import uuid
from pydantic import BaseModel, Field

class CreateExchangeRequest(BaseModel):
    customer_phone_or_id: str = Field(..., min_length=4, max_length=50)
    is_demo: bool = False

class CreateExchangeResponse(BaseModel):
    id: uuid.UUID
    shop_id: uuid.UUID
    state: str
    is_demo: bool
    customer_ref: str

class LockIntakeRequest(BaseModel):
    gross_mg: int = Field(..., ge=1, le=1_000_000_000)
    stones_mg: int = Field(0, ge=0, le=1_000_000_000)
    instrument_id: uuid.UUID | None = None

class SubmitWitnessRequest(BaseModel):
    customer_entry_mg: int = Field(..., ge=0)
    mode: str = Field("OWN_DEVICE", pattern="^(OWN_DEVICE|ASSISTED)$")

class WitnessResponse(BaseModel):
    matched: bool
    customer_entry_mg: int

class AddReadingRequest(BaseModel):
    kind: str = Field(..., pattern="^(XRF_POINT|KARAT_METER|TOUCHSTONE_RANGE|ASSAY)$")
    value_int: int = Field(..., ge=0, le=1000)
    tolerance_int: int = Field(0, ge=0, le=100)
    instrument_id: uuid.UUID | None = None
    point_index: int = Field(1, ge=1)
    evidence_blob_sha256: str | None = None

class GenerateQuoteRequest(BaseModel):
    nominal_permille: int = Field(..., ge=0, le=1000)
    tolerance_permille: int = Field(10, ge=0, le=100)
    deduction_bp: int = Field(..., ge=0, le=10000)
    rate_paise_per_g: int = Field(..., gt=0)

class CosignRequest(BaseModel):
    staff_approved_hash: str = Field(..., min_length=64, max_length=64)
    customer_approved_hash: str = Field(..., min_length=64, max_length=64)
    receipt: dict[str, Any]

class SettleRequest(BaseModel):
    payment_method: str = Field("Cash", pattern="^(Cash|Bank|UPI|NEFT)$")

class PublicVerifyResponse(BaseModel):
    receipt_hash: str
    valid: bool
    is_demo: bool
    timestamp_utc: str
    weight_net_formatted: str
    purity_nominal_permille: int
    settlement_inr_formatted: str
    integrity_status: str
