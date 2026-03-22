from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import Optional
from app.models.core import RoleEnum

class UserCreate(BaseModel):
    phone_number: str
    email: Optional[EmailStr] = None
    password: str
    full_name: str
    tenant_id: UUID  # The exact ID of the school they belong to
    role: RoleEnum   # e.g., 'INSTITUTE_ADMIN'

class UserResponse(BaseModel):
    id: UUID
    full_name: str
    phone_number: str
    
    model_config = ConfigDict(from_attributes=True)