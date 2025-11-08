"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Admin Integration Settings API Routes
Secure configuration management for external service integrations (AI Node, etc.)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx
import structlog
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.integrations import IntegrationSetting
from app.schemas.integrations import (
    AINodeConfigRequest,
    AINodeConfigResponse,
    AINodePingResponse,
    AINodeHealthResponse,
    HealthCheckItem
)
from app.api.deps import require_owner_claims
from app.db_models import TaskLogModel

router = APIRouter(prefix="/admin/integrations/ai-node", tags=["admin", "integrations"])
logger = structlog.get_logger(__name__)

AI_NODE_NAMESPACE = "ai_node"


@router.get("/config", response_model=AINodeConfigResponse)
def get_ai_node_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_owner_claims)
):
    """
    Get AI Node integration configuration.

    Returns configuration with bearer_token_set boolean (never echoes actual secret).
    Requires OWNER role for security.

    Returns:
        AINodeConfigResponse with base_url, bearer_token_set flag, and review_mode
    """
    config = db.query(IntegrationSetting).filter(
        IntegrationSetting.namespace == AI_NODE_NAMESPACE
    ).first()

    if not config:
        # Return default/empty config
        logger.info("ai_node_config_not_found", user_id=current_user.get("user_id"))
        return AINodeConfigResponse(
            base_url="",
            bearer_token_set=False,
            review_mode=True,
            last_updated=None,
            last_ping_status=None,
            last_ping_latency_ms=None
        )

    logger.info(
        "ai_node_config_retrieved",
        user_id=current_user.get("user_id"),
        has_secret=config.has_secret()
    )

    return AINodeConfigResponse(
        base_url=config.base_url or "",
        bearer_token_set=config.has_secret(),  # NEVER echo actual token
        review_mode=config.review_mode,
        last_updated=config.updated_at,
        last_ping_status=config.last_ping_status,
        last_ping_latency_ms=config.last_ping_latency_ms
    )


@router.post("/config", response_model=AINodeConfigResponse, status_code=status.HTTP_200_OK)
def update_ai_node_config(
    request: AINodeConfigRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_owner_claims)
):
    """
    Update AI Node integration configuration.

    Encrypts and stores bearer token using Fernet encryption at rest.
    Only OWNER role can update integration settings for security.

    Args:
        request: Configuration including base_url, bearer_token (optional), and review_mode

    Returns:
        AINodeConfigResponse with updated config (secrets masked)

    Raises:
        HTTPException: If encryption fails or validation errors occur
    """
    user_id = current_user.get("user_id")

    # Fetch or create config
    config = db.query(IntegrationSetting).filter(
        IntegrationSetting.namespace == AI_NODE_NAMESPACE
    ).first()

    if not config:
        logger.info("ai_node_config_creating", user_id=user_id)
        config = IntegrationSetting(
            namespace=AI_NODE_NAMESPACE,
            created_by=user_id
        )
        db.add(config)

    # Update fields
    config.base_url = str(request.base_url)
    config.review_mode = request.review_mode
    config.updated_by = user_id

    # Encrypt and store bearer token if provided
    if request.bearer_token is not None:
        try:
            config.set_secret(request.bearer_token)
            logger.info("ai_node_secret_updated", user_id=user_id)
        except ValueError as e:
            logger.error("ai_node_secret_encryption_failed", error=str(e), user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to encrypt bearer token: {str(e)}"
            )

    try:
        db.commit()
        db.refresh(config)
    except Exception as e:
        db.rollback()
        logger.error("ai_node_config_update_failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save configuration"
        )

    logger.info("ai_node_config_updated", user_id=user_id)

    return AINodeConfigResponse(
        base_url=config.base_url or "",
        bearer_token_set=config.has_secret(),
        review_mode=config.review_mode,
        last_updated=config.updated_at,
        last_ping_status=config.last_ping_status,
        last_ping_latency_ms=config.last_ping_latency_ms
    )


