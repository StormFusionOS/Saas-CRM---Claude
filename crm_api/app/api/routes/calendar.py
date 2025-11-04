"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Calendar Connections API Routes.

Endpoints for managing calendar integrations and syncing appointments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db import get_db, InMemoryDB
from app.schemas.calendar import (
    CalendarConnectionResponse,
    CalendarConnectionListItem,
    CalendarConnectionCreate,
    CalendarConnectionUpdate,
    CalendarEventResponse,
    CalendarEventListItem,
    SyncAppointmentRequest,
    SyncResultResponse,
)
from app.services import calendar_service
from app.api.deps import require_sales_claims
from app.models import CalendarConnection, get_next_calendar_connection_id
from datetime import datetime


router = APIRouter(tags=["calendar"])


# ============================================================================
# Calendar Connection Endpoints
# ============================================================================


@router.get("/calendar/connections", response_model=List[CalendarConnectionListItem])
def list_calendar_connections(
    is_active: Optional[bool] = None,
    provider: Optional[str] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[CalendarConnectionListItem]:
    """
    List calendar connections for current user (STAFF ONLY).

    Filters:
    - is_active: Filter by active/inactive status
    - provider: Filter by calendar provider
    """
    # In production, filter by current_user["user_id"]
    # For now, get all connections
    connections = list(db.calendar_connections.values())

    # Apply filters
    if is_active is not None:
        connections = [c for c in connections if c.is_active == is_active]

    if provider:
        connections = [c for c in connections if c.provider == provider]

    # Sort by created_at descending
    connections.sort(key=lambda c: c.created_at, reverse=True)

    return [
        CalendarConnectionListItem(
            id=conn.id,
            provider=conn.provider,
            calendar_name=conn.calendar_name,
            is_active=conn.is_active,
            sync_enabled=conn.sync_enabled,
            last_sync_at=conn.last_sync_at,
            last_sync_status=conn.last_sync_status,
            events_synced=conn.events_synced,
            created_at=conn.created_at,
        )
        for conn in connections
    ]


@router.get("/calendar/connections/{connection_id}", response_model=CalendarConnectionResponse)
def get_calendar_connection(
    connection_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> CalendarConnectionResponse:
    """
    Get calendar connection details (STAFF ONLY).
    """
    connection = db.calendar_connections.get(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar connection not found",
        )

    return CalendarConnectionResponse(
        id=connection.id,
        user_id=connection.user_id,
        provider=connection.provider,
        calendar_id=connection.calendar_id,
        calendar_name=connection.calendar_name,
        is_active=connection.is_active,
        sync_enabled=connection.sync_enabled,
        sync_direction=connection.sync_direction,
        auto_sync=connection.auto_sync,
        sync_interval_minutes=connection.sync_interval_minutes,
        last_sync_at=connection.last_sync_at,
        last_sync_status=connection.last_sync_status,
        last_sync_error=connection.last_sync_error,
        events_synced=connection.events_synced,
        sync_failures=connection.sync_failures,
        token_expires_at=connection.token_expires_at,
        metadata=connection.metadata,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
    )


@router.post("/calendar/connections", response_model=CalendarConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_connection(
    request: CalendarConnectionCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> CalendarConnectionResponse:
    """
    Create a new calendar connection (STAFF ONLY).

    NOTE: In production, this would involve OAuth 2.0 flow:
    1. User clicks "Connect Calendar"
    2. Redirect to provider (Google, Outlook, etc.)
    3. User authorizes
    4. Provider redirects back with authorization code
    5. Exchange code for access/refresh tokens
    6. Create connection with tokens
    """
    # Get user ID from token (mock: use ID 1)
    user_id = current_user.get("user_id", 1)

    connection = CalendarConnection(
        id=get_next_calendar_connection_id(),
        user_id=user_id,
        provider=request.provider,
        calendar_id=request.calendar_id,
        calendar_name=request.calendar_name,
        access_token=request.access_token,  # Would be encrypted in production
        refresh_token=request.refresh_token,
        token_expires_at=request.token_expires_at,
        is_active=True,
        sync_enabled=request.sync_enabled,
        sync_direction=request.sync_direction,
        auto_sync=request.auto_sync,
        sync_interval_minutes=request.sync_interval_minutes,
        created_at=datetime.utcnow(),
    )

    db.calendar_connections[connection.id] = connection
    db.commit()

    return CalendarConnectionResponse(**connection.__dict__)


@router.patch("/calendar/connections/{connection_id}", response_model=CalendarConnectionResponse)
def update_calendar_connection(
    connection_id: int,
    request: CalendarConnectionUpdate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> CalendarConnectionResponse:
    """
    Update calendar connection settings (STAFF ONLY).
    """
    connection = db.calendar_connections.get(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar connection not found",
        )

    # Update fields
    if request.calendar_name is not None:
        connection.calendar_name = request.calendar_name
    if request.sync_enabled is not None:
        connection.sync_enabled = request.sync_enabled
    if request.sync_direction is not None:
        connection.sync_direction = request.sync_direction
    if request.auto_sync is not None:
        connection.auto_sync = request.auto_sync
    if request.sync_interval_minutes is not None:
        connection.sync_interval_minutes = request.sync_interval_minutes

    connection.updated_at = datetime.utcnow()
    db.commit()

    return CalendarConnectionResponse(**connection.__dict__)


@router.delete("/calendar/connections/{connection_id}")
def disconnect_calendar(
    connection_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Disconnect a calendar (STAFF ONLY).

    This deactivates the connection and stops syncing.
    """
    try:
        calendar_service.disconnect_calendar(db, connection_id)
        return {"message": "Calendar disconnected successfully", "connection_id": connection_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Calendar Event Sync Endpoints
# ============================================================================


@router.post("/calendar/sync", response_model=SyncResultResponse)
def sync_appointment(
    request: SyncAppointmentRequest,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SyncResultResponse:
    """
    Sync an appointment to an external calendar (STAFF ONLY).

    If connection_id is not provided, syncs to all active connections.
    """
    try:
        # If specific connection specified, sync to that one
        if request.connection_id:
            result = calendar_service.sync_appointment_to_calendar(
                db,
                request.appointment_id,
                request.connection_id,
            )
            return SyncResultResponse(**result)

        # Otherwise, sync to all active connections
        # For now, just return error asking for specific connection
        raise ValueError("Please specify a connection_id to sync to")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/calendar/events", response_model=List[CalendarEventListItem])
def list_calendar_events(
    connection_id: Optional[int] = None,
    appointment_id: Optional[int] = None,
    sync_status: Optional[str] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[CalendarEventListItem]:
    """
    List calendar sync events (STAFF ONLY).

    Filters:
    - connection_id: Filter by calendar connection
    - appointment_id: Filter by appointment
    - sync_status: Filter by sync status
    """
    events = db.calendar_events

    # Apply filters
    if connection_id:
        events = [e for e in events if e.connection_id == connection_id]

    if appointment_id:
        events = [e for e in events if e.appointment_id == appointment_id]

    if sync_status:
        events = [e for e in events if e.sync_status == sync_status]

    # Sort by created_at descending
    events = sorted(events, key=lambda e: e.created_at, reverse=True)

    return [
        CalendarEventListItem(
            id=event.id,
            appointment_id=event.appointment_id,
            external_event_id=event.external_event_id,
            title=event.title,
            start_time=event.start_time,
            sync_status=event.sync_status,
            last_synced_at=event.last_synced_at,
        )
        for event in events
    ]
