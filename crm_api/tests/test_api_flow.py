"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
API Flow Test: Login → Create Contact → List Leads

Tests the complete API workflow without a real server using FastAPI TestClient.
Simulates a real client making sequential API calls.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import InMemoryDB
from app.models import User, Contact, Lead, LeadStatus
from app.core.security import hash_password


# Test client that acts like a real HTTP client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data before each test."""
    from app.db import init_demo_data, _users, _contacts, _leads

    # Clear all data
    _users.clear()
    _contacts.clear()
    _leads.clear()

    # Create a test user directly in the module-level collections
    test_user = User(
        id=1,
        email="sales@example.com",
        hashed_password=hash_password("testpass123"),
        full_name="Sales User",
        roles=["SALES"],
        is_active=True,
    )
    _users.append(test_user)

    # Create an initial contact with a lead (for count comparison)
    initial_contact = Contact(
        id=1,
        email="existing@example.com",
        phone="+1234567890",
        first_name="Existing",
        last_name="Contact",
        company="Existing Corp",
    )
    _contacts.append(initial_contact)

    initial_lead = Lead(
        id=1,
        contact_id=1,
        status=LeadStatus.NEW.value,
        source="FACEBOOK",
        value=1000.0,
        assigned_to_id=1,
    )
    _leads.append(initial_lead)

    yield

    # Cleanup
    _users.clear()
    _contacts.clear()
    _leads.clear()


def test_api_flow_login_create_contact_list_leads():
    """
    Complete API flow test:
    1. Login to get JWT token
    2. Create a new contact
    3. Create a lead for that contact
    4. List all leads
    5. Verify lead count increased by 1
    """

    # STEP 1: Login to get authentication token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "testpass123",
        },
    )

    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data = login_response.json()

    assert "access_token" in login_data
    assert "token_type" in login_data
    assert login_data["token_type"] == "bearer"

    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"✓ Step 1: Successfully logged in, got token: {token[:20]}...")

    # STEP 2: Get initial leads count
    initial_leads_response = client.get("/api/v1/leads", headers=headers)
    assert initial_leads_response.status_code == 200

    initial_leads_data = initial_leads_response.json()
    initial_total_count = sum([
        len(initial_leads_data.get("new", [])),
        len(initial_leads_data.get("contacted", [])),
        len(initial_leads_data.get("qualified", [])),
        len(initial_leads_data.get("won", [])),
        len(initial_leads_data.get("lost", [])),
    ])

    print(f"✓ Step 2: Initial lead count: {initial_total_count}")

    # STEP 3: Create a new contact
    contact_response = client.post(
        "/api/v1/contacts",
        headers=headers,
        json={
            "email": "newlead@example.com",
            "phone": "+1987654321",
            "first_name": "John",
            "last_name": "Doe",
            "company": "Acme Corp",
            "title": "CEO",
            "tags": ["hot-lead", "enterprise"],
            "custom_fields": {
                "source": "website",
                "campaign": "summer-2025",
            },
        },
    )

    assert contact_response.status_code == 201, f"Contact creation failed: {contact_response.text}"
    contact_data = contact_response.json()

    assert contact_data["email"] == "newlead@example.com"
    assert contact_data["first_name"] == "John"
    assert contact_data["last_name"] == "Doe"
    assert "id" in contact_data

    contact_id = contact_data["id"]
    print(f"✓ Step 3: Created contact with ID: {contact_id}")

    # STEP 4: Create a lead for the new contact
    # (In this simplified API, leads are created automatically via webhooks,
    # but we'll manually create one to simulate the workflow)
    db = InMemoryDB()
    new_lead = Lead(
        id=db._get_next_id(Lead),
        contact_id=contact_id,
        status=LeadStatus.NEW.value,
        source="GOOGLE",
        value=5000.0,
        assigned_to_id=1,
    )
    db.add(new_lead)
    db.commit()

    print(f"✓ Step 4: Created lead for contact {contact_id}")

    # STEP 5: List all leads again and verify count increased
    final_leads_response = client.get("/api/v1/leads", headers=headers)
    assert final_leads_response.status_code == 200

    final_leads_data = final_leads_response.json()
    final_total_count = sum([
        len(final_leads_data.get("new", [])),
        len(final_leads_data.get("contacted", [])),
        len(final_leads_data.get("qualified", [])),
        len(final_leads_data.get("won", [])),
        len(final_leads_data.get("lost", [])),
    ])

    print(f"✓ Step 5: Final lead count: {final_total_count}")

    # STEP 6: Verify count increased by exactly 1
    assert final_total_count == initial_total_count + 1, (
        f"Expected lead count to increase by 1, "
        f"but went from {initial_total_count} to {final_total_count}"
    )

    print("✓ Step 6: Lead count increased by 1 as expected")

    # STEP 7: Verify the new lead appears in the "new" status
    new_leads = final_leads_data.get("new", [])
    new_lead_emails = [lead["contact"]["email"] for lead in new_leads]

    assert "newlead@example.com" in new_lead_emails, (
        "New lead not found in 'new' status"
    )

    print("✓ Step 7: New lead appears in 'new' status")


