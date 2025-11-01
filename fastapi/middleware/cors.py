"""
Minimal CORS middleware stub for offline testing.

PRODUCTION NOTE: Use the real FastAPI CORS middleware:
    from fastapi.middleware.cors import CORSMiddleware
"""

from typing import List, Optional


class CORSMiddleware:
    """
    Stub CORS middleware for testing.

    In production, use fastapi.middleware.cors.CORSMiddleware
    """

    def __init__(
        self,
        app,
        allow_origins: Optional[List[str]] = None,
        allow_credentials: bool = False,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 600,
    ):
        self.app = app
        self.allow_origins = allow_origins or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.max_age = max_age

    def __call__(self, *args, **kwargs):
        """Middleware call handler."""
        # Stub implementation for testing
        return self.app(*args, **kwargs)


__all__ = ["CORSMiddleware"]
