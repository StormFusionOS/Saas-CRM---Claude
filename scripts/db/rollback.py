#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Database Rollback Script.

Rolls back database migrations using Alembic downgrade.
Supports rolling back one revision or to a specific revision.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class RollbackManager:
    """Manages database rollbacks for multiple services."""

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

    def get_current_revision(self, service: str) -> Optional[str]:
        """Get current revision for a service."""
        service_dir = self.services[service]
        os.chdir(service_dir)

        try:
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Parse revision from output
                for line in result.stdout.split('\n'):
                    if '(head)' in line or 'current' in line.lower():
                        # Extract revision hash (first word)
                        parts = line.split()
                        if parts:
                            return parts[0]
                return None
            else:
                return None

        except FileNotFoundError:
            print("⚠️  Alembic not installed (stub mode)")
            return None
        finally:
            os.chdir(self.project_root)

    def get_migration_history(self, service: str, limit: int = 10) -> list:
        """Get migration history for a service."""
        service_dir = self.services[service]
        versions_dir = service_dir / "alembic" / "versions"

        if not versions_dir.exists():
            return []

        migrations = []
        for mig_file in sorted(versions_dir.glob("*.py")):
            # Read revision from file
            content = mig_file.read_text()
            revision = None
            down_revision = None

            for line in content.split('\n'):
                if line.startswith("revision ="):
                    revision = line.split('=')[1].strip().strip("'\"")
                elif line.startswith("down_revision ="):
                    down_revision = line.split('=')[1].strip().strip("'\"")

            if revision:
                migrations.append({
                    "file": mig_file.name,
                    "revision": revision,
                    "down_revision": down_revision
                })

        return migrations[-limit:]

    def rollback(
        self,
        service: str,
        steps: int = 1,
        target_revision: Optional[str] = None,
        dry_run: bool = False
    ) -> bool:
        """
        Rollback migrations.

        Args:
            service: Service name (crm, ops, or all)
            steps: Number of revisions to rollback
            target_revision: Specific revision to rollback to
            dry_run: Print commands without executing

        Returns:
            True if successful
        """
        if service == "all":
            success = True
            for svc in self.services.keys():
                if not self.rollback(svc, steps, target_revision, dry_run):
                    success = False
            return success

        if not self.check_alembic_setup(service):
            return False

        service_dir = self.services[service]
        os.chdir(service_dir)

        # Determine target
        if target_revision:
            target = target_revision
        elif steps == 1:
            target = "-1"
        else:
            target = f"-{steps}"

        cmd = ["alembic", "downgrade", target]

        print(f"\n{'='*80}")
        print(f"Rolling back {service.upper()} API")
        print(f"{'='*80}")
        print(f"Working directory: {service_dir}")

        # Show current revision
        current = self.get_current_revision(service)
        if current:
            print(f"Current revision: {current}")

        # Show migration history
        print(f"\nMigration history:")
        migrations = self.get_migration_history(service)
        for i, mig in enumerate(reversed(migrations)):
            is_current = (current and current in mig["file"])
            marker = "→" if is_current else " "
            print(f"  {marker} {mig['file']} (rev: {mig['revision'][:8]}...)")

        print(f"\nCommand: {' '.join(cmd)}")

        if dry_run:
            print("🔍 DRY RUN - Command not executed")
            return True

        # Confirm before rollback
        if not self._confirm_rollback(service, steps, target_revision):
            print("❌ Rollback cancelled")
            return False

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                print(result.stdout)
                print(f"✅ {service.upper()} rollback completed successfully")

                # Show new current revision
                new_current = self.get_current_revision(service)
                if new_current:
                    print(f"   New current revision: {new_current}")

                return True
            else:
                print(result.stdout)
                print(result.stderr)
                print(f"❌ {service.upper()} rollback failed")
                return False

        except FileNotFoundError:
            print("❌ Alembic not found. Install with: pip install alembic")
            print("   Or use stub version for testing without database")
            return False
        except Exception as e:
            print(f"❌ Rollback error: {e}")
            return False
        finally:
            os.chdir(self.project_root)

    def _confirm_rollback(
        self,
        service: str,
        steps: int,
        target_revision: Optional[str]
    ) -> bool:
        """Confirm rollback operation."""
        print(f"\n⚠️  WARNING: This will rollback {steps} revision(s) for {service.upper()} API")

        if target_revision:
            print(f"   Target revision: {target_revision}")

        print("   This operation may result in data loss!")
        print("   Ensure you have a backup before proceeding.")

        response = input("\nContinue? [y/N]: ").strip().lower()
        return response in ['y', 'yes']


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rollback database migrations for CRM and Ops APIs"
    )

    parser.add_argument(
        "service",
        choices=["crm", "ops", "all"],
        help="Service to rollback"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of revisions to rollback (default: 1)"
    )
    parser.add_argument(
        "--to",
        dest="target_revision",
        help="Target revision to rollback to"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    manager = RollbackManager(project_root)

    # Override confirmation if --yes flag provided
    if args.yes:
        manager._confirm_rollback = lambda *a, **k: True

    success = manager.rollback(
        args.service,
        args.steps,
        args.target_revision,
        args.dry_run
    )

    if success:
        print("\n✅ Rollback completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Rollback failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
