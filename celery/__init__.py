"""
Minimal Celery stub for offline testing.

PRODUCTION NOTE: Replace this stub with the real Celery package:
    pip install celery[redis]

This stub provides basic task definition and execution for tests.
"""

from typing import Any, Callable, Dict, List, Optional
import uuid
from datetime import datetime, timedelta


class Task:
    """Stub for Celery Task."""

    def __init__(self, func: Callable, name: Optional[str] = None, **options):
        self.func = func
        self.name = name or f"{func.__module__}.{func.__name__}"
        self.max_retries = options.get("max_retries", 3)
        self.default_retry_delay = options.get("default_retry_delay", 60)
        self.bind = options.get("bind", False)
        self.ignore_result = options.get("ignore_result", False)

    def __call__(self, *args, **kwargs):
        """Execute task synchronously."""
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        """Queue task for async execution (stub returns result immediately)."""
        return AsyncResult(self(*args, **kwargs))

    def apply_async(self, args=None, kwargs=None, **options):
        """
        Apply task asynchronously.

        In stub, executes immediately and returns result.
        """
        args = args or ()
        kwargs = kwargs or {}
        result = self(*args, **kwargs)
        return AsyncResult(result)

    def retry(self, exc=None, **kwargs):
        """Retry the task."""
        raise Retry(exc=exc, **kwargs)

    def s(self, *args, **kwargs):
        """Create signature (stub)."""
        return Signature(self, args, kwargs)


class Signature:
    """Stub for Celery Signature (canvas primitive)."""

    def __init__(self, task: Task, args: tuple, kwargs: dict):
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def apply_async(self, **options):
        """Execute signature."""
        return self.task.apply_async(args=self.args, kwargs=self.kwargs, **options)

    def delay(self):
        """Execute signature with delay."""
        return self.task.delay(*self.args, **self.kwargs)


class AsyncResult:
    """Stub for Celery AsyncResult."""

    def __init__(self, result: Any, task_id: Optional[str] = None):
        self.id = task_id or str(uuid.uuid4())
        self._result = result
        self._state = "SUCCESS"

    def get(self, timeout=None, propagate=True):
        """Get task result."""
        return self._result

    def ready(self) -> bool:
        """Check if task is ready."""
        return True

    def successful(self) -> bool:
        """Check if task was successful."""
        return self._state == "SUCCESS"

    def failed(self) -> bool:
        """Check if task failed."""
        return self._state == "FAILURE"

    @property
    def state(self) -> str:
        """Get task state."""
        return self._state

    @property
    def result(self) -> Any:
        """Get task result."""
        return self._result


class Retry(Exception):
    """Exception raised to retry a task."""

    def __init__(self, exc=None, when=None, **kwargs):
        self.exc = exc
        self.when = when
        super().__init__(str(exc))


class Celery:
    """
    Minimal Celery application stub.

    Provides basic task registration and execution for testing.
    """

    def __init__(
        self,
        main: str = "app",
        broker: Optional[str] = None,
        backend: Optional[str] = None,
        **kwargs
    ):
        self.main = main
        self.conf = CeleryConfig()
        self.tasks = {}

        if broker:
            self.conf.broker_url = broker
        if backend:
            self.conf.result_backend = backend

    def task(self, *args, **options):
        """
        Decorator to register a task.

        Usage:
            @app.task
            def my_task(x, y):
                return x + y
        """
        def decorator(func: Callable) -> Task:
            task = Task(func, **options)
            self.tasks[task.name] = task
            return task

        # Handle both @app.task and @app.task()
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return decorator

    def send_task(self, name: str, args=None, kwargs=None, **options):
        """Send task by name."""
        task = self.tasks.get(name)
        if task:
            return task.apply_async(args=args, kwargs=kwargs, **options)
        return AsyncResult(None)

    def on_after_configure(self):
        """Decorator for after-configure hooks."""
        def decorator(func):
            return func
        return decorator


class CeleryConfig:
    """Celery configuration object."""

    def __init__(self):
        self.broker_url = "redis://localhost:6379/0"
        self.result_backend = "redis://localhost:6379/0"
        self.task_serializer = "json"
        self.result_serializer = "json"
        self.accept_content = ["json"]
        self.timezone = "UTC"
        self.enable_utc = True
        self.task_track_started = True
        self.task_time_limit = 30 * 60  # 30 minutes
        self.task_soft_time_limit = 25 * 60  # 25 minutes
        self.worker_max_tasks_per_child = 1000
        self.worker_prefetch_multiplier = 4

    def update(self, **kwargs):
        """Update configuration."""
        for key, value in kwargs.items():
            setattr(self, key, value)


# Beat scheduler for periodic tasks
class Beat:
    """Stub for Celery Beat scheduler."""

    def __init__(self, app: Celery):
        self.app = app
        self.schedule = {}

    def add_periodic_task(self, schedule, sig, **kwargs):
        """Add periodic task."""
        name = kwargs.get("name", sig.task.name)
        self.schedule[name] = {
            "schedule": schedule,
            "task": sig,
            **kwargs
        }


def crontab(
    minute="*",
    hour="*",
    day_of_week="*",
    day_of_month="*",
    month_of_year="*"
):
    """
    Stub for crontab schedule.

    Returns a simple dict representation.
    """
    return {
        "type": "crontab",
        "minute": minute,
        "hour": hour,
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "month_of_year": month_of_year,
    }


__all__ = [
    "Celery",
    "Task",
    "AsyncResult",
    "Retry",
    "Signature",
    "crontab",
]
