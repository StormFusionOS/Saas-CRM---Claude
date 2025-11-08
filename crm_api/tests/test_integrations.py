"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Tests for AI Node integration settings.

Covers:
- EncryptionService encrypt/decrypt functionality
- IntegrationSetting model methods
- GET /admin/integrations/ai-node/config
- POST /admin/integrations/ai-node/config
- POST /admin/integrations/ai-node/ping
- RBAC enforcement (OWNER only)
"""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import httpx

from app.main import app
from app.core.encryption import EncryptionService, get_encryption_service
from app.models.integrations import IntegrationSetting
from app.core.security import create_access_token
from cryptography.fernet import Fernet


# Test client
client = TestClient(app)


# ============================================================================
# EncryptionService Tests
# ============================================================================


def test_encryption_service_roundtrip():
    """Test that encrypted data can be decrypted back to original."""
    # Generate a test key
    key = Fernet.generate_key()
    service = EncryptionService(key=key)

    plaintext = "my-secret-bearer-token-12345"
    encrypted = service.encrypt(plaintext)
    decrypted = service.decrypt(encrypted)

    assert decrypted == plaintext
    assert encrypted != plaintext  # Ensure it's actually encrypted


def test_encryption_service_empty_string():
    """Test encryption service with empty string."""
    key = Fernet.generate_key()
    service = EncryptionService(key=key)

    encrypted = service.encrypt("")
    assert encrypted == ""

    decrypted = service.decrypt("")
    assert decrypted == ""


def test_encryption_service_invalid_key():
    """Test that invalid key raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        EncryptionService(key=b"invalid-key")

    assert "Invalid encryption key" in str(exc_info.value)


def test_encryption_service_decrypt_with_wrong_key():
    """Test that decryption with wrong key raises ValueError."""
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()

    service1 = EncryptionService(key=key1)
    service2 = EncryptionService(key=key2)

    plaintext = "secret-data"
    encrypted = service1.encrypt(plaintext)

    # Try to decrypt with wrong key
    with pytest.raises(ValueError) as exc_info:
        service2.decrypt(encrypted)

    assert "Decryption failed" in str(exc_info.value)


def test_encryption_service_from_env():
    """Test that EncryptionService reads from ENCRYPTION_KEY env var."""
    test_key = Fernet.generate_key().decode()

    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        service = EncryptionService()

        plaintext = "test-secret"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext


def test_encryption_service_missing_env_key():
    """Test that missing ENCRYPTION_KEY raises ValueError."""
    with patch.dict(os.environ, {}, clear=True):
        # Clear the global instance to force re-initialization
        import app.core.encryption
        app.core.encryption._encryption_service = None

        with pytest.raises(ValueError) as exc_info:
            EncryptionService()

        assert "ENCRYPTION_KEY environment variable must be set" in str(exc_info.value)


# ============================================================================
# IntegrationSetting Model Tests
# ============================================================================


def test_integration_setting_set_secret(db):
    """Test setting and retrieving encrypted secrets."""
    # Set up encryption key for test
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        # Clear singleton
        import app.core.encryption
        app.core.encryption._encryption_service = None

        setting = IntegrationSetting(
            namespace="test_integration",
            base_url="https://api.example.com",
            review_mode=True
        )
        db.add(setting)

        # Set secret
        secret = "bearer-token-xyz-123"
        setting.set_secret(secret)
        db.commit()

        # Verify encrypted_secret is stored
        assert setting.encrypted_secret is not None
        assert setting.encrypted_secret != secret  # Should be encrypted

        # Retrieve secret
        retrieved = setting.get_secret()
        assert retrieved == secret


def test_integration_setting_has_secret(db):
    """Test has_secret() method."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        setting = IntegrationSetting(namespace="test", base_url="https://test.com")
        db.add(setting)

        # Initially no secret
        assert setting.has_secret() is False

        # Set secret
        setting.set_secret("my-secret")
        db.commit()

        # Now has secret
        assert setting.has_secret() is True


def test_integration_setting_clear_secret(db):
    """Test clearing a secret by setting it to None."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        setting = IntegrationSetting(namespace="test", base_url="https://test.com")
        setting.set_secret("initial-secret")
        db.add(setting)
        db.commit()

        assert setting.has_secret() is True

        # Clear secret
        setting.set_secret(None)
        db.commit()

        assert setting.has_secret() is False
        assert setting.get_secret() is None


