"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Celery configuration for AI automation tasks.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Celery app instance
celery_app = Celery(
    "crm_ai_suite",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time for memory efficiency
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
)

# Auto-discover tasks in app/tasks/ directory
celery_app.autodiscover_tasks(["app.tasks"])

# Beat schedule for periodic tasks (Step 07-12 automation jobs)
celery_app.conf.beat_schedule = {
    # Daily SERP position scraping (Step 07)
    "serp-position-scraper": {
        "task": "app.tasks.serp.scrape_serp_positions",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM UTC
    },
    
    # Daily anomaly detection (Step 08)
    "anomaly-analyzer": {
        "task": "app.tasks.anomaly.detect_anomalies",
        "schedule": crontab(hour=5, minute=0),  # Daily at 5 AM UTC (after SERP scrape)
    },
    
    # Weekly CTR optimizer (Step 09)
    "ctr-optimizer": {
        "task": "app.tasks.ctr.optimize_meta_tags",
        "schedule": crontab(day_of_week=1, hour=6, minute=0),  # Mondays at 6 AM UTC
    },
    
    # Monthly content cluster builder (Step 10)
    "content-cluster-builder": {
        "task": "app.tasks.clusters.build_content_clusters",
        "schedule": crontab(day_of_month=1, hour=7, minute=0),  # 1st of month at 7 AM UTC
    },
    
    # Weekly backlink discovery (Step 11)
    "backlink-discovery": {
        "task": "app.tasks.backlinks.discover_backlinks",
        "schedule": crontab(day_of_week=0, hour=4, minute=0),  # Sundays at 4 AM UTC
    },
    
    # Daily schema generator (Step 09)
    "schema-generator": {
        "task": "app.tasks.schema.generate_schemas",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8 AM UTC
    },
    
    # Auto-revert monitoring (Step 16) - runs every 6 hours
    "auto-revert-monitor": {
        "task": "app.tasks.governance.monitor_recent_auto_changes",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    
    # Hourly materialized view refresh
    "refresh-materialized-views": {
        "task": "app.tasks.maintenance.refresh_views",
        "schedule": crontab(minute=0),  # Every hour
    },
    
    # Health monitoring - every 5 minutes
    "health-monitor": {
        "task": "app.tasks.maintenance.check_system_health",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
}

# Task routing - route specific tasks to specific queues
celery_app.conf.task_routes = {
    "app.tasks.serp.*": {"queue": "serp"},
    "app.tasks.anomaly.*": {"queue": "ai"},
    "app.tasks.ctr.*": {"queue": "ai"},
    "app.tasks.clusters.*": {"queue": "ai"},
    "app.tasks.backlinks.*": {"queue": "scraper"},
    "app.tasks.schema.*": {"queue": "ai"},
    "app.tasks.governance.*": {"queue": "governance"},
    "app.tasks.maintenance.*": {"queue": "default"},
}

# Default queue
celery_app.conf.task_default_queue = "default"
