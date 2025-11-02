# CI/CD Policy as Code
#
# This policy enforces merge requirements for the CI/CD pipeline.
# Used with Open Policy Agent (OPA) or stub runner.
#
# Policy Gates:
# 1. All tests must pass (green)
# 2. Code coverage ≥85% backend / ≥80% frontend
# 3. SBOM must be present and valid
# 4. License compliance must pass
# 5. Performance budgets must pass (for main branch merges)
# 6. No critical security vulnerabilities
#
# Usage:
#   opa eval -d policy/ci.rego -i input.json "data.ci.allow"
#   python tools/policy/opa_stub.py --policy policy/ci.rego --input input.json

package ci

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# ==============================================================================
# Main Decision: Allow or Deny Merge
# ==============================================================================

default allow = false

# Allow merge if all gates pass
allow if {
    tests_pass
    coverage_sufficient
    sbom_present
    licenses_compliant
    performance_acceptable
    no_critical_vulnerabilities
    required_approvals_met
}

# ==============================================================================
# Gate 1: Tests Must Pass (Green)
# ==============================================================================

default tests_pass = false

tests_pass if {
    input.tests.status == "passed"
    input.tests.failures == 0
    input.tests.errors == 0
}

# Generate violation message if tests fail
tests_violation[msg] {
    not tests_pass
    msg := sprintf("Tests failed: %d failures, %d errors", [
        object.get(input.tests, "failures", 0),
        object.get(input.tests, "errors", 0)
    ])
}

# ==============================================================================
# Gate 2: Code Coverage Requirements
# ==============================================================================

# Backend coverage threshold
backend_coverage_threshold := 85.0

# Frontend coverage threshold
frontend_coverage_threshold := 80.0

# Check if backend coverage meets threshold
backend_coverage_sufficient if {
    input.coverage.backend >= backend_coverage_threshold
}

# Check if frontend coverage meets threshold
frontend_coverage_sufficient if {
    input.coverage.frontend >= frontend_coverage_threshold
}

# Overall coverage check
default coverage_sufficient = false

coverage_sufficient if {
    backend_coverage_sufficient
    frontend_coverage_sufficient
}

# Generate violation messages for coverage
coverage_violation[msg] {
    not backend_coverage_sufficient
    msg := sprintf("Backend coverage %.1f%% below threshold %.1f%%", [
        object.get(input.coverage, "backend", 0),
        backend_coverage_threshold
    ])
}

coverage_violation[msg] {
    not frontend_coverage_sufficient
    msg := sprintf("Frontend coverage %.1f%% below threshold %.1f%%", [
        object.get(input.coverage, "frontend", 0),
        frontend_coverage_threshold
    ])
}

# ==============================================================================
# Gate 3: SBOM Must Be Present and Valid
# ==============================================================================

default sbom_present = false

sbom_present if {
    input.sbom.exists == true
    input.sbom.valid == true
    count(input.sbom.components) > 0
}

# Generate violation message if SBOM missing
sbom_violation[msg] {
    not sbom_present
    not input.sbom.exists
    msg := "SBOM file not found - run SBOM generation"
}

sbom_violation[msg] {
    not sbom_present
    input.sbom.exists == true
    input.sbom.valid == false
    msg := "SBOM validation failed - invalid format"
}

sbom_violation[msg] {
    not sbom_present
    input.sbom.exists == true
    count(input.sbom.components) == 0
    msg := "SBOM contains no components"
}

# ==============================================================================
# Gate 4: License Compliance
# ==============================================================================

default licenses_compliant = false

licenses_compliant if {
    input.licenses.status == "pass"
    count(input.licenses.violations) == 0
    count(input.licenses.unknown) == 0
}

# Generate violation messages for license issues
license_violation[msg] {
    not licenses_compliant
    count(input.licenses.violations) > 0
    violation := input.licenses.violations[_]
    msg := sprintf("License violation: %s (%s) - %s", [
        violation.package,
        violation.license,
        violation.reason
    ])
}

license_violation[msg] {
    not licenses_compliant
    count(input.licenses.unknown) > 0
    unknown := input.licenses.unknown[_]
    msg := sprintf("Unknown license: %s (license: %s)", [
        unknown.package,
        unknown.license
    ])
}

# ==============================================================================
# Gate 5: Performance Budgets (Main Branch Only)
# ==============================================================================

# Check if this is a merge to main/master
is_main_merge if {
    input.target_branch == "main"
}

is_main_merge if {
    input.target_branch == "master"
}

# Performance budgets check
default performance_acceptable = true

# For main branch merges, enforce performance budgets
performance_acceptable if {
    not is_main_merge
}

performance_acceptable if {
    is_main_merge
    input.performance.status == "pass"
    count(input.performance.failures) == 0
}

# Generate violation messages for performance budget failures
performance_violation[msg] {
    is_main_merge
    not performance_acceptable
    failure := input.performance.failures[_]
    msg := sprintf("Performance budget exceeded: %s - p95 %.0fms > budget %.0fms (%.1f%% over)", [
        failure.endpoint,
        failure.actual_p95,
        failure.budget_p95,
        failure.breach_percentage
    ])
}

