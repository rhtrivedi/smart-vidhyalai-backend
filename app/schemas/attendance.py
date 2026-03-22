from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from uuid import UUID
from app.models.attendance import AttendanceStatus


# 1. Individual Student Record in the payload
class AttendanceRecordCreate(BaseModel):
    student_profile_id: UUID
    status: AttendanceStatus = (
        AttendanceStatus.PRESENT
    )  # Defaults to Present to save clicks!
    remarks: Optional[str] = None


# 2. The Master Bulk Payload
class BulkAttendanceCreate(BaseModel):
    class_id: UUID
    academic_year_id: UUID
    date: date
    records: List[AttendanceRecordCreate]  # The array of students


# 3. The Response
class BulkAttendanceResponse(BaseModel):
    message: str
    recorded_count: int


# --- REPORTING SCHEMAS ---


class DailyAttendanceReportItem(BaseModel):
    student_profile_id: UUID
    full_name: str
    enrollment_number: str
    status: AttendanceStatus
    remarks: Optional[str] = None


class DailyAttendanceReportResponse(BaseModel):
    class_id: UUID
    date: date
    total_students: int
    present_count: int
    absent_count: int
    records: List[DailyAttendanceReportItem]
