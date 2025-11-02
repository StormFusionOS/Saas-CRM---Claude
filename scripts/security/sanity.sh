#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

# ==============================================================================
# Security Sanity Checks
# ==============================================================================
# Quick, high-signal security tests for:
# - Token validation (valid/expired/wrong audience)
# - Cross-realm access control (CRM ↔ Ops isolation)
# - Webhook signature validation (Facebook, Twilio, Google)
# - Nginx security headers and origin pinning
# ==============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TESTS_DIR="$PROJECT_ROOT/tests/security"

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_SUITES=0
PASSED_SUITES=0

# Test results by category
declare -A CATEGORY_TESTS
declare -A CATEGORY_PASSED

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}SECURITY SANITY CHECKS${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""
echo -e "${CYAN}Running quick, high-signal security tests...${NC}"
echo ""

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

run_test_suite() {
    local suite_name="$1"
    local test_script="$2"
    local category="$3"

    echo -e "${BLUE}[$((TOTAL_SUITES + 1))/4] ${suite_name}${NC}"
    echo ""

    TOTAL_SUITES=$((TOTAL_SUITES + 1))

    if [ ! -f "$test_script" ]; then
        echo -e "${RED}✗ Test script not found: $test_script${NC}"
        echo ""
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi

    # Run test script and capture output
    if output=$(python3 "$test_script" 2>&1); then
        echo "$output"
        echo ""

        # Extract test counts from output
        if [[ $output =~ Results:\ ([0-9]+)\ passed,\ ([0-9]+)\ failed ]]; then
            local passed="${BASH_REMATCH[1]}"
            local failed="${BASH_REMATCH[2]}"
            local suite_total=$((passed + failed))

            TOTAL_TESTS=$((TOTAL_TESTS + suite_total))
            PASSED_TESTS=$((PASSED_TESTS + passed))
            FAILED_TESTS=$((FAILED_TESTS + failed))

            # Track by category
            CATEGORY_TESTS["$category"]=$((${CATEGORY_TESTS["$category"]:-0} + suite_total))
            CATEGORY_PASSED["$category"]=$((${CATEGORY_PASSED["$category"]:-0} + passed))

            if [ "$failed" -eq 0 ]; then
                PASSED_SUITES=$((PASSED_SUITES + 1))
                echo -e "${GREEN}✅ Suite passed: $passed/$suite_total tests${NC}"
            else
                echo -e "${RED}❌ Suite failed: $passed/$suite_total tests passed${NC}"
            fi
        fi
        echo ""
        return 0
    else
        echo "$output"
        echo ""
        echo -e "${RED}❌ Suite failed with errors${NC}"
        echo ""

        # Count as failures if we can extract counts
        if [[ $output =~ Results:\ ([0-9]+)\ passed,\ ([0-9]+)\ failed ]]; then
            local passed="${BASH_REMATCH[1]}"
            local failed="${BASH_REMATCH[2]}"
            local suite_total=$((passed + failed))

            TOTAL_TESTS=$((TOTAL_TESTS + suite_total))
            PASSED_TESTS=$((PASSED_TESTS + passed))
            FAILED_TESTS=$((FAILED_TESTS + failed))

            CATEGORY_TESTS["$category"]=$((${CATEGORY_TESTS["$category"]:-0} + suite_total))
            CATEGORY_PASSED["$category"]=$((${CATEGORY_PASSED["$category"]:-0} + passed))
        else
            # Count entire suite as 1 failure if no detailed output
            TOTAL_TESTS=$((TOTAL_TESTS + 1))
            FAILED_TESTS=$((FAILED_TESTS + 1))
            CATEGORY_TESTS["$category"]=$((${CATEGORY_TESTS["$category"]:-0} + 1))
        fi

        return 1
    fi
}

# ------------------------------------------------------------------------------
# Run Test Suites
# ------------------------------------------------------------------------------

run_test_suite \
    "Token Validation Tests" \
    "$TESTS_DIR/test_tokens.py" \
    "Authentication"

run_test_suite \
    "Cross-Realm Access Control" \
    "$TESTS_DIR/test_cross_realm.py" \
    "Authorization"

run_test_suite \
    "Webhook Signature Validation" \
    "$TESTS_DIR/test_webhooks.py" \
    "Webhooks"

run_test_suite \
    "Nginx Security Configuration" \
    "$TESTS_DIR/test_nginx_config.py" \
    "Infrastructure"

# ------------------------------------------------------------------------------
# Summary Report
# ------------------------------------------------------------------------------

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}SECURITY OK REPORT${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

# Overall stats
echo -e "${CYAN}Overall Test Results:${NC}"
echo -e "  Total Tests: $TOTAL_TESTS"
echo -e "  Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "  Failed: ${RED}$FAILED_TESTS${NC}"
echo -e "  Success Rate: $((TOTAL_TESTS > 0 ? PASSED_TESTS * 100 / TOTAL_TESTS : 0))%"
echo ""

# Suite stats
echo -e "${CYAN}Test Suite Results:${NC}"
echo -e "  Total Suites: $TOTAL_SUITES"
echo -e "  Passed: ${GREEN}$PASSED_SUITES${NC}"
echo -e "  Failed: ${RED}$((TOTAL_SUITES - PASSED_SUITES))${NC}"
echo ""

# Category breakdown
echo -e "${CYAN}Results by Category:${NC}"
for category in "Authentication" "Authorization" "Webhooks" "Infrastructure"; do
    if [ -n "${CATEGORY_TESTS[$category]}" ]; then
        total="${CATEGORY_TESTS[$category]}"
        passed="${CATEGORY_PASSED[$category]}"
        failed=$((total - passed))
        status="${GREEN}✓${NC}"
        if [ "$failed" -gt 0 ]; then
            status="${RED}✗${NC}"
        fi
        echo -e "  $status $category: $passed/$total passed"
    fi
done
echo ""

# Security domains covered
echo -e "${CYAN}Security Domains Tested:${NC}"
echo -e "  ✓ Access Tokens (valid/expired/wrong audience)"
echo -e "  ✓ Refresh Token Flow"
echo -e "  ✓ Cross-Realm Isolation (CRM ↔ Ops)"
echo -e "  ✓ Role Separation and RBAC"
echo -e "  ✓ Webhook Signatures (Facebook, Twilio, Google)"
echo -e "  ✓ Timestamp Validation and Replay Protection"
echo -e "  ✓ Security Headers (X-Frame-Options, HSTS, CSP, etc.)"
echo -e "  ✓ Origin Pinning for API Routes"
echo -e "  ✓ Rate Limiting Configuration"
echo ""

# Final verdict
if [ "$FAILED_TESTS" -eq 0 ]; then
    echo -e "${GREEN}=====================================================================${NC}"
    echo -e "${GREEN}✅ SECURITY OK - ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}=====================================================================${NC}"
    echo ""
    echo -e "${GREEN}All $TOTAL_TESTS security checks passed successfully.${NC}"
    echo -e "${GREEN}System is ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}=====================================================================${NC}"
    echo -e "${RED}❌ SECURITY ISSUES DETECTED${NC}"
    echo -e "${RED}=====================================================================${NC}"
    echo ""
    echo -e "${RED}$FAILED_TESTS of $TOTAL_TESTS security checks failed.${NC}"
    echo -e "${RED}Please review and fix issues before deploying to production.${NC}"
    exit 1
fi
