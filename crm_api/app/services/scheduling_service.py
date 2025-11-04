"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Scheduling Service - Generate available slots and book appointments.
"""

from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Optional
from app.db import InMemoryDB
from app.models import AvailabilityConfig, Appointment, Quote, Contact, get_next_appointment_id


def get_availability_config(db: InMemoryDB, config_id: Optional[int] = None) -> AvailabilityConfig:
    """
    Get availability configuration.

    Args:
        db: Database session
        config_id: Config ID (uses default if None)

    Returns:
        AvailabilityConfig
    """
    if config_id:
        config = db.availability_configs.get(config_id)
        if not config:
            raise ValueError(f"Availability config {config_id} not found")
        return config

    # Get default (first active) config
    for config in db.availability_configs.values():
        if config.is_active:
            return config

    raise ValueError("No active availability configuration found")


def generate_available_slots(
    db: InMemoryDB,
    quote_id: int,
    start_date: Optional[datetime] = None,
    days: int = 14
) -> Dict:
    """
    Generate available time slots for booking.

    Args:
        db: Database session
        quote_id: Quote ID
        start_date: Start date (defaults to now + min_notice_hours)
        days: Number of days to generate slots for

    Returns:
        Dict with available_dates and slots
    """
    # Get config
    config = get_availability_config(db)

    # Calculate start date
    if not start_date:
        start_date = datetime.utcnow() + timedelta(hours=config.min_notice_hours)

    # Limit to max days advance
    end_date = min(
        start_date + timedelta(days=days),
        datetime.utcnow() + timedelta(days=config.max_days_advance)
    )

    # Get existing appointments in date range
    existing_appointments = [
        appt for appt in db.appointments
        if appt.scheduled_start >= start_date and appt.scheduled_start <= end_date
        and appt.status in ["scheduled", "confirmed"]
    ]

    available_slots = []
    available_dates = set()

    # Generate slots day by day
    current_date = start_date.date()
    while current_date <= end_date.date():
        # Check if day is in working_days (Monday=1, Sunday=7)
        weekday = current_date.isoweekday()
        if weekday not in config.working_days:
            current_date += timedelta(days=1)
            continue

        # Check if date is in blackout dates
        if current_date.isoformat() in config.blackout_dates:
            current_date += timedelta(days=1)
            continue

        # Generate slots for this day
        day_slots = _generate_day_slots(
            date=current_date,
            config=config,
            existing_appointments=existing_appointments
        )

        if day_slots:
            available_dates.add(current_date.isoformat())
            available_slots.extend(day_slots)

        current_date += timedelta(days=1)

    return {
        "available_dates": sorted(list(available_dates)),
        "slots": available_slots,
        "min_notice_hours": config.min_notice_hours,
        "max_days_advance": config.max_days_advance,
    }


def _generate_day_slots(
    date,
    config: AvailabilityConfig,
    existing_appointments: List[Appointment]
) -> List[Dict]:
    """Generate time slots for a single day."""

    slots = []

    # Parse start and end time
    start_hour, start_minute = map(int, config.start_time.split(":"))
    end_hour, end_minute = map(int, config.end_time.split(":"))

    # Current slot start time
    slot_start = datetime.combine(date, dt_time(start_hour, start_minute))
    day_end = datetime.combine(date, dt_time(end_hour, end_minute))

    # Count appointments on this day
    day_appointments = [
        appt for appt in existing_appointments
        if appt.scheduled_start.date() == date
    ]

    # Check if max appointments reached
    if len(day_appointments) >= config.max_appointments_per_day:
        return []

    # Generate slots
    while slot_start + timedelta(minutes=config.slot_duration_minutes) <= day_end:
        slot_end = slot_start + timedelta(minutes=config.slot_duration_minutes)

        # Check if slot conflicts with existing appointment
        is_available = True
        for appt in day_appointments:
            # Check for overlap (with buffer)
            appt_start_with_buffer = appt.scheduled_start - timedelta(minutes=config.buffer_minutes)
            appt_end_with_buffer = appt.scheduled_end + timedelta(minutes=config.buffer_minutes)

            if not (slot_end <= appt_start_with_buffer or slot_start >= appt_end_with_buffer):
                is_available = False
                break

        if is_available:
            slots.append({
                "start": slot_start,
                "end": slot_end,
                "duration_minutes": config.slot_duration_minutes,
                "date": date.isoformat(),
                "time": slot_start.strftime("%H:%M"),
            })

        # Move to next slot (including buffer)
        slot_start = slot_end + timedelta(minutes=config.buffer_minutes)

    return slots


def book_appointment(
    db: InMemoryDB,
    quote_id: int,
    scheduled_start: datetime,
    customer_name: str,
    address: str,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
    special_instructions: str = ""
) -> Appointment:
    """
    Book an appointment for a quote.

    Args:
        db: Database session
        quote_id: Quote ID
        scheduled_start: Desired start time
        customer_name: Customer name
        address: Service address
        customer_email: Optional email
        customer_phone: Optional phone
        special_instructions: Optional instructions

    Returns:
        Created Appointment

    Raises:
        ValueError: If quote not found, not accepted, or slot not available
    """
    from app.models import Quote

    # Get quote
    quote = db.query(Quote).filter_by(id=quote_id).first()
    if not quote:
        raise ValueError("Quote not found")

    # Verify quote is accepted
    if quote.status != "ACCEPTED":
        raise ValueError("Quote must be accepted before booking appointment")

    # Get config and validate slot
    config = get_availability_config(db)

    # Check minimum notice
    min_start = datetime.utcnow() + timedelta(hours=config.min_notice_hours)
    if scheduled_start < min_start:
        raise ValueError(f"Appointment must be at least {config.min_notice_hours} hours in advance")

    # Check max advance
    max_start = datetime.utcnow() + timedelta(days=config.max_days_advance)
    if scheduled_start > max_start:
        raise ValueError(f"Cannot book more than {config.max_days_advance} days in advance")

    # Calculate end time
    scheduled_end = scheduled_start + timedelta(minutes=config.slot_duration_minutes)

    # Check for conflicts
    conflicts = [
        appt for appt in db.appointments
        if appt.status in ["scheduled", "confirmed"]
        and not (scheduled_end <= appt.scheduled_start or scheduled_start >= appt.scheduled_end)
    ]

    if conflicts:
        raise ValueError("This time slot is no longer available")

    # Get service description from quote
    service_desc = f"Quote #{quote.quote_number}"
    if hasattr(quote, 'title'):
        service_desc = quote.title

    # Create appointment
    appointment = Appointment(
        id=get_next_appointment_id(),
        quote_id=quote_id,
        contact_id=quote.contact_id,
        lead_id=quote.lead_id,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_end,
        duration_minutes=config.slot_duration_minutes,
        status="scheduled",
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        service_description=service_desc,
        special_instructions=special_instructions,
        address=address,
        created_at=datetime.utcnow(),
    )

    db.appointments.append(appointment)
    db.commit()

    return appointment
