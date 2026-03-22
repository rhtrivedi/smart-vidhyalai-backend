from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import date
from typing import Optional
from app.models.profiles import GuardianRelationship


# 1. The Parent/Guardian Sub-Schema
class GuardianCreate(BaseModel):
    phone_number: str
    email: Optional[EmailStr] = None
    full_name: str
    password: str  # Initial password for the parent portal
    relationship: GuardianRelationship
    occupation: Optional[str] = None
    annual_income: Optional[str] = None


# 2. The Master Student Enrollment Schema
class StudentEnrollmentCreate(BaseModel):
    # Student Account Core
    phone_number: Optional[str] = None  # Minors might not have phones
    email: Optional[EmailStr] = None
    full_name: str
    password: str  # Initial password for the student portal

    # Student Academic Profile
    enrollment_number: str
    date_of_birth: date
    gender: str
    blood_group: Optional[str] = None

    # Compliance Details
    aadhaar_number: Optional[str] = None
    apaar_id: Optional[str] = None
    caste_category: Optional[str] = None
    religion: Optional[str] = None
    mother_tongue: Optional[str] = None
    is_cwsn: bool = False
    residential_address: Optional[str] = None

    # The Nested Parent Data
    guardian: GuardianCreate


# 3. The Response Schema
class StudentEnrollmentResponse(BaseModel):
    student_user_id: UUID
    student_profile_id: UUID
    parent_user_id: UUID
    message: str = "Student and Guardian successfully enrolled and linked."
