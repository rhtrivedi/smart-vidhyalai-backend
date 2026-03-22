from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.schemas import attendance as schemas
from app.crud import attendance as crud
from app.api import deps
from app.models.core import TenantUser
from datetime import date

router = APIRouter()


@router.post("/bulk", response_model=schemas.BulkAttendanceResponse)
def record_bulk_attendance(
    bulk_in: schemas.BulkAttendanceCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    High-Concurrency Endpoint: Records attendance for an entire classroom
    in a single database transaction.
    """
    return crud.create_bulk_attendance(
        db=db,
        bulk_in=bulk_in,
        tenant_id=tenant_context.tenant_id,
        user_id=tenant_context.user_id,  # Safely inject the logged-in teacher's ID
    )


@router.get("/daily-report", response_model=schemas.DailyAttendanceReportResponse)
def get_daily_attendance_report(
    class_id: UUID,
    report_date: date,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    Fetches a human-readable daily attendance report for a specific classroom.
    Example URL: /api/v1/attendance/daily-report?class_id=123...&report_date=2026-03-24
    """
    return crud.get_daily_class_report(
        db=db,
        class_id=class_id,
        query_date=report_date,
        tenant_id=tenant_context.tenant_id,
    )
