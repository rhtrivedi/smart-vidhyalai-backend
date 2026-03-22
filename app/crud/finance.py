from sqlalchemy.orm import Session
from uuid import UUID

from app.models import finance as models
from app.schemas import finance as schemas
from fastapi import HTTPException, status
from app.models.core import User


def create_fee_category(
    db: Session, category_in: schemas.FeeCategoryCreate, tenant_id: UUID
):
    db_category = models.FeeCategory(
        tenant_id=tenant_id, name=category_in.name, description=category_in.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def create_fee_structure(
    db: Session, structure_in: schemas.FeeStructureCreate, tenant_id: UUID
):
    db_structure = models.FeeStructure(
        tenant_id=tenant_id,
        category_id=structure_in.category_id,
        academic_year_id=structure_in.academic_year_id,
        class_id=structure_in.class_id,
        amount=structure_in.amount,
    )
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure


def create_student_invoice(
    db: Session, invoice_in: schemas.StudentInvoiceCreate, tenant_id: UUID
):
    # 1. Securely fetch the amount from the master rule
    fee_structure = (
        db.query(models.FeeStructure)
        .filter(
            models.FeeStructure.id == invoice_in.fee_structure_id,
            models.FeeStructure.tenant_id == tenant_id,
        )
        .first()
    )

    if not fee_structure:
        raise HTTPException(status_code=404, detail="Fee structure not found.")

    # 2. Generate the immutable bill
    db_invoice = models.StudentInvoice(
        tenant_id=tenant_id,
        student_profile_id=invoice_in.student_profile_id,
        fee_structure_id=invoice_in.fee_structure_id,
        amount_due=fee_structure.amount,  # Locked from the database, not the user input!
        due_date=invoice_in.due_date,
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def process_payment(
    db: Session,
    payment_in: schemas.PaymentReceiptCreate,
    tenant_id: UUID,
    user_id: UUID,
):
    # 1. Fetch the invoice AND lock the row to prevent concurrent payment bugs
    invoice = (
        db.query(models.StudentInvoice)
        .filter(
            models.StudentInvoice.id == payment_in.invoice_id,
            models.StudentInvoice.tenant_id == tenant_id,
        )
        .with_for_update()
        .first()
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    if invoice.status == models.InvoiceStatus.PAID:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="This invoice is already fully paid."
        )

    # 2. Math Check: Prevent overcharging
    remaining_balance = invoice.amount_due - invoice.amount_paid
    if payment_in.amount_paid > remaining_balance:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Payment of {payment_in.amount_paid} exceeds the remaining balance of {remaining_balance}.",
        )

    # 3. Create the Receipt Ledger Entry
    db_receipt = models.PaymentReceipt(
        tenant_id=tenant_id,
        invoice_id=payment_in.invoice_id,
        amount_paid=payment_in.amount_paid,
        payment_method=payment_in.payment_method,
        transaction_reference=payment_in.transaction_reference,
        recorded_by_id=user_id,
    )
    db.add(db_receipt)

    # 4. Update the Master Invoice Status
    invoice.amount_paid += payment_in.amount_paid
    if invoice.amount_paid >= invoice.amount_due:
        invoice.status = models.InvoiceStatus.PAID
    else:
        invoice.status = models.InvoiceStatus.PARTIAL

    # 5. Commit both actions simultaneously
    db.commit()
    db.refresh(db_receipt)
    return db_receipt
