"""
Field-Level Encryption and Pseudonymization

Provides field-level encryption for PII in database records.

Features:
- Encrypt/decrypt individual fields
- Pseudonymization (one-way hash with salt)
- Deterministic encryption (for searchable fields)
- Access audit logging
- Batch encryption for migrations

Usage:
    kms = KMSStub()
    kek_id = kms.create_master_key("customer-data-key")

    encryptor = FieldEncryptor(kms, kek_id)

    # Encrypt field
    encrypted_email = encryptor.encrypt_field("user@example.com", context={"user_id": "123"})

    # Decrypt field
    plaintext_email = encryptor.decrypt_field(encrypted_email, context={"user_id": "123"})

    # Pseudonymize (one-way)
    hashed_email = encryptor.pseudonymize("user@example.com")
"""

import os
import json
import base64
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .kms_stub import KMSStub

logger = logging.getLogger(__name__)


@dataclass
class FieldEncryptionAudit:
    """Audit log for field encryption/decryption"""
    timestamp: str
    operation: str  # ENCRYPT, DECRYPT, PSEUDONYMIZE
    field_name: Optional[str] = None
    user_id: Optional[str] = None
    service_name: Optional[str] = None
    context: Optional[Dict[str, str]] = None
    result: str = "SUCCESS"


