"""Scheduler routes for task management."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from app.api.deps import require_sales_claims


router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/next")
def get_next_task(
    claims: dict = Depends(require_sales_claims)
) -> dict:
    """
    Get the next scheduled task to execute.

    This is a lightweight endpoint for performance testing
    that simulates task scheduling logic.

    Args:
        claims: JWT claims

    Returns:
        Next task information
    """
    # Simulate fetching next task from queue
    # In production, this would query a task queue or scheduler
    return {
        "task_id": "task_123",
        "task_type": "send_followup_email",
        "scheduled_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "priority": "normal",
        "metadata": {
            "lead_id": 42,
            "template": "followup_v1"
        }
    }


__all__ = ["router"]
