# Performance Budgets

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: Performance Engineering Team

## Overview

This document defines performance budgets for all API endpoints. These budgets are enforced in CI/CD to prevent performance regressions.

**Enforcement**:
- CI fails if p95 latency exceeds budget by >10%
- Alerts fire if p95 exceeds budget in production
- Monthly review to adjust budgets based on real usage

---

## Budget Philosophy

**Budget Setting Criteria**:
1. **User Experience**: Based on perceived responsiveness thresholds
2. **Business Impact**: Critical paths have tighter budgets
3. **Technical Constraints**: Database queries, external APIs, etc.
4. **Historical Data**: P95 + 20% headroom for growth

**Breach Tolerance**:
- **0-10% over budget**: Warning (allowed)
- **10-25% over budget**: CI fails, requires approval to merge
- **>25% over budget**: Hard failure, must be fixed

---

## API Endpoint Budgets

### Authentication Endpoints

| Endpoint | Method | p50 Budget | p95 Budget | p99 Budget | Notes |
|----------|--------|------------|------------|------------|-------|
| `/api/v1/auth/login` | POST | 80ms | 300ms | 500ms | Critical: user-facing |
| `/api/v1/auth/logout` | POST | 20ms | 100ms | 200ms | Simple token invalidation |
| `/api/v1/auth/refresh` | POST | 50ms | 200ms | 400ms | Frequent operation |
| `/api/v1/auth/validate` | GET | 10ms | 50ms | 100ms | Called on every request |

**Login Budget Breakdown** (p95: 300ms):
- Auth validation: 50ms
- Database lookup: 150ms
- Token generation: 50ms
- Response: 50ms

### CRM Endpoints

| Endpoint | Method | p50 Budget | p95 Budget | p99 Budget | Notes |
|----------|--------|------------|------------|------------|-------|
| `/api/v1/customers` | GET | 100ms | 400ms | 800ms | List with pagination |
| `/api/v1/customers/{id}` | GET | 50ms | 200ms | 400ms | Single record |
| `/api/v1/customers` | POST | 120ms | 500ms | 1000ms | Create with validation |
| `/api/v1/customers/{id}` | PUT | 130ms | 550ms | 1100ms | Update with validation |
| `/api/v1/customers/{id}` | DELETE | 80ms | 350ms | 700ms | Soft delete |
| `/api/v1/leads` | GET | 120ms | 500ms | 1000ms | List with filters |
| `/api/v1/leads/{id}` | GET | 60ms | 250ms | 500ms | Single lead |
| `/api/v1/leads` | POST | 140ms | 600ms | 1200ms | Create lead |
| `/api/v1/invoices` | GET | 150ms | 600ms | 1200ms | Complex joins |
| `/api/v1/invoices/{id}` | GET | 100ms | 400ms | 800ms | With line items |
| `/api/v1/invoices` | POST | 200ms | 800ms | 1500ms | PDF generation |

**Leads List Budget Breakdown** (p95: 500ms):
- Query parsing: 20ms
- Database query: 300ms
- Result serialization: 100ms
- Response: 80ms

### Operations Endpoints

| Endpoint | Method | p50 Budget | p95 Budget | p99 Budget | Notes |
|----------|--------|------------|------------|------------|-------|
| `/api/v1/tasks/enqueue` | POST | 30ms | 150ms | 300ms | Background task queue |
| `/api/v1/tasks/{id}` | GET | 20ms | 100ms | 200ms | Task status |
| `/api/v1/metrics` | GET | 200ms | 1000ms | 2000ms | Aggregation queries |
| `/api/v1/reports/daily` | GET | 500ms | 2000ms | 4000ms | Heavy computation |
| `/api/v1/health` | GET | 5ms | 50ms | 100ms | Health check |

**Task Enqueue Budget Breakdown** (p95: 150ms):
- Validation: 10ms
- Queue insertion: 100ms
- Redis update: 30ms
- Response: 10ms

### Search Endpoints

| Endpoint | Method | p50 Budget | p95 Budget | p99 Budget | Notes |
|----------|--------|------------|------------|------------|-------|
| `/api/v1/search/customers` | GET | 150ms | 600ms | 1200ms | Full-text search |
| `/api/v1/search/leads` | GET | 120ms | 500ms | 1000ms | Full-text search |
| `/api/v1/search/global` | GET | 200ms | 800ms | 1500ms | Cross-entity search |

### File Operations

| Endpoint | Method | p50 Budget | p95 Budget | p99 Budget | Notes |
|----------|--------|------------|------------|------------|-------|
| `/api/v1/files/upload` | POST | 500ms | 2000ms | 4000ms | Up to 10MB |
| `/api/v1/files/{id}/download` | GET | 200ms | 1000ms | 2000ms | Streaming |
| `/api/v1/export/customers` | POST | 1000ms | 5000ms | 10000ms | CSV export |

---

## Database Query Budgets

| Query Type | p50 Budget | p95 Budget | Notes |
|------------|------------|------------|-------|
| Primary key lookup | 5ms | 20ms | Indexed |
| Index scan | 20ms | 100ms | With LIMIT |
| Full table scan | N/A | N/A | Should never happen |
| Join (2 tables) | 50ms | 200ms | Indexed joins only |
| Join (3+ tables) | 100ms | 400ms | Complex queries |
| Aggregation | 100ms | 500ms | GROUP BY, COUNT, etc. |

