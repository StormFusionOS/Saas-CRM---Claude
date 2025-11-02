# Deployment Scripts

This directory contains deployment scripts for the RiverCityClean SaaS CRM system.

## Dry Run Deployment

The `dry_run.sh` script performs a production-like deployment sequence locally to verify the entire stack works correctly.

### Prerequisites

- Docker and Docker Compose
- Node.js and npm
- curl
- (Optional) nginx

### Usage

```bash
./scripts/deploy/dry_run.sh
```

### What It Does

1. **Cleanup**: Stops any existing services
2. **Infrastructure**: Starts databases, Redis, and API services via Docker Compose
3. **Health Checks**: Waits for all services to be healthy
4. **Data Seeding**: Initializes demo data (currently using in-memory data)
5. **SPA Build**: Builds both CRM and Ops Console SPAs
6. **Nginx** (optional): Starts Nginx to serve SPAs and proxy APIs
7. **Smoke Tests**: Tests all endpoints:
   - `GET /health` (both APIs)
   - `GET /metrics` (both APIs)
   - `GET /api/v1/v1/leads` (CRM API, with authentication token)
8. **Log Check**: Scans logs for stack traces
9. **Summary**: Prints deployment status and service URLs

### Expected Output

```
=================================================================
                      DEPLOY OK ✓
=================================================================

Service URLs:
  • CRM API:         http://localhost:8000
  • CRM API Health:  http://localhost:8000/health
  • CRM API Metrics: http://localhost:8000/metrics
  • CRM API Docs:    http://localhost:8000/docs

  • Ops API:         http://localhost:8001
  • Ops API Health:  http://localhost:8001/health
  • Ops API Metrics: http://localhost:8001/metrics
  • Ops API Docs:    http://localhost:8001/docs

  • CRM SPA:         http://localhost:8080/
  • Ops Console:     http://localhost:8080/ops/
```

### Acceptance Criteria

✅ All Docker services start successfully
✅ Health checks pass for both APIs
✅ Metrics endpoints return data
✅ Authenticated API calls succeed
✅ No stack traces in logs
✅ All curls return 200 OK

### Cleanup

To stop all services:

```bash
# Stop Docker services
docker-compose down

# Stop Nginx (if running)
kill $(cat nginx.pid)
```

### Logs

The dry run script creates a detailed log file at `deploy_dry_run.log` in the project root.

View Docker logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f crm-api
docker-compose logs -f ops-api
```

### Troubleshooting

**Port already in use:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different ports in docker-compose.yml
```

**Docker build fails:**
```bash
# Rebuild without cache
docker-compose build --no-cache
```

**Nginx not installed:**
The script will continue without Nginx. APIs will still be accessible directly on ports 8000 and 8001.

**NPM install fails:**
```bash
# Clear npm cache
npm cache clean --force

# Install dependencies manually
cd crm && npm install
cd ../ops-console && npm install
```

## Production Deployment

For actual production deployment, see the main deployment documentation in `/docs/DEPLOYMENT.md`.

Key differences from dry run:
- Uses real databases (not in-memory)
- Runs migrations before starting
- Uses production secrets from secrets manager
- Deploys behind load balancer
- Enables HTTPS/TLS
- Configures monitoring and alerting
