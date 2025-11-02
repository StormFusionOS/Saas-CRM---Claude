"""Simple test that doesn't depend on conftest."""

def test_basic():
    """Most basic test possible."""
    assert 1 + 1 == 2

def test_imports():
    """Test that imports work."""
    from fastapi.exceptions import RequestValidationError, HTTPException
    from starlette.responses import JSONResponse

    assert RequestValidationError is not None
    assert HTTPException is not None
    assert JSONResponse is not None
