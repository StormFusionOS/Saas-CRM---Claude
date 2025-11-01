# Break-Glass Access Procedures

**Purpose**: Emergency access procedures for temporary privilege elevation in critical situations.

**Owner**: Security Team
**Last Updated**: 2025-11-01
**Review Cadence**: Quarterly

---

## Overview

Break-glass access allows temporary privilege escalation to the OWNER role for emergency situations where normal access controls would prevent critical operations.

**Key Principles**:
- **Dual Approval Required**: At least 2 approvers must authorize break-glass access
- **Time-Limited**: Access automatically expires after TTL (default: 4 hours)
- **Immutable Audit Log**: All break-glass events are logged with approvers, reason, and duration
- **Justification Required**: Every break-glass request must include a detailed reason
- **Automatic Revocation**: Access is automatically revoked after TTL expires

---

## When to Use Break-Glass

### ✅ Appropriate Use Cases

1. **Production Incident Response**
   - Critical system outage requiring cross-team access
   - Data recovery requiring elevated privileges
   - Security incident requiring immediate containment

2. **Emergency Maintenance**
   - Critical security patch deployment outside change window
   - Database corruption requiring manual intervention
   - Infrastructure failure requiring immediate remediation

3. **Business Continuity**
   - Key personnel unavailable during critical operations
   - Disaster recovery procedures requiring elevated access
   - Regulatory compliance requiring emergency data access

### ❌ Inappropriate Use Cases

1. **Convenience**: Bypassing normal approval processes
2. **Curiosity**: Accessing data outside normal job function
3. **Testing**: Using production for development/testing
4. **Workaround**: Avoiding proper access request procedures

---

## Break-Glass Workflow

### Step 1: Request Break-Glass Access

**Requester Actions**:

```bash
# Request temporary OWNER elevation
python scripts/access/approve_temp_role.py request \
    --user "devops@rivercityclean.com" \
    --reason "Critical production database corruption requires manual repair" \
    --duration 4  # Hours
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

Waiting for approvals...
```

### Step 2: Dual Approval

**First Approver**:
```bash
python scripts/access/approve_temp_role.py approve \
    --request-id bg-2024-11-01-001 \
    --approver "manager1@rivercityclean.com"
```

**Output**:
```
Approval 1/2 Recorded
====================
Approver: manager1@rivercityclean.com
Approved At: 2024-11-01T14:30:00Z

Waiting for 1 more approval...
```

**Second Approver**:
```bash
python scripts/access/approve_temp_role.py approve \
    --request-id bg-2024-11-01-001 \
    --approver "manager2@rivercityclean.com"
```

**Output**:
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

IMPORTANT: This token grants OWNER-level access across all systems.
           Use responsibly and only for the stated reason.
           All actions will be audited.
```

### Step 3: Use Temporary Access

**Using the Token**:

```bash
# Export token as environment variable
export BREAK_GLASS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use with API calls
curl -H "Authorization: Bearer $BREAK_GLASS_TOKEN" \
     https://api.rivercityclean.com/admin/emergency-repair

# Or use with CLI tools
./admin-tool --token "$BREAK_GLASS_TOKEN" repair-database
```

**Token Claims**:
```json
{
  "sub": "devops@rivercityclean.com",
  "roles": ["OWNER"],
  "break_glass_approved": true,
  "break_glass_approvers": [
    "manager1@rivercityclean.com",
    "manager2@rivercityclean.com"
  ],
  "break_glass_request_id": "bg-2024-11-01-001",
  "break_glass_reason": "Critical production database corruption requires manual repair",
  "break_glass_expires_at": 1698854100,
  "exp": 1698854100,
  "iat": 1698839700
}
```

### Step 4: Automatic Revocation

Access is automatically revoked when:
- TTL expires (after specified duration)
- Manual revocation by approver
- Security event triggers revocation

**Check Access Status**:
```bash
python scripts/access/approve_temp_role.py status \
    --request-id bg-2024-11-01-001
```

**Manual Revocation** (if needed):
```bash
python scripts/access/approve_temp_role.py revoke \
    --request-id bg-2024-11-01-001 \
    --revoker "security@rivercityclean.com" \
    --reason "Incident resolved, access no longer needed"
