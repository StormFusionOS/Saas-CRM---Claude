"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Quote, QuoteItem, and Service schemas for the quoting engine."""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Service Schemas
# ============================================================================


class ServiceBase(BaseModel):
    """Base service schema."""

    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    category: str = Field(..., description="Service category (e.g., house_wash, roof_wash)")
    base_price: float = Field(..., description="Base price for the service")
    unit: str = Field(..., description="Unit of measurement (e.g., sq_ft, linear_ft, each)")
    pricing_formula: Optional[str] = Field(None, description="Formula for calculating price")
    is_active: bool = Field(True, description="Whether the service is active")
    display_order: int = Field(0, description="Display order in UI")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class ServiceCreate(ServiceBase):
    """Create service request."""

    pass


class ServiceUpdate(BaseModel):
    """Update service request."""

    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = None
    unit: Optional[str] = None
    pricing_formula: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None


class ServiceResponse(ServiceBase):
    """Service response."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============================================================================
# QuoteItem Schemas
# ============================================================================


class QuoteItemBase(BaseModel):
    """Base quote item schema."""

    service_id: int = Field(..., description="ID of the service")
    service_name: str = Field(..., description="Service name snapshot")
    description: str = Field(..., description="Line item description")
    quantity: float = Field(1.0, description="Quantity of the service")
    unit_price: float = Field(0.0, description="Unit price")
    subtotal: float = Field(0.0, description="Subtotal (quantity * unit_price)")
    discount_percent: float = Field(0.0, description="Discount percentage")
    discount_amount: float = Field(0.0, description="Discount amount")
    tax_percent: float = Field(0.0, description="Tax percentage")
    tax_amount: float = Field(0.0, description="Tax amount")
    total: float = Field(0.0, description="Total (subtotal - discount + tax)")
    display_order: int = Field(0, description="Display order in quote")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class QuoteItemCreate(BaseModel):
    """Create quote item request."""

    service_id: int
    quantity: float = 1.0
    unit_price: Optional[float] = None  # Will be calculated from service if not provided
    discount_percent: float = 0.0
    tax_percent: float = 0.0
    metadata: Dict[str, str] = {}


class QuoteItemUpdate(BaseModel):
    """Update quote item request."""

    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    discount_percent: Optional[float] = None
    tax_percent: Optional[float] = None
    display_order: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None


class QuoteItemResponse(QuoteItemBase):
    """Quote item response."""

    id: int
    quote_id: int
    created_at: datetime


# ============================================================================
# Quote Schemas
# ============================================================================


class QuoteBase(BaseModel):
    """Base quote schema."""

    lead_id: int = Field(..., description="Associated lead ID")
    contact_id: int = Field(..., description="Associated contact ID")
    title: str = Field(..., description="Quote title")
    valid_until: Optional[datetime] = Field(None, description="Quote expiration date")
    terms: str = Field("", description="Payment and service terms")
    notes: str = Field("", description="Internal notes")
    public_notes: str = Field("", description="Notes visible to customer")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class QuoteCreate(QuoteBase):
    """Create quote request.

    Creates a new quote with optional line items.
    """

    items: List[QuoteItemCreate] = Field(default_factory=list, description="Quote line items")


class QuoteUpdate(BaseModel):
    """Update quote request."""

    title: Optional[str] = None
    status: Optional[str] = None
    valid_until: Optional[datetime] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    public_notes: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class QuoteStatusUpdate(BaseModel):
    """Update quote status request."""

    status: str = Field(..., description="New quote status (DRAFT, SENT, ACCEPTED, etc.)")


class QuoteResponse(QuoteBase):
    """Quote response without items."""

    id: int
    quote_number: str
    status: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    total: float
    created_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class QuoteWithItems(QuoteResponse):
    """Quote response with line items included."""

    items: List[QuoteItemResponse] = Field(default_factory=list, description="Quote line items")


class QuoteListItem(BaseModel):
    """Lightweight quote for list views."""

    id: int
    quote_number: str
    lead_id: int
    contact_id: int
    title: str
    status: str
    total: float
    valid_until: Optional[datetime] = None
    created_at: datetime


__all__ = [
    # Service
    "ServiceBase",
    "ServiceCreate",
    "ServiceUpdate",
    "ServiceResponse",
    # QuoteItem
    "QuoteItemBase",
    "QuoteItemCreate",
    "QuoteItemUpdate",
    "QuoteItemResponse",
    # Quote
    "QuoteBase",
    "QuoteCreate",
    "QuoteUpdate",
    "QuoteStatusUpdate",
    "QuoteResponse",
    "QuoteWithItems",
    "QuoteListItem",
]
