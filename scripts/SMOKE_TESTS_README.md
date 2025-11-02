# Smoke Tests - Quick Reference

**Fast, repeatable QA tests for critical functionality**

---

## Quick Start

```bash
# Run all smoke tests (one command)
./scripts/smoke.sh

# Or run individual test suites:

# CRM API tests
cd crm_api && pytest tests/test_smoke.py -v

# Ops API tests
cd ops_api && pytest tests/test_smoke.py -v

# CRM SPA tests
cd crm && npm test -- smoke.integration.test.tsx

# Ops Console SPA tests
cd ops-console && npm test -- smoke.integration.test.tsx
```

---

## What Gets Tested

### CRM API (6 tests)
- ✅ `SMOKE-API-CRM-001`: Health check (`/health`)
- ✅ `SMOKE-API-CRM-002`: Auth login (`/api/auth/login`)
- ✅ `SMOKE-API-CRM-003`: Protected route (leads list)
- ✅ `SMOKE-API-CRM-004`: RBAC denial (viewer cannot create leads)
- ✅ `SMOKE-API-CRM-005`: Unauthenticated request denied
- ✅ `SMOKE-API-CRM-006`: Invalid token rejected

### Ops API (5 tests)
- ✅ `SMOKE-API-OPS-001`: Health check (`/health`)
- ✅ `SMOKE-API-OPS-002`: Valid auth token accepted
- ✅ `SMOKE-API-OPS-003`: Protected route placeholder
- ✅ `SMOKE-API-OPS-004`: RBAC role differentiation
- ✅ `SMOKE-API-OPS-005`: Token expiration format

### CRM SPA (6 tests)
- ✅ `SMOKE-UI-CRM-001`: Login renders and submits
- ✅ `SMOKE-UI-CRM-002`: Protected route accessible with token
- ✅ `SMOKE-UI-CRM-003`: Route guard denies without token
- ✅ `SMOKE-UI-CRM-004`: Login error handling
- ✅ `SMOKE-UI-CRM-005`: Theme classes applied

### Ops Console SPA (6 tests)
- ✅ `SMOKE-UI-OPS-001`: Login renders and submits
- ✅ `SMOKE-UI-OPS-002`: System Health accessible with token
- ✅ `SMOKE-UI-OPS-003`: Route guard denies without token
- ✅ `SMOKE-UI-OPS-004`: Login error handling
- ✅ `SMOKE-UI-OPS-005`: Service tiles styling
- ✅ `SMOKE-UI-OPS-006`: Theme consistency

**Total: 23 smoke tests across 4 test suites**

---

## Expected Output

When all tests pass, you should see:

```
========================================
RiverCityClean QA Smoke Test Suite
========================================

[1/4] CRM API Smoke Tests
----------------------------------------
  ✔ CRM API Health, Auth, Protected Routes, RBAC

[2/4] Ops API Smoke Tests
----------------------------------------
  ✔ Ops API Health, Auth, Token Validation

[3/4] CRM SPA Smoke Tests
----------------------------------------
  ✔ CRM Login Flow, Protected Routes, Route Guards

[4/4] Ops Console SPA Smoke Tests
----------------------------------------
  ✔ Ops Console Login Flow, System Health, Route Guards

========================================
Smoke Test Summary
========================================

Coverage Areas:
----------------------------------------
  ✔ Authentication (login, token generation)
  ✔ Authorization (RBAC, role validation)
  ✔ Protected Routes (API endpoints, SPA pages)
  ✔ UI Components (login forms, dashboards)

Statistics:
----------------------------------------
  Total Suites:  4
  Passed:        4
  Failed:        0
  Duration:      8s

✅ All smoke tests passed!

✔ Authentication working
✔ RBAC enforcement validated
✔ Protected routes secured
✔ UI flows functional
```

---

## Prerequisites

### Python Tests (crm_api, ops_api)
```bash
pip install pytest fastapi
```

### SPA Tests (crm, ops-console)
```bash
cd crm && npm install
cd ops-console && npm install
```

---

## Test Locations

| Test Suite | Location | Purpose |
|------------|----------|---------|
| **CRM API Smoke** | `crm_api/tests/test_smoke.py` | API health, auth, RBAC |
| **Ops API Smoke** | `ops_api/tests/test_smoke.py` | API health, auth, token validation |
| **CRM SPA Smoke** | `crm/src/__tests__/smoke.integration.test.tsx` | Login flow, route guards |
| **Ops Console Smoke** | `ops-console/src/__tests__/smoke.integration.test.tsx` | Login flow, system health |

---

## When to Run

- **On every commit**: Before pushing to prevent regressions
- **Pre-deployment**: CI/CD pipeline gate
- **After dependency updates**: Verify no breaking changes
- **Monthly**: As part of QA review

---

## Test Philosophy

These are **smoke tests**, not full integration tests:

✅ **DO:**
- Test critical happy paths
- Verify auth and RBAC work
- Ensure protected routes are guarded
- Check UI can render and submit forms

❌ **DON'T:**
- Test edge cases (use unit tests)
- Require real databases (use mocks)
- Spin up browsers (use RTL instead of Playwright)
- Take longer than 10 seconds total

**Goal:** Catch 80% of regressions in < 10 seconds.

---

## Troubleshooting

### Tests fail with "Module not found"
```bash
# Python: Install pytest
pip install pytest

# SPA: Install dependencies
cd crm && npm install
```

### Tests fail with import errors
```bash
# Ensure you're in the right directory
cd crm_api  # for Python tests
cd crm      # for SPA tests
```

### Tests timeout
```bash
# Check if APIs are running (they shouldn't need to be)
# Smoke tests use TestClient (Python) and mock APIs (SPA)
```

---

## Integration with CI/CD

Add to `.github/workflows/ci.yml`:

```yaml
- name: Run Smoke Tests
  run: ./scripts/smoke.sh
```

Or in `package.json`:

```json
{
  "scripts": {
    "smoke": "./scripts/smoke.sh"
  }
}
```

---

## QA Matrix

See `QA_MATRIX.md` for full test coverage mapping:
- Features vs. test IDs
- Coverage requirements (85% backend, 80% frontend)
- Gap analysis and remediation plan

---

**Last Updated:** 2025-11-02
**Owner:** QA Team
**Questions:** See QA_MATRIX.md or contact @qa-lead