**Query Optimization Rules**:
1. All queries must use indexes (no seq scans in production)
2. Limit result sets (default: 100 rows)
3. Use connection pooling
4. Enable query caching for repeated queries

---

## Background Job Budgets

| Job Type | p50 Budget | p95 Budget | p99 Budget | Notes |
|----------|------------|------------|------------|-------|
| Email send | 500ms | 2000ms | 4000ms | External SMTP |
| PDF generation | 1000ms | 4000ms | 8000ms | Complex invoices |
| Data sync | 2000ms | 10000ms | 20000ms | External API |
| Report generation | 5000ms | 20000ms | 40000ms | Heavy computation |

---

## Frontend Performance Budgets

| Metric | Budget | Notes |
|--------|--------|-------|
| First Contentful Paint (FCP) | <1.5s | Critical for UX |
| Largest Contentful Paint (LCP) | <2.5s | Core Web Vital |
| Time to Interactive (TTI) | <3.5s | Usability threshold |
| Total Bundle Size | <300KB | Gzipped |
| JavaScript Bundle | <200KB | Gzipped |
| CSS Bundle | <50KB | Gzipped |

---

## Budget Enforcement

### CI/CD Integration

**Pre-Merge Check**:
```bash
# Run in CI pipeline before merge
python scripts/perf/check_budgets.py --report artifacts/perf/load_test.json

# Exit codes:
# 0 = All budgets met
# 1 = Budgets exceeded by >10%
# 2 = Missing data
```

**Enforcement Rules**:
1. Load test must run on every PR
2. Results compared against budgets
3. PR blocked if p95 > budget × 1.10
4. Override requires performance lead approval

### Production Monitoring

**Alerts**:
```yaml
# Alert when p95 exceeds budget
- name: latency_budget_breach
  expr: |
    histogram_quantile(0.95,
      rate(http_request_duration_ms_bucket[5m])
    ) > (budget_p95_ms * 1.1)
  for: 10m
  severity: warning
  annotations:
    summary: "Latency budget breach for {{ $labels.endpoint }}"
```

---

## Budget Review Process

### Monthly Review

**Participants**: Performance Engineering, Backend Team, Product

**Agenda**:
1. Review actual p50/p95/p99 from production
2. Identify endpoints consistently under/over budget
3. Adjust budgets based on real usage patterns
4. Identify optimization opportunities

**Budget Adjustment Criteria**:
- Consistently 50%+ under budget → Tighten by 20%
- Consistently 80%+ of budget → Loosen by 20%
- Must maintain user experience standards

### Quarterly Optimization

**Process**:
1. Identify top 10 slowest endpoints
2. Profile and optimize
3. Update budgets to reflect improvements
4. Document optimization techniques

---

## Performance Optimization Checklist

### Before Requesting Budget Increase

Verify you've tried:
- [ ] Database query optimization (indexes, explain analyze)
- [ ] Caching (Redis, in-memory)
- [ ] Connection pooling
- [ ] Async I/O for external calls
- [ ] Pagination for large result sets
- [ ] Response compression
- [ ] Database denormalization (if appropriate)
- [ ] CDN for static assets

### Documentation Required

When requesting budget change:
1. Benchmark results showing current performance
2. Profiling data showing bottleneck
3. List of optimizations attempted
4. Business justification for increased budget
5. Plan to improve performance over time

---

## Sample Budget Violations

### Example 1: Acceptable (Warning Only)

```json
{
  "endpoint": "/api/v1/leads",
  "method": "GET",
  "latency_p95": 525,
  "budget_p95": 500,
  "breach_percentage": 5.0,
  "status": "WARNING"
}
```

**Action**: Monitor, no immediate action required.

### Example 2: CI Failure Required

```json
{
  "endpoint": "/api/v1/customers",
  "method": "POST",
  "latency_p95": 600,
  "budget_p95": 500,
  "breach_percentage": 20.0,
  "status": "FAIL"
}
```

**Action**:
1. Profile endpoint to find bottleneck
2. Optimize or request budget increase
3. Update PR with fix

### Example 3: Critical Breach

```json
{
  "endpoint": "/api/v1/auth/login",
  "method": "POST",
  "latency_p95": 450,
  "budget_p95": 300,
  "breach_percentage": 50.0,
  "status": "CRITICAL"
}
```

**Action**:
1. Immediate investigation required
2. Rollback if in production
3. Root cause analysis
4. Fix before re-deploying

---

## Budget History

| Date | Endpoint | Old Budget | New Budget | Reason |
|------|----------|------------|------------|--------|
| 2025-11-01 | All | N/A | Initial | Initial budget definition |

---

## References

- [Load Testing Harness](../../tools/perf/harness.py)
- [Budget Check Script](../../scripts/perf/check_budgets.py)
- [SLO Documentation](../reliability/slos.md)
- [Latency Benchmarks](../../tests/performance/latency_test.py)

---

## Appendix: Budget Calculation Methodology

**Formula**:
```
Budget_p95 = Historical_p95 × 1.20 (20% headroom)

# Or for new endpoints:
Budget_p95 = Σ(Component_Latency) × 1.30 (30% safety margin)
```

**Components for Login**:
- Auth validation: 50ms
- DB query: 150ms
- Token generation: 50ms
- Response: 50ms
- **Total**: 300ms

**This gives us**: 300ms × 1.30 = 390ms → Rounded to 400ms for production
