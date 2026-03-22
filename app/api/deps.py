from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.core import User, TenantUser

# This tells FastAPI to look for an "Authorization: Bearer <token>" header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Validates the JWT token from the incoming request and returns the current user.
    """
    token = credentials.credentials

    try:
        # 1. Decrypt the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure.",
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    # 2. Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return user


def get_current_tenant_user(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> TenantUser:
    """
    Fetches the active Tenant mapping for the currently authenticated user.
    This guarantees that the user is actively employed/enrolled in a valid school.
    """
    tenant_user = (
        db.query(TenantUser)
        .filter(TenantUser.user_id == current_user.id, TenantUser.is_active == True)
        .first()
    )

    if not tenant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to any active institution.",
        )

    return tenant_user
