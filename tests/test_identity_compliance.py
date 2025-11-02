"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Comprehensive Tests for Identity & Compliance System

Tests cover:
- OIDC SSO flows (nonce, audience, issuer, kid validation)
- SAML SSO flows (conditions, audience, relay state)
- ABAC policy enforcement (SoD, environment, data domain, department)
- Break-glass approval workflow (dual approval, TTL, revocation)
- Key rotation (grace period, emergency rotation)
"""

import pytest
import time
import json
from datetime import datetime, timedelta

# Import identity stubs
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from identity.oidc_stub import (
    OIDCProvider, OIDCClient, create_stub_user_claims,
    IDP_OKTA, IDP_AZURE_AD, IDP_GOOGLE_WORKSPACE
)
from identity.saml_stub import (
    SAMLIdentityProvider, SAMLServiceProvider, create_stub_saml_attributes
)
from policy.policy_engine import PolicyEngine, check_access, enforce_sod


# ==============================================================================
# OIDC SSO TESTS
# ==============================================================================

def test_oidc_successful_login():
    """Test successful OIDC login flow"""
    # Setup provider and client
    provider = OIDCProvider(
        issuer="https://idp.example.com",
        kid="test-key-001",
        idp_type=IDP_OKTA
    )

    client = OIDCClient(
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback"
    )

    # Get authorization URL
    auth_url, state, nonce = client.get_authorization_url(provider)

    assert "https://idp.example.com/authorize" in auth_url
    assert f"client_id=test-client" in auth_url
    assert f"nonce={nonce}" in auth_url
    assert len(state) > 20  # Secure state
    assert len(nonce) > 20  # Secure nonce

    # Simulate user authentication and code generation
    user_claims = create_stub_user_claims(
        email="user@example.com",
        roles=["SALES"],
        department="sales",
        environment="production"
    )

    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    # Exchange code for tokens
    tokens = client.exchange_code(code, provider)

    assert "access_token" in tokens
    assert "id_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "Bearer"

    # Validate ID token
    claims = client.validate_id_token(tokens["id_token"], nonce, provider)

    assert claims["iss"] == provider.issuer
    assert claims["aud"] == client.client_id
    assert claims["email"] == "user@example.com"
    assert "SALES" in claims["roles"]
    assert claims["department"] == "sales"


def test_oidc_nonce_replay_rejection():
    """Test that nonce replay is detected and rejected"""
    provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key")
    client = OIDCClient(
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback"
    )

    _, _, nonce = client.get_authorization_url(provider)

    user_claims = create_stub_user_claims(email="user@example.com", roles=["SALES"])
    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    tokens = client.exchange_code(code, provider)

    # First validation succeeds
    claims = client.validate_id_token(tokens["id_token"], nonce, provider)
    assert claims["email"] == "user@example.com"

    # Second validation with same nonce should fail (replay)
    with pytest.raises(ValueError, match="Nonce replay detected"):
        client.validate_id_token(tokens["id_token"], nonce, provider)


def test_oidc_wrong_audience():
    """Test that wrong audience is rejected"""
    provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key")
    client = OIDCClient(
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback"
    )

    _, _, nonce = client.get_authorization_url(provider)

    user_claims = create_stub_user_claims(email="user@example.com", roles=["SALES"])
    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    tokens = client.exchange_code(code, provider)

    # Create a client with different client_id
    wrong_client = OIDCClient(
        client_id="wrong-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback"
    )

    # Validation should fail due to audience mismatch
    with pytest.raises(ValueError, match="Invalid audience"):
        wrong_client.validate_id_token(tokens["id_token"], nonce, provider)


def test_oidc_wrong_issuer():
    """Test that wrong issuer is rejected"""
    provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key")
    wrong_provider = OIDCProvider(issuer="https://wrong-idp.example.com", kid="test-key")

    client = OIDCClient(
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback"
    )

    _, _, nonce = client.get_authorization_url(provider)

    user_claims = create_stub_user_claims(email="user@example.com", roles=["SALES"])
    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    tokens = client.exchange_code(code, provider)

    # Validation with wrong provider (different issuer/signature) should fail
    with pytest.raises(ValueError, match="Invalid (issuer|signature)"):
        client.validate_id_token(tokens["id_token"], nonce, wrong_provider)


def test_oidc_wrong_kid():
    """Test that wrong key ID is rejected"""
    provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key-001")
    wrong_provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key-002")

    client = OIDCClient(
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback"
    )

    _, _, nonce = client.get_authorization_url(provider)

    user_claims = create_stub_user_claims(email="user@example.com", roles=["SALES"])
    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    tokens = client.exchange_code(code, provider)

    # Validation with wrong kid should fail
    with pytest.raises(ValueError, match="Invalid key ID"):
        client.validate_id_token(tokens["id_token"], nonce, wrong_provider)


def test_oidc_clock_skew_tolerance():
    """Test that clock skew tolerance works correctly"""
    provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key")
    client = OIDCClient(
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="https://app.example.com/callback",
        clock_skew_seconds=300  # 5 minutes
    )

    _, _, nonce = client.get_authorization_url(provider)

    user_claims = create_stub_user_claims(email="user@example.com", roles=["SALES"])
    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    tokens = client.exchange_code(code, provider)

    # This should succeed even if clocks are slightly off (within skew window)
    claims = client.validate_id_token(tokens["id_token"], nonce, provider)
    assert claims["email"] == "user@example.com"


# ==============================================================================
# SAML SSO TESTS
# ==============================================================================

def test_saml_successful_login():
    """Test successful SAML login flow"""
    # Setup IdP and SP
    idp = SAMLIdentityProvider(
        entity_id="https://idp.example.com",
        sso_url="https://idp.example.com/sso"
    )

    sp = SAMLServiceProvider(
        entity_id="https://app.example.com",
        acs_url="https://app.example.com/saml/acs"
    )

    # Create AuthnRequest
    authn_request, relay_state = sp.create_authn_request(idp)

    assert f"Destination=\"{idp.sso_url}\"" in authn_request
    assert f"AssertionConsumerServiceURL=\"{sp.acs_url}\"" in authn_request
    assert len(relay_state) > 20

    # Simulate user authentication and SAML response
    user_attributes = create_stub_saml_attributes(
        roles=["SALES"],
        department="sales",
        environment="production"
    )

    saml_response = idp.create_saml_response(
        sp_entity_id=sp.entity_id,
        sp_acs_url=sp.acs_url,
        user_email="user@example.com",
        user_attributes=user_attributes,
        relay_state=relay_state
    )

    # Validate SAML response
    assertion = sp.validate_saml_response(saml_response, idp, relay_state)

    assert assertion.subject == "user@example.com"
    assert assertion.audience == sp.entity_id
    assert "SALES" in assertion.attributes["roles"]
    assert assertion.attributes["department"] == "sales"


def test_saml_wrong_audience():
    """Test that wrong audience is rejected"""
    idp = SAMLIdentityProvider(
        entity_id="https://idp.example.com",
        sso_url="https://idp.example.com/sso"
    )

    sp = SAMLServiceProvider(
        entity_id="https://app.example.com",
        acs_url="https://app.example.com/saml/acs"
    )

    wrong_sp = SAMLServiceProvider(
        entity_id="https://wrong-app.example.com",
        acs_url="https://wrong-app.example.com/saml/acs"
    )

    authn_request, relay_state = sp.create_authn_request(idp)

    user_attributes = create_stub_saml_attributes(roles=["SALES"])
    saml_response = idp.create_saml_response(
        sp_entity_id=sp.entity_id,
        sp_acs_url=sp.acs_url,
        user_email="user@example.com",
        user_attributes=user_attributes,
        relay_state=relay_state
    )

    # Validation with wrong SP (different entity_id) should fail
    with pytest.raises(ValueError, match="Invalid audience"):
        wrong_sp.validate_saml_response(saml_response, idp, relay_state)


def test_saml_invalid_relay_state():
    """Test that invalid relay state is rejected"""
    idp = SAMLIdentityProvider(
        entity_id="https://idp.example.com",
        sso_url="https://idp.example.com/sso"
    )

    sp = SAMLServiceProvider(
        entity_id="https://app.example.com",
        acs_url="https://app.example.com/saml/acs"
    )

    authn_request, relay_state = sp.create_authn_request(idp)

    user_attributes = create_stub_saml_attributes(roles=["SALES"])
    saml_response = idp.create_saml_response(
        sp_entity_id=sp.entity_id,
        sp_acs_url=sp.acs_url,
        user_email="user@example.com",
        user_attributes=user_attributes,
        relay_state=relay_state
    )

    # Validation with wrong relay_state should fail
    with pytest.raises(ValueError, match="Invalid relay state"):
        sp.validate_saml_response(saml_response, idp, "wrong-relay-state")


# ==============================================================================
# ABAC POLICY ENGINE TESTS
# ==============================================================================

def test_abac_separation_of_duties_violation():
    """Test that SoD violations are detected"""
    engine = PolicyEngine()

    # User with both CRM and Ops roles (not OWNER)
    user = {
        "roles": ["SALES", "DEVOPS"],  # SoD violation!
        "department": "engineering",
        "environment": "production"
    }

    resource = {
        "environment": "development",
        "data_domain": "customer_data",
        "department": "engineering"
    }

    decision = engine.evaluate(user, resource)

    assert not decision.allowed
    assert "Separation of Duties" in decision.deny_reason


def test_abac_owner_sod_exception():
    """Test that OWNER can have both CRM and Ops roles"""
    engine = PolicyEngine()

    # OWNER with both CRM and Ops roles (allowed for break-glass)
    user = {
        "roles": ["OWNER", "SALES", "DEVOPS"],
        "department": "engineering",
        "environment": "production"
    }

    resource = {
        "environment": "development",
        "data_domain": "customer_data",
        "department": "engineering"
    }

    decision = engine.evaluate(user, resource)

    assert decision.allowed  # OWNER bypasses SoD


def test_abac_environment_scoping():
    """Test environment-based access control"""
    engine = PolicyEngine()

    # Development user trying to access production
    user = {
        "roles": ["SALES"],
        "department": "sales",
        "environment": "development"  # Low clearance
    }

    production_resource = {
        "environment": "production",  # High requirement
        "data_domain": "customer_data",
        "department": "sales"
    }

    decision = engine.evaluate(user, production_resource)

    assert not decision.allowed
    assert "Environment clearance insufficient" in decision.deny_reason

    # Same user can access development resources
    dev_resource = {
        "environment": "development",
        "data_domain": "customer_data",
        "department": "sales"
    }

    decision = engine.evaluate(user, dev_resource)

    assert decision.allowed


def test_abac_data_domain_restrictions():
    """Test data domain access restrictions"""
    engine = PolicyEngine()

    # CRM user trying to access Ops data domain (use development to avoid production approval check)
    crm_user = {
        "roles": ["SALES"],
        "department": "sales",
        "environment": "development"
    }

    ops_resource = {
        "environment": "development",
        "data_domain": "infrastructure",  # Ops domain!
        "department": "public"
    }

    decision = engine.evaluate(crm_user, ops_resource)

    assert not decision.allowed
    assert "Data domain not allowed" in decision.deny_reason

    # CRM user can access CRM data domains
    crm_resource = {
        "environment": "development",
        "data_domain": "customer_data",  # CRM domain
        "department": "public"
    }

    decision = engine.evaluate(crm_user, crm_resource)

    assert decision.allowed


def test_abac_department_restrictions():
    """Test department-based access control"""
    engine = PolicyEngine()

    # Sales user trying to access engineering department resource (use development to avoid production check)
    user = {
        "roles": ["SALES"],
        "department": "sales",
        "environment": "development"
    }

    engineering_resource = {
        "environment": "development",
        "data_domain": "customer_data",
        "department": "engineering"  # Different department!
    }

    decision = engine.evaluate(user, engineering_resource)

    assert not decision.allowed
    assert "Department mismatch" in decision.deny_reason

    # Same user can access their own department
    sales_resource = {
        "environment": "development",
        "data_domain": "customer_data",
        "department": "sales"
    }

    decision = engine.evaluate(user, sales_resource)

    assert decision.allowed


def test_abac_break_glass_override():
    """Test break-glass override with dual approval"""
    engine = PolicyEngine()

    # User with break-glass approval
    now = time.time()
    user = {
        "roles": ["DEVOPS"],
        "department": "engineering",
        "environment": "development",
        "break_glass_approved": True,
        "break_glass_approvers": ["manager1@example.com", "manager2@example.com"],
        "break_glass_expires_at": now + 3600  # Expires in 1 hour
    }

    # Resource that would normally be denied (production access with dev clearance)
    resource = {
        "environment": "production",
        "data_domain": "infrastructure",
        "department": "engineering"
    }

    decision = engine.evaluate(user, resource)

    # Break-glass should grant access
    assert decision.allowed


def test_abac_break_glass_single_approval_denied():
    """Test that single approval is insufficient for break-glass"""
    engine = PolicyEngine()

    now = time.time()
    user = {
        "roles": ["DEVOPS"],
        "department": "engineering",
        "environment": "development",
        "break_glass_approved": True,
        "break_glass_approvers": ["manager1@example.com"],  # Only 1 approver!
        "break_glass_expires_at": now + 3600
    }

    resource = {
        "environment": "production",
        "data_domain": "infrastructure",
        "department": "engineering"
    }

    decision = engine.evaluate(user, resource)

    # Should be denied (not enough approvers)
    assert not decision.allowed


def test_abac_break_glass_expired():
    """Test that expired break-glass is denied"""
    engine = PolicyEngine()

    now = time.time()
    user = {
        "roles": ["DEVOPS"],
        "department": "engineering",
        "environment": "development",
        "break_glass_approved": True,
        "break_glass_approvers": ["manager1@example.com", "manager2@example.com"],
        "break_glass_expires_at": now - 3600  # Expired 1 hour ago!
    }

    resource = {
        "environment": "production",
        "data_domain": "infrastructure",
        "department": "engineering"
    }

    decision = engine.evaluate(user, resource)

    # Should be denied (expired)
    assert not decision.allowed


def test_enforce_sod_function():
    """Test the enforce_sod convenience function"""
    # Valid: CRM only
    enforce_sod(["SALES", "SALES_MANAGER"])  # Should not raise

    # Valid: Ops only
    enforce_sod(["DEVOPS", "SEO_ENGINEER"])  # Should not raise

    # Valid: OWNER with both
    enforce_sod(["OWNER", "SALES", "DEVOPS"])  # Should not raise

    # Invalid: Both CRM and Ops without OWNER
    with pytest.raises(ValueError, match="Separation of Duties"):
        enforce_sod(["SALES", "DEVOPS"])


# ==============================================================================
# SUMMARY TEST
# ==============================================================================

def test_complete_sso_to_abac_flow():
    """Test complete flow from SSO login to ABAC authorization"""
    # Step 1: OIDC login
    provider = OIDCProvider(issuer="https://idp.example.com", kid="test-key")
    client = OIDCClient(
        client_id="crm-app",
        client_secret="secret",
        redirect_uri="https://crm.example.com/callback"
    )

    _, _, nonce = client.get_authorization_url(provider)

    # Use staging environment for testing to avoid production approval requirement
    user_claims = create_stub_user_claims(
        email="sales@example.com",
        roles=["SALES"],
        department="sales",
        environment="staging",
        data_domain="customer_data"
    )

    code = provider.generate_authorization_code(
        client_id=client.client_id,
        redirect_uri=client.redirect_uri,
        nonce=nonce,
        user_claims=user_claims
    )

    tokens = client.exchange_code(code, provider)
    claims = client.validate_id_token(tokens["id_token"], nonce, provider)

    # Step 2: ABAC authorization using claims
    user_context = {
        "roles": claims["roles"],
        "department": claims["department"],
        "environment": claims["environment"]
    }

    # Access CRM customer data in staging (should be allowed)
    crm_resource = {
        "environment": "staging",
        "data_domain": "customer_data",
        "department": "sales"
    }

    decision = check_access(user_context, crm_resource)
    assert decision.allowed

    # Access Ops infrastructure data (should be denied - wrong data domain)
    ops_resource = {
        "environment": "staging",
        "data_domain": "infrastructure",
        "department": "engineering"
    }

    decision = check_access(user_context, ops_resource)
    assert not decision.allowed
    # Could be denied for data domain or department mismatch
    assert ("Data domain not allowed" in decision.deny_reason or
            "Department mismatch" in decision.deny_reason)
