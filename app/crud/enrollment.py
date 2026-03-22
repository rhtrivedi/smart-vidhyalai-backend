from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models import core as core_models
from app.models import profiles as profile_models
from app.schemas import enrollment as schemas
from app.core.security import get_password_hash


def enroll_student_with_guardian(
    db: Session, enrollment_data: schemas.StudentEnrollmentCreate, tenant_id: UUID
):
    try:
        # --- 1. HANDLE THE PARENT/GUARDIAN ---
        # Check if parent already exists globally
        parent_user = (
            db.query(core_models.User)
            .filter(
                core_models.User.phone_number == enrollment_data.guardian.phone_number
            )
            .first()
        )

        if not parent_user:
            # Create new parent user
            parent_user = core_models.User(
                phone_number=enrollment_data.guardian.phone_number,
                email=enrollment_data.guardian.email,
                full_name=enrollment_data.guardian.full_name,
                password_hash=get_password_hash(enrollment_data.guardian.password),
            )
            db.add(parent_user)
            db.flush()  # Get the new Parent ID immediately

            # Bind Parent to the School
            parent_tenant_link = core_models.TenantUser(
                tenant_id=tenant_id,
                user_id=parent_user.id,
                role=core_models.RoleEnum.PARENT,
            )
            db.add(parent_tenant_link)
            db.flush()

        # --- 2. HANDLE THE STUDENT ---
        student_user = core_models.User(
            phone_number=enrollment_data.phone_number
            or f"STU-{enrollment_data.enrollment_number}",  # Fallback if no phone
            email=enrollment_data.email,
            full_name=enrollment_data.full_name,
            password_hash=get_password_hash(enrollment_data.password),
        )
        db.add(student_user)
        db.flush()

        # Bind Student to the School
        student_tenant_link = core_models.TenantUser(
            tenant_id=tenant_id,
            user_id=student_user.id,
            role=core_models.RoleEnum.STUDENT,
        )
        db.add(student_tenant_link)
        db.flush()

        # --- 3. CREATE THE STUDENT PROFILE (Compliance Data) ---
        student_profile = profile_models.StudentProfile(
            tenant_user_id=student_tenant_link.id,
            enrollment_number=enrollment_data.enrollment_number,
            date_of_birth=enrollment_data.date_of_birth,
            gender=enrollment_data.gender,
            blood_group=enrollment_data.blood_group,
            aadhaar_number=enrollment_data.aadhaar_number,
            apaar_id=enrollment_data.apaar_id,
            caste_category=enrollment_data.caste_category,
            religion=enrollment_data.religion,
            mother_tongue=enrollment_data.mother_tongue,
            is_cwsn=enrollment_data.is_cwsn,
            residential_address=enrollment_data.residential_address,
        )
        db.add(student_profile)
        db.flush()

        # --- 4. CREATE THE MAGICAL LINK (Student <-> Parent) ---
        guardian_mapping = profile_models.StudentGuardian(
            tenant_id=tenant_id,
            student_profile_id=student_profile.id,
            parent_user_id=parent_user.id,
            relationship=enrollment_data.guardian.relationship,
            occupation=enrollment_data.guardian.occupation,
            annual_income=enrollment_data.guardian.annual_income,
        )
        db.add(guardian_mapping)

        # --- 5. COMMIT EVERYTHING ---
        db.commit()

        return schemas.StudentEnrollmentResponse(
            student_user_id=student_user.id,
            student_profile_id=student_profile.id,
            parent_user_id=parent_user.id,
        )

    except Exception as e:
        db.rollback()  # If ANYTHING fails, undo all database changes instantly
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Enrollment failed: {str(e)}",
        )
