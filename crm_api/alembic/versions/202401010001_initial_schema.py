"""Initial schema

Revision ID: 202401010001
Revises:
Create Date: 2024-01-01 00:01:00

"""
from alembic import op
# import sqlalchemy as sa


# revision identifiers
revision = '202401010001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create initial tables for CRM API.

    Tables: users, contacts, leads, interactions, auto_reply_rules

    PRODUCTION NOTE: This is a stub migration.
    With real SQLAlchemy and Alembic, use:
        alembic revision --autogenerate -m "initial schema"
    """
    # Stub for testing - in production, create tables:
    #
    # op.create_table('users',
    #     sa.Column('id', sa.Integer(), primary_key=True),
    #     sa.Column('email', sa.String(255), unique=True, nullable=False),
    #     sa.Column('hashed_password', sa.String(255), nullable=False),
    #     sa.Column('full_name', sa.String(255)),
    #     sa.Column('roles', sa.ARRAY(sa.String(50)), nullable=False),
    #     sa.Column('is_active', sa.Boolean(), default=True),
    #     sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    #     sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    # )
    # ... create other tables ...

    pass


def downgrade() -> None:
    """Drop initial tables."""
    # op.drop_table('auto_reply_rules')
    # op.drop_table('interactions')
    # op.drop_table('leads')
    # op.drop_table('contacts')
    # op.drop_table('users')
    pass
