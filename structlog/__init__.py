"""
Minimal structlog stub for offline testing.

PRODUCTION NOTE: Replace this stub with the real structlog package:
    pip install structlog

This stub provides basic structured logging functionality for tests.
"""

import logging
import json
from typing import Any, Dict, Optional


class BoundLogger:
    """
    Stub for structlog's BoundLogger.

    Provides basic logging with structured context.
    """

    def __init__(self, logger_name: str = "app", context: Optional[Dict] = None):
        self._logger = logging.getLogger(logger_name)
        self._context = context or {}

    def bind(self, **kwargs) -> "BoundLogger":
        """Bind additional context to logger."""
        new_context = {**self._context, **kwargs}
        return BoundLogger(self._logger.name, new_context)

    def unbind(self, *keys) -> "BoundLogger":
        """Remove context keys."""
        new_context = {k: v for k, v in self._context.items() if k not in keys}
        return BoundLogger(self._logger.name, new_context)

    def new(self, **kwargs) -> "BoundLogger":
        """Create new logger with fresh context."""
        return BoundLogger(self._logger.name, kwargs)

    def _log(self, level: str, event: str, **kwargs):
        """Internal log method."""
        log_data = {
            "event": event,
            **self._context,
            **kwargs,
        }

        # Format as JSON for structured logging
        message = json.dumps(log_data)

        # Use standard logging
        log_method = getattr(self._logger, level.lower())
        log_method(message)

    def debug(self, event: str, **kwargs):
        """Log debug message."""
        self._log("debug", event, **kwargs)

    def info(self, event: str, **kwargs):
        """Log info message."""
        self._log("info", event, **kwargs)

    def warning(self, event: str, **kwargs):
        """Log warning message."""
        self._log("warning", event, **kwargs)

    def warn(self, event: str, **kwargs):
        """Alias for warning."""
        self.warning(event, **kwargs)

    def error(self, event: str, **kwargs):
        """Log error message."""
        self._log("error", event, **kwargs)

    def critical(self, event: str, **kwargs):
        """Log critical message."""
        self._log("critical", event, **kwargs)

    def exception(self, event: str, **kwargs):
        """Log exception with traceback."""
        self._log("error", event, exc_info=True, **kwargs)


def get_logger(name: str = "app") -> BoundLogger:
    """
    Get a bound logger instance.

    Args:
        name: Logger name

    Returns:
        BoundLogger instance
    """
    return BoundLogger(name)


def configure(**kwargs):
    """
    Configure structlog (stub does nothing).

    In production, use this to set up processors, formatters, etc.
    """
    pass


def wrap_logger(logger, **kwargs) -> BoundLogger:
    """
    Wrap a standard logger with structlog interface.

    Args:
        logger: Standard library logger

    Returns:
        BoundLogger instance
    """
    return BoundLogger(logger.name)


# Convenience module-level logger
_logger = get_logger()


def bind(**kwargs):
    """Bind context to module-level logger."""
    global _logger
    _logger = _logger.bind(**kwargs)


def unbind(*keys):
    """Remove context from module-level logger."""
    global _logger
    _logger = _logger.unbind(*keys)


def debug(event: str, **kwargs):
    """Log debug message using module-level logger."""
    _logger.debug(event, **kwargs)


def info(event: str, **kwargs):
    """Log info message using module-level logger."""
    _logger.info(event, **kwargs)


def warning(event: str, **kwargs):
    """Log warning message using module-level logger."""
    _logger.warning(event, **kwargs)


def error(event: str, **kwargs):
    """Log error message using module-level logger."""
    _logger.error(event, **kwargs)


def critical(event: str, **kwargs):
    """Log critical message using module-level logger."""
    _logger.critical(event, **kwargs)


__all__ = [
    "get_logger",
    "configure",
    "wrap_logger",
    "BoundLogger",
    "bind",
    "unbind",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
]
