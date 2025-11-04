"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Estimates routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db import get_db, InMemoryDB
from app.api.deps import require_sales_claims
from app.models import (
    Estimate,
    Job,
    Lead,
    LeadStatus,
    get_next_estimate_id,
    get_next_job_id,
)
from app.api.routes.pricebook import _pricebook_items
from app.services.formula_engine import FormulaEngine

router = APIRouter(tags=["estimates"])

# In-memory storage
_estimates: List[Estimate] = []
_jobs: List[Job] = []


class QuoteRequest(BaseModel):
    """Request to generate a quote."""
    lead_id: int
    service_ids: List[int]
    inputs: Dict[str, Any]  # e.g., {"sq_ft": 2500, "stories": 2}


class AcceptEstimateRequest(BaseModel):
    """Request to accept an estimate."""
    selected_tier: str  # "good", "better", "best"


def evaluate_formula(formula: str, inputs: Dict[str, Any], base_price: float) -> float:
    """
    Safely evaluate a pricing formula using the FormulaEngine.

    Args:
        formula: Formula string (e.g., "base_price * sq_ft + (stories - 1) * 50")
        inputs: Input variables (e.g., {"sq_ft": 2500, "stories": 2})
        base_price: Base price from pricebook

    Returns:
        Calculated price
    """
    result = FormulaEngine.evaluate(formula, inputs, base_price)

    if not result.success:
        raise ValueError(result.error)

    return result.result


@router.post("/estimates/quote", response_model=dict)
def create_quote(
    request: QuoteRequest,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> dict:
    """
    Generate a Good/Better/Best quote for a lead.

    Args:
        request: Quote request with lead_id, service_ids, and inputs
        db: Database session
        claims: JWT claims

    Returns:
        Estimate with three pricing tiers
    """
    # Validate lead exists
    lead = db.query(Lead).filter(id=request.lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Fetch pricebook items
    selected_services = [
        item for item in _pricebook_items
        if item.id in request.service_ids and item.is_active
    ]

    if not selected_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid services selected"
        )

    # Calculate base prices for each service
    service_prices = []
    for service in selected_services:
        try:
            price = evaluate_formula(service.formula, request.inputs, service.base_price)
            service_prices.append({
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "price": round(price, 2)
            })
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error calculating price for {service.name}: {str(e)}"
            )

    base_total = sum(item["price"] for item in service_prices)

    # Calculate Good/Better/Best tiers
    # Good: Base pricing
    good_tier = {
        "name": "Good",
        "price": round(base_total, 2),
        "items": service_prices.copy(),
        "features": [
            "Standard service",
            "Basic equipment",
            "Email support"
        ]
    }

    # Better: Base + 30% with added features
    better_multiplier = 1.30
    better_tier = {
        "name": "Better",
        "price": round(base_total * better_multiplier, 2),
        "items": [
            {**item, "price": round(item["price"] * better_multiplier, 2)}
            for item in service_prices
        ],
        "features": [
            "Premium service",
            "Professional-grade equipment",
            "Priority scheduling",
            "Phone & email support",
            "30-day satisfaction guarantee"
        ]
    }

    # Best: Base + 60% with premium features
    best_multiplier = 1.60
    best_tier = {
        "name": "Best",
        "price": round(base_total * best_multiplier, 2),
        "items": [
            {**item, "price": round(item["price"] * best_multiplier, 2)}
            for item in service_prices
        ],
        "features": [
            "Premium service with extras",
            "Commercial-grade equipment",
            "Priority scheduling + flexibility",
            "24/7 phone & email support",
            "90-day satisfaction guarantee",
            "Quarterly maintenance included",
            "Free touch-ups within 30 days"
        ]
    }

    # Create estimate
    estimate = Estimate(
        id=get_next_estimate_id(),
        lead_id=request.lead_id,
        contact_id=lead.contact_id,
        service_ids=request.service_ids,
        inputs=request.inputs,
        good_tier=good_tier,
        better_tier=better_tier,
        best_tier=best_tier,
        status="draft",
        created_at=datetime.utcnow()
    )

    _estimates.append(estimate)

    return {
        "id": estimate.id,
        "lead_id": estimate.lead_id,
        "contact_id": estimate.contact_id,
        "good_tier": good_tier,
        "better_tier": better_tier,
        "best_tier": best_tier,
        "status": estimate.status,
        "created_at": estimate.created_at.isoformat(),
    }


