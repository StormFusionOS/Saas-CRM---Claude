"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Quote Service - Pricing Logic and Quote Management

This module contains all business logic for the quoting engine:
- Quote creation and management
- Pricing calculations
- Quote item management
- Service catalog operations
- Status workflow management

Designed for clean separation of concerns - keeps business logic
out of API route handlers.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import Quote, QuoteItem, Service, QuoteStatus, Lead, Contact
from app.db import InMemoryDB


# ============================================================================
# Quote Operations
# ============================================================================


def create_quote(
    db: InMemoryDB,
    lead_id: int,
    contact_id: int,
    title: str,
    items: List[Dict[str, Any]],
    created_by_id: Optional[int] = None,
    **kwargs
) -> Quote:
    """
    Create a new quote with line items.

    Handles:
    - Quote number generation (Q-YYYY-NNNN format)
    - Line item creation from services
    - Price calculations
    - Total aggregation
    - Default terms and expiration

    Args:
        db: Database session
        lead_id: Associated lead ID
        contact_id: Associated contact ID
        title: Quote title
        items: List of quote item data (service_id, quantity, etc.)
        created_by_id: User ID creating the quote
        **kwargs: Additional quote fields (terms, notes, etc.)

    Returns:
        Created quote with all line items

    Raises:
        ValueError: If lead or contact not found
        ValueError: If service not found for any item
    """
    from app.models import get_next_quote_id, get_next_quote_item_id

    # Validate lead and contact exist (simplified for in-memory)
    lead_exists = any(l.id == lead_id for l in db.leads)
    contact_exists = any(c.id == contact_id for c in db.contacts)

    if not lead_exists:
        raise ValueError(f"Lead {lead_id} not found")
    if not contact_exists:
        raise ValueError(f"Contact {contact_id} not found")

    # Generate unique quote number
    quote_number = generate_quote_number(db)

    # Set default valid_until (30 days from now)
    valid_until = kwargs.get('valid_until')
    if not valid_until:
        valid_until = datetime.utcnow() + timedelta(days=30)

    # Create quote (without items first)
    quote = Quote(
        id=get_next_quote_id(),
        lead_id=lead_id,
        contact_id=contact_id,
        quote_number=quote_number,
        title=title,
        status=QuoteStatus.DRAFT.value,
        valid_until=valid_until,
        terms=kwargs.get('terms', ''),
        notes=kwargs.get('notes', ''),
        public_notes=kwargs.get('public_notes', ''),
        created_by_id=created_by_id,
        metadata=kwargs.get('metadata', {}),
        created_at=datetime.utcnow(),
    )

    # Create quote items
    quote_items = []
    for item_data in items:
        service_id = item_data.get('service_id')
        service = get_service(db, service_id)

        if not service:
            raise ValueError(f"Service {service_id} not found")

        quantity = item_data.get('quantity', 1.0)
        unit_price = item_data.get('unit_price')

        # Calculate unit price if not provided
        if unit_price is None:
            unit_price = service.base_price

        # Calculate line item totals
        subtotal = unit_price * quantity
        discount_percent = item_data.get('discount_percent', 0.0)
        discount_amount = subtotal * (discount_percent / 100.0)
        tax_percent = item_data.get('tax_percent', 0.0)
        subtotal_after_discount = subtotal - discount_amount
        tax_amount = subtotal_after_discount * (tax_percent / 100.0)
        total = subtotal_after_discount + tax_amount

        quote_item = QuoteItem(
            id=get_next_quote_item_id(),
            quote_id=quote.id,
            service_id=service.id,
            service_name=service.name,
            description=service.description,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            tax_percent=tax_percent,
            tax_amount=tax_amount,
            total=total,
            display_order=item_data.get('display_order', len(quote_items)),
            metadata=item_data.get('metadata', {}),
            created_at=datetime.utcnow(),
        )
        quote_items.append(quote_item)
        db.add(quote_item)

    # Calculate quote totals
    totals = calculate_quote_totals(quote_items)
    quote.subtotal = totals['subtotal']
    quote.discount_amount = totals['discount_amount']
    quote.tax_amount = totals['tax_amount']
    quote.total = totals['total']

    # Save quote to database
    db.add(quote)
    db.commit()

    return quote


