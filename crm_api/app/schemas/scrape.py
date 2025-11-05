"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Scrape Suite Pydantic Schemas

Request/response models for Scrape Suite API endpoints.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ==============================================================================
# Job Management
# ==============================================================================

class JobTriggerRequest(BaseModel):
    """Request to manually trigger a scrape job."""

    type: str = Field(..., description="Job type: serp, crawl, backlinks, citations")
    payload: Dict[str, Any] = Field(..., description="Job-specific payload")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "serp",
                "payload": {
                    "queries": ["pressure washing near me"],
                    "location": "US"
                }
            }
        }


class JobStatusResponse(BaseModel):
    """Job status with task log info."""

    job_id: str
    task_id: Optional[str] = None
    status: str = Field(..., description="Status: queued, running, completed, failed")
    task_name: Optional[str] = None
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    items_processed: int = 0
    items_succeeded: int = 0
    items_failed: int = 0
    error_message: Optional[str] = None
    output_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ==============================================================================
# Keywords
# ==============================================================================

class KeywordCreate(BaseModel):
    """Request to create a new keyword."""

    keyword_text: str = Field(..., min_length=1, max_length=500)
    target_domain: str = Field(..., max_length=255)
    target_page: Optional[str] = Field(None, max_length=2000)
    intent: Optional[str] = Field(None, max_length=50)
    search_volume: Optional[int] = None
    difficulty: Optional[int] = Field(None, ge=0, le=100)
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "keyword_text": "pressure washing services",
                "target_domain": "rivercityclean.com",
                "target_page": "https://rivercityclean.com/services/pressure-washing",
                "intent": "commercial",
                "search_volume": 1000,
                "difficulty": 45,
                "is_active": True
            }
        }


class KeywordUpdate(BaseModel):
    """Request to update keyword fields."""

    keyword_text: Optional[str] = Field(None, min_length=1, max_length=500)
    target_domain: Optional[str] = Field(None, max_length=255)
    target_page: Optional[str] = Field(None, max_length=2000)
    intent: Optional[str] = Field(None, max_length=50)
    search_volume: Optional[int] = None
    difficulty: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class KeywordResponse(BaseModel):
    """Keyword with performance metrics."""

    id: int
    keyword_text: str
    target_domain: str
    target_page: Optional[str] = None
    search_volume: Optional[int] = None
    difficulty: Optional[int] = None
    intent: Optional[str] = None
    current_rank: Optional[int] = None
    previous_rank: Optional[int] = None
    best_rank: Optional[int] = None
    worst_rank: Optional[int] = None
    ctr: Optional[float] = None
    impressions: int = 0
    clicks: int = 0
    is_active: bool = True
    last_checked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KeywordListResponse(BaseModel):
    """Paginated list of keywords."""

    keywords: List[KeywordResponse]
    total: int
    page: int
    page_size: int


# ==============================================================================
# Competitors
# ==============================================================================

class CompetitorCreate(BaseModel):
    """Request to create a new competitor."""
    domain: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    priority: str = Field(default='medium', pattern='^(low|medium|high|critical)$')
    is_active: bool = True


