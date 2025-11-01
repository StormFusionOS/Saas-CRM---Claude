"""Pytest configuration for Ops API tests."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db import get_db, init_demo_data

@pytest.fixture
def db():
    """Provide database session."""
    init_demo_data()
    return next(get_db())

@pytest.fixture
def app():
    """Provide app instance."""
    from app.main import create_app
    return create_app()
