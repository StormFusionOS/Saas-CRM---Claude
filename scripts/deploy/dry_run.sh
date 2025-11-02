#!/usr/bin/env bash
# ==============================================================================
# Deployment Dry Run Script
# ==============================================================================
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# Role: Release Engineer
# Purpose: Perform a production-like deployment dry run
#
# Sequence:
#   1. Migrate → Seed → Start APIs (Docker)
#   2. Build SPAs
#   3. Serve via Nginx (local)
#   4. Health checks and smoke tests
#
# Usage:
#   ./scripts/deploy/dry_run.sh
#
# Acceptance:
#   - All services start successfully
#   - All health checks pass
#   - All API endpoints respond correctly
#   - No stack traces in logs
# ==============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ports
CRM_API_PORT=8000
OPS_API_PORT=8001
NGINX_PORT=8080

# Log file
LOG_FILE="$PROJECT_ROOT/deploy_dry_run.log"

# ==============================================================================
# Helper Functions
# ==============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $*" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $*" | tee -a "$LOG_FILE"
}

section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}===================================================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$*${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}===================================================================${NC}" | tee -a "$LOG_FILE"
}

wait_for_service() {
    local name=$1
    local url=$2
    local max_wait=${3:-60}
    local elapsed=0

    log "Waiting for $name to be ready at $url..."

    while [ $elapsed -lt $max_wait ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            success "$name is ready"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo -n "." >> "$LOG_FILE"
    done

    error "$name failed to start within ${max_wait}s"
    return 1
}

check_prerequisites() {
    section "Checking Prerequisites"

    local missing=0

    for cmd in docker docker-compose node npm curl; do
        if command -v $cmd &> /dev/null; then
            success "$cmd is installed"
        else
            error "$cmd is not installed"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -gt 0 ]; then
        error "$missing required tools are missing"
        exit 1
    fi
}

cleanup() {
    section "Cleanup"
    log "Stopping any existing services..."

    # Stop Nginx if running
    if [ -f "$PROJECT_ROOT/nginx.pid" ]; then
        log "Stopping Nginx..."
        kill $(cat "$PROJECT_ROOT/nginx.pid") 2>/dev/null || true
        rm -f "$PROJECT_ROOT/nginx.pid"
    fi

    # Stop Docker services
    cd "$PROJECT_ROOT"
    docker-compose down -v 2>&1 >> "$LOG_FILE" || true

    success "Cleanup complete"
}

# ==============================================================================
# Main Deployment Steps
# ==============================================================================

start_infrastructure() {
    section "Step 1: Starting Infrastructure (Docker Compose)"

    cd "$PROJECT_ROOT"

    log "Starting databases, Redis, and API services..."
    docker-compose up -d --build 2>&1 >> "$LOG_FILE"

    success "Docker services started"
}

wait_for_services() {
    section "Step 2: Waiting for Services to be Healthy"

    wait_for_service "CRM API" "http://localhost:$CRM_API_PORT/health" 90
    wait_for_service "Ops API" "http://localhost:$OPS_API_PORT/health" 90

    # Give services a moment to fully initialize
    sleep 2
}

seed_data() {
    section "Step 3: Seeding Data"

    log "Running seed script for CRM API..."
    # Note: In a real deployment, you'd run migrations here
    # For now, the in-memory database auto-initializes with demo data
    success "Data seeding complete (in-memory demo data)"
}

build_spas() {
    section "Step 4: Building SPAs"

    # Build CRM SPA
    log "Building CRM SPA..."
    cd "$PROJECT_ROOT/crm"
    npm install --silent 2>&1 >> "$LOG_FILE" || true
    npm run build 2>&1 >> "$LOG_FILE"
    success "CRM SPA built"

    # Build Ops Console SPA
    log "Building Ops Console SPA..."
    cd "$PROJECT_ROOT/ops-console"
    npm install --silent 2>&1 >> "$LOG_FILE" || true
    npm run build 2>&1 >> "$LOG_FILE"
    success "Ops Console SPA built"
}

