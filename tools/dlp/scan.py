#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Data Loss Prevention (DLP) Scanner

Scans files for sensitive data patterns to prevent accidental commits.

Features:
- Detects PII, credentials, API keys, secrets
- Configurable patterns and exclusions
- Whitelist support for false positives
- CI/CD integration (exit code 1 on findings)
- JSON reports for automation

Usage:
    # Scan all files
    python tools/dlp/scan.py

    # Scan specific directory
    python tools/dlp/scan.py --path docs/

    # Scan with fail on findings (for CI)
    python tools/dlp/scan.py --fail-on-findings

    # Generate JSON report
    python tools/dlp/scan.py --report dlp_report.json

    # Test scanner with sample data
    python tools/dlp/scan.py --test
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# Sensitive data patterns
PATTERNS = {
    # Personally Identifiable Information (PII)
    "ssn": {
        "name": "Social Security Number",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "severity": "high",
        "description": "US Social Security Number (XXX-XX-XXXX)"
    },
    "email": {
        "name": "Email Address",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "severity": "medium",
        "description": "Email address"
    },
    "phone": {
        "name": "Phone Number",
        "pattern": r"\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
        "severity": "medium",
        "description": "Phone number"
    },
    "credit_card": {
        "name": "Credit Card Number",
        "pattern": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "severity": "high",
        "description": "Credit card number (16 digits)"
    },
    "ip_address": {
        "name": "IP Address",
        "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "severity": "low",
        "description": "IPv4 address"
    },

    # Credentials and Secrets
    "api_key": {
        "name": "API Key",
        "pattern": r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
        "severity": "critical",
        "description": "API key assignment"
    },
    "secret_key": {
        "name": "Secret Key",
        "pattern": r"(?i)(secret[_-]?key|secretkey)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
        "severity": "critical",
        "description": "Secret key assignment"
    },
    "password": {
        "name": "Password",
        "pattern": r"(?i)password\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
        "severity": "critical",
        "description": "Hardcoded password"
    },
    "aws_access_key": {
        "name": "AWS Access Key",
        "pattern": r"\b(AKIA[0-9A-Z]{16})\b",
        "severity": "critical",
        "description": "AWS access key ID"
    },
    "aws_secret_key": {
        "name": "AWS Secret Key",
        "pattern": r"(?i)aws[_-]?secret[_-]?access[_-]?key['\"]?\s*[=:]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?",
        "severity": "critical",
        "description": "AWS secret access key"
    },
    "private_key": {
        "name": "Private Key",
        "pattern": r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
        "severity": "critical",
        "description": "Private cryptographic key"
    },
    "jwt_token": {
        "name": "JWT Token",
        "pattern": r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
        "severity": "high",
        "description": "JSON Web Token"
    },
    "github_token": {
        "name": "GitHub Token",
        "pattern": r"\bgh[ps]_[a-zA-Z0-9]{36,}\b",
        "severity": "critical",
        "description": "GitHub personal access token"
    },
    "slack_token": {
        "name": "Slack Token",
        "pattern": r"\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}\b",
        "severity": "critical",
        "description": "Slack API token"
    },

    # Database Credentials
    "connection_string": {
        "name": "Database Connection String",
        "pattern": r"(?i)(mysql|postgres|mongodb|redis)://[^:]+:[^@]+@[^/]+",
        "severity": "critical",
        "description": "Database connection string with credentials"
    }
}


@dataclass
class Finding:
    """DLP scan finding"""
    file_path: str
    line_number: int
    pattern_id: str
    pattern_name: str
    severity: str
    description: str
    matched_text: str
    context: str  # Surrounding lines


@dataclass
class ScanResult:
    """DLP scan result"""
    timestamp: str
    total_files_scanned: int
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings: List[Finding]
    whitelisted_findings: int = 0


