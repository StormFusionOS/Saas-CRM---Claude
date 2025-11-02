"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Celery exceptions stub.

PRODUCTION NOTE: Use real celery.exceptions module.
"""


class CeleryError(Exception):
    """Base exception for Celery errors."""
    pass


class Retry(CeleryError):
    """Exception raised to retry a task."""

    def __init__(self, message=None, exc=None, when=None, **kwargs):
        self.exc = exc
        self.when = when
        super().__init__(message or str(exc))


class TaskRevokedError(CeleryError):
    """Exception raised when a task is revoked."""
    pass


class TimeoutError(CeleryError):
    """Exception raised when a task times out."""
    pass


class MaxRetriesExceededError(CeleryError):
    """Exception raised when max retries are exceeded."""
    pass


class SoftTimeLimitExceeded(CeleryError):
    """Exception raised when soft time limit is exceeded."""
    pass


class TimeLimitExceeded(CeleryError):
    """Exception raised when hard time limit is exceeded."""
    pass


__all__ = [
    "CeleryError",
    "Retry",
    "TaskRevokedError",
    "TimeoutError",
    "MaxRetriesExceededError",
    "SoftTimeLimitExceeded",
    "TimeLimitExceeded",
]
