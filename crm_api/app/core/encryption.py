"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

At-rest encryption utilities using Fernet (symmetric encryption)
Used for storing sensitive integration secrets in database
"""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class EncryptionService:
    """
    Handles encryption/decryption of sensitive data at rest using Fernet.

    Fernet guarantees that a message encrypted using it cannot be manipulated
    or read without the key. Uses AES 128 in CBC mode with PKCS7 padding and HMAC.
    """

    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption service.

        Args:
            key: Fernet key (32 url-safe base64-encoded bytes).
                 If None, reads from ENCRYPTION_KEY env var.

        Raises:
            ValueError: If no key provided and ENCRYPTION_KEY not set
        """
        if key is None:
            key_str = os.getenv('ENCRYPTION_KEY')
            if not key_str:
                raise ValueError(
                    "ENCRYPTION_KEY environment variable must be set. "
                    "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
                )
            key = key_str.encode()

        try:
            self.fernet = Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {e}")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted string (safe for DB storage)
        """
        if not plaintext:
            return plaintext

        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise ValueError(f"Encryption failed: {e}")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.

        Args:
            ciphertext: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If decryption fails (invalid key or corrupted data)
        """
        if not ciphertext:
            return ciphertext

        try:
            decrypted_bytes = self.fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            logger.error("decryption_failed", reason="invalid_token_or_key")
            raise ValueError("Decryption failed: Invalid token or encryption key")
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise ValueError(f"Decryption failed: {e}")


# Global instance (lazily initialized)
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get global encryption service instance (singleton pattern).

    Returns:
        EncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
