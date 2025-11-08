"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Tests for AI Review Endpoints

Covers:
- GET /ai/review/pending - List pending changes
- GET /ai/review/{id} - Get change details
- POST /ai/review/{id}/approve - Approve and execute change
- POST /ai/review/{id}/reject - Reject change
- Task logs audit trail
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.db_models import ChangeLogModel, TaskLogModel
from app.core.security import create_access_token
from app.schemas.integrations import ApplyResult


# Test client
client = TestClient(app)


# ============================================================================
# GET /ai/review/pending Tests
# ============================================================================


def test_get_pending_changes_empty(db):
    """Test getting pending changes when none exist."""
    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/ai/review/pending", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert len(data["changes"]) == 0
    assert data["page"] == 1
    assert data["has_more"] is False


def test_get_pending_changes_with_data(db):
    """Test getting pending changes with sample data."""
    # Create test changes
    for i in range(5):
        change = ChangeLogModel(
            change_id=f"test_change_{i}",
            module="seo_meta",
            action="update_meta_title",
            target_type="wordpress_post",
            target_id=i,
            old_value={"title": f"Old Title {i}"},
            new_value={"title": f"New Title {i}"},
            status="PENDING",
            created_at=datetime.utcnow() - timedelta(hours=i)
        )
        db.add(change)

    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/ai/review/pending", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 5
    assert len(data["changes"]) == 5
    assert data["page"] == 1
    assert data["has_more"] is False

    # Verify newest first (created_at DESC)
    assert data["changes"][0]["change_id"] == "test_change_0"
    assert data["changes"][4]["change_id"] == "test_change_4"


