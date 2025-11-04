"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Reporting & Dashboard Schemas.

Pydantic models for analytics, reports, and dashboard data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# ============================================================================
# Dashboard Response Schemas
# ============================================================================


class SalesDashboardResponse(BaseModel):
    """Sales performance dashboard metrics."""

    # Quote metrics
    total_quotes: int
    quotes_pending: int
    quotes_accepted: int
    quotes_rejected: int
    quote_acceptance_rate: float
    total_quote_value: float
    accepted_quote_value: float

    # Proposal metrics
    total_proposals: int
    proposals_sent: int
    proposals_accepted: int
    proposal_acceptance_rate: float

    # Revenue metrics
    revenue_this_month: float
    revenue_last_month: float
    revenue_growth_percent: float

    # Top performing items
    top_services: List[Dict[str, Any]] = []
    top_packages: List[Dict[str, Any]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "total_quotes": 45,
                "quotes_pending": 12,
                "quotes_accepted": 28,
                "quotes_rejected": 5,
                "quote_acceptance_rate": 62.2,
                "total_quote_value": 125000.0,
                "accepted_quote_value": 78000.0,
            }
        }


class LeadFunnelResponse(BaseModel):
    """Lead funnel and conversion metrics."""

    # Lead counts by status
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    lost_leads: int

    # Conversion rates
    contact_to_qualified_rate: float
    qualified_to_converted_rate: float
    overall_conversion_rate: float

    # Lead sources
    leads_by_source: Dict[str, int] = {}

    # Average time metrics (in days)
    avg_time_to_contact: Optional[float] = None
    avg_time_to_qualify: Optional[float] = None
    avg_time_to_convert: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_leads": 100,
                "new_leads": 15,
                "contacted_leads": 40,
                "qualified_leads": 30,
                "converted_leads": 10,
                "lost_leads": 5,
                "contact_to_qualified_rate": 75.0,
                "qualified_to_converted_rate": 33.3,
                "overall_conversion_rate": 10.0,
            }
        }


class ActivityDashboardResponse(BaseModel):
    """Activity and productivity metrics."""

    # Interaction metrics
    total_interactions: int
    interactions_this_week: int
    interactions_by_type: Dict[str, int] = {}

    # Appointment metrics
    total_appointments: int
    upcoming_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    appointment_completion_rate: float

    # Follow-up metrics
    active_followup_sequences: int
    followup_tasks_pending: int
    followup_tasks_completed: int
    followup_completion_rate: float

    # Staff activity
    most_active_users: List[Dict[str, Any]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "total_interactions": 250,
                "interactions_this_week": 45,
                "total_appointments": 30,
                "upcoming_appointments": 8,
                "completed_appointments": 20,
                "cancelled_appointments": 2,
                "appointment_completion_rate": 90.9,
            }
        }


class CommunicationDashboardResponse(BaseModel):
    """Communication channel metrics."""

    # Email metrics
    total_emails_sent: int
    emails_this_week: int
    email_response_rate: Optional[float] = None

    # SMS metrics
    total_sms_sent: int
    total_sms_received: int
    sms_this_week: int
    active_conversations: int
    avg_response_time_minutes: Optional[float] = None

    # Form submissions
    total_form_submissions: int
    submissions_this_week: int
    forms_by_template: Dict[str, int] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "total_emails_sent": 500,
                "emails_this_week": 85,
                "total_sms_sent": 120,
                "total_sms_received": 45,
                "sms_this_week": 22,
                "active_conversations": 15,
            }
        }


# ============================================================================
# Time-Series Report Schemas
# ============================================================================


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""

    date: date
    value: float
    label: Optional[str] = None

    class Config:
        from_attributes = True


class TimeSeriesReport(BaseModel):
    """Time-series data for charts."""

    metric_name: str
    period: str  # daily, weekly, monthly
    data_points: List[TimeSeriesDataPoint]
    total: float
    average: float
    trend: str  # up, down, stable

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Revenue",
                "period": "daily",
                "data_points": [
                    {"date": "2025-11-01", "value": 5000.0},
                    {"date": "2025-11-02", "value": 6200.0},
                ],
                "total": 11200.0,
                "average": 5600.0,
                "trend": "up",
            }
        }


# ============================================================================
# Custom Report Request Schemas
# ============================================================================


class ReportRequest(BaseModel):
    """Request for a custom report."""

    report_type: str = Field(..., description="Type of report to generate")
    start_date: Optional[date] = Field(None, description="Start date for report period")
    end_date: Optional[date] = Field(None, description="End date for report period")
    group_by: Optional[str] = Field(None, description="Grouping dimension (day, week, month, source, status)")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters")

    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "leads_by_source",
                "start_date": "2025-10-01",
                "end_date": "2025-10-31",
                "group_by": "source",
            }
        }


class ReportResponse(BaseModel):
    """Generic report response."""

    report_type: str
    generated_at: datetime
    period_start: Optional[date]
    period_end: Optional[date]
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ============================================================================
# Performance Metrics Schemas
# ============================================================================


class PerformanceMetricsResponse(BaseModel):
    """System and team performance metrics."""

    # Response time metrics
    avg_response_time_hours: Optional[float] = None
    median_response_time_hours: Optional[float] = None

    # Quote turnaround
    avg_quote_turnaround_days: Optional[float] = None

    # Lead velocity
    leads_per_day: float
    leads_this_month: int
    leads_last_month: int
    lead_growth_percent: float

    # Team productivity
    interactions_per_lead: float
    appointments_per_lead: float
    conversion_rate: float

    class Config:
        json_schema_extra = {
            "example": {
                "avg_response_time_hours": 2.5,
                "avg_quote_turnaround_days": 1.2,
                "leads_per_day": 3.5,
                "leads_this_month": 105,
                "leads_last_month": 88,
                "lead_growth_percent": 19.3,
                "interactions_per_lead": 4.2,
                "conversion_rate": 12.5,
            }
        }


# ============================================================================
# Export Schemas
# ============================================================================


class ExportRequest(BaseModel):
    """Request to export data."""

    export_type: str = Field(..., description="Type of data to export (leads, quotes, interactions, etc.)")
    format: str = Field("csv", description="Export format (csv, json, xlsx)")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "export_type": "leads",
                "format": "csv",
                "start_date": "2025-10-01",
                "end_date": "2025-10-31",
                "filters": {"status": "QUALIFIED"},
            }
        }
