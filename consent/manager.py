"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Consent Manager

Manages consent records: creation, withdrawal, querying, and expiration.
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from .models import (
    ConsentRecord,
    ConsentPreferences,
    ConsentPurpose,
    ConsentStatus,
    CURRENT_POLICY_VERSION,
    get_current_policy
)

logger = logging.getLogger(__name__)


class ConsentManager:
    """
    Consent management system

    Handles consent tracking, withdrawal, and querying.
    """

    def __init__(
        self,
        storage_dir: str = "data/consent",
        audit_log_path: str = "logs/consent_audit.jsonl"
    ):
        """
        Initialize consent manager

        Args:
            storage_dir: Directory to store consent records
            audit_log_path: Path to audit log
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def give_consent(
        self,
        user_id: str,
        purpose: ConsentPurpose,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        source: str = "web",
        metadata: Optional[Dict] = None
    ) -> ConsentRecord:
        """
        Record user consent for a purpose

        Args:
            user_id: User ID
            purpose: Consent purpose
            ip_address: IP address of user
            user_agent: User agent string
            source: Source of consent (web, api, mobile)
            metadata: Additional metadata

        Returns:
            Created consent record
        """
        # Calculate expiration
        policy = get_current_policy()
        purpose_config = policy["purposes"][purpose]
        retention_days = purpose_config.get("retention_days")

        expires_at = None
        if retention_days:
            expiry_date = datetime.now(timezone.utc) + timedelta(days=retention_days)
            expires_at = expiry_date.isoformat()

        # Create consent record
        consent = ConsentRecord(
            user_id=user_id,
            purpose=purpose,
            status=ConsentStatus.GIVEN,
            version=CURRENT_POLICY_VERSION,
            given_at=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            source=source,
            metadata=metadata or {}
        )

        # Save consent
        self._save_consent(consent)

        # Audit log
        self._audit_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "GIVE_CONSENT",
            "user_id": user_id,
            "purpose": purpose.value,
            "version": CURRENT_POLICY_VERSION,
            "ip_address": ip_address
        })

        logger.info(f"User {user_id} gave consent for {purpose.value}")

        return consent

    def withdraw_consent(
        self,
        user_id: str,
        purpose: ConsentPurpose,
        ip_address: Optional[str] = None
    ) -> ConsentRecord:
        """
        Withdraw user consent for a purpose

        Args:
            user_id: User ID
            purpose: Consent purpose
            ip_address: IP address of user

        Returns:
            Updated consent record
        """
        # Load existing consent
        consent = self._load_consent(user_id, purpose)

        if not consent:
            raise ValueError(f"No consent found for user {user_id} and purpose {purpose.value}")

        # Update consent
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = datetime.now(timezone.utc).isoformat()

        # Save updated consent
        self._save_consent(consent)

        # Audit log
        self._audit_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "WITHDRAW_CONSENT",
            "user_id": user_id,
            "purpose": purpose.value,
            "ip_address": ip_address
        })

        logger.info(f"User {user_id} withdrew consent for {purpose.value}")

        return consent

    def get_user_consents(self, user_id: str) -> ConsentPreferences:
        """
        Get all consents for a user

        Args:
            user_id: User ID

        Returns:
            User's consent preferences
        """
        user_dir = self.storage_dir / user_id
        if not user_dir.exists():
            # Return default preferences (no consents)
            return ConsentPreferences(
                user_id=user_id,
                consents={},
                last_updated=datetime.now(timezone.utc).isoformat(),
                version=CURRENT_POLICY_VERSION
            )

        # Load all consent records
        consents = {}
        last_updated = None

        for consent_file in user_dir.glob("*.json"):
            consent_data = json.loads(consent_file.read_text())

            # Convert string enums back to Enum types
            consent_data["purpose"] = ConsentPurpose(consent_data["purpose"])
            consent_data["status"] = ConsentStatus(consent_data["status"])

            consent = ConsentRecord(**consent_data)

            consents[consent.purpose.value] = consent

            # Track most recent update
            given_at = datetime.fromisoformat(consent.given_at.replace('Z', '+00:00'))
            if last_updated is None or given_at > last_updated:
                last_updated = given_at

        return ConsentPreferences(
            user_id=user_id,
            consents=consents,
            last_updated=last_updated.isoformat() if last_updated else datetime.now(timezone.utc).isoformat(),
            version=CURRENT_POLICY_VERSION
        )

    def has_consent(self, user_id: str, purpose: ConsentPurpose) -> bool:
        """
        Check if user has active consent for a purpose

        Args:
            user_id: User ID
            purpose: Consent purpose

        Returns:
            True if consent is active
        """
        consent = self._load_consent(user_id, purpose)

        if not consent:
            return False

        return consent.is_active

    def bulk_give_consent(
        self,
        user_id: str,
        purposes: List[ConsentPurpose],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        source: str = "web"
    ) -> List[ConsentRecord]:
        """
        Give consent for multiple purposes at once

        Args:
            user_id: User ID
            purposes: List of purposes to consent to
            ip_address: IP address
            user_agent: User agent
            source: Source of consent

        Returns:
            List of created consent records
        """
        consents = []

        for purpose in purposes:
            consent = self.give_consent(
                user_id=user_id,
                purpose=purpose,
                ip_address=ip_address,
                user_agent=user_agent,
                source=source
            )
            consents.append(consent)

        return consents

    def expire_consents(self) -> int:
        """
        Mark expired consents as expired

        Returns:
            Number of consents marked as expired
        """
        count = 0
        now = datetime.now(timezone.utc)

        # Scan all user directories
        for user_dir in self.storage_dir.iterdir():
            if not user_dir.is_dir():
                continue

            for consent_file in user_dir.glob("*.json"):
                consent_data = json.loads(consent_file.read_text())
                consent = ConsentRecord(**consent_data)

                # Check if expired
                if consent.expires_at and consent.status == ConsentStatus.GIVEN:
                    expiry = datetime.fromisoformat(consent.expires_at.replace('Z', '+00:00'))
                    if now > expiry:
                        # Mark as expired
                        consent.status = ConsentStatus.EXPIRED
                        self._save_consent(consent)
                        count += 1

                        logger.info(f"Expired consent: {consent.user_id} / {consent.purpose.value}")

        logger.info(f"Marked {count} consents as expired")
        return count

    def _save_consent(self, consent: ConsentRecord):
        """Save consent record to disk"""
        user_dir = self.storage_dir / consent.user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        consent_file = user_dir / f"{consent.purpose.value}.json"

        # Convert to dict for JSON serialization
        consent_dict = {
            "user_id": consent.user_id,
            "purpose": consent.purpose.value,
            "status": consent.status.value,
            "version": consent.version,
            "given_at": consent.given_at,
            "withdrawn_at": consent.withdrawn_at,
            "expires_at": consent.expires_at,
            "ip_address": consent.ip_address,
            "user_agent": consent.user_agent,
            "source": consent.source,
            "metadata": consent.metadata
        }

        consent_file.write_text(json.dumps(consent_dict, indent=2))

    def _load_consent(
        self,
        user_id: str,
        purpose: ConsentPurpose
    ) -> Optional[ConsentRecord]:
        """Load consent record from disk"""
        consent_file = self.storage_dir / user_id / f"{purpose.value}.json"

        if not consent_file.exists():
            return None

        consent_data = json.loads(consent_file.read_text())

        # Convert string enums back to Enum types
        consent_data["purpose"] = ConsentPurpose(consent_data["purpose"])
        consent_data["status"] = ConsentStatus(consent_data["status"])

        return ConsentRecord(**consent_data)

    def _audit_log(self, entry: Dict):
        """Write audit log entry"""
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Consent Management Demo ===\n")

    manager = ConsentManager(
        storage_dir="data/consent_test",
        audit_log_path="logs/consent_test_audit.jsonl"
    )

    user_id = "user_12345"

    # Give consent for multiple purposes
    print("1. User gives consent for analytics and marketing\n")
    manager.give_consent(
        user_id=user_id,
        purpose=ConsentPurpose.ANALYTICS,
        ip_address="203.0.113.1",
        source="web"
    )
    manager.give_consent(
        user_id=user_id,
        purpose=ConsentPurpose.MARKETING,
        ip_address="203.0.113.1",
        source="web"
    )

    # Check consent
    print("2. Check consents\n")
    has_analytics = manager.has_consent(user_id, ConsentPurpose.ANALYTICS)
    has_profiling = manager.has_consent(user_id, ConsentPurpose.PROFILING)

    print(f"  Has analytics consent: {has_analytics}")
    print(f"  Has profiling consent: {has_profiling}\n")

    # Get all consents
    print("3. Get all user consents\n")
    preferences = manager.get_user_consents(user_id)
    print(f"  User: {preferences.user_id}")
    print(f"  Active consents: {[p.value for p in preferences.get_active_consents()]}\n")

    # Withdraw consent
    print("4. User withdraws marketing consent\n")
    manager.withdraw_consent(
        user_id=user_id,
        purpose=ConsentPurpose.MARKETING,
        ip_address="203.0.113.1"
    )

    # Check again
    preferences = manager.get_user_consents(user_id)
    print(f"  Active consents: {[p.value for p in preferences.get_active_consents()]}\n")

    print("=== Demo complete! ===")
