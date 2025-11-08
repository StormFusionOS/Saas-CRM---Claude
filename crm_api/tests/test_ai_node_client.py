"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Tests for AI Node Client Service

Covers:
- Client initialization
- Database configuration loading
- HTTP request methods (trigger_ctr_test, trigger_content_refresh, execute_change)
- Retry logic with exponential backoff
- Authentication headers
- Error handling
"""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
import httpx
from cryptography.fernet import Fernet

from app.services.ai_node_client import (
    AINodeClient,
    AINodeNotConfiguredError,
    AINodeConnectionError,
    get_ai_node_client
)
from app.models.integrations import IntegrationSetting
from app.schemas.integrations import (
    CtrTestIn,
    ContentRefreshIn,
    JobAck202,
    ApplyResult
)


# ============================================================================
# Client Initialization Tests
# ============================================================================


def test_ai_node_client_init():
    """Test AINodeClient initialization with direct parameters."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token-123",
        timeout=60.0,
        max_retries=5
    )

    assert client.base_url == "https://ai-node.example.com"
    assert client.bearer_token == "test-token-123"
    assert client.timeout == 60.0
    assert client.max_retries == 5


def test_ai_node_client_strips_trailing_slash():
    """Test that trailing slash is removed from base_url."""
    client = AINodeClient(
        base_url="https://ai-node.example.com/",
        bearer_token="test-token"
    )

    assert client.base_url == "https://ai-node.example.com"


def test_ai_node_client_from_db_success(db):
    """Test creating client from database configuration."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create config in database
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=True,
            created_by=3
        )
        config.set_secret("bearer-token-xyz")
        db.add(config)
        db.commit()

        # Create client from DB
        client = AINodeClient.from_db(db)

        assert client.base_url == "https://ai-node.example.com"
        assert client.bearer_token == "bearer-token-xyz"


def test_ai_node_client_from_db_not_configured(db):
    """Test that from_db raises error when AI Node is not configured."""
    with pytest.raises(AINodeNotConfiguredError) as exc_info:
        AINodeClient.from_db(db)

    assert "not configured" in str(exc_info.value).lower()


def test_ai_node_client_from_db_no_base_url(db):
    """Test that from_db raises error when base_url is missing."""
    config = IntegrationSetting(
        namespace="ai_node",
        base_url="",  # Empty base URL
        review_mode=True,
        created_by=3
    )
    db.add(config)
    db.commit()

    with pytest.raises(AINodeNotConfiguredError):
        AINodeClient.from_db(db)


def test_ai_node_client_from_db_without_token(db):
    """Test creating client from DB without bearer token."""
    config = IntegrationSetting(
        namespace="ai_node",
        base_url="https://ai-node.example.com",
        review_mode=True,
        created_by=3
    )
    db.add(config)
    db.commit()

    client = AINodeClient.from_db(db)

    assert client.base_url == "https://ai-node.example.com"
    assert client.bearer_token is None


# ============================================================================
# HTTP Headers Tests
# ============================================================================


def test_get_headers_with_token():
    """Test that headers include Authorization when token is provided."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token-123"
    )

    headers = client._get_headers()

    assert headers["Authorization"] == "Bearer test-token-123"
    assert headers["Content-Type"] == "application/json"
    assert "User-Agent" in headers


def test_get_headers_without_token():
    """Test that headers exclude Authorization when token is not provided."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token=None
    )

    headers = client._get_headers()

    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"


# ============================================================================
# Retry Logic Tests
# ============================================================================


@pytest.mark.asyncio
async def test_retry_request_success_on_first_attempt():
    """Test successful request on first attempt."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token"
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        response = await client._retry_request("GET", "https://ai-node.example.com/ping")

        assert response.status_code == 200
        # Should only call once (no retries)
        assert mock_client_instance.request.call_count == 1


@pytest.mark.asyncio
async def test_retry_request_retries_on_429():
    """Test that 429 status triggers retry with exponential backoff."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token",
        max_retries=2
    )

    # First two attempts return 429, third returns 200
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(
            side_effect=[mock_response_429, mock_response_429, mock_response_200]
        )
        mock_client_class.return_value = mock_client_instance

        with patch('asyncio.sleep') as mock_sleep:  # Mock sleep to speed up test
            response = await client._retry_request("GET", "https://ai-node.example.com/ping")

            assert response.status_code == 200
            assert mock_client_instance.request.call_count == 3
            # Should sleep with exponential backoff: 1s, 2s
            assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_retry_request_retries_on_500():
    """Test that 5xx errors trigger retry."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token",
        max_retries=1
    )

    mock_response_500 = MagicMock()
    mock_response_500.status_code = 500

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(
            side_effect=[mock_response_500, mock_response_200]
        )
        mock_client_class.return_value = mock_client_instance

        with patch('asyncio.sleep'):
            response = await client._retry_request("GET", "https://ai-node.example.com/ping")

            assert response.status_code == 200
            assert mock_client_instance.request.call_count == 2


@pytest.mark.asyncio
async def test_retry_request_exhausts_retries():
    """Test that retries are exhausted and final response is returned."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token",
        max_retries=2
    )

    mock_response_503 = MagicMock()
    mock_response_503.status_code = 503

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response_503)
        mock_client_class.return_value = mock_client_instance

        with patch('asyncio.sleep'):
            response = await client._retry_request("GET", "https://ai-node.example.com/ping")

            assert response.status_code == 503
            # Should try 3 times total (initial + 2 retries)
            assert mock_client_instance.request.call_count == 3


@pytest.mark.asyncio
async def test_retry_request_no_retry_on_4xx():
    """Test that 4xx errors (except 429) do not trigger retry."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token",
        max_retries=2
    )

    mock_response_404 = MagicMock()
    mock_response_404.status_code = 404

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response_404)
        mock_client_class.return_value = mock_client_instance

        response = await client._retry_request("GET", "https://ai-node.example.com/ping")

        assert response.status_code == 404
        # Should only call once (no retries for 404)
        assert mock_client_instance.request.call_count == 1


