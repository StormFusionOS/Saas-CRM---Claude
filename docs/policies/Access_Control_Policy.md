# Access Control Policy

**Version**: 1.0
**Effective Date**: 2025-11-01
**Owner**: Security Team
**Review Frequency**: Annual

## Purpose

Define and enforce access control requirements for the RiverCityClean SaaS platform to protect customer data and system resources.

## Scope

Applies to all systems, applications, data, and users within the River CityClean environment.

## Policy Statements

### 1. Principle of Least Privilege

Access rights are granted based on minimum permissions necessary to perform job functions.

**Controls**:
- Role-Based Access Control (RBAC) implemented across CRM and Ops APIs
- Attribute-Based Access Control (ABAC) for fine-grained permissions
- Regular access reviews (quarterly)

**Implementation**: `policy/policy_engine.py`, RBAC tests

### 2. Separation of Duties (SoD)

Critical functions require multiple individuals to prevent fraud and errors.

**Controls**:
- CRM and Ops roles cannot be combined (except OWNER for break-glass)
- Dual approval required for break-glass access
- Enforced programmatically in policy engine

**Implementation**: `policy/access.rego` (SoD rules), `policy/policy_engine.py`

### 3. Authentication Requirements

All access must be authenticated using enterprise SSO.

**Controls**:
- OIDC/SAML integration with IdP (Okta/Azure AD/Google Workspace)
- Multi-factor authentication (MFA) required for production access
- Session timeout: 15 minutes idle, 8 hours maximum
- JWT token expiration: 1 hour

**Implementation**: `identity/oidc_stub.py`, `identity/saml_stub.py`

### 4. Authorization Enforcement

Access decisions based on user attributes and resource classifications.

**Controls**:
- Environment scoping (dev/staging/production)
- Data domain restrictions (CRM/Ops separation)
- Department-based access control
- Deny-by-default policy

**Implementation**: `policy/policy_engine.py` (ABAC engine)

### 5. Break-Glass Access

Emergency access procedures for critical incidents.

**Controls**:
- Dual approval required (minimum 2 approvers)
- Time-limited access (default 4 hours, maximum 24 hours)
- Justification required
- Immutable audit logging
- Automatic revocation after TTL

**Implementation**: `docs/security/break_glass.md`, `scripts/access/approve_temp_role.py`

### 6. Access Review & Recertification

Periodic review of access rights to ensure appropriateness.

**Controls**:
- Quarterly access reviews by managers
- Annual recertification for privileged access
- Immediate revocation upon termination
- Dormant account deactivation (90 days)

### 7. Audit & Monitoring

All access events logged and monitored.

**Controls**:
- Immutable audit logs (7-year retention)
- Real-time alerting for anomalous access
- SIEM integration
- Quarterly audit log reviews

**Implementation**: Break-glass audit log, future SIEM integration

## Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| Security Team | Policy enforcement, monitoring, incident response |
| Engineering Managers | Access approval, quarterly reviews |
| System Owners | Resource classification, access requirements |
| Users | Compliance with policy, secure credential management |

## Enforcement

Violations may result in:
- Access revocation
- Security incident investigation
- Disciplinary action up to termination
- Legal action if criminal activity

## Compliance

Supports: SOC 2 CC6.7, ISO 27001 A.9, NIST CSF PR.AC

## Appendix

Related Documentation:
- Break-Glass Procedures: `docs/security/break_glass.md`
- ABAC Policy Rules: `policy/access.rego`
- Compliance Mapping: `docs/enterprise/controls-map.md`
