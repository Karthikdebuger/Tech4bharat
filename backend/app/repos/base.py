"""Base repository with mandatory TenantContext enforcement.

Per §7.2 Rule 2:
The repository layer strictly requires a TenantContext; no repository method
accepts a bare ID without a tenant context.
"""

from dataclasses import dataclass
import uuid
from sqlalchemy.orm import Session

@dataclass(frozen=True, slots=True)
class TenantContext:
    shop_id: uuid.UUID
    staff_id: uuid.UUID | None = None
    role: str | None = None

class BaseTenantRepository:
    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.shop_id = tenant.shop_id
