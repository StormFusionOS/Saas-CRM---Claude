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
    QUALIFIED = "QUALIFIED"
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


# Auto-incrementing ID counters
_contact_id_counter = 1
_lead_id_counter = 1
_interaction_id_counter = 1
_auto_reply_rule_id_counter = 1


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


__all__ = [
    "User",
    "Contact",
    "Lead",
    "Interaction",
    "AutoReplyRule",
    "LeadStatus",
    "InteractionType",
    "LeadSource",
    "get_next_contact_id",
    "get_next_lead_id",
    "get_next_interaction_id",
    "get_next_auto_reply_rule_id",
]
