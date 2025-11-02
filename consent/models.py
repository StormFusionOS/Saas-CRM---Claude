"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Consent Management Models

Defines data structures for consent tracking.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum


class ConsentPurpose(str, Enum):
    """Purposes for which consent can be given"""
    ESSENTIAL = "essential"  # Required for service (not optional)
    ANALYTICS = "analytics"  # Usage analytics
    MARKETING = "marketing"  # Marketing communications
    PERSONALIZATION = "personalization"  # Personalized content
    THIRD_PARTY_SHARING = "third_party_sharing"  # Share with partners
    PROFILING = "profiling"  # Automated decision-making


class ConsentStatus(str, Enum):
    """Consent status"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"  # Awaiting user action


@dataclass
class ConsentRecord:
    """
    Individual consent record

    Tracks a user's consent for a specific purpose.
    """
    user_id: str
    purpose: ConsentPurpose
    status: ConsentStatus
    version: str  # Version of consent policy
    given_at: str  # ISO timestamp
    withdrawn_at: Optional[str] = None
    expires_at: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: str = "web"  # web, api, mobile
    metadata: Dict = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if consent is currently active"""
        if self.status != ConsentStatus.GIVEN:
            return False

        # Check expiration
        if self.expires_at:
            expiry = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > expiry:
                return False

        return True


@dataclass
class ConsentPreferences:
    """
    User's consent preferences across all purposes

    Provides a unified view of all consents for a user.
    """
    user_id: str
    consents: Dict[str, ConsentRecord]  # purpose -> consent
    last_updated: str
    version: str

    def has_consent(self, purpose: ConsentPurpose) -> bool:
        """Check if user has active consent for a purpose"""
        consent = self.consents.get(purpose.value)
        return consent is not None and consent.is_active

    def get_active_consents(self) -> List[ConsentPurpose]:
        """Get list of purposes with active consent"""
        return [
            ConsentPurpose(purpose)
            for purpose, consent in self.consents.items()
            if consent.is_active
        ]


# Consent policy versions (track changes to consent text)
CONSENT_POLICY_VERSIONS = {
    "1.0": {
        "effective_date": "2024-01-01",
        "purposes": {
            ConsentPurpose.ESSENTIAL: {
                "name": "Essential Services",
                "description": "Required for the service to function (account management, security, etc.)",
                "required": True,
                "retention_days": None  # Kept as long as account exists
            },
            ConsentPurpose.ANALYTICS: {
                "name": "Analytics",
                "description": "Help us understand how you use our service to improve it",
                "required": False,
                "retention_days": 365 * 2  # 2 years
            },
            ConsentPurpose.MARKETING: {
                "name": "Marketing Communications",
                "description": "Receive emails about new features, promotions, and news",
                "required": False,
                "retention_days": 365 * 3  # 3 years
            },
            ConsentPurpose.PERSONALIZATION: {
                "name": "Personalization",
                "description": "Personalize content and recommendations based on your usage",
                "required": False,
                "retention_days": 365 * 2  # 2 years
            },
            ConsentPurpose.THIRD_PARTY_SHARING: {
                "name": "Third-Party Sharing",
                "description": "Share anonymized data with trusted partners for research",
                "required": False,
                "retention_days": 365 * 1  # 1 year
            },
            ConsentPurpose.PROFILING: {
                "name": "Automated Profiling",
                "description": "Use automated systems to suggest features and content",
                "required": False,
                "retention_days": 365 * 2  # 2 years
            }
        }
    }
}

# Current policy version
CURRENT_POLICY_VERSION = "1.0"


def get_current_policy() -> Dict:
    """Get current consent policy"""
    return CONSENT_POLICY_VERSIONS[CURRENT_POLICY_VERSION]


def is_required_purpose(purpose: ConsentPurpose) -> bool:
    """Check if a purpose is required (essential)"""
    policy = get_current_policy()
    purpose_config = policy["purposes"].get(purpose)
    return purpose_config.get("required", False) if purpose_config else False