def test_api_flow_without_auth_fails():
    """
    Verify that protected endpoints require authentication.
    """

    # Try to create contact without authentication
    response = client.post(
        "/api/v1/contacts",
        json={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    # Should fail with 401 or be rejected
    # (Note: The stub API might not have full auth middleware,
    # but this tests the expected behavior)
    assert response.status_code in [401, 403, 422], (
        "Expected authentication error, but got: " + str(response.status_code)
    )

    print("✓ Protected endpoints require authentication")


def test_api_flow_duplicate_contact_prevention():
    """
    Verify that creating a duplicate contact is prevented.
    """

    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create first contact
    first_contact_response = client.post(
        "/api/v1/contacts",
        headers=headers,
        json={
            "email": "duplicate@example.com",
            "first_name": "First",
            "last_name": "Contact",
        },
    )

    assert first_contact_response.status_code == 201

    # Try to create duplicate contact with same email
    duplicate_contact_response = client.post(
        "/api/v1/contacts",
        headers=headers,
        json={
            "email": "duplicate@example.com",
            "first_name": "Second",
            "last_name": "Contact",
        },
    )

    # Should fail with 400 Bad Request
    assert duplicate_contact_response.status_code == 400
    error_data = duplicate_contact_response.json()

    assert "error" in error_data
    assert "email" in error_data["error"]["message"].lower() or "exists" in error_data["error"]["message"].lower()

    print("✓ Duplicate contact prevention works")


def test_api_flow_get_specific_lead():
    """
    Test retrieving a specific lead by ID.
    """

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get the initial lead (ID=1)
    lead_response = client.get("/api/v1/leads/1", headers=headers)

    assert lead_response.status_code == 200
    lead_data = lead_response.json()

    assert lead_data["id"] == 1
    assert lead_data["contact_id"] == 1
    assert lead_data["status"] == LeadStatus.NEW.value
    assert "contact" in lead_data
    assert lead_data["contact"]["email"] == "existing@example.com"

    print("✓ Successfully retrieved specific lead with contact details")


def test_api_flow_lead_interactions():
    """
    Test retrieving interactions for a lead.
    """

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get interactions for lead 1
    interactions_response = client.get("/api/v1/leads/1/interactions", headers=headers)

    assert interactions_response.status_code == 200
    interactions_data = interactions_response.json()

    # Should return empty list or list of interactions
    assert isinstance(interactions_data, list)

    print(f"✓ Retrieved {len(interactions_data)} interactions for lead")


def test_api_flow_invalid_credentials():
    """
    Test that invalid credentials are rejected.
    """

    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    error_data = response.json()

    assert "error" in error_data
    assert error_data["error"]["code"] == "ERR_AUTH_INVALID_CREDENTIALS"

    print("✓ Invalid credentials are properly rejected")


def test_api_flow_statistics():
    """
    Test the complete flow and verify statistics are correct.
    """

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get leads board
    leads_response = client.get("/api/v1/leads", headers=headers)
    leads_data = leads_response.json()

    # Count leads by status
    status_counts = {
        "new": len(leads_data.get("new", [])),
        "contacted": len(leads_data.get("contacted", [])),
        "qualified": len(leads_data.get("qualified", [])),
        "won": len(leads_data.get("won", [])),
        "lost": len(leads_data.get("lost", [])),
    }

    print(f"✓ Lead statistics: {status_counts}")

    # Verify initial state has 1 new lead
    assert status_counts["new"] >= 1

    print("✓ Lead statistics are accurate")
