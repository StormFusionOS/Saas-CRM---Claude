"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API Data Models (In-Memory).

Simple dataclass models for in-memory operations.
For SQLAlchemy models used in schema tooling, see db_models.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class LeadStatus(str, Enum):
    """Lead pipeline status."""

    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUOTED = "QUOTED"
    SCHEDULED = "SCHEDULED"
    WON = "WON"
    LOST = "LOST"


class InteractionType(str, Enum):
    """Type of customer interaction."""

    EMAIL = "EMAIL"
    SMS = "SMS"
    PHONE = "PHONE"
    MEETING = "MEETING"
    NOTE = "NOTE"
    WEBHOOK = "WEBHOOK"


class LeadSource(str, Enum):
    """Source of lead."""

    FACEBOOK = "FACEBOOK"
    GOOGLE = "GOOGLE"
    TWILIO = "TWILIO"
    MANUAL = "MANUAL"
    IMPORT = "IMPORT"
    API = "API"


class QuoteStatus(str, Enum):
    """Quote status lifecycle."""

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    SENT = "SENT"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass
class User:
    """CRM user model."""

    id: int
    email: str
    hashed_password: str
    full_name: str
    roles: List[str]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class Contact:
    """Contact/customer model."""

    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"


@dataclass
class Lead:
    """Sales lead model."""

    id: int
    contact_id: int
    status: str = LeadStatus.NEW.value
    source: str = LeadSource.MANUAL.value
    value: Optional[float] = None
    assigned_to_id: Optional[int] = None
    probability: int = 0  # 0-100
    expected_close_date: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    won_at: Optional[datetime] = None
    lost_at: Optional[datetime] = None


@dataclass
class Interaction:
    """Customer interaction record."""

    id: int
    contact_id: int
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    interaction_type: str = InteractionType.NOTE.value
    direction: str = "INBOUND"  # INBOUND, OUTBOUND
    subject: Optional[str] = None
    body: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AutoReplyRule:
    """Auto-reply rule configuration."""

    id: int
    name: str
    trigger_source: str  # FACEBOOK, GOOGLE, TWILIO, etc.
    trigger_conditions: dict = field(default_factory=dict)
    reply_template: str = ""
    reply_channel: str = "EMAIL"  # EMAIL, SMS
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class PricebookItem:
    """Pricebook service item."""

    id: int
    name: str
    description: str
    unit: str  # e.g., "sq_ft", "linear_ft", "each"
    base_price: float
    formula: str  # e.g., "base_price * sq_ft", "base_price + (stories * 50)"
    category: str = "general"  # house_wash, roof_wash, etc.
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Estimate:
    """Estimate/Quote for a lead."""

    id: int
    lead_id: int
    contact_id: int
    service_ids: List[int]
    inputs: dict  # e.g., {"sq_ft": 2500, "stories": 2}
    good_tier: dict  # {"price": 299, "items": [...]}
    better_tier: dict  # {"price": 399, "items": [...]}
    best_tier: dict  # {"price": 499, "items": [...]}
    selected_tier: Optional[str] = None  # "good", "better", "best"
    deposit_amount: Optional[float] = None
    deposit_due: Optional[datetime] = None
    status: str = "draft"  # draft, sent, accepted, rejected
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None


