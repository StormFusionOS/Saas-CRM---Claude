"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Quotes API Routes - Sales Suite

All quoting engine endpoints. Must be mounted under /sales/quotes/...
to ensure proper Sales Suite scoping.

This module provides CRUD operations for:
- Quotes (formal proposals with line items)
- Quote Items (line items within quotes)
- Services (service catalog for quotes)
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db import get_db, InMemoryDB
from app.api.deps import require_sales_claims
from app.schemas.quotes import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    QuoteCreate,
    QuoteUpdate,
    QuoteStatusUpdate,
    QuoteResponse,
    QuoteWithItems,
    QuoteListItem,
    QuoteItemCreate,
    QuoteItemUpdate,
    QuoteItemResponse,
)
from app.models import (
    Service,
    Quote,
    QuoteItem,
    QuoteStatus,
    get_next_service_id,
    get_next_quote_id,
    get_next_quote_item_id,
)


router = APIRouter(tags=["sales", "quotes"])


# ============================================================================
# Quote Endpoints
# ============================================================================


@router.post("/quotes", response_model=QuoteWithItems, status_code=status.HTTP_201_CREATED)
def create_quote(
    quote_data: QuoteCreate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> QuoteWithItems:
    """
    Create a new quote.

    Creates a formal quote/proposal for a lead with optional line items.
    Auto-generates a unique quote number (e.g., Q-2025-0001).

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_data: Quote creation data including line items
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Created quote with all line items

    Raises:
        HTTPException: 404 if lead or contact not found
        HTTPException: 400 if validation fails
    """
    from app.services import quote_service

    try:
        # Convert Pydantic items to dicts
        items_data = [item.dict() for item in quote_data.items]

        # Create quote via service
        quote = quote_service.create_quote(
            db=db,
            lead_id=quote_data.lead_id,
            contact_id=quote_data.contact_id,
            title=quote_data.title,
            items=items_data,
            created_by_id=claims.get('user_id'),
            valid_until=quote_data.valid_until,
            terms=quote_data.terms,
            notes=quote_data.notes,
            public_notes=quote_data.public_notes,
            metadata=quote_data.metadata,
        )

        # Get quote items for response
        quote_items = [item for item in db.quote_items if item.quote_id == quote.id]

        # Build response with items
        return QuoteWithItems(
            **quote.__dict__,
            items=[QuoteItemResponse(**item.__dict__) for item in quote_items]
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/quotes/{quote_id}", response_model=QuoteWithItems)
def get_quote(
    quote_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> QuoteWithItems:
    """
    Get a quote by ID with all line items.

    Retrieves a complete quote including all line items, totals, and metadata.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID to retrieve
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Quote with all line items

    Raises:
        HTTPException: 404 if quote not found
    """
    from app.services import quote_service

    quote = quote_service.get_quote(db, quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote {quote_id} not found"
        )

    # Get quote items
    quote_items = [item for item in db.quote_items if item.quote_id == quote.id]

    return QuoteWithItems(
        **quote.__dict__,
        items=[QuoteItemResponse(**item.__dict__) for item in quote_items]
    )


@router.get("/quotes", response_model=List[QuoteListItem])
def list_quotes(
    lead_id: Optional[int] = Query(None, description="Filter by lead ID"),
    contact_id: Optional[int] = Query(None, description="Filter by contact ID"),
    status: Optional[str] = Query(None, description="Filter by status (DRAFT, SENT, ACCEPTED, etc.)"),
    limit: int = Query(50, description="Maximum number of quotes to return"),
    offset: int = Query(0, description="Number of quotes to skip"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> List[QuoteListItem]:
    """
    List quotes with filtering and pagination.

    Returns a lightweight list of quotes for list views.
    Use get_quote() for full quote details with line items.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        lead_id: Optional lead ID filter
        contact_id: Optional contact ID filter
        status: Optional status filter
        limit: Maximum results to return
        offset: Number of results to skip (pagination)
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        List of quotes (lightweight, no line items)
    """
    from app.services import quote_service

    quotes = quote_service.list_quotes(
        db=db,
        lead_id=lead_id,
        contact_id=contact_id,
        status=status,
        limit=limit,
        offset=offset
    )

    return [QuoteListItem(**quote.__dict__) for quote in quotes]


@router.patch("/quotes/{quote_id}", response_model=QuoteResponse)
def update_quote(
    quote_id: int,
    quote_update: QuoteUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> QuoteResponse:
    """
    Update a quote.

    Updates quote metadata (title, terms, notes, etc.).
    Does not update line items - use quote item endpoints for that.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID to update
        quote_update: Fields to update
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Updated quote

    Raises:
        HTTPException: 404 if quote not found
        HTTPException: 400 if validation fails

    TODO: Implement quote update logic in quote_service.py
    """
    from app.services import quote_service

    try:
        quote = quote_service.update_quote(
            db=db,
            quote_id=quote_id,
            **quote_update.dict(exclude_unset=True)
        )

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return QuoteResponse(**quote.__dict__)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/quotes/{quote_id}/status", response_model=QuoteResponse)
def update_quote_status(
    quote_id: int,
    status_update: QuoteStatusUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> QuoteResponse:
    """
    Update quote status.

    Changes quote status (DRAFT → SENT → ACCEPTED, etc.).
    Tracks timestamps for status transitions (sent_at, accepted_at, etc.).

    **Sales Suite Access Only** - Requires sales role claims.

    Valid status transitions:
    - DRAFT → PENDING, SENT, CANCELLED
    - PENDING → SENT, CANCELLED
    - SENT → VIEWED, ACCEPTED, REJECTED, EXPIRED
    - VIEWED → ACCEPTED, REJECTED, EXPIRED

    Args:
        quote_id: Quote ID to update
        status_update: New status
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Updated quote with new status

    Raises:
        HTTPException: 404 if quote not found
        HTTPException: 400 if invalid status transition

    TODO: Implement status update logic in quote_service.py
    """
    from app.services import quote_service

    try:
        quote = quote_service.update_quote_status(
            db=db,
            quote_id=quote_id,
            new_status=status_update.status
        )

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return QuoteResponse(**quote.__dict__)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/quotes/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> None:
    """
    Delete a quote.

    Soft-deletes a quote by setting status to CANCELLED.
    Does not actually remove the quote from the database.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID to delete
        db: Database session
        claims: JWT claims with sales permissions

    Raises:
        HTTPException: 404 if quote not found
        HTTPException: 400 if quote cannot be deleted (e.g., already accepted)

    TODO: Implement quote deletion logic in quote_service.py
    """
    from app.services import quote_service

    try:
        success = quote_service.delete_quote(db, quote_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# Quote Item Endpoints
# ============================================================================


@router.post("/quotes/{quote_id}/items", response_model=QuoteItemResponse, status_code=status.HTTP_201_CREATED)
def add_quote_item(
    quote_id: int,
    item_data: QuoteItemCreate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> QuoteItemResponse:
    """
    Add a line item to a quote.

    Adds a new service line item to an existing quote.
    Automatically recalculates quote totals.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID to add item to
        item_data: Line item data
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Created quote item

    Raises:
        HTTPException: 404 if quote or service not found
        HTTPException: 400 if quote is not editable (e.g., already accepted)

    TODO: Implement item creation logic in quote_service.py
    """
    from app.services import quote_service

    try:
        quote_item = quote_service.add_quote_item(
            db=db,
            quote_id=quote_id,
            service_id=item_data.service_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_percent=item_data.discount_percent,
            tax_percent=item_data.tax_percent,
            metadata=item_data.metadata
        )

        return QuoteItemResponse(**quote_item.__dict__)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/quotes/{quote_id}/items/{item_id}", response_model=QuoteItemResponse)
def update_quote_item(
    quote_id: int,
    item_id: int,
    item_update: QuoteItemUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> QuoteItemResponse:
    """
    Update a quote line item.

    Updates quantity, pricing, or other line item details.
    Automatically recalculates quote totals.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID
        item_id: Line item ID to update
        item_update: Fields to update
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Updated quote item

    Raises:
        HTTPException: 404 if quote or item not found
        HTTPException: 400 if quote is not editable

    TODO: Implement item update logic in quote_service.py
    """
    from app.services import quote_service

    try:
        quote_item = quote_service.update_quote_item(
            db=db,
            quote_id=quote_id,
            item_id=item_id,
            **item_update.dict(exclude_unset=True)
        )

        if not quote_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote item {item_id} not found"
            )

        return QuoteItemResponse(**quote_item.__dict__)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/quotes/{quote_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote_item(
    quote_id: int,
    item_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> None:
    """
    Remove a line item from a quote.

    Removes a line item and recalculates quote totals.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID
        item_id: Line item ID to remove
        db: Database session
        claims: JWT claims with sales permissions

    Raises:
        HTTPException: 404 if quote or item not found
        HTTPException: 400 if quote is not editable

    TODO: Implement item deletion logic in quote_service.py
    """
    from app.services import quote_service

    try:
        success = quote_service.delete_quote_item(db, quote_id, item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote item {item_id} not found"
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# Service Catalog Endpoints
# ============================================================================


@router.get("/services", response_model=List[ServiceResponse])
def list_services(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> List[ServiceResponse]:
    """
    List available services.

    Returns the service catalog for building quotes.
    Typically filtered to active services only.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        category: Optional category filter
        is_active: Filter by active status (default: True)
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        List of services

    TODO: Implement service listing logic in quote_service.py
    """
    from app.services import quote_service

    services = quote_service.list_services(
        db=db,
        category=category,
        is_active=is_active
    )

    return [ServiceResponse(**service.__dict__) for service in services]


@router.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> ServiceResponse:
    """
    Get a service by ID.

    Retrieves detailed service information including pricing formulas.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        service_id: Service ID to retrieve
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Service details

    Raises:
        HTTPException: 404 if service not found

    TODO: Implement service retrieval logic in quote_service.py
    """
    from app.services import quote_service

    service = quote_service.get_service(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service_id} not found"
        )

    return ServiceResponse(**service.__dict__)


__all__ = ["router"]