```

---

## Approval Authority

### Who Can Approve Break-Glass Requests

**Tier 1 Approvers** (minimum 1 required from each tier):
- Engineering Managers
- Security Team Leads
- DevOps Leads

**Tier 2 Approvers** (minimum 1 required):
- CTO / VP Engineering
- CISO / Security Director
- Operations Director

**Self-Approval Prohibited**: Requester cannot be an approver for their own request.

---

## Separation of Duties Enforcement

Even with break-glass access, **Separation of Duties (SoD) is still enforced**:

### ✅ Allowed
- Temporary OWNER role grants universal access
- Can access both CRM and Ops APIs
- Can perform cross-team operations

### ❌ Forbidden
- Cannot add permanent CRM + Ops roles to same user account
- Cannot bypass audit logging
- Cannot grant break-glass to others without dual approval

**Example**: A DevOps engineer with break-glass can access CRM data temporarily, but the policy engine will still validate that they don't have permanent conflicting roles.

---

## Audit Logging

All break-glass events are logged to an **immutable audit trail**:

### Log Entries

**Request Created**:
```json
{
  "event_type": "break_glass_request",
  "timestamp": "2024-11-01T14:25:00Z",
  "request_id": "bg-2024-11-01-001",
  "requester": "devops@rivercityclean.com",
  "reason": "Critical production database corruption requires manual repair",
  "duration_hours": 4,
  "status": "pending"
}
```

**Approval Recorded**:
```json
{
  "event_type": "break_glass_approval",
  "timestamp": "2024-11-01T14:30:00Z",
  "request_id": "bg-2024-11-01-001",
  "approver": "manager1@rivercityclean.com",
  "approval_number": 1
}
```

**Access Granted**:
```json
{
  "event_type": "break_glass_granted",
  "timestamp": "2024-11-01T14:35:00Z",
  "request_id": "bg-2024-11-01-001",
  "user": "devops@rivercityclean.com",
  "approvers": ["manager1@rivercityclean.com", "manager2@rivercityclean.com"],
  "expires_at": "2024-11-01T18:35:00Z"
}
```

**Access Used**:
```json
{
  "event_type": "break_glass_access",
  "timestamp": "2024-11-01T14:40:00Z",
  "request_id": "bg-2024-11-01-001",
  "user": "devops@rivercityclean.com",
  "action": "POST /admin/emergency-repair",
  "resource": "production_database",
  "ip_address": "10.0.1.50"
}
```

**Access Expired/Revoked**:
```json
{
  "event_type": "break_glass_revoked",
  "timestamp": "2024-11-01T18:35:00Z",
  "request_id": "bg-2024-11-01-001",
  "user": "devops@rivercityclean.com",
  "reason": "TTL expired",
  "revoked_by": "system"
}
```

### Audit Log Location

```bash
# Audit logs are stored in immutable log files
/var/log/access/break_glass_audit.log

# Query audit log
grep "bg-2024-11-01-001" /var/log/access/break_glass_audit.log | jq .
```

---

## Monitoring & Alerting

Break-glass events trigger **immediate alerts**:

### Alert Channels

1. **Slack**: `#security-alerts` channel
2. **PagerDuty**: Security team on-call
3. **Email**: security@rivercityclean.com, cto@rivercityclean.com
4. **SIEM**: Splunk, ELK, or equivalent

### Alert Template

```
🚨 BREAK-GLASS ACCESS GRANTED 🚨

Request ID: bg-2024-11-01-001
User: devops@rivercityclean.com
Approvers: manager1@rivercityclean.com, manager2@rivercityclean.com
Reason: Critical production database corruption requires manual repair
Duration: 4 hours
Expires: 2024-11-01T18:35:00Z

All actions will be audited. Review audit logs:
https://logs.rivercityclean.com/break-glass/bg-2024-11-01-001
```

---

## Security Controls

### Technical Controls

1. **Token Validation**:
   - JWT signature verification
   - Expiration timestamp enforcement
   - Nonce validation (prevent replay)
   - Issuer verification

2. **Approval Validation**:
   - Minimum 2 approvers required
   - Self-approval blocked
   - Approver authority verified
   - Approval timeouts enforced (30 minutes)

