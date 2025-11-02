"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Ops API Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware import RequestIDMiddleware, ErrorHandlerMiddleware
import structlog

structlog.configure()
logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
    )

    # Error handling middleware (must be first to catch all errors)
    app.add_middleware(ErrorHandlerMiddleware)

    # Request ID middleware (adds request_id to all requests)
    app.add_middleware(RequestIDMiddleware)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "ops-api", "version": settings.VERSION}

    # Metrics endpoint
    @app.get("/metrics")
    def metrics():
        """
        Metrics endpoint for monitoring.

        Returns basic application metrics. In production, this would be
        integrated with Prometheus or similar monitoring systems.
        """
        return {
            "service": "ops-api",
            "version": settings.VERSION,
            "counts": {
                "services": 12,  # Placeholder - would query actual data
                "alerts": 3,
                "deployments": 0,
            },
            "system": {
                "cpu_usage": "45%",  # Placeholder - would query actual metrics
                "memory_usage": "62%",
            },
            "uptime_seconds": "N/A",  # Would track actual uptime in production
        }

    return app


app = create_app()


if __name__ == "__main__":
    print(f"✓ {settings.APP_NAME} v{settings.VERSION} initialized")
    print(f"Note: Run with uvicorn app.main:app --host {settings.HOST} --port {settings.PORT}")
