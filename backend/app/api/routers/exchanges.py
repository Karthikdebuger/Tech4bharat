"""FastAPI router for exchange lifecycle and appraisal workflow."""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_tenant_context
from app.api.schemas import (
    AddReadingRequest,
    CosignRequest,
    CreateExchangeRequest,
    CreateExchangeResponse,
    GenerateQuoteRequest,
    LockIntakeRequest,
    SettleRequest,
    SubmitWitnessRequest,
    WitnessResponse,
)
from app.domain.rules import ShopPolicy
from app.domain.units import Bp, Permille, Ug
from app.repos.base import TenantContext
from app.repos.exchange_repo import ExchangeRepository
from app.services.exchange_service import ExchangeService
from app.services.explainer import generate_receipt_explanation
from app.services.settlement_service import SettlementService

router = APIRouter(prefix="/api/exchanges", tags=["exchanges"])
SERVER_SECRET = os.getenv("SECRET_KEY", "dev_secret_key_32_bytes_gold_trust").encode("utf-8")

@router.post("", response_model=CreateExchangeResponse, status_code=status.HTTP_201_CREATED)
def create_exchange(
    req: CreateExchangeRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CreateExchangeResponse:
    svc = ExchangeService(db, SERVER_SECRET)
    exchange = svc.create_exchange(
        tenant=tenant,
        customer_phone_or_id=req.customer_phone_or_id,
        is_demo=req.is_demo,
    )
    db.commit()
    return CreateExchangeResponse(
        id=exchange.id,
        shop_id=exchange.shop_id,
        state=exchange.state,
        is_demo=exchange.is_demo,
        customer_ref=exchange.customer_ref,
    )

@router.post("/{exchange_id}/intake")
def lock_intake(
    exchange_id: uuid.UUID,
    req: LockIntakeRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, object]:
    svc = ExchangeService(db, SERVER_SECRET)
    exchange = svc.lock_intake(
        tenant=tenant,
        exchange_id=exchange_id,
        gross_mg=req.gross_mg,
        stones_mg=req.stones_mg,
        instrument_id=req.instrument_id,
    )
    db.commit()
    return {"id": exchange.id, "state": exchange.state}

@router.post("/{exchange_id}/witness", response_model=WitnessResponse)
def submit_witness(
    exchange_id: uuid.UUID,
    req: SubmitWitnessRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> WitnessResponse:
    svc = ExchangeService(db, SERVER_SECRET)
    matched = svc.submit_weight_witness(
        tenant=tenant,
        exchange_id=exchange_id,
        customer_mg=req.customer_entry_mg,
        mode=req.mode,
    )
    db.commit()
    return WitnessResponse(matched=matched, customer_entry_mg=req.customer_entry_mg)

@router.post("/{exchange_id}/readings")
def add_reading(
    exchange_id: uuid.UUID,
    req: AddReadingRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, object]:
    repo = ExchangeRepository(db, tenant)
    reading = repo.add_reading(
        exchange_id=exchange_id,
        kind=req.kind,
        value_int=req.value_int,
        unit="permille",
        tolerance_int=req.tolerance_int,
        instrument_id=req.instrument_id,
        point_index=req.point_index,
        evidence_blob_sha256=req.evidence_blob_sha256,
    )
    db.commit()
    return {"id": reading.id, "kind": reading.kind, "value_int": reading.value_int}

@router.post("/{exchange_id}/evaluate")
def evaluate_exchange(
    exchange_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, object]:
    svc = ExchangeService(db, SERVER_SECRET)
    policy = ShopPolicy(
        max_deduction_bp=Bp(300),
        xrf_max_variance_permille=Permille(15),
        scale_calibration_required=True,
        min_independent_purity_sources=1,  # lenient for initial testing
        day_close_max_variance_ug=Ug(100_000),
    )
    res = svc.evaluate_integrity(tenant, exchange_id, policy)
    db.commit()
    return res

@router.post("/{exchange_id}/quote")
def generate_quote(
    exchange_id: uuid.UUID,
    req: GenerateQuoteRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, object]:
    svc = ExchangeService(db, SERVER_SECRET)
    res = svc.generate_quote(
        tenant=tenant,
        exchange_id=exchange_id,
        nominal_permille=req.nominal_permille,
        tolerance_permille=req.tolerance_permille,
        deduction_bp=req.deduction_bp,
        rate_paise_per_g=req.rate_paise_per_g,
    )
    db.commit()
    return res

@router.post("/{exchange_id}/cosign")
def cosign_exchange(
    exchange_id: uuid.UUID,
    req: CosignRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, object]:
    svc = SettlementService(db)
    receipt = svc.cosign_exchange(
        tenant=tenant,
        exchange_id=exchange_id,
        receipt_dict=req.receipt,
        staff_approved_hash=req.staff_approved_hash,
        customer_approved_hash=req.customer_approved_hash,
    )
    db.commit()
    return {"receipt_hash": receipt.receipt_hash, "created_at": receipt.created_at.isoformat()}

@router.post("/{exchange_id}/settle")
def settle_exchange(
    exchange_id: uuid.UUID,
    req: SettleRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, object]:
    svc = SettlementService(db)
    res = svc.execute_settlement(
        tenant=tenant,
        exchange_id=exchange_id,
        payment_method=req.payment_method,
    )
    db.commit()
    return res

@router.get("/{exchange_id}/explain")
def explain_receipt(
    exchange_id: uuid.UUID,
    lang: str = Query("en", pattern="^(en|ta)$"),
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[dict[str, str]]:
    repo = ExchangeRepository(db, tenant)
    exchange = repo.get_exchange(exchange_id)
    if not exchange or not exchange.receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finalized receipt not found for this exchange",
        )
    return generate_receipt_explanation(exchange.receipt.canonical_payload, lang=lang)
