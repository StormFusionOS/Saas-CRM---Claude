"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Scrape Bot Connector Service

Connects to the remote Scrape Bot service (Server A) to submit jobs,
poll status, and fetch results for SERP tracking, competitor scraping,
backlinks, and citations.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import httpx
import structlog
from datetime import datetime, timedelta
import time

logger = structlog.get_logger(__name__)


class JobType(str, Enum):
    """Supported job types for Scrape Bot."""
    SERP = "serp"
    CRAWL = "crawl"
    BACKLINKS = "backlinks"
    CITATIONS = "citations"


class JobStatus(str, Enum):
    """Job execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ErrorKind(str, Enum):
    """Error classification for retry logic."""
    TRANSIENT = "TRANSIENT"  # Retry with backoff
    FATAL = "FATAL"  # Don't retry
    AUTH = "AUTH"  # Authentication failed
    TIMEOUT = "TIMEOUT"  # Request timeout


class ScrapeConnectorError(Exception):
    """Base exception for Scrape Connector errors."""

    def __init__(self, message: str, kind: ErrorKind, details: Optional[Dict] = None):
        super().__init__(message)
        self.kind = kind
        self.details = details or {}


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing)
    """

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        """Record successful request."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_attempt(self) -> bool:
        """Check if request can be attempted."""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if timeout has elapsed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = "HALF_OPEN"
                    return True
            return False

        # HALF_OPEN - allow one attempt
        return True


class ScrapeConnector:
    """
    Service for communicating with remote Scrape Bot.

    Provides resilient job submission, polling, and result retrieval
    with retries, circuit breaking, and optional mTLS.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        verify_tls: bool = True,
        mtls_cert_path: Optional[str] = None,
        mtls_key_path: Optional[str] = None,
        ca_bundle_path: Optional[str] = None,
        max_retries: int = 3,
        retry_backoff: float = 1.5
    ):
        """
        Initialize Scrape Bot connector.

        Args:
            base_url: Base URL of Scrape Bot API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            verify_tls: Whether to verify TLS certificates
            mtls_cert_path: Path to client certificate for mTLS
            mtls_key_path: Path to client private key for mTLS
            ca_bundle_path: Path to CA bundle for certificate verification
            max_retries: Maximum retry attempts for transient errors
            retry_backoff: Exponential backoff multiplier
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.circuit_breaker = CircuitBreaker()
        self.logger = logger.bind(service="scrape_connector")

        # Build client config
        client_config = {
            "timeout": timeout,
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        }

        # TLS verification
        if not verify_tls:
            client_config["verify"] = False
        elif ca_bundle_path:
            client_config["verify"] = ca_bundle_path

        # mTLS configuration
        if mtls_cert_path and mtls_key_path:
            client_config["cert"] = (mtls_cert_path, mtls_key_path)

        self.client = httpx.Client(**client_config)

    def __del__(self):
        """Cleanup HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()

    # ==========================================================================
    # Job Submission
    # ==========================================================================

    def submit_job(self, job_type: JobType, payload: Dict[str, Any]) -> str:
        """
        Submit a new job to Scrape Bot.

        Args:
            job_type: Type of job (SERP, CRAWL, BACKLINKS, CITATIONS)
            payload: Job-specific parameters

        Returns:
            Job ID

        Raises:
            ScrapeConnectorError: On failure
        """
        if not self.circuit_breaker.can_attempt():
            raise ScrapeConnectorError(
                "Circuit breaker is OPEN - too many recent failures",
                kind=ErrorKind.TRANSIENT,
                details={"state": self.circuit_breaker.state}
            )

        body = {
            "job_type": job_type.value,
            "payload": payload
        }

        try:
            response = self._request_with_retry(
                method="POST",
                endpoint="/jobs",
                json_data=body
            )

            job_id = response.get("job_id")
            if not job_id:
                raise ScrapeConnectorError(
                    "Invalid response: missing job_id",
                    kind=ErrorKind.FATAL,
                    details={"response": response}
                )

            self.circuit_breaker.record_success()
            self.logger.info("job_submitted", job_id=job_id, job_type=job_type.value)
            return job_id

        except ScrapeConnectorError:
            self.circuit_breaker.record_failure()
            raise
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise ScrapeConnectorError(
                f"Job submission failed: {str(e)}",
                kind=ErrorKind.TRANSIENT,
                details={"error": str(e)}
            )

    # ==========================================================================
    # Status Polling
    # ==========================================================================

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current status of a job.

        Args:
            job_id: Job ID

        Returns:
            Status dict with keys: status, progress, message, run_id

        Raises:
            ScrapeConnectorError: On failure
        """
        try:
            response = self._request_with_retry(
                method="GET",
                endpoint=f"/jobs/{job_id}"
            )

            self.circuit_breaker.record_success()
            return response

        except ScrapeConnectorError:
            self.circuit_breaker.record_failure()
            raise
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise ScrapeConnectorError(
                f"Status check failed: {str(e)}",
                kind=ErrorKind.TRANSIENT,
                details={"job_id": job_id, "error": str(e)}
            )

    def poll_until_complete(
        self,
        job_id: str,
        poll_interval: int = 5,
        max_wait: int = 300
    ) -> Dict[str, Any]:
        """
        Poll job status until completion or timeout.

        Args:
            job_id: Job ID
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait

        Returns:
            Final status dict

        Raises:
            ScrapeConnectorError: On timeout or failure
        """
        start_time = time.time()
        last_status = None

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                raise ScrapeConnectorError(
                    f"Job polling timeout after {max_wait}s",
                    kind=ErrorKind.TIMEOUT,
                    details={"job_id": job_id, "last_status": last_status}
                )

            status_data = self.get_job_status(job_id)
            status = status_data.get("status")
            last_status = status

            if status == JobStatus.SUCCEEDED.value:
                self.logger.info("job_completed", job_id=job_id)
                return status_data

            if status == JobStatus.FAILED.value:
                raise ScrapeConnectorError(
                    f"Job failed: {status_data.get('message', 'Unknown error')}",
                    kind=ErrorKind.FATAL,
                    details={"job_id": job_id, "status_data": status_data}
                )

            # Still running or queued
            self.logger.debug(
                "job_polling",
                job_id=job_id,
                status=status,
                progress=status_data.get("progress", 0)
            )

            time.sleep(poll_interval)

    # ==========================================================================
    # Results Fetching
    # ==========================================================================

    def fetch_results(
        self,
        run_id: str,
        result_type: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch structured results for a completed run.

        Args:
            run_id: Run ID from completed job
            result_type: Type of results (serp, pages, backlinks, citations)

        Returns:
            List of result records

        Raises:
            ScrapeConnectorError: On failure
        """
        try:
            response = self._request_with_retry(
                method="GET",
                endpoint=f"/runs/{run_id}/results",
                params={"type": result_type}
            )

            if not isinstance(response, list):
                raise ScrapeConnectorError(
                    "Invalid results format - expected list",
                    kind=ErrorKind.FATAL,
                    details={"response": response}
                )

            self.circuit_breaker.record_success()
            self.logger.info(
                "results_fetched",
                run_id=run_id,
                result_type=result_type,
                count=len(response)
            )
            return response

        except ScrapeConnectorError:
            self.circuit_breaker.record_failure()
            raise
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise ScrapeConnectorError(
                f"Results fetch failed: {str(e)}",
                kind=ErrorKind.TRANSIENT,
                details={"run_id": run_id, "error": str(e)}
            )

    def fetch_artifact(
        self,
        run_id: str,
        page_id: str,
        artifact_type: str = "html"
    ) -> bytes:
        """
        Fetch binary artifact (e.g., HTML snapshot).

        Args:
            run_id: Run ID
            page_id: Page identifier
            artifact_type: Type of artifact (default: html)

        Returns:
            Raw artifact bytes

        Raises:
            ScrapeConnectorError: On failure
        """
        endpoint = f"/artifacts/{run_id}/{page_id}.{artifact_type}"

        try:
            response = self.client.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()

            self.circuit_breaker.record_success()
            self.logger.info(
                "artifact_fetched",
                run_id=run_id,
                page_id=page_id,
                size=len(response.content)
            )
            return response.content

        except httpx.HTTPStatusError as e:
            self.circuit_breaker.record_failure()
            if e.response.status_code == 401:
                raise ScrapeConnectorError(
                    "Authentication failed",
                    kind=ErrorKind.AUTH,
                    details={"status": 401}
                )
            elif e.response.status_code == 404:
                raise ScrapeConnectorError(
                    f"Artifact not found: {endpoint}",
                    kind=ErrorKind.FATAL,
                    details={"status": 404, "endpoint": endpoint}
                )
            raise ScrapeConnectorError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                kind=ErrorKind.TRANSIENT,
                details={"status": e.response.status_code}
            )
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise ScrapeConnectorError(
                f"Artifact fetch failed: {str(e)}",
                kind=ErrorKind.TRANSIENT,
                details={"error": str(e)}
            )

    # ==========================================================================
    # Internal Helpers
    # ==========================================================================

    def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json_data: JSON request body
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            ScrapeConnectorError: On failure after retries
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.client.get(url, params=params)
                elif method == "POST":
                    response = self.client.post(url, json=json_data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_backoff ** attempt
                    self.logger.warning(
                        "request_timeout_retry",
                        attempt=attempt + 1,
                        wait_seconds=wait_time
                    )
                    time.sleep(wait_time)
                    continue
                raise ScrapeConnectorError(
                    "Request timeout",
                    kind=ErrorKind.TIMEOUT,
                    details={"url": url, "timeout": self.timeout}
                )

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                # Authentication errors - don't retry
                if status == 401:
                    raise ScrapeConnectorError(
                        "Authentication failed - invalid API key",
                        kind=ErrorKind.AUTH,
                        details={"status": 401}
                    )

                # Server errors - retry
                if 500 <= status < 600:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_backoff ** attempt
                        self.logger.warning(
                            "server_error_retry",
                            status=status,
                            attempt=attempt + 1,
                            wait_seconds=wait_time
                        )
                        time.sleep(wait_time)
                        continue
                    raise ScrapeConnectorError(
                        f"Server error after {self.max_retries} retries",
                        kind=ErrorKind.TRANSIENT,
                        details={"status": status}
                    )

                # Client errors (4xx except 401) - don't retry
                raise ScrapeConnectorError(
                    f"HTTP {status}: {e.response.text}",
                    kind=ErrorKind.FATAL,
                    details={"status": status, "response": e.response.text}
                )

            except httpx.RequestError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_backoff ** attempt
                    self.logger.warning(
                        "request_error_retry",
                        error=str(e),
                        attempt=attempt + 1,
                        wait_seconds=wait_time
                    )
                    time.sleep(wait_time)
                    continue
                raise ScrapeConnectorError(
                    f"Request failed: {str(e)}",
                    kind=ErrorKind.TRANSIENT,
                    details={"error": str(e)}
                )

        # Should not reach here, but just in case
        raise ScrapeConnectorError(
            f"Request failed after {self.max_retries} retries",
            kind=ErrorKind.TRANSIENT,
            details={"last_error": str(last_error)}
        )

    def health_check(self) -> bool:
        """
        Check if Scrape Bot is reachable.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Simple health check - just try to connect
            response = self.client.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
