from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import academic as schemas
from app.crud import academic as crud
from app.api import deps
from app.models.core import TenantUser

router = APIRouter()


@router.post("/years", response_model=schemas.AcademicYearResponse)
def create_new_academic_year(
    year_in: schemas.AcademicYearCreate,
    db: Session = Depends(get_db),
    # This single line of code secures the entire route with JWT + Multi-Tenancy checks
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    Creates a new Academic Year.
    Secured: Automatically bound to the authenticated user's institution.
    """
    return crud.create_academic_year(
        db=db, year_in=year_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/classes", response_model=schemas.ClassBatchResponse)
def create_new_class_batch(
    batch_in: schemas.ClassBatchCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """Creates a new Class or Batch within a specific Academic Year."""
    return crud.create_class_batch(
        db=db, batch_in=batch_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/subjects", response_model=schemas.SubjectResponse)
def create_new_subject(
    subject_in: schemas.SubjectCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """Creates a new Subject blueprint for the institution."""
    return crud.create_subject(
        db=db, subject_in=subject_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/class-subjects", response_model=schemas.ClassSubjectResponse)
def assign_subject_to_class(
    mapping_in: schemas.ClassSubjectCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    Maps a Subject to a specific Class/Batch and assigns a Subject Teacher.
    """
    return crud.create_class_subject_mapping(
        db=db, mapping_in=mapping_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/enrollments", response_model=schemas.StudentClassEnrollmentResponse)
def assign_student_to_class(
    enrollment_in: schemas.StudentClassEnrollmentCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    The Historical Ledger: Assigns a student to a specific physical classroom/batch
    for a given academic year.
    """
    return crud.enroll_student_in_class(
        db=db, enrollment_in=enrollment_in, tenant_id=tenant_context.tenant_id
    )
