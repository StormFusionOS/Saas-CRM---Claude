"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

AI Review Endpoints - Human-in-the-Loop Workflow

Endpoints for reviewing AI-generated changes from change_log.
All actions are wrapped in task_logs for audit trail.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
import structlog
from datetime import datetime

from app.db import get_db
from app.db_models import ChangeLogModel, TaskLogModel
from app.schemas.governance import ChangeLogResponse, ChangeLogUpdate
from app.api.deps import require_sales_claims
from app.services.ai_node_client import AINodeClient, get_ai_node_client, AINodeConnectionError
from pydantic import BaseModel, Field


router = APIRouter(prefix="/ai/review", tags=["ai", "review"])
logger = structlog.get_logger(__name__)


# ============================================================================
# Response Schemas
# ============================================================================


class PendingChangesResponse(BaseModel):
    """Paginated list of pending changes"""
    changes: List[ChangeLogResponse] = Field(..., description="List of pending changes")
    total: int = Field(..., description="Total number of pending changes")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    has_more: bool = Field(..., description="Whether there are more pages")

    class Config:
        json_schema_extra = {
            "example": {
                "changes": [],
                "total": 42,
                "page": 1,
                "limit": 20,
                "has_more": True
            }
        }


class ApproveChangeRequest(BaseModel):
    """Request to approve a change"""
    decision_reason: Optional[str] = Field(None, description="Optional reason for approval")

    class Config:
        json_schema_extra = {
            "example": {
                "decision_reason": "SEO improvement looks good, implementing"
            }
        }


class RejectChangeRequest(BaseModel):
    """Request to reject a change"""
    decision_reason: str = Field(..., min_length=1, description="Reason for rejection (required)")

    class Config:
        json_schema_extra = {
            "example": {
                "decision_reason": "Title change conflicts with brand guidelines"
            }
        }


class ReviewActionResponse(BaseModel):
    """Response after approving/rejecting a change"""
    change_id: str = Field(..., description="ID of the changed record")
    status: str = Field(..., description="New status of the change")
    message: str = Field(..., description="Human-readable result message")
    task_log_id: Optional[str] = Field(None, description="ID of the audit log entry")

    class Config:
        json_schema_extra = {
            "example": {
                "change_id": "chg_meta_12345",
                "status": "executed",
                "message": "Change approved and executed successfully",
                "task_log_id": "task_review_abc"
            }
        }


# ============================================================================
# Helper Functions
# ============================================================================


def create_review_task_log(
    db: Session,
    action: str,
    change_id: str,
    user_id: int,
    status: str = "started",
    details: Optional[dict] = None
) -> TaskLogModel:
    """
    Create a task_logs entry for review actions.

    Args:
        db: Database session
        action: Action type (approve, reject, execute)
        change_id: ID of the change being reviewed
        user_id: User performing the action
        status: Initial status (default: started)
        details: Additional details for the log

    Returns:
        Created TaskLogModel instance
    """
    task_id = f"review_{action}_{change_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    task_log = TaskLogModel(
        task_id=task_id,
        task_name=f"review_{action}",
        module="ai_review",
        status=status,
        started_at=datetime.utcnow(),
        queued_at=datetime.utcnow(),
        input_params={
            "change_id": change_id,
            "user_id": user_id,
            "action": action,
            **(details or {})
        }
    )

    db.add(task_log)
    db.flush()  # Get task_id assigned

    logger.info(
        "review_task_log_created",
        task_id=task_log.task_id,
        action=action,
        change_id=change_id,
        user_id=user_id
    )

    return task_log


