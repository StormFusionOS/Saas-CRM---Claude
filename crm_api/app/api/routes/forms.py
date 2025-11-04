"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Forms API Routes - SmartForm Builder.

Endpoints for managing form templates and handling submissions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from app.db import get_db, InMemoryDB
from app.schemas.forms import (
    FormTemplateCreate,
    FormTemplateUpdate,
    FormTemplateResponse,
    FormTemplateListItem,
    FormSubmissionRequest,
    FormSubmissionResponse,
    FormSubmissionListItem,
    FormSubmissionUpdate,
    FormFieldSchema,
)
from app.services import forms_service
from app.api.deps import require_sales_claims


router = APIRouter(tags=["forms"])


# ============================================================================
# Form Template Endpoints (Admin/Staff)
# ============================================================================


@router.get("/forms/templates", response_model=List[FormTemplateListItem])
def list_form_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[FormTemplateListItem]:
    """
    List all form templates (STAFF ONLY).

    Filter by category or active status.
    """
    templates = list(db.form_templates.values())

    # Filter by category
    if category:
        templates = [t for t in templates if t.category == category]

    # Filter by active status
    if is_active is not None:
        templates = [t for t in templates if t.is_active == is_active]

    # Sort by name
    templates.sort(key=lambda t: t.name)

    # Count submissions per template
    submission_counts = {}
    for submission in db.form_submissions:
        template_id = submission.form_template_id
        submission_counts[template_id] = submission_counts.get(template_id, 0) + 1

    # Build response
    result = []
    for template in templates:
        result.append(
            FormTemplateListItem(
                id=template.id,
                name=template.name,
                title=template.title,
                category=template.category,
                is_active=template.is_active,
                field_count=len(template.fields),
                submission_count=submission_counts.get(template.id, 0),
                created_at=template.created_at,
            )
        )

    return result


@router.get("/forms/templates/{template_id}", response_model=FormTemplateResponse)
def get_form_template(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FormTemplateResponse:
    """
    Get a specific form template by ID (STAFF ONLY).
    """
    template = db.form_templates.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form template not found",
        )

    # Convert FormField dataclass to FormFieldSchema
    fields = [FormFieldSchema(**field.__dict__) for field in template.fields]

    return FormTemplateResponse(
        id=template.id,
        name=template.name,
        title=template.title,
        description=template.description,
        fields=fields,
        is_active=template.is_active,
        allow_multiple_submissions=template.allow_multiple_submissions,
        require_authentication=template.require_authentication,
        send_confirmation_email=template.send_confirmation_email,
        confirmation_email_template=template.confirmation_email_template,
        notify_staff_on_submission=template.notify_staff_on_submission,
        notification_emails=template.notification_emails,
        attach_to_proposal=template.attach_to_proposal,
        attach_to_quote=template.attach_to_quote,
        category=template.category,
        tags=template.tags,
        success_message=template.success_message,
        redirect_url=template.redirect_url,
        metadata=template.metadata,
        created_at=template.created_at,
        updated_at=template.updated_at,
        created_by=template.created_by,
    )


