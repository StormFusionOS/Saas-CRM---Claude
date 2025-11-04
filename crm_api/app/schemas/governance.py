"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Pydantic Schemas for Governance API.

Request and response models for change_log, task_logs, audit_issues,
and automation_module_config endpoints.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# ChangeLog Schemas
# ==============================================================================

class ChangeLogCreate(BaseModel):
    """Request schema for creating a new change log entry."""
    change_id: str = Field(..., min_length=1, max_length=50, description="Unique change ID")
    module: str = Field(..., min_length=1, max_length=50, description="Module that generated the change")
    action: str = Field(..., min_length=1, max_length=100, description="Action type (e.g., update_meta_title)")
    target_type: str = Field(..., min_length=1, max_length=50, description="Target resource type (e.g., wordpress_post)")
    target_id: int = Field(..., gt=0, description="Target resource ID")

    old_value: Optional[Dict[str, Any]] = Field(None, description="Current/old value before change")
    new_value: Dict[str, Any] = Field(..., description="Proposed new value")
    reasoning: Optional[str] = Field(None, description="AI reasoning for the change")
    ai_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence score (0.0-1.0)")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence")

    # Rollback support
    rollback_ref: Optional[str] = Field(None, max_length=200, description="Reference for rollback (backup ID, git commit, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "change_id": "chg_meta_12345",
                "module": "seo_meta",
                "action": "update_meta_title",
                "target_type": "wordpress_post",
                "target_id": 123,
                "old_value": {"title": "Old Title"},
                "new_value": {"title": "New SEO-Optimized Title with Keyword"},
                "reasoning": "Current title lacks primary keyword 'commercial cleaning'",
                "ai_confidence": 0.92,
                "evidence": {"keyword_density": 0.0, "competitor_analysis": "3/5 competitors use keyword"}
            }
        }


class ChangeLogUpdate(BaseModel):
    """Request schema for updating a change log entry (approval/rejection)."""
    status: str = Field(..., description="New status (approved, rejected)")
    decision_reason: Optional[str] = Field(None, description="Reason for approval/rejection")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['approved', 'rejected']
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v


class ChangeLogExecute(BaseModel):
    """Request schema for executing an approved change."""
    pass  # Execution is triggered by endpoint, no additional data needed


class ChangeLogRevert(BaseModel):
    """Request schema for reverting an executed change."""
    revert_reason: str = Field(..., min_length=1, description="Reason for reverting the change")


class ChangeLogResponse(BaseModel):
    """Response schema for change log entries."""
    change_id: str
    module: str
    action: str
    target_type: str
    target_id: int

    old_value: Optional[Dict[str, Any]]
    new_value: Dict[str, Any]
    reasoning: Optional[str]
    ai_confidence: Optional[float]
    evidence: Optional[Dict[str, Any]]

    status: str
    created_at: datetime
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    executed_at: Optional[datetime]
    reverted_at: Optional[datetime]

    approved_by: Optional[int]
    rejected_by: Optional[int]
    executed_by: Optional[int]
    reverted_by: Optional[int]

    execution_error: Optional[str]
    revert_reason: Optional[str]
    rollback_ref: Optional[str]

    # Auto-mode fields
    auto_approved: bool
    auto_reverted: bool
    revert_triggers: Optional[Dict[str, Any]]
    rollback_check_status: Optional[str]
    rollback_checked_at: Optional[datetime]

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class ChangeLogListResponse(BaseModel):
    """Paginated response schema for change log list."""
    changes: List[ChangeLogResponse]
    total: int


# ==============================================================================
# TaskLog Schemas
# ==============================================================================

class TaskLogCreate(BaseModel):
    """Request schema for creating a new task log entry."""
    job_name: str = Field(..., min_length=1, max_length=100, description="Job name (e.g., serp-position-scraper)")
    job_id: str = Field(..., min_length=1, max_length=100, description="Unique job execution ID")
    triggered_by: str = Field(..., min_length=1, max_length=50, description="Trigger source (scheduler, manual, webhook)")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Job input parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "job_name": "serp-position-scraper",
                "job_id": "job_serp_20250103_030000",
                "triggered_by": "scheduler",
                "inputs": {"domains": ["example.com"], "keywords": ["commercial cleaning"]}
            }
        }


class TaskLogUpdate(BaseModel):
    """Request schema for updating a task log entry."""
    status: Optional[str] = Field(None, description="Job status (running, completed, failed, timeout)")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Job output data")
    records_processed: Optional[int] = Field(None, ge=0, description="Number of records processed")
    changes_generated: Optional[int] = Field(None, ge=0, description="Number of AI changes generated")
    errors_count: Optional[int] = Field(None, ge=0, description="Number of errors encountered")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_traceback: Optional[str] = Field(None, description="Full error traceback")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed = ['running', 'completed', 'failed', 'timeout', 'cancelled']
            if v not in allowed:
                raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v


