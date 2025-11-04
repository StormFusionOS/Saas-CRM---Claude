"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Pydantic schemas for Scheduling System.

Request/response models for availability and appointment APIs.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Availability Schemas
# ============================================================================


class AvailabilitySlot(BaseModel):
    """A single available time slot."""

    start: datetime = Field(..., description="Slot start time")
    end: datetime = Field(..., description="Slot end time")
    duration_minutes: int = Field(..., description="Duration in minutes")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")


class AvailabilityResponse(BaseModel):
    """Available time slots for booking."""

    quote_id: int
    available_dates: List[str] = Field(..., description="List of available dates (YYYY-MM-DD)")
    slots: List[AvailabilitySlot] = Field(..., description="Available time slots")
    timezone: str = Field(default="UTC", description="Timezone for times")
    min_notice_hours: int = Field(..., description="Minimum hours notice required")
    max_days_advance: int = Field(..., description="Maximum days in advance to book")


# ============================================================================
# Appointment Booking Schemas
# ============================================================================


class AppointmentBookingRequest(BaseModel):
    """Request to book an appointment."""

    quote_id: int = Field(..., description="Quote ID for the appointment")
    scheduled_start: datetime = Field(..., description="Desired appointment start time")
    customer_name: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    address: str = Field(..., min_length=5, max_length=500, description="Service address")
    special_instructions: str = Field(default="", max_length=1000, description="Special instructions")

    class Config:
        json_schema_extra = {
            "example": {
                "quote_id": 1,
                "scheduled_start": "2025-12-01T10:00:00Z",
                "customer_name": "John Smith",
                "customer_email": "john@example.com",
                "customer_phone": "555-123-4567",
                "address": "123 Main St, Springfield, IL 62701",
                "special_instructions": "Please call when arriving"
            }
        }


class AppointmentResponse(BaseModel):
    """Appointment booking response."""

    id: int
    quote_id: int
    contact_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    duration_minutes: int
    status: str
    customer_name: str
    customer_email: Optional[str]
    customer_phone: Optional[str]
    address: str
    special_instructions: str
    service_description: str
    created_at: datetime
    message: str = Field(..., description="Confirmation message")

    class Config:
        from_attributes = True


class AppointmentListItem(BaseModel):
    """Minimal appointment model for list views."""

    id: int
    quote_id: int
    contact_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    status: str
    customer_name: str
    service_description: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Availability Config Schemas (Admin)
# ============================================================================


class AvailabilityConfigResponse(BaseModel):
    """Availability configuration response."""

    id: int
    name: str
    start_time: str
    end_time: str
    working_days: List[int]
    slot_duration_minutes: int
    buffer_minutes: int
    max_appointments_per_day: int
    min_notice_hours: int
    max_days_advance: int
    blackout_dates: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AvailabilityConfigUpdate(BaseModel):
    """Update availability configuration."""

    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    working_days: Optional[List[int]] = None
    slot_duration_minutes: Optional[int] = None
    buffer_minutes: Optional[int] = None
    max_appointments_per_day: Optional[int] = None
    min_notice_hours: Optional[int] = None
    max_days_advance: Optional[int] = None
    blackout_dates: Optional[List[str]] = None
    is_active: Optional[bool] = None
