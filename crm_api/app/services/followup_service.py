"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Follow-Up Automation Service - Trigger and manage automated sequences.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.db import InMemoryDB
from app.models import (
    FollowUpSequence,
    FollowUpInstance,
    FollowUpTask,
    get_next_followup_instance_id,
    get_next_followup_task_id,
)


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Render template with variables.

    Replaces {{variable_name}} with values from variables dict.

    Args:
        template: Template string with {{placeholders}}
        variables: Dict of variable values

    Returns:
        Rendered string
    """
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def get_lead_variables(db: InMemoryDB, lead_id: int, contact_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get template variables for a lead.

    Args:
        db: Database session
        lead_id: Lead ID
        contact_id: Optional contact ID

    Returns:
        Dict of variables for template rendering
    """
    variables = {}

    # Get contact
    if contact_id:
        contact = next((c for c in db.contacts if c.id == contact_id), None)
        if contact:
            variables["first_name"] = contact.first_name
            variables["last_name"] = contact.last_name
            variables["email"] = contact.email or ""
            variables["phone"] = contact.phone or ""
            variables["company_name"] = contact.company or ""

    # Get lead
    lead = next((l for l in db.leads if l.id == lead_id), None)
    if lead:
        variables["lead_status"] = lead.status

    return variables


def trigger_sequence(
    db: InMemoryDB,
    sequence_id: int,
    lead_id: Optional[int] = None,
    contact_id: Optional[int] = None,
    quote_id: Optional[int] = None,
) -> FollowUpInstance:
    """
    Trigger a follow-up sequence for a lead.

    Args:
        db: Database session
        sequence_id: Sequence to trigger
        lead_id: Lead ID
        contact_id: Contact ID
        quote_id: Quote ID (if applicable)

    Returns:
        Created FollowUpInstance

    Raises:
        ValueError: If sequence not found or inactive
    """
    # Get sequence
    sequence = db.followup_sequences.get(sequence_id)
    if not sequence:
        raise ValueError(f"Sequence {sequence_id} not found")

    if not sequence.is_active:
        raise ValueError(f"Sequence {sequence_id} is not active")

    # Create instance
    instance = FollowUpInstance(
        id=get_next_followup_instance_id(),
        sequence_id=sequence_id,
        lead_id=lead_id,
        contact_id=contact_id,
        quote_id=quote_id,
        status="active",
        current_step_index=0,
        started_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db.followup_instances.append(instance)

    # Update sequence stats
    sequence.total_started += 1

    # Schedule first task
    if sequence.steps:
        _schedule_next_step(db, instance, sequence)

    db.commit()

    return instance


def _schedule_next_step(
    db: InMemoryDB,
    instance: FollowUpInstance,
    sequence: FollowUpSequence,
) -> Optional[FollowUpTask]:
    """
    Schedule the next step in a sequence.

    Args:
        db: Database session
        instance: Sequence instance
        sequence: Sequence template

    Returns:
        Created task or None if sequence complete
    """
    if instance.current_step_index >= len(sequence.steps):
        # Sequence complete
        instance.status = "completed"
        instance.completed_at = datetime.utcnow()
        sequence.total_completed += 1
        return None

    step = sequence.steps[instance.current_step_index]

    # Calculate scheduled time
    if instance.current_step_index == 0:
        # First step - delay from sequence start
        scheduled_for = instance.started_at + timedelta(hours=step.delay_hours)
    else:
        # Subsequent steps - delay from last action
        if instance.last_action_at:
            scheduled_for = instance.last_action_at + timedelta(hours=step.delay_hours)
        else:
            scheduled_for = instance.started_at + timedelta(hours=step.delay_hours)

    # Get variables for template rendering
    variables = get_lead_variables(db, instance.lead_id, instance.contact_id)

    # Render templates
    subject = render_template(step.subject, variables)
    body = render_template(step.body_template, variables)
    task_title = render_template(step.task_title, variables)
    task_description = render_template(step.task_description, variables)

    # Create task
    task = FollowUpTask(
        id=get_next_followup_task_id(),
        instance_id=instance.id,
        sequence_id=sequence.id,
        step_id=step.id,
        lead_id=instance.lead_id,
        contact_id=instance.contact_id,
        task_type=step.action_type,
        status="pending",
        scheduled_for=scheduled_for,
        subject=subject,
        body=body,
        task_title=task_title,
        task_description=task_description,
        created_at=datetime.utcnow(),
    )

    db.followup_tasks.append(task)

    return task


def stop_instance(
    db: InMemoryDB,
    instance_id: int,
    reason: str = "Manually stopped",
) -> FollowUpInstance:
    """
    Stop a running sequence instance.

    Args:
        db: Database session
        instance_id: Instance to stop
        reason: Reason for stopping

    Returns:
        Updated instance

    Raises:
        ValueError: If instance not found
    """
    instance = next((i for i in db.followup_instances if i.id == instance_id), None)
    if not instance:
        raise ValueError(f"Instance {instance_id} not found")

    instance.status = "stopped"
    instance.stopped_at = datetime.utcnow()
    instance.stop_reason = reason
    instance.updated_at = datetime.utcnow()

    # Update sequence stats
    sequence = db.followup_sequences.get(instance.sequence_id)
    if sequence:
        sequence.total_stopped += 1

    db.commit()

    return instance


def get_active_instances(
    db: InMemoryDB,
    lead_id: Optional[int] = None,
    sequence_id: Optional[int] = None,
) -> List[FollowUpInstance]:
    """
    Get active sequence instances.

    Args:
        db: Database session
        lead_id: Filter by lead ID
        sequence_id: Filter by sequence ID

    Returns:
        List of active instances
    """
    instances = [i for i in db.followup_instances if i.status == "active"]

    if lead_id:
        instances = [i for i in instances if i.lead_id == lead_id]

    if sequence_id:
        instances = [i for i in instances if i.sequence_id == sequence_id]

    # Sort by started_at descending
    instances.sort(key=lambda i: i.started_at, reverse=True)

    return instances


def get_pending_tasks(
    db: InMemoryDB,
    before: Optional[datetime] = None,
) -> List[FollowUpTask]:
    """
    Get pending tasks that are due.

    Args:
        db: Database session
        before: Get tasks scheduled before this time (defaults to now)

    Returns:
        List of pending tasks
    """
    if not before:
        before = datetime.utcnow()

    tasks = [
        t for t in db.followup_tasks
        if t.status == "pending" and t.scheduled_for <= before
    ]

    # Sort by scheduled_for ascending
    tasks.sort(key=lambda t: t.scheduled_for)

    return tasks