@router.post("/ping", response_model=AINodePingResponse)
async def ping_ai_node(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_owner_claims)
):
    """
    Test connection to AI Node service.

    Performs HEAD or GET request to ${base_url}/ping with Authorization header.
    Measures latency and updates last_ping_* fields in database.

    Returns:
        AINodePingResponse with success status, latency, and any error messages

    Raises:
        HTTPException: If AI Node is not configured
    """
    user_id = current_user.get("user_id")

    # Fetch config
    config = db.query(IntegrationSetting).filter(
        IntegrationSetting.namespace == AI_NODE_NAMESPACE
    ).first()

    if not config or not config.base_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI Node not configured. Please configure base URL first."
        )

    # Get decrypted bearer token
    bearer_token = None
    if config.has_secret():
        try:
            bearer_token = config.get_secret()
        except ValueError as e:
            logger.error("ai_node_secret_decryption_failed", error=str(e), user_id=user_id)
            return AINodePingResponse(
                success=False,
                status_code=None,
                latency_ms=None,
                error_message="Failed to decrypt bearer token. Check encryption key.",
                timestamp=datetime.utcnow()
            )

    # Prepare request
    ping_url = f"{config.base_url}/ping"
    headers = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    # Execute ping request with timeout
    start_time = datetime.utcnow()
    success = False
    status_code = None
    error_message = None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try HEAD first (lightweight), fall back to GET
            try:
                response = await client.head(ping_url, headers=headers, follow_redirects=True)
            except httpx.HTTPStatusError:
                # HEAD might not be supported, try GET
                response = await client.get(ping_url, headers=headers, follow_redirects=True)

            status_code = response.status_code
            success = 200 <= status_code < 300

            if not success:
                error_message = f"HTTP {status_code}: {response.reason_phrase}"
                logger.warning(
                    "ai_node_ping_failed",
                    status_code=status_code,
                    user_id=user_id
                )

    except httpx.TimeoutException:
        error_message = "Request timed out after 10 seconds"
        logger.error("ai_node_ping_timeout", url=ping_url, user_id=user_id)
    except httpx.ConnectError as e:
        error_message = f"Connection failed: {str(e)}"
        logger.error("ai_node_ping_connection_error", error=str(e), user_id=user_id)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error("ai_node_ping_error", error=str(e), user_id=user_id)

    # Calculate latency
    end_time = datetime.utcnow()
    latency_ms = int((end_time - start_time).total_seconds() * 1000)

    # Update config with ping results
    config.last_ping_status = "success" if success else "failed"
    config.last_ping_latency_ms = latency_ms if success else None
    config.last_ping_at = func.now()

    try:
        db.commit()
    except Exception as e:
        logger.error("ai_node_ping_db_update_failed", error=str(e))
        # Don't fail the ping response if DB update fails

    logger.info(
        "ai_node_ping_completed",
        success=success,
        latency_ms=latency_ms,
        user_id=user_id
    )

    return AINodePingResponse(
        success=success,
        status_code=status_code,
        latency_ms=latency_ms if success else None,
        error_message=error_message,
        timestamp=end_time
    )


