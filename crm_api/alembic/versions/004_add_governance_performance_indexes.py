"""Add governance performance indexes

Revision ID: 004_add_governance_performance_indexes
Revises: 003_add_integration_settings
Create Date: 2025-11-07

This migration optimizes query performance for governance tables:
- task_logs(started_at) - NEW: For time-based queries and monthly partitioning
- change_log(status) - ALREADY EXISTS (from migration 001, line 167)
- task_logs(status) - ALREADY EXISTS (from migration 001, line 124)

The started_at index enables efficient queries for:
- Recent task activity monitoring
- Monthly/daily task reports
- Time-range filtering for dashboards
- Potential future table partitioning by month
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_governance_performance_indexes'
down_revision = '003_add_integration_settings'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add performance indexes for governance tables.

    IMPORTANT: change_log(status) and task_logs(status) indexes already exist
    from migration 001. This migration only adds task_logs(started_at).
    """

    # Create index on task_logs.started_at for time-based queries
    # This enables efficient queries like:
    #   - WHERE started_at >= NOW() - INTERVAL '24 hours'
    #   - WHERE started_at BETWEEN '2025-01-01' AND '2025-01-31'
    #   - ORDER BY started_at DESC LIMIT 100
    op.create_index(
        'idx_task_logs_started_at_desc',
        'task_logs',
        ['started_at'],
        unique=False,
        postgresql_using='btree',
        postgresql_ops={'started_at': 'DESC'}
    )

    # Add table comment documenting the optimization strategy
    op.execute("""
        COMMENT ON INDEX idx_task_logs_started_at_desc IS
        'Optimizes time-based queries for task log monitoring and reporting.
        DESC order matches common usage pattern (recent tasks first).
        Supports future monthly table partitioning if needed.'
    """)


def downgrade():
    """
    Remove performance indexes added in this migration.

    Note: Does NOT remove change_log(status) or task_logs(status) indexes
    as those were created in migration 001.
    """

    # Drop the started_at index
    op.drop_index('idx_task_logs_started_at_desc', table_name='task_logs')
