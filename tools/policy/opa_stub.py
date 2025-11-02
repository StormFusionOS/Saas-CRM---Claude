#!/usr/bin/env python3
"""
OPA Policy Runner Stub

Evaluates CI/CD policy defined in policy/ci.rego without requiring actual OPA installation.
Implements the same policy logic in Python for offline development and testing.

Usage:
    # Evaluate policy with input file
    python tools/policy/opa_stub.py --input ci_metrics.json

    # Evaluate with custom policy file
    python tools/policy/opa_stub.py --policy policy/ci.rego --input ci_metrics.json

    # Output detailed report
    python tools/policy/opa_stub.py --input ci_metrics.json --verbose

    # CI mode (exit code 0 if pass, 1 if fail)
    python tools/policy/opa_stub.py --input ci_metrics.json --ci

Input JSON Format:
    {
        "tests": {"status": "passed", "failures": 0, "errors": 0},
        "coverage": {"backend": 87.5, "frontend": 82.3},
        "sbom": {"exists": true, "valid": true, "components": 245},
        "licenses": {"status": "pass", "violations": [], "unknown": []},
        "performance": {"status": "pass", "failures": []},
        "security": {"critical_count": 0, "high_count": 0, "medium_count": 2},
        "pr": {"risk_level": "medium", "approvals": ["@user1", "@user2"]},
        "target_branch": "main"
    }
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


# ==============================================================================
# Policy Thresholds (matches policy/ci.rego)
# ==============================================================================

BACKEND_COVERAGE_THRESHOLD = 85.0
FRONTEND_COVERAGE_THRESHOLD = 80.0

APPROVAL_REQUIREMENTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 3
}


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class PolicyResult:
    """Result of policy evaluation"""
    allow: bool
    gates: Dict[str, bool]
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    exemption_used: Optional[str] = None
    target_branch: str = ""
    is_main_merge: bool = False
    risk_level: str = "medium"

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output"""
        return {
            "decision": "ALLOW" if self.allow else "DENY",
            "allow": self.allow,
            "gates": self.gates,
            "violations": self.violations,
            "violation_count": self.violation_count,
            "warnings": self.warnings,
            "warning_count": self.warning_count,
            "exemption_used": self.exemption_used,
            "target_branch": self.target_branch,
            "is_main_merge": self.is_main_merge,
            "risk_level": self.risk_level
        }


# ==============================================================================
# Policy Evaluator
# ==============================================================================

