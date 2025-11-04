"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

AI Governance Models - change_log, task_logs, audit_issues

These models implement the governance layer required for safe AI automation.
All AI-generated suggestions must flow through change_log in 'pending' state
before being approved and executed.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ==============================================================================
# Enums
# ==============================================================================

class ChangeLogStatus(str, Enum):
    """State machine for change_log records."""
    PENDING = "pending"              # AI generated, awaiting review
    APPROVED = "approved"            # Human approved, ready for execution
    REJECTED = "rejected"            # Human rejected, won't execute
    EXECUTING = "executing"          # Currently being deployed
    EXECUTED = "executed"            # Successfully deployed
    FAILED = "failed"                # Execution failed
    REVERTED = "reverted"            # Rolled back after execution


class ChangeLogModule(str, Enum):
    """AI modules that can generate changes."""
    ANOMALY_DETECTOR = "anomaly_detector"
    CTR_OPTIMIZER = "ctr_optimizer"
    SNIPPET_OPTIMIZER = "snippet_optimizer"
    SCHEMA_GENERATOR = "schema_generator"
    CONTENT_CLUSTERS = "content_clusters"
    INTERNAL_LINKING = "internal_linking"
    BACKLINK_FINDER = "backlink_finder"
    FAQ_GENERATOR = "faq_generator"
    META_REWRITER = "meta_rewriter"
    COMMUNICATIONS_HUB = "communications_hub"


class ChangeLogAction(str, Enum):
    """Types of actions that can be suggested."""
    UPDATE_META_TITLE = "update_meta_title"
    UPDATE_META_DESCRIPTION = "update_meta_description"
    ADD_SCHEMA_MARKUP = "add_schema_markup"
    UPDATE_SCHEMA_MARKUP = "update_schema_markup"
    ADD_INTERNAL_LINK = "add_internal_link"
    CREATE_FAQ_SECTION = "create_faq_section"
    UPDATE_CONTENT = "update_content"
    CREATE_REDIRECT = "create_redirect"
    SEND_COMMUNICATION = "send_communication"


