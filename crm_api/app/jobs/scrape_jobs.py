"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Scrape Suite Scheduled Jobs

Orchestrates scraping tasks via Scrape Bot connector:
- Daily SERP snapshots
- Competitor crawling
- Backlink refresh
- Citations refresh
"""

from typing import Optional, Dict, Any, List
import hashlib
import structlog
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.config import settings
from app.db_models import (
    SerpSnapshotModel,
    SerpResultModel,
    KeywordModel,
    CompetitorModel,
    CompetitorPageModel,
    BacklinkModel,
    ReferringDomainModel,
    CitationModel,
    TaskPriority
)
from app.services.scrape_connector import (
    ScrapeConnector,
    JobType,
    ScrapeConnectorError
)
from app.services.tasklog_service import TaskLogService, get_tasklog_service
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.services.qdrant_service import QdrantService

logger = structlog.get_logger(__name__)

MODULE_NAME = "scrape_suite"


# ==============================================================================
# Job 1: Daily SERP Snapshot
# ==============================================================================

def run_daily_serp_snapshot(db: Session) -> Dict[str, Any]:
    """
    Execute daily SERP snapshot for all tracked keywords.

    Workflow:
    1. Get all active keywords
    2. Submit SERP job to Scrape Bot
    3. Poll until completion
    4. Store snapshot and results
    5. Generate embeddings for snippets
    6. Return summary

    Args:
        db: Database session

    Returns:
        Summary dict with counts and status
    """
    tasklog = get_tasklog_service(db)

    # Use advisory lock to prevent concurrent execution
    with tasklog.advisory_lock("daily_serp_snapshot") as acquired:
        if not acquired:
            logger.warning("serp_snapshot_already_running")
            return {"status": "skipped", "reason": "already_running"}

        # Use context manager for automatic task logging
        with tasklog.task_execution(
            task_name="Daily SERP Snapshot",
            module=MODULE_NAME,
            priority=TaskPriority.HIGH
        ) as task_id:

            # Initialize services
            connector = _get_scrape_connector()
            embedding_service = _get_embedding_service(db)

            # Get all active keywords
            keywords = db.query(KeywordModel).filter_by(
                is_active=True
            ).all()

            if not keywords:
                logger.info("no_active_keywords_found")
                return {"status": "completed", "keywords_processed": 0}

            logger.info(
                "serp_snapshot_starting",
                task_id=task_id,
                keyword_count=len(keywords)
            )

            # Build payload for Scrape Bot
            payload = {
                "queries": [kw.keyword for kw in keywords],
                "location": "US",  # TODO: Make configurable per keyword
                "device": "desktop"
            }

            try:
                # Submit job
                job_id = connector.submit_job(JobType.SERP, payload)
                logger.info("serp_job_submitted", job_id=job_id)

                # Poll until complete
                status_data = connector.poll_until_complete(
                    job_id=job_id,
                    poll_interval=5,
                    max_wait=600  # 10 minutes
                )

                run_id = status_data.get("run_id")
                if not run_id:
                    raise ValueError("No run_id in completion status")

                # Fetch results
                results = connector.fetch_results(run_id, "serp")

                # Process results
                snapshots_created = 0
                serp_results_created = 0
                embeddings_created = 0

                for result in results:
                    query = result.get("query")
                    entries = result.get("results", [])

                    # Find matching keyword
                    keyword = next(
                        (kw for kw in keywords if kw.keyword == query),
                        None
                    )

                    if not keyword:
                        logger.warning("keyword_not_found", query=query)
                        continue

                    # Find our ranking
                    our_rank = None
                    our_url = None
                    for idx, entry in enumerate(entries, start=1):
                        url = entry.get("url", "")
                        if _is_our_domain(url):
                            our_rank = idx
                            our_url = url
                            break

                    # Create snapshot
                    snapshot = SerpSnapshotModel(
                        keyword_id=keyword.id,
                        search_date=datetime.utcnow(),
                        rank=our_rank,
                        url=our_url,
                        featured_snippet=result.get("has_featured_snippet", False),
                        people_also_ask=result.get("has_people_also_ask", False),
                        local_pack=result.get("has_local_pack", False),
                        knowledge_panel=result.get("has_knowledge_panel", False),
                        serp_features=result.get("serp_features", [])
                    )

                    db.add(snapshot)
                    db.flush()  # Get snapshot ID
                    snapshots_created += 1

                    # Create SERP results
                    for idx, entry in enumerate(entries[:20], start=1):  # Top 20
                        url = entry.get("url", "")
                        domain = _extract_domain(url)
                        title = entry.get("title", "")
                        snippet = entry.get("snippet", "")

                        serp_result = SerpResultModel(
                            snapshot_id=snapshot.id,
                            rank=idx,
                            url=url,
                            domain=domain,
                            title=title,
                            snippet=snippet,
                            is_ours=_is_our_domain(url),
                            data=entry  # Store full result
                        )

                        db.add(serp_result)
                        db.flush()  # Get result ID
                        serp_results_created += 1

                        # Generate embedding for snippet
                        if snippet and embedding_service:
                            success = embedding_service.upsert_serp_embedding(
                                result_id=serp_result.id,
                                snapshot_id=snapshot.id,
                                url=url,
                                snippet=snippet,
                                query=query
                            )

                            if success:
                                embeddings_created += 1

                    db.commit()

                # Update task log with counts
                tasklog.complete_task(
                    task_id=task_id,
                    items_processed=len(results),
                    items_succeeded=snapshots_created,
                    output_summary={
                        "snapshots": snapshots_created,
                        "serp_results": serp_results_created,
                        "embeddings": embeddings_created,
                        "run_id": run_id
                    }
                )

                logger.info(
                    "serp_snapshot_completed",
                    snapshots=snapshots_created,
                    results=serp_results_created,
                    embeddings=embeddings_created
                )

                return {
                    "status": "completed",
                    "keywords_processed": len(results),
                    "snapshots_created": snapshots_created,
                    "serp_results_created": serp_results_created,
                    "embeddings_created": embeddings_created
                }

            except ScrapeConnectorError as e:
                logger.error("serp_job_failed", error=str(e), kind=e.kind)
                db.rollback()
                raise

            except Exception as e:
                logger.error("serp_snapshot_error", error=str(e))
                db.rollback()
                raise


# ==============================================================================
# Job 2: Competitor Crawl
# ==============================================================================

def run_competitor_crawl(
    db: Session,
    site_id: Optional[int] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crawl competitor site and detect content changes.

    Workflow:
    1. Get competitor site info
    2. Submit crawl job to Scrape Bot
    3. Poll until completion
    4. For each page:
       - Compute normalized hash
       - Detect changes
       - Store page data
       - Generate embeddings
    5. Return summary

    Args:
        db: Database session
        site_id: Competitor site ID (mutually exclusive with domain)
        domain: Competitor domain (mutually exclusive with site_id)

    Returns:
        Summary dict with counts and changes
    """
    tasklog = get_tasklog_service(db)

    # Get competitor
    if site_id:
        competitor = db.query(CompetitorModel).filter_by(id=site_id).first()
    elif domain:
        competitor = db.query(CompetitorModel).filter_by(domain=domain).first()
    else:
        raise ValueError("Must provide site_id or domain")

    if not competitor:
        raise ValueError(f"Competitor not found: site_id={site_id}, domain={domain}")

    lock_name = f"competitor_crawl_{competitor.id}"

    with tasklog.advisory_lock(lock_name) as acquired:
        if not acquired:
            logger.warning("competitor_crawl_already_running", competitor_id=competitor.id)
            return {"status": "skipped", "reason": "already_running"}

        with tasklog.task_execution(
            task_name=f"Competitor Crawl: {competitor.domain}",
            module=MODULE_NAME,
            priority=TaskPriority.MEDIUM,
            input_params={"site_id": competitor.id, "domain": competitor.domain}
        ) as task_id:

            connector = _get_scrape_connector()
            embedding_service = _get_embedding_service(db)

            # Build payload
            payload = {
                "start_url": f"https://{competitor.domain}",
                "max_pages": 100,  # TODO: Make configurable by tier
                "follow_links": True,
                "extract_text": True
            }

            try:
                # Submit job
                job_id = connector.submit_job(JobType.CRAWL, payload)
                logger.info("crawl_job_submitted", job_id=job_id, domain=competitor.domain)

                # Poll until complete
                status_data = connector.poll_until_complete(
                    job_id=job_id,
                    poll_interval=10,
                    max_wait=1800  # 30 minutes for full crawl
                )

                run_id = status_data.get("run_id")
                if not run_id:
                    raise ValueError("No run_id in completion status")

                # Fetch results
                pages = connector.fetch_results(run_id, "pages")

                pages_created = 0
                pages_updated = 0
                pages_unchanged = 0
                embeddings_created = 0

                for page_data in pages:
                    url = page_data.get("url")
                    title = page_data.get("title", "")
                    extracted_text = page_data.get("extracted_text", "")
                    page_type = page_data.get("page_type", "other")
                    status_code = page_data.get("status_code", 200)

                    # Compute normalized hash
                    content_hash = _compute_content_hash(extracted_text)

                    # Check if page exists
                    existing_page = db.query(CompetitorPageModel).filter(
                        and_(
                            CompetitorPageModel.site_id == competitor.id,
                            CompetitorPageModel.url == url
                        )
                    ).first()

                    if existing_page:
                        # Check for changes
                        if existing_page.content_hash != content_hash:
                            # Content changed
                            existing_page.content_hash = content_hash
                            existing_page.last_seen = datetime.utcnow()
                            existing_page.last_modified = datetime.utcnow()
                            existing_page.title = title
                            existing_page.page_type = page_type
                            existing_page.status_code = status_code
                            pages_updated += 1

                            logger.info(
                                "competitor_page_changed",
                                url=url,
                                old_hash=existing_page.content_hash[:8],
                                new_hash=content_hash[:8]
                            )
                        else:
                            # No change
                            existing_page.last_seen = datetime.utcnow()
                            pages_unchanged += 1
                    else:
                        # New page
                        new_page = CompetitorPageModel(
                            site_id=competitor.id,
                            url=url,
                            title=title,
                            page_type=page_type,
                            content_hash=content_hash,
                            status_code=status_code,
                            first_seen=datetime.utcnow(),
                            last_seen=datetime.utcnow()
                        )

                        db.add(new_page)
                        db.flush()
                        pages_created += 1

                        # Generate embeddings for new pages
                        if extracted_text and embedding_service:
                            # Split into chunks (simple approach: split by paragraphs)
                            chunks = _chunk_text(extracted_text, max_length=1000)

                            if chunks:
                                success = embedding_service.upsert_page_embedding(
                                    page_id=new_page.id,
                                    site_id=competitor.id,
                                    url=url,
                                    title=title,
                                    page_type=page_type,
                                    chunks=chunks
                                )

                                if success:
                                    embeddings_created += 1

                db.commit()

                # Update competitor last_scraped
                competitor.last_scraped = datetime.utcnow()
                db.commit()

                tasklog.complete_task(
                    task_id=task_id,
                    items_processed=len(pages),
                    items_succeeded=pages_created + pages_updated,
                    output_summary={
                        "pages_created": pages_created,
                        "pages_updated": pages_updated,
                        "pages_unchanged": pages_unchanged,
                        "embeddings_created": embeddings_created,
                        "run_id": run_id
                    }
                )

                logger.info(
                    "competitor_crawl_completed",
                    domain=competitor.domain,
                    pages_created=pages_created,
                    pages_updated=pages_updated,
                    embeddings=embeddings_created
                )

                return {
                    "status": "completed",
                    "domain": competitor.domain,
                    "pages_crawled": len(pages),
                    "pages_created": pages_created,
                    "pages_updated": pages_updated,
                    "pages_unchanged": pages_unchanged,
                    "embeddings_created": embeddings_created
                }

            except ScrapeConnectorError as e:
                logger.error("crawl_job_failed", error=str(e), kind=e.kind)
                db.rollback()
                raise

            except Exception as e:
                logger.error("competitor_crawl_error", error=str(e))
                db.rollback()
                raise


