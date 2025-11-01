"""
Ops API Configuration.

Loads settings from environment variables with sensible defaults.
"""

import os
from typing import List


class Settings:
    """Application settings loaded from environment."""

    # Application
    APP_NAME: str = "Ops API"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("OPS_API_DEBUG", "true").lower() == "true"
    API_PREFIX: str = os.getenv("OPS_API_PREFIX", "/api/v1")

    # Server
    HOST: str = os.getenv("OPS_API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("OPS_API_PORT", "8001"))

    # Security
    SECRET_KEY: str = os.getenv(
        "OPS_SECRET_KEY",
        "ops-dev-secret-key-change-in-production-min-32-chars"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(
        os.getenv("OPS_ACCESS_TOKEN_EXPIRE", "900")
    )
    REFRESH_TOKEN_EXPIRE_SECONDS: int = int(
        os.getenv("OPS_REFRESH_TOKEN_EXPIRE", "604800")
    )

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "OPS_CORS_ORIGINS",
        "http://localhost:5174,https://ops.example.com"
    ).split(",")

    # Database
    DB_HOST: str = os.getenv("OPS_DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("OPS_DB_PORT", "5434"))
    DB_NAME: str = os.getenv("OPS_DB_NAME", "ops")
    DB_USER: str = os.getenv("OPS_DB_USER", "ops_user")
    DB_PASSWORD: str = os.getenv("OPS_DB_PASSWORD", "ops_password")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis / Celery
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    @property
    def CELERY_BROKER_URL(self) -> str:
        """Construct Celery broker URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Construct Celery result backend URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # AI / ML Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1000"))

    # Feature Flags
    AI_SUGGESTIONS_ENABLED: bool = os.getenv("AI_SUGGESTIONS_ENABLED", "false").lower() == "true"
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    # Security / File Integrity
    FILE_INTEGRITY_PATHS: List[str] = os.getenv(
        "FILE_INTEGRITY_PATHS",
        "/etc/nginx,/var/www"
    ).split(",")

    # Backup Configuration
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    BACKUP_SCHEDULE: str = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")


# Global settings instance
settings = Settings()
