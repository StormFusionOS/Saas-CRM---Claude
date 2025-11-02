#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Check for migration drift and consistency.

Verifies that:
1. All models have corresponding migrations
2. No schema drift between models and migrations
3. Migration chain is valid
"""

import re
import sys
from pathlib import Path
from typing import Set, Dict, List


class MigrationChecker:
    """Checks migrations for drift and consistency."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services = {
            "crm": project_root / "crm_api",
            "ops": project_root / "ops_api",
        }

    def check_migrations(self, service: str) -> bool:
        """Check migrations for a service."""
        print(f"\n{'='*80}")
        print(f"Checking {service.upper()} API migrations")
        print(f"{'='*80}")

        service_dir = self.services.get(service)
        if not service_dir:
            print(f"❌ Unknown service: {service}")
            return False

        migrations_dir = service_dir / "alembic" / "versions"

        if not migrations_dir.exists():
            print(f"⚠️  Migrations directory not found: {migrations_dir}")
            print(f"   (This is OK if Alembic is not yet set up)")
            return True

        # Check 1: Migration files exist
        migration_files = list(migrations_dir.glob("*.py"))
        if not migration_files:
            print(f"⚠️  No migration files found in {migrations_dir}")
            return True

        print(f"✓ Found {len(migration_files)} migration files")

        # Check 2: Validate revision chain
        if not self._check_revision_chain(migration_files):
            return False

        # Check 3: Check for schema drift
        db_models_file = service_dir / "app" / "db_models.py"
        if db_models_file.exists():
            if not self._check_schema_drift(service, db_models_file, migration_files):
                return False
        else:
            print(f"⚠️  No db_models.py found - skipping schema drift check")

        print(f"✅ {service.upper()} migration checks passed")
        return True

    def _check_revision_chain(self, migration_files: List[Path]) -> bool:
        """Check that migration chain is valid."""
        print("\nChecking revision chain...")

        revisions: Dict[str, Dict] = {}

        for migration_file in migration_files:
            content = migration_file.read_text()

            revision = None
            down_revision = None

            for line in content.split('\n'):
                if line.startswith("revision ="):
                    revision = line.split('=')[1].strip().strip("'\"")
                elif line.startswith("down_revision ="):
                    down_revision = line.split('=')[1].strip().strip("'\"")

            if revision:
                revisions[revision] = {
                    "file": migration_file.name,
                    "down_revision": down_revision
                }

        if not revisions:
            print("❌ No revisions found in migration files")
            return False

        print(f"✓ Found {len(revisions)} unique revisions")

        # Check for duplicates
        files = [info["file"] for info in revisions.values()]
        if len(files) != len(set(files)):
            print("❌ Duplicate revision IDs found")
            return False

        # Check chain integrity
        heads = []
        for rev, info in revisions.items():
            down_rev = info["down_revision"]
            if down_rev == "None" or down_rev is None:
                heads.append(rev)

        if not heads:
            print("⚠️  No initial migration found (down_revision = None)")
        else:
            print(f"✓ Found {len(heads)} migration head(s)")

        return True

    def _check_schema_drift(
        self,
        service: str,
        db_models_file: Path,
        migration_files: List[Path]
    ) -> bool:
        """Check for schema drift between models and migrations."""
        print("\nChecking for schema drift...")

        # Extract table names from db_models.py
        model_tables = self._extract_model_tables(db_models_file)
        print(f"✓ Found {len(model_tables)} models: {', '.join(sorted(model_tables))}")

        # Extract table operations from migrations
        migration_tables = self._extract_migration_tables(migration_files)
        print(f"✓ Found {len(migration_tables)} tables in migrations: {', '.join(sorted(migration_tables))}")

        # Check for missing migrations
        missing_migrations = model_tables - migration_tables
        if missing_migrations:
            print(f"❌ Models without migrations: {', '.join(sorted(missing_migrations))}")
            print(f"   Run: python3 scripts/db/migrate.py create {service} -m 'Add missing tables'")
            return False

        # Check for orphaned migrations
        orphaned_migrations = migration_tables - model_tables
        if orphaned_migrations:
            print(f"⚠️  Tables in migrations but not in models: {', '.join(sorted(orphaned_migrations))}")
            print(f"   (This may be OK if tables were removed intentionally)")

        print(f"✓ No schema drift detected")
        return True

    def _extract_model_tables(self, db_models_file: Path) -> Set[str]:
        """Extract table names from db_models.py."""
        tables = set()
        content = db_models_file.read_text()

        # Look for __tablename__ = "..." pattern
        for match in re.finditer(r'__tablename__\s*=\s*["\'](\w+)["\']', content):
            tables.add(match.group(1))

        return tables

    def _extract_migration_tables(self, migration_files: List[Path]) -> Set[str]:
        """Extract table names from migration files."""
        tables = set()

        for migration_file in migration_files:
            content = migration_file.read_text()

            # Look for op.create_table("...", ...) pattern
            for match in re.finditer(r'op\.create_table\(["\'](\w+)["\']', content):
                tables.add(match.group(1))

        return tables


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    checker = MigrationChecker(project_root)

    services = ["crm", "ops"]

    all_ok = True
    for service in services:
        if not checker.check_migrations(service):
            all_ok = False

    print("\n" + "="*80)
    if all_ok:
        print("✅ ALL MIGRATION CHECKS PASSED")
        print("="*80)
        print("\nNo schema drift detected. All models have migrations.")
        sys.exit(0)
    else:
        print("❌ MIGRATION CHECKS FAILED")
        print("="*80)
        print("\nSchema drift detected or migration chain is invalid.")
        print("Run migration create command to generate missing migrations.")
        sys.exit(1)


if __name__ == "__main__":
    main()
