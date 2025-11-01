"""Ops API Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
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

    return app


app = create_app()


if __name__ == "__main__":
    print(f"✓ {settings.APP_NAME} v{settings.VERSION} initialized")
    print(f"Note: Run with uvicorn app.main:app --host {settings.HOST} --port {settings.PORT}")