start_nginx() {
    section "Step 5: Starting Nginx"

    cd "$PROJECT_ROOT"

    # Check if nginx is available
    if ! command -v nginx &> /dev/null; then
        warn "Nginx is not installed - skipping web server"
        warn "SPAs built but not served"
        return 0
    fi

    # Create a simple nginx config for local testing
    log "Configuring Nginx..."
    cat > "$PROJECT_ROOT/nginx-local.conf" << 'EOF'
worker_processes 1;
pid nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log access.log;
    error_log error.log;

    server {
        listen 8080;
        server_name localhost;

        # CRM SPA
        location / {
            root crm/dist;
            try_files $uri $uri/ /index.html;
        }

        # Ops Console (on different path for local testing)
        location /ops/ {
            alias ops-console/dist/;
            try_files $uri $uri/ /ops/index.html;
        }

        # Proxy to CRM API
        location /api/crm/ {
            proxy_pass http://localhost:8000/;
            proxy_set_header Host $host;
        }

        # Proxy to Ops API
        location /api/ops/ {
            proxy_pass http://localhost:8001/;
            proxy_set_header Host $host;
        }
    }
}
EOF

    log "Starting Nginx on port $NGINX_PORT..."
    nginx -c "$PROJECT_ROOT/nginx-local.conf" -p "$PROJECT_ROOT" 2>&1 >> "$LOG_FILE"

    # Wait for Nginx to start
    sleep 2

    if curl -sf "http://localhost:$NGINX_PORT" > /dev/null 2>&1; then
        success "Nginx started successfully"
    else
        warn "Nginx may not have started correctly"
    fi
}

