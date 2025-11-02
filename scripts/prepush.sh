#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

set -euo pipefail

#==============================================================================
# Pre-Push Quality Gate Sentinel
#==============================================================================
# Runs all quality checks before pushing code to remote repository
# Ensures code meets all standards: hygiene, types, tests, security, perf
#
# Usage: ./scripts/prepush.sh [OPTIONS]
#
# Options:
#   --no-fail-fast    Continue running all gates even if one fails
#   --skip-tests      Skip test execution (faster, use with caution)
#   --skip-build      Skip build validation (not recommended)
#   --quiet           Minimal output, only show final matrix
#==============================================================================

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL_FAST=true
SKIP_TESTS=false
SKIP_BUILD=false
QUIET=false

# Gate results tracking
declare -A GATE_STATUS
declare -A GATE_DURATION
declare -a GATE_ORDER=(
  "config"
  "secrets"
  "types_crm"
  "types_ops"
  "tests_crm"
  "tests_ops"
  "security"
  "performance"
  "build_crm"
  "build_ops"
)

# Gate metadata
declare -A GATE_NAME=(
  ["config"]="Configuration Validation"
  ["secrets"]="Secrets Scan"
  ["types_crm"]="TypeScript (CRM)"
  ["types_ops"]="TypeScript (Ops)"
  ["tests_crm"]="Unit Tests (CRM)"
  ["tests_ops"]="Unit Tests (Ops)"
  ["security"]="Security Sanity Checks"
  ["performance"]="Performance Smoke Tests"
  ["build_crm"]="Build CRM SPA"
  ["build_ops"]="Build Ops Console SPA"
)

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-fail-fast)
      FAIL_FAST=false
      shift
      ;;
    --skip-tests)
      SKIP_TESTS=true
      shift
      ;;
    --skip-build)
      SKIP_BUILD=true
      shift
      ;;
    --quiet|-q)
      QUIET=true
      shift
      ;;
    --help|-h)
      head -n 22 "$0" | tail -n +3 | sed 's/^# //'
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

#==============================================================================
# Helper Functions
#==============================================================================

log_section() {
  if [[ "$QUIET" == "false" ]]; then
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}${CYAN}$1${RESET}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  fi
}

log_gate() {
  if [[ "$QUIET" == "false" ]]; then
    echo -e "\n${BLUE}▶${RESET} ${BOLD}$1${RESET}"
  fi
}

run_gate() {
  local gate_id="$1"
  local gate_command="$2"
  local gate_name="${GATE_NAME[$gate_id]}"

  log_gate "$gate_name"

  local start_time=$(date +%s)
  local output_file=$(mktemp)

  if [[ "$QUIET" == "false" ]]; then
    # Run with output
    if eval "$gate_command" > "$output_file" 2>&1; then
      GATE_STATUS[$gate_id]="PASS"
      echo -e "${GREEN}✓${RESET} ${gate_name} ${DIM}passed${RESET}"
    else
      GATE_STATUS[$gate_id]="FAIL"
      echo -e "${RED}✗${RESET} ${gate_name} ${DIM}failed${RESET}"
      cat "$output_file"
      rm "$output_file"

      if [[ "$FAIL_FAST" == "true" ]]; then
        echo ""
        echo -e "${RED}${BOLD}Gate failed. Aborting pre-push checks.${RESET}"
        echo "Use --no-fail-fast to continue running all gates."
        exit 1
      fi
      return 1
    fi
  else
    # Quiet mode - suppress output
    if eval "$gate_command" > "$output_file" 2>&1; then
      GATE_STATUS[$gate_id]="PASS"
    else
      GATE_STATUS[$gate_id]="FAIL"
      rm "$output_file"

      if [[ "$FAIL_FAST" == "true" ]]; then
        exit 1
      fi
      return 1
    fi
  fi

  rm "$output_file"

  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  GATE_DURATION[$gate_id]=$duration
}

#==============================================================================
# Pre-Flight Checks
#==============================================================================

log_section "🚦 Pre-Push Quality Gate Sentinel"

if [[ "$QUIET" == "false" ]]; then
  echo "Running comprehensive quality checks before push..."
  echo ""
  echo "Configuration:"
  echo "  Fail Fast:   $([ "$FAIL_FAST" == "true" ] && echo "Enabled" || echo "Disabled")"
  echo "  Skip Tests:  $([ "$SKIP_TESTS" == "true" ] && echo "Yes" || echo "No")"
  echo "  Skip Build:  $([ "$SKIP_BUILD" == "true" ] && echo "Yes" || echo "No")"
