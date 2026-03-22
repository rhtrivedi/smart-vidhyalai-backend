from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models.core import TenantTier, TenantStatus

# --- TENANT SCHEMAS ---

# 1. Base Schema (Shared properties)
class TenantBase(BaseModel):
    name: str
    subdomain: str

# 2. Create Schema (What the frontend sends us)
class TenantCreate(TenantBase):
    subscription_tier: TenantTier = TenantTier.BASIC

# 3. Response Schema (What we send BACK to the frontend)
class TenantResponse(TenantBase):
    id: UUID
    status: TenantStatus
    created_at: datetime

    # This tells Pydantic to seamlessly read data from our SQLAlchemy database model
    model_config = ConfigDict(from_attributes=True)