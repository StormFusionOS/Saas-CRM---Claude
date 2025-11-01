# Service Level Objectives (SLOs)

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: SRE Team

## Overview

This document defines Service Level Indicators (SLIs), Service Level Objectives (SLOs), and error budgets for RiverCityClean services.

**Key Concepts**:
- **SLI (Service Level Indicator)**: Quantitative measure of service quality
- **SLO (Service Level Objective)**: Target value for an SLI
- **SLA (Service Level Agreement)**: Contractual commitment (typically SLO - 1%)
- **Error Budget**: Allowed failure rate (100% - SLO)

---

## Service Level Objectives

### Availability SLOs

| Service | SLO | Error Budget | Measurement |
|---------|-----|--------------|-------------|
| CRM API | 99.9% | 0.1% (43.2 min/month) | HTTP 200-299 / all requests |
| Ops Console API | 99.9% | 0.1% (43.2 min/month) | HTTP 200-299 / all requests |
| Database (Postgres) | 99.95% | 0.05% (21.6 min/month) | Successful connections / attempts |
| Cache (Redis) | 99.9% | 0.1% (43.2 min/month) | Successful operations / attempts |

**Measurement Window**: 30 days rolling

**Error Budget Policy**:
- **100-50% budget remaining**: Normal operations, all releases allowed
- **50-10% budget remaining**: Caution mode, feature freeze for risky changes
- **<10% budget remaining**: Emergency mode, only critical fixes
- **0% budget exhausted**: Full freeze until next window

### Latency SLOs

| Service | Endpoint | p50 | p95 | p99 | Budget |
|---------|----------|-----|-----|-----|--------|
| CRM API | GET /api/v1/customers | 50ms | 200ms | 500ms | 95% under 200ms |
| CRM API | POST /api/v1/customers | 100ms | 300ms | 800ms | 95% under 300ms |
| CRM API | GET /api/v1/invoices | 100ms | 400ms | 1000ms | 95% under 400ms |
| Ops API | GET /health | 10ms | 50ms | 100ms | 99% under 50ms |
| Ops API | GET /api/v1/metrics | 200ms | 1000ms | 2000ms | 90% under 1000ms |

**Measurement**: Response time from request received to response sent

**Percentile Definitions**:
- **p50 (median)**: 50% of requests faster than this
- **p95**: 95% of requests faster than this
- **p99**: 99% of requests faster than this

### Throughput SLOs

| Service | SLO | Measurement |
|---------|-----|-------------|
| CRM API | ≥ 100 req/s | Requests processed per second |
| Ops API | ≥ 50 req/s | Requests processed per second |
| Database | ≥ 500 queries/s | Queries executed per second |

### Data Durability SLOs

| Component | SLO | RPO | RTO |
|-----------|-----|-----|-----|
| Customer Data | 99.999999% (8 nines) | 5 min | 15 min |
| Operational Data | 99.99% (4 nines) | 5 min | 15 min |
| Cache Data | 99.9% (3 nines) | N/A | 5 min |

**RPO (Recovery Point Objective)**: Maximum acceptable data loss
**RTO (Recovery Time Objective)**: Maximum acceptable downtime

---

## Service Level Indicators (SLIs)

### 1. Availability SLI

**Definition**: Percentage of successful requests

**Formula**:
```
Availability = (Successful Requests / Total Requests) × 100%
```

**Success Criteria**:
- HTTP status codes 200-299, 304
- Response received within timeout (30s)
- No server errors (500-599)

**Implementation**:
```python
from observability.metrics import http_requests_total

def calculate_availability():
    total = http_requests_total.get_value()
    successful = http_requests_total.get_value(status="2xx")

    return (successful / total) * 100 if total > 0 else 100
```

### 2. Latency SLI

**Definition**: Request processing time at various percentiles

**Formula**:
```
p95_latency = 95th percentile of request_duration_ms
```

**Measurement Points**:
- Request received (ingress)
- Database query start/end
- External API call start/end
- Response sent (egress)

**Implementation**:
```python
from observability.metrics import http_request_duration_ms

def calculate_p95_latency():
    histogram = http_request_duration_ms.get_histogram()
    return histogram.percentile(95)
```

### 3. Error Rate SLI

**Definition**: Percentage of failed requests

**Formula**:
```
Error Rate = (Failed Requests / Total Requests) × 100%
```

**Error Categories**:
- Client errors (4xx): Not counted against SLO
- Server errors (5xx): Counted against SLO
- Timeouts: Counted against SLO
- Database errors: Counted against SLO

**Implementation**:
```python
def calculate_error_rate():
    total = http_requests_total.get_value()
    errors = http_requests_total.get_value(status="5xx")

    return (errors / total) * 100 if total > 0 else 0
```

### 4. Saturation SLI

**Definition**: Resource utilization percentage

**Metrics**:
- CPU usage < 70% (p95)
- Memory usage < 80% (p95)
- Disk usage < 85%
- Connection pool < 80% utilized

