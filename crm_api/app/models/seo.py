"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

SEO Data Models

Models for SERP tracking, backlinks, keywords, page metrics, and content clusters.
These models support AI-powered SEO automation and optimization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


# ==============================================================================
# Enums
# ==============================================================================

class KeywordDifficulty(str, Enum):
    """Keyword competition difficulty."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class SearchIntent(str, Enum):
    """User search intent classification."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


class BacklinkStatus(str, Enum):
    """Backlink status."""
    ACTIVE = "active"
    LOST = "lost"
    BROKEN = "broken"
    NOFOLLOW = "nofollow"


class PageHealthStatus(str, Enum):
    """Page health status."""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


# ==============================================================================
# Keywords & SERP Tracking
# ==============================================================================

class Keyword(BaseModel):
    """
    A tracked keyword/search query.

    Used for rank tracking, search volume monitoring, and opportunity detection.
    """
    id: int
    keyword_text: str = Field(..., description="The search query")
    search_volume: Optional[int] = Field(None, description="Monthly search volume")
    difficulty: Optional[str] = Field(None, description="Ranking difficulty")
    intent: Optional[str] = Field(None, description="Search intent classification")

    # Targeting
    target_domain: str = Field(..., description="Domain we're tracking for")
    target_page: Optional[str] = Field(None, description="Specific page to rank for")
    target_rank: Optional[int] = Field(None, description="Goal rank position")

    # Current Performance
    current_rank: Optional[int] = Field(None, description="Latest rank position")
    previous_rank: Optional[int] = Field(None, description="Rank from last check")
    best_rank: Optional[int] = Field(None, description="Best rank ever achieved")
    worst_rank: Optional[int] = Field(None, description="Worst rank in tracking period")

    # Metrics
    ctr: Optional[float] = Field(None, description="Click-through rate (0.0-1.0)")
    impressions: Optional[int] = Field(None, description="Monthly impressions")
    clicks: Optional[int] = Field(None, description="Monthly clicks")

    # Tracking
    first_tracked_at: datetime = Field(default_factory=datetime.now)
    last_checked_at: Optional[datetime] = None
    is_active: bool = Field(default=True, description="Still tracking this keyword")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SERPSnapshot(BaseModel):
    """
    A SERP (Search Engine Results Page) snapshot at a point in time.

    Captures the top results for a keyword to detect rank changes and analyze competitors.
    """
    id: int
    keyword_id: int
    captured_at: datetime = Field(default_factory=datetime.now)

    # SERP Features
    has_featured_snippet: bool = Field(default=False)
    has_knowledge_panel: bool = Field(default=False)
    has_local_pack: bool = Field(default=False)
    has_people_also_ask: bool = Field(default=False)
    has_related_searches: bool = Field(default=False)

    # Results
    results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top 100 organic results with url, title, description, rank"
    )

    # Our Position
    our_rank: Optional[int] = Field(None, description="Our ranking in this snapshot")
    our_url: Optional[str] = Field(None, description="Our URL that ranked")

    # Metadata
    search_engine: str = Field(default="google", description="google, bing, etc.")
    location: Optional[str] = Field(None, description="Geographic location")
    device: str = Field(default="desktop", description="desktop or mobile")
    created_at: datetime = Field(default_factory=datetime.now)


class RankChange(BaseModel):
    """
    A detected rank change (anomaly or significant movement).

    Generated automatically when rank changes significantly.
    """
    id: int
    keyword_id: int

    # Change Details
    previous_rank: int
    new_rank: int
    rank_change: int = Field(..., description="Positive for improvement, negative for drop")

    # Significance
    is_significant: bool = Field(default=False, description="Movement >5 positions")
    is_anomaly: bool = Field(default=False, description="Unusual/unexpected change")

    # Timing
    detected_at: datetime = Field(default_factory=datetime.now)
    change_occurred_between: Optional[str] = Field(
        None,
        description="Time range when change occurred"
    )

    # Analysis
    possible_causes: List[str] = Field(
        default_factory=list,
        description="AI-detected possible reasons"
    )
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation")

    # Action
    suggested_action: Optional[str] = Field(None)
    change_log_id: Optional[int] = Field(None, description="Link to AI suggestion")

    created_at: datetime = Field(default_factory=datetime.now)


