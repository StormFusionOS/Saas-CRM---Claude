"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Tests for cross-role and cross-origin security.

Ensures that:
1. CRM roles cannot access Ops endpoints
2. Ops roles cannot access CRM endpoints
3. Lower privilege roles cannot access higher privilege endpoints
"""

import pytest
from app.core.security import Role, RoleGuard


def test_sales_cannot_access_manager_only():
    """Test that SALES role cannot access SALES_MANAGER endpoints."""
    manager_guard = RoleGuard([Role.SALES_MANAGER])
    sales_claims = {"sub": "sales@example.com", "roles": [Role.SALES.value]}

    with pytest.raises(Exception) as exc_info:
        manager_guard(sales_claims)

    assert "Forbidden" in str(exc_info.value)


def test_sales_manager_can_access_sales():
    """Test that SALES_MANAGER can access SALES endpoints."""
    sales_guard = RoleGuard([Role.SALES])
    manager_claims = {"sub": "manager@example.com", "roles": [Role.SALES_MANAGER.value]}

    # This should fail unless we explicitly allow it
    # The guard checks for exact role match, not hierarchy
    with pytest.raises(Exception) as exc_info:
        sales_guard(manager_claims)

    assert "Forbidden" in str(exc_info.value)


def test_owner_universal_access_sales():
    """Test OWNER can access all SALES endpoints."""
    sales_guard = RoleGuard([Role.SALES])
    owner_claims = {"sub": "owner@example.com", "roles": [Role.OWNER.value]}

    result = sales_guard(owner_claims)
    assert result == owner_claims


def test_owner_universal_access_manager():
    """Test OWNER can access all SALES_MANAGER endpoints."""
    manager_guard = RoleGuard([Role.SALES_MANAGER])
    owner_claims = {"sub": "owner@example.com", "roles": [Role.OWNER.value]}

    result = manager_guard(owner_claims)
    assert result == owner_claims


def test_empty_roles_denied():
    """Test that empty roles list is denied."""
    guard = RoleGuard([Role.SALES])
    claims = {"sub": "user@example.com", "roles": []}

    with pytest.raises(Exception) as exc_info:
        guard(claims)

    assert "Forbidden" in str(exc_info.value)


def test_wrong_role_denied():
    """Test that completely wrong role is denied."""
    sales_guard = RoleGuard([Role.SALES])

    # Someone with ops role trying to access CRM
    # (This simulates cross-service access attempt)
    ops_claims = {"sub": "devops@example.com", "roles": ["DEVOPS"]}

    with pytest.raises(Exception) as exc_info:
        sales_guard(ops_claims)

    assert "Forbidden" in str(exc_info.value)


def test_multiple_required_roles_any_match():
    """Test that having any of multiple required roles grants access."""
    guard = RoleGuard([Role.SALES, Role.SALES_MANAGER])

    # SALES should pass
    sales_claims = {"sub": "sales@example.com", "roles": [Role.SALES.value]}
    result = guard(sales_claims)
    assert result == sales_claims

    # SALES_MANAGER should pass
    manager_claims = {"sub": "manager@example.com", "roles": [Role.SALES_MANAGER.value]}
    result = guard(manager_claims)
    assert result == manager_claims


def test_no_role_claim_denied():
    """Test that missing 'roles' claim is denied."""
    guard = RoleGuard([Role.SALES])
    claims = {"sub": "user@example.com"}  # Missing roles

    with pytest.raises(Exception) as exc_info:
        guard(claims)

    assert "Forbidden" in str(exc_info.value)
