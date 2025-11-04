"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Calendar Service - Sync appointments to external calendars.

NOTE: This is a mock implementation for demo purposes.
In production, this would integrate with actual calendar APIs
(Google Calendar API, Microsoft Graph API, etc.) using OAuth 2.0.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from app.db import InMemoryDB
from app.models import CalendarEvent, get_next_calendar_event_id


def sync_appointment_to_calendar(
    db: InMemoryDB,
    appointment_id: int,
    connection_id: int,
) -> Dict[str, Any]:
    """
    Sync a CRM appointment to an external calendar.

    In production, this would:
    1. Get the appointment details
    2. Authenticate with the calendar provider using OAuth tokens
    3. Create or update the event in the external calendar
    4. Store the sync record

    Args:
        db: Database session
        appointment_id: CRM appointment to sync
        connection_id: Calendar connection to sync to

    Returns:
        Dict with sync result

    Raises:
        ValueError: If connection or appointment not found
    """
    # Get calendar connection
    connection = db.calendar_connections.get(connection_id)
    if not connection:
        raise ValueError(f"Calendar connection {connection_id} not found")

    if not connection.is_active or not connection.sync_enabled:
        raise ValueError(f"Calendar connection {connection_id} is not active or sync is disabled")

    # Get appointment
    appointment = next((a for a in db.appointments if a.id == appointment_id), None)
    if not appointment:
        raise ValueError(f"Appointment {appointment_id} not found")

    # Check if already synced
    existing_event = next(
        (e for e in db.calendar_events
         if e.appointment_id == appointment_id and e.connection_id == connection_id),
        None
    )

    if existing_event:
        # Update existing event
        existing_event.title = f"Appointment #{appointment.id} - {appointment.service_type}"
        existing_event.start_time = appointment.scheduled_start
        existing_event.end_time = appointment.scheduled_end
        existing_event.sync_status = "synced"
        existing_event.last_synced_at = datetime.utcnow()
        existing_event.updated_at = datetime.utcnow()

        result = {
            "success": True,
            "appointment_id": appointment_id,
            "connection_id": connection_id,
            "external_event_id": existing_event.external_event_id,
            "message": f"Successfully updated event in {connection.provider} calendar",
            "action": "updated",
        }
    else:
        # Create new event
        # In production, this would call the external calendar API
        mock_external_id = f"{connection.provider}_event_{appointment_id}_{datetime.utcnow().timestamp()}"

        new_event = CalendarEvent(
            id=get_next_calendar_event_id(),
            connection_id=connection_id,
            appointment_id=appointment_id,
            external_event_id=mock_external_id,
            title=f"Appointment #{appointment.id} - {appointment.service_type}",
            start_time=appointment.scheduled_start,
            end_time=appointment.scheduled_end,
            location=appointment.location or "",
            description=f"CRM Appointment #{appointment.id}\nContact: {appointment.contact_id}\nLead: {appointment.lead_id}",
            sync_status="synced",
            last_synced_at=datetime.utcnow(),
            attendees=[],
            created_at=datetime.utcnow(),
        )

        db.calendar_events.append(new_event)

        result = {
            "success": True,
            "appointment_id": appointment_id,
            "connection_id": connection_id,
            "external_event_id": mock_external_id,
            "message": f"Successfully synced to {connection.provider} calendar",
            "action": "created",
        }

    # Update connection stats
    connection.events_synced += 1
    connection.last_sync_at = datetime.utcnow()
    connection.last_sync_status = "success"
    connection.updated_at = datetime.utcnow()

    db.commit()

    return result


def disconnect_calendar(
    db: InMemoryDB,
    connection_id: int,
) -> None:
    """
    Disconnect a calendar connection.

    Args:
        db: Database session
        connection_id: Connection to disconnect

    Raises:
        ValueError: If connection not found
    """
    connection = db.calendar_connections.get(connection_id)
    if not connection:
        raise ValueError(f"Calendar connection {connection_id} not found")

    connection.is_active = False
    connection.sync_enabled = False
    connection.updated_at = datetime.utcnow()

    db.commit()


def get_calendar_availability(
    db: InMemoryDB,
    connection_id: int,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    """
    Check calendar availability for a date range.

    In production, this would query the external calendar API
    to find free/busy time slots.

    Args:
        db: Database session
        connection_id: Calendar to check
        start_date: Start of date range
        end_date: End of date range

    Returns:
        Dict with availability information

    Raises:
        ValueError: If connection not found
    """
    connection = db.calendar_connections.get(connection_id)
    if not connection:
        raise ValueError(f"Calendar connection {connection_id} not found")

    # Mock availability check
    # In production, this would call the calendar API
    return {
        "connection_id": connection_id,
        "calendar_name": connection.calendar_name,
        "provider": connection.provider,
        "start_date": start_date,
        "end_date": end_date,
        "busy_slots": [
            # Mock busy times
            {
                "start": start_date.replace(hour=10, minute=0),
                "end": start_date.replace(hour=11, minute=0),
            },
            {
                "start": start_date.replace(hour=14, minute=0),
                "end": start_date.replace(hour=15, minute=30),
            },
        ],
        "message": "Mock availability data - in production, this would query the external calendar API",
    }
