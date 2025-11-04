"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Scheduling API Routes - Customer self-scheduling.

Public endpoints for viewing availability and booking appointments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.db import get_db, InMemoryDB
from app.schemas.scheduling import (
    AvailabilityResponse,
    AppointmentBookingRequest,
    AppointmentResponse,
    AvailabilitySlot,
)
from app.services import scheduling_service


router = APIRouter(tags=["scheduling"])


@router.get("/scheduling/{quote_id}/availability", response_model=AvailabilityResponse)
def get_availability(
    quote_id: int,
    days: int = 14,
    db: InMemoryDB = Depends(get_db),
) -> AvailabilityResponse:
    """
    Get available time slots for booking (PUBLIC - no auth required).

    Customers can view available appointment times for their accepted quote.

    Args:
        quote_id: Quote ID
        days: Number of days to show (default 14, max 60)
        db: Database session

    Returns:
        Available dates and time slots

    Raises:
        HTTPException: 404 if quote not found
    """
    from app.models import Quote

    # Verify quote exists and is accepted
    quote = db.query(Quote).filter_by(id=quote_id).first()
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found",
        )

    if quote.status != "ACCEPTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote must be accepted before booking appointment",
        )

    # Limit days
    days = min(days, 60)

    try:
        # Generate availability
        availability = scheduling_service.generate_available_slots(
            db=db,
            quote_id=quote_id,
            days=days
        )

        # Convert to response format
        slots = [
            AvailabilitySlot(**slot)
            for slot in availability["slots"]
        ]

        return AvailabilityResponse(
            quote_id=quote_id,
            available_dates=availability["available_dates"],
            slots=slots,
            timezone="UTC",
            min_notice_hours=availability["min_notice_hours"],
            max_days_advance=availability["max_days_advance"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/scheduling/book", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    booking_data: AppointmentBookingRequest,
    db: InMemoryDB = Depends(get_db),
) -> AppointmentResponse:
    """
    Book an appointment (PUBLIC - no auth required).

    Customers can book appointments for their accepted quotes.

    Args:
        booking_data: Booking details
        db: Database session

    Returns:
        Created appointment

    Raises:
        HTTPException: 404 if quote not found, 400 if slot unavailable
    """
    try:
        # Book the appointment
        appointment = scheduling_service.book_appointment(
            db=db,
            quote_id=booking_data.quote_id,
            scheduled_start=booking_data.scheduled_start,
            customer_name=booking_data.customer_name,
            customer_email=booking_data.customer_email,
            customer_phone=booking_data.customer_phone,
            address=booking_data.address,
            special_instructions=booking_data.special_instructions,
        )

        # Format confirmation message
        date_str = appointment.scheduled_start.strftime("%B %d, %Y")
        time_str = appointment.scheduled_start.strftime("%I:%M %p")
        message = f"Your appointment has been scheduled for {date_str} at {time_str}."

        return AppointmentResponse(
            id=appointment.id,
            quote_id=appointment.quote_id,
            contact_id=appointment.contact_id,
            scheduled_start=appointment.scheduled_start,
            scheduled_end=appointment.scheduled_end,
            duration_minutes=appointment.duration_minutes,
            status=appointment.status,
            customer_name=appointment.customer_name,
            customer_email=appointment.customer_email,
            customer_phone=appointment.customer_phone,
            address=appointment.address,
            special_instructions=appointment.special_instructions,
            service_description=appointment.service_description,
            created_at=appointment.created_at,
            message=message,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
