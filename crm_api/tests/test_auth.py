"""Tests for authentication endpoints."""

import pytest
from app.api.routes.auth import login
from app.schemas.auth import LoginRequest
from app.core.security import verify_token, hash_password
from app.models import User
from datetime import datetime


def test_login_success(db):
    """Test successful login with valid credentials."""
    request = LoginRequest(
        email="sales@example.com",
        password="password123"
    )

    result = login(request, db)

    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.token_type == "bearer"

    # Verify token can be decoded
    claims = verify_token(result.access_token)
    assert claims["sub"] == "sales@example.com"
    assert "SALES" in claims["roles"]


def test_login_invalid_email(db):
    """Test login with non-existent email."""
    request = LoginRequest(
        email="nonexistent@example.com",
        password="password123"
    )

    with pytest.raises(Exception) as exc_info:
        login(request, db)

    assert "Invalid email or password" in str(exc_info.value)


def test_login_invalid_password(db):
    """Test login with incorrect password."""
    request = LoginRequest(
        email="sales@example.com",
        password="wrongpassword"
    )

    with pytest.raises(Exception) as exc_info:
        login(request, db)

    assert "Invalid email or password" in str(exc_info.value)


def test_login_inactive_user(db):
    """Test login with inactive user account."""
    # Create inactive user
    inactive_user = User(
        id=999,
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        full_name="Inactive User",
        roles=["SALES"],
        is_active=False,
        created_at=datetime.utcnow(),
    )
    db.add(inactive_user)
    db.commit()

    request = LoginRequest(
        email="inactive@example.com",
        password="password123"
    )

    with pytest.raises(Exception) as exc_info:
        login(request, db)

    assert "inactive" in str(exc_info.value).lower()


def test_token_expiration():
    """Test that expired tokens are rejected."""
    from app.core.security import create_access_token
    from datetime import timedelta
    import time

    # Create token that expires immediately
    token = create_access_token(
        data={"sub": "test@example.com", "roles": ["SALES"]},
        expires_delta=timedelta(seconds=1)
    )

    # Wait for expiration
    time.sleep(2)

    # Token should be expired
    with pytest.raises(Exception) as exc_info:
        verify_token(token)

    assert "expired" in str(exc_info.value).lower()


def test_multiple_roles(db):
    """Test login with user having multiple roles."""
    request = LoginRequest(
        email="owner@example.com",
        password="password123"
    )

    result = login(request, db)
    claims = verify_token(result.access_token)

    assert "OWNER" in claims["roles"]
