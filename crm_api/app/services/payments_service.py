"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Payment Service - Payment processing business logic.

Handles payment methods, transactions, refunds, and deposits.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db import InMemoryDB
from app.models import (
    PaymentMethod,
    Payment,
    Refund,
    DepositRequest,
    get_next_payment_method_id,
    get_next_payment_id,
    get_next_refund_id,
    get_next_deposit_request_id,
)


# ============================================================================
# Payment Method Management
# ============================================================================


def create_payment_method(
    db: InMemoryDB,
    contact_id: int,
    method_type: str,
    **kwargs
) -> PaymentMethod:
    """
    Create a new payment method for a customer.

    Args:
        db: Database session
        contact_id: Contact ID
        method_type: Type of payment method (card, ach, check, cash, other)
        **kwargs: Additional payment method fields

    Returns:
        Created PaymentMethod
    """
    # If this is set as default, unset other defaults for this contact
    if kwargs.get("is_default", False):
        for pm in db.payment_methods.values():
            if pm.contact_id == contact_id and pm.is_default:
                pm.is_default = False
                pm.updated_at = datetime.utcnow()

    payment_method = PaymentMethod(
        id=get_next_payment_method_id(),
        contact_id=contact_id,
        method_type=method_type,
        **kwargs
    )

    db.payment_methods[payment_method.id] = payment_method
    db.commit()

    return payment_method


def get_payment_methods_for_contact(
    db: InMemoryDB,
    contact_id: int,
    active_only: bool = True
) -> List[PaymentMethod]:
    """
    Get all payment methods for a contact.

    Args:
        db: Database session
        contact_id: Contact ID
        active_only: Only return active payment methods

    Returns:
        List of PaymentMethod objects
    """
    methods = [
        pm for pm in db.payment_methods.values()
        if pm.contact_id == contact_id
    ]

    if active_only:
        methods = [pm for pm in methods if pm.is_active]

    # Sort by default first, then by created date
    methods.sort(key=lambda x: (not x.is_default, x.created_at), reverse=True)

    return methods


def update_payment_method(
    db: InMemoryDB,
    payment_method_id: int,
    **updates
) -> Optional[PaymentMethod]:
    """Update a payment method."""
    if payment_method_id not in db.payment_methods:
        return None

    payment_method = db.payment_methods[payment_method_id]

    # If setting as default, unset other defaults
    if updates.get("is_default", False) and not payment_method.is_default:
        for pm in db.payment_methods.values():
            if pm.contact_id == payment_method.contact_id and pm.is_default:
                pm.is_default = False
                pm.updated_at = datetime.utcnow()

    for key, value in updates.items():
        if hasattr(payment_method, key):
            setattr(payment_method, key, value)

    payment_method.updated_at = datetime.utcnow()
    db.commit()

    return payment_method


def delete_payment_method(db: InMemoryDB, payment_method_id: int) -> bool:
    """Soft delete a payment method (set is_active = False)."""
    if payment_method_id not in db.payment_methods:
        return False

    payment_method = db.payment_methods[payment_method_id]
    payment_method.is_active = False
    payment_method.updated_at = datetime.utcnow()
    db.commit()

    return True


# ============================================================================
# Payment Processing
# ============================================================================


def create_payment(
    db: InMemoryDB,
    contact_id: int,
    amount: float,
    **kwargs
) -> Payment:
    """
    Create a new payment transaction.

    Args:
        db: Database session
        contact_id: Contact ID
        amount: Payment amount
        **kwargs: Additional payment fields

    Returns:
        Created Payment
    """
    payment = Payment(
        id=get_next_payment_id(),
        contact_id=contact_id,
        amount=amount,
        **kwargs
    )

    # Calculate net amount if processor fee is provided
    if payment.processor_fee is not None:
        payment.net_amount = payment.amount - payment.processor_fee

    db.payments.append(payment)
    db.commit()

    return payment


