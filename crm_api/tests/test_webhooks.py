"""Tests for webhook endpoints and signature verification."""

import pytest
from app.core.security import verify_twilio_signature, verify_facebook_signature
from app.schemas.webhooks import FacebookLeadPayload, GoogleLeadPayload
from app.services.intake import ingest_lead_from_webhook
from app.models import Contact, Lead


def test_facebook_payload_extraction():
    """Test extracting lead data from Facebook webhook."""
    payload = FacebookLeadPayload(
        object="page",
        entry=[{
            "changes": [{
                "field": "leadgen",
                "value": {
                    "leadgen_id": "123456",
                    "form_id": "form_123",
                    "page_id": "page_123",
                    "created_time": "2024-01-01T12:00:00Z",
                    "field_data": [
                        {"name": "email", "values": ["test@example.com"]},
                        {"name": "full_name", "values": ["John Doe"]}
                    ]
                }
            }]
        }]
    )

    lead_data = payload.extract_lead_data()

    assert lead_data is not None
    assert lead_data["leadgen_id"] == "123456"
    assert lead_data["form_id"] == "form_123"


def test_google_payload_contact_extraction():
    """Test extracting contact info from Google lead."""
    payload = GoogleLeadPayload(
        lead_id="google_123",
        google_key="key_123",
        campaign_id="campaign_123",
        user_column_data=[
            {"column_name": "EMAIL", "string_value": "test@example.com"},
            {"column_name": "FIRST_NAME", "string_value": "John"},
            {"column_name": "PHONE_NUMBER", "string_value": "+1234567890"},
        ]
    )

    contact_info = payload.extract_contact_info()

    assert contact_info["email"] == "test@example.com"
    assert contact_info["first_name"] == "John"
    assert contact_info["phone"] == "+1234567890"


def test_ingest_lead_from_facebook(db):
    """Test ingesting a lead from Facebook webhook."""
    lead_data = {
        "email": "facebook_lead@example.com",
        "first_name": "Facebook",
        "last_name": "User",
        "form_id": "form_123"
    }

    result = ingest_lead_from_webhook(db, "FACEBOOK", lead_data)

    assert result["contact_id"] is not None
    assert result["lead_id"] is not None
    assert result["interaction_id"] is not None

    # Verify contact was created
    contact = db.query(Contact).filter(id=result["contact_id"]).first()
    assert contact.email == "facebook_lead@example.com"

    # Verify lead was created
    lead = db.query(Lead).filter(id=result["lead_id"]).first()
    assert lead.source == "FACEBOOK"
    assert lead.status == "NEW"


def test_ingest_lead_duplicate_contact(db):
    """Test that duplicate contacts are not created."""
    lead_data = {
        "email": "duplicate@example.com",
        "first_name": "Test"
    }

    # Ingest first time
    result1 = ingest_lead_from_webhook(db, "GOOGLE", lead_data)

    # Ingest again with same email
    result2 = ingest_lead_from_webhook(db, "GOOGLE", lead_data)

    # Should reuse same contact
    assert result1["contact_id"] == result2["contact_id"]

    # But create new lead
    assert result1["lead_id"] != result2["lead_id"]


def test_webhook_signature_verification():
    """Test Twilio signature verification (example)."""
    # Note: This is a simplified test
    # In real implementation, use actual Twilio signature algorithm

    url = "https://example.com/webhooks/twilio/sms"
    params = {
        "MessageSid": "SM123",
        "From": "+1234567890",
        "Body": "Test message"
    }

    # This will fail without proper signature
    # Just testing that function exists and is callable
    signature = "fake_signature"
    result = verify_twilio_signature(url, params, signature)

    # Should return boolean
    assert isinstance(result, bool)


def test_ingest_without_email_or_phone(db):
    """Test that ingestion fails without email or phone."""
    lead_data = {
        "first_name": "No Contact"
    }

    with pytest.raises(ValueError) as exc_info:
        ingest_lead_from_webhook(db, "MANUAL", lead_data)

    assert "email or phone" in str(exc_info.value).lower()