@router.post("/estimates/{estimate_id}/accept", response_model=dict)
def accept_estimate(
    estimate_id: int,
    request: AcceptEstimateRequest,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> dict:
    """
    Accept an estimate and create a job.

    Args:
        estimate_id: Estimate ID
        request: Acceptance request with selected tier
        db: Database session
        claims: JWT claims

    Returns:
        Created job details
    """
    # Find estimate
    estimate = next((e for e in _estimates if e.id == estimate_id), None)
    if not estimate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimate not found"
        )

    if estimate.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estimate has already been processed"
        )

    # Validate selected tier
    tier_map = {
        "good": estimate.good_tier,
        "better": estimate.better_tier,
        "best": estimate.best_tier,
    }

    if request.selected_tier not in tier_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier selected. Must be 'good', 'better', or 'best'"
        )

    selected_tier_data = tier_map[request.selected_tier]
    total_price = selected_tier_data["price"]

    # Calculate deposit (25% of total)
    deposit_amount = round(total_price * 0.25, 2)
    deposit_due = datetime.utcnow() + timedelta(days=7)  # Due in 7 days

    # Update estimate
    estimate.selected_tier = request.selected_tier
    estimate.deposit_amount = deposit_amount
    estimate.deposit_due = deposit_due
    estimate.status = "accepted"
    estimate.accepted_at = datetime.utcnow()
    estimate.updated_at = datetime.utcnow()

    # Update lead status to WON
    lead = db.query(Lead).filter(id=estimate.lead_id).first()
    if lead:
        lead.status = LeadStatus.WON.value
        lead.won_at = datetime.utcnow()
        lead.updated_at = datetime.utcnow()
        lead.value = total_price
        db.commit()

    # Create job
    job = Job(
        id=get_next_job_id(),
        lead_id=estimate.lead_id,
        estimate_id=estimate.id,
        contact_id=estimate.contact_id,
        title=f"{selected_tier_data['name']} Package - {', '.join([item['name'] for item in selected_tier_data['items']])}",
        total_price=total_price,
        deposit_amount=deposit_amount,
        deposit_paid=False,
        status="pending",
        created_at=datetime.utcnow()
    )

    _jobs.append(job)

    return {
        "job_id": job.id,
        "lead_id": job.lead_id,
        "estimate_id": estimate.id,
        "title": job.title,
        "total_price": job.total_price,
        "deposit_amount": job.deposit_amount,
        "deposit_due": deposit_due.isoformat(),
        "status": job.status,
        "created_at": job.created_at.isoformat(),
    }


@router.get("/estimates/{estimate_id}", response_model=dict)
def get_estimate(
    estimate_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> dict:
    """
    Get an estimate by ID.

    Args:
        estimate_id: Estimate ID
        db: Database session
        claims: JWT claims

    Returns:
        Estimate details
    """
    estimate = next((e for e in _estimates if e.id == estimate_id), None)
    if not estimate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimate not found"
        )

    return {
        "id": estimate.id,
        "lead_id": estimate.lead_id,
        "contact_id": estimate.contact_id,
        "good_tier": estimate.good_tier,
        "better_tier": estimate.better_tier,
        "best_tier": estimate.best_tier,
        "selected_tier": estimate.selected_tier,
        "deposit_amount": estimate.deposit_amount,
        "deposit_due": estimate.deposit_due.isoformat() if estimate.deposit_due else None,
        "status": estimate.status,
        "created_at": estimate.created_at.isoformat(),
        "accepted_at": estimate.accepted_at.isoformat() if estimate.accepted_at else None,
    }


__all__ = ["router"]
