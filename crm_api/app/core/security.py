"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API Security Module.

JWT authentication and role-based access control.
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from enum import Enum

from app.core.config import settings


class Role(str, Enum):
    """CRM user roles."""

    SALES = "SALES"
    SALES_MANAGER = "SALES_MANAGER"
    OWNER = "OWNER"


# Simple JWT implementation for offline testing
# In production, use python-jose or PyJWT


def _base64url_encode(data: bytes) -> str:
    """Base64url encode bytes."""
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    """Base64url decode string."""
    import base64
    # Add padding if needed
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data (should include 'sub' for subject)
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    import json

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS
        )

    to_encode.update({"exp": int(expire.timestamp())})

    # Create JWT (header.payload.signature)
    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = _base64url_encode(json.dumps(header).encode('utf-8'))
    payload_encoded = _base64url_encode(json.dumps(to_encode).encode('utf-8'))

    # Create signature
    message = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_encoded = _base64url_encode(signature)

    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload

    Raises:
        Exception: If token is invalid or expired
    """
    import json

    try:
        # Split token
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        header_encoded, payload_encoded, signature_encoded = parts

        # Verify signature
        message = f"{header_encoded}.{payload_encoded}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_signature_encoded = _base64url_encode(expected_signature)

        if not hmac.compare_digest(signature_encoded, expected_signature_encoded):
            raise ValueError("Invalid signature")

        # Decode payload
        payload_json = _base64url_decode(payload_encoded)
        payload = json.loads(payload_json)

        # Check expiration
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise ValueError("Token expired")

        return payload

    except Exception as e:
        raise Exception(f"Token verification failed: {str(e)}")


def hash_password(password: str) -> str:
    """
    Hash a password (simple version for testing).

    PRODUCTION NOTE: Use passlib or bcrypt for real password hashing.
        pip install passlib[bcrypt]
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        pwd_context.hash(password)
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return hash_password(plain_password) == hashed_password


def check_role(required_roles: list[Role], user_roles: list[str]) -> bool:
    """
    Check if user has required role.

    Args:
        required_roles: List of required roles
        user_roles: List of user's roles

    Returns:
        True if user has at least one required role or is OWNER (universal access)
    """
    # OWNER has universal access
    if Role.OWNER.value in user_roles:
        return True

    required_role_strs = [r.value for r in required_roles]
    return any(role in required_role_strs for role in user_roles)


class RoleGuard:
    """
    Dependency class for role-based access control.

    Usage:
        @router.get("/admin")
        def admin_endpoint(claims: dict = Depends(RoleGuard([Role.OWNER]))):
            ...
    """

    def __init__(self, required_roles: list[Role]):
        self.required_roles = required_roles

    def __call__(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify user has required role.

        Args:
            claims: JWT claims from dependency

        Returns:
            Claims dict if authorized

        Raises:
            Exception: If unauthorized
        """
        user_roles = claims.get("roles", [])

        if not check_role(self.required_roles, user_roles):
            raise Exception(
                f"Forbidden: requires one of {[r.value for r in self.required_roles]}"
            )

        return claims


def verify_twilio_signature(
    url: str,
    params: Dict[str, str],
    signature: str
) -> bool:
    """
    Verify Twilio webhook signature.

    Args:
        url: Full URL of webhook
        params: POST parameters
        signature: X-Twilio-Signature header value

    Returns:
        True if signature is valid
    """
    # Sort params and concatenate
    sorted_params = sorted(params.items())
    data = url + ''.join(f'{k}{v}' for k, v in sorted_params)

    # Compute HMAC-SHA1
    expected = hmac.new(
        settings.TWILIO_AUTH_TOKEN.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha1
    ).digest()

    # Base64 encode
    import base64
    expected_signature = base64.b64encode(expected).decode('utf-8')

    return hmac.compare_digest(signature, expected_signature)


def verify_facebook_signature(payload: str, signature: str) -> bool:
    """
    Verify Facebook webhook signature.

    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header value (format: sha256=...)

    Returns:
        True if signature is valid
    """
    if not signature.startswith('sha256='):
        return False

    signature = signature[7:]  # Remove 'sha256=' prefix

    # Compute HMAC-SHA256
    expected = hmac.new(
        settings.FB_APP_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


__all__ = [
    "Role",
    "create_access_token",
    "verify_token",
    "hash_password",
    "verify_password",
    "check_role",
    "RoleGuard",
    "verify_twilio_signature",
    "verify_facebook_signature",
]
