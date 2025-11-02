"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Error handling middleware.

Catches all exceptions and converts them to standardized error responses.
"""

import uuid
import traceback
from typing import Callable
from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog

from app.core.errors import (
    AppException,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    InternalError,
)


logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request_id to all requests.

    The request_id is added to:
    - Request state (accessible in route handlers)
    - Response headers (X-Request-ID)
    - Structured logs
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state
        request.state.request_id = request_id

        # Add to structured logging context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle all exceptions and return standardized error responses.

    Handles:
    - AppException (custom exceptions)
    - HTTPException (FastAPI standard)
    - RequestValidationError (Pydantic validation)
    - Generic Exception (catch-all)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response

        except AppException as exc:
            # Handle custom application exceptions
            return self._handle_app_exception(request, exc)

        except HTTPException as exc:
            # Handle FastAPI HTTPExceptions
            return self._handle_http_exception(request, exc)

        except RequestValidationError as exc:
            # Handle Pydantic validation errors
            return self._handle_validation_error(request, exc)

        except Exception as exc:
            # Catch-all for unexpected errors
            return self._handle_unexpected_error(request, exc)

    def _get_request_id(self, request: Request) -> str:
        """Get request ID from request state or generate new one."""
        return getattr(request.state, "request_id", str(uuid.uuid4()))

    def _handle_app_exception(self, request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        request_id = self._get_request_id(request)

        # Log the error
        logger.warning(
            "app_exception",
            request_id=request_id,
            error_code=exc.code.value,
            message=exc.message,
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method,
            details=exc.details,
        )

        # Create error response
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                details=exc.details if exc.details else None,
            )
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(exclude_none=True),
        )

    def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTPExceptions by mapping to error codes."""
        request_id = self._get_request_id(request)

        # Map status code to error code
        error_code = self._map_status_to_error_code(exc.status_code, exc.detail)

        # Log the error
        logger.warning(
            "http_exception",
            request_id=request_id,
            error_code=error_code.value,
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method,
        )

        # Create error response
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=error_code,
                message=exc.detail,
                details=None,
            )
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(exclude_none=True),
        )

    def _handle_validation_error(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        request_id = self._get_request_id(request)

        # Extract validation errors
        validation_errors = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            validation_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })

        # Log the error
        logger.warning(
            "validation_error",
            request_id=request_id,
            error_code=ErrorCode.ERR_VALIDATION.value,
            path=request.url.path,
            method=request.method,
            validation_errors=validation_errors,
        )

        # Create error response
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.ERR_VALIDATION,
                message="Request validation failed",
                details={"validation_errors": validation_errors},
            )
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(exclude_none=True),
        )

    def _handle_unexpected_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors (catch-all)."""
        request_id = self._get_request_id(request)

        # Log full traceback for debugging
        logger.error(
            "unexpected_error",
            request_id=request_id,
            error_code=ErrorCode.ERR_INTERNAL.value,
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            path=request.url.path,
            method=request.method,
            traceback=traceback.format_exc(),
        )

        # Create generic error response (don't expose internals)
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.ERR_INTERNAL,
                message="An unexpected error occurred. Please try again later.",
                details={"request_id": request_id},
            )
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(exclude_none=True),
        )

    def _map_status_to_error_code(self, status_code: int, detail: str) -> ErrorCode:
        """Map HTTP status code and detail to error code."""
        # Try to infer error code from detail string
        detail_lower = detail.lower()

        if status_code == 401:
            if "expired" in detail_lower:
                return ErrorCode.ERR_AUTH_EXPIRED
            elif "invalid" in detail_lower and "credentials" in detail_lower:
                return ErrorCode.ERR_AUTH_INVALID_CREDENTIALS
            else:
                return ErrorCode.ERR_AUTH_MISSING

        elif status_code == 403:
            if "admin" in detail_lower:
                return ErrorCode.ERR_FORBIDDEN_NOT_ADMIN
            else:
                return ErrorCode.ERR_FORBIDDEN

        elif status_code == 404:
            if "service" in detail_lower:
                return ErrorCode.ERR_SERVICE_NOT_FOUND
            elif "alert" in detail_lower:
                return ErrorCode.ERR_ALERT_NOT_FOUND
            elif "metric" in detail_lower:
                return ErrorCode.ERR_METRIC_NOT_FOUND
            else:
                return ErrorCode.ERR_NOT_FOUND

        elif status_code == 400:
            if "time" in detail_lower or "range" in detail_lower:
                return ErrorCode.ERR_INVALID_TIME_RANGE
            else:
                return ErrorCode.ERR_VALIDATION

        elif status_code == 429:
            return ErrorCode.ERR_RATE_LIMIT

        else:
            return ErrorCode.ERR_INTERNAL


__all__ = ["RequestIDMiddleware", "ErrorHandlerMiddleware"]
