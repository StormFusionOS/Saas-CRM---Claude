"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API Configuration.

Loads settings from environment variables with sensible defaults.
"""

import os
from typing import List


class Settings:
    """Application settings loaded from environment."""

    # Application
    APP_NAME: str = "CRM API"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("CRM_API_DEBUG", "true").lower() == "true"
    API_PREFIX: str = os.getenv("CRM_API_PREFIX", "/api/v1")

    # Server
    HOST: str = os.getenv("CRM_API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("CRM_API_PORT", "8000"))

    # Security
    SECRET_KEY: str = os.getenv(
        "CRM_SECRET_KEY",
        "crm-dev-secret-key-change-in-production-min-32-chars"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(
        os.getenv("CRM_ACCESS_TOKEN_EXPIRE", "900")
    )  # 15 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = int(
        os.getenv("CRM_REFRESH_TOKEN_EXPIRE", "604800")
    )  # 7 days

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CRM_CORS_ORIGINS",
        "http://localhost:5173,https://crm.example.com"
    ).split(",")

    # Database
    DB_HOST: str = os.getenv("CRM_DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("CRM_DB_PORT", "5433"))
    DB_NAME: str = os.getenv("CRM_DB_NAME", "crm")
    DB_USER: str = os.getenv("CRM_DB_USER", "crm_user")
    DB_PASSWORD: str = os.getenv("CRM_DB_PASSWORD", "crm_password")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Webhook secrets
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    FB_APP_SECRET: str = os.getenv("FB_APP_SECRET", "")
    FB_VERIFY_TOKEN: str = os.getenv("FB_VERIFY_TOKEN", "")
    GOOGLE_WEBHOOK_SECRET: str = os.getenv("GOOGLE_WEBHOOK_SECRET", "")

    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@example.com")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "false").lower() == "true"

    # Scrape Bot Configuration
    SCRAPE_BOT_BASE_URL: str = os.getenv("SCRAPE_BOT_BASE_URL", "https://scrape-runner.internal:8443")
    SCRAPE_BOT_API_KEY: str = os.getenv("SCRAPE_BOT_API_KEY", "")
    SCRAPE_BOT_TIMEOUT: int = int(os.getenv("SCRAPE_BOT_TIMEOUT", "30"))
    SCRAPE_BOT_VERIFY_TLS: bool = os.getenv("SCRAPE_BOT_VERIFY_TLS", "true").lower() == "true"
    SCRAPE_BOT_MTLS_CERT_PATH: str = os.getenv("SCRAPE_BOT_MTLS_CERT_PATH", "")
    SCRAPE_BOT_MTLS_KEY_PATH: str = os.getenv("SCRAPE_BOT_MTLS_KEY_PATH", "")
    SCRAPE_BOT_CA_BUNDLE_PATH: str = os.getenv("SCRAPE_BOT_CA_BUNDLE_PATH", "")

    # Feature flags
    AUTO_REPLY_ENABLED: bool = os.getenv("AUTO_REPLY_ENABLED", "false").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")


# Global settings instance
settings = Settings()
