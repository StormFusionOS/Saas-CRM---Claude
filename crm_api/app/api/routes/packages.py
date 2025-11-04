"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Packages & Bundles API Routes.

Endpoints for managing service packages.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db import get_db, InMemoryDB
from app.schemas.packages import (
    PackageResponse,
    PackageListItem,
    PackageItemSchema,
    PackageCalculationResponse,
)
from app.services import packages_service
from app.api.deps import require_sales_claims


router = APIRouter(tags=["packages"])


# ============================================================================
# Package Endpoints
# ============================================================================


@router.get("/packages", response_model=List[PackageListItem])
def list_packages(
    category: Optional[str] = None,
    featured: bool = False,
    is_active: Optional[bool] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[PackageListItem]:
    """
    List all packages (STAFF ONLY).

    Filters:
    - category: Filter by package category
    - featured: Only show featured packages
    - is_active: Filter by active/inactive status
    """
    packages = list(db.packages.values())

    # Apply filters
    if is_active is not None:
        packages = [p for p in packages if p.is_active == is_active]

    if category:
        packages = [p for p in packages if p.category == category]

    if featured:
        packages = [p for p in packages if p.featured]

    # Sort by display_order, then name
    packages.sort(key=lambda p: (p.display_order, p.name))

    # Build response
    return [
        PackageListItem(
            id=pkg.id,
            name=pkg.name,
            description=pkg.description,
            category=pkg.category,
            pricing_type=pkg.pricing_type,
            fixed_price=pkg.fixed_price,
            discount_percent=pkg.discount_percent,
            is_active=pkg.is_active,
            featured=pkg.featured,
            tags=pkg.tags,
            item_count=len(pkg.items),
            created_at=pkg.created_at,
        )
        for pkg in packages
    ]


@router.get("/packages/{package_id}", response_model=PackageResponse)
def get_package(
    package_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PackageResponse:
    """
    Get package details (STAFF ONLY).
    """
    package = db.packages.get(package_id)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found",
        )

    # Convert items to schema
    items = [PackageItemSchema(**item.__dict__) for item in package.items]

    return PackageResponse(
        id=package.id,
        name=package.name,
        description=package.description,
        category=package.category,
        items=items,
        pricing_type=package.pricing_type,
        fixed_price=package.fixed_price,
        discount_percent=package.discount_percent,
        is_active=package.is_active,
        valid_from=package.valid_from,
        valid_to=package.valid_to,
        image_url=package.image_url,
        display_order=package.display_order,
        featured=package.featured,
        tags=package.tags,
        terms=package.terms,
        requires_site_visit=package.requires_site_visit,
        times_sold=package.times_sold,
        total_revenue=package.total_revenue,
        metadata=package.metadata,
        created_at=package.created_at,
        updated_at=package.updated_at,
        created_by=package.created_by,
    )


@router.get("/packages/{package_id}/calculate", response_model=PackageCalculationResponse)
def calculate_package_price(
    package_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> PackageCalculationResponse:
    """
    Calculate package pricing (STAFF ONLY).

    Returns price breakdown including:
    - Individual item prices
    - Subtotal
    - Discount amount
    - Final price
    - Total savings
    """
    try:
        calculation = packages_service.calculate_package_price(db, package_id)
        return PackageCalculationResponse(**calculation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Public Package Endpoints (for customer-facing applications)
# ============================================================================


@router.get("/packages/public/featured", response_model=List[PackageListItem])
def list_featured_packages(
    db: InMemoryDB = Depends(get_db),
) -> List[PackageListItem]:
    """
    List featured packages (PUBLIC - no auth required).

    Returns only active, featured packages for customer-facing display.
    """
    packages = [
        p for p in db.packages.values()
        if p.is_active and p.featured
    ]

    # Sort by display_order, then name
    packages.sort(key=lambda p: (p.display_order, p.name))

    # Build response
    return [
        PackageListItem(
            id=pkg.id,
            name=pkg.name,
            description=pkg.description,
            category=pkg.category,
            pricing_type=pkg.pricing_type,
            fixed_price=pkg.fixed_price,
            discount_percent=pkg.discount_percent,
            is_active=pkg.is_active,
            featured=pkg.featured,
            tags=pkg.tags,
            item_count=len(pkg.items),
            created_at=pkg.created_at,
        )
        for pkg in packages
    ]