3. **Audit Trail**:
   - Immutable log storage
   - Tamper-evident logging
   - Real-time SIEM forwarding
   - Log retention: 7 years (compliance)

### Procedural Controls

1. **Annual Review**: All break-glass procedures reviewed annually
2. **Approval Training**: Approvers trained on criteria and risks
3. **Abuse Investigation**: All break-glass uses reviewed by security team
4. **Access Recertification**: Quarterly review of approver lists

---

## Incident Response

### If Break-Glass is Abused

1. **Immediate Actions**:
   ```bash
   # Revoke access immediately
   python scripts/access/approve_temp_role.py revoke \
       --request-id <ID> \
       --revoker security@rivercityclean.com \
       --reason "Security incident: unauthorized use"

   # Rotate affected credentials
   python scripts/keys/rotate.py --emergency
   ```

2. **Investigation**:
   - Pull all audit logs for the request
   - Interview requester and approvers
   - Analyze actions taken during break-glass window
   - Determine if data was compromised

3. **Remediation**:
   - Reset affected accounts
   - Revoke approver authority if negligence found
   - Update procedures to prevent recurrence
   - Report to compliance/legal if required

---

## Compliance Mapping

Break-glass procedures support:

- **SOC 2**: CC6.7 (Restricts logical access), CC7.3 (Evaluates deficiencies)
- **ISO 27001**: A.9.2 (User access management), A.9.4 (Secret authentication information)
- **NIST CSF**: PR.AC-4 (Access permissions managed), DE.CM-7 (Monitoring for unauthorized activity)

---

## Example Scenarios

### Scenario 1: Database Corruption

**Situation**: Production CRM database has corrupted indexes preventing queries.

**Workflow**:
1. DevOps engineer requests break-glass (4 hours)
2. Engineering Manager + CTO approve
3. Engineer uses OWNER access to rebuild indexes
4. Incident resolved in 2 hours
5. Access auto-revokes after 4 hours
6. Security team reviews actions taken

**Outcome**: ✅ Appropriate use, no policy violations

---

### Scenario 2: Cross-Team Emergency

**Situation**: Sales Manager needs to access infrastructure logs to diagnose customer-impacting issue.

**Workflow**:
1. Sales Manager requests break-glass (2 hours)
2. Sales VP + DevOps Lead approve
3. Manager uses OWNER access to view Ops logs
4. Root cause identified (network issue)
5. Access auto-revokes after 2 hours
6. Follow-up: DevOps provides log access dashboard for future use

**Outcome**: ✅ Appropriate use, led to process improvement

---

### Scenario 3: Inappropriate Request

**Situation**: Developer requests break-glass to test a feature in production.

**Workflow**:
1. Developer requests break-glass
2. Manager reviews reason
3. Request **DENIED** - use staging environment
4. Developer educated on appropriate use

**Outcome**: ✅ Denial prevented policy violation

---

## Frequently Asked Questions

**Q: How long does approval take?**
A: Approvals typically complete in 15-30 minutes during business hours. For after-hours emergencies, approvers are notified via PagerDuty.

**Q: Can I extend break-glass access if my task isn't complete?**
A: No. Submit a new request with updated justification. Previous access will be audited before new access is granted.

**Q: What if both approvers are unavailable?**
A: Contact the security team for emergency approval procedures. A security team member can act as Tier 2 approver.

**Q: Is break-glass access logged?**
A: Yes. Every action taken with break-glass access is logged immutably and reviewed by the security team.

**Q: Can I use break-glass for routine tasks?**
A: No. Break-glass is for emergencies only. Routine cross-team access should use proper role assignment and approval workflows.

---

## Audit & Compliance

### Quarterly Reviews

Security team reviews:
- All break-glass requests (approved and denied)
- Average time to approval
- Reasons for requests (trending analysis)
- Approver training effectiveness

### Annual Certification

All approvers must:
- Complete break-glass training
- Acknowledge policy updates
- Pass scenario-based quiz (80% minimum)

### Audit Evidence

For SOC 2 / ISO 27001 audits:
```bash
# Generate break-glass report
python scripts/access/approve_temp_role.py report \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --output audit_report.pdf
```

---

**End of Break-Glass Procedures**

**For Assistance**: Contact security@rivercityclean.com
**Emergency**: PagerDuty escalation or call CTO directly
