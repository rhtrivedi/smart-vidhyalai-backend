from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import our custom modules
from app.core.database import get_db
from app.schemas import core as schemas
from app.crud import core as crud

# Create the router instance
router = APIRouter()

@router.post("/", response_model=schemas.TenantResponse)
def create_new_tenant(
    tenant: schemas.TenantCreate, 
    db: Session = Depends(get_db) # This automatically opens and closes the DB connection
):
    """
    Register a new institution (Tenant) into Smart Vidhyalai.
    """
    # Later, we will add logic here to check if the subdomain already exists.
    # For now, we directly pass the validated data to our CRUD function.
    created_tenant = crud.create_tenant(db=db, tenant=tenant)
    return created_tenant