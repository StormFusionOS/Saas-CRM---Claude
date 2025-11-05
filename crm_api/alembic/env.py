"""
Alembic environment configuration for CRM API migrations.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db_models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata


def get_url():
    """Get database URL from environment or config file."""
    # Try to build URL from environment variables (for Docker)
    db_host = os.getenv("CRM_DB_HOST")
    db_port = os.getenv("CRM_DB_PORT")
    db_name = os.getenv("CRM_DB_NAME")
    db_user = os.getenv("CRM_DB_USER")
    db_pass = os.getenv("CRM_DB_PASSWORD")

    if all([db_host, db_port, db_name, db_user, db_pass]):
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    # Fall back to config file URL (for local development)
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Override URL with environment variable if available
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
