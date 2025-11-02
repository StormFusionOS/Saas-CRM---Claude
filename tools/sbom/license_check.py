#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
License Policy Checker

Validates that all dependencies in SBOMs comply with approved license policy.

Features:
- Checks licenses against allowlist
- Reports violations
- Supports conditional approvals
- CI-friendly exit codes

Usage:
    # Check all services
    python tools/sbom/license_check.py

    # Check specific service
    python tools/sbom/license_check.py --service crm_api

    # Strict mode (fail on unknown licenses)
    python tools/sbom/license_check.py --strict

Exit codes:
    0 - All licenses approved
    1 - License violations found
    2 - Configuration/file errors
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


REPO_ROOT = Path(__file__).parent.parent.parent
SBOM_DIR = REPO_ROOT / "sbom"
ALLOWLIST_FILE = Path(__file__).parent / "allowlist.json"

# Service names
SERVICES = ["crm_api", "ops_api", "crm", "ops-console"]


class LicensePolicy:
    """License policy enforcement"""

    def __init__(self, allowlist_path: Path):
        self.allowlist_path = allowlist_path
        self.approved_licenses: Set[str] = set()
        self.denied_licenses: Set[str] = set()
        self.conditional_approvals: Dict[str, Dict] = {}
        self._load_policy()

    def _load_policy(self):
        """Load license policy from allowlist"""
        if not self.allowlist_path.exists():
            raise FileNotFoundError(f"Allowlist not found: {self.allowlist_path}")

        with open(self.allowlist_path, "r") as f:
            policy = json.load(f)

        # Load approved licenses
        self.approved_licenses = set(policy.get("approved_licenses", []))

        # Load denied licenses
        self.denied_licenses = set(policy.get("denied_licenses", []))

        # Load conditional approvals
        for item in policy.get("conditionally_approved", []):
            license_id = item["license"]
            self.conditional_approvals[license_id] = {
                "condition": item.get("condition", ""),
                "packages": set(item.get("packages", []))
            }

    def check_license(self, license_id: str, package_name: str) -> Tuple[str, str]:
        """
        Check if a license is approved for a package.

        Returns:
            Tuple of (status, reason)
            status: "approved", "denied", "unknown", "conditional"
        """
        if not license_id or license_id == "UNKNOWN":
            return ("unknown", "License not specified")

        # Check if explicitly denied
        if license_id in self.denied_licenses:
            return ("denied", f"License '{license_id}' is explicitly denied by policy")

        # Check if approved
        if license_id in self.approved_licenses:
            return ("approved", "License is on approved list")

        # Check conditional approvals
        if license_id in self.conditional_approvals:
            approval = self.conditional_approvals[license_id]
            packages = approval["packages"]

            # If package list is empty, approve for all packages
            if not packages or package_name in packages:
                condition = approval["condition"]
                return ("conditional", f"Conditionally approved: {condition}")
            else:
                return ("denied", f"Package '{package_name}' not approved for license '{license_id}'")

        # Unknown license
        return ("unknown", f"License '{license_id}' not in policy")


