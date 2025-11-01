# Data Governance Runbook

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: Data Governance & Privacy Teams

## Overview

This runbook provides operational procedures for data governance, privacy compliance, and data protection for RiverCityClean services.

**Components**:
- Data classification and handling
- Retention policy enforcement
- Encryption and pseudonymization
- Data Subject Request (DSR) workflows
- Consent management
- Data Loss Prevention (DLP)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Data Classification](#data-classification)
3. [Encryption](#encryption)
4. [Retention Management](#retention-management)
5. [Data Subject Requests](#data-subject-requests)
6. [Consent Management](#consent-management)
7. [DLP Scanning](#dlp-scanning)
8. [Compliance SOPs](#compliance-sops)
9. [Incident Response](#incident-response)

---

## Quick Start

### Daily Operations

```bash
# Check consent expirations (daily)
python -c "from consent.manager import ConsentManager; ConsentManager().expire_consents()"

# Review pending DSR requests
python scripts/data/dsr.py list --status pending

# Scan codebase for sensitive data (before commits)
python tools/dlp/scan.py --path .
```

### Weekly Operations

```bash
# Review retention policy compliance (weekly, dry-run)
python scripts/data/retention_enforcer.py --all --dry-run

# Export retention report
python scripts/data/retention_enforcer.py --all --dry-run --report reports/retention_weekly.json
```

### Monthly Operations

```bash
# Enforce retention policies (monthly, with approval)
python scripts/data/retention_enforcer.py --all --execute

# Review DLP scan results
python tools/dlp/scan.py --report reports/dlp_monthly.json

# Audit encryption key usage
grep "DECRYPT_DEK" logs/kms_audit.jsonl | tail -100
```

---

## Data Classification

### Classification Levels

See `docs/data/classification.md` for complete classification guide.

**Summary**:
- **PUBLIC**: Marketing materials, public documentation
- **INTERNAL**: Business data, analytics, internal docs
- **CONFIDENTIAL**: Customer PII, financial data, contracts
- **RESTRICTED**: Authentication credentials, health data, government IDs

### Handling Requirements

| Level | Encryption | Access Control | Logging | Retention |
|-------|-----------|----------------|---------|-----------|
| PUBLIC | No | No restrictions | None | As needed |
| INTERNAL | At rest | Role-based | Access logs | Per policy |
| CONFIDENTIAL | At rest + transit | Need-to-know | All access | 7 years |
| RESTRICTED | Field-level + at rest + transit | Explicit approval | Every access | Minimal |

### Checking Classification

```python
from crypto.field_encryptor import FieldEncryptor

# Example: Classify customer data
customer_fields = {
    "id": "INTERNAL",           # Internal ID
    "email": "RESTRICTED",      # PII
    "name": "CONFIDENTIAL",     # PII
    "phone": "RESTRICTED",      # PII
    "address": "RESTRICTED",    # PII
    "created_at": "INTERNAL"    # Metadata
}

# Encrypt RESTRICTED fields
fields_to_encrypt = [k for k, v in customer_fields.items() if v == "RESTRICTED"]
```

---

## Encryption

### Envelope Encryption

Using KMS stub for offline/development:

```python
from crypto.kms_stub import KMSStub, EnvelopeEncryption

# Initialize KMS
kms = KMSStub()

# Create master key (do once)
kek_id = kms.create_master_key("customer-data-master-key")

# Encrypt data
envelope = EnvelopeEncryption(kms, kek_id)
encrypted_blob = envelope.encrypt(b"sensitive data")

# Decrypt data
plaintext = envelope.decrypt(encrypted_blob)
```

### Field-Level Encryption

For database PII fields:

```python
from crypto.field_encryptor import FieldEncryptor

# Initialize encryptor
kms = KMSStub()
kek_id = "customer-data-master-key"
encryptor = FieldEncryptor(kms, kek_id)

# Encrypt customer record
customer = {
    "id": 12345,
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+1-555-0100"
}

encrypted_customer = encryptor.encrypt_record(
    customer,
    fields_to_encrypt=["email", "phone"],
    context={"record_id": "12345"}
)

# Decrypt when needed
decrypted_customer = encryptor.decrypt_record(
    encrypted_customer,
    fields_to_decrypt=["email", "phone"],
    context={"record_id": "12345"}
)
```

### Pseudonymization

For analytics and logging (one-way):

```python
from crypto.field_encryptor import PseudonymizationEngine

# Initialize pseudonymizer
engine = PseudonymizationEngine(salt="your-secure-salt")

# Pseudonymize for logging
email_hash = engine.pseudonymize_email("user@example.com")
ip_hash = engine.pseudonymize_ip("192.168.1.100")

# Use in logs/analytics (cannot reverse)
logger.info(f"User login: {email_hash} from {ip_hash}")
```

### Key Rotation

Rotate master keys annually:

```python
kms = KMSStub()

# Rotate key (creates new version)
old_kek = "customer-data-master-key-v1"
new_kek = "customer-data-master-key-v2"

kms.rotate_master_key(old_kek, new_kek)

# Old encrypted data still decryptable with old key
# New encryptions use new key
```

---

## Retention Management

### Retention Policies

See `docs/data/retention.md` for complete policies.

**Key Policies**:
- **Customers**: 7 years after account closure (tax law)
- **Leads**: 2 years (legitimate interest)
- **Audit Logs**: 7 years (compliance)
- **Sessions**: 90 days (security monitoring)
- **Support Tickets**: 3 years, then anonymize

### Dry-Run Enforcement

Preview what would be deleted/anonymized:

```bash
# Preview all policies
python scripts/data/retention_enforcer.py --all --dry-run

# Preview specific entity
python scripts/data/retention_enforcer.py --entity customers --dry-run

# Export report
python scripts/data/retention_enforcer.py --all --dry-run --report retention_report.json
```

### Executing Enforcement

**⚠️ CAUTION**: This deletes/anonymizes data permanently.

```bash
# Execute all policies (requires approval)
python scripts/data/retention_enforcer.py --all --execute

# Execute specific entity
python scripts/data/retention_enforcer.py --entity sessions --execute
```

### List Retention Policies

```bash
python scripts/data/retention_enforcer.py --list-policies
```

**Output**:
```
Entity: customers
  Retention: 2555 days (7 years)
  Legal basis: Tax law (7 years), contractual obligations
  Action: delete

Entity: leads
  Retention: 730 days (2 years)
  Legal basis: Legitimate interest (GDPR Art. 6(1)(f))
  Action: delete
...
```

---

## Data Subject Requests

### DSR Types

- **Access**: Export all user data
- **Portability**: Export in portable format (JSON)
- **Rectification**: Correct inaccurate data
- **Erasure**: Delete all user data (right to be forgotten)

### Creating DSR

**Access Request**:
```bash
python scripts/data/dsr.py access \
  --user-id user_12345 \
  --user-email user@example.com \
  --reason "User requested data export"
```

**Erasure Request**:
```bash
python scripts/data/dsr.py erase \
  --user-id user_12345 \
  --user-email user@example.com \
  --reason "User account deletion request"
```

**Rectification Request**:
```bash
python scripts/data/dsr.py rectify \
  --user-id user_12345 \
  --user-email user@example.com \
  --corrections '{"email": "newemail@example.com", "phone": "+1-555-9999"}'
```

### Approving DSR

```bash
# Approve request
python scripts/data/dsr.py approve \
  --request-id dsr_abc123 \
  --approver admin@example.com

# Reject request
python scripts/data/dsr.py reject \
  --request-id dsr_abc123 \
  --approver admin@example.com \
  --reason "Unable to verify identity"
```

### Processing DSR

```bash
# Process all approved requests
python scripts/data/dsr.py process
```

**Output**:
```
Request: dsr_abc123 (access)
  Status: completed
  Export: artifacts/dsr_exports/dsr_abc123_user_12345_access.json

Request: dsr_def456 (erase)
  Status: completed
  Deleted entities: customers, leads, sessions, audit_logs, support_tickets
```

### Listing DSR

```bash
# List all pending requests
python scripts/data/dsr.py list --status pending

# List all requests for user
python scripts/data/dsr.py list --user-id user_12345
```

---

## Consent Management

### Consent Purposes

- **Essential**: Required for service (always enabled)
- **Analytics**: Usage analytics
- **Marketing**: Marketing emails
- **Personalization**: Personalized content
- **Third-party sharing**: Share with partners
- **Profiling**: Automated decision-making

### Programmatic Consent

```python
from consent.manager import ConsentManager
from consent.models import ConsentPurpose

manager = ConsentManager()

# Give consent
manager.give_consent(
    user_id="user_12345",
    purpose=ConsentPurpose.ANALYTICS,
    ip_address="203.0.113.1"
)

# Check consent
has_consent = manager.has_consent("user_12345", ConsentPurpose.ANALYTICS)

# Withdraw consent
manager.withdraw_consent(
    user_id="user_12345",
    purpose=ConsentPurpose.MARKETING
)

# Get all consents
preferences = manager.get_user_consents("user_12345")
active_purposes = preferences.get_active_consents()
```

### Bulk Consent

```python
from consent.models import ConsentPurpose

# Give consent for multiple purposes
purposes = [
    ConsentPurpose.ANALYTICS,
    ConsentPurpose.MARKETING,
    ConsentPurpose.PERSONALIZATION
]

manager.bulk_give_consent(
    user_id="user_12345",
    purposes=purposes,
    ip_address="203.0.113.1"
)
```

### Consent Expiration

Run daily to expire old consents:

```python
from consent.manager import ConsentManager

manager = ConsentManager()
expired_count = manager.expire_consents()
print(f"Marked {expired_count} consents as expired")
```

### UI Integration

**Consent Banner** (first visit):
```tsx
import { ConsentBanner } from './consent/ui/ConsentBanner';

function App() {
  return (
    <>
      <ConsentBanner userId="user_123" />
      <YourApp />
    </>
  );
}
```

**Preferences Page** (settings):
```tsx
import { ConsentPreferences } from './consent/ui/ConsentPreferences';

function SettingsPage() {
  return <ConsentPreferences userId="user_123" />;
}
```

---

## DLP Scanning

### Scanning Codebase

**Before commit** (recommended in pre-commit hook):
```bash
python tools/dlp/scan.py
```

**Scan specific directory**:
```bash
python tools/dlp/scan.py --path docs/
```

**Fail on findings** (for CI/CD):
```bash
python tools/dlp/scan.py --fail-on-findings
```

**Generate report**:
```bash
python tools/dlp/scan.py --report dlp_report.json
```

### Testing DLP Scanner

```bash
# Create test sample and scan
python tools/dlp/scan.py --test
```

**Output**:
```
Created test sample: tools/dlp/test_sample.txt

Found 15 violations in test sample:

  - CRITICAL: API Key (line 11)
  - CRITICAL: Secret Key (line 12)
  - CRITICAL: Password (line 13)
  - HIGH: Social Security Number (line 7)
  - HIGH: Credit Card Number (line 9)
  ...
```

### Whitelisting False Positives

Edit `tools/dlp/whitelist.json`:

```json
[
  {
    "file_pattern": ".*test.*",
    "reason": "Test files may contain sample data"
  },
  {
    "file": "docs/example.md",
    "pattern_id": "email",
    "line": 42,
    "reason": "Documentation example email"
  }
]
```

### CI/CD Integration

Add to `.github/workflows/security.yml`:

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  dlp-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: DLP Scan
        run: python tools/dlp/scan.py --fail-on-findings
```

---

## Compliance SOPs

### SOP 1: New User Registration

When a new user registers:

1. **Collect consent** for non-essential purposes
2. **Classify data** according to classification guide
3. **Encrypt PII** fields (email, phone, address)
4. **Log action** with user ID and timestamp
5. **Schedule retention** based on account type

```python
# Example registration flow
from consent.manager import ConsentManager
from crypto.field_encryptor import FieldEncryptor

# 1. Collect consent
consent_manager = ConsentManager()
consent_manager.give_consent(user_id, ConsentPurpose.ESSENTIAL)

# 2-3. Encrypt PII
encryptor = FieldEncryptor(kms, kek_id)
encrypted_user = encryptor.encrypt_record(
    user_data,
    fields_to_encrypt=["email", "phone", "address"]
)

# 4. Save to database with encryption
db.save(encrypted_user)

# 5. Set retention schedule (automatic)
```

### SOP 2: Account Deletion

When a user requests account deletion:

1. **Create DSR** for erasure
2. **Require approval** from privacy team
3. **Export data** before deletion (audit)
4. **Delete across all systems** (CRM, Ops, backups)
5. **Notify user** of completion

```bash
# 1. Create erasure request
python scripts/data/dsr.py erase --user-id user_12345 --user-email user@example.com

# 2. Approve (privacy team)
python scripts/data/dsr.py approve --request-id dsr_abc123 --approver privacy@example.com

# 3-4. Process (exports then deletes)
python scripts/data/dsr.py process

# 5. Send notification email (manual or automated)
```

### SOP 3: Data Breach Response

If sensitive data is exposed:

1. **Identify scope**: Which data, how many users
2. **Contain breach**: Revoke credentials, block access
3. **Assess impact**: Classification level, consent status
4. **Notify users**: Within 72 hours (GDPR)
5. **Document incident**: Audit log, lessons learned
6. **Remediate**: Rotate keys, update policies

### SOP 4: Consent Withdrawal

When user withdraws consent:

1. **Update consent** immediately
2. **Stop processing** for that purpose
3. **Delete associated data** if no longer needed
4. **Log withdrawal** with timestamp
5. **Confirm to user**

```python
from consent.manager import ConsentManager

# 1. Withdraw consent
manager = ConsentManager()
manager.withdraw_consent(user_id, ConsentPurpose.MARKETING)

# 2-3. Stop marketing, delete marketing data
# (Application-specific logic)

# 4-5. Confirmation logged automatically
```

---

## Incident Response

### Scenario 1: Unencrypted PII in Logs

**Alert**: DLP scanner finds email addresses in application logs

**Response**:
1. Stop log collection immediately
2. Delete exposed logs: `rm logs/app_*.log`
3. Review code for log statements with PII
4. Update logger to use pseudonymization
5. Re-deploy with fix
6. Assess if breach notification required

### Scenario 2: Expired Consent Still Being Used

**Alert**: Marketing emails sent to users without active consent

**Response**:
1. Stop all marketing sends
2. Run consent expiration: `python -c "from consent.manager import ConsentManager; ConsentManager().expire_consents()"`
3. Review consent checking logic in email service
4. Update application to check consent before sending
5. Apologize to affected users
6. Document incident

### Scenario 3: Retention Policy Not Enforced

**Alert**: Audit finds data older than retention period

**Response**:
1. Run dry-run to assess scope: `python scripts/data/retention_enforcer.py --all --dry-run`
2. Export report for review
3. Get approval from legal/privacy team
4. Execute enforcement: `python scripts/data/retention_enforcer.py --all --execute`
5. Review enforcement logs
6. Update automation to prevent recurrence

### Scenario 4: DSR Not Completed in Time

**Alert**: Access request created 45 days ago, not completed (GDPR: 30 days)

**Response**:
1. List pending requests: `python scripts/data/dsr.py list --status pending`
2. Prioritize overdue requests
3. Expedite approval process
4. Process immediately: `python scripts/data/dsr.py process`
5. Deliver export to user with apology
6. Implement SLA monitoring

---

## Compliance Mapping

| Framework | Control | Implementation |
|-----------|---------|----------------|
| GDPR Art. 5 | Data Minimization | Classification guide, retention policies |
| GDPR Art. 6 | Lawful Basis | Consent management, legal basis in retention |
| GDPR Art. 15-22 | Data Subject Rights | DSR workflow (access, rectify, erase, portability) |
| GDPR Art. 25 | Privacy by Design | Encryption by default, pseudonymization |
| GDPR Art. 32 | Security | Envelope encryption, field-level encryption, DLP |
| GDPR Art. 33 | Breach Notification | Incident response SOPs, audit logging |
| CCPA § 1798.100 | Right to Know | DSR access workflow |
| CCPA § 1798.105 | Right to Delete | DSR erasure workflow |
| SOC 2 CC6.1 | Logical Access | Classification-based access control |
| SOC 2 CC6.7 | Encryption | KMS, envelope encryption, field encryption |
| ISO 27001 A.8.2.3 | Asset Handling | Classification guide, handling requirements |
| ISO 27001 A.18.1.4 | Privacy | Consent management, DSR workflows |

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-01 | 1.0 | Initial runbook |

---

## References

- [Data Classification Guide](classification.md)
- [Retention Policy](retention.md)
- [Observability Runbook](../observability/runbook.md)
- [Supply Chain Security](../supply-chain/SBOM.md)
