"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Pydantic schemas for Follow-Up Automation.

Request/response models for automation sequences.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Follow-Up Sequence Schemas
# ============================================================================


class FollowUpStepSchema(BaseModel):
    """Follow-up step schema."""

    id: str
    order: int
    delay_hours: int
    action_type: str  # email, sms, task, call
    subject: str = ""
    body_template: str = ""
    task_title: str = ""
    task_description: str = ""
    assign_to_role: Optional[str] = None
    conditions: Dict[str, Any] = Field(default_factory=dict)
    skip_if_responded: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "day_1_email",
                "order": 1,
                "delay_hours": 24,
                "action_type": "email",
                "subject": "Follow up on your inquiry",
                "body_template": "Hi {{first_name}}, ...",
                "skip_if_responded": True
            }
        }


class FollowUpSequenceResponse(BaseModel):
    """Follow-up sequence response."""

    id: int
    name: str
    description: str
    trigger_event: str
    trigger_conditions: Dict[str, Any]
    steps: List[FollowUpStepSchema]
    is_active: bool
    priority: int
    stop_on_response: bool
    stop_on_status_change: bool
    stop_statuses: List[str]
    category: str
    tags: List[str]
    total_started: int
    total_completed: int
    total_stopped: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class FollowUpSequenceListItem(BaseModel):
    """Minimal sequence for list views."""

    id: int
    name: str
    description: str
    trigger_event: str
    is_active: bool
    step_count: int
    total_started: int
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Follow-Up Instance Schemas
# ============================================================================


class FollowUpInstanceResponse(BaseModel):
    """Follow-up instance response."""

    id: int
    sequence_id: int
    sequence_name: str = Field(..., description="Name of the sequence")
    lead_id: Optional[int]
    contact_id: Optional[int]
    quote_id: Optional[int]
    status: str  # active, completed, stopped, paused
    current_step_index: int
    started_at: datetime
    completed_at: Optional[datetime]
    stopped_at: Optional[datetime]
    stop_reason: str
    steps_completed: List[str]
    last_action_at: Optional[datetime]
    has_responded: bool
    response_date: Optional[datetime]
    response_type: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FollowUpInstanceListItem(BaseModel):
    """Minimal instance for list views."""

    id: int
    sequence_id: int
    sequence_name: str
    lead_id: Optional[int]
    contact_id: Optional[int]
    status: str
    current_step_index: int
    total_steps: int
    started_at: datetime
    has_responded: bool

    class Config:
        from_attributes = True


# ============================================================================
# Follow-Up Task Schemas
# ============================================================================


class FollowUpTaskResponse(BaseModel):
    """Follow-up task response."""

    id: int
    instance_id: int
    sequence_id: int
    step_id: str
    lead_id: Optional[int]
    contact_id: Optional[int]
    task_type: str
    status: str  # pending, sent, completed, failed, skipped
    scheduled_for: datetime
    executed_at: Optional[datetime]
    subject: str
    body: str
    task_title: str
    task_description: str
    assigned_to: Optional[int]
    completed_by: Optional[int]
    success: bool
    error_message: str
    response_received: bool
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FollowUpTaskListItem(BaseModel):
    """Minimal task for list views."""

    id: int
    task_type: str
    status: str
    scheduled_for: datetime
    subject: str
    task_title: str
    assigned_to: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Trigger Request
# ============================================================================


class TriggerSequenceRequest(BaseModel):
    """Manually trigger a sequence for a lead."""

    sequence_id: int = Field(..., description="Sequence to trigger")
    lead_id: Optional[int] = Field(None, description="Lead ID")
    contact_id: Optional[int] = Field(None, description="Contact ID")
    quote_id: Optional[int] = Field(None, description="Quote ID (if applicable)")

    class Config:
        json_schema_extra = {
            "example": {
                "sequence_id": 1,
                "lead_id": 1
            }
        }