# ==============================================================================
# Backlinks & Citations
# ==============================================================================

class Backlink(BaseModel):
    """
    An inbound link from another domain.

    Tracked for SEO value and link building opportunities.
    """
    id: int

    # Link Details
    source_url: str = Field(..., description="URL linking to us")
    source_domain: str = Field(..., description="Domain linking to us")
    target_url: str = Field(..., description="Our URL being linked to")
    anchor_text: Optional[str] = Field(None, description="Link text")

    # Link Attributes
    is_dofollow: bool = Field(default=True)
    is_sponsored: bool = Field(default=False)
    is_ugc: bool = Field(default=False)

    # SEO Metrics
    source_domain_authority: Optional[int] = Field(None, description="DA 0-100")
    source_page_authority: Optional[int] = Field(None, description="PA 0-100")
    source_spam_score: Optional[int] = Field(None, description="Spam score 0-100")

    # Status
    status: str = Field(default="active", description="active/lost/broken")
    first_seen_at: datetime = Field(default_factory=datetime.now)
    last_seen_at: datetime = Field(default_factory=datetime.now)
    lost_at: Optional[datetime] = None

    # Discovery
    discovered_by: Optional[str] = Field(None, description="How we found it")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Citation(BaseModel):
    """
    A mention of our brand/domain (may or may not include a link).

    Used for brand monitoring and link building opportunities.
    """
    id: int

    # Citation Details
    source_url: str
    source_domain: str
    citation_text: str = Field(..., description="Text mentioning our brand")
    context: Optional[str] = Field(None, description="Surrounding text")

    # Link Status
    has_link: bool = Field(default=False)
    backlink_id: Optional[int] = Field(None, description="Link to Backlink if linked")

    # Sentiment
    sentiment: Optional[str] = Field(None, description="positive/neutral/negative")
    sentiment_score: Optional[float] = Field(None, description="-1.0 to 1.0")

    # Opportunity
    is_link_opportunity: bool = Field(default=False)
    outreach_status: Optional[str] = Field(None, description="pending/contacted/success/failed")

    # Timing
    published_at: Optional[datetime] = None
    discovered_at: datetime = Field(default_factory=datetime.now)

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==============================================================================
# Page Metrics & Performance
# ==============================================================================

class PageMetrics(BaseModel):
    """
    Performance metrics for a specific page/URL.

    Aggregates data from Google Search Console, Analytics, and crawlers.
    """
    id: int
    url: str = Field(..., description="Page URL")
    domain: str = Field(..., description="Domain")
    page_path: str = Field(..., description="Path portion of URL")

    # Content
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: Optional[str] = None
    word_count: Optional[int] = None

    # Rankings
    keywords_ranking: int = Field(default=0, description="Number of keywords this page ranks for")
    avg_rank: Optional[float] = Field(None, description="Average rank across all keywords")
    best_rank: Optional[int] = Field(None, description="Best rank for any keyword")

    # Traffic (30 day)
    impressions_30d: Optional[int] = Field(0)
    clicks_30d: Optional[int] = Field(0)
    ctr_30d: Optional[float] = Field(None, description="Click-through rate")
    position_30d: Optional[float] = Field(None, description="Avg position in search")

    # Engagement
    pageviews_30d: Optional[int] = Field(0)
    avg_time_on_page: Optional[float] = Field(None, description="Seconds")
    bounce_rate: Optional[float] = Field(None, description="0.0-1.0")

    # Technical SEO
    load_time_ms: Optional[int] = Field(None)
    core_web_vitals_score: Optional[int] = Field(None, description="0-100")
    mobile_friendly: bool = Field(default=True)
    has_schema_markup: bool = Field(default=False)
    schema_types: List[str] = Field(default_factory=list)

    # Backlinks
    backlink_count: int = Field(default=0)
    referring_domains: int = Field(default=0)

    # Health
    health_status: str = Field(default="good")
    health_issues: List[str] = Field(default_factory=list)

    # Indexing
    is_indexed: bool = Field(default=False)
    index_status: Optional[str] = Field(None)
    canonical_url: Optional[str] = Field(None)

    # Timestamps
    last_crawled_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    metrics_date: date = Field(default_factory=date.today)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==============================================================================
