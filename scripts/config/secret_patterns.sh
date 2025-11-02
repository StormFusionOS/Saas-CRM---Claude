#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

# ==============================================================================
# Secret Pattern Scanner
# ==============================================================================
# Scans files for common secret patterns using grep.
# Used by pre-commit hooks to prevent accidental secret commits.
# ==============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit code
EXIT_CODE=0

# Secret patterns to detect
declare -a PATTERNS=(
    # AWS credentials
    "AKIA[0-9A-Z]{16}"
    "aws_access_key_id.*=.*[A-Z0-9]{20}"
    "aws_secret_access_key.*=.*[A-Za-z0-9/+=]{40}"

    # Private keys
    "-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY"
    "-----BEGIN PRIVATE KEY-----"

    # API keys and tokens (common formats)
    "['\"]?api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-]{32,}['\"]"
    "['\"]?api[_-]?secret['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-]{32,}['\"]"
    "['\"]?access[_-]?token['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-]{32,}['\"]"
    "['\"]?secret[_-]?token['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-]{32,}['\"]"

    # GitHub tokens
    "ghp_[a-zA-Z0-9]{36}"
    "gho_[a-zA-Z0-9]{36}"
    "ghu_[a-zA-Z0-9]{36}"
    "ghs_[a-zA-Z0-9]{36}"
    "ghr_[a-zA-Z0-9]{36}"

    # Slack tokens
    "xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}"

    # Stripe keys
    "sk_live_[a-zA-Z0-9]{24,}"
    "pk_live_[a-zA-Z0-9]{24,}"

    # Google API keys
    "AIza[0-9A-Za-z\\-_]{35}"

    # JWT tokens (full tokens, not just the word)
    "eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"

    # Generic base64 secrets (64+ chars)
    "['\"]?secret['\"]?\s*[:=]\s*['\"][A-Za-z0-9+/=]{64,}['\"]"
    "['\"]?password['\"]?\s*[:=]\s*['\"][A-Za-z0-9+/=]{64,}['\"]"

    # Database connection strings with embedded passwords
    "postgresql://[^:]+:[^@]{8,}@"
    "mysql://[^:]+:[^@]{8,}@"
    "mongodb://[^:]+:[^@]{8,}@"
)

# Scan all provided files
for file in "$@"; do
    # Skip if file doesn't exist
    [[ ! -f "$file" ]] && continue

    # Check each pattern
    for pattern in "${PATTERNS[@]}"; do
        # Use grep with Perl-compatible regex
        if grep -E -n -H "$pattern" "$file" 2>/dev/null; then
            echo -e "${RED}✗ Potential secret detected in $file${NC}"
            echo -e "${YELLOW}  Pattern: $pattern${NC}"
            EXIT_CODE=1
        fi
    done
done

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}=====================================================================${NC}"
    echo -e "${RED}BLOCKED: Potential secrets detected in staged files${NC}"
    echo -e "${RED}=====================================================================${NC}"
    echo ""
    echo "If this is a false positive, you can:"
    echo "  1. Update the pattern in scripts/config/secret_patterns.sh"
    echo "  2. Add the file to the exclude list in .pre-commit-config.yaml"
    echo "  3. Use environment variables instead of hardcoded secrets"
    echo ""
fi

exit $EXIT_CODE
