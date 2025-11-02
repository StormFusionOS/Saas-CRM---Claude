"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Pricebook routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.db import get_db, InMemoryDB
from app.api.deps import require_sales_claims
from app.models import (
    PricebookItem,
    get_next_pricebook_item_id,
)

router = APIRouter(tags=["pricebook"])

# Seed pricebook data
_pricebook_items = [
    PricebookItem(
        id=get_next_pricebook_item_id(),
        name="House Wash",
        description="Professional exterior house washing service",
        unit="sq_ft",
        base_price=0.15,  # $0.15 per sq ft
        formula="base_price * sq_ft + (stories - 1) * 50",
        category="house_wash",
    ),
    PricebookItem(
        id=get_next_pricebook_item_id(),
        name="Roof Wash",
        description="Soft wash roof cleaning with eco-friendly solution",
        unit="sq_ft",
        base_price=0.25,  # $0.25 per sq ft
        formula="base_price * sq_ft + (pitch_difficulty * 25)",
        category="roof_wash",
    ),
    PricebookItem(
        id=get_next_pricebook_item_id(),
        name="Gutter Cleaning",
        description="Complete gutter cleaning and flush",
        unit="linear_ft",
        base_price=1.50,  # $1.50 per linear ft
        formula="base_price * linear_ft",
        category="gutters",
    ),
    PricebookItem(
        id=get_next_pricebook_item_id(),
        name="Driveway Wash",
        description="High-pressure driveway and walkway cleaning",
        unit="sq_ft",
        base_price=0.20,  # $0.20 per sq ft
        formula="base_price * sq_ft",
        category="concrete",
    ),
    PricebookItem(
        id=get_next_pricebook_item_id(),
        name="Window Cleaning",
        description="Interior and exterior window cleaning",
        unit="each",
        base_price=8.00,  # $8 per window
        formula="base_price * window_count + (stories - 1) * 2",
        category="windows",
    ),
]


@router.get("/pricebook", response_model=List[dict])
def get_pricebook_items(
    category: str = None,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> List[dict]:
    """
    Get all pricebook items.

    Args:
        category: Optional category filter
        db: Database session
        claims: JWT claims

    Returns:
        List of pricebook items
    """
    items = _pricebook_items

    if category:
        items = [item for item in items if item.category == category]

    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "unit": item.unit,
            "base_price": item.base_price,
            "formula": item.formula,
            "category": item.category,
            "is_active": item.is_active,
            "created_at": item.created_at.isoformat(),
        }
        for item in items if item.is_active
    ]


@router.get("/pricebook/{item_id}", response_model=dict)
def get_pricebook_item(
    item_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> dict:
    """
    Get a specific pricebook item.

    Args:
        item_id: Pricebook item ID
        db: Database session
        claims: JWT claims

    Returns:
        Pricebook item
    """
    item = next((item for item in _pricebook_items if item.id == item_id), None)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricebook item not found"
        )

    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "unit": item.unit,
        "base_price": item.base_price,
        "formula": item.formula,
        "category": item.category,
        "is_active": item.is_active,
        "created_at": item.created_at.isoformat(),
    }


__all__ = ["router"]