class LicenseChecker:
    """Check SBOM licenses against policy"""

    def __init__(self, policy: LicensePolicy, strict: bool = False):
        self.policy = policy
        self.strict = strict
        self.violations: List[Dict] = []
        self.warnings: List[Dict] = []
        self.approved_count = 0
        self.conditional_count = 0

    def check_service(self, service_name: str) -> bool:
        """
        Check licenses for a service.

        Returns:
            True if all licenses pass, False if violations found
        """
        print(f"\n{'='*60}")
        print(f"Checking licenses for: {service_name}")
        print(f"{'='*60}\n")

        sbom_file = SBOM_DIR / service_name / "sbom.json"

        if not sbom_file.exists():
            print(f"❌ SBOM not found: {sbom_file}")
            self.violations.append({
                "service": service_name,
                "issue": "SBOM not found",
                "severity": "error"
            })
            return False

        # Load SBOM
        with open(sbom_file, "r") as f:
            sbom = json.load(f)

        components = sbom.get("components", [])

        if not components:
            print(f"⚠️  No components found in SBOM")
            return True

        # Check each component
        service_violations = []
        service_warnings = []

        for component in components:
            package_name = component.get("name", "unknown")
            licenses = component.get("licenses", [])

            # Extract license ID
            if not licenses:
                license_id = "UNKNOWN"
            elif isinstance(licenses[0], dict):
                license_data = licenses[0].get("license", {})
                license_id = license_data.get("id", "UNKNOWN")
            else:
                license_id = str(licenses[0])

            # Check license
            status, reason = self.policy.check_license(license_id, package_name)

            if status == "approved":
                print(f"   ✅ {package_name}: {license_id}")
                self.approved_count += 1

            elif status == "conditional":
                print(f"   ⚠️  {package_name}: {license_id} ({reason})")
                self.conditional_count += 1

            elif status == "denied":
                print(f"   ❌ {package_name}: {license_id}")
                print(f"      Reason: {reason}")
                service_violations.append({
                    "package": package_name,
                    "license": license_id,
                    "reason": reason
                })

            elif status == "unknown":
                msg = f"   ⚠️  {package_name}: {license_id} (not in policy)"
                if self.strict:
                    print(f"   ❌ {package_name}: {license_id} (unknown license - strict mode)")
                    service_violations.append({
                        "package": package_name,
                        "license": license_id,
                        "reason": "Unknown license in strict mode"
                    })
                else:
                    print(msg)
                    service_warnings.append({
                        "package": package_name,
                        "license": license_id,
                        "reason": reason
                    })

        # Record violations
        if service_violations:
            self.violations.extend([
                {"service": service_name, **v} for v in service_violations
            ])

        if service_warnings:
            self.warnings.extend([
                {"service": service_name, **w} for w in service_warnings
            ])

        # Summary
        print(f"\nSummary for {service_name}:")
        print(f"   ✅ Approved: {len([c for c in components]) - len(service_violations) - len(service_warnings)}")
        if service_warnings:
            print(f"   ⚠️  Warnings: {len(service_warnings)}")
        if service_violations:
            print(f"   ❌ Violations: {len(service_violations)}")

        return len(service_violations) == 0

    def check_all_services(self) -> bool:
        """Check all services"""
        all_passed = True

        for service in SERVICES:
            passed = self.check_service(service)
            all_passed = all_passed and passed

        return all_passed

    def print_summary(self):
        """Print final summary"""
        print(f"\n{'='*60}")
        print("License Check Summary")
        print(f"{'='*60}\n")

        print(f"✅ Approved licenses: {self.approved_count}")
        print(f"⚠️  Conditional approvals: {self.conditional_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Violations: {len(self.violations)}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning['service']}/{warning['package']}: {warning['license']} - {warning['reason']}")

        if self.violations:
            print(f"\n❌ Violations ({len(self.violations)}):")
            for violation in self.violations:
                print(f"   • {violation['service']}/{violation['package']}: {violation['license']}")
                print(f"     Reason: {violation['reason']}")

        print()


def main():
    parser = argparse.ArgumentParser(description="License Policy Checker")
    parser.add_argument("--service", choices=SERVICES,
                        help="Check specific service only")
    parser.add_argument("--strict", action="store_true",
                        help="Fail on unknown licenses")

    args = parser.parse_args()

    try:
        # Load policy
        policy = LicensePolicy(ALLOWLIST_FILE)
        print(f"✅ Loaded license policy from {ALLOWLIST_FILE}")
        print(f"   Approved licenses: {len(policy.approved_licenses)}")
        print(f"   Denied licenses: {len(policy.denied_licenses)}")
        print(f"   Conditional approvals: {len(policy.conditional_approvals)}")

        # Run checks
        checker = LicenseChecker(policy, strict=args.strict)

        if args.service:
            passed = checker.check_service(args.service)
        else:
            passed = checker.check_all_services()

        # Print summary
        checker.print_summary()

        # Exit with appropriate code
        if not passed:
            print("❌ License check FAILED")
            return 1
        elif checker.warnings and args.strict:
            print("❌ License check FAILED (warnings in strict mode)")
            return 1
        else:
            print("✅ License check PASSED")
            return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return 2
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
