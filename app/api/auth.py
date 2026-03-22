from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.core import User, TenantUser
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a secure JWT access token.
    """
    # 1. Find the user by phone number OR email
    user = (
        db.query(User)
        .filter(
            (User.phone_number == login_data.identifier)
            | (User.email == login_data.identifier)
        )
        .first()
    )

    # 2. If user doesn't exist, or password doesn't match, reject them.
    # We use a generic error message so hackers don't know if the email exists.
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Find their active role and tenant (School) binding
    tenant_user_link = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == user.id, TenantUser.is_active == True)
        .first()
    )

    if not tenant_user_link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have an active role in any institution.",
        )

    # 4. Generate the JWT Payload (The data hidden securely inside the token)
    token_payload = {
        "sub": str(user.id),  # Subject (User ID)
        "tenant_id": str(tenant_user_link.tenant_id),  # Their school ID
        "role": tenant_user_link.role,  # Their permission level
    }

    # 5. Create the token
    access_token = create_access_token(data=token_payload)

    # 6. Return the full response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": tenant_user_link.role,
        "tenant_id": tenant_user_link.tenant_id,
    }
