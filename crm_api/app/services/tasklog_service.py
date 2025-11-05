"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Task Log Service

Provides utilities for creating and managing task execution logs.
Used by scheduled jobs and background tasks to track progress and errors.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager
import uuid
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db_models import TaskLogModel, TaskStatus, TaskPriority

logger = structlog.get_logger(__name__)


class TaskLogService:
    """
    Service for managing task execution logs.

    Provides context managers and helpers for tracking job execution.
    """

    def __init__(self, db: Session):
        """
        Initialize task log service.

        Args:
            db: Database session
        """
        self.db = db
        self.logger = logger.bind(service="tasklog")

    # ==========================================================================
    # Task Creation
    # ==========================================================================

    def create_task(
        self,
        task_name: str,
        module: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        input_params: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> TaskLogModel:
        """
        Create a new task log entry.

        Args:
            task_name: Human-readable task name
            module: Module name (e.g., "scrape_suite", "seo_meta")
            priority: Task priority
            input_params: Input parameters dict
            task_id: Optional custom task ID (generates UUID if not provided)

        Returns:
            TaskLogModel instance
        """
        if not task_id:
            task_id = f"{module}_{uuid.uuid4().hex[:12]}"

        task = TaskLogModel(
            task_id=task_id,
            task_name=task_name,
            module=module,
            status=TaskStatus.QUEUED,
            priority=priority,
            input_params=input_params or {}
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        self.logger.info(
            "task_created",
            task_id=task_id,
            task_name=task_name,
            module=module
        )

        return task

    def start_task(self, task_id: str) -> bool:
        """
        Mark task as started.

        Args:
            task_id: Task ID

        Returns:
            True on success
        """
        task = self.db.query(TaskLogModel).filter_by(task_id=task_id).first()
        if not task:
            self.logger.warning("task_not_found", task_id=task_id)
            return False

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.db.commit()

        self.logger.info("task_started", task_id=task_id)
        return True

    # ==========================================================================
    # Task Completion
    # ==========================================================================

    def complete_task(
        self,
        task_id: str,
        items_processed: int = 0,
        items_succeeded: int = 0,
        items_failed: int = 0,
        output_summary: Optional[Dict[str, Any]] = None,
        changes_generated: int = 0,
        change_ids: Optional[list] = None
    ) -> bool:
        """
        Mark task as completed successfully.

        Args:
            task_id: Task ID
            items_processed: Total items processed
            items_succeeded: Successfully processed items
            items_failed: Failed items
            output_summary: Output data summary
            changes_generated: Number of changes created
            change_ids: List of change log IDs

        Returns:
            True on success
        """
        task = self.db.query(TaskLogModel).filter_by(task_id=task_id).first()
        if not task:
            self.logger.warning("task_not_found", task_id=task_id)
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()

        if task.started_at:
            duration = (task.completed_at - task.started_at).total_seconds()
            task.duration_seconds = duration

        task.items_processed = items_processed
        task.items_succeeded = items_succeeded
        task.items_failed = items_failed
        task.output_summary = output_summary or {}
        task.changes_generated = changes_generated
        task.change_ids = change_ids or []

        self.db.commit()

        self.logger.info(
            "task_completed",
            task_id=task_id,
            duration=task.duration_seconds,
            items_processed=items_processed,
            items_succeeded=items_succeeded,
            items_failed=items_failed
        )

        return True

    def fail_task(
        self,
        task_id: str,
        error_message: str,
        error_traceback: Optional[str] = None,
        items_processed: int = 0,
        items_succeeded: int = 0,
        items_failed: int = 0
    ) -> bool:
        """
        Mark task as failed.

        Args:
            task_id: Task ID
            error_message: Error message
            error_traceback: Full traceback
            items_processed: Items processed before failure
            items_succeeded: Successfully processed items
            items_failed: Failed items

        Returns:
            True on success
        """
        task = self.db.query(TaskLogModel).filter_by(task_id=task_id).first()
        if not task:
            self.logger.warning("task_not_found", task_id=task_id)
            return False

        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow()

        if task.started_at:
            duration = (task.completed_at - task.started_at).total_seconds()
            task.duration_seconds = duration

        task.error_message = error_message
        task.error_traceback = error_traceback
        task.items_processed = items_processed
        task.items_succeeded = items_succeeded
        task.items_failed = items_failed

        self.db.commit()

        self.logger.error(
            "task_failed",
            task_id=task_id,
            error=error_message,
            duration=task.duration_seconds
        )

        return True

    # ==========================================================================
    # Context Manager
    # ==========================================================================

    @contextmanager
    def task_execution(
        self,
        task_name: str,
        module: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        input_params: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for task execution with automatic logging.

        Usage:
            with tasklog_service.task_execution("My Task", "my_module") as task_id:
                # Do work
                # If exception raised, automatically marks as failed
                # Otherwise marks as completed

        Args:
            task_name: Human-readable task name
            module: Module name
            priority: Task priority
            input_params: Input parameters

        Yields:
            task_id: The created task ID
        """
        # Create task
        task = self.create_task(
            task_name=task_name,
            module=module,
            priority=priority,
            input_params=input_params
        )

        task_id = task.task_id

        # Start task
        self.start_task(task_id)

        try:
            yield task_id

            # If no exception, mark as completed
            self.complete_task(task_id)

        except Exception as e:
            # On exception, mark as failed
            import traceback
            error_traceback = traceback.format_exc()

            self.fail_task(
                task_id=task_id,
                error_message=str(e),
                error_traceback=error_traceback
            )

            # Re-raise exception
            raise

    # ==========================================================================
    # Progress Updates
    # ==========================================================================

    def update_progress(
        self,
        task_id: str,
        items_processed: int,
        items_succeeded: int = 0,
        items_failed: int = 0
    ) -> bool:
        """
        Update task progress metrics.

        Args:
            task_id: Task ID
            items_processed: Total items processed so far
            items_succeeded: Successfully processed items
            items_failed: Failed items

        Returns:
            True on success
        """
        task = self.db.query(TaskLogModel).filter_by(task_id=task_id).first()
        if not task:
            return False

        task.items_processed = items_processed
        task.items_succeeded = items_succeeded
        task.items_failed = items_failed

        self.db.commit()
        return True

    # ==========================================================================
    # Advisory Locks
    # ==========================================================================

    @contextmanager
    def advisory_lock(self, lock_name: str, timeout_seconds: int = 0):
        """
        Acquire PostgreSQL advisory lock to prevent concurrent execution.

        Usage:
            with tasklog_service.advisory_lock("daily_serp_snapshot"):
                # Only one process can execute this block at a time
                pass

        Args:
            lock_name: Name of the lock (will be hashed to integer)
            timeout_seconds: Wait timeout (0 = return immediately if locked)

        Yields:
            acquired: True if lock was acquired, False if already locked
        """
        # Convert lock name to integer hash
        lock_id = hash(lock_name) % (2**31 - 1)

        # Try to acquire lock
        if timeout_seconds > 0:
            # Blocking acquire with timeout
            result = self.db.execute(
                text("SELECT pg_advisory_lock(:lock_id)"),
                {"lock_id": lock_id}
            )
            acquired = True
        else:
            # Non-blocking acquire
            result = self.db.execute(
                text("SELECT pg_try_advisory_lock(:lock_id) as acquired"),
                {"lock_id": lock_id}
            )
            acquired = result.fetchone()[0]

        try:
            if acquired:
                self.logger.debug("advisory_lock_acquired", lock_name=lock_name)
            else:
                self.logger.warning("advisory_lock_busy", lock_name=lock_name)

            yield acquired

        finally:
            if acquired:
                # Release lock
                self.db.execute(
                    text("SELECT pg_advisory_unlock(:lock_id)"),
                    {"lock_id": lock_id}
                )
                self.logger.debug("advisory_lock_released", lock_name=lock_name)

    # ==========================================================================
    # Query Helpers
    # ==========================================================================

    def get_task(self, task_id: str) -> Optional[TaskLogModel]:
        """Get task by ID."""
        return self.db.query(TaskLogModel).filter_by(task_id=task_id).first()

    def get_recent_tasks(
        self,
        module: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """
        Get recent tasks.

        Args:
            module: Filter by module name
            limit: Max results

        Returns:
            List of TaskLogModel instances
        """
        query = self.db.query(TaskLogModel)

        if module:
            query = query.filter_by(module=module)

        query = query.order_by(TaskLogModel.queued_at.desc()).limit(limit)

        return query.all()

    def get_running_tasks(self, module: Optional[str] = None) -> list:
        """Get currently running tasks."""
        query = self.db.query(TaskLogModel).filter_by(status=TaskStatus.RUNNING)

        if module:
            query = query.filter_by(module=module)

        return query.all()


# ==============================================================================
# Helper: Get TaskLog Service
# ==============================================================================

def get_tasklog_service(db: Session) -> TaskLogService:
    """
    Get task log service instance.

    Args:
        db: Database session

    Returns:
        TaskLogService instance
    """
    return TaskLogService(db)
