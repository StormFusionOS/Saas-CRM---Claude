"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Structured Logging Module

Provides ECS-like structured logging with JSON Lines output, PII redaction,
and distributed tracing support.

Features:
- JSON Lines format for easy parsing
- ECS (Elastic Common Schema) compatible field names
- PII redaction (email, IP, tokens, passwords)
- W3C traceparent integration
- Automatic context enrichment
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

Usage:
    from observability.logger import get_logger

    logger = get_logger(__name__)
    logger.info("User logged in", user_id="user123", ip_address="192.168.1.1")
"""

import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path


# PII redaction patterns
PII_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "ipv4": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "ipv6": re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),
    "credit_card": re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "jwt": re.compile(r'\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'),
    "bearer_token": re.compile(r'\bBearer\s+[A-Za-z0-9_-]+\b', re.IGNORECASE),
    "api_key": re.compile(r'\b[A-Za-z0-9]{32,}\b'),  # Generic long alphanumeric strings
}

# Sensitive field names to redact
SENSITIVE_FIELDS = {
    "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
    "authorization", "auth", "credentials", "private_key", "access_token",
    "refresh_token", "session_id", "cookie", "x-api-key"
}


class PIIRedactor:
    """Redact PII from log messages and fields"""

    @staticmethod
    def redact_text(text: str) -> str:
        """Redact PII from text"""
        if not isinstance(text, str):
            return text

        redacted = text

        # Redact email addresses
        redacted = PII_PATTERNS["email"].sub("[EMAIL_REDACTED]", redacted)

        # Redact IP addresses
        redacted = PII_PATTERNS["ipv4"].sub("[IP_REDACTED]", redacted)
        redacted = PII_PATTERNS["ipv6"].sub("[IP_REDACTED]", redacted)

        # Redact credit cards
        redacted = PII_PATTERNS["credit_card"].sub("[CC_REDACTED]", redacted)

        # Redact SSN
        redacted = PII_PATTERNS["ssn"].sub("[SSN_REDACTED]", redacted)

        # Redact JWT tokens
        redacted = PII_PATTERNS["jwt"].sub("[JWT_REDACTED]", redacted)

        # Redact bearer tokens
        redacted = PII_PATTERNS["bearer_token"].sub("Bearer [TOKEN_REDACTED]", redacted)

        return redacted

    @staticmethod
    def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields from dictionary"""
        if not isinstance(data, dict):
            return data

        redacted = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Check if field name is sensitive
            if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, str):
                redacted[key] = PIIRedactor.redact_text(value)
            elif isinstance(value, dict):
                redacted[key] = PIIRedactor.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    PIIRedactor.redact_dict(item) if isinstance(item, dict)
                    else PIIRedactor.redact_text(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                redacted[key] = value

        return redacted


class StructuredFormatter(logging.Formatter):
    """Format logs as JSON Lines with ECS-like fields"""

    def __init__(self, service_name: str = "rivercityclean", service_version: str = "1.0.0"):
        super().__init__()
        self.service_name = service_name
        self.service_version = service_version
        self.hostname = self._get_hostname()

    @staticmethod
    def _get_hostname() -> str:
        """Get hostname"""
        import socket
        try:
            return socket.gethostname()
        except Exception:
            return "unknown"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON Line"""

        # Base ECS fields
        log_entry = {
            "@timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "log.level": record.levelname,
            "log.logger": record.name,
            "message": record.getMessage(),
            "ecs.version": "8.0.0",

            # Service fields
            "service.name": self.service_name,
            "service.version": self.service_version,

            # Host fields
            "host.hostname": self.hostname,

            # Process fields
            "process.thread.id": record.thread,
            "process.thread.name": record.threadName,
        }

        # Add file/line information
        if record.pathname:
            log_entry["log.origin"] = {
                "file.name": record.filename,
                "file.line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_entry["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Exception",
                "message": str(record.exc_info[1]) if record.exc_info[1] else "",
                "stack_trace": self.formatException(record.exc_info) if record.exc_info else "",
            }

        # Add custom fields from extra
        if hasattr(record, "custom_fields"):
            custom = record.custom_fields

            # Add HTTP fields if present
            if "http_method" in custom:
                log_entry["http"] = {
                    "request.method": custom.get("http_method"),
                    "request.path": custom.get("http_path"),
                    "response.status_code": custom.get("http_status"),
                    "request.bytes": custom.get("http_request_bytes"),
                    "response.bytes": custom.get("http_response_bytes"),
                }

            # Add user fields if present
            if "user_id" in custom:
                log_entry["user"] = {
                    "id": custom.get("user_id"),
                    "name": custom.get("user_name"),
                    "email": custom.get("user_email"),
                }

            # Add client fields if present
            if "client_ip" in custom:
                log_entry["client"] = {
                    "ip": custom.get("client_ip"),
                    "user_agent": custom.get("user_agent"),
                }

            # Add trace context if present
            if "trace_id" in custom:
                log_entry["trace"] = {
                    "id": custom.get("trace_id"),
                }
                log_entry["span"] = {
                    "id": custom.get("span_id"),
                }

            # Add event fields if present
            if "event_action" in custom:
                log_entry["event"] = {
                    "action": custom.get("event_action"),
                    "category": custom.get("event_category"),
                    "type": custom.get("event_type"),
                    "outcome": custom.get("event_outcome"),
                    "duration": custom.get("event_duration"),
                }

            # Add any remaining custom fields
            for key, value in custom.items():
                if key not in ["http_method", "http_path", "http_status", "http_request_bytes",
                               "http_response_bytes", "user_id", "user_name", "user_email",
                               "client_ip", "user_agent", "trace_id", "span_id",
                               "event_action", "event_category", "event_type", "event_outcome", "event_duration"]:
                    log_entry["labels"] = log_entry.get("labels", {})
                    log_entry["labels"][key] = value

        # Redact PII
        log_entry = PIIRedactor.redact_dict(log_entry)

        return json.dumps(log_entry, default=str)


class StructuredLogger(logging.Logger):
    """Enhanced logger with structured logging support"""

    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log with custom context fields"""
        extra = kwargs.pop("extra", {})

        # Extract custom fields from kwargs
        custom_fields = {k: v for k, v in kwargs.items() if k not in ["exc_info", "stack_info", "stacklevel"]}

        if custom_fields:
            extra["custom_fields"] = custom_fields

        # Remove custom fields from kwargs to avoid passing them to Logger._log
        for key in custom_fields.keys():
            kwargs.pop(key, None)

        super()._log(level, msg, args, extra=extra, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log_with_context(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)


# Configure structured logging
logging.setLoggerClass(StructuredLogger)


def get_logger(name: str, service_name: str = "rivercityclean",
               log_file: Optional[str] = None, log_level: str = "INFO") -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)
        service_name: Service name for ECS fields
        log_file: Optional file path for log output
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        StructuredLogger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = StructuredFormatter(service_name=service_name)

    # Add stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Singleton logger instances for common services
crm_logger = get_logger("crm_api", service_name="crm_api",
                        log_file="logs/crm_api.jsonl", log_level="INFO")
ops_logger = get_logger("ops_api", service_name="ops_api",
                        log_file="logs/ops_api.jsonl", log_level="INFO")
