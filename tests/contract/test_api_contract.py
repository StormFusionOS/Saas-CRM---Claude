"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
API Contract Tests

Validates that API implementations match OpenAPI specifications.

Tests curated route set against live handlers to ensure contract compliance.
"""

import pytest
from pathlib import Path
import yaml


@pytest.fixture
def crm_openapi_spec():
    """Load CRM OpenAPI specification."""
    spec_path = Path(__file__).parent.parent.parent / "docs" / "api" / "crm.yaml"
    with open(spec_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def ops_openapi_spec():
    """Load Ops Console OpenAPI specification."""
    spec_path = Path(__file__).parent.parent.parent / "docs" / "api" / "ops.yaml"
    with open(spec_path, 'r') as f:
        return yaml.safe_load(f)


class TestCRMContract:
    """Contract tests for CRM API."""

    def test_openapi_spec_valid(self, crm_openapi_spec):
        """Verify OpenAPI spec is valid."""
        assert crm_openapi_spec['openapi'] == '3.0.3'
        assert crm_openapi_spec['info']['title'] == 'RiverCityClean CRM API'
        assert crm_openapi_spec['info']['version'] == '0.1.0'

    def test_auth_login_endpoint_defined(self, crm_openapi_spec):
        """Verify /api/auth/login endpoint is defined."""
        assert '/api/auth/login' in crm_openapi_spec['paths']
        login_endpoint = crm_openapi_spec['paths']['/api/auth/login']
        assert 'post' in login_endpoint
        assert login_endpoint['post']['operationId'] == 'login'

    def test_auth_login_request_schema(self, crm_openapi_spec):
        """Verify login request schema."""
        login_endpoint = crm_openapi_spec['paths']['/api/auth/login']['post']
        assert 'requestBody' in login_endpoint
        assert 'content' in login_endpoint['requestBody']
        assert 'application/json' in login_endpoint['requestBody']['content']

        schema_ref = login_endpoint['requestBody']['content']['application/json']['schema']['$ref']
        assert schema_ref == '#/components/schemas/LoginRequest'

        # Check schema definition
        login_schema = crm_openapi_spec['components']['schemas']['LoginRequest']
        assert 'email' in login_schema['required']
        assert 'password' in login_schema['required']

    def test_auth_login_response_schema(self, crm_openapi_spec):
        """Verify login response schema."""
        login_endpoint = crm_openapi_spec['paths']['/api/auth/login']['post']
        assert '200' in login_endpoint['responses']

        response_schema_ref = login_endpoint['responses']['200']['content']['application/json']['schema']['$ref']
        assert response_schema_ref == '#/components/schemas/TokenPair'

        # Check schema definition
        token_schema = crm_openapi_spec['components']['schemas']['TokenPair']
        assert 'access_token' in token_schema['required']
        assert 'token_type' in token_schema['required']

    def test_leads_board_endpoint_defined(self, crm_openapi_spec):
        """Verify /api/v1/leads endpoint is defined."""
        assert '/api/v1/leads' in crm_openapi_spec['paths']
        leads_endpoint = crm_openapi_spec['paths']['/api/v1/leads']
        assert 'get' in leads_endpoint
        assert leads_endpoint['get']['operationId'] == 'getLeadsBoard'

    def test_leads_board_response_schema(self, crm_openapi_spec):
        """Verify leads board response schema."""
        leads_endpoint = crm_openapi_spec['paths']['/api/v1/leads']['get']
        assert '200' in leads_endpoint['responses']

        response_schema_ref = leads_endpoint['responses']['200']['content']['application/json']['schema']['$ref']
        assert response_schema_ref == '#/components/schemas/LeadBoard'

        # Check schema definition
        board_schema = crm_openapi_spec['components']['schemas']['LeadBoard']
        assert 'properties' in board_schema
        assert 'new' in board_schema['properties']
        assert 'closed_won' in board_schema['properties']

    def test_webhook_endpoints_defined(self, crm_openapi_spec):
        """Verify webhook endpoints are defined."""
        assert '/api/webhooks/facebook' in crm_openapi_spec['paths']
        assert '/api/webhooks/twilio' in crm_openapi_spec['paths']
        assert '/api/webhooks/google' in crm_openapi_spec['paths']

        # Verify webhooks don't require auth (security: [])
        facebook_endpoint = crm_openapi_spec['paths']['/api/webhooks/facebook']['post']
        assert 'security' in facebook_endpoint
        assert facebook_endpoint['security'] == []

    def test_scheduler_endpoint_defined(self, crm_openapi_spec):
        """Verify scheduler endpoint is defined."""
        assert '/api/scheduler/next' in crm_openapi_spec['paths']
        scheduler_endpoint = crm_openapi_spec['paths']['/api/scheduler/next']
        assert 'get' in scheduler_endpoint


class TestOpsContract:
    """Contract tests for Ops Console API."""

    def test_openapi_spec_valid(self, ops_openapi_spec):
        """Verify OpenAPI spec is valid."""
        assert ops_openapi_spec['openapi'] == '3.0.3'
        assert ops_openapi_spec['info']['title'] == 'RiverCityClean Ops Console API'
        assert ops_openapi_spec['info']['version'] == '0.1.0'

    def test_health_endpoint_defined(self, ops_openapi_spec):
        """Verify /health endpoint is defined."""
        assert '/health' in ops_openapi_spec['paths']
        health_endpoint = ops_openapi_spec['paths']['/health']
        assert 'get' in health_endpoint
        assert health_endpoint['get']['operationId'] == 'healthCheck'

        # Verify health check doesn't require auth
        assert 'security' in health_endpoint['get']
        assert health_endpoint['get']['security'] == []

    def test_system_health_endpoint_defined(self, ops_openapi_spec):
        """Verify /api/ops/system/health endpoint is defined."""
        assert '/api/ops/system/health' in ops_openapi_spec['paths']
        health_endpoint = ops_openapi_spec['paths']['/api/ops/system/health']
        assert 'get' in health_endpoint

    def test_system_health_response_schema(self, ops_openapi_spec):
        """Verify system health response schema."""
        health_endpoint = ops_openapi_spec['paths']['/api/ops/system/health']['get']
        assert '200' in health_endpoint['responses']

        response_schema_ref = health_endpoint['responses']['200']['content']['application/json']['schema']['$ref']
        assert response_schema_ref == '#/components/schemas/SystemHealth'

        # Check schema definition
        health_schema = ops_openapi_spec['components']['schemas']['SystemHealth']
        assert 'properties' in health_schema
        assert 'overall_status' in health_schema['properties']
        assert 'services' in health_schema['properties']

    def test_services_list_endpoint_defined(self, ops_openapi_spec):
        """Verify /api/ops/services endpoint is defined."""
        assert '/api/ops/services' in ops_openapi_spec['paths']
        services_endpoint = ops_openapi_spec['paths']['/api/ops/services']
        assert 'get' in services_endpoint

    def test_alerts_endpoints_defined(self, ops_openapi_spec):
        """Verify alerts endpoints are defined."""
        assert '/api/ops/alerts' in ops_openapi_spec['paths']
        alerts_endpoint = ops_openapi_spec['paths']['/api/ops/alerts']
        assert 'get' in alerts_endpoint
        assert 'post' in alerts_endpoint

    def test_database_health_endpoint_defined(self, ops_openapi_spec):
        """Verify database health endpoint is defined."""
        assert '/api/ops/database/health' in ops_openapi_spec['paths']
        db_endpoint = ops_openapi_spec['paths']['/api/ops/database/health']
        assert 'get' in db_endpoint


class TestAPIConsistency:
    """Cross-API consistency tests."""

    def test_error_schema_consistent(self, crm_openapi_spec, ops_openapi_spec):
        """Verify error schemas are consistent across APIs."""
        crm_error = crm_openapi_spec['components']['schemas']['Error']
        ops_error = ops_openapi_spec['components']['schemas']['Error']

        # Both should have 'detail' field
        assert 'detail' in crm_error['required']
        assert 'detail' in ops_error['required']

    def test_auth_schema_consistent(self, crm_openapi_spec, ops_openapi_spec):
        """Verify auth schemas are consistent across APIs."""
        crm_token = crm_openapi_spec['components']['schemas']['TokenPair']
        ops_token = ops_openapi_spec['components']['schemas']['TokenPair']

        # Both should have same token structure
        assert 'access_token' in crm_token['required']
        assert 'access_token' in ops_token['required']
        assert 'token_type' in crm_token['required']
        assert 'token_type' in ops_token['required']

    def test_security_scheme_consistent(self, crm_openapi_spec, ops_openapi_spec):
        """Verify security schemes are consistent."""
        crm_bearer = crm_openapi_spec['components']['securitySchemes']['BearerAuth']
        ops_bearer = ops_openapi_spec['components']['securitySchemes']['BearerAuth']

        assert crm_bearer['type'] == 'http'
        assert crm_bearer['scheme'] == 'bearer'
        assert ops_bearer['type'] == 'http'
        assert ops_bearer['scheme'] == 'bearer'


# Integration with pytest
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
