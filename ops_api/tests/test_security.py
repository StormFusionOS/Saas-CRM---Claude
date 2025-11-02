"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Tests for Ops API security."""

import pytest
from datetime import timedelta
from app.security import (
    OpsRole,
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
    OpsRoleGuard,
)


def test_ops_role_enum():
    """Test OpsRole enum values."""
    assert OpsRole.SEO_ENGINEER.value == "SEO_ENGINEER"
    assert OpsRole.DEVOPS.value == "DEVOPS"
    assert OpsRole.OWNER.value == "OWNER"


def test_create_and_verify_token():
    """Test JWT token creation and verification."""
    data = {
        "sub": "Nathan@RiverCityClean.com",
        "user_id": 1,
        "roles": [OpsRole.DEVOPS.value]
    }

    token = create_access_token(data, timedelta(hours=1))

    assert token is not None
    assert isinstance(token, str)
    assert len(token.split('.')) == 3  # JWT has 3 parts

    # Verify token
    claims = verify_token(token)
    assert claims["sub"] == "Nathan@RiverCityClean.com"
    assert OpsRole.DEVOPS.value in claims["roles"]


def test_token_expiration():
    """Test expired tokens are rejected."""
    import time

    data = {"sub": "test@example.com", "roles": ["DEVOPS"]}
    token = create_access_token(data, timedelta(seconds=1))

    # Wait for expiration
    time.sleep(2)

    with pytest.raises(Exception) as exc_info:
        verify_token(token)

    assert "expired" in str(exc_info.value).lower()


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"

    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) == 64  # SHA256 hex digest

    # Verify correct password
    assert verify_password(password, hashed) is True

    # Verify incorrect password
    assert verify_password("wrongpassword", hashed) is False


def test_ops_role_guard_authorized():
    """Test OpsRoleGuard allows authorized users."""
    guard = OpsRoleGuard([OpsRole.DEVOPS])
    claims = {
        "sub": "test@example.com",
        "roles": [OpsRole.DEVOPS.value]
    }

    result = guard(claims)
    assert result == claims


def test_ops_role_guard_unauthorized():
    """Test OpsRoleGuard blocks unauthorized users."""
    guard = OpsRoleGuard([OpsRole.OWNER])
    claims = {
        "sub": "test@example.com",
        "roles": [OpsRole.DEVOPS.value]
    }

    with pytest.raises(Exception) as exc_info:
        guard(claims)

    assert "Forbidden" in str(exc_info.value)


def test_owner_has_universal_access():
    """Test OWNER role has access to all guards."""
    # OWNER should pass DEVOPS guard
    devops_guard = OpsRoleGuard([OpsRole.DEVOPS])
    owner_claims = {"sub": "owner@example.com", "roles": [OpsRole.OWNER.value]}

    result = devops_guard(owner_claims)
    assert result == owner_claims

    # OWNER should pass SEO guard
    seo_guard = OpsRoleGuard([OpsRole.SEO_ENGINEER])
    result = seo_guard(owner_claims)
    assert result == owner_claims


def test_multiple_roles():
    """Test user with multiple roles."""
    guard = OpsRoleGuard([OpsRole.SEO_ENGINEER, OpsRole.DEVOPS])
    claims = {
        "sub": "test@example.com",
        "roles": [OpsRole.SEO_ENGINEER.value]
    }

    result = guard(claims)
    assert result == claims
