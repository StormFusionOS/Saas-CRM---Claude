"""
Pytest configuration and fixtures for CRM API tests.
"""

import pytest
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db import get_db, init_demo_data, InMemoryDB
from app.main import create_app


@pytest.fixture(scope="function")
def db():
    """Provide a fresh database session for each test."""
    init_demo_data()  # Reset demo data
    db_instance = next(get_db())
    yield db_instance
    db_instance.close()


@pytest.fixture(scope="module")
def app():
    """Provide FastAPI app instance."""
    return create_app()


@pytest.fixture
def sample_contact_data():
    """Sample contact data for testing."""
    return {
        "email": "test@example.com",
        "phone": "+1234567890",
        "first_name": "Test",
        "last_name": "User",
        "company": "Test Corp",
        "tags": ["test", "sample"],
    }


@pytest.fixture
def sample_lead_data():
    """Sample lead data for testing."""
    return {
        "contact_id": 1,
        "status": "NEW",
        "source": "MANUAL",
        "value": 10000.0,
        "probability": 50,
        "notes": "Test lead",
    }


@pytest.fixture
def auth_headers(db):
    """Provide authentication headers with valid token."""
    from app.core.security import create_access_token
    from datetime import timedelta

    token = create_access_token(
        data={"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )

    return {"Authorization": f"Bearer {token}"}