class TaskLogStatus(str, Enum):
    """Status of scheduled AI jobs."""
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class AuditIssueSeverity(str, Enum):
    """Severity levels for audit issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ==============================================================================
# change_log - AI Suggestion Review Queue
# ==============================================================================

class ChangeLogRecord(BaseModel):
    """
    A single AI-generated suggestion awaiting review/approval.

    State Flow:
        pending → (human reviews) → approved/rejected
        approved → executing → executed (success)
        approved → executing → failed → reverted
    """
    id: int
    module: str = Field(..., description="AI module that generated this (e.g., 'ctr_optimizer')")
    action: str = Field(..., description="Action type (e.g., 'update_meta_title')")
    target: str = Field(..., description="Target resource (e.g., 'page:123', 'post:/blog/example')")

    # Change details
    diff_preview: Optional[str] = Field(None, description="Visual diff or preview of the change")
    current_value: Optional[str] = Field(None, description="Current value before change")
    proposed_value: str = Field(..., description="Proposed new value")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    # Governance
    status: str = Field(default="pending", description="Current state in workflow")
    severity: str = Field(default="low", description="Impact level: low/medium/high/critical")
    confidence_score: Optional[float] = Field(None, description="AI confidence 0.0-1.0")

    # Review tracking
    generated_by: Optional[str] = Field(None, description="AI job that created this")
    generated_at: datetime = Field(default_factory=datetime.now)
    reviewed_by: Optional[int] = Field(None, description="User ID who approved/rejected")
    reviewed_at: Optional[datetime] = None
    decision_reason: Optional[str] = Field(None, description="Why approved or rejected")

    # Execution tracking
    executed_by: Optional[int] = Field(None, description="User or bot that executed")
    executed_at: Optional[datetime] = None
    execution_result: Optional[str] = Field(None, description="Result or error message")

    # Rollback support
    rollback_ref: Optional[str] = Field(None, description="Reference for reverting (backup ID, git commit)")
    reverted_at: Optional[datetime] = None
    reverted_by: Optional[int] = None
    revert_reason: Optional[str] = None

    # Audit
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateChangeLogRequest(BaseModel):
    """Request to create a new AI suggestion."""
    module: str
    action: str
    target: str
    proposed_value: str
    current_value: Optional[str] = None
    diff_preview: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    severity: str = "low"
    confidence_score: Optional[float] = None
    generated_by: Optional[str] = None


class ReviewChangeLogRequest(BaseModel):
    """Request to approve or reject a change."""
    status: str = Field(..., pattern="^(approved|rejected)$")
    decision_reason: Optional[str] = None


class ExecuteChangeLogRequest(BaseModel):
    """Request to execute an approved change."""
    execution_notes: Optional[str] = None


# ==============================================================================
# task_logs - Job Execution Audit Trail
# ==============================================================================

class TaskLogRecord(BaseModel):
    """
    Audit log of all AI job executions.

    Every scheduled job (SERP scraper, anomaly detector, etc.) logs here.
    """
    id: int
    job_name: str = Field(..., description="Name of the job (e.g., 'serp_position_scraper')")
    job_id: Optional[str] = Field(None, description="Celery task ID or unique run ID")

    # Execution tracking
    status: str = Field(default="started", description="started/running/completed/failed")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Input/Output tracking
    inputs: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Job inputs")
    outputs: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Job outputs")

    # Metrics
    records_processed: Optional[int] = Field(0, description="Number of records processed")
    changes_generated: Optional[int] = Field(0, description="Number of suggestions created")
    errors_count: Optional[int] = Field(0, description="Number of errors encountered")

    # Error tracking
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None

    # Context
    triggered_by: Optional[str] = Field(None, description="'scheduler', 'manual:user_123', 'webhook'")
    environment: Optional[str] = Field("dev", description="dev/stage/prod")

    # Audit
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateTaskLogRequest(BaseModel):
    """Request to start logging a job execution."""
    job_name: str
    job_id: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    triggered_by: Optional[str] = None
    environment: Optional[str] = "dev"


class UpdateTaskLogRequest(BaseModel):
    """Request to update a job execution log."""
    status: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    records_processed: Optional[int] = None
    changes_generated: Optional[int] = None
    errors_count: Optional[int] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None


# ==============================================================================
# audit_issues - System Health & Compliance Issues
# ==============================================================================

class AuditIssueRecord(BaseModel):
    """
    System health, security, and compliance issues detected by audits.

    Examples:
    - SERP crawler failed 3 times in a row
    - API rate limit exceeded
    - Schema validation failed on 15 pages
    - Backup not run in 48 hours
    - Change pending review >72 hours (SLA violation)
    """
    id: int
    issue_type: str = Field(..., description="Type of issue (e.g., 'job_failure', 'sla_violation')")
    severity: str = Field(default="warning", description="info/warning/error/critical")

    # Issue details
    title: str = Field(..., description="Short description")
    description: str = Field(..., description="Detailed explanation")
    affected_resource: Optional[str] = Field(None, description="Resource affected (job name, page URL, etc.)")

    # Resolution tracking
    status: str = Field(default="open", description="open/acknowledged/resolved/ignored")
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None

    # Context
    detected_by: Optional[str] = Field(None, description="health_monitor, manual_audit, etc.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # SLA tracking
    ack_sla_hours: Optional[int] = Field(None, description="Hours to acknowledge")
    resolve_sla_hours: Optional[int] = Field(None, description="Hours to resolve")
    is_sla_violated: bool = Field(default=False)

    # Audit
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateAuditIssueRequest(BaseModel):
    """Request to create a new audit issue."""
    issue_type: str
    severity: str = "warning"
    title: str
    description: str
    affected_resource: Optional[str] = None
    detected_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    ack_sla_hours: Optional[int] = None
    resolve_sla_hours: Optional[int] = None


class UpdateAuditIssueRequest(BaseModel):
    """Request to update an audit issue."""
    status: Optional[str] = None
    resolution_notes: Optional[str] = None


# ==============================================================================
# In-Memory Storage (will be replaced with PostgreSQL)
# ==============================================================================

change_log_records: List[ChangeLogRecord] = []
task_log_records: List[TaskLogRecord] = []
audit_issue_records: List[AuditIssueRecord] = []

# Counters for IDs
_change_log_id_counter = 1
_task_log_id_counter = 1
_audit_issue_id_counter = 1