# Content Clusters & Internal Linking
# ==============================================================================

class ContentCluster(BaseModel):
    """
    A topical content cluster (pillar + supporting pages).

    Used for content strategy and internal linking recommendations.
    """
    id: int
    cluster_name: str = Field(..., description="Cluster topic/theme")

    # Pillar Page
    pillar_page_url: Optional[str] = Field(None, description="Main hub page")
    pillar_page_id: Optional[int] = Field(None, description="Link to PageMetrics")

    # Supporting Pages
    supporting_pages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of {url, page_id, relevance_score}"
    )

    # Keywords
    target_keywords: List[str] = Field(default_factory=list)
    keyword_ids: List[int] = Field(default_factory=list)

    # Performance
    total_traffic_30d: Optional[int] = Field(0)
    total_keywords_ranking: int = Field(default=0)
    avg_cluster_rank: Optional[float] = None

    # Internal Linking
    internal_link_count: int = Field(default=0, description="Links within cluster")
    internal_link_density: Optional[float] = Field(None, description="0.0-1.0")

    # Status
    is_complete: bool = Field(default=False)
    completion_percentage: Optional[float] = Field(None)

    # AI Suggestions
    ai_suggestions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="AI-generated content and linking suggestions"
    )

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class InternalLinkSuggestion(BaseModel):
    """
    AI-generated internal linking suggestion.

    Recommends adding a link from one page to another for SEO benefit.
    """
    id: int

    # Link Details
    source_url: str = Field(..., description="Page to add link from")
    target_url: str = Field(..., description="Page to link to")
    suggested_anchor_text: str = Field(..., description="Recommended link text")
    suggested_placement: Optional[str] = Field(None, description="Where to place link")

    # Context
    context_text: Optional[str] = Field(None, description="Surrounding text")
    relevance_score: float = Field(..., description="0.0-1.0 relevance")

    # SEO Benefit
    estimated_seo_impact: str = Field(..., description="low/medium/high")
    target_keyword: Optional[str] = Field(None)
    cluster_id: Optional[int] = Field(None)

    # Status
    status: str = Field(default="pending", description="pending/approved/rejected/implemented")
    change_log_id: Optional[int] = Field(None, description="Link to governance change_log")

    # AI Details
    ai_confidence: float = Field(..., description="0.0-1.0")
    ai_reasoning: Optional[str] = Field(None)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==============================================================================
# Schema Markup
# ==============================================================================

class SchemaMarkup(BaseModel):
    """
    JSON-LD schema markup for a page.

    Tracks existing and AI-generated schema for rich results.
    """
    id: int
    page_url: str
    page_id: Optional[int] = Field(None, description="Link to PageMetrics")

    # Schema Details
    schema_type: str = Field(..., description="Article, Product, FAQPage, HowTo, etc.")
    schema_json: Dict[str, Any] = Field(..., description="The JSON-LD markup")

    # Status
    is_live: bool = Field(default=False, description="Deployed to production")
    is_ai_generated: bool = Field(default=False)

    # Validation
    is_valid: bool = Field(default=True)
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)

    # Performance
    rich_result_eligible: bool = Field(default=False)
    rich_result_type: Optional[str] = Field(None)

    # Governance
    change_log_id: Optional[int] = Field(None, description="If AI-generated, link to change_log")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==============================================================================
# In-Memory Storage (will be replaced with PostgreSQL)
# ==============================================================================

keywords: List[Keyword] = []
serp_snapshots: List[SERPSnapshot] = []
rank_changes: List[RankChange] = []
backlinks: List[Backlink] = []
citations: List[Citation] = []
page_metrics: List[PageMetrics] = []
content_clusters: List[ContentCluster] = []
internal_link_suggestions: List[InternalLinkSuggestion] = []
schema_markups: List[SchemaMarkup] = []

# Counters
_keyword_id_counter = 1
_serp_snapshot_id_counter = 1
_rank_change_id_counter = 1
_backlink_id_counter = 1
_citation_id_counter = 1
_page_metrics_id_counter = 1
_content_cluster_id_counter = 1
_internal_link_suggestion_id_counter = 1
_schema_markup_id_counter = 1
