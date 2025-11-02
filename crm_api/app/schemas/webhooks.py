"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Webhook payload schemas."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class FacebookLeadPayload(BaseModel):
    """Facebook lead ads webhook payload."""

    object: str  # Should be "page"
    entry: List[Dict]

    def extract_lead_data(self) -> Optional[Dict]:
        """Extract lead data from webhook payload."""
        try:
            for entry_item in self.entry:
                if "changes" in entry_item:
                    for change in entry_item["changes"]:
                        if change.get("field") == "leadgen":
                            leadgen_data = change.get("value", {})
                            return {
                                "leadgen_id": leadgen_data.get("leadgen_id"),
                                "form_id": leadgen_data.get("form_id"),
                                "page_id": leadgen_data.get("page_id"),
                                "created_time": leadgen_data.get("created_time"),
                                "field_data": leadgen_data.get("field_data", []),
                            }
        except Exception:
            return None
        return None


class GoogleLeadPayload(BaseModel):
    """Google Ads lead form webhook payload."""

    lead_id: str
    google_key: str
    campaign_id: Optional[str] = None
    user_column_data: Optional[List[Dict]] = None

    def extract_contact_info(self) -> Dict:
        """Extract contact information from lead data."""
        contact_info = {
            "email": None,
            "phone": None,
            "first_name": None,
            "last_name": None,
        }

        if self.user_column_data:
            for field in self.user_column_data:
                column_name = field.get("column_name", "").lower()
                value = field.get("string_value", "")

                if "email" in column_name:
                    contact_info["email"] = value
                elif "phone" in column_name:
                    contact_info["phone"] = value
                elif "first" in column_name or "given" in column_name:
                    contact_info["first_name"] = value
                elif "last" in column_name or "family" in column_name:
                    contact_info["last_name"] = value

        return contact_info


class TwilioSMSPayload(BaseModel):
    """Twilio SMS webhook payload."""

    MessageSid: str
    AccountSid: str
    From: str
    To: str
    Body: str
    NumMedia: Optional[str] = "0"
    MediaUrl0: Optional[str] = None


class TwilioVoicePayload(BaseModel):
    """Twilio Voice webhook payload."""

    CallSid: str
    AccountSid: str
    From: str
    To: str
    CallStatus: str
    Direction: str
    CallerName: Optional[str] = None
    RecordingUrl: Optional[str] = None


class WebhookVerification(BaseModel):
    """Webhook verification response."""

    verified: bool
    message: Optional[str] = None


__all__ = [
    "FacebookLeadPayload",
    "GoogleLeadPayload",
    "TwilioSMSPayload",
    "TwilioVoicePayload",
    "WebhookVerification",
]
