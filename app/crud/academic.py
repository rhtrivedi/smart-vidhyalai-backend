from sqlalchemy.orm import Session
from app.models import academic as models
from app.schemas import academic as schemas
from uuid import UUID


def create_academic_year(
    db: Session, year_in: schemas.AcademicYearCreate, tenant_id: UUID
):
    db_year = models.AcademicYear(
        tenant_id=tenant_id,  # Injected securely by the backend
        name=year_in.name,
        start_date=year_in.start_date,
        end_date=year_in.end_date,
    )
    db.add(db_year)
    db.commit()
    db.refresh(db_year)
    return db_year


def create_class_batch(
    db: Session, batch_in: schemas.ClassBatchCreate, tenant_id: UUID
):
    db_batch = models.ClassBatch(
        tenant_id=tenant_id,  # Injected securely by the backend
        academic_year_id=batch_in.academic_year_id,
        name=batch_in.name,
        class_teacher_id=batch_in.class_teacher_id,
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def create_subject(db: Session, subject_in: schemas.SubjectCreate, tenant_id: UUID):
    db_subject = models.Subject(
        tenant_id=tenant_id,
        name=subject_in.name,
        code=subject_in.code,
        is_practical=subject_in.is_practical,
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def create_class_subject_mapping(
    db: Session, mapping_in: schemas.ClassSubjectCreate, tenant_id: UUID
):
    db_mapping = models.ClassSubject(
        tenant_id=tenant_id,
        class_id=mapping_in.class_id,
        subject_id=mapping_in.subject_id,
        teacher_id=mapping_in.teacher_id,
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


def enroll_student_in_class(
    db: Session, enrollment_in: schemas.StudentClassEnrollmentCreate, tenant_id: UUID
):
    db_enrollment = models.StudentClassEnrollment(
        tenant_id=tenant_id,
        student_profile_id=enrollment_in.student_profile_id,
        class_id=enrollment_in.class_id,
        academic_year_id=enrollment_in.academic_year_id,
        roll_number=enrollment_in.roll_number,
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment
