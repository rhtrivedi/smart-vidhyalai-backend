import uuid
from datetime import datetime
import enum
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Date,
    Boolean,
    Text,
    Enum as SQLEnum,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship as orm_relationship

from app.core.database import Base


# --- ENUMS ---
class GuardianRelationship(str, enum.Enum):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    LOCAL_GUARDIAN = "LOCAL_GUARDIAN"
    OTHER = "OTHER"


# --- DATABASE TABLES ---


class StudentProfile(Base):
    """Holds specific academic identity details for a Student."""

    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_user_id = Column(
        UUID(as_uuid=True), ForeignKey("tenant_users.id"), unique=True, nullable=False
    )

    # Academic & Core
    enrollment_number = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=False)  # e.g., "MALE", "FEMALE", "OTHER"
    blood_group = Column(String, nullable=True)
    admission_date = Column(Date, default=datetime.utcnow)

    # UDISE+ & CBSE Indian Compliance Fields
    aadhaar_number = Column(String, unique=True, nullable=True)  # 12 digit
    apaar_id = Column(String, unique=True, nullable=True)  # CBSE Mandate 2025-26
    caste_category = Column(String, nullable=True)  # "General", "SC", "ST", "OBC"
    religion = Column(String, nullable=True)
    mother_tongue = Column(String, nullable=True)
    is_cwsn = Column(Boolean, default=False)  # Children with Special Needs
    residential_address = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant_user = orm_relationship("TenantUser")


class StaffProfile(Base):
    """Holds specific employment details for Teachers, Admins, and Support Staff."""

    __tablename__ = "staff_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_user_id = Column(
        UUID(as_uuid=True), ForeignKey("tenant_users.id"), unique=True, nullable=False
    )
    employee_id = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    hire_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant_user = orm_relationship("TenantUser")


class StudentGuardian(Base):
    """The Mapping Engine: Connects one Parent (User) to multiple Students."""

    __tablename__ = "student_guardians"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    student_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False
    )
    parent_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    relationship = Column(SQLEnum(GuardianRelationship), nullable=False)
    emergency_contact_priority = Column(Integer, default=1)

    # CBSE / Indian School Requirements
    occupation = Column(String, nullable=True)
    annual_income = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = orm_relationship("Tenant")
    student_profile = orm_relationship("StudentProfile")
    parent_user = orm_relationship("User")