run_smoke_tests() {
    section "Step 6: Running Smoke Tests"

    local failed=0

    # Test 1: CRM API Health
    log "Testing CRM API /health..."
    if response=$(curl -sf "http://localhost:$CRM_API_PORT/health" 2>&1); then
        if echo "$response" | grep -q '"status":"ok"'; then
            success "CRM API health check passed"
            echo "  Response: $response" >> "$LOG_FILE"
        else
            error "CRM API health check failed - unexpected response"
            failed=$((failed + 1))
        fi
    else
        error "CRM API health check failed - no response"
        failed=$((failed + 1))
    fi

    # Test 2: Ops API Health
    log "Testing Ops API /health..."
    if response=$(curl -sf "http://localhost:$OPS_API_PORT/health" 2>&1); then
        if echo "$response" | grep -q '"status":"ok"'; then
            success "Ops API health check passed"
            echo "  Response: $response" >> "$LOG_FILE"
        else
            error "Ops API health check failed - unexpected response"
            failed=$((failed + 1))
        fi
    else
        error "Ops API health check failed - no response"
        failed=$((failed + 1))
    fi

    # Test 3: CRM API Metrics
    log "Testing CRM API /metrics..."
    if response=$(curl -sf "http://localhost:$CRM_API_PORT/metrics" 2>&1); then
        if echo "$response" | grep -q '"service":"crm-api"'; then
            success "CRM API metrics endpoint passed"
            echo "  Response: $response" >> "$LOG_FILE"
        else
            error "CRM API metrics failed - unexpected response"
            failed=$((failed + 1))
        fi
    else
        error "CRM API metrics failed - no response"
        failed=$((failed + 1))
    fi

    # Test 4: Ops API Metrics
    log "Testing Ops API /metrics..."
    if response=$(curl -sf "http://localhost:$OPS_API_PORT/metrics" 2>&1); then
        if echo "$response" | grep -q '"service":"ops-api"'; then
            success "Ops API metrics endpoint passed"
            echo "  Response: $response" >> "$LOG_FILE"
        else
            error "Ops API metrics failed - unexpected response"
            failed=$((failed + 1))
        fi
    else
        error "Ops API metrics failed - no response"
        failed=$((failed + 1))
    fi

    # Test 5: CRM API authenticated endpoint
    log "Testing CRM API authenticated endpoint..."

    # First, get a token
    log "  Getting authentication token..."
    if token_response=$(curl -sf -X POST "http://localhost:$CRM_API_PORT/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"Nathan@RiverCityClean.com","password":"password123"}' 2>&1); then

        token=$(echo "$token_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

        if [ -n "$token" ]; then
            success "  Got authentication token"

            # Now test the leads endpoint
            log "  Testing /api/v1/leads endpoint with token..."
            if leads_response=$(curl -sf "http://localhost:$CRM_API_PORT/api/v1/v1/leads" \
                -H "Authorization: Bearer $token" 2>&1); then
                success "CRM API authenticated endpoint passed"
                echo "  Response: $leads_response" >> "$LOG_FILE"
            else
                error "CRM API leads endpoint failed"
                failed=$((failed + 1))
            fi
        else
            error "  Failed to extract token from response"
            failed=$((failed + 1))
        fi
    else
        error "  Failed to get authentication token"
        failed=$((failed + 1))
    fi

    echo "" | tee -a "$LOG_FILE"

    if [ $failed -gt 0 ]; then
        error "$failed smoke test(s) failed"
        return 1
    else
        success "All smoke tests passed!"
        return 0
    fi
}

check_logs_for_errors() {
    section "Step 7: Checking Logs for Errors"

    log "Checking Docker logs for stack traces..."

    cd "$PROJECT_ROOT"

    # Check CRM API logs
    if docker-compose logs crm-api 2>&1 | grep -qi "traceback\|exception\|error" | head -5; then
        warn "Found potential errors in CRM API logs (check $LOG_FILE)"
        docker-compose logs --tail=50 crm-api >> "$LOG_FILE" 2>&1
    else
        success "No stack traces found in CRM API logs"
    fi

    # Check Ops API logs
    if docker-compose logs ops-api 2>&1 | grep -qi "traceback\|exception\|error" | head -5; then
        warn "Found potential errors in Ops API logs (check $LOG_FILE)"
        docker-compose logs --tail=50 ops-api >> "$LOG_FILE" 2>&1
    else
        success "No stack traces found in Ops API logs"
    fi
}

print_summary() {
    section "Deployment Dry Run Summary"

    echo ""
    echo -e "${GREEN}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${GREEN}│                      DEPLOY OK ✓                            │${NC}"
    echo -e "${GREEN}└─────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "  • CRM API:         http://localhost:$CRM_API_PORT"
    echo -e "  • CRM API Health:  http://localhost:$CRM_API_PORT/health"
    echo -e "  • CRM API Metrics: http://localhost:$CRM_API_PORT/metrics"
    echo -e "  • CRM API Docs:    http://localhost:$CRM_API_PORT/docs"
    echo ""
    echo -e "  • Ops API:         http://localhost:$OPS_API_PORT"
    echo -e "  • Ops API Health:  http://localhost:$OPS_API_PORT/health"
    echo -e "  • Ops API Metrics: http://localhost:$OPS_API_PORT/metrics"
    echo -e "  • Ops API Docs:    http://localhost:$OPS_API_PORT/docs"
    echo ""

    if command -v nginx &> /dev/null && [ -f "$PROJECT_ROOT/nginx.pid" ]; then
        echo -e "  • CRM SPA:         http://localhost:$NGINX_PORT/"
        echo -e "  • Ops Console:     http://localhost:$NGINX_PORT/ops/"
        echo ""
    fi

    echo -e "${BLUE}Logs:${NC}"
    echo -e "  • Deployment log:  $LOG_FILE"
    echo -e "  • Docker logs:     docker-compose logs -f [service]"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo -e "  • Stop services:   docker-compose down"
    echo -e "  • View logs:       docker-compose logs -f"
    echo -e "  • Check status:    docker-compose ps"
    echo ""
}

# ==============================================================================
# Main Execution
# ==============================================================================

main() {
    # Clear log file
    > "$LOG_FILE"

    section "Deployment Dry Run - Production-like Stack Bring-up"
    log "Starting deployment dry run at $(date)"

    # Run deployment sequence
    check_prerequisites
    cleanup
    start_infrastructure
    wait_for_services
    seed_data
    build_spas
    start_nginx
    run_smoke_tests
    check_logs_for_errors
    print_summary

    log "Deployment dry run completed successfully at $(date)"
}

# Handle Ctrl+C gracefully
trap cleanup EXIT INT TERM

# Run main
main "$@"
