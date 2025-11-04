"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Payment & Deposit API Routes.

Endpoints for payment processing, payment methods, refunds, and deposits.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from app.db import get_db, InMemoryDB
from app.schemas.payments import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    RefundCreate,
    RefundResponse,
    DepositRequestCreate,
    DepositRequestUpdate,
    DepositRequestResponse,
    ProcessorSetupIntentCreate,
    ProcessorSetupIntentResponse,
)
from app.services import payments_service
from app.api.deps import require_sales_claims


router = APIRouter(tags=["payments"])


# ============================================================================
# Payment Method Endpoints
# ============================================================================


@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method_data: PaymentMethodCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentMethodResponse:
    """
    Create a new payment method (STAFF ONLY).

    Stores customer payment method information (card, ACH, etc.) for future use.

    **Security Note**: In production, this would integrate with a payment processor
    (Stripe, Square) and only store tokens/references, never raw card data.
    """
    payment_method = payments_service.create_payment_method(
        db=db,
        contact_id=payment_method_data.contact_id,
        method_type=payment_method_data.method_type,
        lead_id=payment_method_data.lead_id,
        card_last_four=payment_method_data.card_last_four,
        card_brand=payment_method_data.card_brand,
        card_exp_month=payment_method_data.card_exp_month,
        card_exp_year=payment_method_data.card_exp_year,
        bank_name=payment_method_data.bank_name,
        account_last_four=payment_method_data.account_last_four,
        account_type=payment_method_data.account_type,
        processor=payment_method_data.processor,
        processor_payment_method_id=payment_method_data.processor_payment_method_id,
        billing_name=payment_method_data.billing_name,
        billing_address=payment_method_data.billing_address,
        billing_city=payment_method_data.billing_city,
        billing_state=payment_method_data.billing_state,
        billing_zip=payment_method_data.billing_zip,
        is_default=payment_method_data.is_default,
        metadata=payment_method_data.metadata,
        created_by=current_user.get("user_id"),
    )

    return PaymentMethodResponse(**payment_method.__dict__)


