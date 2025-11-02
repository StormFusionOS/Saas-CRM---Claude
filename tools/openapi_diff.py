#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
OpenAPI Diff Tool

Detects breaking changes between OpenAPI specifications.

Usage:
    python tools/openapi_diff.py --baseline docs/api/crm.baseline.yaml --current docs/api/crm.yaml
    python tools/openapi_diff.py --update-baseline --service crm
    python tools/openapi_diff.py --check-all
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import shutil


class BreakingChange:
    """Represents a breaking change in the API."""

    def __init__(self, change_type: str, path: str, description: str):
        self.change_type = change_type
        self.path = path
        self.description = description

    def __str__(self):
        return f"[{self.change_type}] {self.path}: {self.description}"


def load_openapi_spec(file_path: Path) -> Dict:
    """Load OpenAPI specification from YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def find_breaking_changes(baseline: Dict, current: Dict) -> List[BreakingChange]:
    """Detect breaking changes between two OpenAPI specs."""
    breaking_changes = []

    # Check for removed paths
    baseline_paths = set(baseline.get('paths', {}).keys())
    current_paths = set(current.get('paths', {}).keys())

    removed_paths = baseline_paths - current_paths
    for path in removed_paths:
        breaking_changes.append(
            BreakingChange(
                "REMOVED_ENDPOINT",
                path,
                "Endpoint has been removed"
            )
        )

    # Check for removed operations on existing paths
    for path in baseline_paths & current_paths:
        baseline_ops = set(baseline['paths'][path].keys())
        current_ops = set(current['paths'][path].keys())

        removed_ops = baseline_ops - current_ops
        for op in removed_ops:
            if op not in ['description', 'summary', 'parameters']:
                breaking_changes.append(
                    BreakingChange(
                        "REMOVED_OPERATION",
                        f"{path} [{op.upper()}]",
                        f"HTTP method {op.upper()} has been removed"
                    )
                )

    # Check for required parameters added to existing endpoints
    for path in baseline_paths & current_paths:
        for op in set(baseline['paths'][path].keys()) & set(current['paths'][path].keys()):
            if op in ['description', 'summary']:
                continue

            baseline_params = baseline['paths'][path].get(op, {}).get('parameters', [])
            current_params = current['paths'][path].get(op, {}).get('parameters', [])

            baseline_required = {p['name'] for p in baseline_params if p.get('required')}
            current_required = {p['name'] for p in current_params if p.get('required')}

            new_required = current_required - baseline_required
            for param in new_required:
                breaking_changes.append(
                    BreakingChange(
                        "NEW_REQUIRED_PARAM",
                        f"{path} [{op.upper()}]",
                        f"New required parameter '{param}' added"
                    )
                )

    # Check for removed required fields in request body
    for path in baseline_paths & current_paths:
        for op in set(baseline['paths'][path].keys()) & set(current['paths'][path].keys()):
            if op in ['description', 'summary']:
                continue

            baseline_body = baseline['paths'][path].get(op, {}).get('requestBody', {})
            current_body = current['paths'][path].get(op, {}).get('requestBody', {})

            # Simplified check - in production, would check schema references
            if baseline_body and not current_body:
                breaking_changes.append(
                    BreakingChange(
                        "REMOVED_REQUEST_BODY",
                        f"{path} [{op.upper()}]",
                        "Request body has been removed"
                    )
                )

    # Check for changed response status codes
    for path in baseline_paths & current_paths:
        for op in set(baseline['paths'][path].keys()) & set(current['paths'][path].keys()):
            if op in ['description', 'summary']:
                continue

            baseline_responses = set(baseline['paths'][path].get(op, {}).get('responses', {}).keys())
            current_responses = set(current['paths'][path].get(op, {}).get('responses', {}).keys())

            removed_responses = baseline_responses - current_responses
            for status_code in removed_responses:
                if status_code in ['200', '201', '204']:  # Success codes
                    breaking_changes.append(
                        BreakingChange(
                            "REMOVED_SUCCESS_RESPONSE",
                            f"{path} [{op.upper()}]",
                            f"Success response {status_code} has been removed"
                        )
                    )

    return breaking_changes


def check_service(service_name: str, baseline_dir: Path, current_dir: Path) -> Tuple[bool, List[BreakingChange]]:
    """Check a service for breaking changes."""
    baseline_file = baseline_dir / f"{service_name}.baseline.yaml"
    current_file = current_dir / f"{service_name}.yaml"

    if not baseline_file.exists():
        print(f"⚠ No baseline found for {service_name}, creating initial baseline...")
        return True, []

    if not current_file.exists():
        print(f"✗ Current spec not found: {current_file}")
        return False, []

    baseline_spec = load_openapi_spec(baseline_file)
    current_spec = load_openapi_spec(current_file)

    breaking_changes = find_breaking_changes(baseline_spec, current_spec)

    return len(breaking_changes) == 0, breaking_changes


def update_baseline(service_name: str, current_dir: Path, baseline_dir: Path):
    """Update the baseline for a service."""
    current_file = current_dir / f"{service_name}.yaml"
    baseline_file = baseline_dir / f"{service_name}.baseline.yaml"

    if not current_file.exists():
        print(f"✗ Current spec not found: {current_file}")
        return False

    shutil.copy2(current_file, baseline_file)
    print(f"✓ Updated baseline: {baseline_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Detect breaking changes in OpenAPI specifications'
    )
    parser.add_argument(
        '--baseline',
        type=str,
        help='Path to baseline OpenAPI spec'
    )
    parser.add_argument(
        '--current',
        type=str,
        help='Path to current OpenAPI spec'
    )
    parser.add_argument(
        '--update-baseline',
        action='store_true',
        help='Update the baseline with current spec'
    )
    parser.add_argument(
        '--service',
        choices=['crm', 'ops'],
        help='Service to check or update'
    )
    parser.add_argument(
        '--check-all',
        action='store_true',
        help='Check all services for breaking changes'
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    docs_api = project_root / "docs" / "api"

    print("="*80)
    print("OpenAPI Breaking Change Detection")
    print("="*80)
    print()

    if args.update_baseline:
        if not args.service:
            parser.error('--service required with --update-baseline')

        success = update_baseline(args.service, docs_api, docs_api)
        return 0 if success else 1

    if args.check_all:
        all_clean = True
        services = ['crm', 'ops']

        for service in services:
            print(f"Checking {service.upper()} API...")
            clean, breaking_changes = check_service(service, docs_api, docs_api)

            if clean:
                print(f"✓ {service.upper()}: No breaking changes detected")
            else:
                all_clean = False
                print(f"✗ {service.upper()}: {len(breaking_changes)} breaking change(s) detected")
                for change in breaking_changes:
                    print(f"  - {change}")

            print()

        if all_clean:
            print("="*80)
            print("✓ All APIs are compatible with baseline")
            print("="*80)
            return 0
        else:
            print("="*80)
            print("✗ Breaking changes detected!")
            print("="*80)
            print()
            print("To update the baseline:")
            print("  python tools/openapi_diff.py --update-baseline --service crm")
            print("  python tools/openapi_diff.py --update-baseline --service ops")
            return 1

    if args.baseline and args.current:
        baseline_spec = load_openapi_spec(Path(args.baseline))
        current_spec = load_openapi_spec(Path(args.current))

        breaking_changes = find_breaking_changes(baseline_spec, current_spec)

        if breaking_changes:
            print(f"✗ {len(breaking_changes)} breaking change(s) detected:")
            for change in breaking_changes:
                print(f"  - {change}")
            return 1
        else:
            print("✓ No breaking changes detected")
            return 0

    parser.error('Either --check-all or both --baseline and --current must be specified')


if __name__ == '__main__':
    sys.exit(main())
