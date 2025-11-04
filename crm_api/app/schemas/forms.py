"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Pydantic schemas for SmartForm Builder.

Request/response models for form templates and submissions.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Form Field Schemas
# ============================================================================


class FormFieldSchema(BaseModel):
    """Form field definition schema."""

    id: str = Field(..., description="Unique field ID")
    label: str = Field(..., description="Display label")
    field_type: str = Field(
        ...,
        description="Field type: text, email, phone, number, select, multiselect, checkbox, radio, textarea, date, file"
    )

    # Validation
    required: bool = Field(default=False, description="Is field required?")
    placeholder: str = Field(default="", description="Placeholder text")
    help_text: str = Field(default="", description="Help text shown below field")

    # Field-specific options
    options: List[str] = Field(default_factory=list, description="Options for select/radio/multiselect fields")
    min_value: Optional[float] = Field(None, description="Min value for number fields")
    max_value: Optional[float] = Field(None, description="Max value for number fields")
    min_length: Optional[int] = Field(None, description="Min length for text fields")
    max_length: Optional[int] = Field(None, description="Max length for text fields")
    pattern: Optional[str] = Field(None, description="Regex pattern for validation")

    # Conditional logic
    show_if: Optional[Dict[str, Any]] = Field(None, description="Conditional display rules")

    # Display
    order: int = Field(default=0, description="Display order")
    width: str = Field(default="full", description="Field width: full, half, third, quarter")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "property_type",
                "label": "Property Type",
                "field_type": "select",
                "options": ["Residential", "Commercial", "Multi-Family"],
                "required": True,
                "order": 1,
                "width": "half"
            }
        }


# ============================================================================
# Form Template Schemas
# ============================================================================


class FormTemplateCreate(BaseModel):
    """Create a new form template."""

    name: str = Field(..., min_length=2, max_length=100, description="Internal name")
    title: str = Field(..., min_length=2, max_length=200, description="Display title for customers")
    description: str = Field(default="", max_length=500, description="Form description")

    fields: List[FormFieldSchema] = Field(..., min_items=1, description="Form fields")

    # Settings
    is_active: bool = Field(default=True, description="Is form active?")
    allow_multiple_submissions: bool = Field(default=False, description="Allow multiple submissions?")
    require_authentication: bool = Field(default=False, description="Require authentication?")

    # Notifications
    send_confirmation_email: bool = Field(default=True, description="Send confirmation to submitter?")
    confirmation_email_template: str = Field(default="", max_length=5000, description="Email template")
    notify_staff_on_submission: bool = Field(default=True, description="Notify staff?")
    notification_emails: List[str] = Field(default_factory=list, description="Staff emails to notify")

    # Integration
    attach_to_proposal: bool = Field(default=False, description="Can attach to proposals?")
    attach_to_quote: bool = Field(default=False, description="Can attach to quotes?")

    # Categories/Tags
    category: str = Field(default="", max_length=50, description="Form category")
    tags: List[str] = Field(default_factory=list, description="Form tags")

    # Success behavior
    success_message: str = Field(default="Thank you for your submission!", max_length=500)
    redirect_url: Optional[str] = Field(None, max_length=500, description="Redirect URL after submission")

    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Service Intake",
                "title": "Property & Service Details",
                "description": "Help us understand your property and service needs",
                "fields": [
                    {
                        "id": "property_type",
                        "label": "Property Type",
                        "field_type": "select",
                        "options": ["Residential", "Commercial"],
                        "required": True,
                        "order": 1
                    }
                ],
                "attach_to_quote": True,
                "category": "intake"
            }
        }


class FormTemplateUpdate(BaseModel):
    """Update an existing form template."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    fields: Optional[List[FormFieldSchema]] = None
    is_active: Optional[bool] = None
    allow_multiple_submissions: Optional[bool] = None
    require_authentication: Optional[bool] = None
    send_confirmation_email: Optional[bool] = None
    confirmation_email_template: Optional[str] = None
    notify_staff_on_submission: Optional[bool] = None
    notification_emails: Optional[List[str]] = None
    attach_to_proposal: Optional[bool] = None
    attach_to_quote: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    success_message: Optional[str] = None
    redirect_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FormTemplateResponse(BaseModel):
    """Form template response."""

    id: int
    name: str
    title: str
    description: str
    fields: List[FormFieldSchema]
    is_active: bool
    allow_multiple_submissions: bool
    require_authentication: bool
    send_confirmation_email: bool
    confirmation_email_template: str
    notify_staff_on_submission: bool
    notification_emails: List[str]
    attach_to_proposal: bool
    attach_to_quote: bool
    category: str
    tags: List[str]
    success_message: str
    redirect_url: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class FormTemplateListItem(BaseModel):
    """Minimal form template for list views."""

    id: int
    name: str
    title: str
    category: str
    is_active: bool
    field_count: int = Field(..., description="Number of fields in form")
    submission_count: int = Field(default=0, description="Number of submissions")
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Form Submission Schemas
# ============================================================================


class FormSubmissionRequest(BaseModel):
    """Submit a form (PUBLIC - no auth required)."""

    form_template_id: int = Field(..., description="Form template ID")
    responses: Dict[str, Any] = Field(..., description="Field responses")

    # Optional context
    quote_id: Optional[int] = Field(None, description="Quote ID if submitted via quote")
    proposal_id: Optional[int] = Field(None, description="Proposal ID if submitted via proposal")

    # Submitter info
    submitter_name: str = Field(..., min_length=2, max_length=100, description="Submitter name")
    submitter_email: Optional[str] = Field(None, description="Submitter email")
    submitter_phone: Optional[str] = Field(None, description="Submitter phone")

    class Config:
        json_schema_extra = {
            "example": {
                "form_template_id": 1,
                "responses": {
                    "property_type": "Residential",
                    "property_size": 2500,
                    "stories": "2",
                    "service_frequency": "Quarterly"
                },
                "submitter_name": "John Smith",
                "submitter_email": "john@example.com"
            }
        }


class FormSubmissionResponse(BaseModel):
    """Form submission response."""

    id: int
    form_template_id: int
    responses: Dict[str, Any]
    contact_id: Optional[int]
    lead_id: Optional[int]
    quote_id: Optional[int]
    proposal_id: Optional[int]
    submitter_name: str
    submitter_email: Optional[str]
    submitter_phone: Optional[str]
    status: str
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    notes: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    message: str = Field(..., description="Success message")

    class Config:
        from_attributes = True


class FormSubmissionListItem(BaseModel):
    """Minimal form submission for list views."""

    id: int
    form_template_id: int
    form_name: str = Field(..., description="Form template name")
    submitter_name: str
    submitter_email: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class FormSubmissionUpdate(BaseModel):
    """Update form submission (admin only)."""

    status: Optional[str] = Field(None, description="Status: submitted, reviewed, processed, archived")
    notes: Optional[str] = Field(None, max_length=5000, description="Staff notes")
    metadata: Optional[Dict[str, Any]] = None
