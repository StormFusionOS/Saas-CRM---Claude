# QA Testing Matrix

**RiverCityClean SaaS Platform - Quality Assurance Coverage**

Version: 1.0.0 | Last Updated: 2025-11-02

---

## Overview

This matrix maps product features to test coverage across unit, integration, and smoke tests. Each feature must have at least one test ID to ensure quality gates are met before deployment.

**Test Coverage Legend:**
- ✅ **Full Coverage** - All critical paths tested
- ⚠️ **Partial Coverage** - Core functionality tested, edge cases pending
- ❌ **No Coverage** - Tests needed

---

## Feature vs. Test Coverage Matrix

| Feature | Area | Coverage | Test IDs | Test Location | Notes |
|---------|------|----------|----------|---------------|-------|
| **Authentication** | Security | ✅ Full | `AUTH-001`, `AUTH-002`, `AUTH-003` | `crm_api/tests/test_auth.py`, `crm_api/tests/test_smoke.py` | Login, token generation, password validation |
| **RBAC (Role-Based Access Control)** | Security | ✅ Full | `RBAC-001`, `RBAC-002`, `RBAC-003` | `crm_api/tests/test_rbac.py`, `crm_api/tests/test_smoke.py` | Manager, sales, viewer roles with permission checks |
| **Cross-Role Security** | Security | ✅ Full | `RBAC-004`, `RBAC-005` | `crm_api/tests/test_cross_role_security.py` | Prevent unauthorized cross-role access |
| **Leads CRUD** | Core Features | ✅ Full | `LEADS-001`, `LEADS-002`, `LEADS-003`, `LEADS-004` | `crm_api/tests/test_contacts.py`, `crm_api/tests/test_smoke.py` | Create, read, update, delete operations |
| **Leads Filtering** | Core Features | ⚠️ Partial | `LEADS-005` | `crm_api/tests/test_contacts.py` | Filter by status, search |
| **Webhooks Ingest** | Integrations | ✅ Full | `WEBHOOK-001`, `WEBHOOK-002`, `WEBHOOK-003` | `crm_api/tests/test_webhooks.py`, `crm_api/tests/test_smoke.py` | Twilio, SendGrid webhook parsing |
| **Email Scheduler** | Automation | ⚠️ Partial | `SCHED-001` | `crm_api/app/services/email_poller.py` | Email polling service (no automated tests yet) |
| **Data Backups** | Operations | ✅ Full | `BACKUP-001`, `BACKUP-002` | `scripts/dr/backup_snapshot.py`, `scripts/dr/restore_snapshot.py` | Postgres + Redis backups with integrity checks |
| **DR Drills** | Operations | ✅ Full | `DR-001`, `DR-002` | `scripts/dr/drill.py` | Automated disaster recovery drills |
| **Dashboard Widgets - CRM** | Frontend | ⚠️ Partial | `UI-CRM-001`, `UI-CRM-002` | `crm/src/__tests__/theme.smoke.test.tsx` | KPI cards render correctly |
| **Dashboard Widgets - Ops** | Frontend | ⚠️ Partial | `UI-OPS-001`, `UI-OPS-002` | `ops-console/src/__tests__/theme.smoke.test.tsx` | System health tiles render |
| **Login UI - CRM** | Frontend | ✅ Full | `UI-CRM-LOGIN-001`, `UI-CRM-LOGIN-002` | `crm/src/__tests__/login.a11y.test.tsx`, `crm/src/__tests__/smoke.integration.test.tsx` | Login form, accessibility, auth flow |
| **Login UI - Ops** | Frontend | ✅ Full | `UI-OPS-LOGIN-001`, `UI-OPS-LOGIN-002` | `ops-console/src/__tests__/login.a11y.test.tsx`, `ops-console/src/__tests__/smoke.integration.test.tsx` | Login form, accessibility, auth flow |
| **Health Checks** | Operations | ✅ Full | `HEALTH-001`, `HEALTH-002` | `crm_api/tests/test_smoke.py`, `ops_api/tests/test_smoke.py` | API health endpoints |
| **Observability** | Operations | ⚠️ Partial | `OBS-001`, `OBS-002` | `observability/logger.py`, `observability/metrics.py` | Structured logging, metrics (manual validation) |
| **Supply Chain Security** | Security | ✅ Full | `SBOM-001`, `LICENSE-001` | `tools/sbom/generate.py`, `tools/license/check_licenses.py` | SBOM generation, license compliance |
| **Data Governance** | Compliance | ✅ Full | `DLP-001`, `DSR-001`, `CONSENT-001` | `tools/dlp/scan.py`, `scripts/data/dsr.py`, `consent/manager.py` | DLP scanning, data subject requests, consent management |
| **Performance Budgets** | Performance | ✅ Full | `PERF-001`, `PERF-002` | `scripts/perf/check_budgets.py`, `tools/perf/harness.py` | Budget enforcement, load testing |
| **Compliance Controls** | Compliance | ✅ Full | `COMP-001`, `COMP-002` | `docs/compliance/controls_matrix.csv`, `scripts/compliance/collect_evidence.sh` | SOC2/ISO 27001 controls mapping |

