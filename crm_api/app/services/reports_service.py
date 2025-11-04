"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Reports Service - Generate analytics and dashboard data.

This service calculates metrics and generates reports from CRM data.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict
from app.db import InMemoryDB
from app.models import LeadStatus, QuoteStatus


def get_sales_dashboard(db: InMemoryDB) -> Dict[str, Any]:
    """
    Generate sales dashboard metrics.

    Returns:
        Dict with quote, proposal, and revenue metrics
    """
    quotes = db.quotes  # List, not dict
    proposals = list(db.proposal_templates.values())

    # Quote metrics
    total_quotes = len(quotes)
    quotes_pending = sum(1 for q in quotes if q.status == QuoteStatus.DRAFT or q.status == QuoteStatus.SENT)
    quotes_accepted = sum(1 for q in quotes if q.status == QuoteStatus.ACCEPTED)
    quotes_rejected = sum(1 for q in quotes if q.status == QuoteStatus.REJECTED)

    quote_acceptance_rate = (quotes_accepted / total_quotes * 100) if total_quotes > 0 else 0.0

    total_quote_value = sum(q.total for q in quotes)
    accepted_quote_value = sum(q.total for q in quotes if q.status == QuoteStatus.ACCEPTED)

    # Proposal metrics
    total_proposals = len(proposals)
    proposals_sent = sum(1 for p in proposals if p.is_active)
    # Note: ProposalTemplate doesn't track usage, so we mock the acceptance metric
    proposals_accepted = proposals_sent  # Simplified: assume active templates are "accepted"
    proposal_acceptance_rate = (proposals_accepted / total_proposals * 100) if total_proposals > 0 else 0.0

    # Revenue metrics (based on accepted quotes)
    now = datetime.utcnow()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    revenue_this_month = sum(
        q.total for q in quotes
        if q.status == QuoteStatus.ACCEPTED and q.created_at >= this_month_start
    )

    revenue_last_month = sum(
        q.total for q in quotes
        if q.status == QuoteStatus.ACCEPTED
        and q.created_at >= last_month_start
        and q.created_at < this_month_start
    )

    revenue_growth_percent = 0.0
    if revenue_last_month > 0:
        revenue_growth_percent = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100

    # Top services (from quote items)
    service_revenue = defaultdict(float)
    service_count = defaultdict(int)

    for quote in quotes:
        if quote.status == QuoteStatus.ACCEPTED:
            for item in quote.items:
                # Mock service name (in production would join with pricebook)
                service_name = f"Service #{item.pricebook_item_id}"
                service_revenue[service_name] += item.total
                service_count[service_name] += 1

    top_services = [
        {"name": name, "revenue": revenue, "count": service_count[name]}
        for name, revenue in sorted(service_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # Top packages (if any)
    packages = list(db.packages.values())
    top_packages = [
        {"id": p.id, "name": p.name, "times_sold": p.times_sold}
        for p in sorted(packages, key=lambda p: p.times_sold, reverse=True)[:5]
    ]

    return {
        "total_quotes": total_quotes,
        "quotes_pending": quotes_pending,
        "quotes_accepted": quotes_accepted,
        "quotes_rejected": quotes_rejected,
        "quote_acceptance_rate": round(quote_acceptance_rate, 1),
        "total_quote_value": round(total_quote_value, 2),
        "accepted_quote_value": round(accepted_quote_value, 2),
        "total_proposals": total_proposals,
        "proposals_sent": proposals_sent,
        "proposals_accepted": proposals_accepted,
        "proposal_acceptance_rate": round(proposal_acceptance_rate, 1),
        "revenue_this_month": round(revenue_this_month, 2),
        "revenue_last_month": round(revenue_last_month, 2),
        "revenue_growth_percent": round(revenue_growth_percent, 1),
        "top_services": top_services,
        "top_packages": top_packages,
    }


def get_lead_funnel(db: InMemoryDB) -> Dict[str, Any]:
    """
    Generate lead funnel and conversion metrics.

    Returns:
        Dict with lead counts, conversion rates, and source breakdown
    """
    leads = db.leads

    # Lead counts by status
    total_leads = len(leads)
    new_leads = sum(1 for l in leads if l.status == LeadStatus.NEW)
    contacted_leads = sum(1 for l in leads if l.status == LeadStatus.CONTACTED)
    qualified_leads = sum(1 for l in leads if l.status == LeadStatus.QUOTED)  # QUOTED, not QUALIFIED
    converted_leads = sum(1 for l in leads if l.status == LeadStatus.WON)  # WON, not CONVERTED
    lost_leads = sum(1 for l in leads if l.status == LeadStatus.LOST)

    # Conversion rates
    contact_to_qualified_rate = 0.0
    if contacted_leads + qualified_leads + converted_leads > 0:
        contact_to_qualified_rate = ((qualified_leads + converted_leads) / (contacted_leads + qualified_leads + converted_leads)) * 100

    qualified_to_converted_rate = 0.0
    if qualified_leads + converted_leads > 0:
        qualified_to_converted_rate = (converted_leads / (qualified_leads + converted_leads)) * 100

    overall_conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0

    # Lead sources
    leads_by_source = Counter(l.source for l in leads)

    # Average time metrics (mock calculation)
    avg_time_to_contact = None  # Would calculate from interaction timestamps
    avg_time_to_qualify = None  # Would calculate from status change history
    avg_time_to_convert = None  # Would calculate from status change history

    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "contacted_leads": contacted_leads,
        "qualified_leads": qualified_leads,
        "converted_leads": converted_leads,
        "lost_leads": lost_leads,
        "contact_to_qualified_rate": round(contact_to_qualified_rate, 1),
        "qualified_to_converted_rate": round(qualified_to_converted_rate, 1),
        "overall_conversion_rate": round(overall_conversion_rate, 1),
        "leads_by_source": dict(leads_by_source),
        "avg_time_to_contact": avg_time_to_contact,
        "avg_time_to_qualify": avg_time_to_qualify,
        "avg_time_to_convert": avg_time_to_convert,
    }


def get_activity_dashboard(db: InMemoryDB) -> Dict[str, Any]:
    """
    Generate activity and productivity metrics.

    Returns:
        Dict with interaction, appointment, and follow-up metrics
    """
    interactions = db.interactions
    appointments = db.appointments
    followup_sequences = list(db.followup_sequences.values())
    followup_tasks = db.followup_tasks

    # Interaction metrics
    total_interactions = len(interactions)
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    interactions_this_week = sum(1 for i in interactions if i.created_at >= week_ago)

    interactions_by_type = Counter(i.type for i in interactions)

    # Appointment metrics
    total_appointments = len(appointments)
    upcoming_appointments = sum(1 for a in appointments if a.scheduled_start > now and a.status == "scheduled")
    completed_appointments = sum(1 for a in appointments if a.status == "completed")
    cancelled_appointments = sum(1 for a in appointments if a.status == "cancelled")

    appointment_completion_rate = 0.0
    if completed_appointments + cancelled_appointments > 0:
        appointment_completion_rate = (completed_appointments / (completed_appointments + cancelled_appointments)) * 100

    # Follow-up metrics
    active_followup_sequences = sum(1 for seq in followup_sequences if seq.is_active)
    followup_tasks_pending = sum(1 for t in followup_tasks if t.status == "pending")
    followup_tasks_completed = sum(1 for t in followup_tasks if t.status == "completed")

    followup_completion_rate = 0.0
    if followup_tasks_pending + followup_tasks_completed > 0:
        followup_completion_rate = (followup_tasks_completed / (followup_tasks_pending + followup_tasks_completed)) * 100

    # Most active users (based on interactions created)
    user_activity = Counter(i.created_by for i in interactions if i.created_by)
    most_active_users = [
        {"user_id": user_id, "interaction_count": count}
        for user_id, count in user_activity.most_common(5)
    ]

    return {
        "total_interactions": total_interactions,
        "interactions_this_week": interactions_this_week,
        "interactions_by_type": dict(interactions_by_type),
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "appointment_completion_rate": round(appointment_completion_rate, 1),
        "active_followup_sequences": active_followup_sequences,
        "followup_tasks_pending": followup_tasks_pending,
        "followup_tasks_completed": followup_tasks_completed,
        "followup_completion_rate": round(followup_completion_rate, 1),
        "most_active_users": most_active_users,
    }


def get_communication_dashboard(db: InMemoryDB) -> Dict[str, Any]:
    """
    Generate communication channel metrics.

    Returns:
        Dict with email, SMS, and form submission metrics
    """
    interactions = db.interactions
    sms_messages = db.sms_messages
    sms_conversations = list(db.sms_conversations.values())
    form_submissions = db.form_submissions

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    # Email metrics (from interactions)
    email_interactions = [i for i in interactions if i.type == "EMAIL"]
    total_emails_sent = len(email_interactions)
    emails_this_week = sum(1 for i in email_interactions if i.created_at >= week_ago)

    # Mock email response rate
    email_response_rate = None

    # SMS metrics
    sms_sent = [m for m in sms_messages if m.direction == "outbound"]
    sms_received = [m for m in sms_messages if m.direction == "inbound"]

    total_sms_sent = len(sms_sent)
    total_sms_received = len(sms_received)
    sms_this_week = sum(1 for m in sms_messages if m.created_at >= week_ago)

    active_conversations = sum(1 for c in sms_conversations if c.status == "active")

    # Mock average response time
    avg_response_time_minutes = None

    # Form submissions
    total_form_submissions = len(form_submissions)
    submissions_this_week = sum(1 for s in form_submissions if s.submitted_at >= week_ago)

    forms_by_template = Counter(s.template_id for s in form_submissions)

    return {
        "total_emails_sent": total_emails_sent,
        "emails_this_week": emails_this_week,
        "email_response_rate": email_response_rate,
        "total_sms_sent": total_sms_sent,
        "total_sms_received": total_sms_received,
        "sms_this_week": sms_this_week,
        "active_conversations": active_conversations,
        "avg_response_time_minutes": avg_response_time_minutes,
        "total_form_submissions": total_form_submissions,
        "submissions_this_week": submissions_this_week,
        "forms_by_template": {f"Template {k}": v for k, v in forms_by_template.items()},
    }


def get_performance_metrics(db: InMemoryDB) -> Dict[str, Any]:
    """
    Generate system and team performance metrics.

    Returns:
        Dict with response time, velocity, and productivity metrics
    """
    leads = db.leads
    interactions = db.interactions
    quotes = db.quotes  # List, not dict

    # Mock response time metrics (would calculate from interaction timestamps)
    avg_response_time_hours = None
    median_response_time_hours = None

    # Mock quote turnaround time
    avg_quote_turnaround_days = None

    # Lead velocity
    now = datetime.utcnow()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    leads_this_month = sum(1 for l in leads if l.created_at >= this_month_start)
    leads_last_month = sum(
        1 for l in leads
        if l.created_at >= last_month_start and l.created_at < this_month_start
    )

    days_this_month = (now - this_month_start).days + 1
    leads_per_day = leads_this_month / days_this_month if days_this_month > 0 else 0.0

    lead_growth_percent = 0.0
    if leads_last_month > 0:
        lead_growth_percent = ((leads_this_month - leads_last_month) / leads_last_month) * 100

    # Team productivity
    total_leads = len(leads)
    total_interactions = len(interactions)
    total_appointments = len(db.appointments)

    interactions_per_lead = total_interactions / total_leads if total_leads > 0 else 0.0
    appointments_per_lead = total_appointments / total_leads if total_leads > 0 else 0.0

    converted_leads = sum(1 for l in leads if l.status == LeadStatus.WON)  # WON, not CONVERTED
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0

    return {
        "avg_response_time_hours": avg_response_time_hours,
        "median_response_time_hours": median_response_time_hours,
        "avg_quote_turnaround_days": avg_quote_turnaround_days,
        "leads_per_day": round(leads_per_day, 1),
        "leads_this_month": leads_this_month,
        "leads_last_month": leads_last_month,
        "lead_growth_percent": round(lead_growth_percent, 1),
        "interactions_per_lead": round(interactions_per_lead, 1),
        "appointments_per_lead": round(appointments_per_lead, 2),
        "conversion_rate": round(conversion_rate, 1),
    }


def get_time_series_report(
    db: InMemoryDB,
    metric_name: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    period: str = "daily",
) -> Dict[str, Any]:
    """
    Generate time-series data for a specific metric.

    Args:
        db: Database session
        metric_name: Name of metric to track (revenue, leads, interactions, etc.)
        start_date: Start of period
        end_date: End of period
        period: Grouping period (daily, weekly, monthly)

    Returns:
        Dict with time-series data points
    """
    # Set defaults for date range
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Mock implementation - would calculate actual data points
    data_points = [
        {"date": start_date, "value": 1000.0, "label": None},
        {"date": start_date + timedelta(days=10), "value": 1500.0, "label": None},
        {"date": start_date + timedelta(days=20), "value": 1800.0, "label": None},
        {"date": end_date, "value": 2200.0, "label": None},
    ]

    total = sum(p["value"] for p in data_points)
    average = total / len(data_points) if data_points else 0.0

    # Determine trend
    if len(data_points) >= 2:
        first_half_avg = sum(p["value"] for p in data_points[:len(data_points)//2]) / (len(data_points)//2)
        second_half_avg = sum(p["value"] for p in data_points[len(data_points)//2:]) / (len(data_points) - len(data_points)//2)

        if second_half_avg > first_half_avg * 1.1:
            trend = "up"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return {
        "metric_name": metric_name,
        "period": period,
        "data_points": data_points,
        "total": round(total, 2),
        "average": round(average, 2),
        "trend": trend,
    }
