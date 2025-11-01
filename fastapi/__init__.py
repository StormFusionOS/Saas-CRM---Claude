"""
Minimal FastAPI stub for offline testing.

PRODUCTION NOTE: Replace this stub with the real FastAPI package:
    pip install fastapi uvicorn[standard]

This stub provides just enough API surface for unit tests to run without
external dependencies. It is NOT a production-ready web framework.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import json


class HTTPException(Exception):
    """Stub for FastAPI HTTPException."""

    def __init__(self, status_code: int, detail: str = ""):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class Request:
    """Stub for FastAPI Request object."""

    def __init__(self, headers: Optional[Dict[str, str]] = None, body: bytes = b""):
        self.headers = headers or {}
        self.state = type('State', (), {})()
        self._body = body

    async def json(self) -> dict:
        """Parse request body as JSON."""
        return json.loads(self._body.decode('utf-8'))

    async def body(self) -> bytes:
        """Get raw request body."""
        return self._body


class Response:
    """Stub for FastAPI Response object."""

    def __init__(self, content: Any = None, status_code: int = 200, headers: Optional[Dict] = None):
        self.body = content
        self.status_code = status_code
        self.headers = headers or {}


class Depends:
    """Stub for FastAPI dependency injection."""

    def __init__(self, dependency: Optional[Callable] = None):
        self.dependency = dependency

    def __call__(self, *args, **kwargs):
        if self.dependency:
            return self.dependency(*args, **kwargs)
        return None


class APIRouter:
    """Stub for FastAPI APIRouter."""

    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.routes = []

    def get(self, path: str, **kwargs):
        """Register GET route."""
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator

    def post(self, path: str, **kwargs):
        """Register POST route."""
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator

    def put(self, path: str, **kwargs):
        """Register PUT route."""
        def decorator(func):
            self.routes.append(("PUT", path, func))
            return func
        return decorator

    def delete(self, path: str, **kwargs):
        """Register DELETE route."""
        def decorator(func):
            self.routes.append(("DELETE", path, func))
            return func
        return decorator

    def include_router(self, router: "APIRouter", **kwargs):
        """Include another router."""
        pass


class FastAPI:
    """
    Minimal FastAPI application stub.

    Provides just enough functionality for testing route registration
    and basic request/response handling.
    """

    def __init__(self, title: str = "API", version: str = "0.1.0", **kwargs):
        self.title = title
        self.version = version
        self.routes = []
        self.middleware_stack = []
        self.exception_handlers = {}
        self.state = type('State', (), {})()

    def include_router(self, router: APIRouter, prefix: str = "", tags: Optional[List[str]] = None):
        """Include an APIRouter."""
        full_prefix = prefix or router.prefix
        for method, path, handler in router.routes:
            self.routes.append((method, full_prefix + path, handler))

    def add_middleware(self, middleware_class: type, **options):
        """Add middleware to the stack."""
        self.middleware_stack.append((middleware_class, options))

    def add_exception_handler(self, exc_class: type, handler: Callable):
        """Register exception handler."""
        self.exception_handlers[exc_class] = handler

    def get(self, path: str, **kwargs):
        """Register GET route."""
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator

    def post(self, path: str, **kwargs):
        """Register POST route."""
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator

    def on_event(self, event_type: str):
        """Register startup/shutdown event handler."""
        def decorator(func):
            return func
        return decorator


class Body:
    """Stub for FastAPI Body parameter."""

    def __init__(self, default=..., **kwargs):
        self.default = default


class Query:
    """Stub for FastAPI Query parameter."""

    def __init__(self, default=..., **kwargs):
        self.default = default


class Path:
    """Stub for FastAPI Path parameter."""

    def __init__(self, default=..., **kwargs):
        self.default = default


class Header:
    """Stub for FastAPI Header parameter."""

    def __init__(self, default=..., **kwargs):
        self.default = default


class status:
    """HTTP status codes."""

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


__all__ = [
    "FastAPI",
    "APIRouter",
    "HTTPException",
    "Request",
    "Response",
    "Depends",
    "Body",
    "Query",
    "Path",
    "Header",
    "status",
]
