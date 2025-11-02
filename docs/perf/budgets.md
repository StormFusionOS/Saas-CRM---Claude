# Performance Budgets

Performance budgets define acceptable latency thresholds for critical API endpoints. These targets are measured using the smoke test harness with in-memory backend and 10 concurrent requests.

## Purpose

- **Prevent Performance Regression**: Catch performance issues before production
- **Guide Optimization**: Set clear targets for optimization work
- **SLA Baseline**: Establish foundation for production SLAs

## Test Environment

- **Infrastructure**: In-memory database (no network I/O)
- **Concurrency**: 10 concurrent requests
- **Sample Size**: 100 requests per endpoint
- **Metrics**: p50 (median) and p95 (95th percentile) latency

## Budget Targets

| Endpoint | Metric | Budget | Notes |
|----------|--------|--------|-------|
| `/api/auth/login` | p95 | < 120ms | JWT generation + password hash verification |
| `/api/v1/leads` | p95 | < 200ms | List query with contact joins |
| `/api/scheduler/next` | p95 | < 100ms | Lightweight task queue lookup |

## Rationale

### Authentication Endpoints (`/auth/login`)

**Budget: p95 < 120ms**

Authentication is a hot path that occurs on every user session start. The 120ms budget accounts for:
- Password hash verification (~50-80ms with bcrypt)
- JWT token generation (~5-10ms)
- Database user lookup (~10-20ms in-memory)
- Safety margin for variance

**Why p95?** We use p95 instead of p99 because:
- Smoke tests use small sample size (100 requests)
- p95 is more stable for small samples
- Still catches outliers without noise from JIT warm-up

### List Endpoints (`/v1/leads`)

**Budget: p95 < 200ms**

Lead listing is a frequent operation in the CRM UI. The 200ms budget accounts for:
- Query execution (~50-100ms)
- Contact join operations (~30-50ms)
- JSON serialization (~20-40ms)
- Safety margin for in-memory aggregation

This endpoint typically returns 10-50 leads with full contact details.

### Scheduler Endpoints (`/scheduler/next`)

**Budget: p95 < 100ms**

Task scheduling is high-frequency and should be extremely fast. The 100ms budget accounts for:
- Task queue lookup (~20-40ms)
- Priority calculation (~10-20ms)
- Lock acquisition (in-memory, ~5-10ms)
- Safety margin

This endpoint must support background workers polling frequently without overhead.

## Budget Evolution

These budgets are **starter targets** for the smoke test rig with in-memory backend. As the system evolves:

### When to Tighten Budgets
- After optimization work
- When moving to faster infrastructure
- For premium SLA tiers

### When to Relax Budgets
- Adding complex business logic (e.g., RBAC checks)
- Introducing external service calls
- Scaling to larger datasets

### Production Adjustments

Production budgets should account for:
- **Network latency**: +20-50ms
- **Database I/O**: +50-150ms (PostgreSQL on same AZ)
- **Distributed tracing**: +5-10ms
- **Load variance**: +2x safety margin

**Example Production Budget:**
```
p95 login < 300ms  (120ms base + 50ms network + 80ms DB + 50ms margin)
```

## Monitoring in Production

Once deployed, monitor:
- **p50/p95/p99 latencies** via APM (Datadog, New Relic, etc.)
- **Error rates** for 4xx/5xx responses
- **Apdex score** for user satisfaction (T=250ms)

Set alerts:
- ⚠️ **Warning**: p95 exceeds budget by 25%
- 🚨 **Critical**: p95 exceeds budget by 50% or error rate > 1%

## Testing

Run smoke tests locally:

```bash
# Start API server
cd crm_api
uvicorn app.main:app --port 8000

# Run smoke tests (separate terminal)
python tools/perf/smoke.py

# With custom base URL
python tools/perf/smoke.py --base-url http://localhost:8000
```

Expected output:
```
PERFORMANCE SMOKE TEST RESULTS
================================================================================

Endpoint                       Requests   Errors    p50 (ms)    p95 (ms)    Budget
------------------------------------------------------------------------------------------
/api/auth/login                100        0              45.2        98.3    <120ms    ✓
/api/v1/leads                  100        0              78.9       156.7    <200ms    ✓
/api/scheduler/next            100        0              23.4        67.2    <100ms    ✓

✅ PERFORMANCE OK - ALL TESTS PASSED
```

## Continuous Integration

Integrate smoke tests into CI/CD:

```yaml
# .github/workflows/perf.yml
- name: Performance Smoke Tests
  run: |
    # Start server in background
    cd crm_api && uvicorn app.main:app --port 8000 &
    sleep 5

    # Run smoke tests
    python tools/perf/smoke.py

    # Tests fail CI if budgets exceeded
```

## References

- [Google Web Vitals](https://web.dev/vitals/) - User-centric performance metrics
- [Apdex Standard](https://www.apdex.org/) - Application performance index
- [SRE Book - SLIs/SLOs](https://sre.google/sre-book/service-level-objectives/) - Service level objectives