def get_quote(db: InMemoryDB, quote_id: int) -> Optional[Quote]:
    """
    Get a quote by ID with all line items.

    Args:
        db: Database session
        quote_id: Quote ID to retrieve

    Returns:
        Quote with items, or None if not found
    """
    # Find quote
    for quote in db.quotes:
        if quote.id == quote_id:
            return quote
    return None


def list_quotes(
    db: InMemoryDB,
    lead_id: Optional[int] = None,
    contact_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Quote]:
    """
    List quotes with filtering and pagination.

    Args:
        db: Database session
        lead_id: Optional lead ID filter
        contact_id: Optional contact ID filter
        status: Optional status filter
        limit: Maximum results to return
        offset: Number of results to skip

    Returns:
        List of quotes (without items for performance)
    """
    quotes = db.quotes.copy()

    # Apply filters
    if lead_id is not None:
        quotes = [q for q in quotes if q.lead_id == lead_id]

    if contact_id is not None:
        quotes = [q for q in quotes if q.contact_id == contact_id]

    if status:
        quotes = [q for q in quotes if q.status == status]

    # Sort by created_at DESC (most recent first)
    quotes.sort(key=lambda q: q.created_at, reverse=True)

    # Apply pagination
    start = offset
    end = offset + limit
    return quotes[start:end]


def update_quote(
    db: InMemoryDB,
    quote_id: int,
    **updates
) -> Optional[Quote]:
    """
    Update quote fields.

    Updates metadata only - does not update line items.
    Use quote item functions for line item modifications.

    Args:
        db: Database session
        quote_id: Quote ID to update
        **updates: Fields to update (title, terms, notes, etc.)

    Returns:
        Updated quote, or None if not found

    Raises:
        ValueError: If quote cannot be edited (e.g., already accepted)
    """
    quote = get_quote(db, quote_id)
    if not quote:
        return None

    if not is_quote_editable(quote):
        raise ValueError(f"Quote {quote_id} cannot be edited in {quote.status} status")

    # Apply updates
    for key, value in updates.items():
        if hasattr(quote, key) and value is not None:
            setattr(quote, key, value)

    # Set updated_at timestamp
    quote.updated_at = datetime.utcnow()

    return quote


def update_quote_status(
    db: InMemoryDB,
    quote_id: int,
    new_status: str
) -> Optional[Quote]:
    """
    Update quote status with workflow validation.

    Handles status transitions and tracks timestamps:
    - DRAFT → SENT: Sets sent_at
    - SENT → VIEWED: Sets viewed_at
    - VIEWED → ACCEPTED: Sets accepted_at, creates job
    - VIEWED → REJECTED: Sets rejected_at

    Args:
        db: Database session
        quote_id: Quote ID to update
        new_status: New status (must be valid QuoteStatus)

    Returns:
        Updated quote, or None if not found

    Raises:
        ValueError: If status transition is invalid
    """
    quote = get_quote(db, quote_id)
    if not quote:
        return None

    # Validate status is valid
    try:
        QuoteStatus(new_status)
    except ValueError:
        raise ValueError(f"Invalid status: {new_status}")

    # Update status
    old_status = quote.status
    quote.status = new_status

    # Set appropriate timestamp based on status transition
    now = datetime.utcnow()
    if new_status == QuoteStatus.SENT.value:
        quote.sent_at = now
    elif new_status == QuoteStatus.VIEWED.value:
        quote.viewed_at = now
    elif new_status == QuoteStatus.ACCEPTED.value:
        quote.accepted_at = now
        # TODO: Create job on acceptance (future feature)
    elif new_status == QuoteStatus.REJECTED.value:
        quote.rejected_at = now
    elif new_status == QuoteStatus.EXPIRED.value:
        quote.expired_at = now

    quote.updated_at = now

    return quote


def delete_quote(db: InMemoryDB, quote_id: int) -> bool:
    """
    Soft-delete a quote.

    Sets status to CANCELLED rather than removing from database.

    Args:
        db: Database session
        quote_id: Quote ID to delete

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If quote cannot be deleted (e.g., already accepted)
    """
    quote = get_quote(db, quote_id)
    if not quote:
        return False

    # Don't allow deletion of accepted quotes
    if quote.status == QuoteStatus.ACCEPTED.value:
        raise ValueError(f"Cannot delete accepted quote {quote_id}")

    # Soft delete by setting status to CANCELLED
    quote.status = QuoteStatus.CANCELLED.value
    quote.updated_at = datetime.utcnow()

    return True


