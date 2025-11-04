# AI Governance System - Implementation Guide

**Status:** ✅ Implemented
**Date:** 2025-11-03
**Version:** 1.0.0

---

## Overview

The AI Governance System provides the critical safety layer for all AI automation features. It ensures that **no AI-generated changes reach production without human approval** through a review queue workflow.

## Core Components

### 1. change_log Table
**Purpose:** Review queue for all AI-generated suggestions

**State Machine:**
```
pending → (human reviews) → approved/rejected
approved → executing → executed
approved → executing → failed → reverted
```

**Key Fields:**
- `module`: Which AI tool generated this (e.g., 'ctr_optimizer')
- `action`: What to do (e.g., 'update_meta_title')
- `target`: What to change (e.g., 'page:123')
- `proposed_value`: The AI's suggestion
- `current_value`: What it is now
- `diff_preview`: Visual diff for review
- `status`: Current workflow state
- `reviewed_by`, `executed_by`: Audit trail

### 2. task_logs Table
**Purpose:** Audit trail of all AI job executions

**Records:**
- Every SERP scrape, anomaly detection, CTR optimization, etc.
- Job start time, duration, status
- Records processed, changes generated, errors
- Full input/output tracking

### 3. audit_issues Table
**Purpose:** System health and compliance issues

**Tracks:**
- Job failures (e.g., "SERP crawler failed 3 times")
- SLA violations (e.g., "Change pending >72 hours")
- Security issues
- Compliance problems

---

## API Endpoints

### change_log Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/change-log` | POST | Create AI suggestion |
| `/api/v1/change-log` | GET | List review queue (filter by status) |
| `/api/v1/change-log/{id}` | GET | Get single entry |
| `/api/v1/change-log/{id}/review` | PUT | Approve/reject |
| `/api/v1/change-log/{id}/execute` | POST | Deploy approved change |
| `/api/v1/change-log/{id}/revert` | POST | Rollback executed change |

### task_logs Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/task-logs` | POST | Start job logging |
| `/api/v1/task-logs/{id}` | PUT | Update job status/metrics |
| `/api/v1/task-logs` | GET | List job history |
| `/api/v1/task-logs/{id}` | GET | Get job details |

### audit_issues Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/audit-issues` | POST | Create issue |
| `/api/v1/audit-issues` | GET | List issues |
| `/api/v1/audit-issues/{id}` | GET | Get issue |
| `/api/v1/audit-issues/{id}` | PUT | Resolve/acknowledge |

### Dashboard Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/governance/summary` | GET | Dashboard metrics |

---

## Usage Examples

### Example 1: AI Module Creates Suggestion

```python
# CTR Optimizer detects low CTR and suggests new meta title
import requests

response = requests.post("http://localhost:8000/api/v1/change-log", json={
    "module": "ctr_optimizer",
    "action": "update_meta_title",
    "target": "page:456",
    "current_value": "Old Title - Our Company",
    "proposed_value": "5 Ways to Boost Revenue | Our Company 2025",
    "diff_preview": "- Old Title - Our Company\\n+ 5 Ways to Boost Revenue | Our Company 2025",
    "severity": "medium",
    "confidence_score": 0.87,
    "generated_by": "ctr_optimization_job_2025-11-03",
    "metadata": {
        "current_ctr": 0.012,
        "predicted_ctr": 0.034,
        "improvement": "183%",
        "rank": 3,
        "keyword": "boost revenue"
    }
}, headers={"Authorization": "Bearer YOUR_TOKEN"})

# Returns: {"id": 42, "status": "pending", ...}
```

### Example 2: Human Reviews and Approves

