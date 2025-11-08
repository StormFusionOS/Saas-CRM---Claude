"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Integration Settings Model
Stores encrypted configuration for external service integrations
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base
from app.core.encryption import get_encryption_service
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class IntegrationSetting(Base):
    """
    Stores configuration for external integrations (AI Node, payment gateways, etc.)

    Secrets are encrypted at rest using Fernet (see app.core.encryption).
    Each integration is identified by a namespace (e.g., 'ai_node').
    """
    __tablename__ = "integration_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Namespace identifies the integration (e.g., 'ai_node', 'stripe', 'sendgrid')
    namespace = Column(String(100), nullable=False, unique=True, index=True)

    # Configuration fields (JSON-like key-value pairs)
    base_url = Column(String(500), nullable=True, comment="Base URL for API calls")
    encrypted_secret = Column(Text, nullable=True, comment="Encrypted bearer token or API key (Fernet)")

    # Feature flags
    review_mode = Column(Boolean, nullable=False, default=True, comment="Require human review for actions")
    enabled = Column(Boolean, nullable=False, default=True, comment="Whether integration is active")

    # Health check metadata
    last_ping_status = Column(String(50), nullable=True, comment="Status of last connection test")
    last_ping_latency_ms = Column(Integer, nullable=True, comment="Latency of last ping in milliseconds")
    last_ping_at = Column(DateTime(timezone=True), nullable=True, comment="Timestamp of last ping test")

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True, comment="User ID who created this config")
    updated_by = Column(Integer, nullable=True, comment="User ID who last updated this config")

    __table_args__ = (
        Index('idx_integration_namespace', 'namespace'),
    )

    def set_secret(self, plaintext_secret: Optional[str]) -> None:
        """
        Encrypt and store a secret (bearer token, API key, etc.)

        Args:
            plaintext_secret: Unencrypted secret value (or None to clear)
        """
        if plaintext_secret is None:
            self.encrypted_secret = None
            logger.info("integration_secret_cleared", namespace=self.namespace)
            return

        encryption_service = get_encryption_service()
        self.encrypted_secret = encryption_service.encrypt(plaintext_secret)
        logger.info("integration_secret_set", namespace=self.namespace)

    def get_secret(self) -> Optional[str]:
        """
        Decrypt and return the stored secret.

        Returns:
            Decrypted secret string, or None if not set

        Raises:
            ValueError: If decryption fails
        """
        if not self.encrypted_secret:
            return None

        encryption_service = get_encryption_service()
        return encryption_service.decrypt(self.encrypted_secret)

    def has_secret(self) -> bool:
        """
        Check if a secret is configured (without decrypting it).

        Returns:
            True if secret is set, False otherwise
        """
        return self.encrypted_secret is not None and len(self.encrypted_secret) > 0

    def __repr__(self):
        return f"<IntegrationSetting(namespace={self.namespace}, enabled={self.enabled}, has_secret={self.has_secret()})>"
