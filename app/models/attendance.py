import uuid
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship as orm_relationship

from app.core.database import Base


# --- ENUMS ---
class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    HALF_DAY = "HALF_DAY"
    ON_LEAVE = "ON_LEAVE"


# --- DATABASE TABLES ---
class AttendanceRecord(Base):
    """The High-Concurrency Daily Ledger for Student Attendance."""

    __tablename__ = "attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )

    # Where and When
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    academic_year_id = Column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    date = Column(Date, nullable=False, default=date.today)

    # Who
    student_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False
    )

    # What
    status = Column(
        SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT
    )
    remarks = Column(Text, nullable=True)  # e.g., "Doctor's appointment"

    # Audit Trail: Who pressed the submit button?
    recorded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- THE GOD-LEVEL CONSTRAINT ---
    # A student can only have ONE attendance record per class, per day.
    __table_args__ = (
        UniqueConstraint(
            "student_profile_id", "class_id", "date", name="uq_student_class_date"
        ),
    )

    # Relationships
    tenant = orm_relationship("Tenant")
    class_batch = orm_relationship("ClassBatch")
    academic_year = orm_relationship("AcademicYear")
    student_profile = orm_relationship("StudentProfile")
    recorded_by = orm_relationship("User")