---

## Test Categories

### 1. Smoke Tests (Fast, Deterministic)

**Purpose:** Verify core functionality is working end-to-end without deep integration.

**Scope:**
- API health checks (`/health`)
- Authentication (`/auth/login`)
- One protected route per API
- RBAC denial (wrong role access)
- SPA login flow (render → submit → protected view)
- SPA route guards (deny when no token)

**Location:**
- `crm_api/tests/test_smoke.py`
- `ops_api/tests/test_smoke.py`
- `crm/src/__tests__/smoke.integration.test.tsx`
- `ops-console/src/__tests__/smoke.integration.test.tsx`

**Run Time:** < 10 seconds total

**Test IDs:**
- `SMOKE-API-CRM-001` to `SMOKE-API-CRM-004`
- `SMOKE-API-OPS-001` to `SMOKE-API-OPS-004`
- `SMOKE-UI-CRM-001` to `SMOKE-UI-CRM-003`
- `SMOKE-UI-OPS-001` to `SMOKE-UI-OPS-003`

---

### 2. Unit Tests

**Purpose:** Test individual functions and components in isolation.

**Scope:**
- Authentication logic (password hashing, JWT generation)
- RBAC permission checks
- Data validation schemas
- UI component rendering
- Utility functions

**Location:**
- `crm_api/tests/test_auth.py`
- `crm_api/tests/test_rbac.py`
- `crm/src/__tests__/theme.smoke.test.tsx`
- `ops-console/src/__tests__/theme.smoke.test.tsx`

**Run Time:** < 30 seconds

---

### 3. Integration Tests

**Purpose:** Test interactions between components with real dependencies.

**Scope:**
- Database operations (create, read, update, delete)
- Webhook processing pipelines
- Email polling and intake
- Backup/restore workflows
- DR drill automation

**Location:**
- `crm_api/tests/test_contacts.py`
- `crm_api/tests/test_webhooks.py`
- `scripts/dr/drill.py`
- `scripts/data/dsr.py`

**Run Time:** < 2 minutes

---

### 4. Performance Tests

**Purpose:** Ensure system meets latency and throughput budgets.

**Scope:**
- Load testing (login, leads list, enqueue task)
- Latency micro-benchmarks
- Performance budget enforcement

**Location:**
- `tools/perf/harness.py`
- `scripts/perf/check_budgets.py`
- `tests/performance/latency_test.py`

**Run Time:** ~30 seconds (configurable)

---

### 5. Security Tests

**Purpose:** Validate security controls and prevent vulnerabilities.

**Scope:**
- RBAC enforcement (cross-role access denial)
- DLP scanning (prevent secrets in code)
- License compliance (no GPL/copyleft in production)
- SBOM generation and attestation

**Location:**
- `crm_api/tests/test_cross_role_security.py`
- `tools/dlp/scan.py`
- `tools/license/check_licenses.py`
- `tools/sbom/generate.py`

**Run Time:** < 1 minute

---

## Test ID Naming Convention

Format: `<AREA>-<SUBAREA>-<NUMBER>`

**Examples:**
- `AUTH-001`: Authentication test case 1
- `RBAC-002`: RBAC test case 2
- `LEADS-003`: Leads CRUD test case 3
- `WEBHOOK-001`: Webhook ingest test case 1
- `UI-CRM-001`: CRM UI test case 1
- `SMOKE-API-CRM-001`: CRM API smoke test 1

---

## Coverage Requirements

### Pre-Deployment Gates

All deployments must pass:

1. ✅ **100% Smoke Tests** (all SMOKE-* tests green)
2. ✅ **≥90% Unit Tests** (all critical paths covered)
3. ✅ **≥85% Backend Code Coverage** (measured by pytest-cov)
4. ✅ **≥80% Frontend Code Coverage** (measured by Vitest)
5. ✅ **0 Critical Security Findings** (DLP scan, license check)
6. ✅ **Performance Budgets Met** (p95 latency within budget)

