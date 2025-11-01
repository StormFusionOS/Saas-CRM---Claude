"""
Ops API Security Module.

JWT authentication and role-based access for ops users.
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from enum import Enum

from app.core.config import settings


class OpsRole(str, Enum):
    """Ops user roles."""

    SEO_ENGINEER = "SEO_ENGINEER"
    DEVOPS = "DEVOPS"
    OWNER = "OWNER"


def _base64url_encode(data: bytes) -> str:
    """Base64url encode bytes."""
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    """Base64url decode string."""
    import base64
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    import json

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS))
    to_encode.update({"exp": int(expire.timestamp())})

    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = _base64url_encode(json.dumps(header).encode('utf-8'))
    payload_encoded = _base64url_encode(json.dumps(to_encode).encode('utf-8'))

    message = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    signature_encoded = _base64url_encode(signature)

    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token."""
    import json

    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid token format")

    header_encoded, payload_encoded, signature_encoded = parts
    message = f"{header_encoded}.{payload_encoded}"
    expected_signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    expected_signature_encoded = _base64url_encode(expected_signature)

    if not hmac.compare_digest(signature_encoded, expected_signature_encoded):
        raise ValueError("Invalid signature")

    payload = json.loads(_base64url_decode(payload_encoded))
    if datetime.utcnow().timestamp() > payload.get('exp', 0):
        raise ValueError("Token expired")

    return payload


def hash_password(password: str) -> str:
    """Hash password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return hash_password(plain_password) == hashed_password


class OpsRoleGuard:
    """Role guard for ops endpoints."""

    def __init__(self, required_roles: list[OpsRole]):
        self.required_roles = required_roles

    def __call__(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """Verify user has required role. OWNER has universal access."""
        user_roles = claims.get("roles", [])

        # OWNER has universal access
        if OpsRole.OWNER.value in user_roles:
            return claims

        required_role_strs = [r.value for r in self.required_roles]

        if not any(role in required_role_strs for role in user_roles):
            raise Exception(f"Forbidden: requires one of {required_role_strs}")

        return claims


__all__ = ["OpsRole", "create_access_token", "verify_token", "hash_password", "verify_password", "OpsRoleGuard"]
