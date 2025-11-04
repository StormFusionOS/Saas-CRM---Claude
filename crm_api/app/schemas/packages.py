"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Pydantic schemas for Packages & Bundles.

Request/response models for service packages.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Package Item Schemas
# ============================================================================


class PackageItemSchema(BaseModel):
    """Package item schema."""

    pricebook_item_id: int
    quantity: float = 1.0
    unit_override: Optional[str] = None
    description_override: Optional[str] = None
    price_override: Optional[float] = None
    is_optional: bool = False
    display_order: int = 0

    class Config:
        from_attributes = True


# ============================================================================
# Package Schemas
# ============================================================================


class PackageResponse(BaseModel):
    """Complete package response."""

    id: int
    name: str
    description: str
    category: str
    items: List[PackageItemSchema]
    pricing_type: str  # fixed, calculated
    fixed_price: Optional[float]
    discount_percent: float
    is_active: bool
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    image_url: str
    display_order: int
    featured: bool
    tags: List[str]
    terms: str
    requires_site_visit: bool
    times_sold: int
    total_revenue: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class PackageListItem(BaseModel):
    """Minimal package for list views."""

    id: int
    name: str
    description: str
    category: str
    pricing_type: str
    fixed_price: Optional[float]
    discount_percent: float
    is_active: bool
    featured: bool
    tags: List[str]
    item_count: int = Field(..., description="Number of items in package")
    created_at: datetime

    class Config:
        from_attributes = True


class PackageCalculationResponse(BaseModel):
    """Package price calculation response."""

    package_id: int
    package_name: str
    pricing_type: str
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Item details with prices")
    subtotal: float = Field(..., description="Sum of item prices")
    discount_percent: float
    discount_amount: float
    final_price: float
    savings: float = Field(..., description="Amount saved vs. individual items")

    class Config:
        json_schema_extra = {
            "example": {
                "package_id": 1,
                "package_name": "Spring Cleanup Special",
                "pricing_type": "calculated",
                "items": [
                    {"name": "Lawn Cleanup", "price": 150.00},
                    {"name": "Hedge Trimming", "price": 100.00},
                    {"name": "Mulching", "price": 80.00},
                ],
                "subtotal": 330.00,
                "discount_percent": 15.0,
                "discount_amount": 49.50,
                "final_price": 280.50,
                "savings": 49.50,
            }
        }
