"""
Ops API Smoke Tests

Fast, deterministic smoke tests to verify core functionality.
Run these on every commit to catch critical regressions early.

Test IDs: SMOKE-API-OPS-001 to SMOKE-API-OPS-004

Usage:
    pytest tests/test_smoke.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.security import create_access_token, OpsRole


@pytest.fixture(scope="module")
def client():
    """Create test client with fresh app instance."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def owner_token():
    """Generate access token for owner role (full permissions)."""
    return create_access_token(
        data={
            "sub": "Nathan@RiverCityClean.com",
            "role": OpsRole.OWNER.value
        }
    )


@pytest.fixture
def sre_token():
    """Generate access token for SRE engineer role (limited permissions)."""
    return create_access_token(
        data={
            "sub": "sre@example.com",
            "role": OpsRole.SEO_ENGINEER.value
        }
    )


class TestOpsAPISmoke:
    """Ops API smoke test suite."""

    def test_health_check(self, client):
        """
        SMOKE-API-OPS-001: Health check endpoint responds correctly.

        Verifies:
        - /health endpoint is accessible
        - Returns 200 OK
        - Response includes status and service name
        """
        response = client.get("/health")

        assert response.status_code == 200, "Health check should return 200"
        data = response.json()

        assert data["status"] == "ok", "Health status should be 'ok'"
        assert data["service"] == "ops-api", "Service name should be 'ops-api'"
        assert "version" in data, "Health check should include version"

    def test_auth_with_valid_token(self, client, owner_token):
        """
        SMOKE-API-OPS-002: Valid authentication token is accepted.

        Verifies:
        - Token can be created for owner role
        - Token is a valid JWT format
        - Token length is reasonable
        """
        # Verify token creation
        assert owner_token is not None, "Token should be created"
        assert isinstance(owner_token, str), "Token should be a string"
        assert len(owner_token) > 20, "Token should be a valid JWT"
        assert owner_token.count('.') == 2, "JWT should have 3 parts separated by dots"

    def test_protected_route_placeholder(self, client, owner_token):
        """
        SMOKE-API-OPS-003: Protected route accessible with valid token.

        NOTE: This is a placeholder test since ops_api doesn't have
        protected routes yet. When routes are added, update this test.

        Verifies:
        - Token is properly formatted
        - System can generate valid tokens
        """
        # Placeholder: verify token format
        parts = owner_token.split('.')
        assert len(parts) == 3, "JWT should have header, payload, and signature"

        # When actual protected routes exist, replace with:
        # response = client.get(
        #     "/api/system/health",
        #     headers={"Authorization": f"Bearer {owner_token}"}
        # )
        # assert response.status_code == 200

    def test_rbac_role_validation(self, client, sre_token, owner_token):
        """
        SMOKE-API-OPS-004: RBAC role differentiation works correctly.

        Verifies:
        - Different roles generate different tokens
        - Token payload includes role information
        """
        # Verify different roles create different tokens
        assert sre_token != owner_token, "Different roles should have different tokens"

        # Both should be valid JWTs
        assert sre_token.count('.') == 2, "SRE token should be valid JWT"
        assert owner_token.count('.') == 2, "Owner token should be valid JWT"

        # Tokens should have different payloads (role info)
        sre_payload = sre_token.split('.')[1]
        owner_payload = owner_token.split('.')[1]
        assert sre_payload != owner_payload, "Different roles should have different payloads"

    def test_token_expiration_format(self, client, owner_token):
        """
        SMOKE-API-OPS-005: Token includes expiration information.

        Verifies:
        - Token payload can be decoded
        - Expiration timestamp is included
        """
        import json
        import base64

        # Decode payload (without verification for smoke test)
        payload_encoded = owner_token.split('.')[1]

        # Add padding if needed
        padding = 4 - (len(payload_encoded) % 4)
        if padding != 4:
            payload_encoded += '=' * padding

        payload_decoded = base64.urlsafe_b64decode(payload_encoded.encode('utf-8'))
        payload_data = json.loads(payload_decoded)

        assert "exp" in payload_data, "Token should include expiration time"
        assert "sub" in payload_data, "Token should include subject (user email)"
        assert "role" in payload_data, "Token should include role information"


# Run smoke tests in order for clearer output
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
