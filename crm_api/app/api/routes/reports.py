"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Reporting & Dashboard API Routes.

Endpoints for analytics, reports, and dashboard data.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import date
from app.db import get_db, InMemoryDB
from app.schemas.reports import (
    SalesDashboardResponse,
    LeadFunnelResponse,
    ActivityDashboardResponse,
    CommunicationDashboardResponse,
    PerformanceMetricsResponse,
    TimeSeriesReport,
    ReportRequest,
    ReportResponse,
)
from app.services import reports_service
from app.api.deps import require_sales_claims


router = APIRouter(tags=["reports"])


# ============================================================================
# Dashboard Endpoints
# ============================================================================


@router.get("/reports/dashboard/sales", response_model=SalesDashboardResponse)
def get_sales_dashboard(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SalesDashboardResponse:
    """
    Get sales performance dashboard (STAFF ONLY).

    Returns comprehensive sales metrics including:
    - Quote statistics and acceptance rates
    - Proposal metrics
    - Revenue tracking and growth
    - Top performing services and packages
    """
    data = reports_service.get_sales_dashboard(db)
    return SalesDashboardResponse(**data)


@router.get("/reports/dashboard/leads", response_model=LeadFunnelResponse)
def get_lead_funnel_dashboard(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> LeadFunnelResponse:
    """
    Get lead funnel and conversion dashboard (STAFF ONLY).

    Returns lead pipeline metrics including:
    - Lead counts by status
    - Conversion rates at each stage
    - Lead source breakdown
    - Average time metrics
    """
    data = reports_service.get_lead_funnel(db)
    return LeadFunnelResponse(**data)


@router.get("/reports/dashboard/activity", response_model=ActivityDashboardResponse)
def get_activity_dashboard(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> ActivityDashboardResponse:
    """
    Get activity and productivity dashboard (STAFF ONLY).

    Returns activity metrics including:
    - Interaction statistics
    - Appointment tracking
    - Follow-up automation progress
    - Staff activity leaderboard
    """
    data = reports_service.get_activity_dashboard(db)
    return ActivityDashboardResponse(**data)


@router.get("/reports/dashboard/communication", response_model=CommunicationDashboardResponse)
def get_communication_dashboard(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> CommunicationDashboardResponse:
    """
    Get communication channels dashboard (STAFF ONLY).

    Returns communication metrics including:
    - Email activity and response rates
    - SMS messaging statistics
    - Form submission tracking
    - Channel performance comparison
    """
    data = reports_service.get_communication_dashboard(db)
    return CommunicationDashboardResponse(**data)


@router.get("/reports/dashboard/performance", response_model=PerformanceMetricsResponse)
def get_performance_metrics(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PerformanceMetricsResponse:
    """
    Get system and team performance metrics (STAFF ONLY).

    Returns performance indicators including:
    - Response time statistics
    - Quote turnaround time
    - Lead velocity and growth
    - Team productivity metrics
    """
    data = reports_service.get_performance_metrics(db)
    return PerformanceMetricsResponse(**data)


# ============================================================================
# Time-Series Report Endpoints
# ============================================================================


@router.get("/reports/timeseries/{metric_name}", response_model=TimeSeriesReport)
def get_time_series_report(
    metric_name: str,
    start_date: Optional[date] = Query(None, description="Start date for report period"),
    end_date: Optional[date] = Query(None, description="End date for report period"),
    period: str = Query("daily", description="Grouping period: daily, weekly, monthly"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> TimeSeriesReport:
    """
    Get time-series data for a specific metric (STAFF ONLY).

    Available metrics:
    - revenue: Revenue over time
    - leads: Lead count over time
    - quotes: Quote count over time
    - interactions: Interaction count over time
    - appointments: Appointment count over time

    Returns data points suitable for line charts and trend analysis.
    """
    valid_metrics = ["revenue", "leads", "quotes", "interactions", "appointments"]
    if metric_name not in valid_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metric name. Must be one of: {', '.join(valid_metrics)}",
        )

    valid_periods = ["daily", "weekly", "monthly"]
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}",
        )

    data = reports_service.get_time_series_report(
        db,
        metric_name=metric_name,
        start_date=start_date,
        end_date=end_date,
        period=period,
    )

    return TimeSeriesReport(**data)


# ============================================================================
# Summary Endpoints
# ============================================================================


@router.get("/reports/summary")
def get_summary_dashboard(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Get high-level summary of all key metrics (STAFF ONLY).

    Returns a combined view of the most important metrics across all dashboards.
    Useful for executive overview or mobile summary view.
    """
    sales = reports_service.get_sales_dashboard(db)
    leads = reports_service.get_lead_funnel(db)
    activity = reports_service.get_activity_dashboard(db)
    performance = reports_service.get_performance_metrics(db)

    return {
        "summary": {
            # Key sales metrics
            "total_revenue": sales["accepted_quote_value"],
            "revenue_growth": sales["revenue_growth_percent"],
            "quote_acceptance_rate": sales["quote_acceptance_rate"],

            # Key lead metrics
            "total_leads": leads["total_leads"],
            "conversion_rate": leads["overall_conversion_rate"],
            "new_leads": leads["new_leads"],

            # Key activity metrics
            "interactions_this_week": activity["interactions_this_week"],
            "upcoming_appointments": activity["upcoming_appointments"],
            "followup_completion_rate": activity["followup_completion_rate"],

            # Key performance metrics
            "leads_per_day": performance["leads_per_day"],
            "lead_growth_percent": performance["lead_growth_percent"],
        },
        "generated_at": "now",
    }


# ============================================================================
# Quick Stats Endpoints
# ============================================================================


@router.get("/reports/quick-stats")
def get_quick_stats(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Get quick statistics for dashboard header/cards (STAFF ONLY).

    Returns simple count metrics for rapid loading.
    """
    leads = db.leads  # List
    quotes = db.quotes  # List
    appointments = db.appointments  # List
    interactions = db.interactions  # List

    return {
        "total_leads": len(leads),
        "total_quotes": len(quotes),
        "total_appointments": len(appointments),
        "total_interactions": len(interactions),
        "active_followups": sum(1 for seq in db.followup_sequences.values() if seq.is_active),
        "active_sms_conversations": sum(1 for conv in db.sms_conversations.values() if conv.status == "active"),
    }


# ============================================================================
# Export Endpoints (Placeholder)
# ============================================================================


@router.post("/reports/export")
def export_data(
    export_type: str = Query(..., description="Type of data to export"),
    format: str = Query("csv", description="Export format"),
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Export CRM data to CSV/JSON/Excel (STAFF ONLY).

    NOTE: This is a placeholder. In production, this would:
    1. Generate the requested export file
    2. Return a download URL or stream the file
    3. Support various formats (CSV, JSON, XLSX)
    4. Apply filters and date ranges
    5. Handle large datasets with pagination/streaming

    Available export types:
    - leads
    - quotes
    - interactions
    - appointments
    - contacts
    """
    valid_export_types = ["leads", "quotes", "interactions", "appointments", "contacts"]
    if export_type not in valid_export_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid export type. Must be one of: {', '.join(valid_export_types)}",
        )

    valid_formats = ["csv", "json", "xlsx"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}",
        )

    # Mock response
    return {
        "message": f"Export of {export_type} as {format} would be generated here",
        "export_type": export_type,
        "format": format,
        "note": "In production, this would return a downloadable file or URL",
    }