# ============================================================================
# Quote Item Operations
# ============================================================================


def add_quote_item(
    db: InMemoryDB,
    quote_id: int,
    service_id: int,
    quantity: float = 1.0,
    **kwargs
) -> QuoteItem:
    """
    Add a line item to a quote.

    Handles:
    - Service lookup and price calculation
    - Tax and discount application
    - Subtotal calculation
    - Quote total recalculation

    Args:
        db: Database session
        quote_id: Quote ID to add item to
        service_id: Service ID to add
        quantity: Quantity of service
        **kwargs: Additional item fields (unit_price override, metadata, etc.)

    Returns:
        Created quote item

    Raises:
        ValueError: If quote or service not found
        ValueError: If quote is not editable
    """
    from app.models import get_next_quote_item_id

    # Validate quote exists and is editable
    quote = get_quote(db, quote_id)
    if not quote:
        raise ValueError(f"Quote {quote_id} not found")

    if not is_quote_editable(quote):
        raise ValueError(f"Quote {quote_id} cannot be edited in {quote.status} status")

    # Validate service exists
    service = get_service(db, service_id)
    if not service:
        raise ValueError(f"Service {service_id} not found")

    # Calculate unit price from service (or use override)
    unit_price = kwargs.get('unit_price', service.base_price)

    # Calculate line item totals
    subtotal = unit_price * quantity
    discount_percent = kwargs.get('discount_percent', 0.0)
    discount_amount = subtotal * (discount_percent / 100.0)
    tax_percent = kwargs.get('tax_percent', 0.0)
    subtotal_after_discount = subtotal - discount_amount
    tax_amount = subtotal_after_discount * (tax_percent / 100.0)
    total = subtotal_after_discount + tax_amount

    # Get current item count for display_order
    current_items = [item for item in db.quote_items if item.quote_id == quote_id]

    # Create quote item
    quote_item = QuoteItem(
        id=get_next_quote_item_id(),
        quote_id=quote_id,
        service_id=service.id,
        service_name=service.name,
        description=service.description,
        quantity=quantity,
        unit_price=unit_price,
        subtotal=subtotal,
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        tax_percent=tax_percent,
        tax_amount=tax_amount,
        total=total,
        display_order=kwargs.get('display_order', len(current_items)),
        metadata=kwargs.get('metadata', {}),
        created_at=datetime.utcnow(),
    )

    db.add(quote_item)

    # Recalculate quote totals
    all_items = [item for item in db.quote_items if item.quote_id == quote_id]
    totals = calculate_quote_totals(all_items)
    quote.subtotal = totals['subtotal']
    quote.discount_amount = totals['discount_amount']
    quote.tax_amount = totals['tax_amount']
    quote.total = totals['total']
    quote.updated_at = datetime.utcnow()

    db.commit()

    return quote_item


def update_quote_item(
    db: InMemoryDB,
    quote_id: int,
    item_id: int,
    **updates
) -> Optional[QuoteItem]:
    """
    Update a quote line item.

    Recalculates item totals and quote totals after update.

    Args:
        db: Database session
        quote_id: Quote ID
        item_id: Line item ID to update
        **updates: Fields to update (quantity, unit_price, etc.)

    Returns:
        Updated quote item, or None if not found

    Raises:
        ValueError: If quote is not editable
    """
    # Validate quote exists and is editable
    quote = get_quote(db, quote_id)
    if not quote:
        raise ValueError(f"Quote {quote_id} not found")

    if not is_quote_editable(quote):
        raise ValueError(f"Quote {quote_id} cannot be edited in {quote.status} status")

    # Find item and validate it belongs to quote
    item = None
    for quote_item in db.quote_items:
        if quote_item.id == item_id and quote_item.quote_id == quote_id:
            item = quote_item
            break

    if not item:
        return None

    # Apply updates
    for key, value in updates.items():
        if hasattr(item, key) and value is not None:
            setattr(item, key, value)

    # Recalculate item totals
    subtotal = item.unit_price * item.quantity
    discount_amount = subtotal * (item.discount_percent / 100.0)
    subtotal_after_discount = subtotal - discount_amount
    tax_amount = subtotal_after_discount * (item.tax_percent / 100.0)
    total = subtotal_after_discount + tax_amount

    item.subtotal = subtotal
    item.discount_amount = discount_amount
    item.tax_amount = tax_amount
    item.total = total

    # Recalculate quote totals
    all_items = [i for i in db.quote_items if i.quote_id == quote_id]
    totals = calculate_quote_totals(all_items)
    quote.subtotal = totals['subtotal']
    quote.discount_amount = totals['discount_amount']
    quote.tax_amount = totals['tax_amount']
    quote.total = totals['total']
    quote.updated_at = datetime.utcnow()

    db.commit()

    return item


