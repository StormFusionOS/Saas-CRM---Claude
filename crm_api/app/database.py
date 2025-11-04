"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

SQLAlchemy Database Session Management.

Provides database session dependency for FastAPI routes with proper
connection pooling, error handling, and cleanup.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import structlog

from app.core.config import settings
from app.db_models import Base

logger = structlog.get_logger(__name__)


# Create SQLAlchemy engine
# pool_pre_ping=True ensures stale connections are recycled
# pool_size and max_overflow from settings for connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,  # Log SQL statements in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Event listener for connection checkout (optional logging)
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections in debug mode."""
    if settings.DEBUG:
        logger.debug("database_connection_established")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session.

    Usage in routes:
        @router.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Use db session here
            results = db.query(Model).all()
            return results

    The session is automatically closed after the request completes,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("database_session_error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.

    This should only be called during development or initial setup.
    In production, use Alembic migrations instead.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def dispose_engine():
    """
    Dispose of the engine's connection pool.

    Call this during application shutdown to cleanly close all connections.
    """
    logger.info("Disposing database engine...")
    engine.dispose()
    logger.info("Database engine disposed")


__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "dispose_engine",
]
