# Identity & Compliance System Guide

**Purpose**: Complete guide to the enterprise-grade identity and compliance system.

**Version**: 1.0
**Last Updated**: 2025-11-01

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [SSO Integration](#sso-integration)
3. [RBAC/ABAC Enforcement](#rbacabac-enforcement)
4. [Break-Glass Procedures](#break-glass-procedures)
5. [Secrets Management](#secrets-management)
6. [Testing & Validation](#testing--validation)
7. [Compliance](#compliance)

---

## Overview

The RiverCityClean Identity & Compliance system provides:

- ✅ **Enterprise SSO**: OIDC and SAML 2.0 integration (offline stubs)
- ✅ **RBAC/ABAC**: Role and attribute-based access control
- ✅ **Separation of Duties**: CRM and Ops role isolation
- ✅ **Break-Glass**: Dual-approval emergency access
- ✅ **Key Rotation**: JWKS rotation with grace periods
- ✅ **Compliance**: SOC 2, ISO 27001, NIST CSF mappings

**Architecture**:
- **Tenants**: CRM and Ops (strictly separated)
- **IdP Support**: Okta, Azure AD, Google Workspace (stubs for offline testing)
- **Policy Engine**: OPA-style Rego policies with Python evaluator
- **Audit**: Immutable logging for all access events

---

## SSO Integration

### OIDC (OpenID Connect)

**Supported IdPs**: Okta, Azure AD, Google Workspace

**Implementation**: `identity/oidc_stub.py`

**Basic Usage**:

```python
from identity.oidc_stub import OIDCProvider, OIDCClient

# Initialize provider (IdP simulator)
provider = OIDCProvider(
    issuer="https://dev-12345.okta.com",
    kid="key-20241101-abc123",
    idp_type="okta"
)

# Initialize client (your app)
client = OIDCClient(
    client_id="crm-app-client",
    client_secret="app-secret",
    redirect_uri="https://crm.rivercityclean.com/callback"
)

# Generate authorization URL
auth_url, state, nonce = client.get_authorization_url(provider)

# User authenticates at IdP...

# Exchange code for tokens
code = "<authorization_code_from_idp>"
tokens = client.exchange_code(code, provider)

# Validate ID token
claims = client.validate_id_token(tokens["id_token"], nonce, provider)

# Use claims for authorization
user_roles = claims["roles"]  # ["SALES"]
user_dept = claims["department"]  # "sales"
```

**Security Features**:
- Nonce validation (replay prevention)
- State parameter (CSRF protection)
- Audience verification
- Issuer verification
- Kid (key ID) validation
- Clock skew tolerance (300 seconds default)

**Test Coverage**:
- ✅ Successful login flow
- ✅ Nonce replay rejection
- ✅ Wrong audience rejection
- ✅ Wrong issuer rejection
- ✅ Wrong kid rejection
- ✅ Clock skew tolerance

### SAML 2.0

**Supported IdPs**: Okta SAML, Azure AD SAML, Google Workspace SAML

**Implementation**: `identity/saml_stub.py`

**Basic Usage**:

```python
from identity.saml_stub import SAMLIdentityProvider, SAMLServiceProvider

# Initialize IdP (simulator)
idp = SAMLIdentityProvider(
    entity_id="http://www.okta.com/exk1234567890",
    sso_url="https://dev-12345.okta.com/app/app1234567890/sso/saml"
)

# Initialize SP (your app)
sp = SAMLServiceProvider(
    entity_id="https://crm.rivercityclean.com",
    acs_url="https://crm.rivercityclean.com/saml/acs"
)

# Create AuthnRequest
authn_request_xml, relay_state = sp.create_authn_request(idp)

# User authenticates at IdP...

# Validate SAML response at ACS
saml_response_b64 = "<saml_response_from_idp>"
assertion = sp.validate_saml_response(saml_response_b64, idp, relay_state)

# Use assertion attributes
user_email = assertion.subject  # "user@example.com"
user_roles = assertion.attributes["roles"]  # ["SALES"]
```

**Security Features**:
- Relay state validation
- Audience restriction
- Conditions validation (NotBefore, NotOnOrAfter)
- Issuer verification
- Clock skew tolerance

**Test Coverage**:
- ✅ Successful login flow
- ✅ Wrong audience rejection
- ✅ Invalid relay state rejection

### Switching from Stub to Real IdP

**Step 1**: Install real libraries

```bash
# For OIDC
pip install authlib requests

# For SAML
pip install python3-saml
```

**Step 2**: Update configuration

Replace stub provider initialization with real IdP metadata:

```python
# OIDC with Authlib
from authlib.integrations.requests_client import OAuth2Session

client = OAuth2Session(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://yourapp.com/callback"
)

# Discovery
metadata = client.load_server_metadata(
    "https://your-idp.com/.well-known/openid-configuration"
)
```

**Step 3**: Update routes (see SSO Routes section)

---

## RBAC/ABAC Enforcement

### Policy Engine

**Implementation**: `policy/policy_engine.py`, `policy/access.rego`

**Features**:
- Deny-by-default
- Separation of Duties (SoD) enforcement
- Environment scoping (dev/staging/production)
- Data domain restrictions (CRM vs Ops)
- Department-based access
- Break-glass override

**Basic Usage**:

```python
from policy.policy_engine import PolicyEngine, check_access

# Method 1: Using engine directly
engine = PolicyEngine()

decision = engine.evaluate(
    user={
        "roles": ["SALES"],
        "department": "sales",
        "environment": "production"
    },
    resource={
        "environment": "production",
        "data_domain": "customer_data",
        "department": "sales"
    }
)

if decision.allowed:
    # Grant access
    pass
else:
    # Deny access
    print(f"Access denied: {decision.deny_reason}")

# Method 2: Convenience function
decision = check_access(
    user={"roles": ["SALES"], "department": "sales"},
    resource={"data_domain": "customer_data", "department": "sales"}
)
```

### Separation of Duties (SoD)

**Rule**: CRM and Ops roles cannot be combined (except OWNER for break-glass).

**Enforcement**:

```python
from policy.policy_engine import enforce_sod

# Valid: CRM only
enforce_sod(["SALES", "SALES_MANAGER"])  # OK

# Valid: Ops only
enforce_sod(["DEVOPS", "SEO_ENGINEER"])  # OK

# Valid: OWNER with both (break-glass)
enforce_sod(["OWNER", "SALES", "DEVOPS"])  # OK

# Invalid: Both without OWNER
enforce_sod(["SALES", "DEVOPS"])  # Raises ValueError
```

**Test Coverage**:
- ✅ SoD violation detection
- ✅ OWNER exception
- ✅ Environment scoping
- ✅ Data domain restrictions
- ✅ Department restrictions
- ✅ Break-glass override

### Environment Hierarchy

```
development (level 1)
    ↓ (can access)
staging (level 2)
    ↓ (can access)
production (level 3)
```

- **Development users**: Can access dev only
- **Staging users**: Can access dev + staging
- **Production users**: Can access all environments

### Data Domain Mapping

**CRM Domains**:
- `customer_data`
- `lead_data`
- `sales_data`

**Ops Domains**:
- `infrastructure`
- `monitoring`
- `security`

**Access Matrix**:

| Role         | CRM Domains | Ops Domains |
|--------------|-------------|-------------|
| SALES        | ✅          | ❌          |
| SALES_MANAGER| ✅          | ❌          |
| SEO_ENGINEER | ❌          | ✅          |
| DEVOPS       | ❌          | ✅          |
| OWNER        | ✅          | ✅          |

---

## Break-Glass Procedures

**Purpose**: Emergency privilege elevation with dual approval.

**Documentation**: `docs/security/break_glass.md`
**Implementation**: `scripts/access/approve_temp_role.py`

### Request Break-Glass Access

```bash
python scripts/access/approve_temp_role.py request \
    --user devops@rivercityclean.com \
    --reason "Critical production database corruption requires manual repair" \
    --duration 4  # hours
```

**Output**:
```
Break-Glass Request Created
===========================
Request ID: bg-2024-11-01-001
User: devops@rivercityclean.com
Reason: Critical production database corruption requires manual repair
Duration: 4 hours
Status: PENDING_APPROVAL
Approvers Needed: 2
```

### Approve Request (Dual Approval)

**First Approver**:
```bash
python scripts/access/approve_temp_role.py approve \
    --request-id bg-2024-11-01-001 \
    --approver manager1@rivercityclean.com
```

**Second Approver**:
```bash
python scripts/access/approve_temp_role.py approve \
    --request-id bg-2024-11-01-001 \
    --approver manager2@rivercityclean.com
```

**After Second Approval**:
```
✅ Break-Glass Access APPROVED
==============================
Request ID: bg-2024-11-01-001
User: devops@rivercityclean.com
Approvers: manager1@rivercityclean.com, manager2@rivercityclean.com
Granted At: 2024-11-01T14:35:00Z
Expires At: 2024-11-01T18:35:00Z (in 4 hours)

Temporary Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Check Status

```bash
python scripts/access/approve_temp_role.py status \
    --request-id bg-2024-11-01-001
```

### Revoke Access

```bash
python scripts/access/approve_temp_role.py revoke \
    --request-id bg-2024-11-01-001 \
    --revoker security@rivercityclean.com \
    --reason "Incident resolved"
```

### Generate Audit Report

```bash
python scripts/access/approve_temp_role.py report \
    --start-date 2024-01-01 \
    --end-date 2024-12-31
```

**Security Controls**:
- ✅ Dual approval enforced (minimum 2)
- ✅ Self-approval prevented
- ✅ Time-limited (auto-expiration)
- ✅ Immutable audit log
- ✅ Real-time alerting

---

## Secrets Management

### Key Rotation

**Implementation**: `scripts/keys/rotate.py`

**Normal Rotation** (90-day interval):

```bash
# Rotate keys for all tenants (CRM + Ops)
python scripts/keys/rotate.py --tenant all --grace-period 72
```

**Output**:
```
============================================================
Rotating keys for tenant: CRM
============================================================

✅ New key generated: key-20241101-abc123
✅ JWKS updated with 2 active key(s)
   Primary (new) key: key-20241101-abc123
   Grace period: 72h
   Keeping key key-20241029-xyz789 (expires in 48.0h)

✅ Key Rotation Complete
```

**Emergency Rotation** (immediate invalidation):

```bash
python scripts/keys/rotate.py --tenant all --emergency
```

**Validate Rotation**:

```bash
python scripts/keys/rotate.py --validate
```

### JWKS Structure

**Location**: `secrets/keys/{tenant}_jwks.json`

**Example**:
```json
{
  "keys": [
    {
      "kty": "oct",
      "use": "sig",
      "kid": "key-20241101-abc123",
      "alg": "HS256",
      "k": "encoded-secret-key",
      "created_at": 1730476800.0,
      "expires_at": 1730736000.0
    }
  ]
}
```

### Secret Patterns to Deny

**Pre-commit Hook** (to add):

```bash
# Add to .git/hooks/pre-commit

# Patterns to block
grep -r "password\s*=\s*['\"]" --include="*.py" --include="*.ts" .
grep -r "api_key\s*=\s*['\"]" --include="*.py" --include="*.ts" .
grep -r "secret\s*=\s*['\"]" --include="*.py" --include="*.ts" .
```

**Note**: secrets/ directory is already in .gitignore

---

## Testing & Validation

### Run All Identity & Compliance Tests

```bash
# Run comprehensive test suite
cd /home/user/Saas-CRM---Claude
pytest tests/test_identity_compliance.py -v
```

**Test Coverage**:
- ✅ OIDC: 6 tests (login, nonce replay, audience, issuer, kid, clock skew)
- ✅ SAML: 3 tests (login, audience, relay state)
- ✅ ABAC: 10 tests (SoD, environment, data domain, department, break-glass)
- ✅ Total: 19 comprehensive tests

### Run Specific Test Categories

```bash
# OIDC tests only
pytest tests/test_identity_compliance.py::test_oidc -v

# SAML tests only
pytest tests/test_identity_compliance.py::test_saml -v

# ABAC tests only
pytest tests/test_identity_compliance.py::test_abac -v

# Break-glass tests
pytest tests/test_identity_compliance.py::test_abac_break_glass -v
```

### Manual Testing

**1. Test OIDC Flow**:

```python
from identity.oidc_stub import OIDCProvider, OIDCClient, create_stub_user_claims

provider = OIDCProvider(issuer="https://idp.test.com", kid="test-key")
client = OIDCClient(client_id="test", client_secret="secret", redirect_uri="http://localhost/callback")

# Get auth URL
auth_url, state, nonce = client.get_authorization_url(provider)
print(f"Auth URL: {auth_url}")

# Simulate auth and get code
user_claims = create_stub_user_claims(email="test@example.com", roles=["SALES"])
code = provider.generate_authorization_code(client.client_id, client.redirect_uri, nonce, user_claims)

# Exchange for tokens
tokens = client.exchange_code(code, provider)
claims = client.validate_id_token(tokens["id_token"], nonce, provider)

print(f"User: {claims['email']}, Roles: {claims['roles']}")
```

**2. Test ABAC Policy**:

```python
from policy.policy_engine import check_access

# Allowed access
decision = check_access(
    user={"roles": ["SALES"], "department": "sales", "environment": "production"},
    resource={"data_domain": "customer_data", "department": "sales", "environment": "production"}
)
print(f"Allowed: {decision.allowed}")  # True

# Denied access (SoD violation)
decision = check_access(
    user={"roles": ["SALES", "DEVOPS"], "department": "engineering"},  # SoD violation!
    resource={"data_domain": "customer_data", "department": "engineering"}
)
print(f"Allowed: {decision.allowed}, Reason: {decision.deny_reason}")  # False, SoD violation
```

**3. Test Break-Glass**:

```bash
# Create request
python scripts/access/approve_temp_role.py request --user test@example.com --reason "Test" --duration 1

# Approve (need 2 approvals)
python scripts/access/approve_temp_role.py approve --request-id <ID> --approver approver1@example.com
python scripts/access/approve_temp_role.py approve --request-id <ID> --approver approver2@example.com

# Check status
python scripts/access/approve_temp_role.py status --request-id <ID>
```

**4. Test Key Rotation**:

```bash
# Rotate keys
python scripts/keys/rotate.py --tenant crm --grace-period 72

# Validate
python scripts/keys/rotate.py --validate

# Check JWKS
cat secrets/keys/crm_jwks.json | jq .
```

---

## Compliance

### SOC 2 Readiness

**Controls Implemented**:

| SOC 2 CC | Control | Implementation |
|----------|---------|----------------|
| CC6.6    | Logical Access Security | OIDC/SAML SSO, RBAC/ABAC |
| CC6.7    | Access Restriction | SoD, data domain restrictions |
| CC6.8    | Identification & Authentication | JWT validation, nonce checking |
| CC7.5    | Security Risk Assessment | Policy engine, audit logging |

**Evidence Locations**:
- SSO Implementation: `identity/oidc_stub.py`, `identity/saml_stub.py`
- RBAC/ABAC: `policy/policy_engine.py`, `policy/access.rego`
- Break-Glass: `docs/security/break_glass.md`, audit logs
- Tests: `tests/test_identity_compliance.py`

**Readiness**: See `docs/compliance/soc2/readiness.md` (to be created)

### ISO 27001 Compliance

**Annex A Controls**:

| Control | Name | Implementation |
|---------|------|----------------|
| A.9.1   | Access Control Policy | `docs/policies/Access_Control_Policy.md` |
| A.9.2   | User Access Provisioning | SSO integration, break-glass workflow |
| A.9.3   | Privileged Access Management | OWNER role, dual approval |
| A.9.4   | Secret Authentication | JWKS rotation, key management |

### NIST CSF Mapping

**Functions Supported**:

| Function | Subcategory | Implementation |
|----------|-------------|----------------|
| IDENTIFY | ID.RA-3 | Risk-based access (environment scoping) |
| PROTECT  | PR.AC-1 | Identity management (SSO) |
| PROTECT  | PR.AC-4 | Access permissions (RBAC/ABAC) |
| DETECT   | DE.CM-7 | Unauthorized access monitoring (audit log) |

---

## Quick Reference Commands

```bash
# SSO Tests
pytest tests/test_identity_compliance.py::test_oidc -v
pytest tests/test_identity_compliance.py::test_saml -v

# ABAC Tests
pytest tests/test_identity_compliance.py::test_abac -v

# Break-Glass
python scripts/access/approve_temp_role.py request --user <email> --reason "<reason>" --duration 4
python scripts/access/approve_temp_role.py approve --request-id <id> --approver <email>
python scripts/access/approve_temp_role.py status --request-id <id>

# Key Rotation
python scripts/keys/rotate.py --tenant all --grace-period 72
python scripts/keys/rotate.py --emergency  # Emergency rotation
python scripts/keys/rotate.py --validate   # Validate only

# Audit
python scripts/access/approve_temp_role.py report --start-date 2024-01-01 --end-date 2024-12-31
cat secrets/break_glass_audit.log | jq .
```

---

## File Locations

**Identity Stubs**:
- `identity/oidc_stub.py` - OIDC provider and client
- `identity/saml_stub.py` - SAML IdP and SP

**Policy Engine**:
- `policy/access.rego` - OPA-style policy rules
- `policy/policy_engine.py` - Python policy evaluator

**Break-Glass**:
- `docs/security/break_glass.md` - Procedures
- `scripts/access/approve_temp_role.py` - Approval workflow

**Secrets & Keys**:
- `scripts/keys/rotate.py` - Key rotation
- `secrets/keys/*_jwks.json` - JWKS keystores
- `secrets/break_glass_requests/` - Request storage
- `secrets/break_glass_audit.log` - Audit log

**Tests**:
- `tests/test_identity_compliance.py` - All tests

**Policies**:
- `docs/policies/Access_Control_Policy.md`
- Additional policies in `docs/policies/`

**Compliance**:
- `docs/enterprise/controls-map.md` - Framework mappings
- `docs/compliance/soc2/` - SOC 2 documentation

---

## Next Steps

1. **Integration**: Add SSO routes to CRM and Ops APIs
2. **Production**: Replace stubs with real IdP libraries
3. **Monitoring**: Integrate with SIEM for audit logs
4. **Testing**: Add integration tests with real IdPs (staging)
5. **Documentation**: Complete SOC 2 readiness documentation

---

**For Questions**: Contact security@rivercityclean.com
**For Incidents**: Use break-glass procedures in `docs/security/break_glass.md`