@pytest.mark.asyncio
async def test_retry_request_connection_error():
    """Test that connection errors trigger retry and eventually raise exception."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token",
        max_retries=2
    )

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        mock_client_class.return_value = mock_client_instance

        with patch('asyncio.sleep'):
            with pytest.raises(AINodeConnectionError) as exc_info:
                await client._retry_request("GET", "https://ai-node.example.com/ping")

            assert "Connection refused" in str(exc_info.value)
            # Should try 3 times total
            assert mock_client_instance.request.call_count == 3


@pytest.mark.asyncio
async def test_retry_request_timeout():
    """Test that timeout errors trigger retry and eventually raise exception."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token",
        max_retries=1
    )

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(
            side_effect=httpx.TimeoutException("Request timeout")
        )
        mock_client_class.return_value = mock_client_instance

        with patch('asyncio.sleep'):
            with pytest.raises(AINodeConnectionError):
                await client._retry_request("GET", "https://ai-node.example.com/ping")


# ============================================================================
# trigger_ctr_test Tests
# ============================================================================


@pytest.mark.asyncio
async def test_trigger_ctr_test_success():
    """Test successful CTR test trigger."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token"
    )

    payload = CtrTestIn(
        page_url="https://example.com/landing",
        variant_count=3,
        test_duration_hours=24
    )

    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "job_id": "job_123",
        "correlation_id": "corr_456",
        "status": "accepted",
        "message": "CTR test queued",
        "estimated_completion_seconds": 300
    }

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        result = await client.trigger_ctr_test(payload)

        assert isinstance(result, JobAck202)
        assert result.job_id == "job_123"
        assert result.correlation_id == "corr_456"
        assert result.status == "accepted"

        # Verify request was made to correct endpoint
        call_args = mock_client_instance.request.call_args
        assert call_args[0][0] == "POST"
        assert "/api/ctr-test" in call_args[0][1]


@pytest.mark.asyncio
async def test_trigger_ctr_test_non_202_response():
    """Test that non-202 response raises HTTPStatusError."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token"
    )

    payload = CtrTestIn(
        page_url="https://example.com/landing",
        variant_count=3
    )

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "400 Bad Request",
        request=MagicMock(),
        response=mock_response
    )

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        with pytest.raises(httpx.HTTPStatusError):
            await client.trigger_ctr_test(payload)


# ============================================================================
# trigger_content_refresh Tests
# ============================================================================


@pytest.mark.asyncio
async def test_trigger_content_refresh_success():
    """Test successful content refresh trigger."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token"
    )

    payload = ContentRefreshIn(
        content_type="blog_post",
        content_id=42,
        refresh_strategy="incremental"
    )

    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "job_id": "job_789",
        "correlation_id": "corr_012",
        "status": "accepted",
        "message": "Content refresh queued",
        "estimated_completion_seconds": 600
    }

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        result = await client.trigger_content_refresh(payload)

        assert isinstance(result, JobAck202)
        assert result.job_id == "job_789"
        assert result.correlation_id == "corr_012"

        # Verify request was made to correct endpoint
        call_args = mock_client_instance.request.call_args
        assert call_args[0][0] == "POST"
        assert "/api/content-refresh" in call_args[0][1]


# ============================================================================
# execute_change Tests
# ============================================================================


@pytest.mark.asyncio
async def test_execute_change_success():
    """Test successful change execution."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token"
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "change_id": 123,
        "success": True,
        "applied_at": "2025-11-06T12:00:00Z",
        "message": "Change applied successfully",
        "details": {"modified_fields": ["title"]},
        "errors": None
    }

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        result = await client.execute_change(change_id=123)

        assert isinstance(result, ApplyResult)
        assert result.change_id == 123
        assert result.success is True
        assert result.message == "Change applied successfully"

        # Verify request was made to correct endpoint
        call_args = mock_client_instance.request.call_args
        assert call_args[0][0] == "POST"
        assert "/api/changes/123/execute" in call_args[0][1]


@pytest.mark.asyncio
async def test_execute_change_failure():
    """Test change execution failure."""
    client = AINodeClient(
        base_url="https://ai-node.example.com",
        bearer_token="test-token"
    )

    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.text = "Validation error"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "422 Unprocessable Entity",
        request=MagicMock(),
        response=mock_response
    )

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        with pytest.raises(httpx.HTTPStatusError):
            await client.execute_change(change_id=999)


# ============================================================================
# Dependency Injection Tests
# ============================================================================


def test_get_ai_node_client_dependency(db):
    """Test dependency injection helper."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=True,
            created_by=3
        )
        config.set_secret("token-123")
        db.add(config)
        db.commit()

        # Get client via dependency
        client = get_ai_node_client(db)

        assert isinstance(client, AINodeClient)
        assert client.base_url == "https://ai-node.example.com"
        assert client.bearer_token == "token-123"


def test_get_ai_node_client_not_configured(db):
    """Test dependency injection when AI Node is not configured."""
    with pytest.raises(AINodeNotConfiguredError):
        get_ai_node_client(db)
