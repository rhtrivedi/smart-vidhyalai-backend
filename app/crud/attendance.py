from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models import attendance as models
from app.schemas import attendance as schemas

from app.models import core as core_models
from app.models import profiles as profile_models
from datetime import date


def create_bulk_attendance(
    db: Session, bulk_in: schemas.BulkAttendanceCreate, tenant_id: UUID, user_id: UUID
):
    try:
        db_records = []
        for record_in in bulk_in.records:
            db_record = models.AttendanceRecord(
                tenant_id=tenant_id,
                class_id=bulk_in.class_id,
                academic_year_id=bulk_in.academic_year_id,
                date=bulk_in.date,
                student_profile_id=record_in.student_profile_id,
                status=record_in.status,
                remarks=record_in.remarks,
                recorded_by_id=user_id,  # Automatically tracks which teacher submitted it
            )
            db_records.append(db_record)
            db.add(db_record)

        # ONE single hit to the database!
        db.commit()

        return schemas.BulkAttendanceResponse(
            message="Bulk attendance successfully recorded.",
            recorded_count=len(db_records),
        )

    except IntegrityError:
        # The God-Level safety net catches duplicates
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate attendance detected. One or more students already have a record for this class and date.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


def get_daily_class_report(
    db: Session, class_id: UUID, query_date: date, tenant_id: UUID
):
    # Perform a 4-table JOIN to get the exact human-readable data
    query_results = (
        db.query(
            models.AttendanceRecord.student_profile_id,
            models.AttendanceRecord.status,
            models.AttendanceRecord.remarks,
            core_models.User.full_name,
            profile_models.StudentProfile.enrollment_number,
        )
        .join(
            profile_models.StudentProfile,
            models.AttendanceRecord.student_profile_id
            == profile_models.StudentProfile.id,
        )
        .join(
            core_models.TenantUser,
            profile_models.StudentProfile.tenant_user_id == core_models.TenantUser.id,
        )
        .join(core_models.User, core_models.TenantUser.user_id == core_models.User.id)
        .filter(
            models.AttendanceRecord.tenant_id == tenant_id,
            models.AttendanceRecord.class_id == class_id,
            models.AttendanceRecord.date == query_date,
        )
        .all()
    )

    # Process the results for the frontend
    report_items = []
    present_count = 0
    absent_count = 0

    for row in query_results:
        report_items.append(
            schemas.DailyAttendanceReportItem(
                student_profile_id=row.student_profile_id,
                full_name=row.full_name,
                enrollment_number=row.enrollment_number,
                status=row.status,
                remarks=row.remarks,
            )
        )

        if row.status == models.AttendanceStatus.PRESENT:
            present_count += 1
        elif row.status == models.AttendanceStatus.ABSENT:
            absent_count += 1

    return schemas.DailyAttendanceReportResponse(
        class_id=class_id,
        date=query_date,
        total_students=len(report_items),
        present_count=present_count,
        absent_count=absent_count,
        records=report_items,
    )