class DLPScanner:
    """
    Data Loss Prevention Scanner

    Scans files for sensitive data patterns.
    """

    def __init__(
        self,
        patterns: Dict = PATTERNS,
        whitelist_path: str = "tools/dlp/whitelist.json",
        excluded_dirs: Optional[List[str]] = None
    ):
        """
        Initialize DLP scanner

        Args:
            patterns: Patterns to scan for
            whitelist_path: Path to whitelist file
            excluded_dirs: Directories to exclude from scanning
        """
        self.patterns = patterns
        self.whitelist_path = Path(whitelist_path)
        self.excluded_dirs = excluded_dirs or [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            ".cache"
        ]

        # Load whitelist
        self.whitelist = self._load_whitelist()

    def scan_file(self, file_path: Path) -> List[Finding]:
        """
        Scan a single file

        Args:
            file_path: Path to file

        Returns:
            List of findings
        """
        findings = []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, start=1):
                for pattern_id, pattern_config in self.patterns.items():
                    pattern = pattern_config["pattern"]
                    matches = re.finditer(pattern, line)

                    for match in matches:
                        matched_text = match.group(0)

                        # Check whitelist
                        if self._is_whitelisted(file_path, line_num, pattern_id, matched_text):
                            continue

                        # Get context (3 lines before/after)
                        context_start = max(0, line_num - 4)
                        context_end = min(len(lines), line_num + 3)
                        context = '\n'.join(lines[context_start:context_end])

                        finding = Finding(
                            file_path=str(file_path),
                            line_number=line_num,
                            pattern_id=pattern_id,
                            pattern_name=pattern_config["name"],
                            severity=pattern_config["severity"],
                            description=pattern_config["description"],
                            matched_text=matched_text,
                            context=context
                        )

                        findings.append(finding)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)

        return findings

    def scan_directory(
        self,
        directory: Path,
        file_extensions: Optional[List[str]] = None
    ) -> ScanResult:
        """
        Scan a directory recursively

        Args:
            directory: Directory to scan
            file_extensions: List of file extensions to scan (None = all text files)

        Returns:
            Scan result
        """
        if file_extensions is None:
            file_extensions = [
                '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rb',
                '.php', '.c', '.cpp', '.h', '.hpp', '.cs', '.sh', '.bash',
                '.yaml', '.yml', '.json', '.xml', '.env', '.config', '.ini',
                '.md', '.txt', '.rst', '.csv', '.sql'
            ]

        all_findings = []
        files_scanned = 0

        for file_path in directory.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                continue

            # Skip non-text files
            if file_path.suffix not in file_extensions:
                continue

            # Scan file
            findings = self.scan_file(file_path)
            all_findings.extend(findings)
            files_scanned += 1

        # Count by severity
        findings_by_severity = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        for finding in all_findings:
            findings_by_severity[finding.severity] += 1

        result = ScanResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_files_scanned=files_scanned,
            total_findings=len(all_findings),
            findings_by_severity=findings_by_severity,
            findings=all_findings
        )

        return result

    def _is_whitelisted(
        self,
        file_path: Path,
        line_number: int,
        pattern_id: str,
        matched_text: str
    ) -> bool:
        """Check if a finding is whitelisted"""
        file_str = str(file_path)

        for entry in self.whitelist:
            # Match file path (support wildcards)
            if 'file_pattern' in entry:
                if not re.search(entry['file_pattern'], file_str):
                    continue

            # Match exact file
            if 'file' in entry and entry['file'] != file_str:
                continue

            # Match line number
            if 'line' in entry and entry['line'] != line_number:
                continue

            # Match pattern ID
            if 'pattern_id' in entry and entry['pattern_id'] != pattern_id:
                continue

            # Match reason (always allow if reason is provided)
            if 'reason' in entry:
                return True

        return False

    def _load_whitelist(self) -> List[Dict]:
        """Load whitelist from file"""
        if not self.whitelist_path.exists():
            return []

        try:
            return json.loads(self.whitelist_path.read_text())
        except Exception as e:
            print(f"Warning: Failed to load whitelist: {e}", file=sys.stderr)
            return []