class TaskLogResponse(BaseModel):
    """Response schema for task log entries."""
    job_name: str
    job_id: str
    status: str
    triggered_by: str

    inputs: Optional[Dict[str, Any]]
    outputs: Optional[Dict[str, Any]]

    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]

    records_processed: Optional[int]
    changes_generated: Optional[int]
    errors_count: Optional[int]
    error_message: Optional[str]
    error_traceback: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# AuditIssue Schemas
# ==============================================================================

class AuditIssueCreate(BaseModel):
    """Request schema for creating a new audit issue."""
    issue_type: str = Field(..., min_length=1, max_length=50, description="Issue type (data_quality, security, compliance, etc.)")
    severity: str = Field(..., description="Severity level (info, warning, error, critical)")
    title: str = Field(..., min_length=1, max_length=200, description="Short issue title")
    description: str = Field(..., min_length=1, description="Detailed issue description")
    affected_resource: Optional[str] = Field(None, max_length=200, description="Affected resource (e.g., page:123, job:serp-scraper)")
    detected_by: str = Field(..., min_length=1, max_length=50, description="Detection source (health-monitor, manual, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        allowed = ['info', 'warning', 'error', 'critical']
        if v not in allowed:
            raise ValueError(f"Severity must be one of: {', '.join(allowed)}")
        return v


class AuditIssueUpdate(BaseModel):
    """Request schema for updating an audit issue."""
    status: Optional[str] = Field(None, description="New status (open, acknowledged, resolved, ignored)")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed = ['open', 'acknowledged', 'resolved', 'ignored']
            if v not in allowed:
                raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v


class AuditIssueResponse(BaseModel):
    """Response schema for audit issues."""
    issue_type: str
    severity: str
    title: str
    description: str
    affected_resource: Optional[str]
    detected_by: str
    metadata: Optional[Dict[str, Any]]

    status: str
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolved_by: Optional[int]
    resolution_notes: Optional[str]

    updated_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# AutomationModuleConfig Schemas
# ==============================================================================

class ModuleConfigUpdate(BaseModel):
    """Request schema for updating module configuration."""
    operating_mode: Optional[str] = Field(None, description="Operating mode (review, auto)")
    enabled: Optional[bool] = Field(None, description="Enable/disable module")

    confidence_threshold_auto: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence threshold for auto mode")
    confidence_threshold_review: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence threshold for review mode")

    daily_limit_pilot: Optional[int] = Field(None, ge=0, description="Daily limit during pilot phase")
    daily_limit_expand: Optional[int] = Field(None, ge=0, description="Daily limit during expand phase")
    daily_limit_full: Optional[int] = Field(None, ge=0, description="Daily limit during full deployment")

    @field_validator('operating_mode')
    @classmethod
    def validate_operating_mode(cls, v):
        if v is not None:
            allowed = ['review', 'auto']
            if v not in allowed:
                raise ValueError(f"Operating mode must be one of: {', '.join(allowed)}")
        return v


class ModuleConfigGraduate(BaseModel):
    """Request schema for graduating a module to auto mode."""
    graduation_notes: Optional[str] = Field(None, description="Notes about the graduation decision")


class ModuleConfigRollback(BaseModel):
    """Request schema for rolling back a module to review mode."""
    rollback_reason: str = Field(..., min_length=1, description="Reason for rolling back to review mode")


class ModuleConfigResponse(BaseModel):
    """Response schema for module configuration."""
    module: str
    operating_mode: str
    enabled: bool

    confidence_threshold_auto: float
    confidence_threshold_review: float

    daily_limit_pilot: int
    daily_limit_expand: int
    daily_limit_full: int
    current_phase: str

    graduated_at: Optional[datetime]
    graduated_by: Optional[int]
    last_downgraded_at: Optional[datetime]
    downgrade_reason: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# Summary/Dashboard Schemas
# ==============================================================================

class GovernanceSummary(BaseModel):
    """Response schema for governance dashboard summary."""
    change_log: Dict[str, int] = Field(..., description="Change log counts by status")
    task_logs: Dict[str, int] = Field(..., description="Task log counts by status")
    audit_issues: Dict[str, int] = Field(..., description="Audit issue counts")
    health_status: str = Field(..., description="Overall system health status")


__all__ = [
    # ChangeLog
    "ChangeLogCreate",
    "ChangeLogUpdate",
    "ChangeLogExecute",
    "ChangeLogRevert",
    "ChangeLogResponse",
    "ChangeLogListResponse",

    # TaskLog
    "TaskLogCreate",
    "TaskLogUpdate",
    "TaskLogResponse",

    # AuditIssue
    "AuditIssueCreate",
    "AuditIssueUpdate",
    "AuditIssueResponse",

    # ModuleConfig
    "ModuleConfigUpdate",
    "ModuleConfigGraduate",
    "ModuleConfigRollback",
    "ModuleConfigResponse",

    # Summary
    "GovernanceSummary",
]
