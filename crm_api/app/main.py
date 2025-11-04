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
from app.api.routes import auth, leads, webhooks, pricebook, estimates, quotes, proposals
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
    app.include_router(pricebook.router, prefix=settings.API_PREFIX)
    app.include_router(estimates.router, prefix=settings.API_PREFIX)

    # Quotes router - mounted under /sales scope as required
    app.include_router(quotes.router, prefix=f"{settings.API_PREFIX}/sales")

    # Proposals router - also under /sales scope
    app.include_router(proposals.router, prefix=f"{settings.API_PREFIX}/sales")

    # Scheduling router - customer self-scheduling (public endpoints)
    from app.api.routes import scheduling
    app.include_router(scheduling.router, prefix=settings.API_PREFIX)

    # Forms router - SmartForm Builder (mixed public/staff endpoints)
    from app.api.routes import forms
    app.include_router(forms.router, prefix=settings.API_PREFIX)

    # Follow-Up Automation router - automated follow-up sequences (staff endpoints)
    from app.api.routes import followup
    app.include_router(followup.router, prefix=settings.API_PREFIX)

    # Packages & Bundles router - service packages (mixed staff/public endpoints)
    from app.api.routes import packages
    app.include_router(packages.router, prefix=settings.API_PREFIX)

    # Calendar Connections router - calendar integration (staff endpoints)
    from app.api.routes import calendar
    app.include_router(calendar.router, prefix=settings.API_PREFIX)

    # SMS / Text Hub router - SMS messaging (staff endpoints)
    from app.api.routes import sms
    app.include_router(sms.router, prefix=settings.API_PREFIX)

    # Reports & Dashboards router - analytics and reporting (staff endpoints)
    from app.api.routes import reports
    app.include_router(reports.router, prefix=settings.API_PREFIX)

    # Payments & Deposits router - payment processing (staff endpoints)
    from app.api.routes import payments
    app.include_router(payments.router, prefix=settings.API_PREFIX)

    # Formula Engine router - formula testing and validation (staff endpoints)
    from app.api.routes import formulas
    app.include_router(formulas.router, prefix=settings.API_PREFIX)

    # Consent & Compliance router - GDPR, consent tracking (staff endpoints)
    from app.api.routes import consent
    app.include_router(consent.router, prefix=settings.API_PREFIX)

    # Governance router - AI governance (change_log, task_logs, audit_issues) (staff endpoints)
    from app.api.routes import governance
    app.include_router(governance.router, prefix=settings.API_PREFIX)

    # RAG router - Retrieval Augmented Generation (context retrieval, embeddings, AI chain) (staff endpoints)
    from app.api.routes import rag
    app.include_router(rag.router, prefix=settings.API_PREFIX)

    # Prompts router - Prompt library with versioning, validation, and self-healing (staff endpoints)
    from app.api.routes import prompts
    app.include_router(prompts.router, prefix=settings.API_PREFIX)

    # AI Jobs router - Manual trigger endpoints for AI automation jobs (staff endpoints)
    from app.api.routes import ai_jobs
    app.include_router(ai_jobs.router, prefix=settings.API_PREFIX)

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