# ==============================================================================
# Job 3: Backlink Refresh
# ==============================================================================

def run_backlink_refresh(db: Session) -> Dict[str, Any]:
    """
    Refresh backlink data for our domain.

    Workflow:
    1. Submit backlinks job to Scrape Bot
    2. Poll until completion
    3. Upsert backlinks
    4. Aggregate referring domains
    5. Recalculate Link Authority Score (LAS)

    Args:
        db: Database session

    Returns:
        Summary dict with counts
    """
    tasklog = get_tasklog_service(db)

    with tasklog.advisory_lock("backlink_refresh") as acquired:
        if not acquired:
            logger.warning("backlink_refresh_already_running")
            return {"status": "skipped", "reason": "already_running"}

        with tasklog.task_execution(
            task_name="Backlink Refresh",
            module=MODULE_NAME,
            priority=TaskPriority.MEDIUM
        ) as task_id:

            connector = _get_scrape_connector()

            # Build payload
            payload = {
                "target_domain": _get_our_domain(),
                "include_lost": True,
                "max_backlinks": 10000
            }

            try:
                # Submit job
                job_id = connector.submit_job(JobType.BACKLINKS, payload)
                logger.info("backlinks_job_submitted", job_id=job_id)

                # Poll until complete
                status_data = connector.poll_until_complete(
                    job_id=job_id,
                    poll_interval=10,
                    max_wait=1800  # 30 minutes
                )

                run_id = status_data.get("run_id")
                if not run_id:
                    raise ValueError("No run_id in completion status")

                # Fetch results
                backlinks = connector.fetch_results(run_id, "backlinks")

                backlinks_created = 0
                backlinks_updated = 0
                domains_updated = 0

                # Group by referring domain for aggregation
                domain_stats: Dict[str, Dict[str, Any]] = {}

                for bl_data in backlinks:
                    source_url = bl_data.get("source_url")
                    source_domain = _extract_domain(source_url)
                    target_url = bl_data.get("target_url")
                    anchor_text = bl_data.get("anchor_text", "")
                    is_dofollow = bl_data.get("is_dofollow", False)
                    is_inbody = bl_data.get("is_inbody", False)
                    first_seen = bl_data.get("first_seen")
                    last_seen = bl_data.get("last_seen")
                    is_lost = bl_data.get("is_lost", False)

                    # Check if backlink exists
                    existing_bl = db.query(BacklinkModel).filter_by(
                        source_url=source_url,
                        target_url=target_url
                    ).first()

                    if existing_bl:
                        # Update
                        existing_bl.last_checked = datetime.utcnow()
                        existing_bl.is_lost = is_lost
                        existing_bl.anchor_text = anchor_text
                        backlinks_updated += 1
                    else:
                        # Create
                        new_bl = BacklinkModel(
                            source_url=source_url,
                            source_domain=source_domain,
                            target_url=target_url,
                            anchor_text=anchor_text,
                            is_dofollow=is_dofollow,
                            is_inbody=is_inbody,
                            first_seen=first_seen or datetime.utcnow(),
                            last_seen=last_seen or datetime.utcnow(),
                            last_checked=datetime.utcnow(),
                            is_lost=is_lost
                        )

                        db.add(new_bl)
                        backlinks_created += 1

                    # Aggregate domain stats
                    if source_domain not in domain_stats:
                        domain_stats[source_domain] = {
                            "backlink_count": 0,
                            "inbody_link_count": 0,
                            "authority_score": bl_data.get("domain_authority", 0)
                        }

                    domain_stats[source_domain]["backlink_count"] += 1
                    if is_inbody:
                        domain_stats[source_domain]["inbody_link_count"] += 1

                db.commit()

                # Update referring domains
                for domain, stats in domain_stats.items():
                    ref_domain = db.query(ReferringDomainModel).filter_by(
                        domain=domain
                    ).first()

                    if ref_domain:
                        ref_domain.backlink_count = stats["backlink_count"]
                        ref_domain.inbody_link_count = stats["inbody_link_count"]
                        ref_domain.authority_score = stats["authority_score"]
                        ref_domain.last_updated = datetime.utcnow()
                    else:
                        ref_domain = ReferringDomainModel(
                            domain=domain,
                            backlink_count=stats["backlink_count"],
                            inbody_link_count=stats["inbody_link_count"],
                            authority_score=stats["authority_score"]
                        )
                        db.add(ref_domain)

                    domains_updated += 1

                db.commit()

                # TODO: Recalculate LAS (Link Authority Score)
                # This would be a separate calculation based on referring domain authority

                tasklog.complete_task(
                    task_id=task_id,
                    items_processed=len(backlinks),
                    items_succeeded=backlinks_created + backlinks_updated,
                    output_summary={
                        "backlinks_created": backlinks_created,
                        "backlinks_updated": backlinks_updated,
                        "domains_updated": domains_updated,
                        "run_id": run_id
                    }
                )

                logger.info(
                    "backlink_refresh_completed",
                    backlinks_created=backlinks_created,
                    backlinks_updated=backlinks_updated,
                    domains=domains_updated
                )

                return {
                    "status": "completed",
                    "backlinks_processed": len(backlinks),
                    "backlinks_created": backlinks_created,
                    "backlinks_updated": backlinks_updated,
                    "domains_updated": domains_updated
                }

            except ScrapeConnectorError as e:
                logger.error("backlinks_job_failed", error=str(e), kind=e.kind)
                db.rollback()
                raise

            except Exception as e:
                logger.error("backlink_refresh_error", error=str(e))
                db.rollback()
                raise