def print_result(result: ScanResult):
    """Print scan result to console"""
    print(f"\n=== DLP Scan Results ===")
    print(f"Scanned: {result.total_files_scanned} files")
    print(f"Findings: {result.total_findings}")
    print(f"  Critical: {result.findings_by_severity['critical']}")
    print(f"  High: {result.findings_by_severity['high']}")
    print(f"  Medium: {result.findings_by_severity['medium']}")
    print(f"  Low: {result.findings_by_severity['low']}")

    if result.total_findings > 0:
        print(f"\n=== Findings ===\n")

        for finding in result.findings:
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(finding.severity, "⚪")

            print(f"{severity_icon} {finding.severity.upper()} - {finding.pattern_name}")
            print(f"  File: {finding.file_path}:{finding.line_number}")
            print(f"  Found: {finding.matched_text}")
            print(f"  Description: {finding.description}")
            print()


def create_sample_violations():
    """Create sample file with violations for testing"""
    sample_path = Path("tools/dlp/test_sample.txt")
    sample_path.parent.mkdir(parents=True, exist_ok=True)

    sample_content = """
# DLP Scanner Test Sample
# This file contains sample violations for testing

# PII
SSN: 123-45-6789
Email: john.doe@example.com
Phone: +1-555-123-4567
Credit Card: 4111-1111-1111-1111

# Credentials
api_key = "abcdef1234567890abcdef1234567890"
secret_key = "secret_0123456789abcdefghijklmnop"
password = "MySecurePassword123!"

# AWS
AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Database
connection_string = "postgres://admin:password123@db.example.com:5432/mydb"

# JWT
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

# Private Key
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
"""

    sample_path.write_text(sample_content)
    print(f"Created test sample: {sample_path}")
    return sample_path


def main():
    parser = argparse.ArgumentParser(description="DLP Scanner")
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help="Path to scan (default: current directory)"
    )
    parser.add_argument(
        '--fail-on-findings',
        action='store_true',
        help="Exit with code 1 if findings are found (for CI)"
    )
    parser.add_argument(
        '--report',
        type=str,
        help="Export results to JSON file"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help="Create test sample and scan it"
    )

    args = parser.parse_args()

    # Test mode
    if args.test:
        print("=== DLP Scanner Test Mode ===\n")
        sample_path = create_sample_violations()

        scanner = DLPScanner()
        findings = scanner.scan_file(sample_path)

        print(f"\nFound {len(findings)} violations in test sample:\n")
        for finding in findings:
            print(f"  - {finding.severity.upper()}: {finding.pattern_name} (line {finding.line_number})")

        print("\n✓ Test complete")
        return

    # Normal scan
    scanner = DLPScanner()
    scan_path = Path(args.path)

    print(f"Scanning: {scan_path}")

    if scan_path.is_file():
        # Scan single file
        findings = scanner.scan_file(scan_path)
        result = ScanResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_files_scanned=1,
            total_findings=len(findings),
            findings_by_severity={
                "critical": sum(1 for f in findings if f.severity == "critical"),
                "high": sum(1 for f in findings if f.severity == "high"),
                "medium": sum(1 for f in findings if f.severity == "medium"),
                "low": sum(1 for f in findings if f.severity == "low")
            },
            findings=findings
        )
    else:
        # Scan directory
        result = scanner.scan_directory(scan_path)

    # Print results
    print_result(result)

    # Export report
    if args.report:
        report_path = Path(args.report)
        report_path.write_text(json.dumps(asdict(result), indent=2, default=str))
        print(f"\n✓ Report exported to: {report_path}")

    # Fail on findings (for CI)
    if args.fail_on_findings and result.total_findings > 0:
        print("\n❌ DLP scan failed - sensitive data detected")
        sys.exit(1)

    print("\n✓ DLP scan complete")


if __name__ == "__main__":
    main()
