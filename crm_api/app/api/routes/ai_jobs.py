"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

AI Jobs API Endpoints
Manual trigger endpoints for AI automation jobs
All jobs are tracked in task_logs with standardized event-driven pattern
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
import structlog
from datetime import datetime
import uuid

from app.database import get_db
from app.db_models import TaskLogModel
from app.api.deps import require_sales_claims, require_manager_claims
from app.schemas.integrations import CtrTestIn, ContentRefreshIn, JobAck202
from app.services.ai_node_client import get_ai_node_client, AINodeClient, AINodeConnectionError

router = APIRouter(prefix="/ai/jobs", tags=["ai-jobs"])
logger = structlog.get_logger(__name__)


# ============================================================================
# Request Schemas (extending base schemas for CRM-specific fields)
# ============================================================================


class CtrTestRequest(CtrTestIn):
    """Request to trigger CTR test with optional WordPress post ID"""
    wp_post_id: Optional[int] = Field(None, description="WordPress post ID (optional)")

    @validator('page_url')
    def validate_url(cls, v):
        if not v.startswith('http://') and not v.startswith('https://'):
            raise ValueError('page_url must be a valid HTTP(S) URL')
        return v


class ContentRefreshRequest(ContentRefreshIn):
    """Request to trigger content refresh with validation"""
    pass


# ============================================================================
# Helper Functions
# ============================================================================


def create_task_log(
    db: Session,
    task_name: str,
    module: str,
    input_params: dict,
    triggered_by: str
) -> TaskLogModel:
    """
    Create a task_logs entry for a job with status='queued'.

    Args:
        db: Database session
        task_name: Name of the task (e.g., 'ctr_test')
        module: AI module name (e.g., 'ctr_optimizer')
        input_params: Input parameters for the job
        triggered_by: Who triggered the job (e.g., 'manual_user_1')

    Returns:
        Created TaskLogModel instance
    """
    task_id = f"{task_name}_{uuid.uuid4().hex[:8]}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    task_log = TaskLogModel(
        task_id=task_id,
        task_name=task_name,
        module=module,
        status="queued",
        queued_at=datetime.utcnow(),
        started_at=None,
        input_params=input_params
    )

    db.add(task_log)
    db.commit()
    db.refresh(task_log)

    logger.info(
        "task_log_created",
        task_id=task_id,
        task_name=task_name,
        module=module,
        status="queued"
    )

    return task_log


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/ctr-test", response_model=JobAck202, status_code=status.HTTP_202_ACCEPTED)
async def trigger_ctr_test(
    request: CtrTestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_manager_claims),
    ai_client: AINodeClient = Depends(get_ai_node_client)
):
    """
    Trigger a CTR (Click-Through Rate) test on the AI Node.

    Workflow:
    1. Validate the request payload
    2. Create task_logs entry with status='queued'
    3. Call AI Node client to trigger the job
    4. Return 202 Accepted with correlation ID

    The AI Node will process the job asynchronously and update task_logs
    when complete.

    Args:
        request: CTR test configuration
        db: Database session
        current_user: Authenticated user (MANAGER or OWNER)
        ai_client: AI Node client

    Returns:
        JobAck202 with job_id and correlation_id

    Raises:
        400: Invalid request parameters
        503: AI Node connection failed
    """
    user_id = current_user.get("user_id")

    logger.info(
        "ctr_test_triggered",
        user_id=user_id,
        page_url=request.page_url,
        variant_count=request.variant_count,
        test_duration_hours=request.test_duration_hours
    )

    # Create task_logs entry
    task_log = create_task_log(
        db=db,
        task_name="ctr_test",
        module="ctr_optimizer",
        input_params={
            "page_url": request.page_url,
            "wp_post_id": request.wp_post_id,
            "variant_count": request.variant_count,
            "test_duration_hours": request.test_duration_hours,
            "metadata": request.metadata,
        },
        triggered_by=f"manual_user_{user_id}"
    )

    try:
        # Trigger job on AI Node
        result = await ai_client.trigger_ctr_test(
            CtrTestIn(
                page_url=request.page_url,
                variant_count=request.variant_count,
                test_duration_hours=request.test_duration_hours,
                metadata=request.metadata
            )
        )

        logger.info(
            "ctr_test_job_accepted",
            task_id=task_log.task_id,
            job_id=result.job_id,
            correlation_id=result.correlation_id
        )

        # Update task_log with correlation info
        task_log.input_params["ai_node_job_id"] = result.job_id
        task_log.input_params["correlation_id"] = result.correlation_id
        db.commit()

        return JobAck202(
            job_id=task_log.task_id,
            correlation_id=result.correlation_id,
            status="accepted",
            message=f"CTR test job queued successfully. Testing {request.variant_count} variants over {request.test_duration_hours} hours.",
            estimated_completion_seconds=result.estimated_completion_seconds
        )

    except AINodeConnectionError as e:
        logger.error(
            "ctr_test_connection_failed",
            task_id=task_log.task_id,
            error=str(e)
        )

        # Update task_log status
        task_log.status = "failed"
        task_log.error_message = f"AI Node connection failed: {str(e)}"
        task_log.completed_at = datetime.utcnow()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Node connection failed: {str(e)}"
        )

    except Exception as e:
        logger.error(
            "ctr_test_trigger_failed",
            task_id=task_log.task_id,
            error=str(e),
            exc_info=True
        )

        # Update task_log status
        task_log.status = "failed"
        task_log.error_message = str(e)
        task_log.completed_at = datetime.utcnow()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger CTR test: {str(e)}"
        )


