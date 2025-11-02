"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API Main Application.

Entry point for the CRM API service.

To run:
    python -m app.main

Or with uvicorn (when using real FastAPI):
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, leads, webhooks
from app.middleware import RequestIDMiddleware, ErrorHandlerMiddleware
import structlog


# Configure logging
structlog.configure()
logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
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

    # Import scheduler here to avoid circular imports
    from app.api.routes import scheduler

    # Include routers
    app.include_router(auth.router, prefix=settings.API_PREFIX)
    app.include_router(leads.router, prefix=settings.API_PREFIX)
    app.include_router(scheduler.router, prefix=settings.API_PREFIX)
    app.include_router(webhooks.router)  # No prefix for webhooks

    # Health check endpoint
    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "service": "crm-api",
            "version": settings.VERSION
        }

    # Metrics endpoint
    @app.get("/metrics")
    def metrics():
        """
        Metrics endpoint for monitoring.

        Returns basic application metrics. In production, this would be
        integrated with Prometheus or similar monitoring systems.
        """
        from app.db import _users, _contacts, _leads, _interactions

        return {
            "service": "crm-api",
            "version": settings.VERSION,
            "counts": {
                "users": len(_users),
                "contacts": len(_contacts),
                "leads": len(_leads),
                "interactions": len(_interactions),
            },
            "uptime_seconds": "N/A",  # Would track actual uptime in production
        }

    @app.on_event("startup")
    async def startup_event():
        """Run on application startup."""
        logger.info(
            "crm_api_starting",
            version=settings.VERSION,
            debug=settings.DEBUG
        )

    @app.on_event("shutdown")
    async def shutdown_event():
        """Run on application shutdown."""
        logger.info("crm_api_shutting_down")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    """
    Run the application directly.

    Note: This is for testing only. In production, use:
        uvicorn app.main:app --host 0.0.0.0 --port 8000
    """
    print(f"✓ {settings.APP_NAME} v{settings.VERSION} initialized")
    print(f"✓ API Prefix: {settings.API_PREFIX}")
    print(f"✓ CORS Origins: {settings.CORS_ORIGINS}")
    print(f"✓ Debug Mode: {settings.DEBUG}")
    print(f"\nNote: This stub creates an app instance for testing.")
    print(f"In production, run with: uvicorn app.main:app --host {settings.HOST} --port {settings.PORT}")
    print(f"\nRoutes registered:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            for method in route.methods:
                print(f"  {method:6} {route.path}")
