"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

SEO Meta Optimization Job
Scheduled job to analyze pages and generate meta tag optimizations
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
import structlog

from app.services.ai_modules.seo_meta_optimizer import get_seo_meta_optimizer
from app.services.wordpress_service import wordpress_service
from app.api.routes.governance import create_task_log, update_task_log
from app.schemas.governance import TaskLogCreate, TaskLogUpdate

logger = structlog.get_logger()


class SEOMetaOptimizationJob:
    """
    Scheduled job: SEO Meta Tag Optimization

    Analyzes WordPress pages and generates optimized meta tag suggestions.
    """

    JOB_NAME = "seo_meta_optimizer"

    def __init__(self):
        self.logger = logger.bind(job=self.JOB_NAME)

    async def run(
        self,
        limit: int = 10,
        triggered_by: str = "scheduler"
    ) -> Dict[str, Any]:
        """
        Run SEO meta optimization job.

        Args:
            limit: Number of pages to analyze
            triggered_by: Trigger source (scheduler, manual, webhook)

        Returns:
            Job execution results
        """
        job_id = f"{self.JOB_NAME}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        self.logger.info("job_started", job_id=job_id, limit=limit)

        # Create task log entry
        task_log = TaskLogCreate(
            job_name=self.JOB_NAME,
            job_id=job_id,
            triggered_by=triggered_by,
            inputs={"limit": limit}
        )
        create_task_log(task_log)

        try:
            # Fetch pages from WordPress
            pages = await wordpress_service.get_pages(limit=limit, orderby="modified")

            self.logger.info("pages_fetched", count=len(pages))

            # Analyze each page
            results = []
            changes_generated = 0
            errors_count = 0

            for page in pages:
                try:
                    # Get primary keyword
                    primary_keyword = await wordpress_service.get_page_primary_keyword(page["id"])

                    # Analyze page
                    result = await get_seo_meta_optimizer().analyze_page(
                        page_id=page["id"],
                        page_url=page["url"],
                        page_content=page["content"],
                        current_title=page.get("meta_title", page["title"]),
                        current_description=page.get("meta_description", ""),
                        primary_keyword=primary_keyword,
                        secondary_keywords=[]  # TODO: Extract from content
                    )

                    if result["success"]:
                        changes_generated += 1
                        results.append({
                            "page_id": page["id"],
                            "change_id": result["change_id"],
                            "confidence": result["optimization"]["confidence"]
                        })
                    else:
                        errors_count += 1
                        results.append({
                            "page_id": page["id"],
                            "error": result["error"]
                        })

                except Exception as e:
                    self.logger.error(
                        "page_analysis_error",
                        page_id=page["id"],
                        error=str(e),
                        exc_info=True
                    )
                    errors_count += 1
                    results.append({
                        "page_id": page["id"],
                        "error": str(e)
                    })

            # Update task log with results
            update_data = TaskLogUpdate(
                status="completed",
                outputs={"results": results},
                records_processed=len(pages),
                changes_generated=changes_generated,
                errors_count=errors_count
            )
            update_task_log(job_id, update_data)

            self.logger.info(
                "job_completed",
                job_id=job_id,
                pages_processed=len(pages),
                changes_generated=changes_generated,
                errors=errors_count
            )

            return {
                "job_id": job_id,
                "status": "completed",
                "pages_processed": len(pages),
                "changes_generated": changes_generated,
                "errors_count": errors_count,
                "results": results
            }

        except Exception as e:
            self.logger.error(
                "job_failed",
                job_id=job_id,
                error=str(e),
                exc_info=True
            )

            # Update task log with failure
            update_data = TaskLogUpdate(
                status="failed",
                error_message=str(e),
                errors_count=1
            )
            update_task_log(job_id, update_data)

            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }


# Global instance
seo_meta_job = SEOMetaOptimizationJob()


# Async entry point for scheduler
async def run_seo_meta_optimization(limit: int = 10, triggered_by: str = "scheduler"):
    """Entry point for running SEO meta optimization job."""
    return await seo_meta_job.run(limit=limit, triggered_by=triggered_by)
