"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Pydantic schemas for Calendar Connections.

Request/response models for calendar integration.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Calendar Connection Schemas
# ============================================================================


class CalendarConnectionResponse(BaseModel):
    """Calendar connection response."""

    id: int
    user_id: int
    provider: str
    calendar_id: str
    calendar_name: str
    is_active: bool
    sync_enabled: bool
    sync_direction: str
    auto_sync: bool
    sync_interval_minutes: int
    last_sync_at: Optional[datetime]
    last_sync_status: str
    last_sync_error: str
    events_synced: int
    sync_failures: int
    token_expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CalendarConnectionListItem(BaseModel):
    """Minimal calendar connection for list views."""

    id: int
    provider: str
    calendar_name: str
    is_active: bool
    sync_enabled: bool
    last_sync_at: Optional[datetime]
    last_sync_status: str
    events_synced: int
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarConnectionCreate(BaseModel):
    """Request to create a calendar connection."""

    provider: str = Field(..., description="Calendar provider (google, outlook, apple)")
    calendar_id: str = Field(..., description="External calendar ID")
    calendar_name: str
    access_token: str
    refresh_token: str
    token_expires_at: Optional[datetime] = None
    sync_enabled: bool = True
    sync_direction: str = "bidirectional"
    auto_sync: bool = True
    sync_interval_minutes: int = 15

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "google",
                "calendar_id": "primary",
                "calendar_name": "My Calendar",
                "access_token": "ya29.a0...",
                "refresh_token": "1//0e...",
                "sync_enabled": True,
                "sync_direction": "bidirectional",
                "auto_sync": True,
                "sync_interval_minutes": 15,
            }
        }


class CalendarConnectionUpdate(BaseModel):
    """Request to update calendar connection settings."""

    calendar_name: Optional[str] = None
    sync_enabled: Optional[bool] = None
    sync_direction: Optional[str] = None
    auto_sync: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None


# ============================================================================
# Calendar Event Schemas
# ============================================================================


class CalendarEventResponse(BaseModel):
    """Calendar event response."""

    id: int
    connection_id: int
    appointment_id: int
    external_event_id: str
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    description: str
    sync_status: str
    last_synced_at: Optional[datetime]
    sync_error: str
    attendees: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CalendarEventListItem(BaseModel):
    """Minimal calendar event for list views."""

    id: int
    appointment_id: int
    external_event_id: str
    title: str
    start_time: datetime
    sync_status: str
    last_synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class SyncAppointmentRequest(BaseModel):
    """Request to sync an appointment to calendar."""

    appointment_id: int = Field(..., description="CRM appointment to sync")
    connection_id: Optional[int] = Field(None, description="Specific connection to sync to (default: all active)")

    class Config:
        json_schema_extra = {
            "example": {
                "appointment_id": 1,
                "connection_id": 1,
            }
        }


class SyncResultResponse(BaseModel):
    """Result of a sync operation."""

    success: bool
    appointment_id: int
    connection_id: int
    external_event_id: Optional[str] = None
    message: str
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "appointment_id": 1,
                "connection_id": 1,
                "external_event_id": "google_event_123",
                "message": "Successfully synced to Google Calendar",
            }
        }
