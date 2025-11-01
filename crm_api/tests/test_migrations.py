"""Tests for database migrations."""

import pytest
from pathlib import Path


def test_migrations_exist():
    """Test that migration files exist."""
    migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"

    assert migrations_dir.exists(), "Migrations directory should exist"

    migrations = list(migrations_dir.glob("*.py"))
    assert len(migrations) >= 2, "Should have at least 2 migration files"


def test_initial_migration_exists():
    """Test that initial migration file exists."""
    migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"
    initial_migration = migrations_dir / "202401010001_initial_schema.py"

    assert initial_migration.exists(), "Initial migration should exist"


def test_migration_chain():
    """Test that migrations have proper revision chain."""
    # Read migration files and check revision chain
    migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"

    # Get all migration files
    migration_files = sorted(migrations_dir.glob("*.py"))

    # Check that each migration (except first) has down_revision
    for migration_file in migration_files:
        content = migration_file.read_text()

        # Should have revision identifier
        assert "revision =" in content, f"{migration_file.name} should have revision"

        # Should have down_revision (even if None for first)
        assert "down_revision" in content, f"{migration_file.name} should have down_revision"


def test_alembic_config_exists():
    """Test that alembic.ini exists."""
    alembic_ini = Path(__file__).parent.parent / "alembic.ini"
    assert alembic_ini.exists(), "alembic.ini should exist"


def test_alembic_env_exists():
    """Test that alembic/env.py exists."""
    env_py = Path(__file__).parent.parent / "alembic" / "env.py"
    assert env_py.exists(), "alembic/env.py should exist"


def test_models_can_be_imported():
    """Test that database models can be imported."""
    from app.db_models import UserModel, ContactModel, LeadModel

    # Check that models have __tablename__
    assert hasattr(UserModel, '__tablename__')
    assert hasattr(ContactModel, '__tablename__')
    assert hasattr(LeadModel, '__tablename__')


def test_no_orphan_migrations():
    """Test that all migrations are in proper sequence."""
    migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"

    revisions = {}
    down_revisions = []

    for migration_file in migrations_dir.glob("*.py"):
        content = migration_file.read_text()

        # Extract revision and down_revision
        for line in content.split('\n'):
            if line.startswith("revision ="):
                rev = line.split('=')[1].strip().strip("'\"")
                revisions[rev] = migration_file.name
            elif line.startswith("down_revision ="):
                down_rev = line.split('=')[1].strip().strip("'\"")
                if down_rev != "None":
                    down_revisions.append(down_rev)

    # All down_revisions (except None) should point to existing revisions
    for down_rev in down_revisions:
        assert down_rev in revisions, f"Down revision {down_rev} should exist"
