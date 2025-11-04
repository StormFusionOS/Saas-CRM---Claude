"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
SMS / Text Hub API Routes.

Endpoints for SMS messaging, conversations, and templates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db import get_db, InMemoryDB
from app.schemas.sms import (
    SMSMessageSend,
    SMSMessageResponse,
    SMSMessageListItem,
    SMSConversationResponse,
    SMSConversationListItem,
    SMSConversationUpdate,
    SMSTemplateCreate,
    SMSTemplateUpdate,
    SMSTemplateResponse,
    SMSTemplateListItem,
    SMSStatsResponse,
)
from app.services import sms_service
from app.api.deps import require_sales_claims
from app.models import SMSTemplate, get_next_sms_template_id
from datetime import datetime


router = APIRouter(tags=["sms"])


# ============================================================================
# SMS Messaging Endpoints
# ============================================================================


@router.post("/sms/send", response_model=dict)
def send_sms_message(
    request: SMSMessageSend,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> dict:
    """
    Send an SMS message (STAFF ONLY).

    NOTE: In production, this would call Twilio API.
    """
    try:
        user_id = current_user.get("user_id", 1)

        result = sms_service.send_sms(
            db,
            to_number=request.to_number,
            body=request.body,
            contact_id=request.contact_id,
            lead_id=request.lead_id,
            template_id=request.template_id,
            sent_by=user_id,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/sms/messages", response_model=List[SMSMessageListItem])
def list_sms_messages(
    conversation_id: Optional[int] = None,
    contact_id: Optional[int] = None,
    direction: Optional[str] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[SMSMessageListItem]:
    """
    List SMS messages (STAFF ONLY).

    Filters:
    - conversation_id: Filter by conversation
    - contact_id: Filter by contact
    - direction: Filter by direction (inbound/outbound)
    """
    messages = db.sms_messages

    # Apply filters
    if conversation_id:
        messages = [m for m in messages if m.conversation_id == conversation_id]

    if contact_id:
        messages = [m for m in messages if m.contact_id == contact_id]

    if direction:
        messages = [m for m in messages if m.direction == direction]

    # Sort by sent_at descending (newest first)
    messages = sorted(
        messages,
        key=lambda m: m.sent_at or m.created_at,
        reverse=True
    )

    return [
        SMSMessageListItem(
            id=msg.id,
            conversation_id=msg.conversation_id,
            from_number=msg.from_number,
            to_number=msg.to_number,
            body=msg.body,
            direction=msg.direction,
            status=msg.status,
            sent_at=msg.sent_at,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.get("/sms/messages/{message_id}", response_model=SMSMessageResponse)
def get_sms_message(
    message_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSMessageResponse:
    """
    Get SMS message details (STAFF ONLY).
    """
    message = next((m for m in db.sms_messages if m.id == message_id), None)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    return SMSMessageResponse(**message.__dict__)


# ============================================================================
# SMS Conversation Endpoints
# ============================================================================


@router.get("/sms/conversations", response_model=List[SMSConversationListItem])
def list_sms_conversations(
    status_filter: Optional[str] = None,
    assigned_to: Optional[int] = None,
    has_unread: Optional[bool] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[SMSConversationListItem]:
    """
    List SMS conversations (STAFF ONLY).

    Filters:
    - status_filter: Filter by status (active/archived/blocked)
    - assigned_to: Filter by assigned staff member
    - has_unread: Filter conversations with unread messages
    """
    conversations = list(db.sms_conversations.values())

    # Apply filters
    if status_filter:
        conversations = [c for c in conversations if c.status == status_filter]

    if assigned_to:
        conversations = [c for c in conversations if c.assigned_to == assigned_to]

    if has_unread is not None:
        if has_unread:
            conversations = [c for c in conversations if c.unread_count > 0]
        else:
            conversations = [c for c in conversations if c.unread_count == 0]

    # Sort by last_message_at descending (most recent first)
    conversations.sort(
        key=lambda c: c.last_message_at or c.created_at,
        reverse=True
    )

    # Add last message preview
    result = []
    for conv in conversations:
        # Get last message for preview
        conv_messages = [m for m in db.sms_messages if m.conversation_id == conv.id]
        last_message = max(
            conv_messages,
            key=lambda m: m.sent_at or m.created_at,
            default=None
        )

        result.append(
            SMSConversationListItem(
                id=conv.id,
                contact_id=conv.contact_id,
                phone_number=conv.phone_number,
                status=conv.status,
                message_count=conv.message_count,
                unread_count=conv.unread_count,
                last_message_at=conv.last_message_at,
                last_message_preview=last_message.body[:50] + "..." if last_message and len(last_message.body) > 50 else last_message.body if last_message else None,
                assigned_to=conv.assigned_to,
            )
        )

    return result


@router.get("/sms/conversations/{conversation_id}", response_model=SMSConversationResponse)
def get_sms_conversation(
    conversation_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSConversationResponse:
    """
    Get conversation details with messages (STAFF ONLY).
    """
    conversation = db.sms_conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get last message preview
    messages = sms_service.get_conversation_messages(db, conversation_id)
    last_message = messages[-1] if messages else None

    return SMSConversationResponse(
        id=conversation.id,
        contact_id=conversation.contact_id,
        phone_number=conversation.phone_number,
        status=conversation.status,
        message_count=conversation.message_count,
        unread_count=conversation.unread_count,
        last_message_at=conversation.last_message_at,
        last_message_preview=last_message.body[:100] if last_message else None,
        assigned_to=conversation.assigned_to,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.patch("/sms/conversations/{conversation_id}", response_model=SMSConversationResponse)
def update_sms_conversation(
    conversation_id: int,
    request: SMSConversationUpdate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSConversationResponse:
    """
    Update conversation metadata (STAFF ONLY).
    """
    conversation = db.sms_conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Update fields
    if request.status:
        conversation.status = request.status

    if request.assigned_to is not None:
        conversation.assigned_to = request.assigned_to

    if request.mark_read:
        sms_service.mark_conversation_read(db, conversation_id)

    conversation.updated_at = datetime.utcnow()
    db.commit()

    # Get last message preview
    messages = sms_service.get_conversation_messages(db, conversation_id)
    last_message = messages[-1] if messages else None

    return SMSConversationResponse(
        id=conversation.id,
        contact_id=conversation.contact_id,
        phone_number=conversation.phone_number,
        status=conversation.status,
        message_count=conversation.message_count,
        unread_count=conversation.unread_count,
        last_message_at=conversation.last_message_at,
        last_message_preview=last_message.body[:100] if last_message else None,
        assigned_to=conversation.assigned_to,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


# ============================================================================
# SMS Template Endpoints
# ============================================================================


@router.get("/sms/templates", response_model=List[SMSTemplateListItem])
def list_sms_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[SMSTemplateListItem]:
    """
    List SMS templates (STAFF ONLY).

    Filters:
    - category: Filter by category
    - is_active: Filter by active status
    """
    templates = list(db.sms_templates.values())

    # Apply filters
    if category:
        templates = [t for t in templates if t.category == category]

    if is_active is not None:
        templates = [t for t in templates if t.is_active == is_active]

    # Sort by name
    templates.sort(key=lambda t: t.name)

    return [
        SMSTemplateListItem(
            id=tpl.id,
            name=tpl.name,
            category=tpl.category,
            body=tpl.body,
            is_active=tpl.is_active,
            times_used=tpl.times_used,
        )
        for tpl in templates
    ]


@router.get("/sms/templates/{template_id}", response_model=SMSTemplateResponse)
def get_sms_template(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSTemplateResponse:
    """
    Get SMS template details (STAFF ONLY).
    """
    template = db.sms_templates.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return SMSTemplateResponse(**template.__dict__)


@router.post("/sms/templates", response_model=SMSTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_sms_template(
    request: SMSTemplateCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSTemplateResponse:
    """
    Create a new SMS template (STAFF ONLY).
    """
    user_id = current_user.get("user_id", 1)

    template = SMSTemplate(
        id=get_next_sms_template_id(),
        name=request.name,
        category=request.category,
        body=request.body,
        is_active=True,
        times_used=0,
        variables=request.variables,
        created_at=datetime.utcnow(),
        created_by=user_id,
    )

    db.sms_templates[template.id] = template
    db.commit()

    return SMSTemplateResponse(**template.__dict__)


@router.patch("/sms/templates/{template_id}", response_model=SMSTemplateResponse)
def update_sms_template(
    template_id: int,
    request: SMSTemplateUpdate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSTemplateResponse:
    """
    Update an SMS template (STAFF ONLY).
    """
    template = db.sms_templates.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Update fields
    if request.name:
        template.name = request.name
    if request.category:
        template.category = request.category
    if request.body:
        template.body = request.body
    if request.is_active is not None:
        template.is_active = request.is_active
    if request.variables is not None:
        template.variables = request.variables

    template.updated_at = datetime.utcnow()
    db.commit()

    return SMSTemplateResponse(**template.__dict__)


@router.delete("/sms/templates/{template_id}")
def delete_sms_template(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Delete an SMS template (STAFF ONLY).
    """
    if template_id not in db.sms_templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    del db.sms_templates[template_id]
    db.commit()

    return {"message": "Template deleted successfully", "template_id": template_id}


# ============================================================================
# SMS Stats Endpoint
# ============================================================================


@router.get("/sms/stats", response_model=SMSStatsResponse)
def get_sms_stats(
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> SMSStatsResponse:
    """
    Get SMS usage statistics (STAFF ONLY).
    """
    stats = sms_service.get_sms_stats(db)
    return SMSStatsResponse(**stats)
