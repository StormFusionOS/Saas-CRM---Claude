"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

AI Governance API Routes - Database-Backed Implementation

Endpoints for change_log (review queue), task_logs (job audit), audit_issues (system health),
and automation_module_config. These are the foundation for safe AI automation with
human-in-the-loop governance.

Step 03: Migrated from in-memory storage to PostgreSQL database persistence.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import structlog

from app.database import get_db
from app.db_models import (
    ChangeLogModel,
    TaskLogModel,
    AuditIssueModel,
    AutomationModuleConfigModel,
    ChangeStatus,
    OperatingMode,
    RolloutPhase,
)
from app.schemas.governance import (
    ChangeLogCreate,
    ChangeLogUpdate,
    ChangeLogExecute,
    ChangeLogRevert,
    ChangeLogResponse,
    ChangeLogListResponse,
    TaskLogCreate,
    TaskLogUpdate,
    TaskLogResponse,
    AuditIssueCreate,
    AuditIssueUpdate,
    AuditIssueResponse,
    ModuleConfigUpdate,
    ModuleConfigGraduate,
    ModuleConfigRollback,
    ModuleConfigResponse,
    GovernanceSummary,
)
from app.api.deps import require_sales_claims

router = APIRouter(tags=["governance"])
logger = structlog.get_logger(__name__)


# ==============================================================================
# change_log - AI Suggestion Review Queue
# ==============================================================================

