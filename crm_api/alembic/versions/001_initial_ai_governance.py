"""Initial AI governance tables

Revision ID: 001
Revises: 
Create Date: 2025-11-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table (core CRM)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('roles', postgresql.ARRAY(sa.String(length=50)), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String(length=50)), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_contacted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=True)
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_phone'), 'contacts', ['phone'], unique=False)

    # Create pages table (SEO)
    op.create_table('pages',
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=2000), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('meta_description', sa.String(length=1000), nullable=True),
        sa.Column('page_type', sa.String(length=50), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('last_crawled_at', sa.DateTime(), nullable=True),
        sa.Column('require_manual_review', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('page_id')
    )
    op.create_index(op.f('ix_pages_domain'), 'pages', ['domain'], unique=False)
    op.create_index(op.f('ix_pages_page_id'), 'pages', ['page_id'], unique=False)
    op.create_index(op.f('ix_pages_url'), 'pages', ['url'], unique=True)

    # Create keywords table (SEO)
    op.create_table('keywords',
        sa.Column('keyword_id', sa.Integer(), nullable=False),
        sa.Column('keyword_text', sa.String(length=500), nullable=False),
        sa.Column('search_volume', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.Integer(), nullable=True),
        sa.Column('intent', sa.String(length=50), nullable=True),
        sa.Column('target_page_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['target_page_id'], ['pages.page_id'], ),
        sa.PrimaryKeyConstraint('keyword_id')
    )
    op.create_index(op.f('ix_keywords_keyword_id'), 'keywords', ['keyword_id'], unique=False)
    op.create_index(op.f('ix_keywords_keyword_text'), 'keywords', ['keyword_text'], unique=False)

    # =========================================================================
    # AI GOVERNANCE TABLES (Step 01 - Critical)
    # =========================================================================

    # Create task_logs table (for tracking AI jobs)
    op.create_table('task_logs',
        sa.Column('task_id', sa.String(length=50), nullable=False),
        sa.Column('task_name', sa.String(length=100), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'RETRYING', 'CANCELLED', name='taskstatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='taskpriority'), nullable=True),
        sa.Column('queued_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('items_processed', sa.Integer(), nullable=True),
        sa.Column('items_succeeded', sa.Integer(), nullable=True),
        sa.Column('items_failed', sa.Integer(), nullable=True),
        sa.Column('input_params', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('changes_generated', sa.Integer(), nullable=True),
        sa.Column('change_ids', postgresql.ARRAY(sa.String(length=50)), nullable=True),
        sa.PrimaryKeyConstraint('task_id')
    )
    op.create_index('idx_task_logs_module_status', 'task_logs', ['module', 'status'], unique=False)
    op.create_index('idx_task_logs_status_queued', 'task_logs', ['status', 'queued_at'], unique=False)
    op.create_index(op.f('ix_task_logs_module'), 'task_logs', ['module'], unique=False)
    op.create_index(op.f('ix_task_logs_queued_at'), 'task_logs', ['queued_at'], unique=False)
    op.create_index(op.f('ix_task_logs_status'), 'task_logs', ['status'], unique=False)
    op.create_index(op.f('ix_task_logs_task_name'), 'task_logs', ['task_name'], unique=False)

    # Create change_log table (central governance table)
    op.create_table('change_log',
        sa.Column('change_id', sa.String(length=50), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('old_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('evidence', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'EXECUTED', 'REVERTED', 'FAILED', name='changestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('reverted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('rejected_by', sa.Integer(), nullable=True),
        sa.Column('executed_by', sa.Integer(), nullable=True),
        sa.Column('decision_reason', sa.Text(), nullable=True),
        sa.Column('execution_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('revert_reason', sa.Text(), nullable=True),
        sa.Column('auto_approved', sa.Boolean(), nullable=True),
        sa.Column('auto_reverted', sa.Boolean(), nullable=True),
        sa.Column('revert_triggers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('rollback_check_status', sa.String(length=20), nullable=True),
        sa.Column('rollback_checked_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['executed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['rejected_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('change_id')
    )
    op.create_index('idx_change_log_auto_monitoring', 'change_log', ['auto_approved', 'executed_at', 'status'], unique=False)
    op.create_index('idx_change_log_module_status', 'change_log', ['module', 'status'], unique=False)
    op.create_index('idx_change_log_status_created', 'change_log', ['status', 'created_at'], unique=False)
    op.create_index(op.f('ix_change_log_change_id'), 'change_log', ['change_id'], unique=False)
    op.create_index(op.f('ix_change_log_created_at'), 'change_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_change_log_module'), 'change_log', ['module'], unique=False)
    op.create_index(op.f('ix_change_log_status'), 'change_log', ['status'], unique=False)

    # Create audit_issues table
    op.create_table('audit_issues',
        sa.Column('issue_id', sa.String(length=50), nullable=False),
        sa.Column('issue_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.Enum('INFO', 'WARNING', 'ERROR', 'CRITICAL', name='issueseverity'), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED', 'IGNORED', name='issuestatus'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('affected_entity_type', sa.String(length=50), nullable=True),
        sa.Column('affected_entity_id', sa.Integer(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('detected_by_task_id', sa.String(length=50), nullable=True),
        sa.Column('detection_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolution_action_taken', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['detected_by_task_id'], ['task_logs.task_id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('issue_id')
    )
    op.create_index('idx_audit_issues_detected', 'audit_issues', ['detected_at'], unique=False)
    op.create_index('idx_audit_issues_severity_status', 'audit_issues', ['severity', 'status'], unique=False)
    op.create_index(op.f('ix_audit_issues_detected_at'), 'audit_issues', ['detected_at'], unique=False)
    op.create_index(op.f('ix_audit_issues_issue_type'), 'audit_issues', ['issue_type'], unique=False)
    op.create_index(op.f('ix_audit_issues_severity'), 'audit_issues', ['severity'], unique=False)
    op.create_index(op.f('ix_audit_issues_status'), 'audit_issues', ['status'], unique=False)

    # Create automation_module_config table
    op.create_table('automation_module_config',
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('operating_mode', sa.Enum('REVIEW', 'AUTO', name='operatingmode'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('confidence_threshold_auto', sa.Float(), nullable=True),
        sa.Column('confidence_threshold_review', sa.Float(), nullable=True),
        sa.Column('daily_limit_pilot', sa.Integer(), nullable=True),
        sa.Column('daily_limit_expand', sa.Integer(), nullable=True),
        sa.Column('daily_limit_full', sa.Integer(), nullable=True),
        sa.Column('current_phase', sa.Enum('REVIEW', 'PILOT', 'EXPAND', 'FULL', name='rolloutphase'), nullable=True),
        sa.Column('graduated_at', sa.DateTime(), nullable=True),
        sa.Column('graduated_by', sa.Integer(), nullable=True),
        sa.Column('last_downgraded_at', sa.DateTime(), nullable=True),
        sa.Column('downgrade_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['graduated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('module')
    )

    # Create module_graduation_log table
    op.create_table('module_graduation_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('action', sa.Enum('GRADUATED', 'DOWNGRADED', 'PHASE_ADVANCED', name='modulegraduationaction'), nullable=False),
        sa.Column('from_mode', sa.String(length=20), nullable=True),
        sa.Column('to_mode', sa.String(length=20), nullable=True),
        sa.Column('from_phase', sa.String(length=20), nullable=True),
        sa.Column('to_phase', sa.String(length=20), nullable=True),
        sa.Column('performed_by', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('metrics_snapshot', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_graduation_log_module_created', 'module_graduation_log', ['module', 'created_at'], unique=False)
    op.create_index(op.f('ix_module_graduation_log_created_at'), 'module_graduation_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_module_graduation_log_id'), 'module_graduation_log', ['id'], unique=False)
    op.create_index(op.f('ix_module_graduation_log_module'), 'module_graduation_log', ['module'], unique=False)

    # Insert default module configurations
    op.execute("""
        INSERT INTO automation_module_config (module, operating_mode, enabled) VALUES
        ('seo_meta', 'REVIEW', true),
        ('seo_schema', 'REVIEW', true),
        ('seo_faq', 'REVIEW', true),
        ('internal_linking', 'REVIEW', true),
        ('anomaly_detection', 'REVIEW', true)
    """)


def downgrade() -> None:
    op.drop_table('module_graduation_log')
    op.drop_table('automation_module_config')
    op.drop_table('audit_issues')
    op.drop_table('change_log')
    op.drop_table('task_logs')
    op.drop_table('keywords')
    op.drop_table('pages')
    op.drop_table('contacts')
    op.drop_table('users')
    
    # Drop custom enums
    op.execute('DROP TYPE IF EXISTS modulegraduationaction')
    op.execute('DROP TYPE IF EXISTS rolloutphase')
    op.execute('DROP TYPE IF EXISTS operatingmode')
    op.execute('DROP TYPE IF EXISTS issuestatus')
    op.execute('DROP TYPE IF EXISTS issueseverity')
    op.execute('DROP TYPE IF EXISTS changestatus')
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS taskpriority')