def test_integration_setting_get_secret_when_none(db):
    """Test get_secret() returns None when no secret is set."""
    setting = IntegrationSetting(namespace="test", base_url="https://test.com")
    db.add(setting)
    db.commit()

    assert setting.get_secret() is None


# ============================================================================
# API Route Tests - GET /admin/integrations/ai-node/config
# ============================================================================


def test_get_ai_node_config_no_config(db):
    """Test GET /config when no configuration exists."""
    # Create OWNER token
    token = create_access_token(
        data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/integrations/ai-node/config", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["base_url"] == ""
    assert data["bearer_token_set"] is False
    assert data["review_mode"] is True
    assert data["last_updated"] is None
    assert data["last_ping_status"] is None


def test_get_ai_node_config_with_config(db):
    """Test GET /config when configuration exists."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=False,
            created_by=3
        )
        config.set_secret("bearer-token-123")
        db.add(config)
        db.commit()

        # Create OWNER token
        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/admin/integrations/ai-node/config", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["base_url"] == "https://ai-node.example.com"
        assert data["bearer_token_set"] is True  # Secret masked
        assert data["review_mode"] is False
        assert data["last_updated"] is not None

        # Ensure actual token is NEVER returned
        assert "bearer-token-123" not in str(response.content)


def test_get_ai_node_config_requires_owner(db):
    """Test GET /config requires OWNER role."""
    # Create SALES token (not OWNER)
    token = create_access_token(
        data={"sub": "sales@rivercityclean.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/integrations/ai-node/config", headers=headers)

    assert response.status_code == 403  # Forbidden


def test_get_ai_node_config_no_auth(db):
    """Test GET /config without authentication."""
    response = client.get("/api/v1/admin/integrations/ai-node/config")

    assert response.status_code == 422  # Missing auth header


# ============================================================================
# API Route Tests - POST /admin/integrations/ai-node/config
# ============================================================================


def test_post_ai_node_config_create(db):
    """Test POST /config creates new configuration."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/admin/integrations/ai-node/config",
            headers=headers,
            json={
                "base_url": "https://ai-node.example.com",
                "bearer_token": "sk_test_abc123",
                "review_mode": True
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["base_url"] == "https://ai-node.example.com"
        assert data["bearer_token_set"] is True  # Secret masked
        assert data["review_mode"] is True

        # Verify config was created in database
        config = db.query(IntegrationSetting).filter(
            IntegrationSetting.namespace == "ai_node"
        ).first()

        assert config is not None
        assert config.base_url == "https://ai-node.example.com"
        assert config.has_secret() is True
        assert config.get_secret() == "sk_test_abc123"


def test_post_ai_node_config_update(db):
    """Test POST /config updates existing configuration."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create initial config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://old-url.com",
            review_mode=True,
            created_by=3
        )
        config.set_secret("old-token")
        db.add(config)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Update config
        response = client.post(
            "/api/v1/admin/integrations/ai-node/config",
            headers=headers,
            json={
                "base_url": "https://new-url.com",
                "bearer_token": "new-token-456",
                "review_mode": False
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["base_url"] == "https://new-url.com"
        assert data["review_mode"] is False

        # Verify database was updated
        db.refresh(config)
        assert config.base_url == "https://new-url.com"
        assert config.review_mode is False
        assert config.get_secret() == "new-token-456"


def test_post_ai_node_config_update_without_token(db):
    """Test POST /config updates config without changing token."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create initial config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://old-url.com",
            review_mode=True,
            created_by=3
        )
        config.set_secret("existing-token")
        db.add(config)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Update config without providing bearer_token
        response = client.post(
            "/api/v1/admin/integrations/ai-node/config",
            headers=headers,
            json={
                "base_url": "https://updated-url.com",
                "review_mode": False
            }
        )

        assert response.status_code == 200

        # Verify token was NOT changed
        db.refresh(config)
        assert config.get_secret() == "existing-token"
        assert config.base_url == "https://updated-url.com"


def test_post_ai_node_config_invalid_bearer_token(db):
    """Test POST /config validates bearer token length."""
    token = create_access_token(
        data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Too short
    response = client.post(
        "/api/v1/admin/integrations/ai-node/config",
        headers=headers,
        json={
            "base_url": "https://ai-node.example.com",
            "bearer_token": "short",  # Less than 10 chars
            "review_mode": True
        }
    )

    assert response.status_code == 422  # Validation error


def test_post_ai_node_config_invalid_url(db):
    """Test POST /config validates URL format."""
    token = create_access_token(
        data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/admin/integrations/ai-node/config",
        headers=headers,
        json={
            "base_url": "not-a-valid-url",
            "bearer_token": "sk_test_abc123",
            "review_mode": True
        }
    )

    assert response.status_code == 422  # Validation error


def test_post_ai_node_config_requires_owner(db):
    """Test POST /config requires OWNER role."""
    token = create_access_token(
        data={"sub": "sales@rivercityclean.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/admin/integrations/ai-node/config",
        headers=headers,
        json={
            "base_url": "https://ai-node.example.com",
            "bearer_token": "sk_test_abc123",
            "review_mode": True
        }
    )

    assert response.status_code == 403  # Forbidden


# ============================================================================
# API Route Tests - POST /admin/integrations/ai-node/ping
# ============================================================================


@pytest.mark.asyncio
async def test_post_ai_node_ping_success(db):
    """Test POST /ping with successful connection."""
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
        config.set_secret("bearer-token-123")
        db.add(config)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason_phrase = "OK"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            response = client.post("/api/v1/admin/integrations/ai-node/ping", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["status_code"] == 200
            assert data["latency_ms"] is not None
            assert data["error_message"] is None

            # Verify database was updated with ping results
            db.refresh(config)
            assert config.last_ping_status == "success"
            assert config.last_ping_latency_ms is not None


@pytest.mark.asyncio
async def test_post_ai_node_ping_timeout(db):
    """Test POST /ping with timeout."""
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
        db.add(config)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock httpx client to raise TimeoutException
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.return_value = mock_client_instance

            response = client.post("/api/v1/admin/integrations/ai-node/ping", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert data["status_code"] is None
            assert "timed out" in data["error_message"].lower()

            # Verify database was updated
            db.refresh(config)
            assert config.last_ping_status == "failed"


@pytest.mark.asyncio
async def test_post_ai_node_ping_connection_error(db):
    """Test POST /ping with connection error."""
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
        db.add(config)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock httpx client to raise ConnectError
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.return_value = mock_client_instance

            response = client.post("/api/v1/admin/integrations/ai-node/ping", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert "Connection failed" in data["error_message"]


def test_post_ai_node_ping_no_config(db):
    """Test POST /ping when no configuration exists."""
    token = create_access_token(
        data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/admin/integrations/ai-node/ping", headers=headers)

    assert response.status_code == 400
    assert "not configured" in response.json()["detail"].lower()


def test_post_ai_node_ping_requires_owner(db):
    """Test POST /ping requires OWNER role."""
    token = create_access_token(
        data={"sub": "sales@rivercityclean.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/admin/integrations/ai-node/ping", headers=headers)

    assert response.status_code == 403  # Forbidden


# ============================================================================
# API Route Tests - GET /admin/integrations/ai-node/health
# ============================================================================


@pytest.mark.asyncio
async def test_get_health_all_healthy(db):
    """Test health check when all systems are healthy."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create AI Node config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=True,
            created_by=3
        )
        config.set_secret("token-123")
        db.add(config)

        # Add some task logs (import TaskLogModel from db_models)
        from app.db_models import TaskLogModel
        from datetime import datetime, timedelta

        # Recent successful task
        task1 = TaskLogModel(
            job_name="test_job",
            job_id="job_123",
            status="completed",
            started_at=datetime.utcnow() - timedelta(hours=1),
            completed_at=datetime.utcnow(),
            duration_seconds=60.0
        )
        db.add(task1)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock AI Node ping
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client_instance

            response = client.get("/api/v1/admin/integrations/ai-node/health", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["overall_status"] == "healthy"
            assert data["database"]["status"] == "healthy"
            assert data["task_logs"]["status"] == "healthy"
            assert data["ai_node"]["status"] == "healthy"

            assert data["summary"]["healthy_checks"] == 3
            assert data["summary"]["unhealthy_checks"] == 0


@pytest.mark.asyncio
async def test_get_health_degraded_task_logs(db):
    """Test health check when task logs show degraded status."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create AI Node config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=True,
            created_by=3
        )
        db.add(config)

        # Add old task log (>24 hours)
        from app.db_models import TaskLogModel
        from datetime import datetime, timedelta

        old_task = TaskLogModel(
            job_name="old_job",
            job_id="job_old",
            status="completed",
            started_at=datetime.utcnow() - timedelta(hours=48),  # 48 hours ago
            completed_at=datetime.utcnow() - timedelta(hours=47),
            duration_seconds=60.0
        )
        db.add(old_task)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock AI Node ping
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client_instance

            response = client.get("/api/v1/admin/integrations/ai-node/health", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["overall_status"] == "degraded"  # Due to old task logs
            assert data["task_logs"]["status"] == "degraded"
            assert "No recent task activity" in data["task_logs"]["message"]


@pytest.mark.asyncio
async def test_get_health_high_error_rate(db):
    """Test health check when task logs have high error rate."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create AI Node config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=True,
            created_by=3
        )
        db.add(config)

        # Add task logs with high error rate
        from app.db_models import TaskLogModel
        from datetime import datetime, timedelta

        # 3 failed, 1 successful (75% error rate)
        for i in range(3):
            failed_task = TaskLogModel(
                job_name=f"job_{i}",
                job_id=f"failed_{i}",
                status="failed",
                started_at=datetime.utcnow() - timedelta(hours=1),
                completed_at=datetime.utcnow(),
                duration_seconds=10.0,
                error_message="Test error"
            )
            db.add(failed_task)

        success_task = TaskLogModel(
            job_name="success_job",
            job_id="success_1",
            status="completed",
            started_at=datetime.utcnow() - timedelta(minutes=30),
            completed_at=datetime.utcnow(),
            duration_seconds=60.0
        )
        db.add(success_task)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock AI Node ping
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client_instance

            response = client.get("/api/v1/admin/integrations/ai-node/health", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["overall_status"] == "degraded"
            assert data["task_logs"]["status"] == "degraded"
            assert "High error rate" in data["task_logs"]["message"]
            assert data["task_logs"]["details"]["error_count_24h"] == 3


@pytest.mark.asyncio
async def test_get_health_ai_node_not_configured(db):
    """Test health check when AI Node is not configured."""
    token = create_access_token(
        data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/integrations/ai-node/health", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["overall_status"] == "unhealthy"
    assert data["ai_node"]["status"] == "unhealthy"
    assert "not configured" in data["ai_node"]["message"].lower()


@pytest.mark.asyncio
async def test_get_health_ai_node_timeout(db):
    """Test health check when AI Node ping times out."""
    test_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key}):
        import app.core.encryption
        app.core.encryption._encryption_service = None

        # Create AI Node config
        config = IntegrationSetting(
            namespace="ai_node",
            base_url="https://ai-node.example.com",
            review_mode=True,
            created_by=3
        )
        db.add(config)
        db.commit()

        token = create_access_token(
            data={"sub": "owner@rivercityclean.com", "user_id": 3, "roles": ["OWNER"]},
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Mock AI Node timeout
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.head = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client_class.return_value = mock_client_instance

            response = client.get("/api/v1/admin/integrations/ai-node/health", headers=headers)

            assert response.status_code == 200
            data = response.json()

            assert data["overall_status"] == "unhealthy"
            assert data["ai_node"]["status"] == "unhealthy"
            assert "timed out" in data["ai_node"]["message"].lower()


def test_get_health_requires_owner(db):
    """Test that health endpoint requires OWNER role."""
    token = create_access_token(
        data={"sub": "sales@rivercityclean.com", "user_id": 1, "roles": ["SALES"]},
        expires_delta=timedelta(hours=1)
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/integrations/ai-node/health", headers=headers)

    assert response.status_code == 403  # Forbidden
