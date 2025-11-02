#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Performance Budget CI Gate

Checks load test results against performance budgets and fails if exceeded by >10%.

Usage:
    # Check budgets from load test report
    python scripts/perf/check_budgets.py --report artifacts/perf/load_test.json

    # Strict mode (fail on any breach)
    python scripts/perf/check_budgets.py --report results.json --strict

    # Custom tolerance
    python scripts/perf/check_budgets.py --report results.json --tolerance 0.05

Exit codes:
    0 = All budgets met
    1 = Budgets exceeded by >tolerance
    2 = Missing data or error
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class BudgetCheck:
    """Budget check result"""
    endpoint: str
    metric: str  # p50, p95, p99
    actual: float
    budget: float
    breach_percentage: float
    status: str  # PASS, WARNING, FAIL


# Performance budgets (from docs/perf/budgets.md)
BUDGETS = {
    "login": {
        "p50": 80,
        "p95": 300,
        "p99": 500
    },
    "leads": {
        "p50": 120,
        "p95": 500,
        "p99": 1000
    },
    "enqueue": {
        "p50": 30,
        "p95": 150,
        "p99": 300
    },
    "customers": {
        "p50": 100,
        "p95": 400,
        "p99": 800
    },
    "invoices": {
        "p50": 150,
        "p95": 600,
        "p99": 1200
    }
}


class BudgetChecker:
    """
    Budget enforcement for CI/CD

    Compares load test results against defined budgets.
    """

    def __init__(self, tolerance: float = 0.10):
        """
        Initialize budget checker

        Args:
            tolerance: Allowed budget breach percentage (default: 0.10 = 10%)
        """
        self.tolerance = tolerance
        self.budgets = BUDGETS

    def check_report(self, report_path: str) -> List[BudgetCheck]:
        """
        Check load test report against budgets

        Args:
            report_path: Path to load test JSON report

        Returns:
            List of budget check results
        """
        # Load report
        report_file = Path(report_path)
        if not report_file.exists():
            raise FileNotFoundError(f"Report not found: {report_path}")

        report = json.loads(report_file.read_text())

        checks = []

        # Check each endpoint
        for endpoint_result in report.get("endpoints", []):
            endpoint_name = endpoint_result["endpoint"]

            # Get budget for this endpoint
            if endpoint_name not in self.budgets:
                print(f"⚠️  No budget defined for endpoint: {endpoint_name}")
                continue

            budget = self.budgets[endpoint_name]

            # Check p50
            checks.append(self._check_metric(
                endpoint_name,
                "p50",
                endpoint_result["latency_p50"],
                budget["p50"]
            ))

            # Check p95 (most important)
            checks.append(self._check_metric(
                endpoint_name,
                "p95",
                endpoint_result["latency_p95"],
                budget["p95"]
            ))

            # Check p99
            checks.append(self._check_metric(
                endpoint_name,
                "p99",
                endpoint_result["latency_p99"],
                budget["p99"]
            ))

        return checks

    def _check_metric(
        self,
        endpoint: str,
        metric: str,
        actual: float,
        budget: float
    ) -> BudgetCheck:
        """Check a single metric against budget"""
        breach_percentage = ((actual - budget) / budget) * 100 if budget > 0 else 0

        # Determine status
        if actual <= budget:
            status = "PASS"
        elif breach_percentage <= (self.tolerance * 100):
            status = "WARNING"  # Under tolerance, just warn
        else:
            status = "FAIL"  # Exceeds tolerance, fail CI

        return BudgetCheck(
            endpoint=endpoint,
            metric=metric,
            actual=actual,
            budget=budget,
            breach_percentage=breach_percentage,
            status=status
        )

    def print_results(self, checks: List[BudgetCheck]):
        """Print budget check results"""
        print("\n" + "=" * 80)
        print("PERFORMANCE BUDGET CHECK")
        print("=" * 80)

        # Group by endpoint
        endpoints = {}
        for check in checks:
            if check.endpoint not in endpoints:
                endpoints[check.endpoint] = []
            endpoints[check.endpoint].append(check)

        # Print each endpoint
        for endpoint, endpoint_checks in endpoints.items():
            print(f"\n{endpoint}:")

            for check in endpoint_checks:
                status_icon = {
                    "PASS": "✓",
                    "WARNING": "⚠️",
                    "FAIL": "❌"
                }.get(check.status, "?")

                breach_str = f"+{check.breach_percentage:.1f}%" if check.breach_percentage > 0 else ""

                print(f"  {status_icon} {check.metric}: "
                      f"{check.actual:.0f}ms / {check.budget:.0f}ms "
                      f"{breach_str} "
                      f"[{check.status}]")

        # Summary
        print("\n" + "=" * 80)

        pass_count = sum(1 for c in checks if c.status == "PASS")
        warning_count = sum(1 for c in checks if c.status == "WARNING")
        fail_count = sum(1 for c in checks if c.status == "FAIL")

        print(f"Results: {pass_count} passed, {warning_count} warnings, {fail_count} failed")

        if fail_count > 0:
            print(f"\n❌ BUDGET CHECK FAILED")
            print(f"   {fail_count} metric(s) exceeded budget by >{self.tolerance*100:.0f}%")
            print(f"   Performance regression detected!")
        elif warning_count > 0:
            print(f"\n⚠️  BUDGET CHECK PASSED WITH WARNINGS")
            print(f"   {warning_count} metric(s) slightly over budget")
            print(f"   Monitor these endpoints closely")
        else:
            print(f"\n✓ ALL BUDGETS MET")

        print("=" * 80)

    def has_failures(self, checks: List[BudgetCheck]) -> bool:
        """Check if any checks failed"""
        return any(c.status == "FAIL" for c in checks)


def main():
    parser = argparse.ArgumentParser(description="Performance Budget CI Gate")
    parser.add_argument(
        '--report',
        type=str,
        required=True,
        help="Path to load test JSON report"
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.10,
        help="Breach tolerance (default: 0.10 = 10%%)"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Fail on any budget breach (tolerance=0)"
    )

    args = parser.parse_args()

    # Set tolerance
    tolerance = 0.0 if args.strict else args.tolerance

    try:
        # Run budget check
        checker = BudgetChecker(tolerance=tolerance)
        checks = checker.check_report(args.report)

        # Print results
        checker.print_results(checks)

        # Exit with appropriate code
        if checker.has_failures(checks):
            sys.exit(1)  # CI failure
        else:
            sys.exit(0)  # Success

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(2)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