### Monthly Quality Review

- Review partial coverage items (⚠️) and plan test additions
- Update QA matrix with new features
- Conduct DR drill and document results
- Generate compliance evidence pack

---

## Gap Analysis

### Features Needing Additional Tests

1. **Email Scheduler** (⚠️ Partial Coverage)
   - **Gap:** No automated tests for email polling service
   - **Action:** Add `test_email_poller.py` with mock IMAP server
   - **Owner:** Backend Team
   - **Due:** Q1 2026

2. **Dashboard Widgets** (⚠️ Partial Coverage)
   - **Gap:** Only basic rendering tests, no interaction tests
   - **Action:** Add click/filter/sort tests for KPI cards
   - **Owner:** Frontend Team
   - **Due:** Q1 2026

3. **Observability** (⚠️ Partial Coverage)
   - **Gap:** Manual validation only, no automated log/metric assertions
   - **Action:** Add `test_observability.py` with log capture and metric checks
   - **Owner:** SRE Team
   - **Due:** Q2 2026

4. **Leads Filtering** (⚠️ Partial Coverage)
   - **Gap:** Basic filter tests exist, complex queries untested
   - **Action:** Expand `test_contacts.py` with edge cases (empty results, pagination)
   - **Owner:** Backend Team
   - **Due:** Q1 2026

---

## Smoke Test Execution

### Quick Command

```bash
./scripts/smoke.sh
```

**Output:**
```
=== RiverCityClean QA Smoke Test Suite ===

[1/4] CRM API Smoke Tests...
  ✔ SMOKE-API-CRM-001: Health check
  ✔ SMOKE-API-CRM-002: Auth login
  ✔ SMOKE-API-CRM-003: Protected route (leads)
  ✔ SMOKE-API-CRM-004: RBAC denial (wrong role)

[2/4] Ops API Smoke Tests...
  ✔ SMOKE-API-OPS-001: Health check
  ✔ SMOKE-API-OPS-002: Auth login
  ✔ SMOKE-API-OPS-003: Protected route (system health)
  ✔ SMOKE-API-OPS-004: RBAC denial (wrong role)

[3/4] CRM SPA Smoke Tests...
  ✔ SMOKE-UI-CRM-001: Login renders and submits
  ✔ SMOKE-UI-CRM-002: Protected route with token
  ✔ SMOKE-UI-CRM-003: Route guard denies without token

[4/4] Ops SPA Smoke Tests...
  ✔ SMOKE-UI-OPS-001: Login renders and submits
  ✔ SMOKE-UI-OPS-002: Protected route with token
  ✔ SMOKE-UI-OPS-003: Route guard denies without token

=== Summary ===
Total: 16 tests
Passed: 16
Failed: 0
Duration: 8.3s

✅ All smoke tests passed!
```

---

## Continuous Integration

### Pre-Commit Hooks

- DLP scan (prevent secrets)
- Linting (pylint, ESLint)
- Type checking (mypy, TypeScript)

### CI Pipeline (GitHub Actions)

1. **Lint & Type Check** (30s)
2. **Unit Tests** (30s)
3. **Smoke Tests** (10s)
4. **Integration Tests** (2min)
5. **Performance Tests** (30s)
6. **Security Scans** (1min)
7. **Build** (2min)

**Total CI Time:** ~6 minutes

### Policy Gates (OPA)

Policy enforcement via `tools/policy/opa_stub.py`:
- All tests must pass
- Code coverage ≥85% backend / ≥80% frontend
- SBOM present and valid
- License compliance
- Performance budgets met
- No critical/high vulnerabilities

---

## Maintenance Schedule

- **Daily:** Smoke tests on every commit
- **Weekly:** Full integration test suite + performance tests
- **Monthly:** DR drill + compliance evidence collection
- **Quarterly:** Penetration testing + external audit prep

---

## Appendix: Test Data

### Demo Credentials

**CRM API:**
- Manager: `Nathan@RiverCityClean.com` / `password123`
- Sales: `sales@example.com` / `password123`
- Viewer: `viewer@example.com` / `password123`

**Ops API:**
- Admin: `Nathan@RiverCityClean.com` / `password123`
- Operator: `operator@example.com` / `password123`

**Note:** These are development credentials only. Production uses SSO.

---

**Document Owner:** QA Team
**Reviewers:** Platform Lead, Security Lead, SRE Lead
**Next Review:** 2026-02-01 (Quarterly)
