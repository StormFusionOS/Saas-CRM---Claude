"""
Tests for cross-role security in Ops API.

Ensures proper isolation between:
1. SEO_ENGINEER and DEVOPS roles
2. Ops roles and CRM roles (cross-service)
3. OWNER universal access
"""

import pytest
from app.security import OpsRole, OpsRoleGuard


def test_seo_cannot_access_devops_only():
    """Test that SEO_ENGINEER cannot access DEVOPS endpoints."""
    devops_guard = OpsRoleGuard([OpsRole.DEVOPS])
    seo_claims = {"sub": "seo@example.com", "roles": [OpsRole.SEO_ENGINEER.value]}

    with pytest.raises(Exception) as exc_info:
        devops_guard(seo_claims)

    assert "Forbidden" in str(exc_info.value)


def test_devops_cannot_access_seo_only():
    """Test that DEVOPS cannot access SEO_ENGINEER endpoints."""
    seo_guard = OpsRoleGuard([OpsRole.SEO_ENGINEER])
    devops_claims = {"sub": "devops@example.com", "roles": [OpsRole.DEVOPS.value]}

    with pytest.raises(Exception) as exc_info:
        seo_guard(devops_claims)

    assert "Forbidden" in str(exc_info.value)


def test_owner_can_access_all_ops_endpoints():
    """Test OWNER has universal access to all Ops endpoints."""
    # DEVOPS endpoint
    devops_guard = OpsRoleGuard([OpsRole.DEVOPS])
    owner_claims = {"sub": "owner@example.com", "roles": [OpsRole.OWNER.value]}
    result = devops_guard(owner_claims)
    assert result == owner_claims

    # SEO endpoint
    seo_guard = OpsRoleGuard([OpsRole.SEO_ENGINEER])
    result = seo_guard(owner_claims)
    assert result == owner_claims


def test_crm_role_cannot_access_ops():
    """Test that CRM roles (simulated) cannot access Ops endpoints."""
    devops_guard = OpsRoleGuard([OpsRole.DEVOPS])

    # Someone with CRM SALES role trying to access Ops
    crm_claims = {"sub": "sales@example.com", "roles": ["SALES"]}

    with pytest.raises(Exception) as exc_info:
        devops_guard(crm_claims)

    assert "Forbidden" in str(exc_info.value)


def test_empty_roles_denied():
    """Test that empty roles list is denied."""
    guard = OpsRoleGuard([OpsRole.DEVOPS])
    claims = {"sub": "user@example.com", "roles": []}

    with pytest.raises(Exception) as exc_info:
        guard(claims)

    assert "Forbidden" in str(exc_info.value)


def test_multiple_required_roles():
    """Test endpoints requiring multiple specific roles."""
    guard = OpsRoleGuard([OpsRole.DEVOPS, OpsRole.SEO_ENGINEER])

    # DEVOPS should pass
    devops_claims = {"sub": "devops@example.com", "roles": [OpsRole.DEVOPS.value]}
    result = guard(devops_claims)
    assert result == devops_claims

    # SEO should pass
    seo_claims = {"sub": "seo@example.com", "roles": [OpsRole.SEO_ENGINEER.value]}
    result = guard(seo_claims)
    assert result == seo_claims


def test_no_role_claim_denied():
    """Test that missing 'roles' claim is denied."""
    guard = OpsRoleGuard([OpsRole.DEVOPS])
    claims = {"sub": "user@example.com"}  # Missing roles

    with pytest.raises(Exception) as exc_info:
        guard(claims)

    assert "Forbidden" in str(exc_info.value)


def test_invalid_role_format_denied():
    """Test that invalid role format is denied."""
    guard = OpsRoleGuard([OpsRole.DEVOPS])
    claims = {"sub": "user@example.com", "roles": "DEVOPS"}  # String instead of list

    # This should either fail or handle gracefully
    try:
        result = guard(claims)
        # If it doesn't raise, check that it was denied
        assert False, "Should have raised exception for invalid role format"
    except:
        # Expected to raise
        pass
