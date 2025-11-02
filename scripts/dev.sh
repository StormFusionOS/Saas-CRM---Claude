#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

# ==============================================================================
# Development Environment Startup Script
# ==============================================================================
# Brings up all services needed for local development:
# - Docker Compose (PostgreSQL + Redis)
# - CRM API (port 8000)
# - Ops API (port 8001)
# - CRM Frontend (port 5173)
# - Ops Console (port 5174)
#
# Usage:
#   ./scripts/dev.sh          # Start all services
#   ./scripts/dev.sh --stop   # Stop all services
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i:$1 >/dev/null 2>&1
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."

    # Stop Docker Compose
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        print_success "Docker services stopped"
    fi

    # Kill running processes on known ports
    for port in 8000 8001 5173 5174; do
        if port_in_use $port; then
            print_status "Killing process on port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done

    print_success "All services stopped"
    exit 0
}

# Handle --stop flag
if [ "$1" == "--stop" ]; then
    stop_services
fi

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

print_status "Running pre-flight checks..."

# Check for required commands
MISSING_DEPS=false

if ! command_exists docker; then
    print_error "Docker not found. Please install Docker."
    MISSING_DEPS=true
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose not found. Please install Docker Compose."
    MISSING_DEPS=true
fi

if ! command_exists python; then
    print_error "Python not found. Please install Python 3.11+."
    MISSING_DEPS=true
fi

if ! command_exists node; then
    print_error "Node.js not found. Please install Node.js 18+."
    MISSING_DEPS=true
fi

if [ "$MISSING_DEPS" = true ]; then
    print_error "Missing required dependencies. Please install them and try again."
    exit 1
fi

print_success "All required dependencies found"

# Check for .env file
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Copying from .env.example..."
    cp .env.example .env
    print_success "Created .env file"
fi

# ==============================================================================
# Start Docker Services
# ==============================================================================

print_status "Starting Docker services (PostgreSQL + Redis)..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for databases to be ready..."
sleep 5

# Check if databases are up
if docker-compose ps | grep -q "crm-db.*Up"; then
    print_success "CRM database ready"
else
    print_error "CRM database failed to start"
fi

if docker-compose ps | grep -q "ops-db.*Up"; then
    print_success "Ops database ready"
else
    print_error "Ops database failed to start"
fi

if docker-compose ps | grep -q "redis.*Up"; then
    print_success "Redis ready"
else
    print_error "Redis failed to start"
fi

# ==============================================================================
# Install Dependencies (if needed)
# ==============================================================================

print_status "Checking dependencies..."

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    print_warning "pytest not found. Installing..."
    pip install -q pytest pytest-cov
fi

# ==============================================================================
# Start Backend APIs
# ==============================================================================

print_status "Starting backend APIs..."

# Start CRM API in background
print_status "Starting CRM API on http://localhost:8000..."
cd "$ROOT_DIR/crm_api"
PYTHONPATH="$ROOT_DIR:$PYTHONPATH" python -m app.main > ../logs/crm-api.log 2>&1 &
CRM_API_PID=$!
print_success "CRM API started (PID: $CRM_API_PID)"

# Start Ops API in background
print_status "Starting Ops API on http://localhost:8001..."
cd "$ROOT_DIR/ops_api"
PYTHONPATH="$ROOT_DIR:$PYTHONPATH" python -m app.main > ../logs/ops-api.log 2>&1 &
OPS_API_PID=$!
print_success "Ops API started (PID: $OPS_API_PID)"

cd "$ROOT_DIR"

# ==============================================================================
# Start Frontend SPAs
# ==============================================================================

print_status "Starting frontend SPAs..."

# Create logs directory
mkdir -p logs

# CRM Frontend
print_status "Starting CRM frontend on http://localhost:5173..."
cd "$ROOT_DIR/crm"
if [ ! -d "node_modules" ]; then
    print_warning "Installing CRM frontend dependencies..."
    npm install --silent
fi
npm run dev > ../logs/crm-frontend.log 2>&1 &
CRM_FRONTEND_PID=$!
print_success "CRM frontend started (PID: $CRM_FRONTEND_PID)"

# Ops Console
print_status "Starting Ops Console on http://localhost:5174..."
cd "$ROOT_DIR/ops-console"
if [ ! -d "node_modules" ]; then
    print_warning "Installing Ops Console dependencies..."
    npm install --silent
fi
npm run dev > ../logs/ops-console.log 2>&1 &
OPS_CONSOLE_PID=$!
print_success "Ops Console started (PID: $OPS_CONSOLE_PID)"

cd "$ROOT_DIR"

# ==============================================================================
# Summary
# ==============================================================================

echo ""
print_success "====================================================================="
print_success "  Development Environment Ready!"
print_success "====================================================================="
echo ""
echo "  Services:"
echo "    CRM API:         http://localhost:8000"
echo "    CRM API Health:  http://localhost:8000/health"
echo "    Ops API:         http://localhost:8001"
echo "    Ops API Health:  http://localhost:8001/health"
echo ""
echo "  Frontends:"
echo "    CRM Frontend:    http://localhost:5173"
echo "    Ops Console:     http://localhost:5174"
echo ""
echo "  Databases:"
echo "    CRM PostgreSQL:  localhost:5433"
echo "    Ops PostgreSQL:  localhost:5434"
echo "    Redis:           localhost:6379"
echo ""
echo "  Demo Credentials:"
echo "    Email:    Nathan@RiverCityClean.com"
echo "    Password: password123"
echo ""
echo "  Logs:"
echo "    API logs:   ./logs/*.log"
echo "    Frontend:   Check terminal output"
echo ""
print_warning "  To stop all services:"
print_warning "    ./scripts/dev.sh --stop"
echo ""
print_warning "  Note: Frontends may take 10-20 seconds to be ready"
echo ""

# Save PIDs for cleanup
echo "$CRM_API_PID $OPS_API_PID $CRM_FRONTEND_PID $OPS_CONSOLE_PID" > .dev-pids

print_success "Done! Press Ctrl+C to view logs or run with --stop to shut down."
