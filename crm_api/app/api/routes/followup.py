"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Follow-Up Automation API Routes.

Endpoints for managing automated follow-up sequences.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db import get_db, InMemoryDB
from app.schemas.followup import (
    FollowUpSequenceResponse,
    FollowUpSequenceListItem,
    FollowUpInstanceResponse,
    FollowUpInstanceListItem,
    FollowUpTaskResponse,
    FollowUpTaskListItem,
    TriggerSequenceRequest,
    FollowUpStepSchema,
)
from app.services import followup_service
from app.api.deps import require_sales_claims


router = APIRouter(tags=["followup"])


# ============================================================================
# Sequence Endpoints
# ============================================================================


@router.get("/followup/sequences", response_model=List[FollowUpSequenceListItem])
def list_sequences(
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[FollowUpSequenceListItem]:
    """
    List all follow-up sequences (STAFF ONLY).
    """
    sequences = list(db.followup_sequences.values())

    # Filter
    if is_active is not None:
        sequences = [s for s in sequences if s.is_active == is_active]

    if category:
        sequences = [s for s in sequences if s.category == category]

    # Sort by priority
    sequences.sort(key=lambda s: (s.priority, s.name), reverse=True)

    # Build response
    return [
        FollowUpSequenceListItem(
            id=seq.id,
            name=seq.name,
            description=seq.description,
            trigger_event=seq.trigger_event,
            is_active=seq.is_active,
            step_count=len(seq.steps),
            total_started=seq.total_started,
            category=seq.category,
            created_at=seq.created_at,
        )
        for seq in sequences
    ]


@router.get("/followup/sequences/{sequence_id}", response_model=FollowUpSequenceResponse)
def get_sequence(
    sequence_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FollowUpSequenceResponse:
    """
    Get sequence details (STAFF ONLY).
    """
    sequence = db.followup_sequences.get(sequence_id)
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found",
        )

    # Convert steps
    steps = [FollowUpStepSchema(**step.__dict__) for step in sequence.steps]

    return FollowUpSequenceResponse(
        id=sequence.id,
        name=sequence.name,
        description=sequence.description,
        trigger_event=sequence.trigger_event,
        trigger_conditions=sequence.trigger_conditions,
        steps=steps,
        is_active=sequence.is_active,
        priority=sequence.priority,
        stop_on_response=sequence.stop_on_response,
        stop_on_status_change=sequence.stop_on_status_change,
        stop_statuses=sequence.stop_statuses,
        category=sequence.category,
        tags=sequence.tags,
        total_started=sequence.total_started,
        total_completed=sequence.total_completed,
        total_stopped=sequence.total_stopped,
        metadata=sequence.metadata,
        created_at=sequence.created_at,
        updated_at=sequence.updated_at,
        created_by=sequence.created_by,
    )


# ============================================================================
# Instance Endpoints
# ============================================================================


@router.post("/followup/trigger", response_model=FollowUpInstanceResponse, status_code=status.HTTP_201_CREATED)
def trigger_sequence(
    request: TriggerSequenceRequest,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> FollowUpInstanceResponse:
    """
    Manually trigger a sequence for a lead (STAFF ONLY).
    """
    try:
        instance = followup_service.trigger_sequence(
            db=db,
            sequence_id=request.sequence_id,
            lead_id=request.lead_id,
            contact_id=request.contact_id,
            quote_id=request.quote_id,
        )

        # Get sequence name
        sequence = db.followup_sequences.get(instance.sequence_id)
        sequence_name = sequence.name if sequence else f"Sequence #{instance.sequence_id}"

        return FollowUpInstanceResponse(
            id=instance.id,
            sequence_id=instance.sequence_id,
            sequence_name=sequence_name,
            lead_id=instance.lead_id,
            contact_id=instance.contact_id,
            quote_id=instance.quote_id,
            status=instance.status,
            current_step_index=instance.current_step_index,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
            stopped_at=instance.stopped_at,
            stop_reason=instance.stop_reason,
            steps_completed=instance.steps_completed,
            last_action_at=instance.last_action_at,
            has_responded=instance.has_responded,
            response_date=instance.response_date,
            response_type=instance.response_type,
            metadata=instance.metadata,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/followup/instances", response_model=List[FollowUpInstanceListItem])
def list_instances(
    lead_id: Optional[int] = None,
    sequence_id: Optional[int] = None,
    status: Optional[str] = None,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[FollowUpInstanceListItem]:
    """
    List follow-up instances (STAFF ONLY).
    """
    instances = db.followup_instances

    # Filter
    if lead_id:
        instances = [i for i in instances if i.lead_id == lead_id]

    if sequence_id:
        instances = [i for i in instances if i.sequence_id == sequence_id]

    if status:
        instances = [i for i in instances if i.status == status]

    # Sort by started_at descending
    instances = sorted(instances, key=lambda i: i.started_at, reverse=True)

    # Build response
    result = []
    for instance in instances:
        # Get sequence
        sequence = db.followup_sequences.get(instance.sequence_id)
        sequence_name = sequence.name if sequence else f"Sequence #{instance.sequence_id}"
        total_steps = len(sequence.steps) if sequence else 0

        result.append(
            FollowUpInstanceListItem(
                id=instance.id,
                sequence_id=instance.sequence_id,
                sequence_name=sequence_name,
                lead_id=instance.lead_id,
                contact_id=instance.contact_id,
                status=instance.status,
                current_step_index=instance.current_step_index,
                total_steps=total_steps,
                started_at=instance.started_at,
                has_responded=instance.has_responded,
            )
        )

    return result


@router.post("/followup/instances/{instance_id}/stop")
def stop_instance(
    instance_id: int,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
):
    """
    Stop a running sequence instance (STAFF ONLY).
    """
    try:
        instance = followup_service.stop_instance(db, instance_id, reason="Manually stopped")
        return {"message": "Instance stopped successfully", "instance_id": instance.id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Task Endpoints
# ============================================================================


@router.get("/followup/tasks", response_model=List[FollowUpTaskListItem])
def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 50,
    db: InMemoryDB = Depends(get_db),
    current_user: dict = Depends(require_sales_claims),
) -> List[FollowUpTaskListItem]:
    """
    List follow-up tasks (STAFF ONLY).
    """
    tasks = db.followup_tasks

    # Filter
    if status:
        tasks = [t for t in tasks if t.status == status]

    if task_type:
        tasks = [t for t in tasks if t.task_type == task_type]

    # Sort by scheduled_for ascending
    tasks = sorted(tasks, key=lambda t: t.scheduled_for)

    # Limit
    tasks = tasks[:limit]

    # Build response
    return [
        FollowUpTaskListItem(
            id=task.id,
            task_type=task.task_type,
            status=task.status,
            scheduled_for=task.scheduled_for,
            subject=task.subject,
            task_title=task.task_title,
            assigned_to=task.assigned_to,
            created_at=task.created_at,
        )
        for task in tasks
    ]
