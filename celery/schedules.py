"""
Celery schedules stub.

PRODUCTION NOTE: Use real celery.schedules module.
"""

from datetime import datetime, timedelta
from typing import Optional


class schedule:
    """Base schedule class."""

    def __init__(self, run_every: Optional[timedelta] = None):
        self.run_every = run_every or timedelta(seconds=0)

    def remaining_estimate(self, last_run_at: datetime) -> timedelta:
        """Estimate time remaining until next run."""
        if not last_run_at:
            return timedelta(seconds=0)

        next_run = last_run_at + self.run_every
        now = datetime.utcnow()

        if next_run <= now:
            return timedelta(seconds=0)

        return next_run - now

    def is_due(self, last_run_at: Optional[datetime] = None) -> tuple:
        """
        Check if schedule is due.

        Returns:
            Tuple of (is_due: bool, next_time_to_run: float)
        """
        if not last_run_at:
            return True, 0.0

        remaining = self.remaining_estimate(last_run_at)
        if remaining.total_seconds() <= 0:
            return True, 0.0

        return False, remaining.total_seconds()


class crontab(schedule):
    """
    Crontab-like schedule.

    Simple stub that mimics crontab schedule behavior.
    """

    def __init__(
        self,
        minute="*",
        hour="*",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    ):
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.month_of_year = month_of_year

    def __repr__(self):
        return (
            f"<crontab: {self.minute} {self.hour} {self.day_of_month} "
            f"{self.month_of_year} {self.day_of_week}>"
        )

    def is_due(self, last_run_at: Optional[datetime] = None) -> tuple:
        """
        Check if crontab schedule is due.

        Simplified logic for testing.
        """
        # Stub: just check if enough time has passed (5 minutes default)
        if not last_run_at:
            return True, 0.0

        now = datetime.utcnow()
        elapsed = (now - last_run_at).total_seconds()

        # Simple heuristic: run every 5 minutes minimum
        if elapsed >= 300:
            return True, 0.0

        return False, 300 - elapsed


class solar(schedule):
    """
    Solar event-based schedule (sunrise, sunset, etc.).

    Stub implementation.
    """

    def __init__(self, event: str, lat: float, lon: float):
        self.event = event  # "sunrise", "sunset", etc.
        self.lat = lat
        self.lon = lon

    def is_due(self, last_run_at: Optional[datetime] = None) -> tuple:
        """Check if solar schedule is due."""
        # Stub: always return not due for testing
        return False, 86400.0  # Check again in 24 hours


__all__ = [
    "schedule",
    "crontab",
    "solar",
]