class CompetitorUpdate(BaseModel):
    """Request to update competitor fields."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = Field(None, pattern='^(low|medium|high|critical)$')
    is_active: Optional[bool] = None


class CompetitorResponse(BaseModel):
    """Competitor details."""
    id: int
    domain: str
    name: str
    category: Optional[str] = None
    priority: str
    is_active: bool
    last_scraped: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompetitorListResponse(BaseModel):
    """Paginated list of competitors."""
    competitors: List[CompetitorResponse]
    total: int
    page: int
    page_size: int


# ==============================================================================
# SERP Snapshots & Results
# ==============================================================================

class SerpSnapshotResponse(BaseModel):
    """SERP snapshot for a keyword."""

    id: int
    keyword_id: int
    search_date: datetime
    rank: Optional[int] = None
    url: Optional[str] = None
    featured_snippet: bool = False
    people_also_ask: bool = False
    local_pack: bool = False
    knowledge_panel: bool = False
    serp_features: List[str] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SerpResultResponse(BaseModel):
    """Individual SERP result."""

    id: int
    snapshot_id: int
    rank: int
    url: str
    domain: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    is_ours: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SerpSnapshotListResponse(BaseModel):
    """Paginated list of SERP snapshots."""

    snapshots: List[SerpSnapshotResponse]
    total: int
    page: int
    page_size: int


class SerpResultListResponse(BaseModel):
    """List of SERP results for a snapshot."""

    results: List[SerpResultResponse]
    snapshot_id: int
    total: int


# ==============================================================================
# Competitors
# ==============================================================================

class CompetitorResponse(BaseModel):
    """Competitor site info."""

    id: int
    domain: str
    name: str
    category: Optional[str] = None
    priority: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_scraped: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompetitorListResponse(BaseModel):
    """List of competitors."""

    competitors: List[CompetitorResponse]
    total: int


class CompetitorPageResponse(BaseModel):
    """Competitor page with snapshot info."""

    id: int
    site_id: int
    url: str
    title: Optional[str] = None
    page_type: Optional[str] = None
    content_hash: Optional[str] = None
    status_code: Optional[int] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    is_changed: bool = False  # Computed field

    class Config:
        from_attributes = True


class CompetitorPageListResponse(BaseModel):
    """Paginated list of competitor pages."""

    pages: List[CompetitorPageResponse]
    total: int
    page: int
    page_size: int


# ==============================================================================
# Backlinks
# ==============================================================================

class BacklinkResponse(BaseModel):
    """Backlink info."""

    id: int
    source_url: str
    source_domain: str
    target_url: str
    anchor_text: Optional[str] = None
    is_dofollow: bool = False
    is_inbody: bool = False
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    is_lost: bool = False

    class Config:
        from_attributes = True


class ReferringDomainResponse(BaseModel):
    """Referring domain aggregate."""

    id: int
    domain: str
    backlink_count: int = 0
    inbody_link_count: int = 0
    authority_score: Optional[int] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class BacklinkListResponse(BaseModel):
    """Paginated list of backlinks."""

    backlinks: List[BacklinkResponse]
    total: int
    page: int
    page_size: int


class ReferringDomainListResponse(BaseModel):
    """List of referring domains."""

    domains: List[ReferringDomainResponse]
    total: int


# ==============================================================================
# Citations
# ==============================================================================

class CitationResponse(BaseModel):
    """Business citation."""

    id: int
    platform: str
    listing_url: Optional[str] = None
    is_listed: bool = False
    name_found: Optional[str] = None
    address_found: Optional[str] = None
    phone_found: Optional[str] = None
    nap_match: bool = False
    first_checked: Optional[datetime] = None
    last_checked: Optional[datetime] = None

    class Config:
        from_attributes = True


class CitationListResponse(BaseModel):
    """List of citations."""

    citations: List[CitationResponse]
    total: int


# ==============================================================================
# Page Audits
# ==============================================================================

class PageAuditIssueResponse(BaseModel):
    """Individual audit issue."""

    id: int
    audit_id: int
    type: str
    description: Optional[str] = None
    severity: str
    fixed: bool = False
    fixed_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PageAuditResponse(BaseModel):
    """Page audit with issues."""

    id: int
    page_url: str
    audit_date: datetime
    status_code: Optional[int] = None
    performance_proxy: Optional[Dict[str, Any]] = None
    issues_found: int = 0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    issues: List[PageAuditIssueResponse] = []

    class Config:
        from_attributes = True


class PageAuditListResponse(BaseModel):
    """Paginated list of page audits."""

    audits: List[PageAuditResponse]
    total: int
    page: int
    page_size: int


# ==============================================================================
# Settings
# ==============================================================================

class ScrapeSettingsResponse(BaseModel):
    """Scrape Suite settings."""

    review_mode: bool = Field(
        default=False,
        description="If true, require manual approval before publishing changes"
    )
    daily_serp_enabled: bool = True
    weekly_crawl_enabled: bool = True
    monthly_crawl_enabled: bool = True
    backlinks_refresh_days: int = 7
    citations_refresh_days: int = 30
    max_pages_per_crawl: int = 100
    proxy_pool_enabled: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "review_mode": False,
                "daily_serp_enabled": True,
                "weekly_crawl_enabled": True,
                "monthly_crawl_enabled": True,
                "backlinks_refresh_days": 7,
                "citations_refresh_days": 30,
                "max_pages_per_crawl": 100,
                "proxy_pool_enabled": False
            }
        }


class ScrapeSettingsUpdate(BaseModel):
    """Update scrape settings."""

    review_mode: Optional[bool] = None
    daily_serp_enabled: Optional[bool] = None
    weekly_crawl_enabled: Optional[bool] = None
    monthly_crawl_enabled: Optional[bool] = None
    backlinks_refresh_days: Optional[int] = None
    citations_refresh_days: Optional[int] = None
    max_pages_per_crawl: Optional[int] = None
    proxy_pool_enabled: Optional[bool] = None


# ==============================================================================
# Dashboard/Stats
# ==============================================================================

class ScrapeSuiteDashboardResponse(BaseModel):
    """Dashboard stats for Scrape Suite."""

    serp_snapshots_count: int = 0
    competitors_tracked: int = 0
    pages_monitored: int = 0
    backlinks_count: int = 0
    citations_count: int = 0
    recent_changes: int = 0
    pending_reviews: int = 0
    last_serp_snapshot: Optional[datetime] = None
    last_competitor_crawl: Optional[datetime] = None
    last_backlinks_refresh: Optional[datetime] = None
