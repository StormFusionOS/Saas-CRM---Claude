"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

AI Node Client Service

HTTP client for interacting with external AI Node service.
Handles authentication, retries, and async job orchestration.
"""

import httpx
import asyncio
import structlog
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.models.integrations import IntegrationSetting
from app.schemas.integrations import (
    CtrTestIn,
    ContentRefreshIn,
    JobAck202,
    ApplyResult
)


logger = structlog.get_logger(__name__)

AI_NODE_NAMESPACE = "ai_node"


class AINodeNotConfiguredError(Exception):
    """Raised when AI Node integration is not configured"""
    pass


class AINodeConnectionError(Exception):
    """Raised when AI Node connection fails"""
    pass


class AINodeClient:
    """
    HTTP client for AI Node service integration.

    Handles:
    - Bearer token authentication
    - Exponential backoff retries on 429/5xx errors
    - 202 Accepted async job tracking
    - Connection pooling via httpx.AsyncClient
    """

    def __init__(
        self,
        base_url: str,
        bearer_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize AI Node client.

        Args:
            base_url: Base URL of AI Node service (e.g., https://ai-node.example.com)
            bearer_token: Bearer token for authentication (optional)
            timeout: Request timeout in seconds (default 30)
            max_retries: Maximum number of retries for 429/5xx errors (default 3)
        """
        self.base_url = base_url.rstrip('/')
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.max_retries = max_retries

        logger.info(
            "ai_node_client_initialized",
            base_url=self.base_url,
            has_token=self.bearer_token is not None,
            timeout=timeout,
            max_retries=max_retries
        )

    @classmethod
    def from_db(cls, db: Session) -> "AINodeClient":
        """
        Create AI Node client from database settings.

        Args:
            db: Database session

        Returns:
            Configured AINodeClient instance

        Raises:
            AINodeNotConfiguredError: If AI Node is not configured in database
        """
        config = db.query(IntegrationSetting).filter(
            IntegrationSetting.namespace == AI_NODE_NAMESPACE
        ).first()

        if not config or not config.base_url:
            logger.error("ai_node_not_configured")
            raise AINodeNotConfiguredError(
                "AI Node integration is not configured. "
                "Please configure it via /admin/integrations/ai-node/config"
            )

        # Get decrypted bearer token
        bearer_token = None
        if config.has_secret():
            try:
                bearer_token = config.get_secret()
            except ValueError as e:
                logger.error("ai_node_token_decryption_failed", error=str(e))
                raise AINodeNotConfiguredError(
                    f"Failed to decrypt AI Node bearer token: {e}"
                )

        return cls(
            base_url=config.base_url,
            bearer_token=bearer_token
        )

    def _get_headers(self) -> dict:
        """
        Get HTTP headers including Authorization.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "RiverCityClean-CRM/1.0"
        }

        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        return headers

    async def _retry_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Execute HTTP request with exponential backoff retry logic.

        Retries on:
        - 429 Too Many Requests
        - 5xx Server Errors
        - Connection errors

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments for httpx.request()

        Returns:
            httpx.Response object

        Raises:
            AINodeConnectionError: If all retries are exhausted
        """
        attempt = 0
        last_exception = None

        while attempt <= self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)

                    # Success cases (2xx, 3xx, 4xx except 429)
                    if response.status_code < 500 and response.status_code != 429:
                        logger.info(
                            "ai_node_request_success",
                            method=method,
                            url=url,
                            status_code=response.status_code,
                            attempt=attempt + 1
                        )
                        return response

                    # Retry cases (429, 5xx)
                    logger.warning(
                        "ai_node_request_retry",
                        method=method,
                        url=url,
                        status_code=response.status_code,
                        attempt=attempt + 1,
                        max_retries=self.max_retries
                    )

                    # Don't retry if we've reached max retries
                    if attempt >= self.max_retries:
                        return response

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                logger.warning(
                    "ai_node_connection_error",
                    method=method,
                    url=url,
                    error=str(e),
                    attempt=attempt + 1
                )

                # Don't retry if we've reached max retries
                if attempt >= self.max_retries:
                    raise AINodeConnectionError(
                        f"Failed to connect to AI Node after {self.max_retries + 1} attempts: {e}"
                    )

            # Exponential backoff: 1s, 2s, 4s, 8s...
            backoff_seconds = 2 ** attempt
            logger.info("ai_node_retry_backoff", seconds=backoff_seconds)
            await asyncio.sleep(backoff_seconds)

            attempt += 1

        # Should never reach here, but just in case
        if last_exception:
            raise AINodeConnectionError(f"Request failed: {last_exception}")

        raise AINodeConnectionError("Request failed after all retries")

    async def trigger_ctr_test(self, payload: CtrTestIn) -> JobAck202:
        """
        Trigger CTR (Click-Through Rate) test on AI Node.

        Args:
            payload: CTR test configuration

        Returns:
            JobAck202 with job tracking information

        Raises:
            AINodeConnectionError: If request fails
            httpx.HTTPStatusError: If AI Node returns 4xx error
        """
        url = f"{self.base_url}/api/ctr-test"

        logger.info(
            "ai_node_trigger_ctr_test",
            page_url=payload.page_url,
            variant_count=payload.variant_count
        )

        response = await self._retry_request(
            method="POST",
            url=url,
            headers=self._get_headers(),
            json=payload.dict()
        )

        # Handle non-202 responses
        if response.status_code != 202:
            logger.error(
                "ai_node_ctr_test_failed",
                status_code=response.status_code,
                response_body=response.text
            )
            response.raise_for_status()

        # Parse 202 Accepted response
        data = response.json()
        result = JobAck202(**data)

        logger.info(
            "ai_node_ctr_test_accepted",
            job_id=result.job_id,
            correlation_id=result.correlation_id
        )

        return result

    async def trigger_content_refresh(self, payload: ContentRefreshIn) -> JobAck202:
        """
        Trigger content refresh on AI Node.

        Args:
            payload: Content refresh configuration

        Returns:
            JobAck202 with job tracking information

        Raises:
            AINodeConnectionError: If request fails
            httpx.HTTPStatusError: If AI Node returns 4xx error
        """
        url = f"{self.base_url}/api/content-refresh"

        logger.info(
            "ai_node_trigger_content_refresh",
            content_type=payload.content_type,
            content_id=payload.content_id,
            strategy=payload.refresh_strategy
        )

        response = await self._retry_request(
            method="POST",
            url=url,
            headers=self._get_headers(),
            json=payload.dict()
        )

        # Handle non-202 responses
        if response.status_code != 202:
            logger.error(
                "ai_node_content_refresh_failed",
                status_code=response.status_code,
                response_body=response.text
            )
            response.raise_for_status()

        # Parse 202 Accepted response
        data = response.json()
        result = JobAck202(**data)

        logger.info(
            "ai_node_content_refresh_accepted",
            job_id=result.job_id,
            correlation_id=result.correlation_id
        )

        return result

    async def execute_change(self, change_id: int) -> ApplyResult:
        """
        Execute a change via AI Node.

        This is a synchronous operation (not 202 Accepted).

        Args:
            change_id: ID of the change to execute

        Returns:
            ApplyResult with execution status

        Raises:
            AINodeConnectionError: If request fails
            httpx.HTTPStatusError: If AI Node returns error
        """
        url = f"{self.base_url}/api/changes/{change_id}/execute"

        logger.info("ai_node_execute_change", change_id=change_id)

        response = await self._retry_request(
            method="POST",
            url=url,
            headers=self._get_headers()
        )

        # Handle errors
        if response.status_code >= 400:
            logger.error(
                "ai_node_execute_change_failed",
                change_id=change_id,
                status_code=response.status_code,
                response_body=response.text
            )
            response.raise_for_status()

        # Parse success response (200 OK)
        data = response.json()
        result = ApplyResult(**data)

        logger.info(
            "ai_node_execute_change_completed",
            change_id=change_id,
            success=result.success
        )

        return result


# ============================================================================
# Dependency Injection Helper
# ============================================================================


def get_ai_node_client(db: Session = Depends(get_db)) -> AINodeClient:
    """
    FastAPI dependency for injecting AI Node client.

    Usage in routes:
        @router.post("/some-endpoint")
        async def my_endpoint(
            ai_client: AINodeClient = Depends(get_ai_node_client)
        ):
            result = await ai_client.trigger_ctr_test(payload)
            ...

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        Configured AINodeClient instance

    Raises:
        AINodeNotConfiguredError: If AI Node is not configured
    """
    return AINodeClient.from_db(db)
