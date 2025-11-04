"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
SMS / Text Hub Schemas.

Pydantic models for SMS messaging, conversations, and templates.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# SMS Message Schemas
# ============================================================================


class SMSMessageSend(BaseModel):
    """Request to send an SMS message."""

    to_number: str = Field(..., description="Recipient phone number in E.164 format")
    body: str = Field(..., description="Message body (max 1600 chars for concatenated SMS)")
    contact_id: Optional[int] = Field(None, description="Associated contact ID")
    lead_id: Optional[int] = Field(None, description="Associated lead ID")
    template_id: Optional[int] = Field(None, description="Template used (if any)")

    class Config:
        json_schema_extra = {
            "example": {
                "to_number": "+15551234567",
                "body": "Hi John! Just wanted to check if you had any questions about the quote we sent.",
                "contact_id": 1,
                "lead_id": 1,
            }
        }


class SMSMessageResponse(BaseModel):
    """Full SMS message details."""

    id: int
    conversation_id: Optional[int]
    contact_id: Optional[int]
    lead_id: Optional[int]
    from_number: str
    to_number: str
    body: str
    direction: str  # inbound, outbound
    status: str  # pending, sent, delivered, failed, received
    provider: str
    provider_message_id: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: str
    sent_by: Optional[int]
    template_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SMSMessageListItem(BaseModel):
    """Abbreviated message info for lists."""

    id: int
    conversation_id: Optional[int]
    from_number: str
    to_number: str
    body: str
    direction: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SMS Conversation Schemas
# ============================================================================


class SMSConversationResponse(BaseModel):
    """Full conversation details."""

    id: int
    contact_id: Optional[int]
    phone_number: str
    status: str  # active, archived, blocked
    message_count: int
    unread_count: int
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str] = None
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SMSConversationListItem(BaseModel):
    """Abbreviated conversation for lists."""

    id: int
    contact_id: Optional[int]
    phone_number: str
    status: str
    message_count: int
    unread_count: int
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str]
    assigned_to: Optional[int]

    class Config:
        from_attributes = True


class SMSConversationUpdate(BaseModel):
    """Update conversation metadata."""

    status: Optional[str] = Field(None, description="active, archived, blocked")
    assigned_to: Optional[int] = Field(None, description="Assign to staff member")
    mark_read: Optional[bool] = Field(None, description="Mark all messages as read")


# ============================================================================
# SMS Template Schemas
# ============================================================================


class SMSTemplateCreate(BaseModel):
    """Create a new SMS template."""

    name: str = Field(..., description="Template name")
    category: str = Field("general", description="Template category")
    body: str = Field(..., description="Template body with {{variables}}")
    variables: List[str] = Field(default_factory=list, description="Variable names used")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Appointment Reminder",
                "category": "scheduling",
                "body": "Hi {{first_name}}! Reminder: appointment on {{date}} at {{time}}.",
                "variables": ["first_name", "date", "time"],
            }
        }


class SMSTemplateUpdate(BaseModel):
    """Update an SMS template."""

    name: Optional[str] = None
    category: Optional[str] = None
    body: Optional[str] = None
    is_active: Optional[bool] = None
    variables: Optional[List[str]] = None


class SMSTemplateResponse(BaseModel):
    """Full template details."""

    id: int
    name: str
    category: str
    body: str
    is_active: bool
    times_used: int
    variables: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class SMSTemplateListItem(BaseModel):
    """Abbreviated template for lists."""

    id: int
    name: str
    category: str
    body: str
    is_active: bool
    times_used: int

    class Config:
        from_attributes = True


# ============================================================================
# SMS Stats Schema
# ============================================================================


class SMSStatsResponse(BaseModel):
    """SMS usage statistics."""

    total_messages: int
    total_sent: int
    total_received: int
    total_delivered: int
    total_failed: int
    active_conversations: int
    unread_count: int
    last_message_at: Optional[datetime]

    class Config:
        from_attributes = True
