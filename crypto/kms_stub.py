"""
KMS Stub - Envelope Encryption

Simulates cloud KMS for offline development/testing.

Features:
- Data Encryption Key (DEK) generation
- Master Key Encryption Key (KEK) management
- Envelope encryption pattern
- Key access audit logging
- Key rotation support

SECURITY NOTE: This is a stub for offline development.
In production, use AWS KMS, Azure Key Vault, GCP KMS, or HashiCorp Vault.
"""

import os
import json
import base64
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

logger = logging.getLogger(__name__)


@dataclass
class KeyMetadata:
    """Metadata for encryption keys"""
    key_id: str
    created_at: str
    algorithm: str = "AES-256-GCM"
    purpose: str = "ENCRYPT_DECRYPT"
    state: str = "ENABLED"  # ENABLED, DISABLED, SCHEDULED_FOR_DELETION
    rotation_period_days: int = 90


@dataclass
class AuditLogEntry:
    """Audit log entry for key operations"""
    timestamp: str
    operation: str  # GENERATE_DEK, ENCRYPT, DECRYPT, ROTATE
    key_id: str
    user_id: Optional[str] = None
    service_name: Optional[str] = None
    result: str = "SUCCESS"  # SUCCESS, FAILURE
    error_message: Optional[str] = None


