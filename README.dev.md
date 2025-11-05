# Local Development Guide

Complete guide for setting up and running the SaaS CRM system locally using Docker.

## Quick Start

```bash
# 1. Clone and enter project
cd Saas-CRM---Claude

# 2. Initial setup (copy .env, install deps)
make setup

# 3. Start all services
make dev-up

# 4. View logs
make dev-logs
```

## Prerequisites

- **Docker** & **Docker Compose** (v2.0+)
- **Node.js** 18+ and **npm**
- **Python** 3.11+
- **Git**

## Architecture Overview

The monorepo contains:
- **crm/** - CRM frontend (React + TypeScript + Vite)
- **ops-console/** - Ops frontend (React + TypeScript + Vite)
- **crm_api/** - CRM backend (FastAPI + PostgreSQL)
- **ops_api/** - Ops backend (FastAPI + PostgreSQL)

### Services

| Service | Port | Description |
|---------|------|-------------|
| CRM API | 8000 | Main CRM REST API |
| Ops API | 8001 | Operations console API |
| CRM DB | 5433 | PostgreSQL (CRM data) |
| Ops DB | 5434 | PostgreSQL (Ops data) |
| Redis | 6379 | Cache & Celery broker |
| Qdrant | 6333 | Vector database (RAG) |
| Adminer | 8080 | Database GUI |
| RedisInsight | 8081 | Redis GUI |

## Development Workflows

### Option 1: All Services in Docker (Recommended for Backend Work)

```bash
# Start everything
make dev-up

# View logs
make dev-logs

# Restart specific service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart crm-api

# Stop everything
make dev-down
```

### Option 2: Hybrid (Frontend Native, Backend Docker)

Best for frontend development with hot-reload:

```bash
# Start only backend services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d crm-db ops-db redis qdrant

# Run frontends natively
cd crm && npm run dev           # Runs on :5173
cd ops-console && npm run dev   # Runs on :5174
```

### Option 3: Fully Native (No Docker)

For maximum flexibility:

```bash
# Start databases manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d crm-db ops-db redis

# Run APIs natively
cd crm_api && uvicorn app.main:app --reload --port 8000
cd ops_api && uvicorn app.main:app --reload --port 8001

# Run frontends natively
cd crm && npm run dev
cd ops-console && npm run dev
```

## Common Tasks

### Reset Databases

**WARNING:** This destroys all data!

```bash
make db-reset
```

### View Database

Using Adminer GUI (easiest):
1. Open http://localhost:8080
2. Server: `crm-db` or `ops-db`
3. Username/Password: from `.env`

Using CLI:
```bash
# CRM database
make db-shell-crm

# Ops database
make db-shell-ops
```

### Run Tests

```bash
# All tests
make test

# API tests only
make test-api
```

### Code Quality

```bash
# Run linters
make lint

# Clean artifacts
make clean
```

### Rebuild Services

After changing Dockerfile or requirements:

```bash
make dev-rebuild
```

## Environment Variables

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Key variables:
- `CRM_SECRET_KEY` - JWT signing secret
- `CRM_DB_PASSWORD` - Database password
- `CRM_CORS_ORIGINS` - Allowed frontend origins

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Refused

```bash
# Check if DB is healthy
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# View DB logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs crm-db
```

### Frontend Can't Reach API

Check CORS settings in `.env`:
```
CRM_CORS_ORIGINS=http://localhost:5173,http://192.168.0.220:5173
```

### Hot-Reload Not Working

1. **Frontend:** Vite may need host flag
   ```bash
   npm run dev -- --host 0.0.0.0
   ```

2. **Backend:** Ensure volume mounts in `docker-compose.dev.yml`:
   ```yaml
   volumes:
     - ./crm_api:/app
   ```

## Service URLs

Once running:

- **CRM SPA:** http://localhost:5173
- **Ops SPA:** http://localhost:5174
- **CRM API Docs:** http://localhost:8000/docs
- **Ops API Docs:** http://localhost:8001/docs
- **Adminer (DB GUI):** http://localhost:8080
- **RedisInsight:** http://localhost:8081

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Check [API Documentation](http://localhost:8000/docs) for endpoints
- Review [Contributing Guidelines](./CONTRIBUTING.md)

## Getting Help

- **Logs:** `make dev-logs`
- **Status:** `make status`
- **Issues:** Check GitHub Issues

---

**Happy Coding!** 🚀
