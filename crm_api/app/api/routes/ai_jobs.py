"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

AI Jobs API Endpoints
Manual trigger endpoints for AI automation jobs
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any
import structlog

from app.jobs.seo_meta_job import run_seo_meta_optimization
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/ai-jobs", tags=["ai-jobs"])
logger = structlog.get_logger()


class SEOMetaJobRequest(BaseModel):
    """Request schema for triggering SEO meta optimization job."""
    limit: int = Field(default=10, ge=1, le=100, description="Number of pages to analyze")


class JobResponse(BaseModel):
    """Response schema for job execution."""
    job_id: str
    status: str
    pages_processed: int
    changes_generated: int
    errors_count: int


@router.post("/seo-meta-optimizer", response_model=JobResponse)
async def trigger_seo_meta_optimizer(
    request: SEOMetaJobRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Manually trigger SEO meta tag optimization job.

    Analyzes WordPress pages and generates meta tag optimization suggestions.
    Requires ADMIN role.

    Args:
        request: Job configuration (limit)
        current_user: Authenticated user

    Returns:
        Job execution results
    """
    # Check authorization (ADMIN or OWNER can trigger jobs)
    user_roles = current_user.get("roles", [])
    if "ADMIN" not in user_roles and "OWNER" not in user_roles:
        raise HTTPException(status_code=403, detail="Admin or Owner access required")

    logger.info(
        "seo_meta_job_triggered",
        user_id=current_user.get("user_id"),
        limit=request.limit
    )

    try:
        # Run job
        result = await run_seo_meta_optimization(
            limit=request.limit,
            triggered_by=f"manual_user_{current_user.get('user_id')}"
        )

        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Job failed"))

        return JobResponse(**result)

    except Exception as e:
        logger.error("job_trigger_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seo-meta-optimizer/status")
async def get_seo_meta_optimizer_status(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get SEO meta optimizer module status.

    Returns:
        Module configuration and recent job stats
    """
    # TODO: Fetch from module config and recent task logs
    return {
        "module": "seo_meta_optimizer",
        "enabled": True,
        "operating_mode": "review",  # or "auto"
        "recent_jobs": []  # TODO: Query task_log
    }
