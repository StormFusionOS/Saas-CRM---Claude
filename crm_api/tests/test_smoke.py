"""
CRM API Smoke Tests

Fast, deterministic smoke tests to verify core functionality.
Run these on every commit to catch critical regressions early.

Test IDs: SMOKE-API-CRM-001 to SMOKE-API-CRM-004

Usage:
    pytest tests/test_smoke.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.security import create_access_token
from app.db import init_demo_data


@pytest.fixture(scope="module")
def client():
    """Create test client with fresh app instance."""
    init_demo_data()  # Ensure demo data is loaded
    app = create_app()
    return TestClient(app)


@pytest.fixture
def manager_token():
    """Generate access token for manager role."""
    return create_access_token(
        sub="Nathan@RiverCityClean.com",
        role="manager"
    )


@pytest.fixture
def viewer_token():
    """Generate access token for viewer role (limited permissions)."""
    return create_access_token(
        sub="viewer@example.com",
        role="viewer"
    )


class TestCRMAPISmoke:
    """CRM API smoke test suite."""

    def test_health_check(self, client):
        """
        SMOKE-API-CRM-001: Health check endpoint responds correctly.

        Verifies:
        - /health endpoint is accessible
        - Returns 200 OK
        - Response includes status and service name
        """
        response = client.get("/health")

        assert response.status_code == 200, "Health check should return 200"
        data = response.json()

        assert data["status"] == "ok", "Health status should be 'ok'"
        assert data["service"] == "crm-api", "Service name should be 'crm-api'"
        assert "version" in data, "Health check should include version"

    def test_auth_login(self, client):
        """
        SMOKE-API-CRM-002: Authentication login works correctly.

        Verifies:
        - /api/auth/login accepts credentials
        - Returns 200 OK for valid credentials
        - Response includes access_token
        - Token type is 'bearer'
        """
        response = client.post(
            "/api/auth/login",
            data={
                "username": "Nathan@RiverCityClean.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200, "Login should succeed with valid credentials"
        data = response.json()

        assert "access_token" in data, "Response should include access_token"
        assert data["token_type"] == "bearer", "Token type should be 'bearer'"
        assert len(data["access_token"]) > 20, "Access token should be a valid JWT"

    def test_protected_route_with_auth(self, client, manager_token):
        """
        SMOKE-API-CRM-003: Protected route accessible with valid token.

        Verifies:
        - /api/leads endpoint requires authentication
        - Returns 200 OK with valid token
        - Response includes list of leads
        """
        response = client.get(
            "/api/leads",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 200, "Protected route should be accessible with valid token"
        data = response.json()

        assert isinstance(data, list), "Leads endpoint should return a list"
        # Demo data should have at least one lead
        assert len(data) > 0, "Demo data should include sample leads"

    def test_rbac_denial_wrong_role(self, client, viewer_token):
        """
        SMOKE-API-CRM-004: RBAC denies access for insufficient permissions.

        Verifies:
        - Viewer role cannot create new leads (requires manager role)
        - Returns 403 Forbidden
        - Error message indicates insufficient permissions
        """
        new_lead = {
            "contact_id": 1,
            "status": "NEW",
            "priority": "medium",
            "notes": "Test lead"
        }

        response = client.post(
            "/api/leads",
            json=new_lead,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403, "Viewer role should not be able to create leads"
        data = response.json()

        assert "detail" in data, "Error response should include detail message"
        assert "permission" in data["detail"].lower() or "forbidden" in data["detail"].lower(), \
            "Error should indicate permission issue"

    def test_unauthenticated_request_denied(self, client):
        """
        SMOKE-API-CRM-005: Unauthenticated requests are denied.

        Verifies:
        - Protected endpoints reject requests without token
        - Returns 401 Unauthorized
        """
        response = client.get("/api/leads")

        assert response.status_code == 401, "Unauthenticated request should return 401"
        data = response.json()

        assert "detail" in data, "Error response should include detail message"

    def test_invalid_token_rejected(self, client):
        """
        SMOKE-API-CRM-006: Invalid tokens are rejected.

        Verifies:
        - Malformed or invalid tokens return 401
        - System properly validates JWT signatures
        """
        response = client.get(
            "/api/leads",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )

        assert response.status_code == 401, "Invalid token should return 401"


# Run smoke tests in order for clearer output
pytest.main([__file__, "-v", "--tb=short"])
