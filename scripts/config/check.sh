#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

# ==============================================================================
# Configuration Security Check
# ==============================================================================
# Unified runner for configuration validation and secrets scanning.
# Runs sanity.py for env validation + grep-based secret detection.
# ==============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Track results
SANITY_PASSED=0
SECRETS_PASSED=0

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Configuration Security Check${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

# ------------------------------------------------------------------------------
# 1. Environment Configuration Sanity Check
# ------------------------------------------------------------------------------
echo -e "${BLUE}[1/2] Running environment configuration validation...${NC}"
echo ""

ENV_FILE="${1:-$PROJECT_ROOT/.env}"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠ .env file not found, checking .env.example instead${NC}"
    ENV_FILE="$PROJECT_ROOT/.env.example"
fi

# Run Python sanity checker
if python3 "$PROJECT_ROOT/tools/config/sanity.py" "$ENV_FILE"; then
    SANITY_PASSED=1
else
    SANITY_PASSED=0
fi

echo ""
echo ""

# ------------------------------------------------------------------------------
# 2. Secrets Scan
# ------------------------------------------------------------------------------
echo -e "${BLUE}[2/2] Running secrets pattern scan...${NC}"
echo ""

# Find all relevant files (exclude node_modules, .git, dist, test fixtures, etc.)
FILES_TO_SCAN=$(find "$PROJECT_ROOT" \
    -type f \
    \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" \
       -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.sh" -o -name ".env" \) \
    ! -path "*/node_modules/*" \
    ! -path "*/.git/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.venv/*" \
    ! -path "*/venv/*" \
    ! -name ".env.example" \
    ! -path "*/tools/config/sanity.py" \
    ! -path "*/tools/dlp/scan.py" \
    ! -path "*/scripts/config/*.sh" \
    ! -path "*/tests/*" \
    ! -path "*/__tests__/*" \
    2>/dev/null || true)

if [ -z "$FILES_TO_SCAN" ]; then
    echo -e "${YELLOW}⚠ No files found to scan${NC}"
    SECRETS_PASSED=1
else
    # Count files
    FILE_COUNT=$(echo "$FILES_TO_SCAN" | wc -l)
    echo "Scanning $FILE_COUNT files for hardcoded secrets..."
    echo ""

    # Run secret scanner
    if echo "$FILES_TO_SCAN" | xargs "$SCRIPT_DIR/secret_patterns.sh"; then
        echo -e "${GREEN}✓ No secrets detected${NC}"
        SECRETS_PASSED=1
    else
        SECRETS_PASSED=0
    fi
fi

echo ""
echo ""

# ------------------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------------------
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

if [ $SANITY_PASSED -eq 1 ]; then
    echo -e "${GREEN}✓ Environment configuration validation: PASSED${NC}"
else
    echo -e "${RED}✗ Environment configuration validation: FAILED${NC}"
fi

if [ $SECRETS_PASSED -eq 1 ]; then
    echo -e "${GREEN}✓ Secrets pattern scan: PASSED${NC}"
else
    echo -e "${RED}✗ Secrets pattern scan: FAILED${NC}"
fi

echo ""

if [ $SANITY_PASSED -eq 1 ] && [ $SECRETS_PASSED -eq 1 ]; then
    echo -e "${GREEN}=====================================================================${NC}"
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}=====================================================================${NC}"
    echo ""
    echo "Configuration is ready for deployment."
    exit 0
else
    echo -e "${RED}=====================================================================${NC}"
    echo -e "${RED}✗ CHECKS FAILED${NC}"
    echo -e "${RED}=====================================================================${NC}"
    echo ""
    echo "Please fix the issues above before deploying to production."
    exit 1
fi