fi

#==============================================================================
# Gate 1: Configuration Validation
#==============================================================================

log_section "Gate 1: Configuration Hygiene"

run_gate "config" "$PROJECT_ROOT/scripts/config/check.sh $PROJECT_ROOT/.env.example"

#==============================================================================
# Gate 2: Secrets Scan
#==============================================================================

log_section "Gate 2: Secrets Scan"

# Secrets scan is part of config check, mark as skipped or use grep
GATE_STATUS["secrets"]="SKIP"
GATE_DURATION["secrets"]=0
if [[ "$QUIET" == "false" ]]; then
  echo -e "${YELLOW}⊘${RESET} Secrets Scan ${DIM}(included in config check)${RESET}"
fi

#==============================================================================
# Gate 3: TypeScript Type Checking (CRM)
#==============================================================================

log_section "Gate 3: TypeScript Type Checking"

run_gate "types_crm" "cd $PROJECT_ROOT/crm && npx tsc --noEmit"

#==============================================================================
# Gate 4: TypeScript Type Checking (Ops Console)
#==============================================================================

run_gate "types_ops" "cd $PROJECT_ROOT/ops-console && npx tsc --noEmit"

#==============================================================================
# Gate 5: Unit Tests (CRM)
#==============================================================================

if [[ "$SKIP_TESTS" == "false" ]]; then
  log_section "Gate 5: Unit Tests"

  run_gate "tests_crm" "cd $PROJECT_ROOT/crm && npm test -- --run"
else
  GATE_STATUS["tests_crm"]="SKIP"
  GATE_DURATION["tests_crm"]=0
  if [[ "$QUIET" == "false" ]]; then
    echo -e "${YELLOW}⊘${RESET} Unit Tests (CRM) ${DIM}skipped${RESET}"
  fi
fi

#==============================================================================
# Gate 6: Unit Tests (Ops Console)
#==============================================================================

if [[ "$SKIP_TESTS" == "false" ]]; then
  run_gate "tests_ops" "cd $PROJECT_ROOT/ops-console && npm test -- --run"
else
  GATE_STATUS["tests_ops"]="SKIP"
  GATE_DURATION["tests_ops"]=0
  if [[ "$QUIET" == "false" ]]; then
    echo -e "${YELLOW}⊘${RESET} Unit Tests (Ops Console) ${DIM}skipped${RESET}"
  fi
fi

#==============================================================================
# Gate 7: Security Sanity Checks
#==============================================================================

log_section "Gate 7: Security Sanity Checks"

run_gate "security" "$PROJECT_ROOT/scripts/security/sanity.sh"

#==============================================================================
# Gate 8: Performance Smoke Tests
#==============================================================================

log_section "Gate 8: Performance Smoke Tests"

run_gate "performance" "python3 $PROJECT_ROOT/tools/perf/smoke_stub.py"

#==============================================================================
# Gate 9: Build Validation (CRM)
#==============================================================================

if [[ "$SKIP_BUILD" == "false" ]]; then
  log_section "Gate 9: Build Validation"

  run_gate "build_crm" "cd $PROJECT_ROOT/crm && npm run build"
else
  GATE_STATUS["build_crm"]="SKIP"
  GATE_DURATION["build_crm"]=0
  if [[ "$QUIET" == "false" ]]; then
    echo -e "${YELLOW}⊘${RESET} Build CRM SPA ${DIM}skipped${RESET}"
  fi
fi

#==============================================================================
# Gate 10: Build Validation (Ops Console)
#==============================================================================

if [[ "$SKIP_BUILD" == "false" ]]; then
  run_gate "build_ops" "cd $PROJECT_ROOT/ops-console && npm run build"
else
  GATE_STATUS["build_ops"]="SKIP"
  GATE_DURATION["build_ops"]=0
  if [[ "$QUIET" == "false" ]]; then
    echo -e "${YELLOW}⊘${RESET} Build Ops Console SPA ${DIM}skipped${RESET}"
  fi
fi

#==============================================================================
# Final Results Matrix
#==============================================================================

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${CYAN}                          PRE-PUSH QUALITY GATE MATRIX${RESET}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${RESET}"
echo ""