@router.get("/health", response_model=AINodeHealthResponse)
async def get_ai_node_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_owner_claims)
):
    """
    Comprehensive health check for AI Node integration.

    Checks:
    - Database connectivity
    - Task logs health (recent activity, error rate)
    - AI Node service availability
    - Overall system status

    Returns:
        AINodeHealthResponse with detailed health status
    """
    user_id = current_user.get("user_id")
    check_time = datetime.utcnow()

    logger.info("ai_node_health_check_started", user_id=user_id)

    # ========================================================================
    # 1. Database Connectivity Check
    # ========================================================================

    db_check_start = datetime.utcnow()
    try:
        # Simple query to test database connection
        db.execute("SELECT 1")
        db_latency_ms = int((datetime.utcnow() - db_check_start).total_seconds() * 1000)

        database_check = HealthCheckItem(
            status="healthy",
            message="Database connection successful",
            details={"latency_ms": db_latency_ms},
            checked_at=datetime.utcnow()
        )
        logger.info("ai_node_health_db_ok", latency_ms=db_latency_ms)
    except Exception as e:
        logger.error("ai_node_health_db_failed", error=str(e))
        database_check = HealthCheckItem(
            status="unhealthy",
            message=f"Database connection failed: {str(e)}",
            details={"error": str(e)},
            checked_at=datetime.utcnow()
        )

    # ========================================================================
    # 2. Task Logs Health Check
    # ========================================================================

    try:
        # Find latest task log entry
        latest_task = db.query(TaskLogModel).order_by(
            TaskLogModel.started_at.desc()
        ).first()

        # Count errors in last 24 hours
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        error_count = db.query(func.count(TaskLogModel.id)).filter(
            TaskLogModel.status == "failed",
            TaskLogModel.started_at >= twenty_four_hours_ago
        ).scalar()

        # Count total tasks in last 24 hours
        total_count = db.query(func.count(TaskLogModel.id)).filter(
            TaskLogModel.started_at >= twenty_four_hours_ago
        ).scalar()

        # Determine task logs health status
        if not latest_task:
            task_logs_status = "degraded"
            task_logs_message = "No task logs found"
            latest_age_hours = None
        else:
            latest_age_hours = (datetime.utcnow() - latest_task.started_at).total_seconds() / 3600

            # If latest task is more than 24 hours old, consider degraded
            if latest_age_hours > 24:
                task_logs_status = "degraded"
                task_logs_message = "No recent task activity (>24h)"
            # If error rate is high (>20%), consider degraded
            elif total_count > 0 and (error_count / total_count) > 0.2:
                task_logs_status = "degraded"
                task_logs_message = f"High error rate: {error_count}/{total_count} failed"
            else:
                task_logs_status = "healthy"
                task_logs_message = "Task logs operational"

        task_logs_check = HealthCheckItem(
            status=task_logs_status,
            message=task_logs_message,
            details={
                "latest_entry_age_hours": round(latest_age_hours, 1) if latest_age_hours is not None else None,
                "error_count_24h": error_count,
                "total_count_24h": total_count,
                "latest_task_id": latest_task.job_id if latest_task else None,
                "latest_task_status": latest_task.status if latest_task else None
            },
            checked_at=datetime.utcnow()
        )

        logger.info(
            "ai_node_health_task_logs_checked",
            status=task_logs_status,
            error_count=error_count,
            total_count=total_count
        )

    except Exception as e:
        logger.error("ai_node_health_task_logs_failed", error=str(e))
        task_logs_check = HealthCheckItem(
            status="unhealthy",
            message=f"Task logs check failed: {str(e)}",
            details={"error": str(e)},
            checked_at=datetime.utcnow()
        )

    # ========================================================================
    # 3. AI Node Service Check
    # ========================================================================

    try:
        # Get AI Node configuration
        config = db.query(IntegrationSetting).filter(
            IntegrationSetting.namespace == AI_NODE_NAMESPACE
        ).first()

        if not config or not config.base_url:
            ai_node_check = HealthCheckItem(
                status="unhealthy",
                message="AI Node not configured",
                details={"configured": False},
                checked_at=datetime.utcnow()
            )
        else:
            # Get decrypted bearer token
            bearer_token = None
            if config.has_secret():
                try:
                    bearer_token = config.get_secret()
                except ValueError as e:
                    logger.error("ai_node_health_token_decrypt_failed", error=str(e))
                    ai_node_check = HealthCheckItem(
                        status="unhealthy",
                        message="Failed to decrypt AI Node bearer token",
                        details={"error": str(e)},
                        checked_at=datetime.utcnow()
                    )
                    bearer_token = None

            # Only proceed with ping if token decryption succeeded
            if bearer_token is not None or not config.has_secret():
                # Perform ping to AI Node
                ping_url = f"{config.base_url}/ping"
                headers = {}
                if bearer_token:
                    headers["Authorization"] = f"Bearer {bearer_token}"

                ping_start = datetime.utcnow()
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        try:
                            response = await client.head(ping_url, headers=headers, follow_redirects=True)
                        except httpx.HTTPStatusError:
                            response = await client.get(ping_url, headers=headers, follow_redirects=True)

                        ping_latency_ms = int((datetime.utcnow() - ping_start).total_seconds() * 1000)

                        if 200 <= response.status_code < 300:
                            ai_node_check = HealthCheckItem(
                                status="healthy",
                                message="AI Node responding",
                                details={
                                    "latency_ms": ping_latency_ms,
                                    "status_code": response.status_code,
                                    "base_url": config.base_url
                                },
                                checked_at=datetime.utcnow()
                            )
                        else:
                            ai_node_check = HealthCheckItem(
                                status="degraded",
                                message=f"AI Node returned HTTP {response.status_code}",
                                details={
                                    "status_code": response.status_code,
                                    "latency_ms": ping_latency_ms
                                },
                                checked_at=datetime.utcnow()
                            )

                except httpx.TimeoutException:
                    ai_node_check = HealthCheckItem(
                        status="unhealthy",
                        message="AI Node ping timed out",
                        details={"timeout_seconds": 10},
                        checked_at=datetime.utcnow()
                    )
                except httpx.ConnectError as e:
                    ai_node_check = HealthCheckItem(
                        status="unhealthy",
                        message=f"AI Node connection failed: {str(e)}",
                        details={"error": str(e)},
                        checked_at=datetime.utcnow()
                    )
                except Exception as e:
                    ai_node_check = HealthCheckItem(
                        status="unhealthy",
                        message=f"AI Node check failed: {str(e)}",
                        details={"error": str(e)},
                        checked_at=datetime.utcnow()
                    )

        logger.info("ai_node_health_ai_node_checked", status=ai_node_check.status)

    except Exception as e:
        logger.error("ai_node_health_ai_node_failed", error=str(e))
        ai_node_check = HealthCheckItem(
            status="unhealthy",
            message=f"AI Node check failed: {str(e)}",
            details={"error": str(e)},
            checked_at=datetime.utcnow()
        )

    # ========================================================================
    # 4. Calculate Overall Status
    # ========================================================================

    checks = [database_check, task_logs_check, ai_node_check]

    healthy_count = sum(1 for c in checks if c.status == "healthy")
    degraded_count = sum(1 for c in checks if c.status == "degraded")
    unhealthy_count = sum(1 for c in checks if c.status == "unhealthy")
    total_checks = len(checks)

    # Determine overall status
    if unhealthy_count > 0:
        overall_status = "unhealthy"
    elif degraded_count > 0:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    summary = {
        "healthy_checks": healthy_count,
        "degraded_checks": degraded_count,
        "unhealthy_checks": unhealthy_count,
        "total_checks": total_checks
    }

    logger.info(
        "ai_node_health_check_completed",
        overall_status=overall_status,
        summary=summary,
        user_id=user_id
    )

    return AINodeHealthResponse(
        overall_status=overall_status,
        timestamp=check_time,
        database=database_check,
        task_logs=task_logs_check,
        ai_node=ai_node_check,
        backups=None,  # Optional: not implemented
        wordpress=None,  # Optional: not implemented
        summary=summary
    )
