#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Database Migration Wrapper.

Unified interface for running Alembic migrations across CRM and Ops services.
Handles both stub (test) and production (real SQLAlchemy) environments.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class MigrationManager:
    """Manages database migrations for multiple services."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services = {
            "crm": project_root / "crm_api",
            "ops": project_root / "ops_api",
        }

    def check_alembic_setup(self, service: str) -> bool:
        """Check if Alembic is set up for a service."""
        service_dir = self.services.get(service)
        if not service_dir:
            print(f"❌ Unknown service: {service}")
            return False

        alembic_ini = service_dir / "alembic.ini"
        alembic_dir = service_dir / "alembic"

        if not alembic_ini.exists():
            print(f"⚠️  Alembic not configured for {service}")
            print(f"   Missing: {alembic_ini}")
            return False

        if not alembic_dir.exists():
            print(f"⚠️  Alembic directory not found for {service}")
            print(f"   Missing: {alembic_dir}")
            return False

        return True

    def run_migration(self, service: str, revision: str = "head", dry_run: bool = False) -> bool:
        """
        Run migration for a service.

        Args:
            service: Service name (crm, ops, or all)
            revision: Target revision (default: head)
            dry_run: Print commands without executing

        Returns:
            True if successful, False otherwise
        """
        if service == "all":
            success = True
            for svc in self.services.keys():
                if not self.run_migration(svc, revision, dry_run):
                    success = False
            return success

        if not self.check_alembic_setup(service):
            return False

        service_dir = self.services[service]
        os.chdir(service_dir)

        cmd = ["alembic", "upgrade", revision]

        print(f"\n{'='*80}")
        print(f"Migrating {service.upper()} API to {revision}")
        print(f"{'='*80}")
        print(f"Working directory: {service_dir}")
        print(f"Command: {' '.join(cmd)}")

        if dry_run:
            print("🔍 DRY RUN - Command not executed")
            return True

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                print(result.stdout)
                print(f"✅ {service.upper()} migration completed successfully")
                return True
            else:
                print(result.stdout)
                print(result.stderr)
                print(f"❌ {service.upper()} migration failed")
                return False

        except FileNotFoundError:
            print("❌ Alembic not found. Install with: pip install alembic")
            print("   Or use stub version for testing without database")
            return False
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False
        finally:
            os.chdir(self.project_root)

    def show_current(self, service: str) -> bool:
        """Show current migration revision."""
        if service == "all":
            success = True
            for svc in self.services.keys():
                if not self.show_current(svc):
                    success = False
            return success

        if not self.check_alembic_setup(service):
            return False

        service_dir = self.services[service]
        os.chdir(service_dir)

        cmd = ["alembic", "current"]

        print(f"\n{'='*80}")
        print(f"{service.upper()} API - Current Revision")
        print(f"{'='*80}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(result.stdout)
            return result.returncode == 0
        except FileNotFoundError:
            print("⚠️  Alembic not installed (stub mode)")
            return True
        finally:
            os.chdir(self.project_root)

    def show_history(self, service: str, count: int = 10) -> bool:
        """Show migration history."""
        if service == "all":
            success = True
            for svc in self.services.keys():
                if not self.show_history(svc, count):
                    success = False
            return success

        if not self.check_alembic_setup(service):
            return False

        service_dir = self.services[service]
        os.chdir(service_dir)

        cmd = ["alembic", "history", "-n", str(count)]

        print(f"\n{'='*80}")
        print(f"{service.upper()} API - Migration History (last {count})")
        print(f"{'='*80}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(result.stdout)
            return result.returncode == 0
        except FileNotFoundError:
            print("⚠️  Alembic not installed (stub mode)")
            # Read versions directory manually
            versions_dir = service_dir / "alembic" / "versions"
            if versions_dir.exists():
                migrations = sorted(versions_dir.glob("*.py"))
                print(f"Found {len(migrations)} migration files:")
                for mig in migrations[-count:]:
                    print(f"  - {mig.name}")
            return True
        finally:
            os.chdir(self.project_root)

    def create_migration(self, service: str, message: str, autogenerate: bool = True) -> bool:
        """
        Create a new migration.

        Args:
            service: Service name (crm or ops)
            message: Migration message
            autogenerate: Use autogenerate (requires SQLAlchemy)

        Returns:
            True if successful
        """
        if service == "all":
            print("❌ Cannot create migration for 'all'. Specify crm or ops.")
            return False

        if not self.check_alembic_setup(service):
            return False

        service_dir = self.services[service]
        os.chdir(service_dir)

        if autogenerate:
            cmd = ["alembic", "revision", "--autogenerate", "-m", message]
        else:
            cmd = ["alembic", "revision", "-m", message]

        print(f"\n{'='*80}")
        print(f"Creating migration for {service.upper()} API")
        print(f"{'='*80}")
        print(f"Message: {message}")
        print(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(result.stdout)

            if result.returncode == 0:
                print(f"✅ Migration created successfully")
                return True
            else:
                print(result.stderr)
                print(f"❌ Migration creation failed")
                return False

        except FileNotFoundError:
            print("❌ Alembic not found. Install with: pip install alembic")
            return False
        finally:
            os.chdir(self.project_root)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database migration wrapper for CRM and Ops APIs"
    )

    subparsers = parser.add_subparsers(dest="command", help="Migration command")

    # Migrate command
    migrate_parser = subparsers.add_parser("upgrade", help="Upgrade database to revision")
    migrate_parser.add_argument(
        "service",
        choices=["crm", "ops", "all"],
        help="Service to migrate"
    )
    migrate_parser.add_argument(
        "--revision",
        default="head",
        help="Target revision (default: head)"
    )
    migrate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing"
    )

    # Current command
    current_parser = subparsers.add_parser("current", help="Show current revision")
    current_parser.add_argument(
        "service",
        choices=["crm", "ops", "all"],
        help="Service to check"
    )

    # History command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument(
        "service",
        choices=["crm", "ops", "all"],
        help="Service to check"
    )
    history_parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of migrations to show (default: 10)"
    )

    # Create command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument(
        "service",
        choices=["crm", "ops"],
        help="Service for migration"
    )
    create_parser.add_argument(
        "-m", "--message",
        required=True,
        help="Migration message"
    )
    create_parser.add_argument(
        "--no-autogenerate",
        action="store_true",
        help="Don't use autogenerate"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    manager = MigrationManager(project_root)

    # Execute command
    if args.command == "upgrade":
        success = manager.run_migration(
            args.service,
            args.revision,
            args.dry_run
        )
    elif args.command == "current":
        success = manager.show_current(args.service)
    elif args.command == "history":
        success = manager.show_history(args.service, args.count)
    elif args.command == "create":
        success = manager.create_migration(
            args.service,
            args.message,
            not args.no_autogenerate
        )
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