def delete_quote_item(
    db: InMemoryDB,
    quote_id: int,
    item_id: int
) -> bool:
    """
    Remove a line item from a quote.

    Recalculates quote totals after removal.

    Args:
        db: Database session
        quote_id: Quote ID
        item_id: Line item ID to remove

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If quote is not editable
    """
    # Validate quote exists and is editable
    quote = get_quote(db, quote_id)
    if not quote:
        raise ValueError(f"Quote {quote_id} not found")

    if not is_quote_editable(quote):
        raise ValueError(f"Quote {quote_id} cannot be edited in {quote.status} status")

    # Find item and validate it belongs to quote
    item = None
    for quote_item in db.quote_items:
        if quote_item.id == item_id and quote_item.quote_id == quote_id:
            item = quote_item
            break

    if not item:
        return False

    # Remove item from database
    db.delete(item)

    # Recalculate quote totals
    all_items = [i for i in db.quote_items if i.quote_id == quote_id]
    totals = calculate_quote_totals(all_items)
    quote.subtotal = totals['subtotal']
    quote.discount_amount = totals['discount_amount']
    quote.tax_amount = totals['tax_amount']
    quote.total = totals['total']
    quote.updated_at = datetime.utcnow()

    db.commit()

    return True


# ============================================================================
# Pricing Calculations
# ============================================================================


