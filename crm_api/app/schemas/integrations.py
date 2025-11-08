"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Integration Settings Schemas
Pydantic models for admin integration configuration (AI Node, etc.)
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional
from datetime import datetime


class AINodeConfigRequest(BaseModel):
    """Request to update AI Node configuration"""
    base_url: HttpUrl = Field(..., description="Base URL of AI Node service")
    bearer_token: Optional[str] = Field(None, description="Bearer token for authentication (encrypted at rest)")
    review_mode: bool = Field(True, description="Whether to require human review for AI suggestions")

    @validator('bearer_token')
    def validate_bearer_token(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 10:
                raise ValueError("Bearer token must be at least 10 characters")
            if len(v) > 500:
                raise ValueError("Bearer token too long (max 500 characters)")
        return v

    @validator('base_url')
    def validate_base_url(cls, v):
        """Ensure base URL is properly formatted"""
        url_str = str(v)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        # Remove trailing slash for consistency
        return url_str.rstrip('/')

    class Config:
        schema_extra = {
            "example": {
                "base_url": "https://ai-node.example.com",
                "bearer_token": "sk_live_abc123...",
                "review_mode": True
            }
        }


class AINodeConfigResponse(BaseModel):
    """Response for AI Node configuration (secrets masked)"""
    base_url: str = Field(..., description="Base URL of AI Node service")
    bearer_token_set: bool = Field(..., description="Whether bearer token is configured (never echo actual token)")
    review_mode: bool = Field(..., description="Whether review mode is enabled")
    last_updated: Optional[datetime] = Field(None, description="Last configuration update timestamp")
    last_ping_status: Optional[str] = Field(None, description="Status of last ping test")
    last_ping_latency_ms: Optional[int] = Field(None, description="Latency of last ping test in milliseconds")

    class Config:
        schema_extra = {
            "example": {
                "base_url": "https://ai-node.example.com",
                "bearer_token_set": True,
                "review_mode": True,
                "last_updated": "2025-11-06T12:00:00Z",
                "last_ping_status": "success",
                "last_ping_latency_ms": 127
            }
        }


class AINodePingResponse(BaseModel):
    """Response from AI Node ping test"""
    success: bool = Field(..., description="Whether ping was successful")
    status_code: Optional[int] = Field(None, description="HTTP status code from ping")
    latency_ms: Optional[int] = Field(None, description="Round-trip latency in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if ping failed")
    timestamp: datetime = Field(..., description="When ping was performed")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "latency_ms": 127,
                "error_message": None,
                "timestamp": "2025-11-06T12:00:00Z"
            }
        }


# ============================================================================
# AI Node Client Request/Response Schemas
# ============================================================================


class CtrTestIn(BaseModel):
    """Request to trigger CTR (Click-Through Rate) test on AI Node"""
    page_url: str = Field(..., description="URL of the page to test")
    variant_count: int = Field(3, ge=1, le=10, description="Number of variants to generate")
    test_duration_hours: int = Field(24, ge=1, le=168, description="Test duration in hours")
    metadata: Optional[dict] = Field(None, description="Additional metadata for the test")

    class Config:
        schema_extra = {
            "example": {
                "page_url": "https://example.com/landing-page",
                "variant_count": 3,
                "test_duration_hours": 48,
                "metadata": {"campaign": "summer-2025"}
            }
        }


class ContentRefreshIn(BaseModel):
    """Request to trigger content refresh on AI Node"""
    content_type: str = Field(..., description="Type of content to refresh (e.g., 'blog_post', 'product_description')")
    content_id: int = Field(..., description="ID of the content to refresh")
    refresh_strategy: str = Field("incremental", description="Refresh strategy: 'incremental' or 'full'")
    metadata: Optional[dict] = Field(None, description="Additional metadata for the refresh")

    @validator('refresh_strategy')
    def validate_strategy(cls, v):
        allowed = ['incremental', 'full']
        if v not in allowed:
            raise ValueError(f"refresh_strategy must be one of {allowed}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "content_type": "blog_post",
                "content_id": 42,
                "refresh_strategy": "incremental",
                "metadata": {"section": "marketing"}
            }
        }


