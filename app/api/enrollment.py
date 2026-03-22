from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import enrollment as schemas
from app.crud import enrollment as crud
from app.api import deps
from app.models.core import TenantUser

router = APIRouter()


@router.post("/student", response_model=schemas.StudentEnrollmentResponse)
def enroll_new_student(
    enrollment_data: schemas.StudentEnrollmentCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    God-Level Enrollment API: Creates the Student, the Parent,
    generates their compliant profiles, and links them cryptographically.
    """
    return crud.enroll_student_with_guardian(
        db=db, enrollment_data=enrollment_data, tenant_id=tenant_context.tenant_id
    )