@dataclass
class Job:
    """Job created from accepted estimate."""

    id: int
    lead_id: int
    estimate_id: int
    contact_id: int
    title: str
    total_price: float
    deposit_amount: float
    deposit_paid: bool = False
    status: str = "pending"  # pending, scheduled, in_progress, completed, cancelled
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class Service:
    """Service offering for quotes.

    Represents a service that can be added to quotes.
    More focused than PricebookItem - designed for the quoting engine.
    """

    id: int
    name: str
    description: str
    category: str  # e.g., "house_wash", "roof_wash", "window_cleaning"
    base_price: float
    unit: str  # e.g., "sq_ft", "linear_ft", "each", "hour"
    min_price: Optional[float] = None  # Minimum price floor for this service
    pricing_formula: Optional[str] = None  # e.g., "base_price * sq_ft + (stories * 50)"
    modifiers: dict = field(default_factory=dict)  # Optional pricing modifiers (e.g., {"difficulty": 1.2})
    is_active: bool = True
    display_order: int = 0
    metadata: dict = field(default_factory=dict)  # Additional service-specific data
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class QuoteItem:
    """Line item in a quote.

    Represents a single service line item within a quote.
    """

    id: int
    quote_id: int
    service_id: int
    service_name: str  # Snapshot of service name at time of quote
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    subtotal: float = 0.0  # quantity * unit_price
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    tax_percent: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0  # subtotal - discount_amount + tax_amount
    display_order: int = 0
    metadata: dict = field(default_factory=dict)  # e.g., {"sq_ft": 2500, "stories": 2}
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Quote:
    """Formal quote/proposal for a lead.

    Main quoting engine model. Represents a formal quote with line items,
    pricing, terms, and lifecycle tracking.
    """

    id: int
    lead_id: int
    contact_id: int
    quote_number: str  # e.g., "Q-2025-0001"
    title: str
    status: str = QuoteStatus.DRAFT.value
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0
    valid_until: Optional[datetime] = None
    terms: str = ""  # Payment terms, service terms, etc.
    notes: str = ""  # Internal notes
    public_notes: str = ""  # Notes visible to customer
    created_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)  # Flexible field for extensions
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# Auto-incrementing ID counters
_contact_id_counter = 1
_lead_id_counter = 1
_interaction_id_counter = 1
_auto_reply_rule_id_counter = 1
_pricebook_item_id_counter = 1
_estimate_id_counter = 1
_job_id_counter = 1
_service_id_counter = 1
_quote_id_counter = 1
_quote_item_id_counter = 1


def get_next_contact_id() -> int:
    """Get next contact ID."""
    global _contact_id_counter
    id = _contact_id_counter
    _contact_id_counter += 1
    return id


def get_next_lead_id() -> int:
    """Get next lead ID."""
    global _lead_id_counter
    id = _lead_id_counter
    _lead_id_counter += 1
    return id


def get_next_interaction_id() -> int:
    """Get next interaction ID."""
    global _interaction_id_counter
    id = _interaction_id_counter
    _interaction_id_counter += 1
    return id


def get_next_auto_reply_rule_id() -> int:
    """Get next auto-reply rule ID."""
    global _auto_reply_rule_id_counter
    id = _auto_reply_rule_id_counter
    _auto_reply_rule_id_counter += 1
    return id


def get_next_pricebook_item_id() -> int:
    """Get next pricebook item ID."""
    global _pricebook_item_id_counter
    id = _pricebook_item_id_counter
    _pricebook_item_id_counter += 1
    return id


def get_next_estimate_id() -> int:
    """Get next estimate ID."""
    global _estimate_id_counter
    id = _estimate_id_counter
    _estimate_id_counter += 1
    return id


def get_next_job_id() -> int:
    """Get next job ID."""
    global _job_id_counter
    id = _job_id_counter
    _job_id_counter += 1
    return id


def get_next_service_id() -> int:
    """Get next service ID."""
    global _service_id_counter
    id = _service_id_counter
    _service_id_counter += 1
    return id


def get_next_quote_id() -> int:
    """Get next quote ID."""
    global _quote_id_counter
    id = _quote_id_counter
    _quote_id_counter += 1
    return id


def get_next_quote_item_id() -> int:
    """Get next quote item ID."""
    global _quote_item_id_counter
    id = _quote_item_id_counter
    _quote_item_id_counter += 1
    return id


__all__ = [
    "User",
    "Contact",
    "Lead",
    "Interaction",
    "AutoReplyRule",
    "PricebookItem",
    "Estimate",
    "Job",
    "Service",
    "Quote",
    "QuoteItem",
    "LeadStatus",
    "InteractionType",
    "LeadSource",
    "QuoteStatus",
    "get_next_contact_id",
    "get_next_lead_id",
    "get_next_interaction_id",
    "get_next_auto_reply_rule_id",
    "get_next_pricebook_item_id",
    "get_next_estimate_id",
    "get_next_job_id",
    "get_next_service_id",
    "get_next_quote_id",
    "get_next_quote_item_id",
]