@router.post("/forms/templates", response_model=FormTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_form_template(
    template_data: FormTemplateCreate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FormTemplateResponse:
    """
    Create a new form template (STAFF ONLY).
    """
    from app.models import FormTemplate, FormField, get_next_form_template_id
    from datetime import datetime

    # Convert FormFieldSchema to FormField dataclass
    fields = []
    for field_schema in template_data.fields:
        fields.append(
            FormField(
                id=field_schema.id,
                label=field_schema.label,
                field_type=field_schema.field_type,
                required=field_schema.required,
                placeholder=field_schema.placeholder,
                help_text=field_schema.help_text,
                options=field_schema.options,
                min_value=field_schema.min_value,
                max_value=field_schema.max_value,
                min_length=field_schema.min_length,
                max_length=field_schema.max_length,
                pattern=field_schema.pattern,
                show_if=field_schema.show_if,
                order=field_schema.order,
                width=field_schema.width,
                metadata=field_schema.metadata,
            )
        )

    # Create template
    template = FormTemplate(
        id=get_next_form_template_id(),
        name=template_data.name,
        title=template_data.title,
        description=template_data.description,
        fields=fields,
        is_active=template_data.is_active,
        allow_multiple_submissions=template_data.allow_multiple_submissions,
        require_authentication=template_data.require_authentication,
        send_confirmation_email=template_data.send_confirmation_email,
        confirmation_email_template=template_data.confirmation_email_template,
        notify_staff_on_submission=template_data.notify_staff_on_submission,
        notification_emails=template_data.notification_emails,
        attach_to_proposal=template_data.attach_to_proposal,
        attach_to_quote=template_data.attach_to_quote,
        category=template_data.category,
        tags=template_data.tags,
        success_message=template_data.success_message,
        redirect_url=template_data.redirect_url,
        metadata=template_data.metadata,
        created_at=datetime.utcnow(),
        created_by=current_user.get("user_id"),
    )

    db.form_templates[template.id] = template
    db.commit()

    # Convert back for response
    fields_response = [FormFieldSchema(**field.__dict__) for field in template.fields]

    return FormTemplateResponse(
        id=template.id,
        name=template.name,
        title=template.title,
        description=template.description,
        fields=fields_response,
        is_active=template.is_active,
        allow_multiple_submissions=template.allow_multiple_submissions,
        require_authentication=template.require_authentication,
        send_confirmation_email=template.send_confirmation_email,
        confirmation_email_template=template.confirmation_email_template,
        notify_staff_on_submission=template.notify_staff_on_submission,
        notification_emails=template.notification_emails,
        attach_to_proposal=template.attach_to_proposal,
        attach_to_quote=template.attach_to_quote,
        category=template.category,
        tags=template.tags,
        success_message=template.success_message,
        redirect_url=template.redirect_url,
        metadata=template.metadata,
        created_at=template.created_at,
        updated_at=template.updated_at,
        created_by=template.created_by,
    )


@router.patch("/forms/templates/{template_id}", response_model=FormTemplateResponse)
def update_form_template(
    template_id: int,
    updates: FormTemplateUpdate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FormTemplateResponse:
    """
    Update a form template (STAFF ONLY).
    """
    from app.models import FormField
    from datetime import datetime

    template = db.form_templates.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form template not found",
        )

    # Update fields
    update_data = updates.model_dump(exclude_unset=True)

    # Special handling for fields
    if "fields" in update_data:
        fields = []
        for field_schema in update_data["fields"]:
            fields.append(
                FormField(
                    id=field_schema["id"],
                    label=field_schema["label"],
                    field_type=field_schema["field_type"],
                    required=field_schema.get("required", False),
                    placeholder=field_schema.get("placeholder", ""),
                    help_text=field_schema.get("help_text", ""),
                    options=field_schema.get("options", []),
                    min_value=field_schema.get("min_value"),
                    max_value=field_schema.get("max_value"),
                    min_length=field_schema.get("min_length"),
                    max_length=field_schema.get("max_length"),
                    pattern=field_schema.get("pattern"),
                    show_if=field_schema.get("show_if"),
                    order=field_schema.get("order", 0),
                    width=field_schema.get("width", "full"),
                    metadata=field_schema.get("metadata", {}),
                )
            )
        template.fields = fields
        del update_data["fields"]

    # Update other fields
    for key, value in update_data.items():
        setattr(template, key, value)

    template.updated_at = datetime.utcnow()
    db.commit()

    # Convert for response
    fields_response = [FormFieldSchema(**field.__dict__) for field in template.fields]

    return FormTemplateResponse(
        id=template.id,
        name=template.name,
        title=template.title,
        description=template.description,
        fields=fields_response,
        is_active=template.is_active,
        allow_multiple_submissions=template.allow_multiple_submissions,
        require_authentication=template.require_authentication,
        send_confirmation_email=template.send_confirmation_email,
        confirmation_email_template=template.confirmation_email_template,
        notify_staff_on_submission=template.notify_staff_on_submission,
        notification_emails=template.notification_emails,
        attach_to_proposal=template.attach_to_proposal,
        attach_to_quote=template.attach_to_quote,
        category=template.category,
        tags=template.tags,
        success_message=template.success_message,
        redirect_url=template.redirect_url,
        metadata=template.metadata,
        created_at=template.created_at,
        updated_at=template.updated_at,
        created_by=template.created_by,
    )


@router.delete("/forms/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form_template(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Delete a form template (STAFF ONLY).
    """
    if template_id not in db.form_templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form template not found",
        )

    del db.form_templates[template_id]
    db.commit()


# ============================================================================
# Form Submission Endpoints
# ============================================================================


@router.get("/forms/{template_id}", response_model=FormTemplateResponse)
def get_public_form(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
) -> FormTemplateResponse:
    """
    Get a form template for filling out (PUBLIC - no auth required).

    Returns active form templates only.
    """
    template = db.form_templates.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found",
        )

    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This form is no longer accepting submissions",
        )

    # Convert FormField dataclass to FormFieldSchema
    fields = [FormFieldSchema(**field.__dict__) for field in template.fields]

    return FormTemplateResponse(
        id=template.id,
        name=template.name,
        title=template.title,
        description=template.description,
        fields=fields,
        is_active=template.is_active,
        allow_multiple_submissions=template.allow_multiple_submissions,
        require_authentication=template.require_authentication,
        send_confirmation_email=template.send_confirmation_email,
        confirmation_email_template=template.confirmation_email_template,
        notify_staff_on_submission=template.notify_staff_on_submission,
        notification_emails=template.notification_emails,
        attach_to_proposal=template.attach_to_proposal,
        attach_to_quote=template.attach_to_quote,
        category=template.category,
        tags=template.tags,
        success_message=template.success_message,
        redirect_url=template.redirect_url,
        metadata=template.metadata,
        created_at=template.created_at,
        updated_at=template.updated_at,
        created_by=template.created_by,
    )


@router.post("/forms/submit", response_model=FormSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_form(
    submission: FormSubmissionRequest,
    request: Request,
    db: InMemoryDB = Depends(get_db),
) -> FormSubmissionResponse:
    """
    Submit a form (PUBLIC - no auth required).

    Validates responses and creates submission record.
    """
    try:
        # Get IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Submit form
        form_submission = forms_service.submit_form(
            db=db,
            form_template_id=submission.form_template_id,
            responses=submission.responses,
            submitter_name=submission.submitter_name,
            submitter_email=submission.submitter_email,
            submitter_phone=submission.submitter_phone,
            quote_id=submission.quote_id,
            proposal_id=submission.proposal_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Get success message from template
        template = db.form_templates.get(submission.form_template_id)
        message = template.success_message if template else "Thank you for your submission!"

        return FormSubmissionResponse(
            id=form_submission.id,
            form_template_id=form_submission.form_template_id,
            responses=form_submission.responses,
            contact_id=form_submission.contact_id,
            lead_id=form_submission.lead_id,
            quote_id=form_submission.quote_id,
            proposal_id=form_submission.proposal_id,
            submitter_name=form_submission.submitter_name,
            submitter_email=form_submission.submitter_email,
            submitter_phone=form_submission.submitter_phone,
            status=form_submission.status,
            reviewed_by=form_submission.reviewed_by,
            reviewed_at=form_submission.reviewed_at,
            notes=form_submission.notes,
            metadata=form_submission.metadata,
            created_at=form_submission.created_at,
            updated_at=form_submission.updated_at,
            message=message,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/forms/submissions", response_model=List[FormSubmissionListItem])
def list_form_submissions(
    form_template_id: Optional[int] = None,
    status: Optional[str] = None,
    contact_id: Optional[int] = None,
    quote_id: Optional[int] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[FormSubmissionListItem]:
    """
    List form submissions with optional filtering (STAFF ONLY).
    """
    submissions = forms_service.get_form_submissions(
        db=db,
        form_template_id=form_template_id,
        status=status,
        contact_id=contact_id,
        quote_id=quote_id,
    )

    # Build response
    result = []
    for submission in submissions:
        # Get form template name
        template = db.form_templates.get(submission.form_template_id)
        form_name = template.name if template else f"Form #{submission.form_template_id}"

        result.append(
            FormSubmissionListItem(
                id=submission.id,
                form_template_id=submission.form_template_id,
                form_name=form_name,
                submitter_name=submission.submitter_name,
                submitter_email=submission.submitter_email,
                status=submission.status,
                created_at=submission.created_at,
            )
        )

    return result


@router.get("/forms/submissions/{submission_id}", response_model=FormSubmissionResponse)
def get_form_submission(
    submission_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FormSubmissionResponse:
    """
    Get a specific form submission (STAFF ONLY).
    """
    submission = None
    for s in db.form_submissions:
        if s.id == submission_id:
            submission = s
            break

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form submission not found",
        )

    return FormSubmissionResponse(
        id=submission.id,
        form_template_id=submission.form_template_id,
        responses=submission.responses,
        contact_id=submission.contact_id,
        lead_id=submission.lead_id,
        quote_id=submission.quote_id,
        proposal_id=submission.proposal_id,
        submitter_name=submission.submitter_name,
        submitter_email=submission.submitter_email,
        submitter_phone=submission.submitter_phone,
        status=submission.status,
        reviewed_by=submission.reviewed_by,
        reviewed_at=submission.reviewed_at,
        notes=submission.notes,
        metadata=submission.metadata,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
        message="Submission retrieved successfully",
    )


@router.patch("/forms/submissions/{submission_id}", response_model=FormSubmissionResponse)
def update_form_submission(
    submission_id: int,
    updates: FormSubmissionUpdate,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FormSubmissionResponse:
    """
    Update form submission status and notes (STAFF ONLY).
    """
    try:
        update_data = updates.model_dump(exclude_unset=True)

        submission = forms_service.update_submission_status(
            db=db,
            submission_id=submission_id,
            status=update_data.get("status", "submitted"),
            notes=update_data.get("notes", ""),
            reviewed_by=current_user.get("user_id"),
        )

        return FormSubmissionResponse(
            id=submission.id,
            form_template_id=submission.form_template_id,
            responses=submission.responses,
            contact_id=submission.contact_id,
            lead_id=submission.lead_id,
            quote_id=submission.quote_id,
            proposal_id=submission.proposal_id,
            submitter_name=submission.submitter_name,
            submitter_email=submission.submitter_email,
            submitter_phone=submission.submitter_phone,
            status=submission.status,
            reviewed_by=submission.reviewed_by,
            reviewed_at=submission.reviewed_at,
            notes=submission.notes,
            metadata=submission.metadata,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
            message="Submission updated successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
