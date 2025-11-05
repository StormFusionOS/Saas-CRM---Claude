"""Scrape Suite initial tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # SCRAPE SUITE TABLES
    # =========================================================================

    # Create serp_results table
    # Individual SERP results for each snapshot
    op.create_table('serp_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('snapshot_id', sa.Integer(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=2000), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('is_ours', sa.Boolean(), nullable=True),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['snapshot_id'], ['serp_snapshots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_serp_results_snapshot', 'serp_results', ['snapshot_id'], unique=False)
    op.create_index('idx_serp_results_domain_rank', 'serp_results', ['domain', 'rank'], unique=False)
    op.create_index(op.f('ix_serp_results_domain'), 'serp_results', ['domain'], unique=False)
    op.create_index(op.f('ix_serp_results_id'), 'serp_results', ['id'], unique=False)
    op.create_index(op.f('ix_serp_results_is_ours'), 'serp_results', ['is_ours'], unique=False)
    op.create_index(op.f('ix_serp_results_snapshot_id'), 'serp_results', ['snapshot_id'], unique=False)

    # Create competitors table
    # Competitor sites being monitored
    op.create_table('competitors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_scraped', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_competitors_active_priority', 'competitors', ['is_active', 'priority'], unique=False)
    op.create_index(op.f('ix_competitors_domain'), 'competitors', ['domain'], unique=True)
    op.create_index(op.f('ix_competitors_id'), 'competitors', ['id'], unique=False)
    op.create_index(op.f('ix_competitors_is_active'), 'competitors', ['is_active'], unique=False)

    # Create referring_domains table
    # Domain-level backlink metrics aggregation
    op.create_table('referring_domains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('backlink_count', sa.Integer(), nullable=True),
        sa.Column('inbody_link_count', sa.Integer(), nullable=True),
        sa.Column('authority_score', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_referring_domains_authority', 'referring_domains', ['authority_score'], unique=False)
    op.create_index(op.f('ix_referring_domains_domain'), 'referring_domains', ['domain'], unique=True)
    op.create_index(op.f('ix_referring_domains_id'), 'referring_domains', ['id'], unique=False)

    # Create page_audits table
    # Technical SEO audits for specific pages
    # TODO (Step 15): Partition by audit_date for high-volume data
    op.create_table('page_audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_url', sa.String(length=2000), nullable=False),
        sa.Column('audit_date', sa.DateTime(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('performance_proxy', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('issues_found', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_page_audits_url_date', 'page_audits', ['page_url', 'audit_date'], unique=False)
    op.create_index(op.f('ix_page_audits_audit_date'), 'page_audits', ['audit_date'], unique=False)
    op.create_index(op.f('ix_page_audits_id'), 'page_audits', ['id'], unique=False)
    op.create_index(op.f('ix_page_audits_page_url'), 'page_audits', ['page_url'], unique=False)

    # Create page_audit_issues table
    # Individual issues found during page audits
    op.create_table('page_audit_issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('fixed', sa.Boolean(), nullable=True),
        sa.Column('fixed_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['audit_id'], ['page_audits.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_issues_audit_severity', 'page_audit_issues', ['audit_id', 'severity'], unique=False)
    op.create_index('idx_audit_issues_fixed', 'page_audit_issues', ['fixed', 'type'], unique=False)
    op.create_index(op.f('ix_page_audit_issues_audit_id'), 'page_audit_issues', ['audit_id'], unique=False)
    op.create_index(op.f('ix_page_audit_issues_fixed'), 'page_audit_issues', ['fixed'], unique=False)
    op.create_index(op.f('ix_page_audit_issues_id'), 'page_audit_issues', ['id'], unique=False)
    op.create_index(op.f('ix_page_audit_issues_severity'), 'page_audit_issues', ['severity'], unique=False)
    op.create_index(op.f('ix_page_audit_issues_type'), 'page_audit_issues', ['type'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('page_audit_issues')
    op.drop_table('page_audits')
    op.drop_table('referring_domains')
    op.drop_table('competitors')
    op.drop_table('serp_results')