@router.post("/change-log", response_model=ChangeLogResponse, status_code=201)
def create_change_log_entry(
    request: ChangeLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Create a new AI-generated suggestion.

    All AI modules MUST call this endpoint to suggest changes.
    Changes start in 'pending' status and require human approval.
    """
    logger.info("create_change_log", change_id=request.change_id, module=request.module)

    # Check for duplicate change_id
    existing = db.query(ChangeLogModel).filter(ChangeLogModel.change_id == request.change_id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Change with change_id '{request.change_id}' already exists"
        )

    change = ChangeLogModel(
        change_id=request.change_id,
        module=request.module,
        action=request.action,
        target_type=request.target_type,
        target_id=request.target_id,
        old_value=request.old_value,
        new_value=request.new_value,
        reasoning=request.reasoning,
        ai_confidence=request.ai_confidence,
        evidence=request.evidence,
        rollback_ref=request.rollback_ref,
        status=ChangeStatus.PENDING,
    )

    db.add(change)
    db.commit()
    db.refresh(change)

    logger.info("change_log_created", change_id=change.change_id, status=change.status.value)

    return change


@router.get("/change-log", response_model=ChangeLogListResponse)
def list_change_log(
    status: Optional[str] = Query(None, description="Filter by status"),
    module: Optional[str] = Query(None, description="Filter by module"),
    limit: int = Query(100, ge=1, le=1000, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    List change log entries (review queue).

    Filter by status:
    - pending: Items awaiting review
    - approved: Items ready for execution
    - executed: Deployed changes
    - rejected: Denied suggestions
    - reverted: Rolled back changes
    """
    # Build base query for filtering
    query = db.query(ChangeLogModel)

    if status:
        query = query.filter(ChangeLogModel.status == ChangeStatus(status))

    if module:
        query = query.filter(ChangeLogModel.module == module)

    # Get total count (before pagination)
    total = query.count()

    # Sort by created_at desc (newest first)
    query = query.order_by(ChangeLogModel.created_at.desc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    results = query.all()

    logger.debug("list_change_log", count=len(results), total=total, status=status, module=module)

    return {"changes": results, "total": total}


@router.get("/change-log/{change_id}", response_model=ChangeLogResponse)
def get_change_log_entry(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """Get a single change log entry by change_id."""
    change = db.query(ChangeLogModel).filter(ChangeLogModel.change_id == change_id).first()

    if not change:
        raise HTTPException(status_code=404, detail=f"Change log entry '{change_id}' not found")

    return change


@router.put("/change-log/{change_id}/review", response_model=ChangeLogResponse)
def review_change_log_entry(
    change_id: str,
    request: ChangeLogUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Approve or reject a pending change.

    Transitions:
    - pending → approved: Change will be executed
    - pending → rejected: Change will not be executed
    """
    change = db.query(ChangeLogModel).filter(ChangeLogModel.change_id == change_id).first()

    if not change:
        raise HTTPException(status_code=404, detail=f"Change log entry '{change_id}' not found")

    if change.status != ChangeStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review change with status '{change.status.value}'. Must be 'pending'."
        )

    # Update status
    new_status = ChangeStatus(request.status)
    change.status = new_status
    user_id = current_user.get("user_id")

    if new_status == ChangeStatus.APPROVED:
        change.approved_by = user_id
        change.approved_at = func.now()
    elif new_status == ChangeStatus.REJECTED:
        change.rejected_by = user_id
        change.rejected_at = func.now()

    db.commit()
    db.refresh(change)

    logger.info("change_log_reviewed", change_id=change_id, status=new_status.value, user_id=user_id)

    return change


@router.post("/change-log/{change_id}/execute", response_model=ChangeLogResponse)
def execute_change_log_entry(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Execute an approved change.

    Transitions:
    - approved → executed (on success)
    - approved → failed (on error)

    NOTE: In production, this would trigger deployment jobs (WordPress API, CDN invalidation, etc.)
    """
    change = db.query(ChangeLogModel).filter(ChangeLogModel.change_id == change_id).first()

    if not change:
        raise HTTPException(status_code=404, detail=f"Change log entry '{change_id}' not found")

    if change.status != ChangeStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute change with status '{change.status.value}'. Must be 'approved'."
        )

    user_id = current_user.get("user_id")
    change.executed_by = user_id

    # SIMULATION: In production, this would call WordPress API, update CDN, etc.
    try:
        # TODO (Step 15): Implement actual deployment logic per action type
        # - update_meta_title: Call WordPress API
        # - add_schema_markup: Update JSON-LD on page
        # - add_internal_link: Update content in CMS
        # etc.

        change.status = ChangeStatus.EXECUTED
        change.executed_at = func.now()

        db.commit()
        db.refresh(change)

        logger.info("change_log_executed", change_id=change_id, user_id=user_id)

        return change

    except Exception as e:
        change.status = ChangeStatus.FAILED
        change.execution_error = str(e)

        db.commit()

        logger.error("change_log_execution_failed", change_id=change_id, error=str(e))

        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.post("/change-log/{change_id}/revert", response_model=ChangeLogResponse)
def revert_change_log_entry(
    change_id: str,
    request: ChangeLogRevert,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Revert an executed change (rollback).

    Requires that change has a rollback_ref (backup ID, git commit, etc.)
    """
    change = db.query(ChangeLogModel).filter(ChangeLogModel.change_id == change_id).first()

    if not change:
        raise HTTPException(status_code=404, detail=f"Change log entry '{change_id}' not found")

    if change.status != ChangeStatus.EXECUTED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot revert change with status '{change.status.value}'. Must be 'executed'."
        )

    if not change.rollback_ref:
        raise HTTPException(
            status_code=400,
            detail="Cannot revert: No rollback reference available"
        )

    # TODO (Step 16): Implement rollback logic using rollback_ref

    user_id = current_user.get("user_id")
    change.status = ChangeStatus.REVERTED
    change.reverted_by = user_id
    change.reverted_at = func.now()
    change.revert_reason = request.revert_reason
    change.auto_reverted = False  # Manual revert

    db.commit()
    db.refresh(change)

    logger.info("change_log_reverted", change_id=change_id, reason=request.revert_reason, user_id=user_id)

    return change


# ==============================================================================
# task_logs - Job Execution Audit Trail
# ==============================================================================

@router.post("/task-logs", response_model=TaskLogResponse, status_code=201)
def create_task_log(
    request: TaskLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Start logging a job execution.

    Every AI job (SERP scraper, anomaly detector, etc.) calls this at start.
    """
    logger.info("create_task_log", job_name=request.job_name, job_id=request.job_id)

    # Check for duplicate job_id
    existing = db.query(TaskLogModel).filter(TaskLogModel.job_id == request.job_id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Task log with job_id '{request.job_id}' already exists"
        )

    task_log = TaskLogModel(
        job_name=request.job_name,
        job_id=request.job_id,
        status="running",
        triggered_by=request.triggered_by,
        inputs=request.inputs,
    )

    db.add(task_log)
    db.commit()
    db.refresh(task_log)

    logger.info("task_log_created", job_id=task_log.job_id, status=task_log.status)

    return task_log


@router.put("/task-logs/{job_id}", response_model=TaskLogResponse)
def update_task_log(
    job_id: str,
    request: TaskLogUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Update a job execution log.

    Call this to update status, outputs, metrics, or errors during/after execution.
    """
    task_log = db.query(TaskLogModel).filter(TaskLogModel.job_id == job_id).first()

    if not task_log:
        raise HTTPException(status_code=404, detail=f"Task log with job_id '{job_id}' not found")

    # Update fields
    if request.status is not None:
        task_log.status = request.status

    if request.outputs is not None:
        task_log.outputs = request.outputs

    if request.records_processed is not None:
        task_log.records_processed = request.records_processed

    if request.changes_generated is not None:
        task_log.changes_generated = request.changes_generated

    if request.errors_count is not None:
        task_log.errors_count = request.errors_count

    if request.error_message is not None:
        task_log.error_message = request.error_message

    if request.error_traceback is not None:
        task_log.error_traceback = request.error_traceback

    # Auto-set completed_at and duration if status is terminal
    if request.status in ["completed", "failed", "timeout", "cancelled"]:
        if not task_log.completed_at:
            task_log.completed_at = func.now()
            # Duration will be calculated by database trigger or in application code

    db.commit()
    db.refresh(task_log)

    logger.info("task_log_updated", job_id=job_id, status=task_log.status)

    return task_log


@router.get("/task-logs", response_model=List[TaskLogResponse])
def list_task_logs(
    job_name: Optional[str] = Query(None, description="Filter by job name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    List job execution logs.

    Filter by job_name or status. Useful for dashboards and debugging.
    """
    query = db.query(TaskLogModel)

    if job_name:
        query = query.filter(TaskLogModel.job_name == job_name)

    if status:
        query = query.filter(TaskLogModel.status == status)

    # Sort by started_at desc (most recent first)
    query = query.order_by(TaskLogModel.started_at.desc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    results = query.all()

    logger.debug("list_task_logs", count=len(results), job_name=job_name, status=status)

    return results


@router.get("/task-logs/{job_id}", response_model=TaskLogResponse)
def get_task_log(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """Get a single task log by job_id."""
    task_log = db.query(TaskLogModel).filter(TaskLogModel.job_id == job_id).first()

    if not task_log:
        raise HTTPException(status_code=404, detail=f"Task log with job_id '{job_id}' not found")

    return task_log


# ==============================================================================
# audit_issues - System Health & Compliance Issues
# ==============================================================================

@router.post("/audit-issues", response_model=AuditIssueResponse, status_code=201)
def create_audit_issue(
    request: AuditIssueCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Create a new audit issue.

    Called by health monitors, compliance checkers, or manual audits.
    """
    logger.info("create_audit_issue", issue_type=request.issue_type, severity=request.severity)

    issue = AuditIssueModel(
        issue_type=request.issue_type,
        severity=request.severity,
        title=request.title,
        description=request.description,
        affected_resource=request.affected_resource,
        detected_by=request.detected_by,
        metadata=request.metadata,
        status="open",
    )

    db.add(issue)
    db.commit()
    db.refresh(issue)

    logger.info("audit_issue_created", issue_type=issue.issue_type, severity=issue.severity)

    return issue


@router.get("/audit-issues", response_model=List[AuditIssueResponse])
def list_audit_issues(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, ge=1, le=1000, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    List audit issues.

    Filter by status (open/resolved) or severity (info/warning/error/critical).
    """
    query = db.query(AuditIssueModel)

    if status:
        query = query.filter(AuditIssueModel.status == status)

    if severity:
        query = query.filter(AuditIssueModel.severity == severity)

    # Sort by severity (critical first) then created_at desc
    # Note: This requires custom ordering logic - simplified here
    query = query.order_by(AuditIssueModel.created_at.desc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    results = query.all()

    logger.debug("list_audit_issues", count=len(results), status=status, severity=severity)

    return results


@router.get("/audit-issues/{issue_id}", response_model=AuditIssueResponse)
def get_audit_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """Get a single audit issue by ID."""
    issue = db.query(AuditIssueModel).filter(AuditIssueModel.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail=f"Audit issue {issue_id} not found")

    return issue


@router.put("/audit-issues/{issue_id}", response_model=AuditIssueResponse)
def update_audit_issue(
    issue_id: int,
    request: AuditIssueUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Update an audit issue (acknowledge or resolve).

    Status transitions:
    - open → acknowledged → resolved
    - open → ignored
    """
    issue = db.query(AuditIssueModel).filter(AuditIssueModel.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail=f"Audit issue {issue_id} not found")

    user_id = current_user.get("user_id")

    if request.status:
        issue.status = request.status

        if request.status == "resolved":
            issue.resolved_by = user_id
            issue.resolved_at = func.now()

    if request.resolution_notes:
        issue.resolution_notes = request.resolution_notes

    db.commit()
    db.refresh(issue)

    logger.info("audit_issue_updated", issue_id=issue_id, status=issue.status, user_id=user_id)

    return issue


# ==============================================================================
# module_config - Review/Auto Mode Configuration
# ==============================================================================

@router.get("/module-config", response_model=List[ModuleConfigResponse])
def list_module_configs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    List all AI module configurations.

    Shows review/auto mode settings, approval requirements, and metrics.
    """
    configs = db.query(AutomationModuleConfigModel).all()

    return configs


@router.get("/module-config/{module_name}", response_model=ModuleConfigResponse)
def get_module_config(
    module_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """Get configuration for a specific module."""
    config = db.query(AutomationModuleConfigModel).filter(
        AutomationModuleConfigModel.module == module_name
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    return config


@router.put("/module-config/{module_name}", response_model=ModuleConfigResponse)
def update_module_config(
    module_name: str,
    request: ModuleConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Update module configuration.

    Can change review/auto settings, enable/disable, pause, etc.
    """
    config = db.query(AutomationModuleConfigModel).filter(
        AutomationModuleConfigModel.module == module_name
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    # Update fields
    if request.operating_mode is not None:
        config.operating_mode = OperatingMode(request.operating_mode)

    if request.enabled is not None:
        config.enabled = request.enabled

    if request.confidence_threshold_auto is not None:
        config.confidence_threshold_auto = request.confidence_threshold_auto

    if request.confidence_threshold_review is not None:
        config.confidence_threshold_review = request.confidence_threshold_review

    if request.daily_limit_pilot is not None:
        config.daily_limit_pilot = request.daily_limit_pilot

    if request.daily_limit_expand is not None:
        config.daily_limit_expand = request.daily_limit_expand

    if request.daily_limit_full is not None:
        config.daily_limit_full = request.daily_limit_full

    db.commit()
    db.refresh(config)

    logger.info("module_config_updated", module=module_name)

    return config


@router.post("/module-config/{module_name}/graduate", response_model=ModuleConfigResponse)
def graduate_module_to_auto(
    module_name: str,
    request: ModuleConfigGraduate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Graduate module from review mode to auto mode.

    This is the Step 16 "Go-Live" action. Requirements:
    - Module must have proven track record (high approval rate, low revert rate)
    - Must be explicitly approved by admin
    - Settings are preserved for rollback
    """
    config = db.query(AutomationModuleConfigModel).filter(
        AutomationModuleConfigModel.module == module_name
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    # TODO (Step 16): Implement graduation criteria checks
    # - Query change_log for module approval rate
    # - Query change_log for module revert rate
    # - Validate thresholds

    user_id = current_user.get("user_id")

    # Graduate to auto mode
    config.operating_mode = OperatingMode.AUTO
    config.graduated_at = func.now()
    config.graduated_by = user_id

    db.commit()
    db.refresh(config)

    logger.info("module_graduated", module=module_name, user_id=user_id)

    return config


@router.post("/module-config/{module_name}/rollback-to-review", response_model=ModuleConfigResponse)
def rollback_module_to_review(
    module_name: str,
    request: ModuleConfigRollback,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Rollback module from auto mode to review mode.

    Use this if auto mode causes issues or needs re-evaluation.
    """
    config = db.query(AutomationModuleConfigModel).filter(
        AutomationModuleConfigModel.module == module_name
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    if config.operating_mode == OperatingMode.REVIEW:
        raise HTTPException(
            status_code=400,
            detail="Module is already in review mode"
        )

    user_id = current_user.get("user_id")

    # Rollback to review mode
    config.operating_mode = OperatingMode.REVIEW
    config.last_downgraded_at = func.now()
    config.downgrade_reason = request.rollback_reason

    db.commit()
    db.refresh(config)

    logger.info("module_rolled_back", module=module_name, reason=request.rollback_reason, user_id=user_id)

    return config


# ==============================================================================
# Dashboard Summary Endpoints
# ==============================================================================

@router.get("/governance/summary", response_model=GovernanceSummary)
def get_governance_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Get governance summary for dashboard.

    Returns counts and recent activity across all governance tables.
    """
    # Change log counts by status
    pending_changes = db.query(ChangeLogModel).filter(
        ChangeLogModel.status == ChangeStatus.PENDING
    ).count()

    approved_changes = db.query(ChangeLogModel).filter(
        ChangeLogModel.status == ChangeStatus.APPROVED
    ).count()

    executed_changes = db.query(ChangeLogModel).filter(
        ChangeLogModel.status == ChangeStatus.EXECUTED
    ).count()

    failed_changes = db.query(ChangeLogModel).filter(
        ChangeLogModel.status == ChangeStatus.FAILED
    ).count()

    # Task log counts
    running_jobs = db.query(TaskLogModel).filter(TaskLogModel.status == "running").count()
    failed_jobs = db.query(TaskLogModel).filter(TaskLogModel.status == "failed").count()

    # Audit issue counts
    open_issues = db.query(AuditIssueModel).filter(AuditIssueModel.status == "open").count()
    critical_issues = db.query(AuditIssueModel).filter(
        AuditIssueModel.severity == "critical",
        AuditIssueModel.status == "open"
    ).count()

    # Recent activity (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)

    recent_changes = db.query(ChangeLogModel).filter(
        ChangeLogModel.created_at >= yesterday
    ).count()

    recent_jobs = db.query(TaskLogModel).filter(
        TaskLogModel.started_at >= yesterday
    ).count()

    health_status = "healthy" if critical_issues == 0 and failed_jobs == 0 else "degraded"

    return {
        "change_log": {
            "pending": pending_changes,
            "approved": approved_changes,
            "executed": executed_changes,
            "failed": failed_changes,
            "recent_24h": recent_changes
        },
        "task_logs": {
            "running": running_jobs,
            "failed": failed_jobs,
            "recent_24h": recent_jobs
        },
        "audit_issues": {
            "open": open_issues,
            "critical": critical_issues
        },
        "health_status": health_status
    }