class JobAck202(BaseModel):
    """202 Accepted response with correlation ID for async job tracking"""
    job_id: str = Field(..., description="Unique job ID for tracking")
    correlation_id: str = Field(..., description="Correlation ID for request tracing")
    status: str = Field("accepted", description="Job status")
    message: str = Field(..., description="Human-readable status message")
    estimated_completion_seconds: Optional[int] = Field(None, description="Estimated time to completion")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "correlation_id": "corr_xyz789",
                "status": "accepted",
                "message": "CTR test job queued successfully",
                "estimated_completion_seconds": 300
            }
        }


class ApplyResult(BaseModel):
    """Result of applying a change via AI Node"""
    change_id: int = Field(..., description="ID of the change that was applied")
    success: bool = Field(..., description="Whether the change was applied successfully")
    applied_at: datetime = Field(..., description="Timestamp when change was applied")
    message: str = Field(..., description="Result message")
    details: Optional[dict] = Field(None, description="Additional details about the application")
    errors: Optional[list] = Field(None, description="List of errors if application failed")

    class Config:
        schema_extra = {
            "example": {
                "change_id": 123,
                "success": True,
                "applied_at": "2025-11-06T12:00:00Z",
                "message": "Change applied successfully",
                "details": {"modified_fields": ["title", "description"]},
                "errors": None
            }
        }


# ============================================================================
# Health Check Schemas
# ============================================================================


class HealthCheckItem(BaseModel):
    """Individual health check result"""
    status: str = Field(..., description="Status: 'healthy', 'degraded', or 'unhealthy'")
    message: str = Field(..., description="Human-readable status message")
    details: Optional[dict] = Field(None, description="Additional details about the check")
    checked_at: datetime = Field(..., description="When the check was performed")

    @validator('status')
    def validate_status(cls, v):
        allowed = ['healthy', 'degraded', 'unhealthy']
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class AINodeHealthResponse(BaseModel):
    """Comprehensive health check response for AI Node integration"""
    overall_status: str = Field(..., description="Overall system health: 'healthy', 'degraded', or 'unhealthy'")
    timestamp: datetime = Field(..., description="When health check was performed")

    # Individual checks
    database: HealthCheckItem = Field(..., description="Database connectivity check")
    task_logs: HealthCheckItem = Field(..., description="Task logs health check")
    ai_node: HealthCheckItem = Field(..., description="AI Node connectivity check")

    # Optional checks
    backups: Optional[HealthCheckItem] = Field(None, description="Backup freshness check (optional)")
    wordpress: Optional[HealthCheckItem] = Field(None, description="WordPress REST API check (optional)")

    # Summary metrics
    summary: dict = Field(..., description="Summary metrics and statistics")

    @validator('overall_status')
    def validate_overall_status(cls, v):
        allowed = ['healthy', 'degraded', 'unhealthy']
        if v not in allowed:
            raise ValueError(f"overall_status must be one of {allowed}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "overall_status": "healthy",
                "timestamp": "2025-11-06T12:00:00Z",
                "database": {
                    "status": "healthy",
                    "message": "Database connection successful",
                    "details": {"latency_ms": 5},
                    "checked_at": "2025-11-06T12:00:00Z"
                },
                "task_logs": {
                    "status": "healthy",
                    "message": "Task logs operational",
                    "details": {
                        "latest_entry_age_hours": 2,
                        "error_count_24h": 0,
                        "total_count_24h": 42
                    },
                    "checked_at": "2025-11-06T12:00:00Z"
                },
                "ai_node": {
                    "status": "healthy",
                    "message": "AI Node responding",
                    "details": {"latency_ms": 127},
                    "checked_at": "2025-11-06T12:00:00Z"
                },
                "backups": None,
                "wordpress": None,
                "summary": {
                    "healthy_checks": 3,
                    "degraded_checks": 0,
                    "unhealthy_checks": 0,
                    "total_checks": 3
                }
            }
        }