@router.get("/contacts/{contact_id}/payment-methods", response_model=List[PaymentMethodResponse])
def get_contact_payment_methods(
    contact_id: int = Path(..., description="Contact ID"),
    active_only: bool = Query(True, description="Only return active payment methods"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[PaymentMethodResponse]:
    """
    Get all payment methods for a contact (STAFF ONLY).

    Returns stored payment methods sorted by default first, then by creation date.
    """
    payment_methods = payments_service.get_payment_methods_for_contact(
        db=db,
        contact_id=contact_id,
        active_only=active_only,
    )

    return [PaymentMethodResponse(**pm.__dict__) for pm in payment_methods]


@router.get("/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse)
def get_payment_method(
    payment_method_id: int = Path(..., description="Payment method ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentMethodResponse:
    """Get a specific payment method (STAFF ONLY)."""
    if payment_method_id not in db.payment_methods:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found",
        )

    payment_method = db.payment_methods[payment_method_id]
    return PaymentMethodResponse(**payment_method.__dict__)


@router.patch("/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    payment_method_id: int = Path(..., description="Payment method ID"),
    updates: PaymentMethodUpdate = ...,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentMethodResponse:
    """Update a payment method (STAFF ONLY)."""
    payment_method = payments_service.update_payment_method(
        db=db,
        payment_method_id=payment_method_id,
        **updates.model_dump(exclude_unset=True),
    )

    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found",
        )

    return PaymentMethodResponse(**payment_method.__dict__)


@router.delete("/payment-methods/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(
    payment_method_id: int = Path(..., description="Payment method ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Delete (deactivate) a payment method (STAFF ONLY).

    This is a soft delete - the payment method is marked as inactive but not removed.
    """
    success = payments_service.delete_payment_method(db=db, payment_method_id=payment_method_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found",
        )


# ============================================================================
# Payment Transaction Endpoints
# ============================================================================


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentResponse:
    """
    Create a new payment (STAFF ONLY).

    **Production Note**: This would integrate with payment processors (Stripe, Square)
    to actually charge the payment method. This demo creates a pending payment that
    can be manually marked as succeeded/failed.
    """
    payment = payments_service.create_payment(
        db=db,
        contact_id=payment_data.contact_id,
        amount=payment_data.amount,
        lead_id=payment_data.lead_id,
        quote_id=payment_data.quote_id,
        payment_method_id=payment_data.payment_method_id,
        payment_type=payment_data.payment_type,
        processor=payment_data.processor,
        description=payment_data.description,
        notes=payment_data.notes,
        metadata=payment_data.metadata,
        created_by=current_user.get("user_id"),
    )

    return PaymentResponse(**payment.__dict__)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int = Path(..., description="Payment ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentResponse:
    """Get a specific payment (STAFF ONLY)."""
    payment = payments_service.get_payment(db=db, payment_id=payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return PaymentResponse(**payment.__dict__)


@router.get("/contacts/{contact_id}/payments", response_model=List[PaymentResponse])
def get_contact_payments(
    contact_id: int = Path(..., description="Contact ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[PaymentResponse]:
    """Get all payments for a contact (STAFF ONLY)."""
    payments = payments_service.get_payments_for_contact(db=db, contact_id=contact_id)
    return [PaymentResponse(**p.__dict__) for p in payments]


@router.get("/quotes/{quote_id}/payments", response_model=List[PaymentResponse])
def get_quote_payments(
    quote_id: int = Path(..., description="Quote ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[PaymentResponse]:
    """Get all payments for a quote (STAFF ONLY)."""
    payments = payments_service.get_payments_for_quote(db=db, quote_id=quote_id)
    return [PaymentResponse(**p.__dict__) for p in payments]


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int = Path(..., description="Payment ID"),
    updates: PaymentUpdate = ...,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentResponse:
    """
    Update a payment (STAFF ONLY).

    Typically used to update status (succeeded, failed, etc.) after processor response.
    """
    payment = payments_service.get_payment(db=db, payment_id=payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    update_dict = updates.model_dump(exclude_unset=True)
    if "status" in update_dict:
        payment = payments_service.update_payment_status(
            db=db,
            payment_id=payment_id,
            status=update_dict.pop("status"),
            **update_dict,
        )
    else:
        for key, value in update_dict.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
        db.commit()

    return PaymentResponse(**payment.__dict__)


@router.post("/payments/{payment_id}/apply-to-quote/{quote_id}", response_model=PaymentResponse)
def apply_payment_to_quote(
    payment_id: int = Path(..., description="Payment ID"),
    quote_id: int = Path(..., description="Quote ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PaymentResponse:
    """Mark a payment as applied to a specific quote (STAFF ONLY)."""
    payment = payments_service.mark_payment_applied_to_quote(
        db=db,
        payment_id=payment_id,
        quote_id=quote_id,
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return PaymentResponse(**payment.__dict__)


# ============================================================================
# Refund Endpoints
# ============================================================================


@router.post("/refunds", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
def create_refund(
    refund_data: RefundCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> RefundResponse:
    """
    Create a refund for a payment (STAFF ONLY).

    **Production Note**: This would call the payment processor API to issue
    the actual refund. This demo creates a pending refund.
    """
    refund = payments_service.create_refund(
        db=db,
        payment_id=refund_data.payment_id,
        amount=refund_data.amount,
        reason=refund_data.reason,
        notes=refund_data.notes,
        metadata=refund_data.metadata,
        created_by=current_user.get("user_id"),
    )

    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return RefundResponse(**refund.__dict__)


@router.get("/refunds/{refund_id}", response_model=RefundResponse)
def get_refund(
    refund_id: int = Path(..., description="Refund ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> RefundResponse:
    """Get a specific refund (STAFF ONLY)."""
    refund = payments_service.get_refund(db=db, refund_id=refund_id)

    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found",
        )

    return RefundResponse(**refund.__dict__)


@router.get("/payments/{payment_id}/refunds", response_model=List[RefundResponse])
def get_payment_refunds(
    payment_id: int = Path(..., description="Payment ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[RefundResponse]:
    """Get all refunds for a payment (STAFF ONLY)."""
    refunds = payments_service.get_refunds_for_payment(db=db, payment_id=payment_id)
    return [RefundResponse(**r.__dict__) for r in refunds]


# ============================================================================
# Deposit Request Endpoints
# ============================================================================


@router.post("/deposit-requests", response_model=DepositRequestResponse, status_code=status.HTTP_201_CREATED)
def create_deposit_request(
    deposit_data: DepositRequestCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> DepositRequestResponse:
    """
    Create a deposit request for a quote (STAFF ONLY).

    Used to request deposits/down payments before work begins.
    """
    deposit = payments_service.create_deposit_request(
        db=db,
        quote_id=deposit_data.quote_id,
        contact_id=deposit_data.contact_id,
        amount=deposit_data.amount,
        lead_id=deposit_data.lead_id,
        deposit_type=deposit_data.deposit_type,
        percentage=deposit_data.percentage,
        due_date=deposit_data.due_date,
        notes=deposit_data.notes,
        metadata=deposit_data.metadata,
        created_by=current_user.get("user_id"),
    )

    return DepositRequestResponse(**deposit.__dict__)


@router.get("/deposit-requests/{deposit_id}", response_model=DepositRequestResponse)
def get_deposit_request(
    deposit_id: int = Path(..., description="Deposit request ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> DepositRequestResponse:
    """Get a specific deposit request (STAFF ONLY)."""
    deposit = payments_service.get_deposit_request(db=db, deposit_id=deposit_id)

    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit request not found",
        )

    return DepositRequestResponse(**deposit.__dict__)


@router.get("/quotes/{quote_id}/deposit-requests", response_model=List[DepositRequestResponse])
def get_quote_deposit_requests(
    quote_id: int = Path(..., description="Quote ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[DepositRequestResponse]:
    """Get all deposit requests for a quote (STAFF ONLY)."""
    deposits = payments_service.get_deposit_requests_for_quote(db=db, quote_id=quote_id)
    return [DepositRequestResponse(**d.__dict__) for d in deposits]


@router.get("/contacts/{contact_id}/deposit-requests", response_model=List[DepositRequestResponse])
def get_contact_deposit_requests(
    contact_id: int = Path(..., description="Contact ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[DepositRequestResponse]:
    """Get all deposit requests for a contact (STAFF ONLY)."""
    deposits = payments_service.get_deposit_requests_for_contact(
        db=db,
        contact_id=contact_id,
        status=status_filter,
    )
    return [DepositRequestResponse(**d.__dict__) for d in deposits]


@router.patch("/deposit-requests/{deposit_id}", response_model=DepositRequestResponse)
def update_deposit_request(
    deposit_id: int = Path(..., description="Deposit request ID"),
    updates: DepositRequestUpdate = ...,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> DepositRequestResponse:
    """Update a deposit request (STAFF ONLY)."""
    deposit = payments_service.update_deposit_request(
        db=db,
        deposit_id=deposit_id,
        **updates.model_dump(exclude_unset=True),
    )

    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit request not found",
        )

    return DepositRequestResponse(**deposit.__dict__)


@router.post("/deposit-requests/{deposit_id}/mark-paid/{payment_id}", response_model=DepositRequestResponse)
def mark_deposit_paid(
    deposit_id: int = Path(..., description="Deposit request ID"),
    payment_id: int = Path(..., description="Payment ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> DepositRequestResponse:
    """Mark a deposit request as paid (STAFF ONLY)."""
    deposit = payments_service.mark_deposit_paid(
        db=db,
        deposit_id=deposit_id,
        payment_id=payment_id,
    )

    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit request not found",
        )

    return DepositRequestResponse(**deposit.__dict__)


# ============================================================================
# Payment Statistics
# ============================================================================


@router.get("/contacts/{contact_id}/payment-stats")
def get_contact_payment_stats(
    contact_id: int = Path(..., description="Contact ID"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Get payment statistics for a contact (STAFF ONLY).

    Returns total paid, refunded, pending amounts, and payment counts.
    """
    return payments_service.get_payment_stats_for_contact(db=db, contact_id=contact_id)


# ============================================================================
# Payment Processor Integration (Mock)
# ============================================================================


@router.post("/processor/setup-intent", response_model=ProcessorSetupIntentResponse)
def create_setup_intent(
    setup_data: ProcessorSetupIntentCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> ProcessorSetupIntentResponse:
    """
    Create a payment processor setup intent (STAFF ONLY).

    **Production Note**: This would call the payment processor API (Stripe, Square)
    to create a setup intent for collecting payment method details from the customer.
    This demo returns mock data.
    """
    # Mock response - in production, this would call Stripe/Square API
    return ProcessorSetupIntentResponse(
        client_secret=f"seti_secret_mock_{setup_data.contact_id}",
        setup_intent_id=f"seti_mock_{setup_data.contact_id}",
        processor=setup_data.processor,
        status="requires_payment_method",
    )
