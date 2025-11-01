"""
Consent Management

Provides GDPR/CCPA-compliant consent tracking and management.

Features:
- Granular consent tracking (marketing, analytics, etc.)
- Consent versioning
- Withdrawal support
- Audit logging
- API and UI components
"""

from .models import ConsentRecord, ConsentPurpose, ConsentStatus
from .manager import ConsentManager
from .api import consent_router

__all__ = [
    "ConsentRecord",
    "ConsentPurpose",
    "ConsentStatus",
    "ConsentManager",
    "consent_router",
]
