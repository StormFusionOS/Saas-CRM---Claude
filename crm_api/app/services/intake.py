"""
Lead intake service.

Handles ingestion of leads from various sources (webhooks, imports, etc.)
"""

from datetime import datetime
from typing import Dict, Optional
import structlog

from app.db import InMemoryDB
from app.models import (
    Contact,
    Lead,
    Interaction,
    LeadSource,
    InteractionType,
    get_next_contact_id,
    get_next_lead_id,
    get_next_interaction_id,
)


logger = structlog.get_logger(__name__)


def find_or_create_contact(
    db: InMemoryDB,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    **extra_fields
) -> Contact:
    """
    Find existing contact or create new one.

    Args:
        db: Database session
        email: Contact email
        phone: Contact phone
        first_name: First name
        last_name: Last name
        **extra_fields: Additional contact fields

    Returns:
        Contact instance
    """
    # Try to find existing contact by email
    if email:
        contact = db.query(Contact).filter(email=email).first()
        if contact:
            logger.info("found_existing_contact", contact_id=contact.id, email=email)
            return contact

    # Try to find by phone
    if phone:
        contact = db.query(Contact).filter(phone=phone).first()
        if contact:
            logger.info("found_existing_contact", contact_id=contact.id, phone=phone)
            return contact

    # Create new contact
    new_contact = Contact(
        id=get_next_contact_id(),
        email=email,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        company=extra_fields.get('company'),
        title=extra_fields.get('title'),
        tags=extra_fields.get('tags', []),
        custom_fields=extra_fields.get('custom_fields', {}),
        created_at=datetime.utcnow(),
    )

    db.add(new_contact)
    db.commit()

    logger.info("created_new_contact", contact_id=new_contact.id)

    return new_contact


def create_lead_if_needed(
    db: InMemoryDB,
    contact: Contact,
    source: str,
    metadata: Optional[Dict] = None
) -> Lead:
    """
    Create a new lead for contact if one doesn't exist.

    Args:
        db: Database session
        contact: Contact instance
        source: Lead source
        metadata: Additional metadata

    Returns:
        Lead instance
    """
    # Check for existing active lead
    existing_lead = db.query(Lead).filter(
        contact_id=contact.id
    ).first()

    # If lead exists and is not closed, return it
    if existing_lead and existing_lead.status not in ["WON", "LOST"]:
        logger.info("found_existing_lead", lead_id=existing_lead.id)
        return existing_lead

    # Create new lead
    new_lead = Lead(
        id=get_next_lead_id(),
        contact_id=contact.id,
        status="NEW",
        source=source,
        notes=metadata.get('notes', '') if metadata else '',
        created_at=datetime.utcnow(),
    )

    db.add(new_lead)
    db.commit()

    logger.info("created_new_lead", lead_id=new_lead.id, contact_id=contact.id)

    return new_lead


def create_interaction(
    db: InMemoryDB,
    contact: Contact,
    lead: Optional[Lead] = None,
    interaction_type: str = "WEBHOOK",
    subject: Optional[str] = None,
    body: str = "",
    metadata: Optional[Dict] = None
) -> Interaction:
    """
    Create an interaction record.

    Args:
        db: Database session
        contact: Contact instance
        lead: Optional lead instance
        interaction_type: Type of interaction
        subject: Interaction subject
        body: Interaction body
        metadata: Additional metadata

    Returns:
        Interaction instance
    """
    interaction = Interaction(
        id=get_next_interaction_id(),
        contact_id=contact.id,
        lead_id=lead.id if lead else None,
        interaction_type=interaction_type,
        direction="INBOUND",
        subject=subject,
        body=body,
        metadata=metadata or {},
        created_at=datetime.utcnow(),
    )

    db.add(interaction)

    # Update contact's last_contacted_at
    contact.last_contacted_at = datetime.utcnow()

    db.commit()

    logger.info(
        "created_interaction",
        interaction_id=interaction.id,
        contact_id=contact.id,
        type=interaction_type
    )

    return interaction


def ingest_lead_from_webhook(
    db: InMemoryDB,
    source: str,
    lead_data: Dict
) -> Dict:
    """
    Main ingestion pipeline for webhook leads.

    Args:
        db: Database session
        source: Lead source (FACEBOOK, GOOGLE, TWILIO, etc.)
        lead_data: Raw lead data from webhook

    Returns:
        Dict with contact, lead, and interaction IDs
    """
    logger.info("ingesting_lead", source=source)

    # Extract contact information
    email = lead_data.get('email')
    phone = lead_data.get('phone')
    first_name = lead_data.get('first_name')
    last_name = lead_data.get('last_name')

    if not email and not phone:
        raise ValueError("Lead must have either email or phone")

    # Find or create contact
    contact = find_or_create_contact(
        db=db,
        email=email,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        company=lead_data.get('company'),
        custom_fields=lead_data.get('custom_fields', {})
    )

    # Create lead if needed
    lead = create_lead_if_needed(
        db=db,
        contact=contact,
        source=source,
        metadata=lead_data
    )

    # Create initial interaction
    interaction_type = lead_data.get('interaction_type', 'WEBHOOK')
    subject = lead_data.get('subject')
    body = lead_data.get('body', '')

    # Build interaction body from lead data
    if not body and 'message' in lead_data:
        body = lead_data['message']
    elif not body and source == 'FACEBOOK':
        body = f"Lead from Facebook form {lead_data.get('form_id', 'unknown')}"
    elif not body and source == 'GOOGLE':
        body = f"Lead from Google Ads campaign {lead_data.get('campaign_id', 'unknown')}"

    interaction = create_interaction(
        db=db,
        contact=contact,
        lead=lead,
        interaction_type=interaction_type,
        subject=subject,
        body=body,
        metadata=lead_data
    )

    # Check for auto-reply rules (if enabled in config)
    # from app.core.config import settings
    # if settings.AUTO_REPLY_ENABLED:
    #     trigger_auto_reply(db, contact, lead, source)

    logger.info(
        "lead_ingested_successfully",
        contact_id=contact.id,
        lead_id=lead.id,
        interaction_id=interaction.id
    )

    return {
        "contact_id": contact.id,
        "lead_id": lead.id,
        "interaction_id": interaction.id,
    }


__all__ = [
    "find_or_create_contact",
    "create_lead_if_needed",
    "create_interaction",
    "ingest_lead_from_webhook",
]
