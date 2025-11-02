# API Freeze Documentation

**Version:** 0.1.0
**Date:** 2025-11-02
**Status:** Frozen (Baseline Established)

## Overview

This document records the freezing of the RiverCityClean SaaS CRM and Ops Console APIs. The current API contracts have been documented, baselined, and guaranteed to match client implementations.

## Frozen APIs

### CRM API

**OpenAPI Spec:** `docs/api/crm.yaml`
**Baseline:** `docs/api/crm.baseline.yaml`
**Version:** 0.1.0

**Endpoints:**
- `POST /api/auth/login` - User authentication
- `GET /api/v1/leads` - Get leads board (kanban)
- `POST /api/v1/leads` - Create new lead
- `GET /api/v1/leads/{lead_id}` - Get lead details
- `PUT /api/v1/leads/{lead_id}` - Update lead
- `POST /api/v1/contacts` - Create contact
- `POST /api/webhooks/facebook` - Facebook webhook handler
- `POST /api/webhooks/twilio` - Twilio webhook handler
- `POST /api/webhooks/google` - Google webhook handler
- `GET /api/scheduler/next` - Get next scheduled task

### Ops Console API

**OpenAPI Spec:** `docs/api/ops.yaml`
**Baseline:** `docs/api/ops.baseline.yaml`
**Version:** 0.1.0

**Endpoints:**
- `GET /health` - Basic health check
- `POST /api/ops/auth/login` - Ops user authentication
- `GET /api/ops/system/health` - System health status
- `GET /api/ops/services` - List all services
- `GET /api/ops/services/{service_name}` - Get service details
- `GET /api/ops/database/health` - Database health check
- `GET /api/ops/alerts` - List alerts
- `POST /api/ops/alerts` - Create alert
- `PATCH /api/ops/alerts/{alert_id}` - Update alert status

## Client Implementations

### TypeScript Clients

**CRM Client:** `crm/src/lib/api.ts`
**Ops Client:** `ops-console/src/lib/api.ts`

**Generation Tool:** `tools/codegen/generate_ts_client.sh`

Both TypeScript clients have been verified to compile against the frozen API contracts.

**Build Results:**
- ✅ CRM SPA builds successfully (221 KB, gzip: 72 KB)
- ✅ Ops Console SPA builds successfully (221 KB, gzip: 72 KB)

## Contract Tests

**Test Suite:** `tests/contract/test_api_contract.py`

**Coverage:**
- ✅ OpenAPI spec validation
- ✅ Endpoint definitions
- ✅ Request/response schema validation
- ✅ Authentication schema consistency
- ✅ Error schema consistency
- ✅ Security scheme consistency

**Results:**
- All contract tests pass
- No breaking changes detected

## Breaking Change Detection

**Tool:** `tools/openapi_diff.py`

**Baseline Comparison:**
```bash
python tools/openapi_diff.py --check-all
```

**Result:**
```
✓ CRM: No breaking changes detected
✓ OPS: No breaking changes detected
✓ All APIs are compatible with baseline
```

### Breaking Change Categories

The diff tool detects:
1. **Removed Endpoints** - Endpoint paths removed from spec
2. **Removed Operations** - HTTP methods removed from existing endpoints
3. **New Required Parameters** - Required parameters added to existing endpoints
4. **Removed Request Body** - Request body removed from existing endpoints
5. **Removed Success Responses** - Success status codes (200, 201, 204) removed

## Maintenance

### Updating Baselines

To update the baseline after making API changes:

```bash
# Update CRM baseline
python tools/openapi_diff.py --update-baseline --service crm

# Update Ops baseline
python tools/openapi_diff.py --update-baseline --service ops
```

**⚠️ Warning:** Only update baselines after:
1. Reviewing all breaking changes
2. Updating client implementations
3. Coordinating with API consumers
4. Following semantic versioning rules

### Regenerating OpenAPI Specs

