"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Error codes and exception handling.

Provides consistent error codes, exception classes, and response formatting
for the CRM API.
"""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """
    Standardized error codes for the CRM API.

    All errors follow the pattern: ERR_<CATEGORY>_<SPECIFIC>
    """
    # Authentication errors (4xx)
    ERR_AUTH_INVALID_CREDENTIALS = "ERR_AUTH_INVALID_CREDENTIALS"
    ERR_AUTH_EXPIRED = "ERR_AUTH_EXPIRED"
    ERR_AUTH_MISSING = "ERR_AUTH_MISSING"
    ERR_AUTH_INVALID_TOKEN = "ERR_AUTH_INVALID_TOKEN"

    # Authorization errors (4xx)
    ERR_FORBIDDEN = "ERR_FORBIDDEN"
    ERR_FORBIDDEN_REALM = "ERR_FORBIDDEN_REALM"
    ERR_FORBIDDEN_INACTIVE = "ERR_FORBIDDEN_INACTIVE"

    # Resource errors (4xx)
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_RESOURCE_NOT_FOUND = "ERR_RESOURCE_NOT_FOUND"
    ERR_CONTACT_NOT_FOUND = "ERR_CONTACT_NOT_FOUND"
    ERR_LEAD_NOT_FOUND = "ERR_LEAD_NOT_FOUND"
    ERR_USER_NOT_FOUND = "ERR_USER_NOT_FOUND"

    # Validation errors (4xx)
    ERR_VALIDATION = "ERR_VALIDATION"
    ERR_DUPLICATE_EMAIL = "ERR_DUPLICATE_EMAIL"
    ERR_INVALID_INPUT = "ERR_INVALID_INPUT"
    ERR_MISSING_FIELD = "ERR_MISSING_FIELD"
    ERR_CONTACT_HAS_LEADS = "ERR_CONTACT_HAS_LEADS"

    # Webhook errors (4xx)
    ERR_WEBHOOK_SIGNATURE = "ERR_WEBHOOK_SIGNATURE"
    ERR_WEBHOOK_VERIFICATION = "ERR_WEBHOOK_VERIFICATION"
    ERR_WEBHOOK_INVALID_SECRET = "ERR_WEBHOOK_INVALID_SECRET"

    # Rate limiting (4xx)
    ERR_RATE_LIMIT = "ERR_RATE_LIMIT"
    ERR_RATE_LIMIT_EXCEEDED = "ERR_RATE_LIMIT_EXCEEDED"

    # Server errors (5xx)
    ERR_INTERNAL = "ERR_INTERNAL"
    ERR_DATABASE = "ERR_DATABASE"
    ERR_EXTERNAL_SERVICE = "ERR_EXTERNAL_SERVICE"
    ERR_INGESTION = "ERR_INGESTION"


class ErrorDetail(BaseModel):
    """Error detail model for consistent error responses."""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """
    Standard error response envelope.

    All errors are returned in this format:
    {
        "error": {
            "code": "ERR_AUTH_EXPIRED",
            "message": "Your session has expired",
            "details": { ... }
        }
    }
    """
    error: ErrorDetail


class AppException(Exception):
    """
    Base exception for all application errors.

    All custom exceptions should inherit from this class.
    """
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppException):
    """Authentication-related errors (401)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_AUTH_INVALID_CREDENTIALS,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=401, details=details)


class AuthorizationError(AppException):
    """Authorization-related errors (403)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_FORBIDDEN,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=403, details=details)


class NotFoundError(AppException):
    """Resource not found errors (404)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_NOT_FOUND,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=404, details=details)


class ValidationError(AppException):
    """Validation errors (400)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_VALIDATION,
        message: str = "Invalid input",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=400, details=details)


class WebhookError(AppException):
    """Webhook-related errors (403)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_WEBHOOK_SIGNATURE,
        message: str = "Webhook verification failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=403, details=details)


class RateLimitError(AppException):
    """Rate limiting errors (429)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_RATE_LIMIT,
        message: str = "Too many requests",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=429, details=details)


class InternalError(AppException):
    """Internal server errors (500)."""
    def __init__(
        self,
        code: ErrorCode = ErrorCode.ERR_INTERNAL,
        message: str = "An internal error occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(code=code, message=message, status_code=500, details=details)


# Error code to HTTP status code mapping
ERROR_STATUS_MAP = {
    # 401 Unauthorized
    ErrorCode.ERR_AUTH_INVALID_CREDENTIALS: 401,
    ErrorCode.ERR_AUTH_EXPIRED: 401,
    ErrorCode.ERR_AUTH_MISSING: 401,
    ErrorCode.ERR_AUTH_INVALID_TOKEN: 401,

    # 403 Forbidden
    ErrorCode.ERR_FORBIDDEN: 403,
    ErrorCode.ERR_FORBIDDEN_REALM: 403,
    ErrorCode.ERR_FORBIDDEN_INACTIVE: 403,
    ErrorCode.ERR_WEBHOOK_SIGNATURE: 403,
    ErrorCode.ERR_WEBHOOK_VERIFICATION: 403,
    ErrorCode.ERR_WEBHOOK_INVALID_SECRET: 403,

    # 404 Not Found
    ErrorCode.ERR_NOT_FOUND: 404,
    ErrorCode.ERR_RESOURCE_NOT_FOUND: 404,
    ErrorCode.ERR_CONTACT_NOT_FOUND: 404,
    ErrorCode.ERR_LEAD_NOT_FOUND: 404,
    ErrorCode.ERR_USER_NOT_FOUND: 404,

    # 400 Bad Request
    ErrorCode.ERR_VALIDATION: 400,
    ErrorCode.ERR_DUPLICATE_EMAIL: 400,
    ErrorCode.ERR_INVALID_INPUT: 400,
    ErrorCode.ERR_MISSING_FIELD: 400,
    ErrorCode.ERR_CONTACT_HAS_LEADS: 400,

    # 429 Too Many Requests
    ErrorCode.ERR_RATE_LIMIT: 429,
    ErrorCode.ERR_RATE_LIMIT_EXCEEDED: 429,

    # 500 Internal Server Error
    ErrorCode.ERR_INTERNAL: 500,
    ErrorCode.ERR_DATABASE: 500,
    ErrorCode.ERR_EXTERNAL_SERVICE: 500,
    ErrorCode.ERR_INGESTION: 500,
}


def get_status_code(error_code: ErrorCode) -> int:
    """Get HTTP status code for an error code."""
    return ERROR_STATUS_MAP.get(error_code, 500)


__all__ = [
    "ErrorCode",
    "ErrorDetail",
    "ErrorResponse",
    "AppException",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "WebhookError",
    "RateLimitError",
    "InternalError",
    "get_status_code",
]
