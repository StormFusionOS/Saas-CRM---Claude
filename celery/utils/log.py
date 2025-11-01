"""
Celery logging utilities stub.

PRODUCTION NOTE: Use real celery.utils.log module.
"""

import logging
from typing import Optional


def get_task_logger(name: str) -> logging.Logger:
    """
    Get a logger for a Celery task.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Set default level if not configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


class TaskLogger(logging.Logger):
    """
    Custom logger for Celery tasks.

    Stub implementation.
    """

    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)


__all__ = [
    "get_task_logger",
    "TaskLogger",
]
