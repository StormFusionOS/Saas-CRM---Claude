#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

# ==============================================================================
# ENTERPRISE ORCHESTRATION SCRIPT
# ==============================================================================
# Purpose: Execute domain prompts for enterprise readiness validation
# Owner: Enterprise Program Lead (Bot)
# Last Updated: 2025-11-01
#
# Usage:
#   ./scripts/enterprise/run_all.sh                    # Show menu
#   ./scripts/enterprise/run_all.sh --all              # Run all prompts sequentially
#   ./scripts/enterprise/run_all.sh --prompt=1         # Run specific prompt
#   ./scripts/enterprise/run_all.sh --phase=1          # Run specific phase
#   ./scripts/enterprise/run_all.sh --status           # Show dashboard
# ==============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Directories
ENTERPRISE_DIR="docs/enterprise"
OUTPUT_DIR="$ENTERPRISE_DIR/reports"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Output files
ORCHESTRATION_FILE="$ENTERPRISE_DIR/ORCHESTRATION.md"
RISKS_FILE="$ENTERPRISE_DIR/risks.md"
CONTROLS_FILE="$ENTERPRISE_DIR/controls-map.md"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${MAGENTA}${BOLD}▶ $1${NC}"
    echo -e "${MAGENTA}────────────────────────────────────────${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# ==============================================================================
# EXECUTION SEQUENCE
# ==============================================================================

show_execution_order() {
    print_header "ENTERPRISE PROMPTS EXECUTION ORDER"

    echo -e "${BOLD}Phase 1: Foundation (Sequential)${NC}"
    echo "  8. Secrets Management & Rotation"
    echo "  1. Security & Compliance Audit"
    echo ""

    echo -e "${BOLD}Phase 2: Infrastructure (Parallel)${NC}"
    echo "  4. Infrastructure as Code Review"
    echo "  6. Database Migration & Schema Validation"
    echo ""

    echo -e "${BOLD}Phase 3: Operational Readiness (Parallel)${NC}"
    echo "  3. Disaster Recovery & Backup Validation"
    echo "  7. Monitoring & Observability Setup"
    echo "  5. API Documentation & OpenAPI Spec"
    echo ""

    echo -e "${BOLD}Phase 4: Performance Validation (Final)${NC}"
    echo "  2. Performance & Load Testing"
    echo ""

    echo -e "${CYAN}Output Location:${NC} $OUTPUT_DIR/"
    echo ""
}

# ==============================================================================
# PROMPT EXECUTION FUNCTIONS
# ==============================================================================