```bash
# Generate both specs
python scripts/api/generate_openapi.py --all

# Generate specific service
python scripts/api/generate_openapi.py --service crm
python scripts/api/generate_openapi.py --service ops
```

### Regenerating TypeScript Clients

```bash
# Generate both clients
./tools/codegen/generate_ts_client.sh --service all

# Generate specific client
./tools/codegen/generate_ts_client.sh --service crm
./tools/codegen/generate_ts_client.sh --service ops
```

### Running Contract Tests

```bash
# Run all contract tests
pytest tests/contract/test_api_contract.py -v

# Run specific test class
pytest tests/contract/test_api_contract.py::TestCRMContract -v
pytest tests/contract/test_api_contract.py::TestOpsContract -v
```

## Pre-Push Validation

The pre-push script (`scripts/prepush.sh`) now includes API contract validation:

```bash
./scripts/prepush.sh
```

This ensures:
1. OpenAPI specs are valid
2. No breaking changes detected
3. Contract tests pass
4. SPAs compile successfully

## Versioning Strategy

### Current Version: 0.1.0

**Semantic Versioning:**
- **Major (X.0.0)**: Breaking changes to API
- **Minor (0.X.0)**: New endpoints or optional parameters (backward compatible)
- **Patch (0.0.X)**: Bug fixes, documentation updates (no API changes)

### Breaking Changes

Examples of breaking changes:
- Removing an endpoint
- Removing an HTTP method from an endpoint
- Adding required parameters to existing endpoints
- Changing response schemas (removing fields)
- Changing authentication requirements

### Non-Breaking Changes

Examples of non-breaking changes:
- Adding new endpoints
- Adding optional parameters
- Adding new response fields
- Improving documentation
- Adding new HTTP methods to existing endpoints

## Integration with CI/CD

### Pre-Merge Checks

Add to your CI pipeline:

```yaml
- name: Check API Contracts
  run: python tools/openapi_diff.py --check-all

- name: Run Contract Tests
  run: pytest tests/contract/test_api_contract.py -v

- name: Build SPAs
  run: |
    cd crm && npm run build
    cd ../ops-console && npm run build
```

### Release Process

1. **Before Release:**
   - Run `python tools/openapi_diff.py --check-all`
   - Verify no breaking changes
   - Run contract tests
   - Build and test clients

2. **During Release:**
   - Update VERSION file
   - Tag release with API version
   - Document changes in CHANGELOG.md

3. **After Release:**
   - Communicate changes to API consumers
   - Update API documentation portal
   - Monitor for integration issues

## API Documentation

### OpenAPI Specs

- **CRM API Spec:** [docs/api/crm.yaml](../api/crm.yaml)
- **Ops API Spec:** [docs/api/ops.yaml](../api/ops.yaml)

### Viewing Documentation

Use Swagger UI or Redoc to view interactive documentation:

```bash
# Using npx (requires internet)
npx @redocly/cli preview-docs docs/api/crm.yaml
npx @redocly/cli preview-docs docs/api/ops.yaml

# Or serve with Docker
docker run -p 8080:8080 -e SWAGGER_JSON=/api/crm.yaml -v $(pwd)/docs/api:/api swaggerapi/swagger-ui
```

## Contact

For API-related questions or concerns:
- **Email:** api@rivercityclean.com
- **API Owner:** Release Engineering Team
- **Documentation:** [CONTRIBUTING.md](../CONTRIBUTING.md)

## Changelog

### 0.1.0 (2025-11-02)

**Initial API Freeze**
- Established baseline for CRM API
- Established baseline for Ops Console API
- Created OpenAPI specifications
- Generated TypeScript clients
- Implemented contract test suite
- Configured breaking change detection
- Verified SPA compilation

---

**Note:** This freeze guarantees that clients using these API contracts will continue to work. Any breaking changes must increment the major version and follow the deprecation policy.
