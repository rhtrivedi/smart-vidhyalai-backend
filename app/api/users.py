from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import user as schemas
from app.crud import user as crud
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.UserResponse)
def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user and safely binds them to a specific Tenant (School).
    """
    return crud.create_tenant_user(db=db, user=user)


@router.get("/me", response_model=schemas.UserResponse)
def read_current_user_profile(current_user=Depends(deps.get_current_user)):
    """
    PROTECTED ROUTE: Returns the profile data of the currently logged-in user.
    Requires a valid JWT token.
    """
    return current_user
