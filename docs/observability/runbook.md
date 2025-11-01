# Observability Runbook

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: Platform Engineering & Security Teams

## Overview

This runbook provides operational procedures for observability, monitoring, and incident response for RiverCityClean services.

**Components**:
- Structured logging (JSON Lines with ECS schema)
- Metrics (Prometheus-style exposition)
- Distributed tracing (W3C traceparent)
- SIEM export and detection
- Alerting and incident response

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Logs](#logs)
3. [Metrics](#metrics)
4. [Tracing](#tracing)
5. [Detections](#detections)
6. [Dashboards](#dashboards)
7. [Triage SOPs](#triage-sops)
8. [Common Issues](#common-issues)

---

## Quick Start

### Running the Trace Demo

Demonstrates distributed tracing across services:

```bash
# Run trace demo
python scripts/observability/trace_demo.py

# Output: Multiple trace scenarios with console logging
# Logs saved to: logs/crm_api.jsonl, logs/ops_api.jsonl
```

### Scraping Metrics

Collect Prometheus metrics snapshots:

```bash
# Scrape all services (requires running services)
python scripts/observability/scrape_metrics.py

# Scrape specific service
python scripts/observability/scrape_metrics.py --service crm_api

# Continuous scraping every 60 seconds
python scripts/observability/scrape_metrics.py --continuous --interval 60

# List saved snapshots
python scripts/observability/scrape_metrics.py --list
```

**Output**: `artifacts/metrics/<service>/<timestamp>.txt` and `.json`

### Running Detections

Execute security detections on logs:

```bash
# Generate sample malicious logs
python scripts/observability/detect.py --generate-sample

# Run detections on sample logs
python scripts/observability/detect.py --log logs/sample_malicious.jsonl

# Test detection rules
python scripts/observability/detect.py --test

# Run specific detection
python scripts/observability/detect.py --log logs/crm_api.jsonl --rule detections/brute_force.yaml
```

**Expected Output**:
```
🚨 ALERT: Brute Force Authentication Attack - 8 events from ('203.0.113.100',)
🚨 ALERT: Excessive 403 Forbidden Responses - 15 events from ('198.51.100.50',)
```

---

## Logs

### Log Locations

| Service | Log File | Format |
|---------|----------|--------|
| CRM API | `logs/crm_api.jsonl` | JSON Lines |
| Ops API | `logs/ops_api.jsonl` | JSON Lines |
| Celery | `logs/celery.jsonl` | JSON Lines |
| Nginx | `logs/nginx.jsonl` | JSON Lines (if configured) |

### Viewing Logs

**Real-time tail**:
```bash
tail -f logs/crm_api.jsonl | jq '.'
```

**Pretty print**:
```bash
cat logs/crm_api.jsonl | jq -C '.' | less -R
```

**Filter by level**:
```bash
jq 'select(.log.level == "ERROR")' logs/crm_api.jsonl
```

**Filter by user**:
```bash
jq 'select(.user.id == "user_12345")' logs/crm_api.jsonl
```

**Trace specific request**:
```bash
TRACE_ID="4bf92f3577b34da6a3ce929d0e0e4736"
jq --arg tid "$TRACE_ID" 'select(.trace.id == $tid)' logs/*.jsonl
```

### Log Export for SIEM

Export logs to timestamped gzip archives:

```bash
# Export all logs
python scripts/observability/export_logs.py

# Export last 24 hours
python scripts/observability/export_logs.py --hours 24

# Continuous export every hour
python scripts/observability/export_logs.py --watch --interval 3600

# List exports
python scripts/observability/export_logs.py --list
```

**Output**: `artifacts/logs/<service>/<timestamp>.jsonl.gz`

### PII Redaction

All logs automatically redact PII:

- **Email**: `user@example.com` → `[EMAIL_REDACTED]`
- **IP**: `192.168.1.1` → `[IP_REDACTED]`
- **Tokens**: `Bearer abc123...` → `Bearer [TOKEN_REDACTED]`
- **Sensitive fields**: `password`, `secret`, `api_key` → `[REDACTED]`

See `logs/schema.md` for complete PII redaction rules.

---

## Metrics

### Metrics Endpoints

| Service | Endpoint | Port |
|---------|----------|------|
| CRM API | `http://localhost:8000/metrics` | 8000 |
| Ops API | `http://localhost:8001/metrics` | 8001 |

### Available Metrics

**HTTP Metrics**:
- `http_requests_total{method, path, status}` - Counter
- `http_request_duration_ms{method, path}` - Histogram
- `http_request_bytes{method, path}` - Histogram
- `http_response_bytes{method, path}` - Histogram
- `http_requests_in_progress{method, path}` - Gauge

**Task Queue Metrics**:
- `task_queue_length{queue}` - Gauge
- `task_processing_duration_ms{queue, task_type}` - Histogram
- `task_total{queue, task_type, status}` - Counter
- `task_retries_total{queue, task_type}` - Counter

**Database Metrics**:
- `db_connections_total{database}` - Gauge
- `db_query_duration_ms{database, operation}` - Histogram

### Manual Metrics Check

```bash
curl http://localhost:8000/metrics
```

### Key Queries

**Request rate (5m avg)**:
```promql
rate(http_requests_total[5m])
```

**P95 latency**:
```promql
histogram_quantile(0.95, http_request_duration_ms_bucket)
```

**Error rate**:
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

**Task queue depth**:
```promql
task_queue_length{queue="celery"}
```

---

## Tracing

### W3C Trace Context

All requests include W3C traceparent header:

```
traceparent: 00-{trace-id}-{parent-id}-{trace-flags}
Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

### Trace Propagation

1. **Frontend → API**: Frontend includes `traceparent` header
2. **API → Task**: Task receives trace context
3. **Task → Downstream**: Downstream API continues trace

### Finding Related Logs

All logs with the same `trace.id` belong to the same request:

```bash
TRACE_ID="4bf92f3577b34da6a3ce929d0e0e4736"

# Find all logs for this trace
grep "$TRACE_ID" logs/*.jsonl | jq '.'

# Or with jq
jq --arg tid "$TRACE_ID" 'select(.trace.id == $tid)' logs/*.jsonl
```

### Trace Analysis

```bash
# Extract trace timeline
jq -r --arg tid "$TRACE_ID" '
  select(.trace.id == $tid) |
  [.["@timestamp"], .service.name, .span.id, .message] |
  @tsv
' logs/*.jsonl | sort
```

---

## Detections

### Available Detection Rules

| Rule ID | Name | Severity | Description |
|---------|------|----------|-------------|
| `brute_force` | Brute Force Auth | High | 5+ failed logins in 5 min |
| `impossible_travel` | Impossible Travel | Critical | Login from distant locations |
| `excessive_403` | Excessive 403s | Medium | 10+ 403s in 10 min |

### Running Detections

**All detections**:
```bash
python scripts/observability/detect.py --log logs/crm_api.jsonl
```

**Specific detection**:
```bash
python scripts/observability/detect.py \
  --log logs/crm_api.jsonl \
  --rule detections/brute_force.yaml
```

**Test detections**:
```bash
python scripts/observability/detect.py --test
```

### Alert Response

When detections trigger alerts:

1. **Review alert details**: Check count, group_by, matching logs
2. **Investigate logs**: Review sample logs in alert
3. **Correlate with metrics**: Check for traffic spikes
4. **Follow triage SOP**: See [Triage SOPs](#triage-sops) below
5. **Document findings**: Create incident ticket
6. **Implement response**: Block IP, require MFA, etc.

---

## Dashboards

While this implementation uses file-based exports, here are recommended dashboards for SIEM/monitoring systems:

### 1. Service Health Dashboard

**Metrics**:
- Request rate (RPM)
- Error rate (%)
- P50/P95/P99 latency
- Requests in progress

**Queries**:
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_ms_bucket[5m]))
```

### 2. Security Dashboard

**Log Queries** (jq):
```bash
# Failed logins (last hour)
jq 'select(.event.action == "auth.login.failure")' logs/crm_api.jsonl | wc -l

# 403 responses
jq 'select(.http.response.status_code == 403)' logs/*.jsonl

# By IP
jq -r '.client.ip' logs/crm_api.jsonl | sort | uniq -c | sort -rn
```

### 3. Task Queue Dashboard

**Metrics**:
- Queue depth
- Processing rate
- Task duration
- Retry count

**Queries**:
```promql
task_queue_length{queue="celery"}
rate(task_total[5m])
histogram_quantile(0.95, task_processing_duration_ms_bucket)
```

### 4. User Activity Dashboard

**Log Queries**:
```bash
# Active users (last hour)
jq -r 'select(.user.id) | .user.id' logs/crm_api.jsonl | sort -u | wc -l

# Top users by activity
jq -r '.user.id' logs/crm_api.jsonl | sort | uniq -c | sort -rn | head -10
```

---

## Triage SOPs

### SOP 1: Brute Force Attack

**Alert**: `brute_force` detection triggered

**Steps**:
1. **Identify source**:
   ```bash
   jq '.client.ip' logs/crm_api.jsonl | sort | uniq -c | sort -rn
   ```

2. **Review attempts**:
   ```bash
   IP="203.0.113.100"
   jq --arg ip "$IP" 'select(.client.ip == $ip and .event.action == "auth.login.failure")' logs/crm_api.jsonl
   ```

3. **Check for success**:
   ```bash
   jq --arg ip "$IP" 'select(.client.ip == $ip and .event.action == "auth.login.success")' logs/crm_api.jsonl
   ```

4. **Response actions**:
   - Block IP at firewall/WAF
   - Alert user if account compromised
   - Require password reset
   - Enable MFA if not already

5. **Document**:
   - Create security incident ticket
   - Update threat intelligence
   - Review detection rule effectiveness

### SOP 2: Impossible Travel

**Alert**: `impossible_travel` detection triggered

**Steps**:
1. **Review locations**:
   ```bash
   USER_ID="user_12345"
   jq --arg uid "$USER_ID" 'select(.user.id == $uid and .event.action == "auth.login.success") | {timestamp: .["@timestamp"], ip: .client.ip, location: .client.geo.city}' logs/crm_api.jsonl
   ```

2. **Check session history**:
   - Review all sessions for user
   - Look for anomalies (OS, browser changes)

3. **User contact**:
   - Contact user via secure channel
   - Verify recent logins
   - Ask about shared credentials

4. **Response actions**:
   - Revoke all sessions
   - Require password reset
   - Enable MFA mandatory
   - Review account for unauthorized changes

5. **Investigation**:
   - Check for credential exposure (haveibeenpwned.com)
   - Review audit logs for account
   - Look for lateral movement

### SOP 3: Excessive 403s

**Alert**: `excessive_403` detection triggered

**Steps**:
1. **Identify source and paths**:
   ```bash
   jq 'select(.http.response.status_code == 403) | {ip: .client.ip, path: .http.request.path, user: .user.id}' logs/crm_api.jsonl
   ```

2. **Check pattern**:
   - Sequential path enumeration?
   - Admin endpoint scanning?
   - Legitimate user permission issue?

3. **Correlate with other activity**:
   - Check for 401s (authentication)
   - Check for successful requests before/after
   - Review user's normal behavior

4. **Response actions**:
   - **If malicious**: Block IP, alert security team
   - **If user error**: Update permissions, notify user
   - **If scanner**: Add to WAF rules

5. **Prevention**:
   - Update access control policies
   - Review RBAC assignments
   - Improve error messages (don't leak info)

### SOP 4: Service Degradation

**Symptoms**: High latency, error rate, or queue depth

**Steps**:
1. **Check metrics**:
   ```bash
   curl http://localhost:8000/metrics | grep -E "(http_request_duration|task_queue_length)"
   ```

2. **Review error logs**:
   ```bash
   jq 'select(.log.level == "ERROR")' logs/crm_api.jsonl | tail -20
   ```

3. **Check dependencies**:
   - Database connections
   - Redis availability
   - External API status

4. **Identify root cause**:
   - Trace slowest requests
   - Check database query performance
   - Review recent deployments

5. **Response actions**:
   - Scale resources if needed
   - Optimize slow queries
   - Enable circuit breakers
   - Rollback if caused by deployment

---

## Common Issues

### Issue: Logs Not Appearing

**Symptoms**: No logs in `logs/*.jsonl`

**Checks**:
1. Service running?
   ```bash
   ps aux | grep -E "(crm_api|ops_api)"
   ```

2. Log directory exists?
   ```bash
   ls -la logs/
   ```

3. Permissions correct?
   ```bash
   ls -la logs/*.jsonl
   ```

**Solution**:
- Ensure services are running
- Create `logs/` directory if missing
- Check file write permissions

### Issue: Metrics Endpoint Returns 404

**Symptoms**: `curl http://localhost:8000/metrics` returns 404

**Checks**:
1. Service running on correct port?
   ```bash
   netstat -tuln | grep 8000
   ```

2. Metrics module imported?
   - Check `observability/metrics.py` is loaded

**Solution**:
- Restart service
- Verify metrics endpoint is registered in API routes

### Issue: Trace IDs Not Propagating

**Symptoms**: Different `trace.id` across services

**Checks**:
1. Review trace demo output
2. Check for `traceparent` header in requests

**Solution**:
- Ensure all services use `observability.tracing` module
- Verify headers propagation in HTTP calls

### Issue: Detection Not Triggering

**Symptoms**: Expected alerts not appearing

**Checks**:
1. Test detection rules:
   ```bash
   python scripts/observability/detect.py --test
   ```

2. Review threshold in YAML:
   - Check `threshold.count`
   - Check `timeframe`

3. Verify log format matches conditions

**Solution**:
- Adjust detection rule parameters
- Generate sample logs to test
- Review exclude conditions

---

## Compliance Mapping

| Framework | Control | Implementation |
|-----------|---------|----------------|
| SOC 2 CC6.8 | Logging & Monitoring | Structured logs, SIEM export |
| SOC 2 CC7.2 | Anomaly Detection | Detection rules, alerting |
| ISO 27001 A.12.4.1 | Event Logging | JSON Lines logs with PII redaction |
| ISO 27001 A.12.4.3 | Admin Logs | User actions logged with trace IDs |
| NIST CSF DE.AE-3 | Correlation | Distributed tracing, detection engine |
| NIST CSF RS.AN-1 | Incident Analysis | Triage SOPs, runbooks |

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-01 | 1.0 | Initial runbook |

