"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Packages Service - Calculate pricing and manage packages.
"""

from typing import Dict, Any, List
from app.db import InMemoryDB
from app.models import Package


def calculate_package_price(db: InMemoryDB, package_id: int) -> Dict[str, Any]:
    """
    Calculate the price of a package.

    For fixed-price packages, returns the fixed price.
    For calculated packages, sums item prices and applies discount.

    Args:
        db: Database session
        package_id: Package ID

    Returns:
        Dict with price breakdown

    Raises:
        ValueError: If package not found
    """
    package = db.packages.get(package_id)
    if not package:
        raise ValueError(f"Package {package_id} not found")

    result = {
        "package_id": package.id,
        "package_name": package.name,
        "pricing_type": package.pricing_type,
        "items": [],
        "subtotal": 0.0,
        "discount_percent": package.discount_percent,
        "discount_amount": 0.0,
        "final_price": 0.0,
        "savings": 0.0,
    }

    if package.pricing_type == "fixed":
        # Fixed price package
        result["final_price"] = package.fixed_price or 0.0
        result["subtotal"] = package.fixed_price or 0.0
        return result

    # Calculated price - sum up items
    # NOTE: In a real implementation, we'd fetch actual prices from pricebook
    # For demo purposes, we'll use mock prices
    subtotal = 0.0
    for item in package.items:
        # Mock price lookup (in production, fetch from pricebook)
        mock_price = _get_mock_item_price(item.pricebook_item_id)

        item_price = item.price_override if item.price_override is not None else mock_price
        item_total = item_price * item.quantity

        result["items"].append({
            "pricebook_item_id": item.pricebook_item_id,
            "name": f"Service #{item.pricebook_item_id}",  # Mock name
            "quantity": item.quantity,
            "unit_price": item_price,
            "total": item_total,
            "is_optional": item.is_optional,
        })

        if not item.is_optional:
            subtotal += item_total

    result["subtotal"] = subtotal

    # Apply discount
    if package.discount_percent > 0:
        result["discount_amount"] = subtotal * (package.discount_percent / 100.0)
        result["final_price"] = subtotal - result["discount_amount"]
        result["savings"] = result["discount_amount"]
    else:
        result["final_price"] = subtotal

    return result


def _get_mock_item_price(pricebook_item_id: int) -> float:
    """
    Mock price lookup for demo purposes.

    In production, this would query the pricebook.

    Args:
        pricebook_item_id: Pricebook item ID

    Returns:
        Mock price
    """
    # Mock prices for demo
    mock_prices = {
        1: 150.00,  # Lawn Cleanup
        2: 100.00,  # Hedge Trimming
        3: 80.00,   # Mulching
        4: 75.00,   # Fertilization
        5: 50.00,   # Lawn Mowing
        6: 25.00,   # Edging
        7: 20.00,   # Blowing/Cleanup
        8: 200.00,  # Leaf Removal
        9: 150.00,  # Gutter Cleaning
        10: 100.00, # Winterization
    }
    return mock_prices.get(pricebook_item_id, 50.00)


def get_active_packages(
    db: InMemoryDB,
    category: str = None,
    featured_only: bool = False,
) -> List[Package]:
    """
    Get active packages, optionally filtered.

    Args:
        db: Database session
        category: Filter by category
        featured_only: Only return featured packages

    Returns:
        List of packages
    """
    packages = [p for p in db.packages.values() if p.is_active]

    if category:
        packages = [p for p in packages if p.category == category]

    if featured_only:
        packages = [p for p in packages if p.featured]

    # Sort by display_order, then name
    packages.sort(key=lambda p: (p.display_order, p.name))

    return packages
