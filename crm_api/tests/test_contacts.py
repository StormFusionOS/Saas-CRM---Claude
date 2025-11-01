"""Tests for contacts and leads endpoints."""

import pytest
from app.api.routes.leads import create_contact, update_contact, delete_contact, get_leads_board
from app.schemas.contact import ContactCreate, ContactUpdate
from app.models import Contact, Lead, get_next_contact_id, get_next_lead_id
from datetime import datetime


def test_create_contact_success(db):
    """Test creating a new contact."""
    contact_data = ContactCreate(
        email="newcontact@example.com",
        first_name="New",
        last_name="Contact",
        phone="+1234567890"
    )

    claims = {"sub": "sales@example.com", "roles": ["SALES"]}
    result = create_contact(contact_data, db, claims)

    assert result.email == "newcontact@example.com"
    assert result.first_name == "New"
    assert result.id is not None


def test_create_duplicate_contact(db):
    """Test that creating duplicate email fails."""
    # Create first contact
    contact = Contact(
        id=get_next_contact_id(),
        email="duplicate@example.com",
        first_name="First",
        created_at=datetime.utcnow()
    )
    db.add(contact)
    db.commit()

    # Try to create duplicate
    contact_data = ContactCreate(email="duplicate@example.com")
    claims = {"sub": "sales@example.com", "roles": ["SALES"]}

    with pytest.raises(Exception) as exc_info:
        create_contact(contact_data, db, claims)

    assert "already exists" in str(exc_info.value).lower()


def test_update_contact(db):
    """Test updating a contact."""
    # Create contact
    contact = Contact(
        id=get_next_contact_id(),
        email="update@example.com",
        first_name="Old",
        created_at=datetime.utcnow()
    )
    db.add(contact)
    db.commit()

    # Update
    update_data = ContactUpdate(first_name="New", company="New Corp")
    claims = {"sub": "sales@example.com", "roles": ["SALES"]}

    result = update_contact(contact.id, update_data, db, claims)

    assert result.first_name == "New"
    assert result.company == "New Corp"
    assert result.updated_at is not None


def test_delete_contact_with_leads(db):
    """Test that contact with leads cannot be deleted."""
    # Create contact and lead
    contact = Contact(
        id=get_next_contact_id(),
        email="withleads@example.com",
        created_at=datetime.utcnow()
    )
    db.add(contact)
    db.commit()

    lead = Lead(
        id=get_next_lead_id(),
        contact_id=contact.id,
        status="NEW",
        created_at=datetime.utcnow()
    )
    db.add(lead)
    db.commit()

    claims = {"sub": "sales@example.com", "roles": ["SALES"]}

    with pytest.raises(Exception) as exc_info:
        delete_contact(contact.id, db, claims)

    assert "associated leads" in str(exc_info.value).lower()


def test_get_leads_board(db):
    """Test getting leads organized by status."""
    # Create contact and leads with different statuses
    contact = Contact(
        id=get_next_contact_id(),
        email="board@example.com",
        first_name="Board",
        created_at=datetime.utcnow()
    )
    db.add(contact)
    db.commit()

    for status in ["NEW", "CONTACTED", "QUALIFIED"]:
        lead = Lead(
            id=get_next_lead_id(),
            contact_id=contact.id,
            status=status,
            created_at=datetime.utcnow()
        )
        db.add(lead)
    db.commit()

    claims = {"sub": "sales@example.com", "roles": ["SALES"]}
    board = get_leads_board(None, db, claims)

    assert len(board.new) >= 1
    assert len(board.contacted) >= 1
    assert len(board.qualified) >= 1