# ==============================================================================
# Gate 6: Security Vulnerabilities
# ==============================================================================

default no_critical_vulnerabilities = true

# Fail if critical or high severity vulnerabilities present
no_critical_vulnerabilities if {
    input.security.critical_count == 0
    input.security.high_count == 0
}

# Generate violation messages for vulnerabilities
security_violation[msg] {
    not no_critical_vulnerabilities
    input.security.critical_count > 0
    msg := sprintf("Critical vulnerabilities found: %d - must be remediated before merge", [
        input.security.critical_count
    ])
}

security_violation[msg] {
    not no_critical_vulnerabilities
    input.security.high_count > 0
    msg := sprintf("High severity vulnerabilities found: %d - must be remediated before merge", [
        input.security.high_count
    ])
}

# ==============================================================================
# Gate 7: Required Approvals
# ==============================================================================

default required_approvals_met = false

# Get risk level from PR metadata
risk_level := object.get(input.pr, "risk_level", "medium")

# Approval requirements by risk level
approval_count_required[count] {
    risk_level == "low"
    count := 1
}

approval_count_required[count] {
    risk_level == "medium"
    count := 2
}

approval_count_required[count] {
    risk_level == "high"
    count := 3
}

approval_count_required[count] {
    risk_level == "critical"
    count := 3
}

# Check if approval count is met
required_approvals_met if {
    required := approval_count_required[_]
    actual := count(input.pr.approvals)
    actual >= required
}

# Generate violation message for insufficient approvals
approval_violation[msg] {
    not required_approvals_met
    required := approval_count_required[_]
    actual := count(input.pr.approvals)
    msg := sprintf("Insufficient approvals: %d of %d required for %s risk PR", [
        actual,
        required,
        risk_level
    ])
}

# ==============================================================================
# Comprehensive Violation Report
# ==============================================================================

# Collect all violation messages
violations[msg] {
    msg := tests_violation[_]
}

violations[msg] {
    msg := coverage_violation[_]
}

violations[msg] {
    msg := sbom_violation[_]
}

violations[msg] {
    msg := license_violation[_]
}

violations[msg] {
    msg := performance_violation[_]
}

violations[msg] {
    msg := security_violation[_]
}

violations[msg] {
    msg := approval_violation[_]
}

# ==============================================================================
# Policy Summary
# ==============================================================================

policy_summary := {
    "decision": allow,
    "gates": {
        "tests_pass": tests_pass,
        "coverage_sufficient": coverage_sufficient,
        "sbom_present": sbom_present,
        "licenses_compliant": licenses_compliant,
        "performance_acceptable": performance_acceptable,
        "no_critical_vulnerabilities": no_critical_vulnerabilities,
        "required_approvals_met": required_approvals_met
    },
    "violations": violations,
    "violation_count": count(violations),
    "target_branch": input.target_branch,
    "is_main_merge": is_main_merge,
    "risk_level": risk_level
}

# ==============================================================================
# Warnings (Non-Blocking)
# ==============================================================================

# Medium severity vulnerabilities generate warnings
warnings[msg] {
    input.security.medium_count > 0
    msg := sprintf("Warning: %d medium severity vulnerabilities found - consider remediation", [
        input.security.medium_count
    ])
}

# Coverage close to threshold generates warnings
warnings[msg] {
    backend_coverage_sufficient
    input.coverage.backend < (backend_coverage_threshold + 5)
    msg := sprintf("Warning: Backend coverage %.1f%% is close to threshold %.1f%%", [
        input.coverage.backend,
        backend_coverage_threshold
    ])
}

warnings[msg] {
    frontend_coverage_sufficient
    input.coverage.frontend < (frontend_coverage_threshold + 5)
    msg := sprintf("Warning: Frontend coverage %.1f%% is close to threshold %.1f%%", [
        input.coverage.frontend,
        frontend_coverage_threshold
    ])
}

# Performance close to budget generates warnings
warnings[msg] {
    performance_acceptable
    near_budget := input.performance.warnings[_]
    msg := sprintf("Warning: %s p95 %.0fms is close to budget %.0fms (%.1f%% of budget)", [
        near_budget.endpoint,
        near_budget.actual_p95,
        near_budget.budget_p95,
        near_budget.budget_utilization
    ])
}

# ==============================================================================
# Exemptions (Override Mechanism)
# ==============================================================================

# Check if exemption is granted
has_valid_exemption if {
    input.exemption.granted == true
    input.exemption.authorized_by != ""
    input.exemption.reason != ""
    input.exemption.expires_at > time.now_ns()
}

# Allow if valid exemption exists (override)
allow if {
    has_valid_exemption
}

# Record exemption usage
exemption_used[msg] {
    has_valid_exemption
    msg := sprintf("Exemption granted by %s: %s (expires: %s)", [
        input.exemption.authorized_by,
        input.exemption.reason,
        input.exemption.expires_at
    ])
}
