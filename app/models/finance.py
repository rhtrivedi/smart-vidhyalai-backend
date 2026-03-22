import uuid
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Date,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship as orm_relationship

from app.core.database import Base


# --- ENUMS ---
class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHEQUE = "CHEQUE"


class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


# --- DATABASE TABLES ---


class FeeCategory(Base):
    """The Master Blueprint of Charges (e.g., 'Tuition Fee', 'Transport Fee')."""

    __tablename__ = "fee_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = orm_relationship("Tenant")


class FeeStructure(Base):
    """The Rules Engine: Maps a Category to a Class and Year with a specific amount."""

    __tablename__ = "fee_structures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("fee_categories.id"), nullable=False
    )
    academic_year_id = Column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    class_id = Column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True
    )  # If null, applies to whole school

    amount = Column(Float, nullable=False)  # e.g., 45000.00
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = orm_relationship("Tenant")
    category = orm_relationship("FeeCategory")
    academic_year = orm_relationship("AcademicYear")
    class_batch = orm_relationship("ClassBatch")


class StudentInvoice(Base):
    """The Bill: What a specific student owes."""

    __tablename__ = "student_invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    student_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False
    )
    fee_structure_id = Column(
        UUID(as_uuid=True), ForeignKey("fee_structures.id"), nullable=False
    )

    # Financial Tracking
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    due_date = Column(Date, nullable=False)
    status = Column(
        SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = orm_relationship("Tenant")
    student_profile = orm_relationship("StudentProfile")
    fee_structure = orm_relationship("FeeStructure")


class PaymentReceipt(Base):
    """The Immutable Ledger: The actual money received."""

    __tablename__ = "payment_receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    invoice_id = Column(
        UUID(as_uuid=True), ForeignKey("student_invoices.id"), nullable=False
    )

    amount_paid = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)

    # Crucial for UPI / Bank Transfers
    transaction_reference = Column(String, nullable=True)

    # Audit Trail: Who collected the money?
    recorded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    tenant = orm_relationship("Tenant")
    invoice = orm_relationship("StudentInvoice")
    recorded_by = orm_relationship("User")