def calculate_item_price(
    service: Service,
    quantity: float,
    inputs: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate price for a quote item.

    Evaluates pricing formulas with user inputs.
    Example: "base_price * sq_ft + (stories * 50)"

    Args:
        service: Service to price
        quantity: Quantity of service
        inputs: User inputs for formula (e.g., {"sq_ft": 2500, "stories": 2})

    Returns:
        Calculated unit price
    """
    if not service.pricing_formula:
        # No formula, use base price * quantity
        return service.base_price * quantity

    # Prepare evaluation context
    context = {
        "base_price": service.base_price,
        "quantity": quantity,
    }

    # Add user inputs to context
    if inputs:
        context.update(inputs)

    try:
        # Safely evaluate the formula
        # Note: In production, use a safer expression evaluator like simpleeval
        # For now, we'll use eval with restricted context
        price = eval(service.pricing_formula, {"__builtins__": {}}, context)
        return float(price)
    except Exception as e:
        # If formula evaluation fails, fall back to base price
        return service.base_price * quantity


def calculate_quote_totals(items: List[QuoteItem]) -> Dict[str, float]:
    """
    Calculate aggregated totals for a quote.

    Args:
        items: List of quote items

    Returns:
        Dict with subtotal, discount_amount, tax_amount, total
    """
    subtotal = sum(item.subtotal for item in items)
    discount_amount = sum(item.discount_amount for item in items)
    tax_amount = sum(item.tax_amount for item in items)
    total = subtotal - discount_amount + tax_amount

    return {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "total": total,
    }


# ============================================================================
# Service Catalog Operations
# ============================================================================


def list_services(
    db: InMemoryDB,
    category: Optional[str] = None,
    is_active: bool = True
) -> List[Service]:
    """
    List services from catalog.

    Args:
        db: Database session
        category: Optional category filter
        is_active: Filter by active status

    Returns:
        List of services
    """
    services = db.services.copy()

    # Apply filters
    if is_active is not None:
        services = [s for s in services if s.is_active == is_active]

    if category:
        services = [s for s in services if s.category == category]

    # Sort by display_order, then name
    services.sort(key=lambda s: (s.display_order, s.name))

    return services


def get_service(db: InMemoryDB, service_id: int) -> Optional[Service]:
    """
    Get a service by ID.

    Args:
        db: Database session
        service_id: Service ID to retrieve

    Returns:
        Service, or None if not found
    """
    for service in db.services:
        if service.id == service_id:
            return service
    return None


def create_service(
    db: InMemoryDB,
    name: str,
    description: str,
    category: str,
    base_price: float,
    unit: str,
    **kwargs
) -> Service:
    """
    Create a new service in the catalog.

    Args:
        db: Database session
        name: Service name
        description: Service description
        category: Service category
        base_price: Base price
        unit: Unit of measurement
        **kwargs: Additional fields (min_price, pricing_formula, modifiers, etc.)

    Returns:
        Created service

    Raises:
        ValueError: If validation fails
    """
    from app.models import get_next_service_id

    # Validate base_price
    if base_price < 0:
        raise ValueError("Base price cannot be negative")

    # Validate min_price if provided
    min_price = kwargs.get('min_price')
    if min_price is not None and min_price < 0:
        raise ValueError("Minimum price cannot be negative")

    service = Service(
        id=get_next_service_id(),
        name=name,
        description=description,
        category=category,
        base_price=base_price,
        unit=unit,
        min_price=min_price,
        pricing_formula=kwargs.get('pricing_formula'),
        modifiers=kwargs.get('modifiers', {}),
        is_active=kwargs.get('is_active', True),
        display_order=kwargs.get('display_order', 0),
        metadata=kwargs.get('metadata', {}),
        created_at=datetime.utcnow(),
    )

    db.add(service)
    db.commit()

    return service


def update_service(
    db: InMemoryDB,
    service_id: int,
    **updates
) -> Optional[Service]:
    """
    Update a service in the catalog.

    Args:
        db: Database session
        service_id: Service ID to update
        **updates: Fields to update

    Returns:
        Updated service, or None if not found

    Raises:
        ValueError: If validation fails
    """
    service = get_service(db, service_id)
    if not service:
        return None

    # Validate base_price if being updated
    if 'base_price' in updates and updates['base_price'] < 0:
        raise ValueError("Base price cannot be negative")

    # Validate min_price if being updated
    if 'min_price' in updates and updates['min_price'] is not None and updates['min_price'] < 0:
        raise ValueError("Minimum price cannot be negative")

    # Apply updates
    for key, value in updates.items():
        if hasattr(service, key) and value is not None:
            setattr(service, key, value)

    # Set updated_at timestamp
    service.updated_at = datetime.utcnow()

    db.commit()

    return service


def delete_service(db: InMemoryDB, service_id: int) -> bool:
    """
    Delete a service from the catalog.

    Soft-deletes by setting is_active to False rather than removing from database.

    Args:
        db: Database session
        service_id: Service ID to delete

    Returns:
        True if deleted, False if not found
    """
    service = get_service(db, service_id)
    if not service:
        return False

    # Soft delete by marking as inactive
    service.is_active = False
    service.updated_at = datetime.utcnow()

    db.commit()

    return True


# ============================================================================
# Helper Functions
# ============================================================================


def generate_quote_number(db: InMemoryDB) -> str:
    """
    Generate a unique quote number.

    Format: Q-YYYY-NNNN (e.g., Q-2025-0001)

    Args:
        db: Database session

    Returns:
        Unique quote number
    """
    current_year = datetime.now().year
    prefix = f"Q-{current_year}-"

    # Find highest quote number for current year
    quotes_this_year = [
        q for q in db.quotes
        if q.quote_number.startswith(prefix)
    ]

    if not quotes_this_year:
        next_num = 1
    else:
        # Extract numbers from quote_number (e.g., "Q-2025-0001" -> 1)
        numbers = [
            int(q.quote_number.split('-')[-1])
            for q in quotes_this_year
        ]
        next_num = max(numbers) + 1

    return f"{prefix}{next_num:04d}"


def is_quote_editable(quote: Quote) -> bool:
    """
    Check if a quote can be edited.

    Quotes can only be edited in DRAFT or PENDING status.

    Args:
        quote: Quote to check

    Returns:
        True if editable, False otherwise
    """
    editable_statuses = [QuoteStatus.DRAFT.value, QuoteStatus.PENDING.value]
    return quote.status in editable_statuses


__all__ = [
    "create_quote",
    "get_quote",
    "list_quotes",
    "update_quote",
    "update_quote_status",
    "delete_quote",
    "add_quote_item",
    "update_quote_item",
    "delete_quote_item",
    "calculate_item_price",
    "calculate_quote_totals",
    "list_services",
    "get_service",
    "generate_quote_number",
    "is_quote_editable",
]
