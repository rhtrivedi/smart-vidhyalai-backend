from pydantic import BaseModel
from uuid import UUID


class LoginRequest(BaseModel):
    # We allow logging in with either phone number or email, so we call it 'identifier'
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    role: str
    tenant_id: UUID
