"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Tests for Ops API database."""

import pytest
from app.db import get_db, init_demo_data, InMemoryDB
from app.security import OpsRole


def test_get_db():
    """Test database session generation."""
    db = next(get_db())

    assert db is not None
    assert isinstance(db, InMemoryDB)
    assert hasattr(db, 'users')
    assert hasattr(db, 'alerts')


def test_demo_data_initialization():
    """Test demo data is properly initialized."""
    init_demo_data()
    db = next(get_db())

    # Should have 3 demo users
    assert len(db.users) == 3

    # Check first user
    nathan = db.users[0]
    assert nathan.email == "Nathan@RiverCityClean.com"
    assert nathan.full_name == "Nathan - DevOps"
    assert OpsRole.DEVOPS.value in nathan.roles
    assert nathan.is_active is True


def test_query_operations(db):
    """Test database query operations."""
    # Test all() operation
    all_users = db.query(type('User', (), {})).all()
    assert isinstance(all_users, list)

    # Test first() operation
    first_user = db.query(type('User', (), {})).first()

    # Test filter operation
    filtered = db.query(type('User', (), {})).filter(id=1).all()


def test_db_add_and_query(db):
    """Test adding items to database."""
    from app.models.alert import Alert
    from datetime import datetime

    alert = Alert(
        id=1,
        severity="HIGH",
        message="Test",
        source="test",
        created_at=datetime.utcnow()
    )

    db.add(alert)
    db.commit()

    # Alert should be in the collection
    assert len(db.alerts) > 0