class PolicyEvaluator:
    """Evaluates CI/CD policy against input data"""

    def __init__(self, input_data: Dict[str, Any]):
        self.input = input_data
        self.violations: List[str] = []
        self.warnings: List[str] = []

    def evaluate(self) -> PolicyResult:
        """Evaluate all policy gates"""

        # Check for exemption first
        exemption = self._check_exemption()
        if exemption:
            return PolicyResult(
                allow=True,
                gates=self._evaluate_all_gates(),
                violations=[],
                warnings=[],
                exemption_used=exemption,
                target_branch=self.input.get("target_branch", ""),
                is_main_merge=self._is_main_merge(),
                risk_level=self.input.get("pr", {}).get("risk_level", "medium")
            )

        # Evaluate all gates
        gates = self._evaluate_all_gates()

        # Collect warnings
        self._check_warnings()

        # Allow if all gates pass
        allow = all(gates.values())

        return PolicyResult(
            allow=allow,
            gates=gates,
            violations=self.violations,
            warnings=self.warnings,
            target_branch=self.input.get("target_branch", ""),
            is_main_merge=self._is_main_merge(),
            risk_level=self.input.get("pr", {}).get("risk_level", "medium")
        )

    def _evaluate_all_gates(self) -> Dict[str, bool]:
        """Evaluate all policy gates and collect violations"""
        return {
            "tests_pass": self._check_tests(),
            "coverage_sufficient": self._check_coverage(),
            "sbom_present": self._check_sbom(),
            "licenses_compliant": self._check_licenses(),
            "performance_acceptable": self._check_performance(),
            "no_critical_vulnerabilities": self._check_security(),
            "required_approvals_met": self._check_approvals()
        }

    # Gate 1: Tests
    def _check_tests(self) -> bool:
        """Check if all tests pass"""
        tests = self.input.get("tests", {})
        status = tests.get("status", "")
        failures = tests.get("failures", 0)
        errors = tests.get("errors", 0)

        if status != "passed" or failures > 0 or errors > 0:
            self.violations.append(
                f"Tests failed: {failures} failures, {errors} errors"
            )
            return False
        return True

    # Gate 2: Coverage
    def _check_coverage(self) -> bool:
        """Check if code coverage meets thresholds"""
        coverage = self.input.get("coverage", {})
        backend = coverage.get("backend", 0.0)
        frontend = coverage.get("frontend", 0.0)

        backend_ok = backend >= BACKEND_COVERAGE_THRESHOLD
        frontend_ok = frontend >= FRONTEND_COVERAGE_THRESHOLD

        if not backend_ok:
            self.violations.append(
                f"Backend coverage {backend:.1f}% below threshold {BACKEND_COVERAGE_THRESHOLD:.1f}%"
            )

        if not frontend_ok:
            self.violations.append(
                f"Frontend coverage {frontend:.1f}% below threshold {FRONTEND_COVERAGE_THRESHOLD:.1f}%"
            )

        return backend_ok and frontend_ok

    # Gate 3: SBOM
    def _check_sbom(self) -> bool:
        """Check if SBOM is present and valid"""
        sbom = self.input.get("sbom", {})
        exists = sbom.get("exists", False)
        valid = sbom.get("valid", False)
        components = sbom.get("components", 0)

        if not exists:
            self.violations.append("SBOM file not found - run SBOM generation")
            return False

        if not valid:
            self.violations.append("SBOM validation failed - invalid format")
            return False

        if components == 0:
            self.violations.append("SBOM contains no components")
            return False

        return True

    # Gate 4: Licenses
    def _check_licenses(self) -> bool:
        """Check license compliance"""
        licenses = self.input.get("licenses", {})
        status = licenses.get("status", "")
        violations = licenses.get("violations", [])
        unknown = licenses.get("unknown", [])

        if status != "pass" or len(violations) > 0 or len(unknown) > 0:
            for violation in violations:
                self.violations.append(
                    f"License violation: {violation['package']} ({violation['license']}) - {violation['reason']}"
                )

            for unk in unknown:
                self.violations.append(
                    f"Unknown license: {unk['package']} (license: {unk.get('license', 'UNKNOWN')})"
                )

            return False

        return True

    # Gate 5: Performance
    def _check_performance(self) -> bool:
        """Check performance budgets (main branch only)"""
        if not self._is_main_merge():
            return True

        performance = self.input.get("performance", {})
        status = performance.get("status", "")
        failures = performance.get("failures", [])

        if status != "pass" or len(failures) > 0:
            for failure in failures:
                self.violations.append(
                    f"Performance budget exceeded: {failure['endpoint']} - "
                    f"p95 {failure['actual_p95']:.0f}ms > budget {failure['budget_p95']:.0f}ms "
                    f"({failure['breach_percentage']:.1f}% over)"
                )
            return False

        return True

    # Gate 6: Security
    def _check_security(self) -> bool:
        """Check for critical/high vulnerabilities"""
        security = self.input.get("security", {})
        critical = security.get("critical_count", 0)
        high = security.get("high_count", 0)

        if critical > 0:
            self.violations.append(
                f"Critical vulnerabilities found: {critical} - must be remediated before merge"
            )

        if high > 0:
            self.violations.append(
                f"High severity vulnerabilities found: {high} - must be remediated before merge"
            )

        return critical == 0 and high == 0

    # Gate 7: Approvals
    def _check_approvals(self) -> bool:
        """Check if required approvals are met"""
        pr = self.input.get("pr", {})
        risk_level = pr.get("risk_level", "medium").lower()
        approvals = pr.get("approvals", [])

        required = APPROVAL_REQUIREMENTS.get(risk_level, 2)
        actual = len(approvals)

        if actual < required:
            self.violations.append(
                f"Insufficient approvals: {actual} of {required} required for {risk_level} risk PR"
            )
            return False

        return True

    # Helper: Check if main merge
    def _is_main_merge(self) -> bool:
        """Check if target branch is main/master"""
        target = self.input.get("target_branch", "")
        return target in ["main", "master"]

    # Helper: Check exemption
    def _check_exemption(self) -> Optional[str]:
        """Check if valid exemption exists"""
        exemption = self.input.get("exemption", {})

        if not exemption.get("granted", False):
            return None

        authorized_by = exemption.get("authorized_by", "")
        reason = exemption.get("reason", "")
        expires_at = exemption.get("expires_at", 0)

        if not authorized_by or not reason:
            return None

        # Check expiration (timestamp in nanoseconds)
        now_ns = datetime.now().timestamp() * 1_000_000_000
        if expires_at <= now_ns:
            return None

        return f"Exemption granted by {authorized_by}: {reason}"

    # Warnings (non-blocking)
    def _check_warnings(self):
        """Generate warning messages"""

        # Medium severity vulnerabilities
        security = self.input.get("security", {})
        medium = security.get("medium_count", 0)
        if medium > 0:
            self.warnings.append(
                f"Warning: {medium} medium severity vulnerabilities found - consider remediation"
            )

        # Coverage close to threshold
        coverage = self.input.get("coverage", {})
        backend = coverage.get("backend", 0.0)
        frontend = coverage.get("frontend", 0.0)

        if BACKEND_COVERAGE_THRESHOLD <= backend < (BACKEND_COVERAGE_THRESHOLD + 5):
            self.warnings.append(
                f"Warning: Backend coverage {backend:.1f}% is close to threshold {BACKEND_COVERAGE_THRESHOLD:.1f}%"
            )

        if FRONTEND_COVERAGE_THRESHOLD <= frontend < (FRONTEND_COVERAGE_THRESHOLD + 5):
            self.warnings.append(
                f"Warning: Frontend coverage {frontend:.1f}% is close to threshold {FRONTEND_COVERAGE_THRESHOLD:.1f}%"
            )

        # Performance close to budget
        performance = self.input.get("performance", {})
        near_budget = performance.get("warnings", [])
        for warning in near_budget:
            self.warnings.append(
                f"Warning: {warning['endpoint']} p95 {warning['actual_p95']:.0f}ms "
                f"is close to budget {warning['budget_p95']:.0f}ms "
                f"({warning['budget_utilization']:.1f}% of budget)"
            )