run_prompt_1() {
    local output_file="$OUTPUT_DIR/security-audit.md"
    print_section "PROMPT 1: Security & Compliance Audit"

    print_info "Executing security validation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Security & Compliance Audit Report

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

This prompt must be executed manually by providing the following instructions to Claude:

```
You are a security auditor. Conduct a comprehensive security audit of the RiverCityClean
SaaS monorepo covering:

1. JWT token security validation (secret strength, expiration, algorithm)
2. RBAC enforcement across all endpoints
3. Input validation and SQL injection prevention
4. Secrets management (scan git history, verify no hardcoded credentials)
5. Dependency vulnerability scanning (pip-audit, npm audit)
6. CORS and origin enforcement validation
7. Nginx security headers verification
8. Webhook signature verification

Produce a report with:
- ✅ Passes
- ❌ Failures with severity (Critical/High/Medium/Low)
- ⚠️ Warnings with recommendations
- Risk scores and mitigation strategies
- Checklist of remediation actions
- Commands to verify fixes

Guardrails:
- Offline only; keep stubs
- Do not weaken existing security gates
- Small surgical diffs only

Output to: docs/enterprise/reports/security-audit.md
```

## Checklist
- [ ] Execute security audit prompt
- [ ] Review findings
- [ ] Prioritize critical/high severity issues
- [ ] Create remediation plan
- [ ] Update risk register (risks.md)

## Commands
```bash
# Run dependency audits
cd crm_api && pip install pip-audit && pip-audit
cd ops_api && pip install pip-audit && pip-audit
cd crm && npm audit
cd ops-console && npm audit

# Run security tests
cd crm_api && pytest tests/test_cross_role_security.py -v
cd ops_api && pytest tests/test_cross_role_security.py -v
cd ops_api && pytest tests/test_hardening_script.py -v

# Scan for secrets (requires git-secrets)
# git secrets --scan-history
```
EOF

    print_success "Prompt 1 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_2() {
    local output_file="$OUTPUT_DIR/performance-report.md"
    print_section "PROMPT 2: Performance & Load Testing"

    print_info "Executing performance validation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Performance & Load Testing Report

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

This prompt must be executed manually:

```
You are a performance engineer. Conduct load testing and performance validation for
the RiverCityClean SaaS monorepo:

1. Establish API endpoint response time baselines (p50, p95, p99)
2. Analyze database query performance (slow query log)
3. Measure frontend bundle size and initial load time
4. Simulate concurrent users (100, 500, 1000 users using locust or similar)
5. Profile memory and CPU usage under load
6. Validate rate limiting behavior under stress
7. Test cache hit ratios (if Redis used)
8. Identify bottlenecks and optimization opportunities

Acceptance criteria:
- API p95 latency < 200ms under normal load
- API p99 latency < 500ms under normal load
- System stable under 2x expected peak load
- Frontend initial load < 3 seconds
- No memory leaks detected

Output performance report with metrics, graphs, bottlenecks, and optimization
recommendations.

Guardrails:
- Use stub databases for testing
- Keep small surgical diffs
- Document load test scripts for future use

Output to: docs/enterprise/reports/performance-report.md
```

## Checklist
- [ ] Install load testing tools (locust, k6, or artillery)
- [ ] Define load test scenarios
- [ ] Execute baseline tests
- [ ] Execute stress tests (2x capacity)
- [ ] Profile memory/CPU
- [ ] Document bottlenecks
- [ ] Create optimization plan

## Commands
```bash
# Example with locust (install first)
# pip install locust
# locust -f load_tests/locustfile.py --host=http://localhost:8000

# Monitor during load test
# docker stats
# htop

# Query profiling
# Enable slow query log in PostgreSQL
# Review query plans with EXPLAIN ANALYZE
```
EOF

    print_success "Prompt 2 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_3() {
    local output_file="$OUTPUT_DIR/dr-plan.md"
    print_section "PROMPT 3: Disaster Recovery & Backup Validation"

    print_info "Executing DR validation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Disaster Recovery & Backup Validation Report

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

```
You are a DevOps engineer specializing in disaster recovery. Create and validate
DR procedures for RiverCityClean SaaS:

1. Design automated backup strategy (daily, weekly, monthly)
2. Create backup scripts for PostgreSQL databases (CRM + Ops)
3. Implement backup restoration procedures
4. Define and test RTO (Recovery Time Objective) < 4 hours
5. Define and test RPO (Recovery Point Objective) < 15 minutes
6. Test failover scenarios (database, API)
7. Validate data integrity post-restore
8. Document off-site backup strategy

Deliverables:
- Automated backup scripts (scripts/backup/)
- Restoration runbook
- DR test results
- RTO/RPO validation
- Backup encryption validation

Guardrails:
- Test with stub/dev databases only
- Document all procedures
- Create rollback procedures

Output to: docs/enterprise/reports/dr-plan.md
```

## Checklist
- [ ] Create backup scripts
- [ ] Test database restore
- [ ] Validate RTO < 4 hours
- [ ] Validate RPO < 15 minutes
- [ ] Test backup encryption
- [ ] Document DR runbook
- [ ] Schedule automated backups

## Commands
```bash
# PostgreSQL backup
# pg_dump -h localhost -p 5432 -U crm_user crm_db > backup_crm_$(date +%Y%m%d).sql
# pg_dump -h localhost -p 5433 -U ops_user ops_db > backup_ops_$(date +%Y%m%d).sql

# Restore
# psql -h localhost -p 5432 -U crm_user crm_db < backup_crm_YYYYMMDD.sql

# Encrypt backup
# gpg --encrypt backup_crm_YYYYMMDD.sql
```
EOF

    print_success "Prompt 3 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_4() {
    local output_file="$OUTPUT_DIR/iac-review.md"
    print_section "PROMPT 4: Infrastructure as Code Review"

    print_info "Executing IaC validation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Infrastructure as Code Review Report

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

```
You are a DevOps engineer. Review and validate infrastructure configuration:

1. Docker Compose validation and optimization
2. Nginx configuration review and linting
3. Database initialization scripts review
4. Environment variable management and documentation
5. SSL/TLS certificate management procedures
6. Network segmentation and firewall rules
7. Resource sizing recommendations
8. Create infrastructure diagram

Deliverables:
- Docker Compose health check validation
- Nginx lint results
- Environment variables documentation
- SSL renewal automation
- Infrastructure diagram (ASCII or mermaid)
- Deployment checklist

Guardrails:
- No changes to production configs
- Document all recommendations
- Small surgical diffs

Output to: docs/enterprise/reports/iac-review.md
```

## Checklist
- [ ] Validate Docker Compose health checks
- [ ] Lint Nginx configuration
- [ ] Document all environment variables
- [ ] Review SSL certificate renewal
- [ ] Create infrastructure diagram
- [ ] Validate resource limits
- [ ] Create deployment checklist

## Commands
```bash
# Docker Compose validation
docker-compose config --quiet

# Nginx lint
nginx -t -c deploy/nginx/nginx.conf

# Check environment variables
grep -r "os.getenv\|process.env" --include="*.py" --include="*.ts"

# Review Docker health checks
docker-compose ps
```
EOF

    print_success "Prompt 4 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_5() {
    local output_file="$OUTPUT_DIR/api-catalog.md"
    print_section "PROMPT 5: API Documentation & OpenAPI Spec"

    print_info "Executing API documentation generation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# API Documentation & OpenAPI Specification

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

```
You are a technical writer and API architect. Generate comprehensive API documentation:

1. Create OpenAPI 3.0 specification for CRM API
2. Create OpenAPI 3.0 specification for Ops API
3. Document all endpoints with request/response examples
4. Document authentication flows (JWT)
5. Create error response catalog
6. Document webhook payload schemas (Facebook, Google, Twilio)
7. Define API versioning strategy
8. Initialize API changelog

Deliverables:
- openapi-crm.yaml (OpenAPI 3.0 spec)
- openapi-ops.yaml (OpenAPI 3.0 spec)
- API documentation in Markdown
- Authentication flow diagrams
- Error code catalog
- Webhook schema documentation

Guardrails:
- Generate from existing code, don't modify APIs
- Validate OpenAPI specs with swagger-cli
- Document existing behavior accurately

Output to: docs/enterprise/reports/api-catalog.md
```

## Checklist
- [ ] Generate CRM API OpenAPI spec
- [ ] Generate Ops API OpenAPI spec
- [ ] Validate specs with swagger-cli
- [ ] Document authentication flows
- [ ] Create error code catalog
- [ ] Document webhook schemas
- [ ] Initialize API changelog

## Commands
```bash
# Generate OpenAPI spec (if using FastAPI)
# When using real FastAPI, it auto-generates at /openapi.json
# curl http://localhost:8000/openapi.json > docs/openapi-crm.json
# curl http://localhost:8001/openapi.json > docs/openapi-ops.json

# Validate OpenAPI spec
# npx swagger-cli validate docs/openapi-crm.json

# Generate human-readable docs
# npx redoc-cli bundle docs/openapi-crm.json -o docs/api-docs-crm.html
```
EOF

    print_success "Prompt 5 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_6() {
    local output_file="$OUTPUT_DIR/db-validation.md"
    print_section "PROMPT 6: Database Migration & Schema Validation"

    print_info "Executing database validation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Database Migration & Schema Validation Report

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

```
You are a database administrator. Validate database migrations and schema integrity:

1. Review all Alembic migrations (CRM + Ops)
2. Detect schema drift between environments
3. Test migration rollback for last 5 migrations
4. Review index optimization for query patterns
5. Validate foreign key constraints
6. Check data type consistency
7. Test migration performance (execution time < 30 seconds)
8. Validate data integrity constraints

Deliverables:
- Migration review report
- Schema drift detection results
- Rollback test results
- Index coverage analysis
- Migration performance benchmarks
- Data integrity validation

Guardrails:
- Use test databases only
- Document all findings
- Create optimization recommendations

Output to: docs/enterprise/reports/db-validation.md
```

## Checklist
- [ ] Review all migrations for reversibility
- [ ] Test rollback for latest migrations
- [ ] Check for schema drift
- [ ] Analyze index coverage
- [ ] Validate constraints
- [ ] Test migration performance
- [ ] Document optimization opportunities

## Commands
```bash
# Check migration status
cd crm_api && alembic current
cd ops_api && alembic current

# Test migration
cd crm_api && alembic upgrade head && alembic downgrade -1 && alembic upgrade head

# Check for schema drift
python tools/check_migrations.py
python tools/schema_diff.py --service crm

# Analyze query performance
# EXPLAIN ANALYZE SELECT ... (in PostgreSQL)
```
EOF

    print_success "Prompt 6 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_7() {
    local output_file="$OUTPUT_DIR/observability-plan.md"
    print_section "PROMPT 7: Monitoring & Observability Setup"

    print_info "Executing observability validation..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Monitoring & Observability Plan

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

```
You are an SRE (Site Reliability Engineer). Establish monitoring and observability:

1. Validate health check endpoints (/health)
2. Implement structured logging with correlation IDs
3. Define metrics collection strategy (Prometheus-ready)
4. Create alert definitions and thresholds (5-10 critical alerts)
5. Design log aggregation strategy
6. Prepare for APM (Application Performance Monitoring)
7. Create Grafana dashboard templates

Critical alerts to define:
- API response time > 500ms (p95)
- Error rate > 1%
- Database connection pool exhausted
- Disk usage > 85%
- Memory usage > 90%

Deliverables:
- Health endpoint validation
- Structured logging implementation
- Prometheus metrics endpoints
- Alert definitions
- Dashboard templates (JSON)
- On-call runbooks

Guardrails:
- Don't add heavy dependencies
- Keep logging efficient
- Document all metrics

Output to: docs/enterprise/reports/observability-plan.md
```

## Checklist
- [ ] Validate health endpoints
- [ ] Implement structured logging
- [ ] Define Prometheus metrics
- [ ] Create 5-10 critical alerts
- [ ] Define log retention policy
- [ ] Create dashboard templates
- [ ] Write on-call runbooks

## Commands
```bash
# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check log format
# grep -r "logger\." crm_api/app/ ops_api/app/

# Prometheus metrics endpoint (when implemented)
# curl http://localhost:8000/metrics
```
EOF

    print_success "Prompt 7 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

run_prompt_8() {
    local output_file="$OUTPUT_DIR/secrets-audit.md"
    print_section "PROMPT 8: Secrets Management & Rotation"

    print_info "Executing secrets audit..."
    print_warning "This is a HUMAN-TRIGGERED prompt - manual execution required"

    cat > "$output_file" <<'EOF'
# Secrets Management & Rotation Audit

**Executed By**: Bot (Placeholder)
**Date**: 2025-11-01
**Status**: PENDING_EXECUTION

## Instructions for Execution

```
You are a security engineer. Audit secrets management and create rotation procedures:

1. Scan git history for exposed secrets (JWT secrets, API keys, passwords)
2. Verify all secrets are in environment variables (not hardcoded)
3. Validate JWT secret strength (256+ bits)
4. Review API key management (Facebook, Google, Twilio)
5. Create secrets rotation procedures
6. Enable secrets scanning in CI/CD
7. Ensure environment-specific secrets isolation
8. Document emergency rotation runbook

Tools to use:
- grep/ag for secret patterns
- git log for history scan
- Custom validation scripts

Deliverables:
- Git history scan results
- Secrets inventory
- Rotation procedures
- Emergency rotation runbook
- CI secrets scanning setup

Guardrails:
- DO NOT log or display actual secret values
- Rotate any found secrets immediately
- Document procedures, not secrets

Output to: docs/enterprise/reports/secrets-audit.md
```

## Checklist
- [ ] Scan git history for secrets
- [ ] Verify no hardcoded secrets
- [ ] Validate JWT secret strength
- [ ] Document rotation procedures
- [ ] Enable CI secrets scanning
- [ ] Verify environment isolation
- [ ] Create emergency runbook
- [ ] Rotate any exposed secrets

## Commands
```bash
# Scan for common secret patterns
grep -r "password\s*=\s*['\"]" --include="*.py" --include="*.ts"
grep -r "api_key\s*=\s*['\"]" --include="*.py" --include="*.ts"
grep -r "secret\s*=\s*['\"]" --include="*.py" --include="*.ts"

# Check JWT secrets
grep JWT_SECRET .env.example

# Scan git history (requires git-secrets or gitleaks)
# git secrets --scan-history
# gitleaks detect --source .

# Verify .gitignore coverage
cat .gitignore | grep -E "\.env$|credentials"
```
EOF

    print_success "Prompt 8 template created: $output_file"
    print_info "Status: PENDING_EXECUTION (Human trigger required)"
}

# ==============================================================================
# PHASE EXECUTION
# ==============================================================================

run_phase_1() {
    print_header "PHASE 1: FOUNDATION (Sequential)"
    print_info "Executing prompts 8 and 1 in sequence..."
    run_prompt_8
    run_prompt_1
    print_success "Phase 1 complete"
}

run_phase_2() {
    print_header "PHASE 2: INFRASTRUCTURE (Parallel)"
    print_info "Executing prompts 4 and 6 (can run in parallel)..."
    run_prompt_4
    run_prompt_6
    print_success "Phase 2 complete"
}

run_phase_3() {
    print_header "PHASE 3: OPERATIONAL READINESS (Parallel)"
    print_info "Executing prompts 3, 5, and 7 (can run in parallel)..."
    run_prompt_3
    run_prompt_5
    run_prompt_7
    print_success "Phase 3 complete"
}

run_phase_4() {
    print_header "PHASE 4: PERFORMANCE VALIDATION (Final)"
    print_info "Executing prompt 2..."
    run_prompt_2
    print_success "Phase 4 complete"
}

run_all_prompts() {
    print_header "RUNNING ALL ENTERPRISE PROMPTS"

    show_execution_order

    print_warning "This will create execution templates for all 8 prompts"
    print_info "Each prompt must be manually executed after template creation"
    echo ""

    run_phase_1
    echo ""
    run_phase_2
    echo ""
    run_phase_3
    echo ""
    run_phase_4

    print_header "ALL PROMPT TEMPLATES CREATED"
    print_success "Templates created in: $OUTPUT_DIR/"
    echo ""
    print_warning "Next Steps:"
    echo "  1. Review each template file"
    echo "  2. Execute prompts manually using instructions in templates"
    echo "  3. Update ORCHESTRATION.md with results"
    echo "  4. Update risk register with findings"
    echo ""
}

# ==============================================================================
# STATUS DISPLAY
# ==============================================================================

show_status() {
    print_header "ENTERPRISE READINESS DASHBOARD"

    echo -e "${BOLD}Orchestration Status${NC}"
    echo ""

    # Check if report files exist
    local reports=(
        "security-audit.md:Prompt 1:Security Audit"
        "performance-report.md:Prompt 2:Performance Testing"
        "dr-plan.md:Prompt 3:Disaster Recovery"
        "iac-review.md:Prompt 4:IaC Review"
        "api-catalog.md:Prompt 5:API Documentation"
        "db-validation.md:Prompt 6:Database Validation"
        "observability-plan.md:Prompt 7:Monitoring Setup"
        "secrets-audit.md:Prompt 8:Secrets Management"
    )

    local completed=0
    local total=8

    for report_info in "${reports[@]}"; do
        IFS=: read -r filename prompt_id prompt_name <<< "$report_info"
        local filepath="$OUTPUT_DIR/$filename"

        if [ -f "$filepath" ]; then
            echo -e "  ✅ ${GREEN}${prompt_name}${NC} - Template created"
            ((completed++))
        else
            echo -e "  ⏸️  ${YELLOW}${prompt_name}${NC} - Not started"
        fi
    done

    echo ""
    echo -e "${BOLD}Progress:${NC} $completed/$total templates created ($(( completed * 100 / total ))%)"
    echo ""

    echo -e "${BOLD}Key Files:${NC}"
    echo "  📊 ORCHESTRATION: $ORCHESTRATION_FILE"
    echo "  ⚠️  RISKS:         $RISKS_FILE"
    echo "  🔒 CONTROLS:      $CONTROLS_FILE"
    echo "  📁 REPORTS:       $OUTPUT_DIR/"
    echo ""

    echo -e "${BOLD}Next Actions:${NC}"
    if [ $completed -eq 0 ]; then
        echo "  1. Run: ./scripts/enterprise/run_all.sh --all"
        echo "  2. Or run specific phase: ./scripts/enterprise/run_all.sh --phase=1"
    else
        echo "  1. Review templates in $OUTPUT_DIR/"
        echo "  2. Execute prompts manually using instructions"
        echo "  3. Update ORCHESTRATION.md with results"
    fi
    echo ""
}

# ==============================================================================
# MAIN MENU
# ==============================================================================

show_menu() {
    print_header "ENTERPRISE ORCHESTRATION MENU"

    echo "Select an option:"
    echo ""
    echo "  ${BOLD}Execution Options:${NC}"
    echo "    1) Run all prompts (create templates)"
    echo "    2) Run Phase 1 (Foundation)"
    echo "    3) Run Phase 2 (Infrastructure)"
    echo "    4) Run Phase 3 (Operational Readiness)"
    echo "    5) Run Phase 4 (Performance)"
    echo ""
    echo "  ${BOLD}Individual Prompts:${NC}"
    echo "    6) Prompt 1: Security & Compliance Audit"
    echo "    7) Prompt 2: Performance & Load Testing"
    echo "    8) Prompt 3: Disaster Recovery"
    echo "    9) Prompt 4: Infrastructure Review"
    echo "    10) Prompt 5: API Documentation"
    echo "    11) Prompt 6: Database Validation"
    echo "    12) Prompt 7: Monitoring Setup"
    echo "    13) Prompt 8: Secrets Management"
    echo ""
    echo "  ${BOLD}Information:${NC}"
    echo "    14) Show execution order"
    echo "    15) Show dashboard status"
    echo "    16) Exit"
    echo ""
    echo -n "Enter choice [1-16]: "

    read -r choice

    case $choice in
        1) run_all_prompts ;;
        2) run_phase_1 ;;
        3) run_phase_2 ;;
        4) run_phase_3 ;;
        5) run_phase_4 ;;
        6) run_prompt_1 ;;
        7) run_prompt_2 ;;
        8) run_prompt_3 ;;
        9) run_prompt_4 ;;
        10) run_prompt_5 ;;
        11) run_prompt_6 ;;
        12) run_prompt_7 ;;
        13) run_prompt_8 ;;
        14) show_execution_order ;;
        15) show_status ;;
        16) exit 0 ;;
        *) print_error "Invalid choice"; show_menu ;;
    esac
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

