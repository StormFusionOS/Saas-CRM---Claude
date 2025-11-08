"""
Add integration_settings table

Revision ID: 003_add_integration_settings
Revises: 002_scrape_suite_initial
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_integration_settings'
down_revision = '002_scrape_suite_initial'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create integration_settings table for storing encrypted integration configs
    """
    op.create_table(
        'integration_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('namespace', sa.String(length=100), nullable=False, comment='Integration identifier (e.g., ai_node)'),
        sa.Column('base_url', sa.String(length=500), nullable=True, comment='Base URL for API calls'),
        sa.Column('encrypted_secret', sa.Text(), nullable=True, comment='Encrypted bearer token or API key (Fernet)'),
        sa.Column('review_mode', sa.Boolean(), nullable=False, server_default='true', comment='Require human review for actions'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true', comment='Whether integration is active'),
        sa.Column('last_ping_status', sa.String(length=50), nullable=True, comment='Status of last connection test'),
        sa.Column('last_ping_latency_ms', sa.Integer(), nullable=True, comment='Latency of last ping in milliseconds'),
        sa.Column('last_ping_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp of last ping test'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='User ID who created this config'),
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='User ID who last updated this config'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('namespace')
    )

    # Create index on namespace for faster lookups
    op.create_index('idx_integration_namespace', 'integration_settings', ['namespace'])

    # Add comment to table
    op.execute("""
        COMMENT ON TABLE integration_settings IS
        'Stores encrypted configuration for external service integrations (AI Node, payment gateways, etc.)'
    """)


def downgrade():
    """
    Drop integration_settings table
    """
    op.drop_index('idx_integration_namespace', table_name='integration_settings')
    op.drop_table('integration_settings')
