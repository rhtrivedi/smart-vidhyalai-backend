from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from uuid import UUID
from typing import Optional

# --- ACADEMIC YEAR SCHEMAS ---


class AcademicYearCreate(BaseModel):
    name: str  # e.g., "2026-2027" or "Summer Crash Course 2026"
    start_date: date
    end_date: date


class AcademicYearResponse(AcademicYearCreate):
    id: UUID
    tenant_id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# --- CLASS BATCH SCHEMAS ---


class ClassBatchCreate(BaseModel):
    academic_year_id: UUID
    name: str  # e.g., "Grade 10 - Section A"
    class_teacher_id: Optional[UUID] = None


class ClassBatchResponse(ClassBatchCreate):
    id: UUID
    tenant_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- SUBJECT SCHEMAS ---


class SubjectCreate(BaseModel):
    name: str  # e.g., "Advanced Physics"
    code: str  # e.g., "PHY-201"
    is_practical: bool = False


class SubjectResponse(SubjectCreate):
    id: UUID
    tenant_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- CLASS-SUBJECT MAPPING SCHEMAS ---


class ClassSubjectCreate(BaseModel):
    class_id: UUID
    subject_id: UUID
    teacher_id: Optional[UUID] = None  # The specific user teaching this subject


class ClassSubjectResponse(ClassSubjectCreate):
    id: UUID
    tenant_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- ROSTER ENROLLMENT SCHEMAS ---


class StudentClassEnrollmentCreate(BaseModel):
    student_profile_id: UUID
    class_id: UUID
    academic_year_id: UUID
    roll_number: Optional[int] = None


class StudentClassEnrollmentResponse(StudentClassEnrollmentCreate):
    id: UUID
    tenant_id: UUID
    enrollment_date: datetime

    model_config = ConfigDict(from_attributes=True)