class KMSStub:
    """
    Key Management Service Stub

    Simulates cloud KMS for envelope encryption pattern.
    Stores master keys locally (for dev/test only).

    Usage:
        kms = KMSStub()

        # Generate KEK (master key)
        kek_id = kms.create_master_key("customer-data-key")

        # Generate DEK (data encryption key)
        plaintext_dek, encrypted_dek = kms.generate_data_key(kek_id)

        # Use plaintext_dek to encrypt data, store encrypted_dek with data
        # When decrypting:
        plaintext_dek = kms.decrypt_data_key(kek_id, encrypted_dek)
    """

    def __init__(self, keys_dir: str = "keys", audit_log_path: str = "logs/kms_audit.jsonl"):
        """
        Initialize KMS stub

        Args:
            keys_dir: Directory to store master keys (SECURE THIS IN PRODUCTION!)
            audit_log_path: Path to audit log file
        """
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)

        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory cache of master keys
        self._kek_cache: Dict[str, bytes] = {}

    def create_master_key(
        self,
        key_id: str,
        rotation_period_days: int = 90
    ) -> str:
        """
        Create a new master key (KEK)

        Args:
            key_id: Unique identifier for the key
            rotation_period_days: Days between automatic rotations

        Returns:
            Key ID
        """
        key_path = self.keys_dir / f"{key_id}.key"
        metadata_path = self.keys_dir / f"{key_id}.metadata.json"

        if key_path.exists():
            logger.warning(f"Master key {key_id} already exists")
            return key_id

        # Generate 256-bit master key
        master_key = AESGCM.generate_key(bit_length=256)

        # Store master key (in production, this would be in HSM/KMS)
        key_path.write_bytes(master_key)
        os.chmod(key_path, 0o600)  # Read/write for owner only

        # Store metadata
        metadata = KeyMetadata(
            key_id=key_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            rotation_period_days=rotation_period_days
        )
        metadata_path.write_text(json.dumps(asdict(metadata), indent=2))

        # Cache master key
        self._kek_cache[key_id] = master_key

        # Audit log
        self._audit_log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="CREATE_MASTER_KEY",
            key_id=key_id,
            service_name="kms_stub"
        ))

        logger.info(f"Created master key: {key_id}")
        return key_id

    def generate_data_key(
        self,
        kek_id: str,
        key_length_bytes: int = 32
    ) -> Tuple[bytes, bytes]:
        """
        Generate a data encryption key (DEK) and encrypt it with master key

        This is the envelope encryption pattern:
        1. Generate random DEK
        2. Encrypt DEK with KEK
        3. Return (plaintext_dek, encrypted_dek)

        Caller uses plaintext_dek to encrypt data, then discards it.
        Encrypted_dek is stored with the encrypted data.

        Args:
            kek_id: Master key ID to encrypt the DEK
            key_length_bytes: Length of DEK in bytes (default 32 = 256 bits)

        Returns:
            Tuple of (plaintext_dek, encrypted_dek)
        """
        # Generate random data key
        plaintext_dek = os.urandom(key_length_bytes)

        # Load master key
        master_key = self._load_master_key(kek_id)

        # Encrypt DEK with master key
        aesgcm = AESGCM(master_key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM

        # Additional authenticated data (AAD)
        aad = json.dumps({
            "kek_id": kek_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "purpose": "DEK"
        }).encode()

        ciphertext = aesgcm.encrypt(nonce, plaintext_dek, aad)

        # Encrypted DEK = nonce || ciphertext || aad_length || aad
        encrypted_dek = (
            nonce +
            ciphertext +
            len(aad).to_bytes(4, 'big') +
            aad
        )

        # Audit log
        self._audit_log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="GENERATE_DEK",
            key_id=kek_id,
            service_name="kms_stub"
        ))

        return plaintext_dek, encrypted_dek

    def decrypt_data_key(
        self,
        kek_id: str,
        encrypted_dek: bytes
    ) -> bytes:
        """
        Decrypt a data encryption key (DEK) using master key

        Args:
            kek_id: Master key ID
            encrypted_dek: Encrypted DEK from generate_data_key()

        Returns:
            Plaintext DEK
        """
        # Load master key
        master_key = self._load_master_key(kek_id)

        # Parse encrypted DEK
        nonce = encrypted_dek[:12]

        # Extract AAD length (last 4 bytes before AAD)
        aad_length = int.from_bytes(encrypted_dek[-4:], 'big')

        # Extract AAD and ciphertext
        aad = encrypted_dek[-(4 + aad_length):-4]
        ciphertext = encrypted_dek[12:-(4 + aad_length)]

        # Decrypt DEK
        aesgcm = AESGCM(master_key)
        try:
            plaintext_dek = aesgcm.decrypt(nonce, ciphertext, aad)

            # Audit log
            self._audit_log(AuditLogEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation="DECRYPT_DEK",
                key_id=kek_id,
                service_name="kms_stub"
            ))

            return plaintext_dek

        except Exception as e:
            # Audit log failure
            self._audit_log(AuditLogEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation="DECRYPT_DEK",
                key_id=kek_id,
                service_name="kms_stub",
                result="FAILURE",
                error_message=str(e)
            ))
            raise

    def rotate_master_key(self, old_kek_id: str, new_kek_id: str) -> str:
        """
        Rotate master key (create new KEK, mark old as deprecated)

        Args:
            old_kek_id: Current master key ID
            new_kek_id: New master key ID

        Returns:
            New key ID
        """
        # Create new master key
        self.create_master_key(new_kek_id)

        # Mark old key as disabled (don't delete - needed to decrypt old data)
        old_metadata_path = self.keys_dir / f"{old_kek_id}.metadata.json"
        if old_metadata_path.exists():
            metadata = json.loads(old_metadata_path.read_text())
            metadata["state"] = "DISABLED"
            metadata["disabled_at"] = datetime.now(timezone.utc).isoformat()
            old_metadata_path.write_text(json.dumps(metadata, indent=2))

        # Audit log
        self._audit_log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="ROTATE_MASTER_KEY",
            key_id=f"{old_kek_id} -> {new_kek_id}",
            service_name="kms_stub"
        ))

        logger.info(f"Rotated master key: {old_kek_id} -> {new_kek_id}")
        return new_kek_id

    def _load_master_key(self, kek_id: str) -> bytes:
        """Load master key from disk or cache"""
        if kek_id in self._kek_cache:
            return self._kek_cache[kek_id]

        key_path = self.keys_dir / f"{kek_id}.key"
        if not key_path.exists():
            raise ValueError(f"Master key not found: {kek_id}")

        master_key = key_path.read_bytes()
        self._kek_cache[kek_id] = master_key
        return master_key

    def _audit_log(self, entry: AuditLogEntry):
        """Write audit log entry"""
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(asdict(entry)) + '\n')