@router.post("/content-refresh", response_model=JobAck202, status_code=status.HTTP_202_ACCEPTED)
async def trigger_content_refresh(
    request: ContentRefreshRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_manager_claims),
    ai_client: AINodeClient = Depends(get_ai_node_client)
):
    """
    Trigger a content refresh job on the AI Node.

    Workflow:
    1. Validate the request payload
    2. Create task_logs entry with status='queued'
    3. Call AI Node client to trigger the job
    4. Return 202 Accepted with correlation ID

    The AI Node will process the job asynchronously and update task_logs
    when complete.

    Args:
        request: Content refresh configuration
        db: Database session
        current_user: Authenticated user (MANAGER or OWNER)
        ai_client: AI Node client

    Returns:
        JobAck202 with job_id and correlation_id

    Raises:
        400: Invalid request parameters
        503: AI Node connection failed
    """
    user_id = current_user.get("user_id")

    logger.info(
        "content_refresh_triggered",
        user_id=user_id,
        content_type=request.content_type,
        content_id=request.content_id,
        refresh_strategy=request.refresh_strategy
    )

    # Create task_logs entry
    task_log = create_task_log(
        db=db,
        task_name="content_refresh",
        module="content_optimizer",
        input_params={
            "content_type": request.content_type,
            "content_id": request.content_id,
            "refresh_strategy": request.refresh_strategy,
            "metadata": request.metadata,
        },
        triggered_by=f"manual_user_{user_id}"
    )

    try:
        # Trigger job on AI Node
        result = await ai_client.trigger_content_refresh(request)

        logger.info(
            "content_refresh_job_accepted",
            task_id=task_log.task_id,
            job_id=result.job_id,
            correlation_id=result.correlation_id
        )

        # Update task_log with correlation info
        task_log.input_params["ai_node_job_id"] = result.job_id
        task_log.input_params["correlation_id"] = result.correlation_id
        db.commit()

        return JobAck202(
            job_id=task_log.task_id,
            correlation_id=result.correlation_id,
            status="accepted",
            message=f"Content refresh job queued successfully. Refreshing {request.content_type} #{request.content_id} using {request.refresh_strategy} strategy.",
            estimated_completion_seconds=result.estimated_completion_seconds
        )

    except AINodeConnectionError as e:
        logger.error(
            "content_refresh_connection_failed",
            task_id=task_log.task_id,
            error=str(e)
        )

        # Update task_log status
        task_log.status = "failed"
        task_log.error_message = f"AI Node connection failed: {str(e)}"
        task_log.completed_at = datetime.utcnow()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Node connection failed: {str(e)}"
        )

    except Exception as e:
        logger.error(
            "content_refresh_trigger_failed",
            task_id=task_log.task_id,
            error=str(e),
            exc_info=True
        )

        # Update task_log status
        task_log.status = "failed"
        task_log.error_message = str(e)
        task_log.completed_at = datetime.utcnow()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger content refresh: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_job_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_sales_claims)
):
    """
    Get the status of a triggered job by task_id.

    Args:
        task_id: Task ID returned from job trigger endpoint
        db: Database session
        current_user: Authenticated user

    Returns:
        Task log details with current status

    Raises:
        404: Task not found
    """
    task_log = db.query(TaskLogModel).filter(
        TaskLogModel.task_id == task_id
    ).first()

    if not task_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found"
        )

    return {
        "task_id": task_log.task_id,
        "task_name": task_log.task_name,
        "module": task_log.module,
        "status": task_log.status,
        "queued_at": task_log.queued_at,
        "started_at": task_log.started_at,
        "completed_at": task_log.completed_at,
        "duration_seconds": task_log.duration_seconds,
        "input_params": task_log.input_params,
        "output_summary": task_log.output_summary,
        "error_message": task_log.error_message,
    }