def test_get_pending_changes_pagination(db):
    """Test pagination of pending changes."""
    # Create 25 test changes
    for i in range(25):
        change = ChangeLogModel(
            change_id=f"page_test_{i}",
            module="seo_meta",
            action="update_meta_title",
            target_type="wordpress_post",
            target_id=i,
            new_value={"title": f"Title {i}"},
            status="PENDING",
            created_at=datetime.utcnow() - timedelta(minutes=i)
        )
        db.add(change)

    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Page 1 (limit 10)
    response = client.get("/api/v1/ai/review/pending?page=1&limit=10", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 25
    assert len(data["changes"]) == 10
    assert data["page"] == 1
    assert data["has_more"] is True

    # Page 2
    response = client.get("/api/v1/ai/review/pending?page=2&limit=10", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 25
    assert len(data["changes"]) == 10
    assert data["page"] == 2
    assert data["has_more"] is True

    # Page 3 (last page)
    response = client.get("/api/v1/ai/review/pending?page=3&limit=10", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 25
    assert len(data["changes"]) == 5
    assert data["page"] == 3
    assert data["has_more"] is False


def test_get_pending_changes_module_filter(db):
    """Test filtering pending changes by module."""
    # Create changes from different modules
    for i in range(3):
        change1 = ChangeLogModel(
            change_id=f"seo_{i}",
            module="seo_meta",
            action="update_meta_title",
            target_type="wordpress_post",
            target_id=i,
            new_value={"title": f"SEO Title {i}"},
            status="PENDING",
            created_at=datetime.utcnow()
        )
        db.add(change1)

        change2 = ChangeLogModel(
            change_id=f"ctr_{i}",
            module="ctr_optimizer",
            action="update_headline",
            target_type="wordpress_post",
            target_id=i + 100,
            new_value={"headline": f"CTR Headline {i}"},
            status="PENDING",
            created_at=datetime.utcnow()
        )
        db.add(change2)

    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Filter by seo_meta
    response = client.get("/api/v1/ai/review/pending?module=seo_meta", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3
    assert all(c["module"] == "seo_meta" for c in data["changes"])

    # Filter by ctr_optimizer
    response = client.get("/api/v1/ai/review/pending?module=ctr_optimizer", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3
    assert all(c["module"] == "ctr_optimizer" for c in data["changes"])


def test_get_pending_changes_excludes_non_pending(db):
    """Test that only PENDING changes are returned."""
    # Create changes with different statuses
    statuses = ["PENDING", "APPROVED", "REJECTED", "EXECUTED", "FAILED"]
    for i, status in enumerate(statuses):
        change = ChangeLogModel(
            change_id=f"status_test_{i}",
            module="seo_meta",
            action="update_meta_title",
            target_type="wordpress_post",
            target_id=i,
            new_value={"title": f"Title {i}"},
            status=status,
            created_at=datetime.utcnow()
        )
        db.add(change)

    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/ai/review/pending", headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Only the PENDING change should be returned
    assert data["total"] == 1
    assert data["changes"][0]["status"] == "PENDING"


# ============================================================================
# GET /ai/review/{id} Tests
# ============================================================================


def test_get_change_details_success(db):
    """Test getting details of a specific change."""
    change = ChangeLogModel(
        change_id="detail_test_1",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=123,
        old_value={"title": "Old SEO Title"},
        new_value={"title": "New SEO Title with Keywords"},
        reasoning="Current title lacks primary keyword",
        ai_confidence=0.92,
        evidence={"keyword_density": 0.0},
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/ai/review/detail_test_1", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["change_id"] == "detail_test_1"
    assert data["module"] == "seo_meta"
    assert data["old_value"]["title"] == "Old SEO Title"
    assert data["new_value"]["title"] == "New SEO Title with Keywords"
    assert data["reasoning"] == "Current title lacks primary keyword"
    assert data["ai_confidence"] == 0.92


def test_get_change_details_not_found(db):
    """Test getting details of non-existent change."""
    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/ai/review/nonexistent_change", headers=headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ============================================================================
# POST /ai/review/{id}/approve Tests
# ============================================================================


@pytest.mark.asyncio
async def test_approve_change_success(db):
    """Test successfully approving and executing a change."""
    # Create pending change
    change = ChangeLogModel(
        change_id="approve_test_1",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=123,
        new_value={"title": "New Title"},
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Mock AI Node client
    mock_result = ApplyResult(
        change_id=123,
        success=True,
        applied_at=datetime.utcnow(),
        message="Change applied successfully",
        details={"modified_fields": ["title"]},
        errors=None
    )

    with patch('app.api.routes.ai_review.get_ai_node_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.execute_change = AsyncMock(return_value=mock_result)
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/ai/review/approve_test_1/approve",
            headers=headers,
            json={"decision_reason": "Looks good"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["change_id"] == "approve_test_1"
        assert data["status"] == "executed"
        assert "successfully" in data["message"].lower()
        assert data["task_log_id"] is not None

        # Verify change was updated in database
        db.refresh(change)
        assert change.status == "EXECUTED"
        assert change.approved_by == 1
        assert change.executed_by == 1
        assert change.approved_at is not None
        assert change.executed_at is not None

        # Verify task log was created
        task_log = db.query(TaskLogModel).filter(
            TaskLogModel.task_id == data["task_log_id"]
        ).first()

        assert task_log is not None
        assert task_log.status == "completed"
        assert task_log.module == "ai_review"


@pytest.mark.asyncio
async def test_approve_change_execution_failed(db):
    """Test approving a change but execution fails."""
    change = ChangeLogModel(
        change_id="approve_fail_test",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=456,
        new_value={"title": "New Title"},
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Mock AI Node client to return failed execution
    mock_result = ApplyResult(
        change_id=456,
        success=False,
        applied_at=datetime.utcnow(),
        message="Execution failed: validation error",
        details={},
        errors=["Field 'title' exceeds maximum length"]
    )

    with patch('app.api.routes.ai_review.get_ai_node_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.execute_change = AsyncMock(return_value=mock_result)
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/ai/review/approve_fail_test/approve",
            headers=headers,
            json={"decision_reason": "Approving"}
        )

        assert response.status_code == 500
        assert "execution failed" in response.json()["detail"].lower()

        # Verify change status was set to FAILED
        db.refresh(change)
        assert change.status == "FAILED"


def test_approve_change_not_pending(db):
    """Test approving a change that is not in PENDING status."""
    change = ChangeLogModel(
        change_id="already_approved",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=789,
        new_value={"title": "New Title"},
        status="EXECUTED",  # Already executed
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/ai/review/already_approved/approve",
        headers=headers,
        json={"decision_reason": "Approving"}
    )

    assert response.status_code == 400
    assert "not pending" in response.json()["detail"].lower()


def test_approve_change_not_found(db):
    """Test approving a non-existent change."""
    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/ai/review/nonexistent/approve",
        headers=headers,
        json={"decision_reason": "Approving"}
    )

    assert response.status_code == 404


# ============================================================================
# POST /ai/review/{id}/reject Tests
# ============================================================================


def test_reject_change_success(db):
    """Test successfully rejecting a change."""
    change = ChangeLogModel(
        change_id="reject_test_1",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=999,
        new_value={"title": "Rejected Title"},
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/ai/review/reject_test_1/reject",
        headers=headers,
        json={"decision_reason": "Conflicts with brand guidelines"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["change_id"] == "reject_test_1"
    assert data["status"] == "rejected"
    assert "successfully" in data["message"].lower()
    assert data["task_log_id"] is not None

    # Verify change was updated in database
    db.refresh(change)
    assert change.status == "REJECTED"
    assert change.rejected_by == 1
    assert change.rejected_at is not None
    assert change.decision_reason == "Conflicts with brand guidelines"

    # Verify task log was created
    task_log = db.query(TaskLogModel).filter(
        TaskLogModel.task_id == data["task_log_id"]
    ).first()

    assert task_log is not None
    assert task_log.status == "completed"
    assert task_log.module == "ai_review"


def test_reject_change_missing_reason(db):
    """Test rejecting a change without providing reason."""
    change = ChangeLogModel(
        change_id="reject_no_reason",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=888,
        new_value={"title": "Title"},
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Missing decision_reason field
    response = client.post(
        "/api/v1/ai/review/reject_no_reason/reject",
        headers=headers,
        json={}
    )

    assert response.status_code == 422  # Validation error


def test_reject_change_not_pending(db):
    """Test rejecting a change that is not in PENDING status."""
    change = ChangeLogModel(
        change_id="already_rejected",
        module="seo_meta",
        action="update_meta_title",
        target_type="wordpress_post",
        target_id=777,
        new_value={"title": "Title"},
        status="REJECTED",  # Already rejected
        created_at=datetime.utcnow()
    )
    db.add(change)
    db.commit()

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/ai/review/already_rejected/reject",
        headers=headers,
        json={"decision_reason": "Rejecting"}
    )

    assert response.status_code == 400
    assert "not pending" in response.json()["detail"].lower()


def test_reject_change_not_found(db):
    """Test rejecting a non-existent change."""
    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/ai/review/nonexistent/reject",
        headers=headers,
        json={"decision_reason": "Rejecting"}
    )

    assert response.status_code == 404


# ============================================================================
# RBAC Tests
# ============================================================================


def test_pending_requires_auth(db):
    """Test that pending endpoint requires authentication."""
    response = client.get("/api/v1/ai/review/pending")
    assert response.status_code == 422  # Missing auth


def test_approve_requires_auth(db):
    """Test that approve endpoint requires authentication."""
    response = client.post(
        "/api/v1/ai/review/test_id/approve",
        json={"decision_reason": "Test"}
    )
    assert response.status_code == 422  # Missing auth


def test_reject_requires_auth(db):
    """Test that reject endpoint requires authentication."""
    response = client.post(
        "/api/v1/ai/review/test_id/reject",
        json={"decision_reason": "Test"}
    )
    assert response.status_code == 422  # Missing auth
