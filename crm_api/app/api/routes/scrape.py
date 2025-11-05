"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Scrape Suite API Routes

REST endpoints for Scrape Suite functionality.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.db import get_db
from app.api.deps import require_manager_claims
from app.schemas.scrape import (
    JobTriggerRequest,
    JobStatusResponse,
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse,
    SerpSnapshotResponse,
    SerpSnapshotListResponse,
    SerpResultResponse,
    SerpResultListResponse,
    CompetitorResponse,
    CompetitorListResponse,
    CompetitorPageResponse,
    CompetitorPageListResponse,
    BacklinkResponse,
    BacklinkListResponse,
    ReferringDomainResponse,
    ReferringDomainListResponse,
    CitationResponse,
    CitationListResponse,
    PageAuditResponse,
    PageAuditListResponse,
    ScrapeSettingsResponse,
    ScrapeSettingsUpdate,
    ScrapeSuiteDashboardResponse
)
from app.db_models import (
    SerpSnapshotModel,
    SerpResultModel,
    CompetitorModel,
    CompetitorPageModel,
    BacklinkModel,
    ReferringDomainModel,
    CitationModel,
    PageAuditModel,
    PageAuditIssueModel,
    TaskLogModel,
    KeywordModel
)
from app.jobs.scrape_jobs import (
    run_daily_serp_snapshot,
    run_competitor_crawl,
    run_backlink_refresh,
    run_citations_refresh
)
from app.services.tasklog_service import get_tasklog_service

import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/scrape", tags=["Scrape Suite"])


# ==============================================================================
# Job Management
# ==============================================================================

