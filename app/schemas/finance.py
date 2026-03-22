from datetime import date
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.models.finance import InvoiceStatus, PaymentMethod

# --- FEE CATEGORY SCHEMAS ---


class FeeCategoryCreate(BaseModel):
    name: str  # e.g., "Tuition Fee", "Transport Fee"
    description: Optional[str] = None


class FeeCategoryResponse(FeeCategoryCreate):
    id: UUID
    tenant_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- FEE STRUCTURE SCHEMAS ---


class FeeStructureCreate(BaseModel):
    category_id: UUID
    academic_year_id: UUID
    class_id: Optional[UUID] = (
        None  # If null, this fee applies to every student in the school
    )
    amount: float


class FeeStructureResponse(FeeStructureCreate):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- INVOICE SCHEMAS ---


class StudentInvoiceCreate(BaseModel):
    student_profile_id: UUID
    fee_structure_id: UUID
    due_date: date


class StudentInvoiceResponse(StudentInvoiceCreate):
    id: UUID
    tenant_id: UUID
    amount_due: float  # Fetched automatically by the backend
    amount_paid: float
    status: InvoiceStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- PAYMENT RECEIPT SCHEMAS ---


class PaymentReceiptCreate(BaseModel):
    invoice_id: UUID
    amount_paid: float
    payment_method: PaymentMethod
    transaction_reference: Optional[str] = None  # For UPI/Bank tracking


class PaymentReceiptResponse(PaymentReceiptCreate):
    id: UUID
    tenant_id: UUID
    payment_date: datetime
    recorded_by_id: UUID

    model_config = ConfigDict(from_attributes=True)
