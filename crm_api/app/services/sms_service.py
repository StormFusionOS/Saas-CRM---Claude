"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
SMS Service - Send/receive SMS messages via Twilio.

NOTE: This is a mock implementation for demo purposes.
In production, this would integrate with Twilio API using their SDK:
- Install: pip install twilio
- from twilio.rest import Client
- client = Client(account_sid, auth_token)
- message = client.messages.create(to=to_number, from_=from_number, body=body)
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from app.db import InMemoryDB
from app.models import (
    SMSMessage,
    SMSConversation,
    SMSTemplate,
    get_next_sms_message_id,
    get_next_sms_conversation_id,
)


def send_sms(
    db: InMemoryDB,
    to_number: str,
    body: str,
    contact_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    template_id: Optional[int] = None,
    sent_by: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Send an SMS message.

    In production, this would:
    1. Validate phone number format
    2. Call Twilio API to send message
    3. Store message record
    4. Update or create conversation thread

    Args:
        db: Database session
        to_number: Recipient phone number (E.164 format)
        body: Message text
        contact_id: Associated contact (optional)
        lead_id: Associated lead (optional)
        template_id: Template used (optional)
        sent_by: User who sent the message

    Returns:
        Dict with message details and status

    Raises:
        ValueError: If phone number is invalid or message is empty
    """
    # Validate inputs
    if not to_number or not to_number.startswith("+"):
        raise ValueError("Phone number must be in E.164 format (e.g., +15551234567)")

    if not body or len(body) == 0:
        raise ValueError("Message body cannot be empty")

    if len(body) > 1600:
        raise ValueError("Message body too long (max 1600 chars for concatenated SMS)")

    # Mock business phone number
    from_number = "+18045551234"  # RiverCityClean business number

    # Find or create conversation
    conversation = _get_or_create_conversation(db, to_number, contact_id)

    # Create message record
    message = SMSMessage(
        id=get_next_sms_message_id(),
        conversation_id=conversation.id,
        contact_id=contact_id,
        lead_id=lead_id,
        from_number=from_number,
        to_number=to_number,
        body=body,
        direction="outbound",
        status="sent",  # In production: pending -> sent -> delivered
        provider="twilio",
        provider_message_id=f"SM{datetime.utcnow().timestamp()}",  # Mock Twilio message ID
        sent_at=datetime.utcnow(),
        delivered_at=datetime.utcnow(),  # Mock instant delivery
        sent_by=sent_by,
        template_id=template_id,
        created_at=datetime.utcnow(),
    )

    db.sms_messages.append(message)

    # Update conversation
    conversation.message_count += 1
    conversation.last_message_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()

    # Update template usage count if applicable
    if template_id and template_id in db.sms_templates:
        db.sms_templates[template_id].times_used += 1

    db.commit()

    return {
        "success": True,
        "message_id": message.id,
        "provider_message_id": message.provider_message_id,
        "status": message.status,
        "conversation_id": conversation.id,
    }


def receive_sms(
    db: InMemoryDB,
    from_number: str,
    to_number: str,
    body: str,
    provider_message_id: str,
) -> Dict[str, Any]:
    """
    Receive an inbound SMS message.

    In production, this would be called by a Twilio webhook when a message is received.

    Args:
        db: Database session
        from_number: Sender's phone number
        to_number: Business phone number that received the message
        body: Message text
        provider_message_id: Twilio's message ID

    Returns:
        Dict with processing result
    """
    # Try to find associated contact
    contact = next(
        (c for c in db.contacts if c.phone and c.phone.replace("-", "").replace(" ", "") in from_number),
        None
    )
    contact_id = contact.id if contact else None

    # Try to find associated lead
    lead = next(
        (l for l in db.leads if contact_id and l.contact_id == contact_id),
        None
    )
    lead_id = lead.id if lead else None

    # Find or create conversation
    conversation = _get_or_create_conversation(db, from_number, contact_id)

    # Create message record
    message = SMSMessage(
        id=get_next_sms_message_id(),
        conversation_id=conversation.id,
        contact_id=contact_id,
        lead_id=lead_id,
        from_number=from_number,
        to_number=to_number,
        body=body,
        direction="inbound",
        status="received",
        provider="twilio",
        provider_message_id=provider_message_id,
        sent_at=datetime.utcnow(),
        delivered_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db.sms_messages.append(message)

    # Update conversation
    conversation.message_count += 1
    conversation.unread_count += 1
    conversation.last_message_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message_id": message.id,
        "conversation_id": conversation.id,
        "contact_id": contact_id,
        "lead_id": lead_id,
    }


def render_sms_template(
    db: InMemoryDB,
    template_id: int,
    variables: Dict[str, Any],
) -> str:
    """
    Render an SMS template with variables.

    Args:
        db: Database session
        template_id: Template to render
        variables: Variable values to substitute

    Returns:
        Rendered message body

    Raises:
        ValueError: If template not found
    """
    template = db.sms_templates.get(template_id)
    if not template:
        raise ValueError(f"Template {template_id} not found")

    # Simple variable substitution (same as follow-up templates)
    result = template.body
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))

    return result


def _get_or_create_conversation(
    db: InMemoryDB,
    phone_number: str,
    contact_id: Optional[int] = None,
) -> SMSConversation:
    """
    Get existing conversation or create new one.

    Args:
        db: Database session
        phone_number: Phone number for conversation
        contact_id: Associated contact (optional)

    Returns:
        SMSConversation instance
    """
    # Try to find existing conversation
    conversation = next(
        (c for c in db.sms_conversations.values() if c.phone_number == phone_number),
        None
    )

    if conversation:
        # Update contact_id if provided and not set
        if contact_id and not conversation.contact_id:
            conversation.contact_id = contact_id
            conversation.updated_at = datetime.utcnow()
        return conversation

    # Create new conversation
    conversation = SMSConversation(
        id=get_next_sms_conversation_id(),
        contact_id=contact_id,
        phone_number=phone_number,
        status="active",
        message_count=0,
        unread_count=0,
        created_at=datetime.utcnow(),
    )

    db.sms_conversations[conversation.id] = conversation
    return conversation


def get_conversation_messages(
    db: InMemoryDB,
    conversation_id: int,
) -> List[SMSMessage]:
    """
    Get all messages in a conversation, ordered by date.

    Args:
        db: Database session
        conversation_id: Conversation to fetch

    Returns:
        List of SMSMessage instances
    """
    messages = [
        msg for msg in db.sms_messages
        if msg.conversation_id == conversation_id
    ]

    # Sort by sent_at ascending (oldest first)
    messages.sort(key=lambda m: m.sent_at or m.created_at)

    return messages


def mark_conversation_read(
    db: InMemoryDB,
    conversation_id: int,
) -> None:
    """
    Mark all messages in a conversation as read.

    Args:
        db: Database session
        conversation_id: Conversation to mark as read

    Raises:
        ValueError: If conversation not found
    """
    conversation = db.sms_conversations.get(conversation_id)
    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")

    conversation.unread_count = 0
    conversation.updated_at = datetime.utcnow()
    db.commit()


def get_sms_stats(db: InMemoryDB) -> Dict[str, Any]:
    """
    Get SMS usage statistics.

    Args:
        db: Database session

    Returns:
        Dict with stats
    """
    messages = db.sms_messages

    total_sent = sum(1 for m in messages if m.direction == "outbound")
    total_received = sum(1 for m in messages if m.direction == "inbound")
    total_delivered = sum(1 for m in messages if m.status == "delivered")
    total_failed = sum(1 for m in messages if m.status == "failed")

    active_conversations = sum(
        1 for c in db.sms_conversations.values()
        if c.status == "active"
    )

    total_unread = sum(
        c.unread_count for c in db.sms_conversations.values()
    )

    last_message = max(
        (m.sent_at or m.created_at for m in messages),
        default=None
    )

    return {
        "total_messages": len(messages),
        "total_sent": total_sent,
        "total_received": total_received,
        "total_delivered": total_delivered,
        "total_failed": total_failed,
        "active_conversations": active_conversations,
        "unread_count": total_unread,
        "last_message_at": last_message,
    }
