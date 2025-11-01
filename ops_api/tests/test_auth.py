"""Tests for Ops API authentication."""
import pytest
from app.security import create_access_token, verify_token, hash_password, OpsRole
from datetime import timedelta

def test_create_and_verify_token():
    """Test token creation and verification."""
    token = create_access_token({"sub": "devops@example.com", "roles": [OpsRole.DEVOPS.value]}, timedelta(hours=1))
    claims = verify_token(token)
    assert claims["sub"] == "devops@example.com"
    assert OpsRole.DEVOPS.value in claims["roles"]

def test_hash_password():
    """Test password hashing."""
    password = "testpass123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) == 64  # SHA256 hex digest
