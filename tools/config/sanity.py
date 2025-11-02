#!/usr/bin/env python3
"""
Configuration Sanity Checker.

Validates .env files for required variables, format compliance, and secrets hygiene.
Never hits the network - all checks are local.
"""

import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


class Status(Enum):
    """Validation status for each environment variable."""
    FOUND = "✓ Found"
    MISSING = "✗ Missing"
    PLACEHOLDER = "⚠ Placeholder"
    INVALID = "✗ Invalid"
    WEAK = "⚠ Weak"


class Severity(Enum):
    """Severity level for validation failures."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationRule:
    """Definition of a single validation rule."""
    key: str
    required: bool
    description: str
    validator: Optional[callable] = None
    prod_required: bool = False  # Must not be placeholder in production
    min_length: Optional[int] = None
    pattern: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    key: str
    status: Status
    value: Optional[str]
    message: str
    severity: Severity


class EnvValidator:
    """Validates environment variables against defined rules."""

    # Known placeholder patterns that should not be used in production
    PLACEHOLDER_PATTERNS = [
        r"change.*in.*production",
        r"your-.*-here",
        r"replace-me",
        r"todo",
        r"fixme",
        r"example\.com",
        r"localhost",
        r"127\.0\.0\.1",
        r"dev-secret",
        r"test-secret",
        r"dummy",
    ]

    # Validation rules for all required environment variables
    VALIDATION_RULES = [
        # JWT Secrets
        ValidationRule(
            key="CRM_SECRET_KEY",
            required=True,
            prod_required=True,
            description="JWT secret for CRM API",
            min_length=32,
        ),
        ValidationRule(
            key="OPS_SECRET_KEY",
            required=True,
            prod_required=True,
            description="JWT secret for Ops API",
            min_length=32,
        ),

        # Database Configuration
        ValidationRule(
            key="CRM_DB_HOST",
            required=True,
            description="CRM database host",
        ),
        ValidationRule(
            key="CRM_DB_NAME",
            required=True,
            description="CRM database name",
        ),
        ValidationRule(
            key="CRM_DB_USER",
            required=True,
            description="CRM database user",
        ),
        ValidationRule(
            key="CRM_DB_PASSWORD",
            required=True,
            prod_required=True,
            description="CRM database password",
            min_length=8,
        ),
        ValidationRule(
            key="OPS_DB_HOST",
            required=True,
            description="Ops database host",
        ),
        ValidationRule(
            key="OPS_DB_NAME",
            required=True,
            description="Ops database name",
        ),
        ValidationRule(
            key="OPS_DB_USER",
            required=True,
            description="Ops database user",
        ),
        ValidationRule(
            key="OPS_DB_PASSWORD",
            required=True,
            prod_required=True,
            description="Ops database password",
            min_length=8,
        ),

        # Redis
        ValidationRule(
            key="REDIS_HOST",
            required=True,
            description="Redis host",
        ),
        ValidationRule(
            key="REDIS_PORT",
            required=True,
            description="Redis port",
            validator=lambda v: v.isdigit() and 1 <= int(v) <= 65535,
        ),

        # API URLs (for frontend)
        ValidationRule(
            key="VITE_CRM_API_URL",
            required=True,
            description="CRM API base URL for frontend",
            validator=lambda v: urlparse(v).scheme in ["http", "https"],
        ),
        ValidationRule(
            key="VITE_OPS_API_URL",
            required=True,
            description="Ops API base URL for frontend",
            validator=lambda v: urlparse(v).scheme in ["http", "https"],
        ),

        # Celery
        ValidationRule(
            key="CELERY_BROKER_URL",
            required=True,
            description="Celery broker URL",
            validator=lambda v: v.startswith("redis://") or v.startswith("amqp://"),
        ),

        # Webhook Secrets (optional but recommended)
        ValidationRule(
            key="TWILIO_AUTH_TOKEN",
            required=False,
            prod_required=False,
            description="Twilio webhook auth token",
        ),
        ValidationRule(
            key="FB_APP_SECRET",
            required=False,
            prod_required=False,
            description="Facebook app secret",
        ),
        ValidationRule(
            key="GOOGLE_WEBHOOK_SECRET",
            required=False,
            prod_required=False,
            description="Google webhook secret",
        ),

        # CORS Origins
        ValidationRule(
            key="CRM_CORS_ORIGINS",
            required=True,
            description="CRM CORS allowed origins",
        ),
        ValidationRule(
            key="OPS_CORS_ORIGINS",
            required=True,
            description="Ops CORS allowed origins",
        ),
    ]

    def __init__(self, env_file: Path, mode: str = "dev"):
        """
        Initialize validator.

        Args:
            env_file: Path to .env file
            mode: Runtime mode ('dev' or 'prod')
        """
        self.env_file = env_file
        self.mode = mode
        self.env_vars: Dict[str, str] = {}
        self.results: List[ValidationResult] = []

    def load_env_file(self) -> bool:
        """Load environment variables from file."""
        if not self.env_file.exists():
            print(f"✗ Environment file not found: {self.env_file}")
            return False

        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.env_vars[key.strip()] = value.strip()
            return True
        except Exception as e:
            print(f"✗ Error reading {self.env_file}: {e}")
            return False

    def is_placeholder(self, value: str) -> bool:
        """Check if value appears to be a placeholder."""
        value_lower = value.lower()
        for pattern in self.PLACEHOLDER_PATTERNS:
            if re.search(pattern, value_lower):
                return True
        return False

    def validate_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate a single rule."""
        value = self.env_vars.get(rule.key)

        # Check if missing
        if value is None or value == "":
            if rule.required:
                return ValidationResult(
                    key=rule.key,
                    status=Status.MISSING,
                    value=None,
                    message=f"Required variable not set: {rule.description}",
                    severity=Severity.ERROR,
                )
            else:
                return ValidationResult(
                    key=rule.key,
                    status=Status.MISSING,
                    value=None,
                    message=f"Optional variable not set: {rule.description}",
                    severity=Severity.INFO,
                )

        # Check if placeholder in production (critical error)
        if self.mode == "prod" and rule.prod_required and self.is_placeholder(value):
            return ValidationResult(
                key=rule.key,
                status=Status.INVALID,
                value=value[:20] + "..." if len(value) > 20 else value,
                message=f"Placeholder value not allowed in production",
                severity=Severity.ERROR,
            )

        # Check minimum length
        if rule.min_length and len(value) < rule.min_length:
            return ValidationResult(
                key=rule.key,
                status=Status.WEAK,
                value=value[:20] + "..." if len(value) > 20 else value,
                message=f"Value too short (min: {rule.min_length} chars, got: {len(value)})",
                severity=Severity.WARNING if self.mode == "dev" else Severity.ERROR,
            )

        # Check pattern
        if rule.pattern and not re.match(rule.pattern, value):
            return ValidationResult(
                key=rule.key,
                status=Status.INVALID,
                value=value[:20] + "..." if len(value) > 20 else value,
                message=f"Value does not match required pattern",
                severity=Severity.ERROR,
            )

        # Run custom validator
        if rule.validator:
            try:
                if not rule.validator(value):
                    return ValidationResult(
                        key=rule.key,
                        status=Status.INVALID,
                        value=value[:20] + "..." if len(value) > 20 else value,
                        message=f"Value failed validation check",
                        severity=Severity.ERROR,
                    )
            except Exception as e:
                return ValidationResult(
                    key=rule.key,
                    status=Status.INVALID,
                    value=value[:20] + "..." if len(value) > 20 else value,
                    message=f"Validation error: {str(e)}",
                    severity=Severity.ERROR,
                )

        # Check for common placeholders as warning
        if self.is_placeholder(value):
            return ValidationResult(
                key=rule.key,
                status=Status.PLACEHOLDER,
                value=value[:20] + "..." if len(value) > 20 else value,
                message=f"Appears to be a placeholder value",
                severity=Severity.WARNING,
            )

        # All checks passed
        return ValidationResult(
            key=rule.key,
            status=Status.FOUND,
            value=value[:20] + "..." if len(value) > 20 else value,
            message=rule.description,
            severity=Severity.INFO,
        )

    def validate_all(self) -> bool:
        """
        Run all validation rules.

        Returns:
            True if all checks pass, False otherwise
        """
        for rule in self.VALIDATION_RULES:
            result = self.validate_rule(rule)
            self.results.append(result)

        # Count errors and warnings
        errors = sum(1 for r in self.results if r.severity == Severity.ERROR)
        warnings = sum(1 for r in self.results if r.severity == Severity.WARNING)

        return errors == 0

    def print_results(self):
        """Print validation results in a formatted table."""
        print("\n" + "=" * 100)
        print(f"Configuration Validation Report - Mode: {self.mode.upper()}")
        print("=" * 100)
        print(f"Environment File: {self.env_file}")
        print()

        # Print table header
        print(f"{'Variable':<35} {'Status':<15} {'Message':<50}")
        print("-" * 100)

        # Group by severity
        for severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]:
            severity_results = [r for r in self.results if r.severity == severity]
            if severity_results:
                for result in severity_results:
                    status_str = result.status.value
                    print(f"{result.key:<35} {status_str:<15} {result.message:<50}")

        print("-" * 100)

        # Summary
        errors = sum(1 for r in self.results if r.severity == Severity.ERROR)
        warnings = sum(1 for r in self.results if r.severity == Severity.WARNING)
        passed = sum(1 for r in self.results if r.status == Status.FOUND)
        total = len(self.results)

        print(f"\nSummary: {passed}/{total} variables OK | "
              f"{errors} errors | {warnings} warnings")

        if errors > 0:
            print("\n✗ VALIDATION FAILED - Fix errors before deploying to production")
            return False
        elif warnings > 0:
            print("\n⚠ VALIDATION PASSED WITH WARNINGS - Review before deploying")
            return True
        else:
            print("\n✓ VALIDATION PASSED - All checks successful")
            return True


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) > 1:
        env_file = Path(sys.argv[1])
    else:
        # Try .env first, fall back to .env.example
        env_file = Path(".env")
        if not env_file.exists():
            env_file = Path(".env.example")

    # Determine mode from environment or default to dev
    mode = os.getenv("MODE", os.getenv("ENVIRONMENT", "dev")).lower()
    if mode not in ["dev", "prod", "production"]:
        mode = "dev"
    if mode == "production":
        mode = "prod"

    print(f"Validating configuration from: {env_file}")
    print(f"Runtime mode: {mode}")

    # Create validator and run checks
    validator = EnvValidator(env_file, mode)

    if not validator.load_env_file():
        sys.exit(1)

    success = validator.validate_all()
    validator.print_results()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
