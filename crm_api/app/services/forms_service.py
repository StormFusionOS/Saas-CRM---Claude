"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Forms Service - Form validation and submission handling.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.db import InMemoryDB
from app.models import FormTemplate, FormField, FormSubmission, get_next_form_submission_id


def validate_field_value(field: FormField, value: Any) -> tuple[bool, Optional[str]]:
    """
    Validate a field value against its rules.

    Args:
        field: FormField definition
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required
    if field.required and (value is None or value == "" or value == []):
        return False, f"{field.label} is required"

    # If not required and empty, it's valid
    if value is None or value == "" or value == []:
        return True, None

    # Type-specific validation
    if field.field_type == "email":
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(value)):
            return False, f"{field.label} must be a valid email address"

    elif field.field_type == "phone":
        # Basic phone validation - allows various formats
        phone_pattern = r'^[\d\s\-\(\)\+\.]+$'
        if not re.match(phone_pattern, str(value)):
            return False, f"{field.label} must be a valid phone number"

    elif field.field_type == "number":
        try:
            num_value = float(value)
            if field.min_value is not None and num_value < field.min_value:
                return False, f"{field.label} must be at least {field.min_value}"
            if field.max_value is not None and num_value > field.max_value:
                return False, f"{field.label} must be at most {field.max_value}"
        except (ValueError, TypeError):
            return False, f"{field.label} must be a number"

    elif field.field_type in ["text", "textarea"]:
        str_value = str(value)
        if field.min_length is not None and len(str_value) < field.min_length:
            return False, f"{field.label} must be at least {field.min_length} characters"
        if field.max_length is not None and len(str_value) > field.max_length:
            return False, f"{field.label} must be at most {field.max_length} characters"
        if field.pattern is not None:
            if not re.match(field.pattern, str_value):
                return False, f"{field.label} format is invalid"

    elif field.field_type == "select":
        if value not in field.options:
            return False, f"{field.label} must be one of: {', '.join(field.options)}"

    elif field.field_type == "multiselect":
        if not isinstance(value, list):
            return False, f"{field.label} must be a list"
        for item in value:
            if item not in field.options:
                return False, f"{field.label} contains invalid option: {item}"

    elif field.field_type == "radio":
        if value not in field.options:
            return False, f"{field.label} must be one of: {', '.join(field.options)}"

    elif field.field_type == "checkbox":
        if not isinstance(value, bool):
            return False, f"{field.label} must be true or false"

    return True, None


def evaluate_conditional_logic(field: FormField, responses: Dict[str, Any]) -> bool:
    """
    Evaluate whether a field should be shown based on conditional logic.

    Args:
        field: FormField with show_if rules
        responses: Current form responses

    Returns:
        True if field should be shown, False otherwise
    """
    if not field.show_if:
        return True  # No conditional logic, always show

    # Simple implementation: check if all conditions match
    for field_id, expected_value in field.show_if.items():
        actual_value = responses.get(field_id)
        if actual_value != expected_value:
            return False

    return True


def validate_form_submission(
    form_template: FormTemplate,
    responses: Dict[str, Any]
) -> tuple[bool, List[str]]:
    """
    Validate form submission against template rules.

    Args:
        form_template: Form template definition
        responses: Submitted responses

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Validate each field
    for field in form_template.fields:
        # Check if field should be shown based on conditional logic
        if not evaluate_conditional_logic(field, responses):
            continue  # Skip validation for hidden fields

        value = responses.get(field.id)
        is_valid, error = validate_field_value(field, value)

        if not is_valid:
            errors.append(error)

    return len(errors) == 0, errors


def submit_form(
    db: InMemoryDB,
    form_template_id: int,
    responses: Dict[str, Any],
    submitter_name: str,
    submitter_email: Optional[str] = None,
    submitter_phone: Optional[str] = None,
    quote_id: Optional[int] = None,
    proposal_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> FormSubmission:
    """
    Submit a form and create a submission record.

    Args:
        db: Database session
        form_template_id: Form template ID
        responses: Field responses
        submitter_name: Submitter name
        submitter_email: Optional email
        submitter_phone: Optional phone
        quote_id: Optional quote ID
        proposal_id: Optional proposal ID
        ip_address: Optional IP address
        user_agent: Optional user agent

    Returns:
        Created FormSubmission

    Raises:
        ValueError: If form not found, inactive, or validation fails
    """
    # Get form template
    form_template = db.form_templates.get(form_template_id)
    if not form_template:
        raise ValueError("Form template not found")

    if not form_template.is_active:
        raise ValueError("This form is no longer accepting submissions")

    # Validate submission
    is_valid, errors = validate_form_submission(form_template, responses)
    if not is_valid:
        raise ValueError(f"Form validation failed: {'; '.join(errors)}")

    # Try to match submitter to existing contact
    contact_id = None
    lead_id = None
    if submitter_email:
        # Find contact by email
        for contact in db.contacts:
            if contact.email and contact.email.lower() == submitter_email.lower():
                contact_id = contact.id
                # Find associated lead
                for lead in db.leads:
                    if lead.contact_id == contact.id:
                        lead_id = lead.id
                        break
                break

    # Create submission
    submission = FormSubmission(
        id=get_next_form_submission_id(),
        form_template_id=form_template_id,
        responses=responses,
        contact_id=contact_id,
        lead_id=lead_id,
        quote_id=quote_id,
        proposal_id=proposal_id,
        submitter_name=submitter_name,
        submitter_email=submitter_email,
        submitter_phone=submitter_phone,
        ip_address=ip_address,
        user_agent=user_agent,
        status="submitted",
        created_at=datetime.utcnow(),
    )

    db.form_submissions.append(submission)
    db.commit()

    return submission


def get_form_submissions(
    db: InMemoryDB,
    form_template_id: Optional[int] = None,
    status: Optional[str] = None,
    contact_id: Optional[int] = None,
    quote_id: Optional[int] = None,
) -> List[FormSubmission]:
    """
    Get form submissions with optional filtering.

    Args:
        db: Database session
        form_template_id: Filter by form template
        status: Filter by status
        contact_id: Filter by contact
        quote_id: Filter by quote

    Returns:
        List of FormSubmission objects
    """
    submissions = db.form_submissions

    if form_template_id is not None:
        submissions = [s for s in submissions if s.form_template_id == form_template_id]

    if status is not None:
        submissions = [s for s in submissions if s.status == status]

    if contact_id is not None:
        submissions = [s for s in submissions if s.contact_id == contact_id]

    if quote_id is not None:
        submissions = [s for s in submissions if s.quote_id == quote_id]

    # Sort by created_at descending
    submissions.sort(key=lambda s: s.created_at, reverse=True)

    return submissions


def update_submission_status(
    db: InMemoryDB,
    submission_id: int,
    status: str,
    notes: str = "",
    reviewed_by: Optional[int] = None,
) -> FormSubmission:
    """
    Update form submission status and notes.

    Args:
        db: Database session
        submission_id: Submission ID
        status: New status
        notes: Staff notes
        reviewed_by: User ID who reviewed

    Returns:
        Updated FormSubmission

    Raises:
        ValueError: If submission not found
    """
    submission = None
    for s in db.form_submissions:
        if s.id == submission_id:
            submission = s
            break

    if not submission:
        raise ValueError("Form submission not found")

    submission.status = status
    submission.notes = notes

    if status in ["reviewed", "processed"]:
        submission.reviewed_by = reviewed_by
        submission.reviewed_at = datetime.utcnow()

    submission.updated_at = datetime.utcnow()
    db.commit()

    return submission
