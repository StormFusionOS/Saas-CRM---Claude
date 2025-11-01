"""Ops API in-memory database for testing."""

from typing import Generator
from datetime import datetime
from app.security import hash_password, OpsRole

# In-memory collections
_users = []
_alerts = []
_service_health = []
_backup_runs = []
_task_runs = []
_schedules = []
_suggestions = []
_file_integrity = []
_change_logs = []


class InMemoryDB:
    """Simple in-memory database for testing."""

    def __init__(self):
        self.users = _users
        self.alerts = _alerts
        self.service_health = _service_health
        self.backup_runs = _backup_runs
        self.task_runs = _task_runs
        self.schedules = _schedules
        self.suggestions = _suggestions
        self.file_integrity = _file_integrity
        self.change_logs = _change_logs

    def add(self, obj):
        """Add object to appropriate collection."""
        collection_name = type(obj).__name__.lower() + 's'
        if hasattr(self, collection_name):
            getattr(self, collection_name).append(obj)

    def commit(self):
        """Commit (no-op)."""
        pass

    def close(self):
        """Close (no-op)."""
        pass

    def query(self, model):
        """Query helper."""
        from app.models.alert import Alert
        from app.models.service_health import ServiceHealth

        model_map = {
            'User': self.users,
            'Alert': self.alerts,
            'ServiceHealth': self.service_health,
            'BackupRun': self.backup_runs,
            'TaskRun': self.task_runs,
            'Schedule': self.schedules,
            'Suggestion': self.suggestions,
        }

        collection = model_map.get(model.__name__, [])
        return QueryHelper(collection)


class QueryHelper:
    """Simple query helper."""

    def __init__(self, collection: list):
        self.collection = collection
        self._filters = []

    def filter(self, **kwargs):
        """Add filter."""
        for key, value in kwargs.items():
            self._filters.append((key, value))
        return self

    def all(self) -> list:
        """Get all matching."""
        results = self.collection.copy()
        for key, value in self._filters:
            results = [obj for obj in results if getattr(obj, key, None) == value]
        return results

    def first(self):
        """Get first matching."""
        results = self.all()
        return results[0] if results else None


def get_db() -> Generator[InMemoryDB, None, None]:
    """Get database session."""
    db = InMemoryDB()
    try:
        yield db
    finally:
        db.close()


def init_demo_data():
    """Initialize demo data."""
    from dataclasses import dataclass

    @dataclass
    class User:
        id: int
        email: str
        hashed_password: str
        full_name: str
        roles: list
        is_active: bool = True

    _users.clear()
    _users.extend([
        User(1, "devops@example.com", hash_password("password123"), "DevOps Engineer", [OpsRole.DEVOPS.value], True),
        User(2, "seo@example.com", hash_password("password123"), "SEO Engineer", [OpsRole.SEO_ENGINEER.value], True),
        User(3, "owner@example.com", hash_password("password123"), "Owner", [OpsRole.OWNER.value], True),
    ])


init_demo_data()

__all__ = ["get_db", "InMemoryDB", "init_demo_data"]