**Implementation**:
```python
from observability.metrics import system_cpu_usage, system_memory_usage

def calculate_saturation():
    cpu = system_cpu_usage.get_value()
    memory = system_memory_usage.get_value()

    return {
        "cpu": cpu,
        "memory": memory,
        "healthy": cpu < 70 and memory < 80
    }
```

---

## SLO Monitoring

### Dashboards

**Grafana Dashboards**:
- **SLO Overview**: All SLOs in one view
- **Availability**: Per-service availability trends
- **Latency**: Latency percentiles and histograms
- **Error Budget**: Burn rate and remaining budget

**Dashboard URL**: `http://grafana.example.com/dashboards/slos`

### Alerts

**Burn Rate Alerts**:
```yaml
# Fast burn (2% budget in 1 hour)
- name: slo_fast_burn
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      /
      sum(rate(http_requests_total[1h]))
    ) > 0.02
  severity: critical

# Slow burn (5% budget in 6 hours)
- name: slo_slow_burn
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[6h]))
      /
      sum(rate(http_requests_total[6h]))
    ) > 0.05
  severity: warning
```

**Latency Alerts**:
```yaml
- name: latency_p95_breached
  expr: |
    histogram_quantile(0.95,
      rate(http_request_duration_ms_bucket[5m])
    ) > 200  # p95 SLO
  severity: warning
```

### Error Budget Reports

**Daily Report**:
```bash
# Calculate error budget remaining
python tools/slo/calculate_budget.py --service crm-api --window 30d
```

**Expected Output**:
```
SLO Report: crm-api (30 days)

Availability SLO: 99.9%
Current Availability: 99.95%
Error Budget Remaining: 50%

Status: ✓ HEALTHY (budget: 50%)
Allowed Downtime: 21.6 minutes remaining this month
```

---

## SLO Enforcement

### Pre-Deployment SLO Check

**Required before all deployments**:

```bash
# Check if sufficient error budget remains
./scripts/check_error_budget.sh

# If budget < 10%, deployment blocked
# Override requires manager approval
```

### Post-Deployment SLO Monitoring

**First 2 hours after deployment**:
- Monitor error rate (should be < 0.1%)
- Monitor latency (p95 should be within SLO)
- Monitor availability (should be ≥ 99.9%)

**Rollback Criteria**:
- Error rate > 1% for 5 minutes
- p95 latency > 2× SLO for 10 minutes
- Availability < 99% for 5 minutes

---

## Hot Path Performance Budgets

### Critical User Journeys

| Journey | Steps | Total Budget | Breakdown |
|---------|-------|--------------|-----------|
| User Login | 3 | 300ms (p95) | Auth: 100ms, DB: 100ms, Response: 100ms |
| Create Invoice | 5 | 800ms (p95) | Validation: 50ms, DB: 300ms, PDF: 400ms, Response: 50ms |
| Search Customers | 4 | 400ms (p95) | Query parse: 50ms, DB: 250ms, Format: 50ms, Response: 50ms |

### Latency Budget Enforcement

**Micro-benchmark Tests** (run in CI/CD):
```python
def test_login_latency():
    """Test that login stays within latency budget"""
    durations = []

    for _ in range(100):
        start = time.time()
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        duration_ms = (time.time() - start) * 1000
        durations.append(duration_ms)

    p95 = sorted(durations)[94]  # 95th percentile

    assert p95 < 300, f"Login p95 latency {p95:.0f}ms exceeds budget (300ms)"
```

**Budget Tracking**:
```bash
# Profile hot paths
python tests/performance/latency_test.py --profile

# Expected output:
# Login Journey (p95: 245ms):
#   - Authentication: 95ms
#   - Database lookup: 100ms
#   - Response encoding: 50ms
#   - Total budget used: 245/300ms (82%)
```

---

## SLO Review Process

### Monthly SLO Review

**Participants**: SRE, Engineering, Product

**Agenda**:
1. Review SLO compliance
2. Analyze error budget consumption
3. Discuss incidents and impact on SLOs
4. Adjust SLOs if needed (with 3-month notice)
5. Identify reliability improvements

**Outputs**:
- SLO compliance report
- Error budget burn rate trends
- Action items for next month

### Quarterly SLO Tuning

**Process**:
1. Analyze 90 days of data
2. Determine if SLOs are too strict or too loose
3. Propose adjustments (must be within 1% of current)
4. Get approval from stakeholders
5. Announce 30 days before change
6. Update monitoring and alerts

---

## SLO History

| Date | Service | Metric | Old SLO | New SLO | Reason |
|------|---------|--------|---------|---------|--------|
| 2025-11-01 | CRM API | Availability | N/A | 99.9% | Initial definition |

---

## References

- [Google SRE Book - SLOs](https://sre.google/sre-book/service-level-objectives/)
- [Observability Runbook](../observability/runbook.md)
- [DR Runbook](../dr/runbook.md)
- [Latency Benchmarks](../../tests/performance/README.md)
