"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API SQLAlchemy Models.

These models define the database schema for the CRM system,
including AI/SEO governance tables.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, JSON, ARRAY, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# ============================================================================
# CORE CRM MODELS
# ============================================================================

class UserModel(Base):
    """CRM users/team members."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    roles = Column(ARRAY(String(50)), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ContactModel(Base):
    """Customer/prospect contacts."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    company = Column(String(255))
    title = Column(String(100))
    tags = Column(ARRAY(String(50)))
    custom_fields = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_contacted_at = Column(DateTime)


class LeadModel(Base):
    """Sales leads."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    status = Column(String(50), default="NEW", index=True)
    source = Column(String(50), default="MANUAL")
    value = Column(Float)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    probability = Column(Integer, default=0)
    expected_close_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    won_at = Column(DateTime)
    lost_at = Column(DateTime)


class InteractionModel(Base):
    """Customer interactions/communications."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    interaction_type = Column(String(50), default="NOTE")
    direction = Column(String(20), default="INBOUND")
    subject = Column(String(500))
    body = Column(Text)
    interaction_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy reserved word
    created_at = Column(DateTime, server_default=func.now(), index=True)


class ServiceModel(Base):
    """Services offered."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    base_price = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    pricing_formula = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)
    extra_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved word
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class QuoteModel(Base):
    """Sales quotes/proposals."""

    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    quote_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="DRAFT", index=True)
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    valid_until = Column(DateTime)
    terms = Column(Text)
    notes = Column(Text)
    public_notes = Column(Text)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    sent_at = Column(DateTime)
    viewed_at = Column(DateTime)
    accepted_at = Column(DateTime)
    rejected_at = Column(DateTime)
    expired_at = Column(DateTime)
    extra_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved word
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now())


class QuoteItemModel(Base):
    """Line items in quotes."""

    __tablename__ = "quote_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    service_name = Column(String(255), nullable=False)
    description = Column(Text)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)
    discount_percent = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_percent = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    display_order = Column(Integer, default=0)
    extra_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved word
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# AI GOVERNANCE MODELS (Step 01 Implementation)
# ============================================================================

class ChangeStatus(str, enum.Enum):
    """State machine for AI-generated changes."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    REVERTED = "reverted"
    FAILED = "failed"