# ==============================================================================
# CLI and Output Formatting
# ==============================================================================

def print_result(result: PolicyResult, verbose: bool = False):
    """Print policy evaluation result"""

    # Print header
    decision_symbol = "✅" if result.allow else "❌"
    decision_text = "ALLOW" if result.allow else "DENY"
    print(f"\n{'=' * 70}")
    print(f"{decision_symbol} Policy Decision: {decision_text}")
    print(f"{'=' * 70}\n")

    # Print metadata
    if verbose:
        print(f"Target Branch: {result.target_branch}")
        print(f"Main Merge: {'Yes' if result.is_main_merge else 'No'}")
        print(f"Risk Level: {result.risk_level}")
        print(f"Exemption: {result.exemption_used or 'None'}\n")

    # Print gate results
    print("Policy Gates:")
    print("-" * 70)
    for gate, passed in result.gates.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        gate_name = gate.replace("_", " ").title()
        print(f"  {status:12} {gate_name}")
    print()

    # Print violations
    if result.violations:
        print(f"❌ Violations ({result.violation_count}):")
        print("-" * 70)
        for i, violation in enumerate(result.violations, 1):
            print(f"  {i}. {violation}")
        print()

    # Print warnings
    if result.warnings:
        print(f"⚠️  Warnings ({result.warning_count}):")
        print("-" * 70)
        for i, warning in enumerate(result.warnings, 1):
            print(f"  {i}. {warning}")
        print()

    # Print summary
    if result.allow:
        print("✅ All policy gates passed. Merge allowed.\n")
    else:
        print(f"❌ {result.violation_count} violation(s) found. Merge blocked.\n")
        print("Fix the violations above and re-run the policy check.\n")


def load_input(input_file: Path) -> Dict[str, Any]:
    """Load input JSON file"""
    try:
        with input_file.open() as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="OPA Policy Runner Stub - Evaluate CI/CD policy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate policy with input file
  python tools/policy/opa_stub.py --input ci_metrics.json

  # CI mode (exit code 0 if pass, 1 if fail)
  python tools/policy/opa_stub.py --input ci_metrics.json --ci

  # Output JSON format
  python tools/policy/opa_stub.py --input ci_metrics.json --format json

  # Verbose output
  python tools/policy/opa_stub.py --input ci_metrics.json --verbose
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to input JSON file with CI metrics"
    )

    parser.add_argument(
        "--policy", "-p",
        type=Path,
        default=Path("policy/ci.rego"),
        help="Path to policy file (for documentation, not parsed)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output with detailed information"
    )

    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit code 0 if pass, 1 if fail (no output unless failure)"
    )

    args = parser.parse_args()

    # Load input data
    input_data = load_input(args.input)

    # Evaluate policy
    evaluator = PolicyEvaluator(input_data)
    result = evaluator.evaluate()

    # Output result
    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    elif args.ci:
        # CI mode: only print if failure
        if not result.allow:
            print_result(result, verbose=False)
    else:
        print_result(result, verbose=args.verbose)

    # Exit with appropriate code
    sys.exit(0 if result.allow else 1)


if __name__ == "__main__":
    main()