# ==============================================================================
# Job 4: Citations Refresh
# ==============================================================================

def run_citations_refresh(db: Session) -> Dict[str, Any]:
    """
    Refresh business citations and verify NAP consistency.

    Workflow:
    1. Submit citations job to Scrape Bot
    2. Poll until completion
    3. Upsert citations
    4. Check NAP (Name, Address, Phone) consistency
    5. Flag inconsistencies

    Args:
        db: Database session

    Returns:
        Summary dict with counts and NAP issues
    """
    tasklog = get_tasklog_service(db)

    with tasklog.advisory_lock("citations_refresh") as acquired:
        if not acquired:
            logger.warning("citations_refresh_already_running")
            return {"status": "skipped", "reason": "already_running"}

        with tasklog.task_execution(
            task_name="Citations Refresh",
            module=MODULE_NAME,
            priority=TaskPriority.LOW
        ) as task_id:

            connector = _get_scrape_connector()

            # Get expected NAP
            expected_nap = _get_expected_nap()

            # Build payload
            payload = {
                "business_name": expected_nap["name"],
                "location": expected_nap["address"],
                "phone": expected_nap["phone"]
            }

            try:
                # Submit job
                job_id = connector.submit_job(JobType.CITATIONS, payload)
                logger.info("citations_job_submitted", job_id=job_id)

                # Poll until complete
                status_data = connector.poll_until_complete(
                    job_id=job_id,
                    poll_interval=10,
                    max_wait=1200  # 20 minutes
                )

                run_id = status_data.get("run_id")
                if not run_id:
                    raise ValueError("No run_id in completion status")

                # Fetch results
                citations = connector.fetch_results(run_id, "citations")

                citations_created = 0
                citations_updated = 0
                nap_issues = 0

                for cit_data in citations:
                    platform = cit_data.get("platform")
                    listing_url = cit_data.get("listing_url")
                    name_found = cit_data.get("name_found", "")
                    address_found = cit_data.get("address_found", "")
                    phone_found = cit_data.get("phone_found", "")
                    is_listed = cit_data.get("is_listed", False)

                    # Check NAP consistency
                    name_match = _normalize_string(name_found) == _normalize_string(expected_nap["name"])
                    address_match = _normalize_string(address_found) == _normalize_string(expected_nap["address"])
                    phone_match = _normalize_phone(phone_found) == _normalize_phone(expected_nap["phone"])

                    nap_match = name_match and address_match and phone_match

                    if is_listed and not nap_match:
                        nap_issues += 1

                    # Check if citation exists
                    existing_cit = db.query(CitationModel).filter_by(
                        platform=platform
                    ).first()

                    if existing_cit:
                        # Update
                        existing_cit.listing_url = listing_url
                        existing_cit.is_listed = is_listed
                        existing_cit.name_found = name_found
                        existing_cit.address_found = address_found
                        existing_cit.phone_found = phone_found
                        existing_cit.nap_match = nap_match
                        existing_cit.last_checked = datetime.utcnow()
                        citations_updated += 1
                    else:
                        # Create
                        new_cit = CitationModel(
                            platform=platform,
                            listing_url=listing_url,
                            is_listed=is_listed,
                            name_found=name_found,
                            address_found=address_found,
                            phone_found=phone_found,
                            nap_match=nap_match,
                            first_checked=datetime.utcnow(),
                            last_checked=datetime.utcnow()
                        )

                        db.add(new_cit)
                        citations_created += 1

                db.commit()

                tasklog.complete_task(
                    task_id=task_id,
                    items_processed=len(citations),
                    items_succeeded=citations_created + citations_updated,
                    output_summary={
                        "citations_created": citations_created,
                        "citations_updated": citations_updated,
                        "nap_issues": nap_issues,
                        "run_id": run_id
                    }
                )

                logger.info(
                    "citations_refresh_completed",
                    citations_created=citations_created,
                    citations_updated=citations_updated,
                    nap_issues=nap_issues
                )

                return {
                    "status": "completed",
                    "citations_processed": len(citations),
                    "citations_created": citations_created,
                    "citations_updated": citations_updated,
                    "nap_issues": nap_issues
                }

            except ScrapeConnectorError as e:
                logger.error("citations_job_failed", error=str(e), kind=e.kind)
                db.rollback()
                raise

            except Exception as e:
                logger.error("citations_refresh_error", error=str(e))
                db.rollback()
                raise


