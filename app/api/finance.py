from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import finance as schemas
from app.crud import finance as crud
from app.api import deps
from app.models.core import TenantUser

router = APIRouter()


@router.post("/categories", response_model=schemas.FeeCategoryResponse)
def create_fee_category(
    category_in: schemas.FeeCategoryCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """Creates a master blueprint for a charge (e.g., 'Tuition Fee')."""
    return crud.create_fee_category(
        db=db, category_in=category_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/structures", response_model=schemas.FeeStructureResponse)
def create_fee_structure(
    structure_in: schemas.FeeStructureCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """Defines the exact cost of a Fee Category for a specific Class and Year."""
    return crud.create_fee_structure(
        db=db, structure_in=structure_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/invoices", response_model=schemas.StudentInvoiceResponse)
def generate_student_invoice(
    invoice_in: schemas.StudentInvoiceCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """Generates a formal bill for a student based on a predefined fee structure."""
    return crud.create_student_invoice(
        db=db, invoice_in=invoice_in, tenant_id=tenant_context.tenant_id
    )


@router.post("/payments", response_model=schemas.PaymentReceiptResponse)
def record_payment_receipt(
    payment_in: schemas.PaymentReceiptCreate,
    db: Session = Depends(get_db),
    tenant_context: TenantUser = Depends(deps.get_current_tenant_user),
):
    """
    Banking-Grade Ledger: Records a payment, handles partial payments automatically,
    and updates the master invoice status.
    """
    return crud.process_payment(
        db=db,
        payment_in=payment_in,
        tenant_id=tenant_context.tenant_id,
        user_id=tenant_context.user_id,
    )