```python
# View pending changes
pending = requests.get(
    "http://localhost:8000/api/v1/change-log?status=pending",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
).json()

# Review change #42
approve = requests.put(
    "http://localhost:8000/api/v1/change-log/42/review",
    json={
        "status": "approved",
        "decision_reason": "Good improvement, aligns with brand voice"
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Example 3: Execute Approved Change

```python
# Execute approved change
execute = requests.post(
    "http://localhost:8000/api/v1/change-log/42/execute",
    json={"execution_notes": "Deployed via WordPress API"},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Returns: {"id": 42, "status": "executed", "executed_at": "2025-11-03T15:30:00Z", ...}
```

### Example 4: Job Execution Logging

```python
# AI job starts
task = requests.post("http://localhost:8000/api/v1/task-logs", json={
    "job_name": "serp_position_scraper",
    "job_id": "celery-task-abc123",
    "inputs": {"keywords": ["boost revenue", "increase sales"], "domain": "example.com"},
    "triggered_by": "scheduler",
    "environment": "prod"
}, headers={"Authorization": "Bearer YOUR_TOKEN"}).json()

task_id = task["id"]

# ... job runs ...

# Update with results
requests.put(f"http://localhost:8000/api/v1/task-logs/{task_id}", json={
    "status": "completed",
    "records_processed": 150,
    "changes_generated": 3,
    "errors_count": 0,
    "outputs": {
        "keywords_tracked": 150,
        "rank_changes": [
            {"keyword": "boost revenue", "old_rank": 5, "new_rank": 3}
        ]
    }
}, headers={"Authorization": "Bearer YOUR_TOKEN"})
```

### Example 5: Create Audit Issue

```python
# Health monitor detects job failure
issue = requests.post("http://localhost:8000/api/v1/audit-issues", json={
    "issue_type": "job_failure",
    "severity": "error",
    "title": "SERP Crawler Failed 3 Consecutive Times",
    "description": "serp_position_scraper job has failed 3 times in a row with timeout errors. Last successful run was 6 hours ago.",
    "affected_resource": "serp_position_scraper",
    "detected_by": "health_monitor",
    "metadata": {
        "last_success": "2025-11-03T09:00:00Z",
        "failure_count": 3,
        "error": "Request timeout after 30s"
    },
    "resolve_sla_hours": 4
}, headers={"Authorization": "Bearer YOUR_TOKEN"})
```

---

## Review Mode vs Auto Mode

### Review Mode (Default)
- **ALL** AI suggestions go to `change_log` with `status='pending'`
- Human must approve before execution
- Safe for testing and initial rollout

### Auto Mode (Graduated)
- Low-risk suggestions can auto-approve and execute
- Still logged in `change_log` for audit
- Only after module proves reliable in review mode
- Configured per-module (Step 03 implementation)

**Important:** Start ALL modules in review mode. Graduate to auto per Step 16 criteria.

---

## Dashboard Integration

The governance summary endpoint provides real-time metrics:

```python
summary = requests.get(
    "http://localhost:8000/api/v1/governance/summary",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
).json()

# Returns:
{
  "change_log": {
    "pending": 5,
    "approved": 2,
    "executed": 47,
    "failed": 1,
    "recent_24h": 12
  },
  "task_logs": {
    "running": 1,
    "failed": 0,
    "recent_24h": 8
  },
  "audit_issues": {
    "open": 2,
    "critical": 0
  },
  "health_status": "healthy"
}
```

Use this for:
- Review Queue badge counts
- System health indicators
- AI automation metrics

---

## Files Created

| File | Purpose |
|------|---------|
| `crm_api/app/models/governance.py` | Pydantic models for all 3 tables |
| `crm_api/app/api/routes/governance.py` | 20+ API endpoints |
| `crm_api/app/main.py` | Router registration (line 117-119) |

---

## Next Steps

1. ✅ Governance tables created (this step)
2. ⏭️ Create `module_config` table for review/auto toggle (Step 03)
3. ⏭️ Migrate to PostgreSQL (current: in-memory)
4. ⏭️ Build Review Queue UI in dashboard (Step 06)
5. ⏭️ Integrate AI modules to use change_log (Steps 07-12)

---

## Security Considerations

### Authentication
- All endpoints require `require_sales_claims` auth
- JWT tokens with user_id for audit trail

### Authorization
- Execution requires human approval
- Rollback requires special permissions (admin)
- Audit trail tracks all actions

### Data Retention
- `change_log`: Keep 1 year for compliance
- `task_logs`: Keep 90 days for troubleshooting
- `audit_issues`: Keep indefinitely (compliance)

---

## Testing

### Manual Testing

```bash
# 1. Create a test suggestion
curl -X POST http://localhost:8000/api/v1/change-log \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "module": "test_module",
    "action": "update_meta_title",
    "target": "page:1",
    "proposed_value": "New Title"
  }'

# 2. List pending
curl http://localhost:8000/api/v1/change-log?status=pending \
  -H "Authorization: Bearer $TOKEN"

# 3. Approve
curl -X PUT http://localhost:8000/api/v1/change-log/1/review \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "decision_reason": "Looks good"}'

# 4. Execute
curl -X POST http://localhost:8000/api/v1/change-log/1/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Troubleshooting

### Issue: Changes stuck in "pending"
**Solution:** Check `/api/v1/change-log?status=pending` and review manually

### Issue: Jobs not logging
**Solution:** Ensure jobs call `/api/v1/task-logs` POST at start

### Issue: Dashboard not updating
**Solution:** Check `/api/v1/governance/summary` endpoint

---

**Status:** ✅ COMPLETE - Safe to proceed with AI automation modules
**Next:** Implement Quick Win #2 (review_mode configuration)

---

*Governance system maintained by the RiverCityClean Engineering Team*
*Last updated: 2025-11-03*