class FieldEncryptor:
    """
    Field-level encryption for database records

    Supports:
    - Random encryption (different ciphertext each time)
    - Deterministic encryption (same plaintext -> same ciphertext, searchable)
    - Context-bound encryption (ciphertext only valid with same context)
    - Access audit logging
    """

    def __init__(
        self,
        kms: KMSStub,
        kek_id: str,
        audit_log_path: str = "logs/field_encryption_audit.jsonl"
    ):
        """
        Initialize field encryptor

        Args:
            kms: KMS instance for key management
            kek_id: Master key ID
            audit_log_path: Path to audit log
        """
        self.kms = kms
        self.kek_id = kek_id
        self.audit_log_path = audit_log_path

        # Generate DEK for this encryptor instance
        self.plaintext_dek, self.encrypted_dek = kms.generate_data_key(kek_id)

    def encrypt_field(
        self,
        plaintext: str,
        field_name: Optional[str] = None,
        context: Optional[Dict[str, str]] = None,
        deterministic: bool = False
    ) -> str:
        """
        Encrypt a single field value

        Args:
            plaintext: Value to encrypt
            field_name: Field name (for audit logging)
            context: Additional context (user_id, record_id, etc.)
            deterministic: If True, same input always produces same output (searchable)

        Returns:
            Base64-encoded encrypted value
        """
        plaintext_bytes = plaintext.encode('utf-8')

        # Additional authenticated data (AAD) from context
        aad = None
        if context:
            aad = json.dumps(context, sort_keys=True).encode('utf-8')

        # Nonce handling
        if deterministic and context:
            # Derive deterministic nonce from context (for searchable encryption)
            nonce = self._derive_deterministic_nonce(plaintext_bytes, context)
        else:
            # Random nonce (default)
            nonce = os.urandom(12)

        # Encrypt
        aesgcm = AESGCM(self.plaintext_dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, aad)

        # Build encrypted field
        # Format: version (1 byte) || nonce (12 bytes) || ciphertext || aad_length (4 bytes) || aad
        version = b'\x01'
        if aad:
            encrypted_field = version + nonce + ciphertext + len(aad).to_bytes(4, 'big') + aad
        else:
            encrypted_field = version + nonce + ciphertext + (0).to_bytes(4, 'big')

        # Audit log
        self._audit_log(FieldEncryptionAudit(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="ENCRYPT",
            field_name=field_name,
            context=context
        ))

        return base64.b64encode(encrypted_field).decode('ascii')

    def decrypt_field(
        self,
        encrypted_value: str,
        field_name: Optional[str] = None,
        context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Decrypt a field value

        Args:
            encrypted_value: Base64-encoded encrypted value
            field_name: Field name (for audit logging)
            context: Context used during encryption (required if used)

        Returns:
            Decrypted plaintext
        """
        encrypted_bytes = base64.b64decode(encrypted_value)

        # Parse encrypted field
        version = encrypted_bytes[0]
        if version != 1:
            raise ValueError(f"Unsupported encryption version: {version}")

        nonce = encrypted_bytes[1:13]

        # Extract AAD
        aad_length = int.from_bytes(encrypted_bytes[-4:], 'big')
        if aad_length > 0:
            aad = encrypted_bytes[-(4 + aad_length):-4]
            ciphertext = encrypted_bytes[13:-(4 + aad_length)]

            # Verify context matches
            if context:
                expected_aad = json.dumps(context, sort_keys=True).encode('utf-8')
                if aad != expected_aad:
                    raise ValueError("Context mismatch - wrong decryption context")
        else:
            aad = None
            ciphertext = encrypted_bytes[13:-4]

        # Decrypt
        aesgcm = AESGCM(self.plaintext_dek)
        try:
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, aad)
            plaintext = plaintext_bytes.decode('utf-8')

            # Audit log
            self._audit_log(FieldEncryptionAudit(
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation="DECRYPT",
                field_name=field_name,
                context=context
            ))

            return plaintext

        except Exception as e:
            # Audit log failure
            self._audit_log(FieldEncryptionAudit(
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation="DECRYPT",
                field_name=field_name,
                context=context,
                result="FAILURE"
            ))
            raise

    def encrypt_record(
        self,
        record: Dict[str, Any],
        fields_to_encrypt: List[str],
        context: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Encrypt multiple fields in a record

        Args:
            record: Record dictionary
            fields_to_encrypt: List of field names to encrypt
            context: Context for encryption

        Returns:
            Record with encrypted fields (original record is not modified)
        """
        encrypted_record = record.copy()

        for field_name in fields_to_encrypt:
            if field_name in record and record[field_name]:
                encrypted_value = self.encrypt_field(
                    str(record[field_name]),
                    field_name=field_name,
                    context=context
                )
                encrypted_record[field_name] = encrypted_value

        return encrypted_record

    def decrypt_record(
        self,
        record: Dict[str, Any],
        fields_to_decrypt: List[str],
        context: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Decrypt multiple fields in a record

        Args:
            record: Record with encrypted fields
            fields_to_decrypt: List of field names to decrypt
            context: Context used during encryption

        Returns:
            Record with decrypted fields
        """
        decrypted_record = record.copy()

        for field_name in fields_to_decrypt:
            if field_name in record and record[field_name]:
                decrypted_value = self.decrypt_field(
                    record[field_name],
                    field_name=field_name,
                    context=context
                )
                decrypted_record[field_name] = decrypted_value

        return decrypted_record

    def _derive_deterministic_nonce(
        self,
        plaintext: bytes,
        context: Dict[str, str]
    ) -> bytes:
        """
        Derive deterministic nonce from plaintext and context

        This enables deterministic encryption (same input -> same output)
        which allows searching encrypted fields.

        WARNING: Only use for fields that need to be searchable.
        Reveals when two records have the same value.
        """
        # Derive nonce using HKDF
        context_bytes = json.dumps(context, sort_keys=True).encode('utf-8')

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=12,  # 96-bit nonce for GCM
            salt=self.plaintext_dek[:16],  # Use part of DEK as salt
            info=context_bytes
        )

        nonce = hkdf.derive(plaintext)
        return nonce

    def _audit_log(self, entry: FieldEncryptionAudit):
        """Write audit log entry"""
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(asdict(entry)) + '\n')


class PseudonymizationEngine:
    """
    Pseudonymization engine

    One-way transformation of PII into pseudonyms:
    - Cannot be reversed (unlike encryption)
    - Same input always produces same output (consistent)
    - Salted to prevent rainbow tables
    - Suitable for analytics, logging, etc.

    Usage:
        engine = PseudonymizationEngine(salt="random-salt-123")

        # Pseudonymize email
        hashed_email = engine.pseudonymize("user@example.com", "email")

        # Pseudonymize IP
        hashed_ip = engine.pseudonymize("192.168.1.1", "ip_address")

        # Verify (without storing original)
        is_match = engine.verify("user@example.com", hashed_email, "email")
    """

    def __init__(
        self,
        salt: Optional[str] = None,
        audit_log_path: str = "logs/pseudonymization_audit.jsonl"
    ):
        """
        Initialize pseudonymization engine

        Args:
            salt: Salt for hashing (generate once, store securely)
            audit_log_path: Path to audit log
        """
        if salt is None:
            # Generate random salt (save this!)
            salt = base64.b64encode(os.urandom(32)).decode('ascii')
            logger.warning(f"Generated random salt: {salt}")
            logger.warning("SAVE THIS SALT! Without it, pseudonyms cannot be verified.")

        self.salt = salt.encode('utf-8')
        self.audit_log_path = audit_log_path

    def pseudonymize(
        self,
        plaintext: str,
        field_type: str = "generic",
        iterations: int = 100000
    ) -> str:
        """
        Pseudonymize a value using PBKDF2

        Args:
            plaintext: Value to pseudonymize
            field_type: Type of field (used as additional context)
            iterations: PBKDF2 iterations (higher = slower but more secure)

        Returns:
            Hex-encoded pseudonym (64 characters)
        """
        # Use field_type as "pepper" in addition to salt
        combined_salt = self.salt + field_type.encode('utf-8')

        # PBKDF2 with SHA-256
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=combined_salt,
            iterations=iterations
        )

        pseudonym = kdf.derive(plaintext.encode('utf-8'))

        # Audit log
        self._audit_log(FieldEncryptionAudit(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="PSEUDONYMIZE",
            field_name=field_type
        ))

        return pseudonym.hex()

    def verify(
        self,
        plaintext: str,
        pseudonym: str,
        field_type: str = "generic",
        iterations: int = 100000
    ) -> bool:
        """
        Verify if plaintext matches pseudonym

        Args:
            plaintext: Original value
            pseudonym: Pseudonym to verify against
            field_type: Type of field (must match original)
            iterations: PBKDF2 iterations (must match original)

        Returns:
            True if match, False otherwise
        """
        computed_pseudonym = self.pseudonymize(plaintext, field_type, iterations)
        return computed_pseudonym == pseudonym

    def pseudonymize_email(self, email: str) -> str:
        """Convenience method for email pseudonymization"""
        return self.pseudonymize(email, field_type="email")

    def pseudonymize_ip(self, ip_address: str) -> str:
        """Convenience method for IP address pseudonymization"""
        return self.pseudonymize(ip_address, field_type="ip_address")

    def pseudonymize_phone(self, phone: str) -> str:
        """Convenience method for phone number pseudonymization"""
        return self.pseudonymize(phone, field_type="phone")

    def _audit_log(self, entry: FieldEncryptionAudit):
        """Write audit log entry"""
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(asdict(entry)) + '\n')


# Example usage and tests
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Field Encryption Demo ===\n")

    from .kms_stub import KMSStub

    # Setup
    kms = KMSStub(keys_dir="keys_test", audit_log_path="logs/kms_test_audit.jsonl")
    kek_id = kms.create_master_key("customer-data-key-test")

    encryptor = FieldEncryptor(kms, kek_id, audit_log_path="logs/field_test_audit.jsonl")

    # 1. Basic field encryption
    email = "alice@example.com"
    encrypted_email = encryptor.encrypt_field(email, field_name="email")
    print(f"✓ Encrypted email: {encrypted_email[:50]}...")

    decrypted_email = encryptor.decrypt_field(encrypted_email, field_name="email")
    assert decrypted_email == email
    print(f"✓ Decrypted email: {decrypted_email}\n")

    # 2. Context-bound encryption
    ssn = "123-45-6789"
    context = {"user_id": "user_12345", "purpose": "kyc"}

    encrypted_ssn = encryptor.encrypt_field(ssn, field_name="ssn", context=context)
    print(f"✓ Encrypted SSN with context: {encrypted_ssn[:50]}...")

    # Can decrypt with correct context
    decrypted_ssn = encryptor.decrypt_field(encrypted_ssn, field_name="ssn", context=context)
    assert decrypted_ssn == ssn
    print(f"✓ Decrypted with correct context: {decrypted_ssn}")

    # Cannot decrypt with wrong context
    try:
        wrong_context = {"user_id": "different_user", "purpose": "kyc"}
        encryptor.decrypt_field(encrypted_ssn, field_name="ssn", context=wrong_context)
        print("✗ Should have failed with wrong context!")
    except ValueError as e:
        print(f"✓ Correctly rejected wrong context: {e}\n")

    # 3. Deterministic encryption (searchable)
    email2 = "bob@example.com"
    search_context = {"field": "email", "table": "customers"}

    enc1 = encryptor.encrypt_field(email2, context=search_context, deterministic=True)
    enc2 = encryptor.encrypt_field(email2, context=search_context, deterministic=True)

    assert enc1 == enc2
    print(f"✓ Deterministic encryption: same input -> same output")
    print(f"  Can search encrypted field: {enc1[:50]}...\n")

    # 4. Record encryption
    customer_record = {
        "id": 12345,
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "+1-555-0100",
        "address": "123 Main St",
        "city": "Springfield"
    }

    encrypted_record = encryptor.encrypt_record(
        customer_record,
        fields_to_encrypt=["email", "phone", "address"],
        context={"record_id": "12345"}
    )

    print("✓ Encrypted customer record:")
    print(f"  id: {encrypted_record['id']}")
    print(f"  name: {encrypted_record['name']}")
    print(f"  email (encrypted): {encrypted_record['email'][:50]}...")
    print(f"  phone (encrypted): {encrypted_record['phone'][:50]}...")
    print(f"  address (encrypted): {encrypted_record['address'][:50]}...\n")

    decrypted_record = encryptor.decrypt_record(
        encrypted_record,
        fields_to_decrypt=["email", "phone", "address"],
        context={"record_id": "12345"}
    )

    assert decrypted_record == customer_record
    print("✓ Decrypted customer record matches original\n")

    # 5. Pseudonymization
    print("=== Pseudonymization Demo ===\n")

    pseudo_engine = PseudonymizationEngine(
        salt="my-secure-salt-123",
        audit_log_path="logs/pseudo_test_audit.jsonl"
    )

    # Pseudonymize for analytics
    email_hash = pseudo_engine.pseudonymize_email("analytics@example.com")
    ip_hash = pseudo_engine.pseudonymize_ip("192.168.1.100")
    phone_hash = pseudo_engine.pseudonymize_phone("+1-555-0199")

    print(f"✓ Pseudonymized email: {email_hash}")
    print(f"✓ Pseudonymized IP: {ip_hash}")
    print(f"✓ Pseudonymized phone: {phone_hash}\n")

    # Verify
    assert pseudo_engine.verify("analytics@example.com", email_hash, "email")
    assert not pseudo_engine.verify("wrong@example.com", email_hash, "email")
    print("✓ Pseudonym verification works\n")

    print("=== All tests passed! ===")