@router.post("/jobs", response_model=JobStatusResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_job(
    request: JobTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Manually trigger a scrape job.

    Submits a background job for the specified type (serp, crawl, backlinks, citations).

    Args:
        request: Job trigger request with type and payload
        background_tasks: FastAPI background tasks
        db: Database session
        claims: JWT claims (requires owner or admin)

    Returns:
        Job status response with task ID

    Raises:
        HTTPException: 400 if invalid job type
    """
    job_type = request.type.lower()

    # Validate job type and schedule appropriate job
    if job_type == "serp":
        background_tasks.add_task(run_daily_serp_snapshot, db)
        task_name = "Manual SERP Snapshot"
    elif job_type == "crawl":
        # Extract site_id or domain from payload
        site_id = request.payload.get("site_id")
        domain = request.payload.get("domain")

        if not site_id and not domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crawl job requires site_id or domain in payload"
            )

        background_tasks.add_task(run_competitor_crawl, db, site_id, domain)
        task_name = f"Manual Crawl: {domain or f'Site {site_id}'}"
    elif job_type == "backlinks":
        background_tasks.add_task(run_backlink_refresh, db)
        task_name = "Manual Backlinks Refresh"
    elif job_type == "citations":
        background_tasks.add_task(run_citations_refresh, db)
        task_name = "Manual Citations Refresh"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job type: {job_type}. Must be serp, crawl, backlinks, or citations"
        )

    logger.info(
        "scrape_job_triggered",
        job_type=job_type,
        triggered_by=claims.get("sub"),
        task_name=task_name
    )

    # Return pending status (job will run in background)
    return JobStatusResponse(
        job_id=f"{job_type}_{datetime.utcnow().timestamp()}",
        task_id=None,
        status="queued",
        task_name=task_name,
        queued_at=datetime.utcnow()
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get job status by ID.

    Queries task_logs to find the job status.

    Args:
        job_id: Job/task ID
        db: Database session
        claims: JWT claims

    Returns:
        Job status response

    Raises:
        HTTPException: 404 if job not found
    """
    # Look up task in task_logs
    task = db.query(TaskLogModel).filter_by(task_id=job_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )

    return JobStatusResponse(
        job_id=job_id,
        task_id=task.task_id,
        status=task.status.value,
        task_name=task.task_name,
        queued_at=task.queued_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        duration_seconds=task.duration_seconds,
        items_processed=task.items_processed,
        items_succeeded=task.items_succeeded,
        items_failed=task.items_failed,
        error_message=task.error_message,
        output_summary=task.output_summary
    )


# ==============================================================================
# Keywords
# ==============================================================================

@router.get("/keywords", response_model=KeywordListResponse)
def get_keywords(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    intent: Optional[str] = Query(None, description="Filter by intent"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get list of tracked keywords with filters.

    Args:
        is_active: Filter by active status
        intent: Filter by keyword intent
        page: Page number
        page_size: Items per page
        db: Database session
        claims: JWT claims

    Returns:
        Paginated list of keywords
    """
    query = db.query(KeywordModel)

    # Apply filters
    if is_active is not None:
        query = query.filter(KeywordModel.is_active == is_active)

    if intent:
        query = query.filter(KeywordModel.intent == intent)

    # Get total count
    total = query.count()

    # Apply pagination
    keywords = query.order_by(
        desc(KeywordModel.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()

    return KeywordListResponse(
        keywords=[KeywordResponse.model_validate(k) for k in keywords],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/keywords", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
def create_keyword(
    keyword: KeywordCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Create a new keyword to track.

    Args:
        keyword: Keyword creation data
        db: Database session
        claims: JWT claims

    Returns:
        Created keyword

    Raises:
        HTTPException: 400 if keyword already exists
    """
    # Check if keyword already exists for this domain
    existing = db.query(KeywordModel).filter(
        and_(
            KeywordModel.keyword_text == keyword.keyword_text,
            KeywordModel.target_domain == keyword.target_domain
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keyword '{keyword.keyword_text}' already exists for domain '{keyword.target_domain}'"
        )

    # Create new keyword
    new_keyword = KeywordModel(
        keyword_text=keyword.keyword_text,
        target_domain=keyword.target_domain,
        target_page=keyword.target_page,
        intent=keyword.intent,
        search_volume=keyword.search_volume,
        difficulty=keyword.difficulty,
        is_active=keyword.is_active
    )

    db.add(new_keyword)
    db.commit()
    db.refresh(new_keyword)

    logger.info(
        "keyword_created",
        keyword_id=new_keyword.id,
        keyword_text=new_keyword.keyword_text,
        target_domain=new_keyword.target_domain
    )

    return KeywordResponse.model_validate(new_keyword)


@router.get("/keywords/{keyword_id}", response_model=KeywordResponse)
def get_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get keyword by ID.

    Args:
        keyword_id: Keyword ID
        db: Database session
        claims: JWT claims

    Returns:
        Keyword details

    Raises:
        HTTPException: 404 if keyword not found
    """
    keyword = db.query(KeywordModel).filter_by(id=keyword_id).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword not found: {keyword_id}"
        )

    return KeywordResponse.model_validate(keyword)


@router.put("/keywords/{keyword_id}", response_model=KeywordResponse)
def update_keyword(
    keyword_id: int,
    keyword_update: KeywordUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Update keyword fields.

    Args:
        keyword_id: Keyword ID
        keyword_update: Fields to update
        db: Database session
        claims: JWT claims

    Returns:
        Updated keyword

    Raises:
        HTTPException: 404 if keyword not found
    """
    keyword = db.query(KeywordModel).filter_by(id=keyword_id).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword not found: {keyword_id}"
        )

    # Update fields if provided
    update_data = keyword_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(keyword, field, value)

    db.commit()
    db.refresh(keyword)

    logger.info(
        "keyword_updated",
        keyword_id=keyword.id,
        fields_updated=list(update_data.keys())
    )

    return KeywordResponse.model_validate(keyword)


@router.delete("/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Delete a keyword.

    Args:
        keyword_id: Keyword ID
        db: Database session
        claims: JWT claims

    Raises:
        HTTPException: 404 if keyword not found
    """
    keyword = db.query(KeywordModel).filter_by(id=keyword_id).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword not found: {keyword_id}"
        )

    db.delete(keyword)
    db.commit()

    logger.info(
        "keyword_deleted",
        keyword_id=keyword_id,
        keyword_text=keyword.keyword_text
    )


# ==============================================================================
# SERP Snapshots & Results
# ==============================================================================

@router.get("/serp/snapshots", response_model=SerpSnapshotListResponse)
def get_serp_snapshots(
    keyword_id: Optional[int] = Query(None, description="Filter by keyword ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for date range"),
    end_date: Optional[datetime] = Query(None, description="End date for date range"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get SERP snapshots with optional filters.

    Args:
        keyword_id: Filter by keyword
        start_date: Filter by date range start
        end_date: Filter by date range end
        page: Page number
        page_size: Items per page
        db: Database session
        claims: JWT claims

    Returns:
        Paginated list of SERP snapshots
    """
    query = db.query(SerpSnapshotModel)

    # Apply filters
    if keyword_id:
        query = query.filter(SerpSnapshotModel.keyword_id == keyword_id)

    if start_date:
        query = query.filter(SerpSnapshotModel.search_date >= start_date)

    if end_date:
        query = query.filter(SerpSnapshotModel.search_date <= end_date)

    # Get total count
    total = query.count()

    # Apply pagination
    snapshots = query.order_by(
        desc(SerpSnapshotModel.search_date)
    ).offset((page - 1) * page_size).limit(page_size).all()

    return SerpSnapshotListResponse(
        snapshots=[SerpSnapshotResponse.model_validate(s) for s in snapshots],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/serp/results", response_model=SerpResultListResponse)
def get_serp_results(
    snapshot_id: int = Query(..., description="Snapshot ID"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get SERP results for a specific snapshot.

    Args:
        snapshot_id: Snapshot ID
        db: Database session
        claims: JWT claims

    Returns:
        List of SERP results for the snapshot

    Raises:
        HTTPException: 404 if snapshot not found
    """
    # Verify snapshot exists
    snapshot = db.query(SerpSnapshotModel).filter_by(id=snapshot_id).first()
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot not found: {snapshot_id}"
        )

    # Get results
    results = db.query(SerpResultModel).filter_by(
        snapshot_id=snapshot_id
    ).order_by(SerpResultModel.rank).all()

    return SerpResultListResponse(
        results=[SerpResultResponse.model_validate(r) for r in results],
        snapshot_id=snapshot_id,
        total=len(results)
    )


# ==============================================================================
# Competitors
# ==============================================================================

@router.get("/competitors", response_model=CompetitorListResponse)
def get_competitors(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get list of tracked competitors.

    Args:
        is_active: Filter by active status
        category: Filter by category
        priority: Filter by priority
        db: Database session
        claims: JWT claims

    Returns:
        List of competitors
    """
    query = db.query(CompetitorModel)

    # Apply filters
    if is_active is not None:
        query = query.filter(CompetitorModel.is_active == is_active)

    if category:
        query = query.filter(CompetitorModel.category == category)

    if priority:
        query = query.filter(CompetitorModel.priority == priority)

    competitors = query.order_by(CompetitorModel.domain).all()

    return CompetitorListResponse(
        competitors=[CompetitorResponse.model_validate(c) for c in competitors],
        total=len(competitors)
    )


@router.get("/pages", response_model=CompetitorPageListResponse)
def get_competitor_pages(
    site_id: Optional[int] = Query(None, description="Filter by competitor site ID"),
    changed_only: bool = Query(False, description="Show only recently changed pages"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get competitor pages with optional filters.

    Args:
        site_id: Filter by competitor site
        changed_only: Show only recently changed pages
        page: Page number
        page_size: Items per page
        db: Database session
        claims: JWT claims

    Returns:
        Paginated list of competitor pages
    """
    query = db.query(CompetitorPageModel)

    # Apply filters
    if site_id:
        query = query.filter(CompetitorPageModel.site_id == site_id)

    if changed_only:
        # Pages modified in last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        query = query.filter(
            and_(
                CompetitorPageModel.last_modified.isnot(None),
                CompetitorPageModel.last_modified >= cutoff_date
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    pages = query.order_by(
        desc(CompetitorPageModel.last_modified)
    ).offset((page - 1) * page_size).limit(page_size).all()

    # Convert to response models
    page_responses = []
    for p in pages:
        response = CompetitorPageResponse.model_validate(p)
        # Compute is_changed flag
        if p.last_modified and p.last_modified > (datetime.utcnow() - timedelta(days=30)):
            response.is_changed = True
        page_responses.append(response)

    return CompetitorPageListResponse(
        pages=page_responses,
        total=total,
        page=page,
        page_size=page_size
    )


# ==============================================================================
# Backlinks
# ==============================================================================

@router.get("/backlinks", response_model=BacklinkListResponse)
def get_backlinks(
    domain: Optional[str] = Query(None, description="Filter by source domain"),
    alive: Optional[bool] = Query(None, description="Filter by alive/lost status"),
    dofollow: Optional[bool] = Query(None, description="Filter by dofollow status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get backlinks with optional filters.

    Args:
        domain: Filter by source domain
        alive: Filter by alive/lost status (alive=True means not lost)
        dofollow: Filter by dofollow status
        page: Page number
        page_size: Items per page
        db: Database session
        claims: JWT claims

    Returns:
        Paginated list of backlinks
    """
    query = db.query(BacklinkModel)

    # Apply filters
    if domain:
        query = query.filter(BacklinkModel.source_domain.ilike(f"%{domain}%"))

    if alive is not None:
        query = query.filter(BacklinkModel.is_lost == (not alive))

    if dofollow is not None:
        query = query.filter(BacklinkModel.is_dofollow == dofollow)

    # Get total count
    total = query.count()

    # Apply pagination
    backlinks = query.order_by(
        desc(BacklinkModel.last_seen)
    ).offset((page - 1) * page_size).limit(page_size).all()

    return BacklinkListResponse(
        backlinks=[BacklinkResponse.model_validate(b) for b in backlinks],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/referring-domains", response_model=ReferringDomainListResponse)
def get_referring_domains(
    min_authority: Optional[int] = Query(None, ge=0, le=100, description="Minimum authority score"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get referring domains (aggregated backlink sources).

    Args:
        min_authority: Filter by minimum authority score
        db: Database session
        claims: JWT claims

    Returns:
        List of referring domains
    """
    query = db.query(ReferringDomainModel)

    # Apply filter
    if min_authority is not None:
        query = query.filter(ReferringDomainModel.authority_score >= min_authority)

    domains = query.order_by(
        desc(ReferringDomainModel.authority_score)
    ).all()

    return ReferringDomainListResponse(
        domains=[ReferringDomainResponse.model_validate(d) for d in domains],
        total=len(domains)
    )


# ==============================================================================
# Citations
# ==============================================================================

@router.get("/citations", response_model=CitationListResponse)
def get_citations(
    listed: Optional[bool] = Query(None, description="Filter by listed status"),
    nap_match: Optional[bool] = Query(None, description="Filter by NAP consistency"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get business citations.

    Args:
        listed: Filter by listed status
        nap_match: Filter by NAP consistency
        db: Database session
        claims: JWT claims

    Returns:
        List of citations
    """
    query = db.query(CitationModel)

    # Apply filters
    if listed is not None:
        query = query.filter(CitationModel.is_listed == listed)

    if nap_match is not None:
        query = query.filter(CitationModel.nap_match == nap_match)

    citations = query.order_by(CitationModel.platform).all()

    return CitationListResponse(
        citations=[CitationResponse.model_validate(c) for c in citations],
        total=len(citations)
    )


# ==============================================================================
# Page Audits
# ==============================================================================

@router.get("/audits", response_model=PageAuditListResponse)
def get_page_audits(
    severity: Optional[str] = Query(None, description="Filter by severity (info, warning, error)"),
    fixed: Optional[bool] = Query(None, description="Filter by fixed status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get page audits with optional filters.

    Args:
        severity: Filter by issue severity
        fixed: Filter by fixed status
        page: Page number
        page_size: Items per page
        db: Database session
        claims: JWT claims

    Returns:
        Paginated list of page audits with issues
    """
    # Start with page audits
    query = db.query(PageAuditModel)

    # Get total count
    total = query.count()

    # Apply pagination
    audits = query.order_by(
        desc(PageAuditModel.audit_date)
    ).offset((page - 1) * page_size).limit(page_size).all()

    # Get audit IDs for fetching issues
    audit_ids = [a.id for a in audits]

    # Fetch all issues for these audits
    issues_query = db.query(PageAuditIssueModel).filter(
        PageAuditIssueModel.audit_id.in_(audit_ids)
    )

    # Apply issue filters
    if severity:
        issues_query = issues_query.filter(PageAuditIssueModel.severity == severity)

    if fixed is not None:
        issues_query = issues_query.filter(PageAuditIssueModel.fixed == fixed)

    issues = issues_query.all()

    # Group issues by audit_id
    issues_by_audit = {}
    for issue in issues:
        if issue.audit_id not in issues_by_audit:
            issues_by_audit[issue.audit_id] = []
        issues_by_audit[issue.audit_id].append(issue)

    # Build response models
    audit_responses = []
    for audit in audits:
        audit_issues = issues_by_audit.get(audit.id, [])
        response = PageAuditResponse.model_validate(audit)
        response.issues = [
            PageAuditIssueResponse.model_validate(i) for i in audit_issues
        ]
        audit_responses.append(response)

    return PageAuditListResponse(
        audits=audit_responses,
        total=total,
        page=page,
        page_size=page_size
    )


# ==============================================================================
# Settings
# ==============================================================================

@router.get("/settings", response_model=ScrapeSettingsResponse)
def get_scrape_settings(
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get Scrape Suite settings.

    For now, returns default settings. In future, load from database.

    Args:
        db: Database session
        claims: JWT claims

    Returns:
        Scrape settings
    """
    # TODO: Load from database settings table
    return ScrapeSettingsResponse(
        review_mode=False,
        daily_serp_enabled=True,
        weekly_crawl_enabled=True,
        monthly_crawl_enabled=True,
        backlinks_refresh_days=7,
        citations_refresh_days=30,
        max_pages_per_crawl=100,
        proxy_pool_enabled=False
    )


@router.put("/settings", response_model=ScrapeSettingsResponse)
def update_scrape_settings(
    settings: ScrapeSettingsUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Update Scrape Suite settings.

    Args:
        settings: Settings update
        db: Database session
        claims: JWT claims

    Returns:
        Updated settings
    """
    # TODO: Store in database settings table
    logger.info(
        "scrape_settings_updated",
        updated_by=claims.get("sub"),
        settings=settings.model_dump(exclude_none=True)
    )

    # For now, return the update as if it was saved
    current = ScrapeSettingsResponse()

    # Apply updates
    update_data = settings.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(current, field, value)

    return current


# ==============================================================================
# Dashboard/Stats
# ==============================================================================

@router.get("/dashboard", response_model=ScrapeSuiteDashboardResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    claims: dict = Depends(require_manager_claims)
):
    """
    Get dashboard statistics for Scrape Suite.

    Args:
        db: Database session
        claims: JWT claims

    Returns:
        Dashboard stats
    """
    # Aggregate counts
    serp_count = db.query(SerpSnapshotModel).count()
    competitors_count = db.query(CompetitorModel).filter_by(is_active=True).count()
    pages_count = db.query(CompetitorPageModel).count()
    backlinks_count = db.query(BacklinkModel).filter_by(is_lost=False).count()
    citations_count = db.query(CitationModel).filter_by(is_listed=True).count()

    # Recent changes (last 7 days)
    cutoff = datetime.utcnow() - timedelta(days=7)
    recent_changes = db.query(CompetitorPageModel).filter(
        and_(
            CompetitorPageModel.last_modified.isnot(None),
            CompetitorPageModel.last_modified >= cutoff
        )
    ).count()

    # Last run dates
    last_serp = db.query(SerpSnapshotModel).order_by(
        desc(SerpSnapshotModel.created_at)
    ).first()

    last_crawl = db.query(CompetitorModel).filter(
        CompetitorModel.last_scraped.isnot(None)
    ).order_by(desc(CompetitorModel.last_scraped)).first()

    last_backlinks = db.query(BacklinkModel).order_by(
        desc(BacklinkModel.last_checked)
    ).first()

    return ScrapeSuiteDashboardResponse(
        serp_snapshots_count=serp_count,
        competitors_tracked=competitors_count,
        pages_monitored=pages_count,
        backlinks_count=backlinks_count,
        citations_count=citations_count,
        recent_changes=recent_changes,
        pending_reviews=0,  # TODO: Implement review queue
        last_serp_snapshot=last_serp.created_at if last_serp else None,
        last_competitor_crawl=last_crawl.last_scraped if last_crawl else None,
        last_backlinks_refresh=last_backlinks.last_checked if last_backlinks else None
    )
