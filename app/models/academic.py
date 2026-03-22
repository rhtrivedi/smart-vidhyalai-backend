import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Import the Base class from your database setup
from app.core.database import Base

# --- ACADEMIC DATABASE TABLES ---


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name = Column(String, nullable=False)  # e.g., "2026-2027" or "Spring Crash Course"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(
        Boolean, default=True
    )  # Only one should be active at a time per tenant
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")


class ClassBatch(Base):
    """Represents a standard Class (e.g., Grade 10) or a dynamic Batch (e.g., Morning JEE)."""

    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    academic_year_id = Column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    name = Column(String, nullable=False)
    class_teacher_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Optional class teacher
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    academic_year = relationship("AcademicYear")
    class_teacher = relationship("User")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name = Column(String, nullable=False)  # e.g., "Physics"
    code = Column(String, nullable=False)  # e.g., "PHY-101"
    is_practical = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")


class ClassSubject(Base):
    """The Mapping Table: Connects a Subject to a Class, and assigns a specific Teacher."""

    __tablename__ = "class_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Who teaches this?
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    class_batch = relationship("ClassBatch")
    subject = relationship("Subject")
    teacher = relationship("User")


class StudentClassEnrollment(Base):
    """The Historical Ledger: Maps a student to a specific class for a specific year."""

    __tablename__ = "student_class_enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )

    # The Core Triad of Enrollment
    student_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False
    )
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    academic_year_id = Column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )

    # Specifics for this year
    roll_number = Column(Integer, nullable=True)
    enrollment_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    student_profile = relationship("StudentProfile")
    class_batch = relationship("ClassBatch")
    academic_year = relationship("AcademicYear")
