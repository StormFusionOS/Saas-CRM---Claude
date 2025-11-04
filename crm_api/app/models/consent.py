"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Consent and Compliance Models

Tracks user consent for data processing, marketing, and compliance with
GDPR, CCPA, and other privacy regulations.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConsentType:
    """Types of consent that can be tracked."""
    ESSENTIAL = "essential"  # Required for service operation
    MARKETING = "marketing"  # Marketing communications
    ANALYTICS = "analytics"  # Analytics and performance tracking
    PERSONALIZATION = "personalization"  # Personalized content
    THIRD_PARTY = "third_party"  # Third-party data sharing


class ConsentRecord(BaseModel):
    """A single consent record."""
    id: int
    contact_id: int
    consent_type: str  # ConsentType
    granted: bool
    source: str  # 'web', 'email', 'phone', 'in_person', etc.
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    consent_text: Optional[str] = None  # Exact text shown to user
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ConsentHistory(BaseModel):
    """Historical record of consent changes."""
    id: int
    consent_record_id: int
    action: str  # 'granted', 'revoked', 'updated', 'expired'
    previous_value: Optional[bool] = None
    new_value: bool
    reason: Optional[str] = None
    changed_by: Optional[int] = None  # user_id if changed by staff
    changed_at: datetime
    ip_address: Optional[str] = None


class DataProcessingAgreement(BaseModel):
    """Data processing agreement/privacy policy acceptance."""
    id: int
    contact_id: int
    policy_version: str  # e.g., "1.0", "2.1"
    policy_url: str
    accepted: bool
    accepted_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class GDPRRequest(BaseModel):
    """GDPR data subject request (access, deletion, portability)."""
    id: int
    contact_id: int
    request_type: str  # 'access', 'deletion', 'portability', 'rectification', 'restriction'
    status: str  # 'pending', 'in_progress', 'completed', 'rejected'
    requested_at: datetime
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None  # user_id
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Pydantic schemas for API

class CreateConsentRequest(BaseModel):
    contact_id: int
    consent_type: str
    granted: bool
    source: str = "web"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    consent_text: Optional[str] = None
    expires_at: Optional[datetime] = None


class UpdateConsentRequest(BaseModel):
    granted: bool
    reason: Optional[str] = None


class CreateDataProcessingAgreementRequest(BaseModel):
    contact_id: int
    policy_version: str
    policy_url: str
    accepted: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class CreateGDPRRequest(BaseModel):
    contact_id: int
    request_type: str = Field(..., pattern="^(access|deletion|portability|rectification|restriction)$")
    notes: Optional[str] = None


class UpdateGDPRRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|in_progress|completed|rejected)$")
    notes: Optional[str] = None


class ConsentSummary(BaseModel):
    """Summary of all consent settings for a contact."""
    contact_id: int
    essential: bool
    marketing: bool
    analytics: bool
    personalization: bool
    third_party: bool
    privacy_policy_accepted: bool
    privacy_policy_version: Optional[str] = None
    last_updated: datetime


class ConsentHistoryResponse(BaseModel):
    """Response containing consent history."""
    consent_record_id: int
    consent_type: str
    history: List[ConsentHistory]


class GDPRRequestResponse(BaseModel):
    """Response for GDPR request."""
    request: GDPRRequest
    contact_email: str
    contact_name: str