def complete_review_task_log(
    task_log: TaskLogModel,
    status: str,
    output: Optional[dict] = None,
    error: Optional[str] = None
):
    """
    Mark a review task log as completed.

    Args:
        task_log: TaskLogModel instance to update
        status: Final status (completed, failed)
        output: Output summary dictionary
        error: Error message if failed
    """
    task_log.status = status
    task_log.completed_at = datetime.utcnow()

    if task_log.started_at:
        duration = (task_log.completed_at - task_log.started_at).total_seconds()
        task_log.duration_seconds = duration

    if output:
        task_log.output_summary = output

    if error:
        task_log.error_message = error

    logger.info(
        "review_task_log_completed",
        task_id=task_log.task_id,
        status=status,
        duration=task_log.duration_seconds
    )


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/pending", response_model=PendingChangesResponse)
def get_pending_changes(
    module: Optional[str] = Query(None, description="Filter by module name"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Get paginated list of pending AI-generated changes.

    Returns changes from change_log where status='PENDING',
    ordered by newest first (created_at DESC).

    Filters:
    - module: Filter by AI module that generated the change
    - page: Page number (1-indexed)
    - limit: Number of items per page (max 100)

    Returns:
        Paginated list of pending changes with metadata
    """
    user_id = current_user.get("user_id")

    logger.info(
        "get_pending_changes",
        user_id=user_id,
        module=module,
        page=page,
        limit=limit
    )

    # Build query
    query = db.query(ChangeLogModel).filter(
        ChangeLogModel.status == "PENDING"
    )

    # Apply module filter if provided
    if module:
        query = query.filter(ChangeLogModel.module == module)

    # Get total count before pagination
    total = query.count()

    # Apply ordering and pagination
    offset = (page - 1) * limit
    changes = query.order_by(desc(ChangeLogModel.created_at)).limit(limit).offset(offset).all()

    # Calculate has_more
    has_more = (offset + len(changes)) < total

    logger.info(
        "pending_changes_retrieved",
        user_id=user_id,
        total=total,
        returned=len(changes),
        page=page
    )

    return PendingChangesResponse(
        changes=changes,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more
    )


@router.get("/{change_id}", response_model=ChangeLogResponse)
def get_change_details(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Get full details of a change for diff view.

    Returns complete change record including:
    - old_value and new_value for diffing
    - AI reasoning and confidence
    - Evidence and metadata
    - Current status and timestamps

    Args:
        change_id: Unique change identifier

    Returns:
        Full change log record

    Raises:
        404: Change not found
    """
    user_id = current_user.get("user_id")

    logger.info("get_change_details", change_id=change_id, user_id=user_id)

    change = db.query(ChangeLogModel).filter(
        ChangeLogModel.change_id == change_id
    ).first()

    if not change:
        logger.warning("change_not_found", change_id=change_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change with ID '{change_id}' not found"
        )

    logger.info(
        "change_details_retrieved",
        change_id=change_id,
        status=change.status,
        user_id=user_id
    )

    return change


@router.post("/{change_id}/approve", response_model=ReviewActionResponse)
async def approve_change(
    change_id: str,
    request: ApproveChangeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
    ai_client: AINodeClient = Depends(get_ai_node_client)
):
    """
    Approve and execute an AI-generated change.

    Workflow:
    1. Validate change exists and is pending
    2. Create task_logs entry (audit trail)
    3. Call AI Node client to execute change
    4. Update change_log status to 'EXECUTED'
    5. Set executed_at and executed_by
    6. Complete task_logs entry

    Args:
        change_id: ID of the change to approve
        request: Approval request with optional reason

    Returns:
        Result of approval and execution

    Raises:
        404: Change not found
        400: Change not in PENDING status
        500: Execution failed
    """
    user_id = current_user.get("user_id")

    logger.info(
        "approve_change_started",
        change_id=change_id,
        user_id=user_id,
        reason=request.decision_reason
    )

    # Get change record
    change = db.query(ChangeLogModel).filter(
        ChangeLogModel.change_id == change_id
    ).first()

    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change with ID '{change_id}' not found"
        )

    # Validate status
    if change.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Change is not pending (current status: {change.status})"
        )

    # Create task log for audit trail
    task_log = create_review_task_log(
        db=db,
        action="approve",
        change_id=change_id,
        user_id=user_id,
        details={"decision_reason": request.decision_reason}
    )

    try:
        # Execute change via AI Node
        logger.info("executing_change_via_ai_node", change_id=change_id)

        # Convert change_id to integer for execute_change
        # Assumes change_id can be parsed or we use a different field
        try:
            change_id_int = int(change_id.split('_')[-1]) if '_' in change_id else int(change_id)
        except ValueError:
            # If change_id is not numeric, use target_id instead
            change_id_int = change.target_id

        result = await ai_client.execute_change(change_id=change_id_int)

        if not result.success:
            # Execution failed
            logger.error(
                "change_execution_failed",
                change_id=change_id,
                errors=result.errors
            )

            # Update change status to FAILED
            change.status = "FAILED"
            change.decision_reason = request.decision_reason
            change.approved_by = user_id
            change.approved_at = datetime.utcnow()
            change.execution_metadata = {
                "error": result.message,
                "details": result.details,
                "errors": result.errors
            }

            # Complete task log as failed
            complete_review_task_log(
                task_log=task_log,
                status="failed",
                error=result.message
            )

            db.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Change execution failed: {result.message}"
            )

        # Execution successful
        change.status = "EXECUTED"
        change.decision_reason = request.decision_reason
        change.approved_by = user_id
        change.approved_at = datetime.utcnow()
        change.executed_by = user_id
        change.executed_at = datetime.utcnow()
        change.execution_metadata = {
            "applied_at": result.applied_at.isoformat(),
            "message": result.message,
            "details": result.details
        }

        # Complete task log as successful
        complete_review_task_log(
            task_log=task_log,
            status="completed",
            output={
                "change_id": change_id,
                "status": "executed",
                "execution_result": result.message
            }
        )

        db.commit()

        logger.info(
            "change_approved_and_executed",
            change_id=change_id,
            user_id=user_id,
            task_log_id=task_log.task_id
        )

        return ReviewActionResponse(
            change_id=change_id,
            status="executed",
            message="Change approved and executed successfully",
            task_log_id=task_log.task_id
        )

    except AINodeConnectionError as e:
        # AI Node connection failed
        logger.error("ai_node_connection_failed", change_id=change_id, error=str(e))

        # Mark change as failed
        change.status = "FAILED"
        change.decision_reason = request.decision_reason
        change.approved_by = user_id
        change.approved_at = datetime.utcnow()
        change.execution_metadata = {"error": str(e)}

        # Complete task log as failed
        complete_review_task_log(
            task_log=task_log,
            status="failed",
            error=str(e)
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Node connection failed: {str(e)}"
        )

    except Exception as e:
        # Unexpected error
        logger.error("change_approval_failed", change_id=change_id, error=str(e))

        # Complete task log as failed
        complete_review_task_log(
            task_log=task_log,
            status="failed",
            error=str(e)
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve change: {str(e)}"
        )