main() {
    cd "$REPO_ROOT" || exit 1

    # Parse command line arguments
    if [ $# -eq 0 ]; then
        show_menu
    else
        case "$1" in
            --all)
                run_all_prompts
                ;;
            --prompt=*)
                prompt_num="${1#*=}"
                case $prompt_num in
                    1) run_prompt_1 ;;
                    2) run_prompt_2 ;;
                    3) run_prompt_3 ;;
                    4) run_prompt_4 ;;
                    5) run_prompt_5 ;;
                    6) run_prompt_6 ;;
                    7) run_prompt_7 ;;
                    8) run_prompt_8 ;;
                    *) print_error "Invalid prompt number: $prompt_num" ;;
                esac
                ;;
            --phase=*)
                phase_num="${1#*=}"
                case $phase_num in
                    1) run_phase_1 ;;
                    2) run_phase_2 ;;
                    3) run_phase_3 ;;
                    4) run_phase_4 ;;
                    *) print_error "Invalid phase number: $phase_num" ;;
                esac
                ;;
            --status)
                show_status
                ;;
            --order)
                show_execution_order
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --all           Run all prompts"
                echo "  --prompt=N      Run specific prompt (1-8)"
                echo "  --phase=N       Run specific phase (1-4)"
                echo "  --status        Show dashboard status"
                echo "  --order         Show execution order"
                echo "  --help          Show this help"
                echo ""
                echo "Examples:"
                echo "  $0                    # Show interactive menu"
                echo "  $0 --all              # Create all prompt templates"
                echo "  $0 --prompt=1         # Create security audit template"
                echo "  $0 --phase=1          # Create Phase 1 templates"
                echo "  $0 --status           # Show current status"
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"
