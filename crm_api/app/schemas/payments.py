"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Payment & Deposit Schemas.

Pydantic models for payment processing, payment methods, and deposits.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# ============================================================================
# Payment Method Schemas
# ============================================================================


class PaymentMethodCreate(BaseModel):
    """Create a new payment method."""

    contact_id: int
    lead_id: Optional[int] = None
    method_type: str = Field(..., description="card, ach, check, cash, other")

    # Card details
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None

    # ACH details
    bank_name: Optional[str] = None
    account_last_four: Optional[str] = None
    account_type: Optional[str] = None

    # External processor
    processor: Optional[str] = None
    processor_payment_method_id: Optional[str] = None

    # Billing address
    billing_name: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip: Optional[str] = None

    is_default: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "contact_id": 1,
                "method_type": "card",
                "card_last_four": "4242",
                "card_brand": "visa",
                "card_exp_month": 12,
                "card_exp_year": 2025,
                "billing_name": "John Doe",
                "billing_zip": "12345",
            }
        }


class PaymentMethodUpdate(BaseModel):
    """Update a payment method."""

    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    billing_name: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class PaymentMethodResponse(BaseModel):
    """Payment method response."""

    id: int
    contact_id: int
    lead_id: Optional[int] = None
    method_type: str
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    bank_name: Optional[str] = None
    account_last_four: Optional[str] = None
    account_type: Optional[str] = None
    processor: Optional[str] = None
    is_default: bool
    is_verified: bool
    is_active: bool
    billing_name: Optional[str] = None
    billing_zip: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Payment Schemas
# ============================================================================


class PaymentCreate(BaseModel):
    """Create a new payment."""

    contact_id: int
    lead_id: Optional[int] = None
    quote_id: Optional[int] = None
    amount: float = Field(..., gt=0, description="Payment amount (must be > 0)")
    payment_method_id: Optional[int] = None
    payment_type: str = Field("payment", description="payment, deposit, refund")
    processor: str = Field("manual", description="stripe, square, authorize_net, manual")
    description: str = ""
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "contact_id": 1,
                "quote_id": 5,
                "amount": 500.0,
                "payment_type": "deposit",
                "description": "50% deposit for gutter cleaning",
            }
        }


class PaymentUpdate(BaseModel):
    """Update a payment."""

    status: Optional[str] = Field(None, description="pending, processing, succeeded, failed, cancelled")
    notes: Optional[str] = None
    processor_transaction_id: Optional[str] = None
    processor_fee: Optional[float] = None
    applied_to_quote: Optional[bool] = None


class PaymentResponse(BaseModel):
    """Payment response."""

    id: int
    contact_id: int
    lead_id: Optional[int] = None
    quote_id: Optional[int] = None
    amount: float
    currency: str
    payment_method_id: Optional[int] = None
    payment_type: str
    status: str
    failure_reason: Optional[str] = None
    processor: Optional[str] = None
    processor_transaction_id: Optional[str] = None
    processor_fee: Optional[float] = None
    description: str
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    receipt_number: Optional[str] = None
    applied_to_quote: bool
    refund_amount: float
    net_amount: Optional[float] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Refund Schemas
# ============================================================================


class RefundCreate(BaseModel):
    """Create a refund."""

    payment_id: int
    amount: float = Field(..., gt=0, description="Refund amount (must be > 0)")
    reason: str = ""
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": 1,
                "amount": 250.0,
                "reason": "Customer requested cancellation",
            }
        }


class RefundResponse(BaseModel):
    """Refund response."""

    id: int
    payment_id: int
    contact_id: int
    amount: float
    currency: str
    reason: str
    status: str
    processor: Optional[str] = None
    processor_refund_id: Optional[str] = None
    notes: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Deposit Request Schemas
# ============================================================================


class DepositRequestCreate(BaseModel):
    """Create a deposit request."""

    quote_id: int
    contact_id: int
    lead_id: Optional[int] = None
    amount: float = Field(..., gt=0)
    deposit_type: str = Field("fixed", description="percentage, fixed")
    percentage: Optional[float] = Field(None, ge=0, le=1, description="0.0 to 1.0 for percentage")
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "quote_id": 5,
                "contact_id": 1,
                "amount": 500.0,
                "deposit_type": "percentage",
                "percentage": 0.50,
            }
        }


class DepositRequestUpdate(BaseModel):
    """Update a deposit request."""

    status: Optional[str] = Field(None, description="pending, paid, waived, expired")
    payment_id: Optional[int] = None
    notes: Optional[str] = None


class DepositRequestResponse(BaseModel):
    """Deposit request response."""

    id: int
    quote_id: int
    contact_id: int
    lead_id: Optional[int] = None
    amount: float
    deposit_type: str
    percentage: Optional[float] = None
    due_date: Optional[datetime] = None
    status: str
    payment_id: Optional[int] = None
    reminder_sent: bool
    reminder_count: int
    last_reminder_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Processor Integration Schemas
# ============================================================================


class ProcessorSetupIntentCreate(BaseModel):
    """Request to create a payment setup intent (for Stripe, Square, etc.)."""

    contact_id: int
    processor: str = Field(..., description="stripe, square, authorize_net")
    return_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "contact_id": 1,
                "processor": "stripe",
                "return_url": "https://app.rivercityclean.com/payment/confirm",
            }
        }


class ProcessorSetupIntentResponse(BaseModel):
    """Response for payment setup intent."""

    client_secret: str
    setup_intent_id: str
    processor: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "client_secret": "seti_secret_abc123",
                "setup_intent_id": "seti_123",
                "processor": "stripe",
                "status": "requires_payment_method",
            }
        }
