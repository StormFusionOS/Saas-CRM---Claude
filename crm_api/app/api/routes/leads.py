"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Leads and contacts routes."""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db import get_db, InMemoryDB
from app.api.deps import require_sales_claims
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    LeadCreate,
    LeadUpdate,
    LeadStatusUpdate,
    LeadAssignUpdate,
    LeadResponse,
    LeadWithContact,
    LeadBoard,
    InteractionCreate,
    InteractionResponse,
)
from app.models import (
    Contact,
    Lead,
    Interaction,
    LeadStatus,
    get_next_contact_id,
    get_next_lead_id,
    get_next_interaction_id,
)


router = APIRouter(tags=["leads", "contacts"])


@router.get("/leads/unassigned", response_model=List[LeadWithContact])
def get_unassigned_leads(
    limit: int = Query(10, description="Maximum number of unassigned leads to return"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> List[LeadWithContact]:
    """
    Get unassigned leads sorted by age (oldest first).

    Args:
        limit: Maximum number of leads to return
        db: Database session
        claims: JWT claims

    Returns:
        List of unassigned leads with contact information
    """
    # Get all unassigned leads
    all_leads = db.query(Lead).all()
    unassigned = [lead for lead in all_leads if lead.assigned_to_id is None]

    # Sort by created_at (oldest first)
    unassigned.sort(key=lambda x: x.created_at)

    # Limit results
    unassigned = unassigned[:limit]

    # Get all contacts for lookup
    contacts = {c.id: c for c in db.query(Contact).all()}

    result = []
    for lead in unassigned:
        contact = contacts.get(lead.contact_id)
        if not contact:
            continue

        result.append(LeadWithContact(
            id=lead.id,
            contact_id=lead.contact_id,
            status=lead.status,
            source=lead.source,
            value=lead.value,
            assigned_to_id=lead.assigned_to_id,
            probability=lead.probability,
            expected_close_date=lead.expected_close_date,
            notes=lead.notes,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
            won_at=lead.won_at,
            lost_at=lead.lost_at,
            contact=ContactResponse(
                id=contact.id,
                email=contact.email,
                phone=contact.phone,
                first_name=contact.first_name,
                last_name=contact.last_name,
                company=contact.company,
                title=contact.title,
                tags=contact.tags,
                custom_fields=contact.custom_fields,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
                last_contacted_at=contact.last_contacted_at,
            )
        ))

    return result


@router.get("/leads/follow-ups-due", response_model=List[LeadWithContact])
def get_follow_ups_due(
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> List[LeadWithContact]:
    """
    Get leads with follow-ups due today.

    Args:
        db: Database session
        claims: JWT claims

    Returns:
        List of leads with follow-ups due today
    """
    from datetime import datetime, timedelta

    # Get today's date range
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Get all interactions
    all_interactions = db.query(Interaction).all()

    # Find interactions with next_step_at in metadata for today
    leads_due = set()
    for interaction in all_interactions:
        if interaction.lead_id and interaction.metadata:
            next_step_str = interaction.metadata.get('next_step_at')
            if next_step_str:
                try:
                    next_step = datetime.fromisoformat(next_step_str.replace('Z', '+00:00'))
                    if today_start <= next_step < today_end:
                        leads_due.add(interaction.lead_id)
                except (ValueError, AttributeError):
                    pass

    # Get leads
    all_leads = db.query(Lead).all()
    leads_to_return = [lead for lead in all_leads if lead.id in leads_due]

    # Get all contacts for lookup
    contacts = {c.id: c for c in db.query(Contact).all()}

    result = []
    for lead in leads_to_return:
        contact = contacts.get(lead.contact_id)
        if not contact:
            continue

        result.append(LeadWithContact(
            id=lead.id,
            contact_id=lead.contact_id,
            status=lead.status,
            source=lead.source,
            value=lead.value,
            assigned_to_id=lead.assigned_to_id,
            probability=lead.probability,
            expected_close_date=lead.expected_close_date,
            notes=lead.notes,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
            won_at=lead.won_at,
            lost_at=lead.lost_at,
            contact=ContactResponse(
                id=contact.id,
                email=contact.email,
                phone=contact.phone,
                first_name=contact.first_name,
                last_name=contact.last_name,
                company=contact.company,
                title=contact.title,
                tags=contact.tags,
                custom_fields=contact.custom_fields,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
                last_contacted_at=contact.last_contacted_at,
            )
        ))

    return result


@router.get("/leads", response_model=LeadBoard)
def get_leads_board(
    status_filter: str = Query(None, description="Filter by status"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> LeadBoard:
    """
    Get leads organized by status (kanban board).

    Args:
        status_filter: Optional status filter
        db: Database session
        claims: JWT claims

    Returns:
        Leads grouped by status
    """
    # Get all leads
    leads = db.query(Lead).all()

    # Get all contacts for lookup
    contacts = {c.id: c for c in db.query(Contact).all()}

    # Group leads by status
    board = LeadBoard()

    for lead in leads:
        if status_filter and lead.status != status_filter:
            continue

        contact = contacts.get(lead.contact_id)
        if not contact:
            continue

        lead_with_contact = LeadWithContact(
            id=lead.id,
            contact_id=lead.contact_id,
            status=lead.status,
            source=lead.source,
            value=lead.value,
            assigned_to_id=lead.assigned_to_id,
            probability=lead.probability,
            expected_close_date=lead.expected_close_date,
            notes=lead.notes,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
            won_at=lead.won_at,
            lost_at=lead.lost_at,
            contact=ContactResponse(
                id=contact.id,
                email=contact.email,
                phone=contact.phone,
                first_name=contact.first_name,
                last_name=contact.last_name,
                company=contact.company,
                title=contact.title,
                tags=contact.tags,
                custom_fields=contact.custom_fields,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
                last_contacted_at=contact.last_contacted_at,
            )
        )

        if lead.status == LeadStatus.NEW.value:
            board.new.append(lead_with_contact)
        elif lead.status == LeadStatus.CONTACTED.value:
            board.contacted.append(lead_with_contact)
        elif lead.status == LeadStatus.QUOTED.value:
            board.quoted.append(lead_with_contact)
        elif lead.status == LeadStatus.SCHEDULED.value:
            board.scheduled.append(lead_with_contact)
        elif lead.status == LeadStatus.WON.value:
            board.won.append(lead_with_contact)
        elif lead.status == LeadStatus.LOST.value:
            board.lost.append(lead_with_contact)

    return board


@router.get("/leads/{lead_id}", response_model=LeadWithContact)
def get_lead(
    lead_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> LeadWithContact:
    """Get lead by ID with contact details."""
    lead = db.query(Lead).filter(id=lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    contact = db.query(Contact).filter(id=lead.contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return LeadWithContact(
        id=lead.id,
        contact_id=lead.contact_id,
        status=lead.status,
        source=lead.source,
        value=lead.value,
        assigned_to_id=lead.assigned_to_id,
        probability=lead.probability,
        expected_close_date=lead.expected_close_date,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        won_at=lead.won_at,
        lost_at=lead.lost_at,
        contact=ContactResponse(
            id=contact.id,
            email=contact.email,
            phone=contact.phone,
            first_name=contact.first_name,
            last_name=contact.last_name,
            company=contact.company,
            title=contact.title,
            tags=contact.tags,
            custom_fields=contact.custom_fields,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            last_contacted_at=contact.last_contacted_at,
        )
    )


@router.get("/leads/{lead_id}/interactions", response_model=List[InteractionResponse])
def get_lead_interactions(
    lead_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> List[InteractionResponse]:
    """Get interaction timeline for a lead."""
    lead = db.query(Lead).filter(id=lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    interactions = db.query(Interaction).filter(lead_id=lead_id).all()

    return [
        InteractionResponse(
            id=i.id,
            contact_id=i.contact_id,
            lead_id=i.lead_id,
            user_id=i.user_id,
            interaction_type=i.interaction_type,
            direction=i.direction,
            subject=i.subject,
            body=i.body,
            metadata=i.metadata,
            created_at=i.created_at,
        )
        for i in sorted(interactions, key=lambda x: x.created_at, reverse=True)
    ]


@router.patch("/leads/{lead_id}/assign", response_model=LeadWithContact)
def assign_lead(
    lead_id: int,
    assign_update: LeadAssignUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> LeadWithContact:
    """
    Assign a lead to a user.

    Args:
        lead_id: Lead ID
        assign_update: Assignment update request
        db: Database session
        claims: JWT claims

    Returns:
        Updated lead with contact
    """
    lead = db.query(Lead).filter(id=lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Update assignment
    lead.assigned_to_id = assign_update.assigned_to_id
    lead.updated_at = datetime.utcnow()
    db.commit()

    # Get contact for response
    contact = db.query(Contact).filter(id=lead.contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return LeadWithContact(
        id=lead.id,
        contact_id=lead.contact_id,
        status=lead.status,
        source=lead.source,
        value=lead.value,
        assigned_to_id=lead.assigned_to_id,
        probability=lead.probability,
        expected_close_date=lead.expected_close_date,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        won_at=lead.won_at,
        lost_at=lead.lost_at,
        contact=ContactResponse(
            id=contact.id,
            email=contact.email,
            phone=contact.phone,
            first_name=contact.first_name,
            last_name=contact.last_name,
            company=contact.company,
            title=contact.title,
            tags=contact.tags,
            custom_fields=contact.custom_fields,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            last_contacted_at=contact.last_contacted_at,
        )
    )


@router.patch("/leads/{lead_id}/status", response_model=LeadWithContact)
def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> LeadWithContact:
    """
    Update lead status (for Kanban drag-drop).

    Args:
        lead_id: Lead ID
        status_update: Status update request
        db: Database session
        claims: JWT claims

    Returns:
        Updated lead with contact
    """
    lead = db.query(Lead).filter(id=lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Validate status
    valid_statuses = [s.value for s in LeadStatus]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Update status and timestamps
    lead.status = status_update.status
    lead.updated_at = datetime.utcnow()

    # Set won_at or lost_at if transitioning to those states
    if status_update.status == LeadStatus.WON.value and not lead.won_at:
        lead.won_at = datetime.utcnow()
    elif status_update.status == LeadStatus.LOST.value and not lead.lost_at:
        lead.lost_at = datetime.utcnow()

    db.commit()

    # Get contact for response
    contact = db.query(Contact).filter(id=lead.contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return LeadWithContact(
        id=lead.id,
        contact_id=lead.contact_id,
        status=lead.status,
        source=lead.source,
        value=lead.value,
        assigned_to_id=lead.assigned_to_id,
        probability=lead.probability,
        expected_close_date=lead.expected_close_date,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        won_at=lead.won_at,
        lost_at=lead.lost_at,
        contact=ContactResponse(
            id=contact.id,
            email=contact.email,
            phone=contact.phone,
            first_name=contact.first_name,
            last_name=contact.last_name,
            company=contact.company,
            title=contact.title,
            tags=contact.tags,
            custom_fields=contact.custom_fields,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            last_contacted_at=contact.last_contacted_at,
        )
    )


@router.post("/leads/{lead_id}/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_lead_interaction(
    lead_id: int,
    interaction: InteractionCreate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> InteractionResponse:
    """
    Create a new interaction for a lead.

    Args:
        lead_id: Lead ID
        interaction: Interaction create request
        db: Database session
        claims: JWT claims

    Returns:
        Created interaction
    """
    lead = db.query(Lead).filter(id=lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Verify contact exists
    contact = db.query(Contact).filter(id=interaction.contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Create interaction
    new_interaction = Interaction(
        id=get_next_interaction_id(),
        contact_id=interaction.contact_id,
        lead_id=lead_id,
        user_id=interaction.user_id or claims.get('user_id'),
        interaction_type=interaction.interaction_type,
        direction=interaction.direction,
        subject=interaction.subject,
        body=interaction.body,
        metadata=interaction.metadata,
        created_at=datetime.utcnow(),
    )

    db.add(new_interaction)

    # Update contact's last_contacted_at
    contact.last_contacted_at = datetime.utcnow()

    db.commit()

    return InteractionResponse(
        id=new_interaction.id,
        contact_id=new_interaction.contact_id,
        lead_id=new_interaction.lead_id,
        user_id=new_interaction.user_id,
        interaction_type=new_interaction.interaction_type,
        direction=new_interaction.direction,
        subject=new_interaction.subject,
        body=new_interaction.body,
        metadata=new_interaction.metadata,
        created_at=new_interaction.created_at,
    )


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: ContactCreate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> ContactResponse:
    """Create a new contact."""
    # Check for existing contact with same email
    if contact.email:
        existing = db.query(Contact).filter(email=contact.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact with this email already exists"
            )

    # Create contact
    new_contact = Contact(
        id=get_next_contact_id(),
        email=contact.email,
        phone=contact.phone,
        first_name=contact.first_name,
        last_name=contact.last_name,
        company=contact.company,
        title=contact.title,
        tags=contact.tags,
        custom_fields=contact.custom_fields,
        created_at=datetime.utcnow(),
    )

    db.add(new_contact)
    db.commit()

    return ContactResponse(
        id=new_contact.id,
        email=new_contact.email,
        phone=new_contact.phone,
        first_name=new_contact.first_name,
        last_name=new_contact.last_name,
        company=new_contact.company,
        title=new_contact.title,
        tags=new_contact.tags,
        custom_fields=new_contact.custom_fields,
        created_at=new_contact.created_at,
        updated_at=new_contact.updated_at,
        last_contacted_at=new_contact.last_contacted_at,
    )


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
) -> ContactResponse:
    """Update existing contact."""
    contact = db.query(Contact).filter(id=contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Update fields
    if contact_update.email is not None:
        contact.email = contact_update.email
    if contact_update.phone is not None:
        contact.phone = contact_update.phone
    if contact_update.first_name is not None:
        contact.first_name = contact_update.first_name
    if contact_update.last_name is not None:
        contact.last_name = contact_update.last_name
    if contact_update.company is not None:
        contact.company = contact_update.company
    if contact_update.title is not None:
        contact.title = contact_update.title
    if contact_update.tags:
        contact.tags = contact_update.tags
    if contact_update.custom_fields:
        contact.custom_fields = contact_update.custom_fields

    contact.updated_at = datetime.utcnow()
    db.commit()

    return ContactResponse(
        id=contact.id,
        email=contact.email,
        phone=contact.phone,
        first_name=contact.first_name,
        last_name=contact.last_name,
        company=contact.company,
        title=contact.title,
        tags=contact.tags,
        custom_fields=contact.custom_fields,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        last_contacted_at=contact.last_contacted_at,
    )


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims)
):
    """Delete a contact."""
    contact = db.query(Contact).filter(id=contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Check for associated leads
    leads = db.query(Lead).filter(contact_id=contact_id).all()
    if leads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete contact with associated leads"
        )

    db.delete(contact)
    db.commit()


__all__ = ["router"]
