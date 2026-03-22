from sqlalchemy.orm import Session
from app.models import core as models
from app.schemas import core as schemas

def create_tenant(db: Session, tenant: schemas.TenantCreate):
    # 1. Map the incoming Pydantic schema to our SQLAlchemy database model
    db_tenant = models.Tenant(
        name=tenant.name,
        subdomain=tenant.subdomain,
        subscription_tier=tenant.subscription_tier
    )
    
    # 2. Add it to the database transaction
    db.add(db_tenant)
    
    # 3. Save it permanently
    db.commit()
    
    # 4. Refresh to get the auto-generated UUID and timestamps
    db.refresh(db_tenant)
    
    return db_tenant