# ==============================================================================
# Helper Functions
# ==============================================================================

def _get_scrape_connector() -> ScrapeConnector:
    """Get configured Scrape Bot connector."""
    return ScrapeConnector(
        base_url=settings.SCRAPE_BOT_BASE_URL,
        api_key=settings.SCRAPE_BOT_API_KEY,
        timeout=settings.SCRAPE_BOT_TIMEOUT,
        verify_tls=settings.SCRAPE_BOT_VERIFY_TLS,
        mtls_cert_path=settings.SCRAPE_BOT_MTLS_CERT_PATH or None,
        mtls_key_path=settings.SCRAPE_BOT_MTLS_KEY_PATH or None,
        ca_bundle_path=settings.SCRAPE_BOT_CA_BUNDLE_PATH or None
    )


def _get_embedding_service(db: Session) -> Optional[EmbeddingService]:
    """Get embedding service with Qdrant."""
    try:
        from app.services.qdrant_service import QdrantService

        # TODO: Get from config
        qdrant = QdrantService(host="localhost", port=6333)
        embedding_service = get_embedding_service(qdrant_service=qdrant)

        return embedding_service
    except Exception as e:
        logger.warning("embedding_service_init_failed", error=str(e))
        return None


def _get_our_domain() -> str:
    """Get our primary domain."""
    # TODO: Load from config or database
    return "rivercityclean.com"


def _is_our_domain(url: str) -> bool:
    """Check if URL belongs to our domain."""
    our_domain = _get_our_domain()
    return our_domain in url.lower()


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return ""


def _compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of normalized text."""
    normalized = text.lower().strip()
    normalized = " ".join(normalized.split())  # Normalize whitespace
    return hashlib.sha256(normalized.encode()).hexdigest()


def _chunk_text(text: str, max_length: int = 1000) -> List[str]:
    """
    Split text into chunks for embedding.

    Simple approach: split by double newlines (paragraphs).
    """
    if not text:
        return []

    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= max_length:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _get_expected_nap() -> Dict[str, str]:
    """Get expected NAP (Name, Address, Phone) for citations."""
    # TODO: Load from database or config
    return {
        "name": "River City Clean",
        "address": "123 Main St, River City, CA 12345",
        "phone": "(555) 123-4567"
    }


def _normalize_string(s: str) -> str:
    """Normalize string for comparison."""
    return s.lower().strip().replace("  ", " ")


def _normalize_phone(phone: str) -> str:
    """Normalize phone number for comparison."""
    # Remove all non-digits
    return "".join(c for c in phone if c.isdigit())
