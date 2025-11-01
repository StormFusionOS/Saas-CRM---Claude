#!/usr/bin/env bash
# ==============================================================================
# Comprehensive Checks Script
# ==============================================================================
# Runs all quality checks:
# - Linting (Python, TypeScript)
# - Type checking (TypeScript)
# - Unit tests with coverage (Python, Node)
# - Schema drift checks
#
# Usage:
#   ./scripts/checks.sh           # Run all checks
#   ./scripts/checks.sh --fast    # Skip slow checks
# ==============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Print functions
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
}

print_check() {
    echo -e "${YELLOW}▸${NC} $1"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

# Fast mode flag
FAST_MODE=false
if [ "$1" == "--fast" ]; then
    FAST_MODE=true
    echo -e "${YELLOW}Running in FAST mode (skipping some checks)${NC}"
fi

# ==============================================================================
# 1. Python Backend Tests
# ==============================================================================

print_header "Python Backend Tests & Coverage"

# CRM API Tests
print_check "Running CRM API tests with coverage..."
cd "$ROOT_DIR/crm_api"
if python -m pytest tests/ --cov=app --cov-report=term --cov-report=html -q > /tmp/crm-test-output.txt 2>&1; then
    # Extract coverage percentage
    COVERAGE=$(grep -oP 'TOTAL\s+\d+\s+\d+\s+\K\d+' /tmp/crm-test-output.txt || echo "0")
    if [ "$COVERAGE" -ge 80 ]; then
        print_success "CRM API: All tests passed with ${COVERAGE}% coverage (≥80% required)"
    else
        print_error "CRM API: Coverage ${COVERAGE}% is below 80% threshold"
    fi
else
    print_error "CRM API: Some tests failed"
    cat /tmp/crm-test-output.txt
fi

# Ops API Tests
print_check "Running Ops API tests with coverage..."
cd "$ROOT_DIR/ops_api"
if python -m pytest tests/ --cov=app --cov-report=term --cov-report=html -q > /tmp/ops-test-output.txt 2>&1; then
    COVERAGE=$(grep -oP 'TOTAL\s+\d+\s+\d+\s+\K\d+' /tmp/ops-test-output.txt || echo "0")
    if [ "$COVERAGE" -ge 80 ]; then
        print_success "Ops API: All tests passed with ${COVERAGE}% coverage (≥80% required)"
    else
        print_error "Ops API: Coverage ${COVERAGE}% is below 80% threshold"
    fi
else
    print_error "Ops API: Some tests failed"
    cat /tmp/ops-test-output.txt
fi

cd "$ROOT_DIR"

# ==============================================================================
# 2. Schema Drift Checks
# ==============================================================================

print_header "Database Schema Checks"

print_check "Checking for migration drift..."
if python tools/check_migrations.py > /tmp/migration-check.txt 2>&1; then
    print_success "Migration checks passed"
else
    print_error "Migration checks failed"
    cat /tmp/migration-check.txt
fi

# ==============================================================================
# 3. Frontend Checks
# ==============================================================================

if [ "$FAST_MODE" = false ]; then
    print_header "Frontend Tests & Type Checking"

    # CRM Frontend
    print_check "Running CRM frontend checks..."
    cd "$ROOT_DIR/crm"

    if [ ! -d "node_modules" ]; then
        echo "  Installing dependencies..."
        npm install --silent
    fi

    # Type checking
    if npx tsc --noEmit > /tmp/crm-typecheck.txt 2>&1; then
        print_success "CRM: TypeScript type check passed"
    else
        print_error "CRM: TypeScript type check failed"
        cat /tmp/crm-typecheck.txt | head -20
    fi

    # Tests
    if npm run test -- --run > /tmp/crm-test.txt 2>&1; then
        print_success "CRM: Frontend tests passed"
    else
        print_error "CRM: Frontend tests failed"
        cat /tmp/crm-test.txt | tail -20
    fi

    # Build check
    if npm run build > /tmp/crm-build.txt 2>&1; then
        print_success "CRM: Production build succeeded"
    else
        print_error "CRM: Production build failed"
        cat /tmp/crm-build.txt | tail -20
    fi

    # Ops Console
    print_check "Running Ops Console checks..."
    cd "$ROOT_DIR/ops-console"

    if [ ! -d "node_modules" ]; then
        echo "  Installing dependencies..."
        npm install --silent
    fi

    # Type checking
    if npx tsc --noEmit > /tmp/ops-typecheck.txt 2>&1; then
        print_success "Ops Console: TypeScript type check passed"
    else
        print_error "Ops Console: TypeScript type check failed"
        cat /tmp/ops-typecheck.txt | head -20
    fi

    # Tests
    if npm run test -- --run > /tmp/ops-test.txt 2>&1; then
        print_success "Ops Console: Frontend tests passed"
    else
        print_error "Ops Console: Frontend tests failed"
        cat /tmp/ops-test.txt | tail -20
    fi

    # Build check
    if npm run build > /tmp/ops-build.txt 2>&1; then
        print_success "Ops Console: Production build succeeded"
    else
        print_error "Ops Console: Production build failed"
        cat /tmp/ops-build.txt | tail -20
    fi

    cd "$ROOT_DIR"
else
    echo ""
    echo -e "${YELLOW}Skipping frontend checks (fast mode)${NC}"
fi

# ==============================================================================
# 4. Security Checks
# ==============================================================================

print_header "Security Checks"

print_check "Running security hardening tests..."
cd "$ROOT_DIR/ops_api"
if python -m pytest tests/test_hardening_script.py -q > /tmp/hardening-test.txt 2>&1; then
    print_success "Nginx hardening checks passed"
else
    print_error "Nginx hardening checks failed"
    cat /tmp/hardening-test.txt
fi

print_check "Running cross-role security tests..."
cd "$ROOT_DIR/crm_api"
if python -m pytest tests/test_cross_role_security.py -q > /tmp/crm-security.txt 2>&1; then
    print_success "CRM cross-role security tests passed"
else
    print_error "CRM cross-role security tests failed"
    cat /tmp/crm-security.txt
fi

cd "$ROOT_DIR/ops_api"
if python -m pytest tests/test_cross_role_security.py -q > /tmp/ops-security.txt 2>&1; then
    print_success "Ops cross-role security tests passed"
else
    print_error "Ops cross-role security tests failed"
    cat /tmp/ops-security.txt
fi

cd "$ROOT_DIR"

# ==============================================================================
# Summary
# ==============================================================================

print_header "Check Summary"

echo ""
echo "  Total checks run: $TOTAL_CHECKS"
echo -e "  ${GREEN}Passed: $PASSED_CHECKS${NC}"
if [ "$FAILED_CHECKS" -gt 0 ]; then
    echo -e "  ${RED}Failed: $FAILED_CHECKS${NC}"
fi
echo ""

if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ SOME CHECKS FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
