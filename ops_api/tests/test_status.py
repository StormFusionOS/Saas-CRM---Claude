"""Tests for status endpoints."""
def test_health_check(app):
    """Test health check endpoint."""
    # Simple test that app initializes
    assert app is not None
    assert hasattr(app, 'routes')
