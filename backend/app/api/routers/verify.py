"""Public verification API route.

Per §7.3:
- Public GET /verify/{hash}: 64-character hex validation.
- Minimal response without customer PII.
- Fast, unauthenticated lookup.
"""

import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.api.schemas import PublicVerifyResponse
from app.models.entities import ReceiptModel

router = APIRouter(prefix="/api/verify", tags=["verification"])
HEX_64_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

@router.get("/{receipt_hash}", response_model=PublicVerifyResponse)
def verify_receipt_public(
    receipt_hash: str,
    db: Session = Depends(get_db),
) -> PublicVerifyResponse:
    if not HEX_64_REGEX.match(receipt_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid receipt hash format. Expected 64-character hex SHA-256.",
        )

    stmt = select(ReceiptModel).where(ReceiptModel.receipt_hash == receipt_hash.lower())
    receipt = db.execute(stmt).scalar_one_or_none()

    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt record not found. Hash does not match any registered transaction.",
        )

    payload = receipt.canonical_payload
    weight = payload["weight"]
    purity = payload["purity"]
    val = payload["valuation"]
    integrity = payload["integrity"]

    return PublicVerifyResponse(
        receipt_hash=receipt.receipt_hash,
        valid=True,
        is_demo=receipt.is_demo,
        timestamp_utc=payload["timestamp_utc"],
        weight_net_formatted=weight.get("formatted_net", f"{weight['net_mg'] / 1000:.3f} g"),
        purity_nominal_permille=purity["nominal_permille"],
        settlement_inr_formatted=val.get("formatted_settlement", f"₹{val['settlement_paise'] / 100:,.2f}"),
        integrity_status=integrity["aggregate_outcome"],
    )