def get_payment(db: InMemoryDB, payment_id: int) -> Optional[Payment]:
    """Get a payment by ID."""
    for payment in db.payments:
        if payment.id == payment_id:
            return payment
    return None


def get_payments_for_contact(
    db: InMemoryDB,
    contact_id: int
) -> List[Payment]:
    """Get all payments for a contact."""
    payments = [p for p in db.payments if p.contact_id == contact_id]
    payments.sort(key=lambda x: x.created_at, reverse=True)
    return payments


def get_payments_for_quote(
    db: InMemoryDB,
    quote_id: int
) -> List[Payment]:
    """Get all payments for a quote."""
    payments = [p for p in db.payments if p.quote_id == quote_id]
    payments.sort(key=lambda x: x.created_at, reverse=True)
    return payments


def update_payment_status(
    db: InMemoryDB,
    payment_id: int,
    status: str,
    **updates
) -> Optional[Payment]:
    """
    Update a payment's status.

    Args:
        db: Database session
        payment_id: Payment ID
        status: New status (pending, processing, succeeded, failed, cancelled, refunded)
        **updates: Additional fields to update

    Returns:
        Updated Payment or None
    """
    payment = get_payment(db, payment_id)
    if not payment:
        return None

    payment.status = status
    payment.updated_at = datetime.utcnow()

    if status in ["succeeded", "failed", "refunded"]:
        payment.processed_at = datetime.utcnow()

    for key, value in updates.items():
        if hasattr(payment, key):
            setattr(payment, key, value)

    db.commit()

    return payment


def mark_payment_applied_to_quote(
    db: InMemoryDB,
    payment_id: int,
    quote_id: int
) -> Optional[Payment]:
    """Mark a payment as applied to a quote."""
    payment = get_payment(db, payment_id)
    if not payment:
        return None

    payment.applied_to_quote = True
    payment.quote_id = quote_id
    payment.updated_at = datetime.utcnow()
    db.commit()

    return payment


# ============================================================================
# Refund Processing
# ============================================================================


def create_refund(
    db: InMemoryDB,
    payment_id: int,
    amount: float,
    reason: str = "",
    **kwargs
) -> Optional[Refund]:
    """
    Create a refund for a payment.

    Args:
        db: Database session
        payment_id: Payment to refund
        amount: Refund amount
        reason: Refund reason
        **kwargs: Additional refund fields

    Returns:
        Created Refund or None if payment not found
    """
    payment = get_payment(db, payment_id)
    if not payment:
        return None

    refund = Refund(
        id=get_next_refund_id(),
        payment_id=payment_id,
        contact_id=payment.contact_id,
        amount=amount,
        reason=reason,
        processor=payment.processor,
        **kwargs
    )

    db.refunds.append(refund)

    # Update payment refund amount
    payment.refund_amount += amount
    if payment.net_amount is not None:
        payment.net_amount -= amount
    payment.updated_at = datetime.utcnow()

    # Update payment status if fully refunded
    if payment.refund_amount >= payment.amount:
        payment.status = "refunded"

    db.commit()

    return refund


def get_refund(db: InMemoryDB, refund_id: int) -> Optional[Refund]:
    """Get a refund by ID."""
    for refund in db.refunds:
        if refund.id == refund_id:
            return refund
    return None


def get_refunds_for_payment(db: InMemoryDB, payment_id: int) -> List[Refund]:
    """Get all refunds for a payment."""
    refunds = [r for r in db.refunds if r.payment_id == payment_id]
    refunds.sort(key=lambda x: x.created_at, reverse=True)
    return refunds


def update_refund_status(
    db: InMemoryDB,
    refund_id: int,
    status: str,
    **updates
) -> Optional[Refund]:
    """Update a refund's status."""
    refund = get_refund(db, refund_id)
    if not refund:
        return None

    refund.status = status
    refund.updated_at = datetime.utcnow()

    if status in ["succeeded", "failed"]:
        refund.processed_at = datetime.utcnow()

    for key, value in updates.items():
        if hasattr(refund, key):
            setattr(refund, key, value)

    db.commit()

    return refund


