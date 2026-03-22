from sqlalchemy.orm import Session
from app.models import core as models
from app.schemas import user as schemas
from app.core.security import get_password_hash

def create_tenant_user(db: Session, user: schemas.UserCreate):
    # 1. Hash the password securely
    hashed_pwd = get_password_hash(user.password)

    # 2. Prepare the primary User record
    db_user = models.User(
        phone_number=user.phone_number,
        email=user.email,
        password_hash=hashed_pwd,
        full_name=user.full_name
    )
    
    db.add(db_user)
    
    # PRO-TIP: We use flush() instead of commit() here. 
    # This pushes the user to the DB to generate their UUID, 
    # but keeps the transaction open in case the next step fails.
    db.flush() 

    # 3. Create the RBAC link (TenantUser) binding them to the school
    db_tenant_user = models.TenantUser(
        tenant_id=user.tenant_id,
        user_id=db_user.id,
        role=user.role
    )
    
    db.add(db_tenant_user)
    
    # 4. Now we permanently commit BOTH actions together
    db.commit()
    db.refresh(db_user)
    
    return db_user