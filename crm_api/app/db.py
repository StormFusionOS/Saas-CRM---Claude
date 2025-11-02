"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API In-Memory Database for Testing.

PRODUCTION NOTE: Replace this with real SQLAlchemy session management:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from app.core.config import settings

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
"""

from typing import Generator, Optional
from datetime import datetime


# In-memory storage for testing
_users = []
_contacts = []
_leads = []
_interactions = []
_auto_reply_rules = []


class InMemoryDB:
    """Simple in-memory database for testing."""

    def __init__(self):
        self.users = _users
        self.contacts = _contacts
        self.leads = _leads
        self.interactions = _interactions
        self.auto_reply_rules = _auto_reply_rules
        self._committed = True

    def add(self, obj):
        """Add object to appropriate collection."""
        from app.models import User, Contact, Lead, Interaction, AutoReplyRule

        if isinstance(obj, User):
            self.users.append(obj)
        elif isinstance(obj, Contact):
            self.contacts.append(obj)
        elif isinstance(obj, Lead):
            self.leads.append(obj)
        elif isinstance(obj, Interaction):
            self.interactions.append(obj)
        elif isinstance(obj, AutoReplyRule):
            self.auto_reply_rules.append(obj)

    def delete(self, obj):
        """Remove object from appropriate collection."""
        from app.models import User, Contact, Lead, Interaction, AutoReplyRule

        if isinstance(obj, User):
            self.users.remove(obj)
        elif isinstance(obj, Contact):
            self.contacts.remove(obj)
        elif isinstance(obj, Lead):
            self.leads.remove(obj)
        elif isinstance(obj, Interaction):
            self.interactions.remove(obj)
        elif isinstance(obj, AutoReplyRule):
            self.auto_reply_rules.remove(obj)

    def commit(self):
        """Commit transaction (no-op in memory)."""
        self._committed = True

    def rollback(self):
        """Rollback transaction (no-op in memory)."""
        self._committed = False

    def close(self):
        """Close session (no-op in memory)."""
        pass

    def refresh(self, obj):
        """Refresh object (no-op in memory)."""
        pass

    def query(self, model):
        """Query helper."""
        from app.models import User, Contact, Lead, Interaction, AutoReplyRule

        if model == User:
            return QueryHelper(self.users)
        elif model == Contact:
            return QueryHelper(self.contacts)
        elif model == Lead:
            return QueryHelper(self.leads)
        elif model == Interaction:
            return QueryHelper(self.interactions)
        elif model == AutoReplyRule:
            return QueryHelper(self.auto_reply_rules)
        else:
            return QueryHelper([])


class QueryHelper:
    """Simple query helper for in-memory collections."""

    def __init__(self, collection: list):
        self.collection = collection
        self._filters = []

    def filter(self, *args, **kwargs):
        """Add filter (simplified)."""
        # Store filter conditions
        for key, value in kwargs.items():
            self._filters.append((key, value))
        return self

    def filter_by(self, **kwargs):
        """Filter by exact match."""
        return self.filter(**kwargs)

    def first(self) -> Optional[object]:
        """Get first matching object."""
        results = self.all()
        return results[0] if results else None

    def all(self) -> list:
        """Get all matching objects."""
        results = self.collection.copy()

        # Apply filters
        for key, value in self._filters:
            results = [
                obj for obj in results
                if getattr(obj, key, None) == value
            ]

        return results

    def count(self) -> int:
        """Count matching objects."""
        return len(self.all())

    def one(self):
        """Get exactly one object (raises if not found or multiple)."""
        results = self.all()
        if len(results) == 0:
            raise Exception("No results found")
        if len(results) > 1:
            raise Exception("Multiple results found")
        return results[0]

    def one_or_none(self) -> Optional[object]:
        """Get one object or None."""
        results = self.all()
        if len(results) == 0:
            return None
        if len(results) > 1:
            raise Exception("Multiple results found")
        return results[0]


def get_db() -> Generator[InMemoryDB, None, None]:
    """
    Get database session.

    Yields:
        Database session
    """
    db = InMemoryDB()
    try:
        yield db
    finally:
        db.close()


def init_demo_data():
    """Initialize demo data for testing."""
    from app.models import User
    from app.core.security import hash_password, Role

    # Clear existing data
    _users.clear()
    _contacts.clear()
    _leads.clear()
    _interactions.clear()
    _auto_reply_rules.clear()

    # Create demo users
    demo_users = [
        User(
            id=1,
            email="Nathan@RiverCityClean.com",
            hashed_password=hash_password("password123"),
            full_name="Nathan - Sales",
            roles=[Role.SALES.value],
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        User(
            id=2,
            email="manager@rivercityclean.com",
            hashed_password=hash_password("password123"),
            full_name="Sales Manager",
            roles=[Role.SALES_MANAGER.value],
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        User(
            id=3,
            email="owner@rivercityclean.com",
            hashed_password=hash_password("password123"),
            full_name="Owner",
            roles=[Role.OWNER.value],
            is_active=True,
            created_at=datetime.utcnow(),
        ),
    ]

    _users.extend(demo_users)


# Initialize demo data on module load
init_demo_data()


__all__ = ["get_db", "InMemoryDB", "init_demo_data"]