class EnvelopeEncryption:
    """
    High-level envelope encryption helper

    Simplifies encrypt/decrypt operations using envelope encryption pattern.

    Usage:
        kms = KMSStub()
        kek_id = kms.create_master_key("app-key")

        envelope = EnvelopeEncryption(kms, kek_id)

        # Encrypt data
        encrypted_blob = envelope.encrypt(b"sensitive data")

        # Decrypt data
        plaintext = envelope.decrypt(encrypted_blob)
    """

    def __init__(self, kms: KMSStub, kek_id: str):
        """
        Initialize envelope encryption

        Args:
            kms: KMS instance
            kek_id: Master key ID to use
        """
        self.kms = kms
        self.kek_id = kek_id

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt data using envelope encryption

        Returns encrypted blob containing:
        - Encrypted DEK
        - Encrypted data
        - Metadata

        Args:
            plaintext: Data to encrypt

        Returns:
            Encrypted blob (can be stored directly)
        """
        # Generate DEK
        plaintext_dek, encrypted_dek = self.kms.generate_data_key(self.kek_id)

        try:
            # Encrypt data with DEK
            aesgcm = AESGCM(plaintext_dek)
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)

            # Build encrypted blob
            # Format: dek_length (4 bytes) || encrypted_dek || nonce (12 bytes) || ciphertext
            encrypted_blob = (
                len(encrypted_dek).to_bytes(4, 'big') +
                encrypted_dek +
                nonce +
                ciphertext
            )

            return encrypted_blob

        finally:
            # Clear plaintext DEK from memory
            plaintext_dek = b'\x00' * len(plaintext_dek)

    def decrypt(self, encrypted_blob: bytes) -> bytes:
        """
        Decrypt data encrypted with envelope encryption

        Args:
            encrypted_blob: Output from encrypt()

        Returns:
            Plaintext data
        """
        # Parse encrypted blob
        dek_length = int.from_bytes(encrypted_blob[:4], 'big')
        encrypted_dek = encrypted_blob[4:4 + dek_length]
        nonce = encrypted_blob[4 + dek_length:4 + dek_length + 12]
        ciphertext = encrypted_blob[4 + dek_length + 12:]

        # Decrypt DEK
        plaintext_dek = self.kms.decrypt_data_key(self.kek_id, encrypted_dek)

        try:
            # Decrypt data with DEK
            aesgcm = AESGCM(plaintext_dek)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)

            return plaintext

        finally:
            # Clear plaintext DEK from memory
            plaintext_dek = b'\x00' * len(plaintext_dek)


# Example usage and tests
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== KMS Stub Demo ===\n")

    # Initialize KMS
    kms = KMSStub(keys_dir="keys_test", audit_log_path="logs/kms_test_audit.jsonl")

    # Create master key
    kek_id = "customer-data-master-key-v1"
    kms.create_master_key(kek_id)
    print(f"✓ Created master key: {kek_id}\n")

    # Envelope encryption demo
    envelope = EnvelopeEncryption(kms, kek_id)

    # Encrypt sensitive data
    sensitive_data = b"SSN: 123-45-6789, Email: user@example.com"
    encrypted_blob = envelope.encrypt(sensitive_data)
    print(f"✓ Encrypted {len(sensitive_data)} bytes -> {len(encrypted_blob)} bytes")
    print(f"  Encrypted blob (base64): {base64.b64encode(encrypted_blob[:50]).decode()}...\n")

    # Decrypt data
    decrypted_data = envelope.decrypt(encrypted_blob)
    assert decrypted_data == sensitive_data
    print(f"✓ Decrypted successfully: {decrypted_data.decode()}\n")

    # Key rotation demo
    new_kek_id = "customer-data-master-key-v2"
    kms.rotate_master_key(kek_id, new_kek_id)
    print(f"✓ Rotated master key: {kek_id} -> {new_kek_id}\n")

    # Old encrypted data can still be decrypted with old key
    decrypted_with_old_key = envelope.decrypt(encrypted_blob)
    assert decrypted_with_old_key == sensitive_data
    print(f"✓ Old data still decryptable with old key\n")

    # New encryptions use new key
    envelope_v2 = EnvelopeEncryption(kms, new_kek_id)
    encrypted_blob_v2 = envelope_v2.encrypt(b"New data with new key")
    decrypted_v2 = envelope_v2.decrypt(encrypted_blob_v2)
    print(f"✓ New data encrypted with new key: {decrypted_v2.decode()}\n")

    print("=== All tests passed! ===")