class ChangeLogModel(Base):
    """
    Central governance table for all AI-generated changes.
    Implements review-first workflow where all AI suggestions
    require human approval before execution.
    """

    __tablename__ = "change_log"

    change_id = Column(String(50), primary_key=True, index=True)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)

    # Change details
    old_value = Column(JSON)
    new_value = Column(JSON)
    reasoning = Column(Text)
    ai_confidence = Column(Float)
    evidence = Column(JSON)

    # State machine
    status = Column(SQLEnum(ChangeStatus), default=ChangeStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    executed_at = Column(DateTime)
    reverted_at = Column(DateTime)

    # Actor tracking
    approved_by = Column(Integer, ForeignKey("users.id"))
    rejected_by = Column(Integer, ForeignKey("users.id"))
    executed_by = Column(Integer, ForeignKey("users.id"))

    # Decision metadata
    decision_reason = Column(Text)
    execution_metadata = Column(JSON)
    revert_reason = Column(Text)

    # Auto-mode fields (Step 16)
    auto_approved = Column(Boolean, default=False)
    auto_reverted = Column(Boolean, default=False)
    revert_triggers = Column(JSON)
    rollback_check_status = Column(String(20), default="pending")
    rollback_checked_at = Column(DateTime)

    __table_args__ = (
        Index('idx_change_log_status_created', 'status', 'created_at'),
        Index('idx_change_log_module_status', 'module', 'status'),
        Index('idx_change_log_auto_monitoring', 'auto_approved', 'executed_at', 'status'),
    )


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    """Task execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskLogModel(Base):
    """
    Logs for all AI automation jobs/tasks.
    Tracks execution, performance, and errors.
    """

    __tablename__ = "task_logs"

    task_id = Column(String(50), primary_key=True)
    task_name = Column(String(100), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)

    # Execution metadata
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.QUEUED, nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    queued_at = Column(DateTime, server_default=func.now(), index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Performance metrics
    duration_seconds = Column(Float)
    items_processed = Column(Integer, default=0)
    items_succeeded = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)

    # Input/Output
    input_params = Column(JSON)
    output_summary = Column(JSON)

    # Error handling
    error_message = Column(Text)
    error_traceback = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Linked changes
    changes_generated = Column(Integer, default=0)
    change_ids = Column(ARRAY(String(50)))

    __table_args__ = (
        Index('idx_task_logs_status_queued', 'status', 'queued_at'),
        Index('idx_task_logs_module_status', 'module', 'status'),
    )


class IssueSeverity(str, enum.Enum):
    """Audit issue severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueStatus(str, enum.Enum):
    """Audit issue lifecycle status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class AuditIssueModel(Base):
    """
    Tracks data quality issues, validation failures,
    and system anomalies detected by AI automation.
    """

    __tablename__ = "audit_issues"

    issue_id = Column(String(50), primary_key=True)
    issue_type = Column(String(100), nullable=False, index=True)
    severity = Column(SQLEnum(IssueSeverity), nullable=False, index=True)
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.OPEN, index=True)

    # Issue details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    affected_entity_type = Column(String(50))
    affected_entity_id = Column(Integer)

    # Detection metadata
    detected_at = Column(DateTime, server_default=func.now(), index=True)
    detected_by_task_id = Column(String(50), ForeignKey("task_logs.task_id"))
    detection_metadata = Column(JSON)

    # Resolution
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolution_notes = Column(Text)
    resolution_action_taken = Column(Text)

    __table_args__ = (
        Index('idx_audit_issues_severity_status', 'severity', 'status'),
        Index('idx_audit_issues_detected', 'detected_at'),
    )


class OperatingMode(str, enum.Enum):
    """Module operating mode."""
    REVIEW = "review"  # Human approval required
    AUTO = "auto"      # Auto-execute high-confidence changes


class RolloutPhase(str, enum.Enum):
    """Gradual rollout phases."""
    REVIEW = "review"
    PILOT = "pilot"
    EXPAND = "expand"
    FULL = "full"


class AutomationModuleConfigModel(Base):
    """
    Configuration for AI automation modules.
    Controls review vs auto mode, confidence thresholds, and limits.
    """

    __tablename__ = "automation_module_config"

    module = Column(String(50), primary_key=True)
    operating_mode = Column(SQLEnum(OperatingMode), default=OperatingMode.REVIEW, nullable=False)
    enabled = Column(Boolean, default=True)

    # Confidence thresholds
    confidence_threshold_auto = Column(Float, default=0.85)
    confidence_threshold_review = Column(Float, default=0.60)

    # Daily limits
    daily_limit_pilot = Column(Integer, default=5)
    daily_limit_expand = Column(Integer, default=20)
    daily_limit_full = Column(Integer, default=50)
    current_phase = Column(SQLEnum(RolloutPhase), default=RolloutPhase.REVIEW)

    # Graduation tracking
    graduated_at = Column(DateTime)
    graduated_by = Column(Integer, ForeignKey("users.id"))
    last_downgraded_at = Column(DateTime)
    downgrade_reason = Column(Text)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ModuleGraduationAction(str, enum.Enum):
    """Module lifecycle actions."""
    GRADUATED = "graduated"
    DOWNGRADED = "downgraded"
    PHASE_ADVANCED = "phase_advanced"


class ModuleGraduationLogModel(Base):
    """
    Audit trail for module graduation/downgrade events.
    """

    __tablename__ = "module_graduation_log"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(50), nullable=False, index=True)
    action = Column(SQLEnum(ModuleGraduationAction), nullable=False)

    # State transition
    from_mode = Column(String(20))
    to_mode = Column(String(20))
    from_phase = Column(String(20))
    to_phase = Column(String(20))

    # Context
    performed_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    metrics_snapshot = Column(JSON)

    created_at = Column(DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        Index('idx_graduation_log_module_created', 'module', 'created_at'),
    )


# ============================================================================
# SEO DATA MODELS (Step 02 Implementation)
# ============================================================================

class PageModel(Base):
    """
    Comprehensive page metrics for SEO tracking.
    Extended from Step 01 placeholder with full metrics.
    """

    __tablename__ = "page_metrics"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2000), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)

    # Content
    title = Column(String(500))
    meta_description = Column(String(1000))
    h1 = Column(String(500))
    page_type = Column(String(50))  # blog, service, homepage, etc.
    content_hash = Column(String(64))
    word_count = Column(Integer)

    # Rankings
    keywords_ranking = Column(Integer, default=0)
    avg_rank = Column(Float)
    best_rank = Column(Integer)

    # Traffic (30-day metrics from GSC)
    impressions_30d = Column(Integer, default=0)
    clicks_30d = Column(Integer, default=0)
    ctr_30d = Column(Float)
    position_30d = Column(Float)

    # Engagement (from GA4)
    pageviews_30d = Column(Integer, default=0)
    avg_time_on_page = Column(Integer)  # seconds
    bounce_rate = Column(Float)

    # Technical
    load_time_ms = Column(Integer)
    core_web_vitals_score = Column(Integer)  # 0-100
    mobile_friendly = Column(Boolean)
    is_indexed = Column(Boolean, default=True)

    # Schema
    has_schema_markup = Column(Boolean, default=False)
    schema_types = Column(ARRAY(String(50)))  # ['FAQPage', 'Article', etc.]

    # Backlinks
    backlink_count = Column(Integer, default=0)
    referring_domains = Column(Integer, default=0)

    # Health
    health_status = Column(String(20), default='healthy')  # healthy, warning, error
    health_issues = Column(ARRAY(String(100)))

    # Timestamps
    last_crawled_at = Column(DateTime)
    require_manual_review = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_page_metrics_is_indexed', 'is_indexed'),
        Index('idx_page_metrics_health_status', 'health_status'),
    )


class KeywordModel(Base):
    """
    Keyword tracking with performance metrics.
    Extended from Step 01 placeholder.
    """

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword_text = Column(String(500), nullable=False, index=True)
    target_domain = Column(String(255), nullable=False, index=True)
    target_page = Column(String(2000))  # URL of target page

    # Search metrics
    search_volume = Column(Integer)
    difficulty = Column(Integer)  # 0-100
    intent = Column(String(50))  # informational, commercial, transactional, navigational

    # Current performance
    current_rank = Column(Integer, index=True)
    previous_rank = Column(Integer)
    best_rank = Column(Integer)
    worst_rank = Column(Integer)

    # GSC metrics
    ctr = Column(Float)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)

    # Tracking
    is_active = Column(Boolean, default=True, index=True)
    last_checked_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_keywords_target_domain_active', 'target_domain', 'is_active'),
    )


class SerpSnapshotModel(Base):
    """
    Daily SERP snapshots for keyword tracking.
    Partitioned by month for performance.
    """

    __tablename__ = "serp_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True)
    search_date = Column(DateTime, nullable=False, index=True)

    # Ranking
    rank = Column(Integer)
    url = Column(String(2000))

    # SERP features
    featured_snippet = Column(Boolean, default=False)
    people_also_ask = Column(Boolean, default=False)
    local_pack = Column(Boolean, default=False)
    knowledge_panel = Column(Boolean, default=False)
    serp_features = Column(ARRAY(String(50)))

    # Metadata
    title = Column(String(500))
    description = Column(String(1000))

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_serp_snapshots_keyword_date', 'keyword_id', 'search_date'),
    )


class RankChangeModel(Base):
    """
    Significant rank changes requiring attention.
    Triggers anomaly detection (Step 08).
    """

    __tablename__ = "rank_changes"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True)

    # Change details
    previous_rank = Column(Integer, nullable=False)
    new_rank = Column(Integer, nullable=False)
    rank_delta = Column(Integer)  # positive = improved, negative = dropped

    # Significance
    is_significant = Column(Boolean, default=False, index=True)  # >= 5 positions
    severity = Column(String(20))  # minor, moderate, major, critical

    # Detection
    detected_at = Column(DateTime, server_default=func.now(), index=True)
    detection_method = Column(String(50))  # daily_scrape, manual, api

    # Metadata
    potential_causes = Column(ARRAY(String(100)))
    notes = Column(Text)

    __table_args__ = (
        Index('idx_rank_changes_significant', 'is_significant', 'detected_at'),
    )


class BacklinkModel(Base):
    """
    Backlink portfolio tracking for off-page SEO.
    """

    __tablename__ = "backlinks"

    id = Column(Integer, primary_key=True, index=True)

    # Source (linking page)
    source_url = Column(String(2000), nullable=False, index=True)
    source_domain = Column(String(255), nullable=False, index=True)
    source_domain_authority = Column(Integer)  # 0-100
    source_spam_score = Column(Integer)  # 0-100
    source_page_authority = Column(Integer)  # 0-100

    # Target (our page)
    target_url = Column(String(2000), nullable=False, index=True)
    target_page_id = Column(Integer, ForeignKey("page_metrics.id"))

    # Link attributes
    anchor_text = Column(String(500))
    is_dofollow = Column(Boolean, default=True)
    link_type = Column(String(50))  # text, image, redirect

    # Status
    status = Column(String(20), default='active', index=True)  # active, lost, broken
    first_seen_at = Column(DateTime, server_default=func.now())
    last_checked_at = Column(DateTime)
    lost_at = Column(DateTime)

    # Metadata
    context = Column(Text)  # surrounding text
    link_position = Column(String(50))  # header, body, footer, sidebar

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_backlinks_target_status', 'target_url', 'status'),
        Index('idx_backlinks_first_seen', 'first_seen_at'),
    )


class SchemaMarkupModel(Base):
    """
    JSON-LD schema markup tracking per page.
    """

    __tablename__ = "schema_markups"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("page_metrics.id"), nullable=False, index=True)

    # Schema details
    schema_type = Column(String(50), nullable=False)  # FAQPage, Article, Product, etc.
    schema_data = Column(JSON, nullable=False)

    # Status
    is_live = Column(Boolean, default=False)
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(ARRAY(String(500)))

    # Performance
    rich_result_earned = Column(Boolean, default=False)
    rich_result_type = Column(String(50))  # faq, howto, recipe, etc.

    # Timestamps
    deployed_at = Column(DateTime)
    last_validated_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_schema_markups_page_type', 'page_id', 'schema_type'),
        Index('idx_schema_markups_live', 'is_live'),
    )


class ContentClusterModel(Base):
    """
    Content topic clusters for internal linking (Step 10).
    """

    __tablename__ = "content_clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String(255), nullable=False)
    pillar_page_id = Column(Integer, ForeignKey("page_metrics.id"))

    # Cluster metrics
    page_count = Column(Integer, default=0)
    total_traffic = Column(Integer, default=0)
    avg_rank = Column(Float)

    # Analysis
    primary_topics = Column(ARRAY(String(100)))
    semantic_similarity_threshold = Column(Float, default=0.7)

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ClusterMembershipModel(Base):
    """
    Many-to-many relationship between pages and clusters.
    """

    __tablename__ = "cluster_memberships"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("content_clusters.id"), nullable=False, index=True)
    page_id = Column(Integer, ForeignKey("page_metrics.id"), nullable=False, index=True)

    # Membership strength
    relevance_score = Column(Float)  # 0.0-1.0
    is_pillar = Column(Boolean, default=False)

    added_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_cluster_memberships_cluster_page', 'cluster_id', 'page_id', unique=True),
    )


class InternalLinkSuggestionModel(Base):
    """
    AI-generated internal linking opportunities (Step 10).
    """

    __tablename__ = "internal_link_suggestions"

    id = Column(Integer, primary_key=True, index=True)

    # Link details
    source_page_id = Column(Integer, ForeignKey("page_metrics.id"), nullable=False, index=True)
    target_url = Column(String(2000), nullable=False, index=True)
    target_page_id = Column(Integer, ForeignKey("page_metrics.id"))

    # Suggestion
    anchor_text = Column(String(500), nullable=False)
    context = Column(Text)  # surrounding paragraph
    placement_hint = Column(String(100))  # "after heading 2", "in intro paragraph", etc.

    # Scoring
    relevance_score = Column(Float)  # 0.0-1.0
    priority_score = Column(Float)  # 0.0-1.0

    # Status
    status = Column(String(20), default='suggested')  # suggested, approved, implemented, rejected
    implemented_at = Column(DateTime)

    # Metadata
    reasoning = Column(Text)
    created_by_task = Column(String(50))  # task_log ID
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_internal_links_source_status', 'source_page_id', 'status'),
    )


class CitationModel(Base):
    """
    NAP (Name, Address, Phone) citations for local SEO (Step 11).
    """

    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)

    # Citation source
    directory_name = Column(String(255), nullable=False, index=True)
    directory_url = Column(String(2000))
    directory_tier = Column(String(10))  # A, B, C (importance)

    # NAP data found
    business_name_found = Column(String(255))
    address_found = Column(String(500))
    phone_found = Column(String(50))

    # Verification
    name_matches = Column(Boolean)
    address_matches = Column(Boolean)
    phone_matches = Column(Boolean)
    nap_consistent = Column(Boolean, index=True)

    # Link
    has_link = Column(Boolean, default=False)
    source_url = Column(String(2000))  # URL of citation page

    # Status
    status = Column(String(20), default='active')  # active, outdated, missing
    last_verified_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_citations_directory_tier', 'directory_tier', 'nap_consistent'),
    )


class CompetitorPageModel(Base):
    """
    Competitor content analysis for gap detection (Step 10).
    """

    __tablename__ = "competitor_pages"

    id = Column(Integer, primary_key=True, index=True)
    competitor_domain = Column(String(255), nullable=False, index=True)
    url = Column(String(2000), nullable=False, unique=True, index=True)

    # Content
    title = Column(String(500))
    meta_description = Column(String(1000))
    h1 = Column(String(500))
    word_count = Column(Integer)
    content_topics = Column(ARRAY(String(100)))

    # Performance
    estimated_traffic = Column(Integer)
    ranking_keywords = Column(Integer, default=0)
    backlinks = Column(Integer, default=0)
    domain_authority = Column(Integer)

    # Analysis
    content_gaps = Column(ARRAY(String(200)))  # Topics they cover that we don't
    our_advantages = Column(ARRAY(String(200)))  # Topics we cover better

    # Tracking
    last_analyzed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_competitor_pages_domain', 'competitor_domain'),
    )


# ============================================================================
# SCRAPE SUITE MODELS (Additional)
# ============================================================================

class SerpResultModel(Base):
    """
    Individual SERP results for each snapshot.
    Stores all positions for a query, not just ours.
    """

    __tablename__ = "serp_results"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("serp_snapshots.id"), nullable=False, index=True)

    # Position data
    rank = Column(Integer, nullable=False)
    url = Column(String(2000), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    title = Column(String(500))
    snippet = Column(Text)

    # Ownership
    is_ours = Column(Boolean, default=False, index=True)

    # Additional data (SERP features, rich results, etc.)
    data = Column(JSON)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_serp_results_snapshot', 'snapshot_id'),
        Index('idx_serp_results_domain_rank', 'domain', 'rank'),
    )


class CompetitorModel(Base):
    """
    Competitor sites being monitored.
    Central table for organizing competitor tracking.
    """

    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    priority = Column(String(20), default='medium')  # low, medium, high, critical

    # Status
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_scraped = Column(DateTime)

    __table_args__ = (
        Index('idx_competitors_active_priority', 'is_active', 'priority'),
    )


class ReferringDomainModel(Base):
    """
    Domain-level backlink metrics aggregation.
    Tracks unique domains linking to us.
    """

    __tablename__ = "referring_domains"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)

    # Metrics
    backlink_count = Column(Integer, default=0)
    inbody_link_count = Column(Integer, default=0)  # Links in main content
    authority_score = Column(Integer)  # 0-100 domain authority

    # Status
    last_updated = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_referring_domains_authority', 'authority_score'),
    )


class PageAuditModel(Base):
    """
    Technical SEO audits for specific pages.
    Stores audit run metadata and overall metrics.

    TODO (Step 15): Partition by audit_date for high-volume data.
    """

    __tablename__ = "page_audits"

    id = Column(Integer, primary_key=True, index=True)
    page_url = Column(String(2000), nullable=False, index=True)
    audit_date = Column(DateTime, nullable=False, index=True)

    # Status
    status_code = Column(Integer)

    # Performance metrics (lightweight proxy)
    performance_proxy = Column(JSON)  # {load_time, size, requests_count, etc.}

    # Summary
    issues_found = Column(Integer, default=0)
    notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_page_audits_url_date', 'page_url', 'audit_date'),
    )


class PageAuditIssueModel(Base):
    """
    Individual issues found during page audits.
    Linked to PageAuditModel.
    """

    __tablename__ = "page_audit_issues"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("page_audits.id"), nullable=False, index=True)

    # Issue details
    type = Column(String(100), nullable=False, index=True)  # missing_meta, slow_load, broken_link
    description = Column(Text)
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical

    # Resolution
    fixed = Column(Boolean, default=False, index=True)
    fixed_date = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_audit_issues_audit_severity', 'audit_id', 'severity'),
        Index('idx_audit_issues_fixed', 'fixed', 'type'),
    )


# Export all models
__all__ = [
    "Base",
    # Core CRM
    "UserModel",
    "ContactModel",
    "LeadModel",
    "InteractionModel",
    "ServiceModel",
    "QuoteModel",
    "QuoteItemModel",
    # AI Governance (Step 01)
    "ChangeLogModel",
    "TaskLogModel",
    "AuditIssueModel",
    "AutomationModuleConfigModel",
    "ModuleGraduationLogModel",
    # SEO Data (Step 02 - Expanded)
    "PageModel",
    "KeywordModel",
    "SerpSnapshotModel",
    "RankChangeModel",
    "BacklinkModel",
    "SchemaMarkupModel",
    "ContentClusterModel",
    "ClusterMembershipModel",
    "InternalLinkSuggestionModel",
    "CitationModel",
    "CompetitorPageModel",
    # Scrape Suite (Additional)
    "SerpResultModel",
    "CompetitorModel",
    "ReferringDomainModel",
    "PageAuditModel",
    "PageAuditIssueModel",
    # Enums
    "ChangeStatus",
    "TaskPriority",
    "TaskStatus",
    "IssueSeverity",
    "IssueStatus",
    "OperatingMode",
    "RolloutPhase",
    "ModuleGraduationAction",
]