# ============================================================================
# Deposit Requests
# ============================================================================


def create_deposit_request(
    db: InMemoryDB,
    quote_id: int,
    contact_id: int,
    amount: float,
    **kwargs
) -> DepositRequest:
    """
    Create a deposit request for a quote.

    Args:
        db: Database session
        quote_id: Quote ID
        contact_id: Contact ID
        amount: Deposit amount
        **kwargs: Additional deposit request fields

    Returns:
        Created DepositRequest
    """
    deposit_request = DepositRequest(
        id=get_next_deposit_request_id(),
        quote_id=quote_id,
        contact_id=contact_id,
        amount=amount,
        **kwargs
    )

    db.deposit_requests.append(deposit_request)
    db.commit()

    return deposit_request


def get_deposit_request(db: InMemoryDB, deposit_id: int) -> Optional[DepositRequest]:
    """Get a deposit request by ID."""
    for deposit in db.deposit_requests:
        if deposit.id == deposit_id:
            return deposit
    return None


def get_deposit_requests_for_quote(
    db: InMemoryDB,
    quote_id: int
) -> List[DepositRequest]:
    """Get all deposit requests for a quote."""
    deposits = [d for d in db.deposit_requests if d.quote_id == quote_id]
    deposits.sort(key=lambda x: x.created_at, reverse=True)
    return deposits


def get_deposit_requests_for_contact(
    db: InMemoryDB,
    contact_id: int,
    status: Optional[str] = None
) -> List[DepositRequest]:
    """Get all deposit requests for a contact, optionally filtered by status."""
    deposits = [d for d in db.deposit_requests if d.contact_id == contact_id]

    if status:
        deposits = [d for d in deposits if d.status == status]

    deposits.sort(key=lambda x: x.created_at, reverse=True)
    return deposits


def mark_deposit_paid(
    db: InMemoryDB,
    deposit_id: int,
    payment_id: int
) -> Optional[DepositRequest]:
    """Mark a deposit request as paid."""
    deposit = get_deposit_request(db, deposit_id)
    if not deposit:
        return None

    deposit.status = "paid"
    deposit.payment_id = payment_id
    deposit.updated_at = datetime.utcnow()
    db.commit()

    return deposit


def update_deposit_request(
    db: InMemoryDB,
    deposit_id: int,
    **updates
) -> Optional[DepositRequest]:
    """Update a deposit request."""
    deposit = get_deposit_request(db, deposit_id)
    if not deposit:
        return None

    for key, value in updates.items():
        if hasattr(deposit, key):
            setattr(deposit, key, value)

    deposit.updated_at = datetime.utcnow()
    db.commit()

    return deposit


# ============================================================================
# Payment Statistics
# ============================================================================


def get_payment_stats_for_contact(db: InMemoryDB, contact_id: int) -> Dict[str, Any]:
    """
    Get payment statistics for a contact.

    Returns:
        Dictionary with payment stats (total_paid, total_refunded, payment_count, etc.)
    """
    payments = get_payments_for_contact(db, contact_id)

    total_paid = sum(p.amount for p in payments if p.status == "succeeded")
    total_refunded = sum(p.refund_amount for p in payments)
    pending_amount = sum(p.amount for p in payments if p.status == "pending")

    return {
        "contact_id": contact_id,
        "total_paid": round(total_paid, 2),
        "total_refunded": round(total_refunded, 2),
        "net_paid": round(total_paid - total_refunded, 2),
        "pending_amount": round(pending_amount, 2),
        "payment_count": len(payments),
        "successful_payment_count": sum(1 for p in payments if p.status == "succeeded"),
        "failed_payment_count": sum(1 for p in payments if p.status == "failed"),
    }
