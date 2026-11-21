"""FastAPI dependencies: Database session and TenantContext injection."""

import os
from typing import Generator
import uuid
from fastapi import Header, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.repos.base import TenantContext

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://goldtrust:goldtrust_dev_secret@localhost:5432/goldtrust",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hardcoded demo tenant fallback for local development / testing
DEFAULT_DEMO_SHOP_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
DEFAULT_DEMO_STAFF_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")

def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tenant_context(
    x_shop_id: str | None = Header(None, alias="X-Shop-ID"),
    x_staff_id: str | None = Header(None, alias="X-Staff-ID"),
) -> TenantContext:
    """Extract and validate TenantContext from request headers."""
    try:
        shop_id = uuid.UUID(x_shop_id) if x_shop_id else DEFAULT_DEMO_SHOP_ID
        staff_id = uuid.UUID(x_staff_id) if x_staff_id else DEFAULT_DEMO_STAFF_ID
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID in tenant headers: {e}",
        ) from e

    return TenantContext(
        shop_id=shop_id,
        staff_id=staff_id,
        role="APPRAISER",
    )