# Print matrix header
printf "%-40s %-12s %-12s\n" "Gate" "Status" "Duration"
echo "-------------------------------------------------------------------------------"

# Calculate totals
total_gates=0
passed_gates=0
failed_gates=0
skipped_gates=0
total_duration=0

# Print each gate's status
for gate_id in "${GATE_ORDER[@]}"; do
  status="${GATE_STATUS[$gate_id]}"
  duration="${GATE_DURATION[$gate_id]}"
  name="${GATE_NAME[$gate_id]}"

  total_gates=$((total_gates + 1))
  total_duration=$((total_duration + duration))

  # Format status with color
  case "$status" in
    "PASS")
      status_display="${GREEN}✓ PASS${RESET}"
      passed_gates=$((passed_gates + 1))
      ;;
    "FAIL")
      status_display="${RED}✗ FAIL${RESET}"
      failed_gates=$((failed_gates + 1))
      ;;
    "SKIP")
      status_display="${YELLOW}⊘ SKIP${RESET}"
      skipped_gates=$((skipped_gates + 1))
      ;;
    *)
      status_display="${DIM}? UNKNOWN${RESET}"
      ;;
  esac

  # Format duration
  if [[ "$duration" -eq 0 ]]; then
    duration_display="${DIM}--${RESET}"
  else
    duration_display="${duration}s"
  fi

  printf "%-40s %-22s %-12s\n" "$name" "$status_display" "$duration_display"
done

echo "-------------------------------------------------------------------------------"
printf "%-40s ${BOLD}%d passed${RESET}, ${RED}%d failed${RESET}, ${YELLOW}%d skipped${RESET}\n" \
  "Summary:" "$passed_gates" "$failed_gates" "$skipped_gates"
printf "%-40s ${BOLD}%ds${RESET}\n" "Total Duration:" "$total_duration"

echo ""

#==============================================================================
# Final Verdict
#==============================================================================

if [[ "$failed_gates" -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════════════════${RESET}"
  echo -e "${GREEN}${BOLD}                         ✓ ALL QUALITY GATES PASSED${RESET}"
  echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════════════════${RESET}"
  echo ""
  echo -e "${GREEN}Your code is ready to push!${RESET}"
  echo ""

  # Get current branch and check for VERSION file
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  current_commit=$(git rev-parse --short HEAD)

  if [[ -f "VERSION" ]]; then
    version=$(cat VERSION | tr -d '\n' | tr -d ' ')
    tag_exists=$(git tag -l "v$version")

    echo -e "${BOLD}Recommended Git Commands:${RESET}"
    echo ""

    if [[ -z "$tag_exists" ]]; then
      echo -e "${CYAN}# Create version tag:${RESET}"
      echo -e "  git tag -a v${version} -m \"Release v${version}\""
      echo ""
    fi

    echo -e "${CYAN}# Push to remote:${RESET}"
    echo -e "  git push -u origin $current_branch"
    echo ""

    if [[ -z "$tag_exists" ]]; then
      echo -e "${CYAN}# Push tags:${RESET}"
      echo -e "  git push origin --tags"
      echo ""
    fi
  else
    echo -e "${BOLD}Recommended Git Commands:${RESET}"
    echo ""
    echo -e "${CYAN}# Push to remote:${RESET}"
    echo -e "  git push -u origin $current_branch"
    echo ""
  fi

  echo -e "${DIM}All quality gates passed. Your code meets the Definition of Done.${RESET}"
  echo ""

  exit 0
else
  echo -e "${RED}${BOLD}═══════════════════════════════════════════════════════════════════════════════${RESET}"
  echo -e "${RED}${BOLD}                         ✗ QUALITY GATES FAILED${RESET}"
  echo -e "${RED}${BOLD}═══════════════════════════════════════════════════════════════════════════════${RESET}"
  echo ""
  echo -e "${RED}${failed_gates} gate(s) failed. Please fix the issues before pushing.${RESET}"
  echo ""
  echo -e "${BOLD}Next Steps:${RESET}"
  echo "  1. Review the failed gate output above"
  echo "  2. Fix the identified issues"
  echo "  3. Run ./scripts/prepush.sh again"
  echo "  4. Once all gates pass, push your code"
  echo ""
  echo -e "${DIM}See POLICY.md for Definition of Done and quality standards.${RESET}"
  echo ""

  exit 1
fi
