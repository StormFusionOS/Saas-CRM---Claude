# Production Runbook: CRM + Ops Console

**Purpose**: Operational guide for deploying, running, and troubleshooting the RiverCityClean SaaS monorepo.

**Last Updated**: 2025-11-01

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Development Workflow](#development-workflow)
5. [Testing & Validation](#testing--validation)
6. [Deployment](#deployment)
7. [Monitoring & Health Checks](#monitoring--health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Security Hardening Checklist](#security-hardening-checklist)
10. [Runbook Maintenance](#runbook-maintenance)

---

## Quick Reference

### Service Ports

| Service         | Port  | URL                              |
|-----------------|-------|----------------------------------|
| CRM API         | 8000  | http://localhost:8000            |
| Ops API         | 8001  | http://localhost:8001            |
| CRM Frontend    | 5173  | http://localhost:5173            |
| Ops Console     | 5174  | http://localhost:5174            |
| CRM Database    | 5432  | postgresql://localhost:5432/crm  |
| Ops Database    | 5433  | postgresql://localhost:5433/ops  |
| Redis           | 6379  | redis://localhost:6379           |

### Demo Credentials

**Company**: RiverCityClean
**Base Domain**: rivercityclean.com

| User Role       | Email                          | Password     | Access     |
|-----------------|--------------------------------|--------------|------------|
| Sales           | Nathan@RiverCityClean.com      | password123  | CRM only   |
| Sales Manager   | Manager@RiverCityClean.com     | password123  | CRM only   |
| SEO Engineer    | SEO@RiverCityClean.com         | password123  | Ops only   |
| DevOps          | DevOps@RiverCityClean.com      | password123  | Ops only   |
| Owner           | Owner@RiverCityClean.com       | password123  | CRM + Ops  |

### One-Command Quickstart

```bash
# Start entire development environment
./scripts/dev.sh

# Stop all services
./scripts/dev.sh --stop

# Run all quality checks
./scripts/checks.sh

# Seed demo data
python scripts/seed.py
```

---

## Prerequisites

### Required Software

- **Python 3.11+**
  ```bash
  python --version  # Should show 3.11 or higher
  ```

- **Node.js 20+** with npm
  ```bash
  node --version   # Should show 20.x or higher
  npm --version    # Should show 10.x or higher
  ```

- **Docker & Docker Compose**
  ```bash
  docker --version          # Should show 24.x or higher
  docker-compose --version  # Should show 2.x or higher
  ```

- **bc** (for shell math in checks.sh)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install bc

  # macOS
  brew install bc
  ```

### Optional Tools

- **make** (for Makefile targets)
- **git** (for version control)
- **curl** (for API testing)
- **jq** (for JSON parsing)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repo-url>
cd Saas-CRM---Claude
```

### 2. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit with your settings
nano .env
```

**Key Variables**:

```bash
# Branding
COMPANY_NAME=RiverCityClean
BASE_DOMAIN=rivercityclean.com

# Database URLs
CRM_DATABASE_URL=postgresql://crm_user:crm_pass@localhost:5432/crm_db
OPS_DATABASE_URL=postgresql://ops_user:ops_pass@localhost:5433/ops_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT Secrets (CHANGE IN PRODUCTION!)
CRM_JWT_SECRET=your-crm-secret-change-me
OPS_JWT_SECRET=your-ops-secret-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API URLs for frontends
VITE_CRM_API_URL=http://localhost:8000/api/v1
VITE_OPS_API_URL=http://localhost:8001/api/v1

# Webhook Secrets (Facebook, Google, Twilio)
FACEBOOK_APP_SECRET=your-facebook-secret
GOOGLE_WEBHOOK_TOKEN=your-google-token
TWILIO_AUTH_TOKEN=your-twilio-token
```

### 3. Install Dependencies

**Python (Both APIs)**:
```bash
# CRM API
cd crm_api
pip install -r requirements.txt

# Ops API
cd ../ops_api
pip install -r requirements.txt
```

**Node.js (Both Frontends)**:
```bash
# CRM Frontend
cd crm
npm install

# Ops Console
cd ../ops-console
npm install
```

---

## Development Workflow

### Method 1: Automated (Recommended)

**Start Everything**:
```bash
./scripts/dev.sh
```

This script:
- ✅ Validates prerequisites (Docker, Python, Node)
- ✅ Starts Docker Compose (PostgreSQL + Redis)
- ✅ Waits for database health checks
- ✅ Starts CRM API (port 8000)
- ✅ Starts Ops API (port 8001)
- ✅ Starts CRM Frontend (port 5173)
- ✅ Starts Ops Console (port 5174)
- ✅ Displays summary with all URLs and credentials

**Stop Everything**:
```bash
./scripts/dev.sh --stop
```

### Method 2: Manual

**Terminal 1 - Docker Services**:
```bash
docker-compose up -d
docker-compose ps  # Verify all healthy
```

**Terminal 2 - CRM API**:
```bash
cd crm_api
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 3 - Ops API**:
```bash
cd ops_api
python -m uvicorn app.main:app --reload --port 8001
```

**Terminal 4 - CRM Frontend**:
```bash
cd crm
npm run dev
```

**Terminal 5 - Ops Console**:
```bash
cd ops-console
npm run dev
```

### Seeding Demo Data

```bash
# Seed all data (CRM + Ops)
python scripts/seed.py

# Seed CRM only
python scripts/seed.py --crm

# Seed Ops only
python scripts/seed.py --ops

# Clear all data
python scripts/seed.py --clear
```

**What gets seeded**:
- **CRM**: 5 contacts, 5 leads, ~12 interactions
- **Ops**: 3 alerts, 5 service health records

---

## Testing & Validation

### Run All Checks (CI-Ready)

```bash
./scripts/checks.sh
```

This validates:
- ✅ Python tests with ≥80% coverage
- ✅ TypeScript type checking
- ✅ Frontend builds
- ✅ Security tests (cross-role, cross-origin)
- ✅ Nginx hardening configuration

**Fast Mode** (skip slower checks):
```bash
./scripts/checks.sh --fast
```

### Individual Test Suites

**CRM API**:
```bash
cd crm_api
pytest tests/ -v --cov=app --cov-report=term
```

**Ops API**:
```bash
cd ops_api
pytest tests/ -v --cov=app --cov-report=term
```

**CRM Frontend**:
```bash
cd crm
npm test
```

**Ops Console**:
```bash
cd ops-console
npm test
```

### Coverage Reports

```bash
# Generate HTML coverage report
cd crm_api
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # View in browser

# Same for Ops API
cd ../ops_api
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Security Tests

**Cross-Role Security**:
```bash
# Verify SALES cannot access MANAGER endpoints
cd crm_api
pytest tests/test_cross_role_security.py -v

# Verify SEO cannot access DEVOPS endpoints
cd ../ops_api
pytest tests/test_cross_role_security.py -v
```

**Nginx Hardening**:
```bash
cd ops_api
pytest tests/test_hardening_script.py -v
```

---

## Deployment

### Pre-Deployment Checklist

- [ ] All tests passing (`./scripts/checks.sh`)
- [ ] Coverage ≥80% on both APIs
- [ ] Environment variables configured for production
- [ ] JWT secrets changed from defaults
- [ ] Database migrations applied
- [ ] Nginx SSL certificates installed
- [ ] Domain DNS configured
- [ ] Backup strategy in place
- [ ] Monitoring/alerting configured

### Database Migrations

**Generate Migration**:
```bash
# CRM database
cd crm_api
alembic revision --autogenerate -m "add new column"

# Ops database
cd ops_api
alembic revision --autogenerate -m "add scheduler table"
```

**Apply Migrations**:
```bash
# CRM
cd crm_api
alembic upgrade head

# Ops
cd ops_api
alembic upgrade head
```

**Rollback**:
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

**Check for Drift**:
```bash
python tools/check_migrations.py
python tools/schema_diff.py
```

### Docker Deployment

**Build Images**:
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build crm-api
```

**Run in Production Mode**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service
docker-compose logs -f crm-api

# Check service status
docker-compose ps
```

**Health Checks**:
```bash
# CRM API
curl http://localhost:8000/health

# Ops API
curl http://localhost:8001/health
```

### Nginx Deployment

**1. Copy Configuration**:
```bash
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/rivercityclean
sudo ln -s /etc/nginx/sites-available/rivercityclean /etc/nginx/sites-enabled/
```

**2. Update SSL Certificates**:
```bash
# Using certbot (Let's Encrypt)
sudo certbot --nginx -d crm.rivercityclean.com -d ops.rivercityclean.com
```

**3. Test & Reload**:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

**4. Verify Security Headers**:
```bash
curl -I https://crm.rivercityclean.com | grep -E "Content-Security-Policy|Strict-Transport-Security|X-Frame-Options"
```

---

## Monitoring & Health Checks

### Happy Path Smoke Tests

**CRM Workflow**:
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"Nathan@RiverCityClean.com","password":"password123"}' \
  | jq -r '.access_token')

# 2. List leads
curl -s http://localhost:8000/api/v1/leads \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Create contact
curl -s -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"Test","last_name":"User"}' | jq

# 4. Health check
curl http://localhost:8000/health
```

**Ops Workflow**:
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"DevOps@RiverCityClean.com","password":"password123"}' \
  | jq -r '.access_token')

# 2. Get service status
curl -s http://localhost:8001/api/v1/status \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. List backups
curl -s http://localhost:8001/api/v1/backups \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Health check
curl http://localhost:8001/health
```

### Service Health Monitoring

**Check All Services**:
```bash
#!/bin/bash
services=(
  "http://localhost:8000/health|CRM API"
  "http://localhost:8001/health|Ops API"
  "http://localhost:5173|CRM Frontend"
  "http://localhost:5174|Ops Console"
)

for service in "${services[@]}"; do
  url="${service%%|*}"
  name="${service##*|}"
  if curl -sf "$url" > /dev/null 2>&1; then
    echo "✅ $name"
  else
    echo "❌ $name"
  fi
done
```

### Log Locations

**Development**:
- CRM API: `crm_api/app.log` (if configured)
- Ops API: `ops_api/app.log` (if configured)
- Frontend: Browser console

**Docker**:
```bash
docker-compose logs -f crm-api
docker-compose logs -f ops-api
docker-compose logs -f crm-db
```

**Production Nginx**:
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Symptoms**:
```
Error: Address already in use (bind: 127.0.0.1:8000)
```

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8002
```

#### 2. Docker Services Not Starting

**Symptoms**:
```
ERROR: for crm-db  Container is unhealthy
```

**Diagnosis**:
```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs crm-db

# Check disk space
df -h

# Restart services
docker-compose restart
```

**Solution**:
```bash
# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

#### 3. Database Connection Errors

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Diagnosis**:
```bash
# Test direct connection
psql -h localhost -p 5432 -U crm_user -d crm_db

# Check environment variables
echo $CRM_DATABASE_URL

# Verify Docker network
docker network ls
docker network inspect saas-crm---claude_default
```

**Solution**:
```bash
# Verify .env file
cat .env | grep DATABASE_URL

# Restart database
docker-compose restart crm-db

# Check migrations
cd crm_api
alembic current
alembic upgrade head
```

#### 4. Frontend Build Failures

**Symptoms**:
```
ERROR: Cannot find module 'react'
```

**Solution**:
```bash
# Clear cache and reinstall
cd crm
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite

# Rebuild
npm run build
```

#### 5. JWT Token Errors

**Symptoms**:
```
401 Unauthorized: Invalid token
```

**Diagnosis**:
```bash
# Check token in browser DevTools > Application > Local Storage

# Verify JWT secret matches between backend and .env
grep JWT_SECRET .env

# Decode token (without verification)
echo "<token>" | cut -d. -f2 | base64 -d | jq
```

**Solution**:
```bash
# Clear localStorage in browser console
localStorage.clear()

# Login again
# Or refresh token if expired
```

#### 6. CORS Errors

**Symptoms**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**Diagnosis**:
```bash
# Check Nginx CORS headers
curl -I -H "Origin: http://localhost:5173" http://localhost:8000/health
```

**Solution**:
- Verify `VITE_CRM_API_URL` in `.env`
- Check Nginx `Access-Control-Allow-Origin` header
- Ensure origin matches expected domain

#### 7. Test Failures

**Symptoms**:
```
FAILED tests/test_auth.py::test_login_success
```

**Diagnosis**:
```bash
# Run with verbose output
pytest tests/test_auth.py::test_login_success -vvs

# Check test database state
# Tests use in-memory stubs, so no DB state persists
```

**Solution**:
```bash
# Ensure demo credentials match
grep "Nathan@RiverCityClean.com" crm_api/app/db.py
grep "Nathan@RiverCityClean.com" crm_api/tests/test_auth.py

# Clear pytest cache
rm -rf .pytest_cache
pytest tests/ --cache-clear
```

#### 8. Low Test Coverage

**Symptoms**:
```
ERROR: Coverage 67% is below 80% threshold
```

**Solution**:
```bash
# Identify untested code
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Add tests for uncovered modules
# Focus on: models, schemas, services
```

---

## Security Hardening Checklist

### Pre-Production Security Review

- [ ] **JWT Secrets**: Changed from defaults, stored securely
- [ ] **Database Passwords**: Strong passwords (16+ chars)
- [ ] **Environment Variables**: Not committed to git
- [ ] **HTTPS Only**: SSL certificates installed and valid
- [ ] **HSTS Enabled**: Strict-Transport-Security header present
- [ ] **CSP Headers**: Content-Security-Policy configured
- [ ] **Rate Limiting**: Nginx rate limits active
- [ ] **Origin Enforcement**: CORS properly restricts origins
- [ ] **Webhook Signatures**: Facebook/Google/Twilio verification enabled
- [ ] **RBAC Tests Passing**: Cross-role denial verified
- [ ] **Nginx Hardening**: All tests in `test_hardening_script.py` pass
- [ ] **SQL Injection**: Parameterized queries used (ORM enforces this)
- [ ] **XSS Protection**: X-Content-Type-Options: nosniff
- [ ] **Clickjacking**: X-Frame-Options: SAMEORIGIN
- [ ] **Session Security**: Refresh tokens with short expiry
- [ ] **Logging**: Sensitive data (passwords, tokens) not logged
- [ ] **Dependency Audit**: `pip audit` and `npm audit` run
- [ ] **Secrets Scanning**: No secrets in git history

### Validate Security Configuration

```bash
# Run security tests
cd ops_api
pytest tests/test_hardening_script.py -v

# Run cross-role tests
cd crm_api
pytest tests/test_cross_role_security.py -v
cd ../ops_api
pytest tests/test_cross_role_security.py -v

# Check for secrets in git
git secrets --scan-history  # If installed

# Audit dependencies
pip install pip-audit
pip-audit

cd crm
npm audit
cd ../ops-console
npm audit
```

---

## Runbook Maintenance

### When to Update This Runbook

- ✅ New service added to monorepo
- ✅ Port numbers changed
- ✅ Environment variables added/removed
- ✅ Deployment process updated
- ✅ New common errors discovered
- ✅ Security requirements changed
- ✅ Database schema changes require new migration steps

### Runbook Version History

| Version | Date       | Author                  | Changes                        |
|---------|------------|-------------------------|--------------------------------|
| 1.0     | 2025-11-01 | Senior Release Engineer | Initial production-ready docs  |

---

## Emergency Contacts

**On-Call Rotation**: [Configure your rotation]

**Escalation**:
1. Check logs and health endpoints
2. Review recent deployments/changes
3. Consult this runbook's troubleshooting section
4. Contact on-call engineer
5. Escalate to platform team

**Key Services**:
- Database: PostgreSQL (managed/self-hosted)
- Caching: Redis
- Reverse Proxy: Nginx
- Hosting: [Your cloud provider]

---

## Quick Command Reference

```bash
# Start everything
./scripts/dev.sh

# Stop everything
./scripts/dev.sh --stop

# Run all checks
./scripts/checks.sh

# Seed demo data
python scripts/seed.py

# Run tests
cd crm_api && pytest tests/ -v
cd ops_api && pytest tests/ -v

# Check coverage
pytest tests/ --cov=app --cov-report=term

# Build frontends
cd crm && npm run build
cd ops-console && npm run build

# Database migrations
cd crm_api && alembic upgrade head
cd ops_api && alembic upgrade head

# Docker operations
docker-compose up -d
docker-compose ps
docker-compose logs -f
docker-compose down

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

**End of Runbook**
