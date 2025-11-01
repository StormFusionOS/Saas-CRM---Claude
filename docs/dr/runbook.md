# Disaster Recovery Runbook

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: Infrastructure & SRE Teams

## Overview

This runbook provides procedures for disaster recovery (DR) scenarios, backup/restore operations, and DR drills.

**Recovery Objectives**:
- **RPO (Recovery Point Objective)**: 5 minutes - Maximum acceptable data loss
- **RTO (Recovery Time Objective)**: 15 minutes - Maximum acceptable downtime

**Components**:
- Postgres databases (CRM, Ops)
- Redis cache
- Application services
- Configuration data

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Backup Procedures](#backup-procedures)
3. [Restore Procedures](#restore-procedures)
4. [DR Scenarios](#dr-scenarios)
5. [DR Drills](#dr-drills)
6. [Roles & Responsibilities](#roles--responsibilities)
7. [Communication Plan](#communication-plan)
8. [Post-Incident](#post-incident)

---

## Quick Reference

### Emergency Contacts

| Role | Contact | Phone | Backup |
|------|---------|-------|--------|
| Incident Commander | oncall@example.com | +1-555-0100 | backup-oncall@example.com |
| Database Lead | dba@example.com | +1-555-0101 | - |
| Infrastructure Lead | infra@example.com | +1-555-0102 | - |
| Engineering Manager | eng-manager@example.com | +1-555-0103 | - |

### Critical Commands

```bash
# Create backup
python scripts/dr/backup_snapshot.py --type full

# Restore from latest backup
python scripts/dr/restore_snapshot.py --latest

# Verify backup
python scripts/dr/backup_snapshot.py --verify <backup_id>

# Run DR drill
python scripts/dr/drill.py --scenario database_failure

# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Status Page

Update status at: `https://status.example.com`

---

## Backup Procedures

### Automated Backups

Backups run automatically:
- **Full backups**: Every 6 hours
- **Incremental backups**: Every 5 minutes (aligns with RPO)
- **Retention**: 30 days

Cron schedule:
```cron
# Full backup every 6 hours
0 */6 * * * /path/to/scripts/dr/backup_snapshot.py --type full

# Incremental backup every 5 minutes
*/5 * * * * /path/to/scripts/dr/backup_snapshot.py --type incremental

# Cleanup old backups daily
0 2 * * * /path/to/scripts/dr/backup_snapshot.py --cleanup
```

### Manual Backup

**When to use**: Before major deployments, schema changes, or maintenance

```bash
# 1. Create full backup
python scripts/dr/backup_snapshot.py --type full --retention-days 90

# 2. Verify backup
python scripts/dr/backup_snapshot.py --list
python scripts/dr/backup_snapshot.py --verify <backup_id>

# 3. Document backup
# Record backup ID and purpose in incident log
```

### Backup Verification

**Run weekly** to ensure backup integrity:

```bash
# List all backups
python scripts/dr/backup_snapshot.py --list

# Verify latest backup
LATEST=$(ls -t artifacts/backups/ | head -1)
python scripts/dr/backup_snapshot.py --verify $LATEST

# Check backup size and age
du -sh artifacts/backups/*
ls -lht artifacts/backups/
```

---

## Restore Procedures

### Pre-Restore Checklist

Before restoring:
1. ☐ Identify root cause of failure
2. ☐ Confirm restore is necessary (not just restart)
3. ☐ Get approval from Incident Commander
4. ☐ Notify stakeholders (see Communication Plan)
5. ☐ Verify backup integrity
6. ☐ Take snapshot of current state (if possible)

### Full Restore from Latest Backup

**Timeline**: ~10-15 minutes (within RTO)

```bash
# 1. Stop services (prevent writes)
systemctl stop crm-api
systemctl stop ops-api
systemctl stop redis

# 2. Verify backup
python scripts/dr/restore_snapshot.py --latest --dry-run

# 3. Restore databases
python scripts/dr/restore_snapshot.py --latest

# 4. Verify restore
python scripts/dr/restore_snapshot.py --latest --database postgres_crm_db
curl http://localhost:5432  # Check Postgres
redis-cli ping              # Check Redis

# 5. Start services
systemctl start redis
systemctl start crm-api
systemctl start ops-api

# 6. Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health

# 7. Verify data
# Check recent records exist
# Verify user logins work
# Test critical workflows
```

### Partial Restore (Single Database)

If only one database is affected:

```bash
# Restore CRM database only
python scripts/dr/restore_snapshot.py --latest --database postgres_crm_db

# Restore Ops database only
python scripts/dr/restore_snapshot.py --latest --database postgres_ops_db

# Restore Redis only
python scripts/dr/restore_snapshot.py --latest --database redis
```

### Point-in-Time Recovery (PITR)

**Note**: Requires WAL archiving (not yet implemented in stub)

```bash
# Restore to specific timestamp
python scripts/dr/restore_snapshot.py --pitr "2025-11-01 12:00:00"
```

---

## DR Scenarios

### Scenario 1: Database Corruption

**Symptoms**:
- Query errors
- Data inconsistency
- Application errors

**Response**:
1. **Detect** (0-2 min): Alerts fire, oncall notified
2. **Assess** (2-5 min): DBA investigates scope
3. **Decide** (5-7 min): Determine restore needed
4. **Restore** (7-15 min): Execute restore procedure
5. **Verify** (15-20 min): Health checks, data validation

**Commands**:
```bash
# Assess damage
psql -c "SELECT pg_size_pretty(pg_database_size('crm_db'));"
psql crm_db -c "SELECT COUNT(*) FROM customers;"

# Restore
python scripts/dr/restore_snapshot.py --latest --database postgres_crm_db

# Verify
psql crm_db -c "SELECT COUNT(*) FROM customers;"
```

**Success Criteria**:
- ✓ Database queryable
- ✓ Record counts match expected
- ✓ Application health checks pass
- ✓ Users can log in

### Scenario 2: Complete Data Center Outage

**Symptoms**:
- All services unreachable
- Network connectivity lost
- Hardware failure

**Response**:
1. **Detect** (0-1 min): Monitoring alerts
2. **Failover** (1-5 min): Switch to backup datacenter
3. **Restore** (5-15 min): Restore from latest backup
4. **Verify** (15-20 min): Full system test

**Commands**:
```bash
# Failover to backup datacenter
terraform apply -target=aws_route53_record.failover

# Restore all services
python scripts/dr/restore_snapshot.py --latest

# Health checks
./scripts/health_check_all.sh
```

**Success Criteria**:
- ✓ All services responding
- ✓ DNS failover complete
- ✓ Data loss < 5 minutes (RPO)
- ✓ Total downtime < 15 minutes (RTO)

### Scenario 3: Ransomware Attack

**Symptoms**:
- Encrypted files
- Ransom note
- Data inaccessible

**Response**:
1. **Isolate** (0-2 min): Disconnect affected systems
2. **Assess** (2-10 min): Determine scope, identify clean backup
3. **Wipe** (10-15 min): Clean slate all affected systems
4. **Restore** (15-25 min): Restore from pre-infection backup
5. **Harden** (25-60 min): Update security, patch vulnerabilities

**Commands**:
```bash
# Identify clean backup (before infection)
python scripts/dr/backup_snapshot.py --list

# Restore from clean backup
python scripts/dr/restore_snapshot.py --backup-id full_20251101_060000

# Verify no infection
clamscan -r /var/lib/postgresql/data
```

**Success Criteria**:
- ✓ All malware removed
- ✓ Data restored from clean backup
- ✓ Security hardening complete
- ✓ No reinfection after 48 hours

### Scenario 4: Accidental Data Deletion

**Symptoms**:
- User reports missing data
- DELETE query ran incorrectly
- Bulk data loss

**Response**:
1. **Stop** (0-1 min): Prevent further damage
2. **Identify** (1-5 min): Find last good backup
3. **Restore** (5-10 min): Restore specific data
4. **Merge** (10-15 min): Merge restored data with current

**Commands**:
```bash
# Export deleted data from backup
python scripts/dr/restore_snapshot.py --latest --database postgres_crm_db

# Extract specific records (manual SQL)
psql backup_crm_db -c "COPY (SELECT * FROM customers WHERE deleted_at > '2025-11-01') TO '/tmp/deleted_customers.csv' CSV HEADER;"

# Import into production
psql crm_db -c "COPY customers FROM '/tmp/deleted_customers.csv' CSV HEADER;"
```

---

## DR Drills

### Monthly DR Drill Schedule

| Month | Scenario | Lead | Duration |
|-------|----------|------|----------|
| Jan | Database corruption | DBA | 30 min |
| Feb | Complete outage | Infra | 45 min |
| Mar | Partial failure | SRE | 30 min |
| Apr | Ransomware | Security | 60 min |
| May | Network failure | NetOps | 30 min |
| Jun | Full failover | All | 90 min |

### Running a DR Drill

**Automated Drill**:
```bash
# Run database failure drill
python scripts/dr/drill.py --scenario database_failure

# Run complete outage drill
python scripts/dr/drill.py --scenario complete_outage

# Run with chaos injection
python scripts/dr/drill.py --scenario database_failure --chaos
```

**Manual Drill Procedure**:

1. **Pre-Drill** (15 min before):
   - Notify all participants
   - Confirm backup exists
   - Set up war room/Zoom

2. **Drill Start** (T+0):
   - Announce scenario
   - Start timer
   - Begin incident response

3. **Execute** (T+0 to T+15):
   - Follow runbook procedures
   - Document actions taken
   - Track time for each step

4. **Verify** (T+15 to T+20):
   - Health checks
   - Data validation
   - User acceptance testing

5. **Debrief** (T+20 to T+40):
   - What went well
   - What went poorly
   - Action items
   - Update runbook

**Drill Success Criteria**:
- ✓ Restore completed within RTO (15 min)
- ✓ Data loss within RPO (5 min)
- ✓ All health checks pass
- ✓ Team followed procedures
- ✓ Communication effective

### Drill Metrics

Track these metrics for each drill:
- Time to detection
- Time to decision
- Time to restore
- Total downtime
- Data loss amount
- Success rate

**Target**:
- 95% of drills complete within RTO
- 100% of drills pass health checks

---

## Roles & Responsibilities

### Incident Commander (IC)

**Responsibilities**:
- Declare incident
- Coordinate response
- Make restore/no-restore decision
- Manage communications
- Call for help/escalate

**Authority**:
- Can override normal procedures
- Can requisition resources
- Final decision on restore

### Database Lead

**Responsibilities**:
- Assess database health
- Execute backup/restore
- Verify data integrity
- Provide time estimates

**On-call rotation**: DBA team

### Infrastructure Lead

**Responsibilities**:
- Assess infrastructure
- Manage failover
- Monitor system resources
- Execute service restarts

**On-call rotation**: SRE team

### Communications Lead

**Responsibilities**:
- Update status page
- Notify stakeholders
- Post incident updates
- Coordinate with support

**Contact**: comms@example.com

---

## Communication Plan

### Internal Communications

**Slack Channels**:
- `#incidents` - Primary incident channel
- `#on-call` - Oncall coordination
- `#engineering` - Engineering updates

**Update Frequency**:
- Every 5 minutes during active incident
- Every 15 minutes during restore
- Every 30 minutes post-restore

**Template**:
```
[HH:MM] UPDATE:
Status: [INVESTIGATING | RESTORING | RESOLVED]
Impact: [Description]
ETA: [Time estimate]
Next update: [Time]
```

### External Communications

**Status Page**: https://status.example.com

**Update Template**:
```
We are currently experiencing [ISSUE].

Impact: [Service/feature affected]
Status: [Investigating/Fixing/Monitoring]
ETA: [Estimated resolution time]

Last update: [Timestamp]
```

**Customer Support**:
- Email: support@example.com
- Phone: +1-555-0199
- Provide talking points
- Update every 15 minutes

### Escalation Path

1. **Level 1**: Oncall engineer (0-5 min)
2. **Level 2**: Team lead (5-10 min)
3. **Level 3**: Engineering manager (10-15 min)
4. **Level 4**: CTO (15+ min or customer-facing)

---

## Post-Incident

### Immediate Actions (within 1 hour)

```bash
# 1. Verify all systems healthy
./scripts/health_check_all.sh

# 2. Check for data loss
# Compare record counts pre/post incident

# 3. Monitor for 1 hour
# Watch error rates, latency, user complaints

# 4. Update status page
# Mark as RESOLVED with summary

# 5. Initial timeline
# Document what happened, when, and actions taken
```

### Post-Incident Review (within 48 hours)

**Participants**:
- Incident Commander
- All responders
- Team leads
- Product manager (if customer impact)

**Agenda**:
1. Timeline review
2. What went well
3. What went poorly
4. Action items (with owners and due dates)
5. Runbook updates
6. Prevention strategies

**Deliverable**: Post-incident report

**Template**: `docs/incidents/YYYY-MM-DD-incident.md`

### Metrics to Track

| Metric | Target | Actual |
|--------|--------|--------|
| Time to detect | < 2 min | |
| Time to engage | < 5 min | |
| Time to restore | < 15 min (RTO) | |
| Data loss | < 5 min (RPO) | |
| Customer impact | < 1000 users | |

### Follow-Up Actions

- [ ] Create action items in Jira
- [ ] Update runbook with lessons learned
- [ ] Schedule follow-up drills
- [ ] Share learnings with team
- [ ] Update monitoring/alerting

---

## Appendices

### A. Backup Manifest Example

```json
{
  "backup_id": "full_20251101_120000",
  "backup_type": "full",
  "timestamp": "2025-11-01T12:00:00Z",
  "databases": {
    "postgres_crm_db": {
      "path": "artifacts/backups/full_20251101_120000/crm_db.sql.gz",
      "size_bytes": 1048576,
      "hash": "abc123...",
      "compression": "gzip"
    },
    "redis": {
      "path": "artifacts/backups/full_20251101_120000/redis.rdb.gz",
      "size_bytes": 524288,
      "hash": "def456...",
      "compression": "gzip"
    }
  },
  "total_size_bytes": 1572864,
  "retention_until": "2025-12-01T12:00:00Z",
  "rpo_minutes": 5,
  "rto_minutes": 15
}
```

### B. Health Check Endpoints

```bash
# CRM API
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "ok", "redis": "ok"}

# Ops API
curl http://localhost:8001/health
# Expected: {"status": "healthy", "database": "ok"}

# Postgres
pg_isready -h localhost -p 5432
# Expected: localhost:5432 - accepting connections

# Redis
redis-cli ping
# Expected: PONG
```

### C. Useful Commands

```bash
# Check disk space
df -h

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('crm_db'));"

# Check active connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis memory
redis-cli info memory

# Check service status
systemctl status crm-api
systemctl status ops-api

# Check logs
tail -f logs/crm_api.log
tail -f logs/ops_api.log
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-01 | 1.0 | Initial runbook created |

---

## Related Documents

- [Backup Scripts](../../scripts/dr/README.md)
- [SLO Definitions](../reliability/slos.md)
- [Incident Response Plan](../incidents/response.md)
- [On-Call Runbook](../oncall/runbook.md)
