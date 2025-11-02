"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Contact and lead schemas."""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    """Base contact schema."""

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, str] = {}


class ContactCreate(ContactBase):
    """Create contact request."""

    pass


class ContactUpdate(ContactBase):
    """Update contact request."""

    pass


class ContactResponse(ContactBase):
    """Contact response."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None


class LeadBase(BaseModel):
    """Base lead schema."""

    contact_id: int
    status: str = "NEW"
    source: str = "MANUAL"
    value: Optional[float] = None
    assigned_to_id: Optional[int] = None
    probability: int = 0
    expected_close_date: Optional[datetime] = None
    notes: str = ""


class LeadCreate(LeadBase):
    """Create lead request."""

    pass


class LeadUpdate(BaseModel):
    """Update lead request."""

    status: Optional[str] = None
    value: Optional[float] = None
    assigned_to_id: Optional[int] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Lead response."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    won_at: Optional[datetime] = None
    lost_at: Optional[datetime] = None


class LeadWithContact(LeadResponse):
    """Lead response with contact details."""

    contact: ContactResponse


class InteractionBase(BaseModel):
    """Base interaction schema."""

    contact_id: int
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    interaction_type: str = "NOTE"
    direction: str = "INBOUND"
    subject: Optional[str] = None
    body: str = ""
    metadata: Dict[str, str] = {}


class InteractionCreate(InteractionBase):
    """Create interaction request."""

    pass


class InteractionResponse(InteractionBase):
    """Interaction response."""

    id: int
    created_at: datetime


class LeadBoard(BaseModel):
    """Lead board grouped by status."""

    new: List[LeadWithContact] = []
    contacted: List[LeadWithContact] = []
    qualified: List[LeadWithContact] = []
    won: List[LeadWithContact] = []
    lost: List[LeadWithContact] = []


__all__ = [
    "ContactBase",
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadWithContact",
    "InteractionBase",
    "InteractionCreate",
    "InteractionResponse",
    "LeadBoard",
]
