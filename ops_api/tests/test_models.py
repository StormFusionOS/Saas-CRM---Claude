"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Tests for Ops API models."""

import pytest
from datetime import datetime


def test_alert_model():
    """Test Alert model creation."""
    from app.models.alert import Alert

    alert = Alert(
        id=1,
        severity="HIGH",
        message="Test alert",
        source="monitoring",
        created_at=datetime.utcnow(),
        resolved=False
    )

    assert alert.id == 1
    assert alert.severity == "HIGH"
    assert alert.message == "Test alert"
    assert alert.resolved is False


def test_service_health_model():
    """Test ServiceHealth model creation."""
    from app.models.service_health import ServiceHealth

    health = ServiceHealth(
        id=1,
        service_name="api",
        status="UP",
        last_check=datetime.utcnow(),
        response_time_ms=45.2
    )

    assert health.id == 1
    assert health.service_name == "api"
    assert health.status == "UP"
    assert health.response_time_ms == 45.2