@router.post("/{change_id}/reject", response_model=ReviewActionResponse)
def reject_change(
    change_id: str,
    request: RejectChangeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Reject an AI-generated change.

    Workflow:
    1. Validate change exists and is pending
    2. Create task_logs entry (audit trail)
    3. Update change_log status to 'REJECTED'
    4. Store rejection reason
    5. Set rejected_at and rejected_by
    6. Complete task_logs entry

    Args:
        change_id: ID of the change to reject
        request: Rejection request with reason (required)

    Returns:
        Result of rejection

    Raises:
        404: Change not found
        400: Change not in PENDING status
    """
    user_id = current_user.get("user_id")

    logger.info(
        "reject_change_started",
        change_id=change_id,
        user_id=user_id,
        reason=request.decision_reason
    )

    # Get change record
    change = db.query(ChangeLogModel).filter(
        ChangeLogModel.change_id == change_id
    ).first()

    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change with ID '{change_id}' not found"
        )

    # Validate status
    if change.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Change is not pending (current status: {change.status})"
        )

    # Create task log for audit trail
    task_log = create_review_task_log(
        db=db,
        action="reject",
        change_id=change_id,
        user_id=user_id,
        details={"decision_reason": request.decision_reason}
    )

    try:
        # Update change status
        change.status = "REJECTED"
        change.decision_reason = request.decision_reason
        change.rejected_by = user_id
        change.rejected_at = datetime.utcnow()

        # Complete task log
        complete_review_task_log(
            task_log=task_log,
            status="completed",
            output={
                "change_id": change_id,
                "status": "rejected",
                "reason": request.decision_reason
            }
        )

        db.commit()

        logger.info(
            "change_rejected",
            change_id=change_id,
            user_id=user_id,
            task_log_id=task_log.task_id
        )

        return ReviewActionResponse(
            change_id=change_id,
            status="rejected",
            message="Change rejected successfully",
            task_log_id=task_log.task_id
        )

    except Exception as e:
        logger.error("change_rejection_failed", change_id=change_id, error=str(e))

        # Complete task log as failed
        complete_review_task_log(
            task_log=task_log,
            status="failed",
            error=str(e)
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject change: {str(e)}"
        )
