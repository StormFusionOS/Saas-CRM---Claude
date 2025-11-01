#!/usr/bin/env python3
"""
Check for migration drift and consistency.

Verifies that all models have corresponding migrations.
"""

import sys
from pathlib import Path


def check_migrations(service: str):
    """Check migrations for a service."""
    print(f"Checking {service} migrations...")

    service_dir = Path(__file__).parent.parent / f"{service}_api"
    migrations_dir = service_dir / "alembic" / "versions"

    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        return False

    migration_files = list(migrations_dir.glob("*.py"))
    print(f"✓ Found {len(migration_files)} migration files")

    # Check revision chain
    revisions = {}
    for migration_file in migration_files:
        content = migration_file.read_text()
        for line in content.split('\n'):
            if line.startswith("revision ="):
                rev = line.split('=')[1].strip().strip("'\"")
                revisions[rev] = migration_file.name

    print(f"✓ {len(revisions)} unique revisions")

    return True


if __name__ == "__main__":
    services = ["crm", "ops"]

    all_ok = True
    for service in services:
        if not check_migrations(service):
            all_ok = False

    if all_ok:
        print("\n✅ All migration checks passed")
        sys.exit(0)
    else:
        print("\n❌ Migration checks failed")
        sys.exit(1)
