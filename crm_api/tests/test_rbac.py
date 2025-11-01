"""Tests for role-based access control."""

import pytest
from app.core.security import Role, RoleGuard, check_role


def test_check_role_single_match():
    """Test role check with single matching role."""
    required = [Role.SALES]
    user_roles = ["SALES", "ANOTHER"]

    assert check_role(required, user_roles) is True


def test_check_role_multiple_options():
    """Test role check with multiple required options."""
    required = [Role.SALES, Role.SALES_MANAGER]
    user_roles = ["SALES"]

    assert check_role(required, user_roles) is True


def test_check_role_no_match():
    """Test role check with no matching roles."""
    required = [Role.OWNER]
    user_roles = ["SALES"]

    assert check_role(required, user_roles) is False


def test_role_guard_authorized():
    """Test RoleGuard allows authorized users."""
    guard = RoleGuard([Role.SALES])
    claims = {"sub": "user@example.com", "roles": ["SALES"]}

    result = guard(claims)
    assert result == claims


def test_role_guard_unauthorized():
    """Test RoleGuard blocks unauthorized users."""
    guard = RoleGuard([Role.OWNER])
    claims = {"sub": "user@example.com", "roles": ["SALES"]}

    with pytest.raises(Exception) as exc_info:
        guard(claims)

    assert "Forbidden" in str(exc_info.value)


def test_manager_access():
    """Test that managers have elevated access."""
    guard = RoleGuard([Role.SALES_MANAGER, Role.OWNER])
    claims = {"sub": "manager@example.com", "roles": ["SALES_MANAGER"]}

    result = guard(claims)
    assert result == claims


def test_owner_access_all():
    """Test that owners can access everything."""
    # Owner should pass SALES guard
    sales_guard = RoleGuard([Role.SALES])
    owner_claims = {"sub": "owner@example.com", "roles": ["OWNER"]}

    result = sales_guard(owner_claims)
    assert result == owner_claims

    # Owner should pass MANAGER guard
    manager_guard = RoleGuard([Role.SALES_MANAGER])
    result = manager_guard(owner_claims)
    assert result == owner_claims
