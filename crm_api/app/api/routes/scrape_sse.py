"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Scrape Suite Server-Sent Events (SSE)

Real-time streaming of job progress and status updates.
"""

import json
import asyncio
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.deps import require_owner_or_admin_claims
from app.db_models import TaskLogModel, TaskStatus
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/scrape", tags=["Scrape Suite", "Streaming"])


class JobProgressStream:
    """
    Manager for streaming job progress via SSE.

    Polls task_logs for job status and streams updates to client.
    """

    def __init__(self, job_id: str, db: Session):
        """
        Initialize stream manager.

        Args:
            job_id: Job/task ID to monitor
            db: Database session
        """
        self.job_id = job_id
        self.db = db
        self.last_status = None
        self.last_items_processed = 0
        self.logger = logger.bind(job_id=job_id)

    async def generate_events(self):
        """
        Generate SSE events for job progress.

        Yields:
            SSE-formatted event strings
        """
        try:
            # Send initial connection event
            yield self._format_sse_event({
                "event": "connected",
                "job_id": self.job_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Poll for updates until job completes
            while True:
                task = self.db.query(TaskLogModel).filter_by(
                    task_id=self.job_id
                ).first()

                if not task:
                    # Job not found
                    yield self._format_sse_event({
                        "event": "error",
                        "job_id": self.job_id,
                        "message": "Job not found",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    break

                # Check if status changed
                current_status = task.status.value
                if current_status != self.last_status:
                    self.logger.info(
                        "job_status_changed",
                        old_status=self.last_status,
                        new_status=current_status
                    )

                    yield self._format_sse_event({
                        "event": "status_change",
                        "job_id": self.job_id,
                        "status": current_status,
                        "task_name": task.task_name,
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    self.last_status = current_status

                # Check if progress changed
                if task.items_processed != self.last_items_processed:
                    yield self._format_sse_event({
                        "event": "progress",
                        "job_id": self.job_id,
                        "status": current_status,
                        "items_processed": task.items_processed,
                        "items_succeeded": task.items_succeeded,
                        "items_failed": task.items_failed,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    self.last_items_processed = task.items_processed

                # Check if job completed
                if current_status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                    # Send final event
                    yield self._format_sse_event({
                        "event": "completed" if current_status == TaskStatus.COMPLETED.value else "failed",
                        "job_id": self.job_id,
                        "status": current_status,
                        "task_name": task.task_name,
                        "items_processed": task.items_processed,
                        "items_succeeded": task.items_succeeded,
                        "items_failed": task.items_failed,
                        "duration_seconds": task.duration_seconds,
                        "error_message": task.error_message,
                        "output_summary": task.output_summary,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    self.logger.info(
                        "job_completed",
                        status=current_status,
                        duration=task.duration_seconds
                    )
                    break

                # Wait before next poll
                await asyncio.sleep(2)  # Poll every 2 seconds

        except asyncio.CancelledError:
            # Client disconnected
            self.logger.info("client_disconnected")
            yield self._format_sse_event({
                "event": "disconnected",
                "job_id": self.job_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            raise

        except Exception as e:
            # Unexpected error
            self.logger.error("stream_error", error=str(e))
            yield self._format_sse_event({
                "event": "error",
                "job_id": self.job_id,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    def _format_sse_event(self, data: dict) -> str:
        """
        Format data as SSE event.

        SSE format:
        data: {json}\\n\\n

        Args:
            data: Event data dict

        Returns:
            SSE-formatted string
        """
        json_data = json.dumps(data)
        return f"data: {json_data}\n\n"


@router.get("/stream/job/{job_id}")
async def stream_job_progress(
    job_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_owner_or_admin_claims)
):
    """
    Stream job progress via Server-Sent Events (SSE).

    Opens a persistent connection and streams job status and progress updates
    in real-time until the job completes or fails.

    Args:
        job_id: Job/task ID to monitor
        db: Database session
        claims: JWT claims (requires owner or admin)

    Returns:
        StreamingResponse with SSE events

    Example:
        GET /scrape/stream/job/serp_abc123

        Client receives events:
        data: {"event": "connected", "job_id": "serp_abc123", ...}
        data: {"event": "status_change", "status": "running", ...}
        data: {"event": "progress", "items_processed": 5, ...}
        data: {"event": "completed", "status": "completed", ...}
    """
    logger.info(
        "job_stream_started",
        job_id=job_id,
        user=claims.get("sub")
    )

    stream = JobProgressStream(job_id, db)

    return StreamingResponse(
        stream.generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/stream/all-jobs")
async def stream_all_jobs(
    module: Optional[str] = Query(None, description="Filter by module (e.g., scrape_suite)"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_owner_or_admin_claims)
):
    """
    Stream updates for all active jobs.

    Monitors all running jobs and streams status/progress updates.
    Useful for dashboard views showing multiple jobs.

    Args:
        module: Filter by module name
        db: Database session
        claims: JWT claims

    Returns:
        StreamingResponse with SSE events for all jobs
    """
    async def generate_events():
        """Generate SSE events for all active jobs."""
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'event': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

            tracked_jobs = {}  # Track last known state for each job

            while True:
                # Query for active jobs
                query = db.query(TaskLogModel).filter(
                    TaskLogModel.status.in_([
                        TaskStatus.QUEUED,
                        TaskStatus.RUNNING,
                        TaskStatus.RETRYING
                    ])
                )

                if module:
                    query = query.filter(TaskLogModel.module == module)

                active_jobs = query.all()

                # Check each active job for updates
                for job in active_jobs:
                    job_id = job.task_id
                    current_state = {
                        "status": job.status.value,
                        "items_processed": job.items_processed
                    }

                    last_state = tracked_jobs.get(job_id)

                    # If new job or state changed, send update
                    if last_state is None or last_state != current_state:
                        yield f"data: {json.dumps({
                            'event': 'job_update',
                            'job_id': job_id,
                            'task_name': job.task_name,
                            'module': job.module,
                            'status': job.status.value,
                            'items_processed': job.items_processed,
                            'items_succeeded': job.items_succeeded,
                            'items_failed': job.items_failed,
                            'started_at': job.started_at.isoformat() if job.started_at else None,
                            'timestamp': datetime.utcnow().isoformat()
                        })}\n\n"

                        tracked_jobs[job_id] = current_state

                # Check for completed jobs
                completed_jobs = db.query(TaskLogModel).filter(
                    TaskLogModel.task_id.in_(list(tracked_jobs.keys())),
                    TaskLogModel.status.in_([
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                        TaskStatus.CANCELLED
                    ])
                ).all()

                for job in completed_jobs:
                    job_id = job.task_id

                    # Send completion event
                    yield f"data: {json.dumps({
                        'event': 'job_completed',
                        'job_id': job_id,
                        'task_name': job.task_name,
                        'module': job.module,
                        'status': job.status.value,
                        'items_processed': job.items_processed,
                        'items_succeeded': job.items_succeeded,
                        'items_failed': job.items_failed,
                        'duration_seconds': job.duration_seconds,
                        'error_message': job.error_message,
                        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                        'timestamp': datetime.utcnow().isoformat()
                    })}\n\n"

                    # Remove from tracking
                    del tracked_jobs[job_id]

                # Wait before next poll
                await asyncio.sleep(3)  # Poll every 3 seconds

        except asyncio.CancelledError:
            logger.info("all_jobs_stream_disconnected")
            yield f"data: {json.dumps({'event': 'disconnected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            raise

        except Exception as e:
            logger.error("all_jobs_stream_error", error=str(e))
            yield f"data: {json.dumps({'event': 'error', 'message': str(e), 'timestamp': datetime.utcnow().isoformat()})}\n\n"

    logger.info(
        "all_jobs_stream_started",
        module=module,
        user=claims.get("sub")
    )

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
