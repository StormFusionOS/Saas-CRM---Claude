#!/usr/bin/env python3
"""
Performance Load Harness

Async load testing for critical API endpoints with configurable concurrency.

Endpoints tested:
- POST /api/v1/auth/login - User authentication
- GET /api/v1/leads - List leads
- POST /api/v1/tasks/enqueue - Background task enqueue

Usage:
    # 2-minute run with 10 concurrent users
    python tools/perf/harness.py --duration 120 --concurrency 10

    # Custom endpoints and higher load
    python tools/perf/harness.py --duration 60 --concurrency 50 --endpoints login,leads

    # Save results to custom path
    python tools/perf/harness.py --duration 30 --output artifacts/perf/custom_test.json
"""

import asyncio
import aiohttp
import time
import json
import statistics
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EndpointResult:
    """Results for a single endpoint"""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    duration_seconds: float
    requests_per_second: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_mean: float
    latency_min: float
    latency_max: float


@dataclass
class LoadTestReport:
    """Complete load test report"""
    test_name: str
    started_at: str
    completed_at: str
    duration_seconds: float
    concurrency: int
    total_requests: int
    total_errors: int
    overall_rps: float
    endpoints: List[EndpointResult]


class LoadHarness:
    """
    Async load testing harness

    Generates configurable load against API endpoints and measures performance.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        concurrency: int = 10,
        duration_seconds: int = 120,
        timeout_seconds: int = 30
    ):
        """
        Initialize load harness

        Args:
            base_url: Base URL of API
            concurrency: Number of concurrent workers
            duration_seconds: Test duration
            timeout_seconds: Request timeout
        """
        self.base_url = base_url
        self.concurrency = concurrency
        self.duration = duration_seconds
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

        # Endpoints to test
        self.endpoints = {
            "login": {
                "method": "POST",
                "path": "/api/v1/auth/login",
                "payload": {"email": "test@example.com", "password": "password123"}
            },
            "leads": {
                "method": "GET",
                "path": "/api/v1/leads",
                "params": {"limit": 20, "offset": 0}
            },
            "enqueue": {
                "method": "POST",
                "path": "/api/v1/tasks/enqueue",
                "payload": {"task_type": "email", "priority": "normal"}
            }
        }

    async def run_test(
        self,
        endpoint_names: Optional[List[str]] = None
    ) -> LoadTestReport:
        """
        Run load test

        Args:
            endpoint_names: List of endpoint names to test (None = all)

        Returns:
            Load test report
        """
        if endpoint_names is None:
            endpoint_names = list(self.endpoints.keys())

        print(f"=== Load Test ===")
        print(f"Base URL: {self.base_url}")
        print(f"Duration: {self.duration}s")
        print(f"Concurrency: {self.concurrency}")
        print(f"Endpoints: {', '.join(endpoint_names)}\n")

        started_at = datetime.now(timezone.utc)
        start_time = time.time()

        # Run tests for all endpoints
        endpoint_results = []
        total_requests = 0
        total_errors = 0

        for endpoint_name in endpoint_names:
            print(f"Testing {endpoint_name}...")
            result = await self._test_endpoint(endpoint_name)
            endpoint_results.append(result)
            total_requests += result.total_requests
            total_errors += result.failed_requests

            print(f"  ✓ {result.total_requests} requests "
                  f"({result.requests_per_second:.1f} req/s, "
                  f"p95: {result.latency_p95:.0f}ms)\n")

        # Calculate overall metrics
        duration = time.time() - start_time
        overall_rps = total_requests / duration if duration > 0 else 0

        report = LoadTestReport(
            test_name="Load Test",
            started_at=started_at.isoformat(),
            completed_at=datetime.now(timezone.utc).isoformat(),
            duration_seconds=duration,
            concurrency=self.concurrency,
            total_requests=total_requests,
            total_errors=total_errors,
            overall_rps=overall_rps,
            endpoints=endpoint_results
        )

        return report

    async def _test_endpoint(self, endpoint_name: str) -> EndpointResult:
        """Test a single endpoint"""
        endpoint_config = self.endpoints[endpoint_name]
        latencies = []
        errors = 0

        start_time = time.time()
        stop_time = start_time + self.duration

        # Create worker tasks
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            workers = [
                self._worker(
                    session,
                    endpoint_name,
                    endpoint_config,
                    stop_time,
                    latencies
                )
                for _ in range(self.concurrency)
            ]

            # Run workers concurrently
            results = await asyncio.gather(*workers, return_exceptions=True)

            # Count errors
            for result in results:
                if isinstance(result, Exception):
                    errors += 1

        # Calculate metrics
        duration = time.time() - start_time
        total_requests = len(latencies)
        successful_requests = total_requests - errors

        if latencies:
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)

            result = EndpointResult(
                endpoint=endpoint_name,
                method=endpoint_config["method"],
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=errors,
                error_rate=(errors / total_requests * 100) if total_requests > 0 else 0,
                duration_seconds=duration,
                requests_per_second=total_requests / duration if duration > 0 else 0,
                latency_p50=sorted_latencies[int(n * 0.50)],
                latency_p95=sorted_latencies[int(n * 0.95)] if n > 20 else sorted_latencies[-1],
                latency_p99=sorted_latencies[int(n * 0.99)] if n > 100 else sorted_latencies[-1],
                latency_mean=statistics.mean(latencies),
                latency_min=min(latencies),
                latency_max=max(latencies)
            )
        else:
            # No successful requests
            result = EndpointResult(
                endpoint=endpoint_name,
                method=endpoint_config["method"],
                total_requests=0,
                successful_requests=0,
                failed_requests=errors,
                error_rate=100.0,
                duration_seconds=duration,
                requests_per_second=0,
                latency_p50=0,
                latency_p95=0,
                latency_p99=0,
                latency_mean=0,
                latency_min=0,
                latency_max=0
            )

        return result

    async def _worker(
        self,
        session: aiohttp.ClientSession,
        endpoint_name: str,
        endpoint_config: Dict,
        stop_time: float,
        latencies: List[float]
    ):
        """Worker that makes requests until stop_time"""
        url = f"{self.base_url}{endpoint_config['path']}"
        method = endpoint_config["method"]

        while time.time() < stop_time:
            start = time.perf_counter()

            try:
                # Make request based on method
                if method == "GET":
                    async with session.get(
                        url,
                        params=endpoint_config.get("params")
                    ) as response:
                        await response.text()
                        success = response.status < 400

                elif method == "POST":
                    async with session.post(
                        url,
                        json=endpoint_config.get("payload")
                    ) as response:
                        await response.text()
                        success = response.status < 400

                else:
                    success = False

                # Record latency only for successful requests
                if success:
                    latency_ms = (time.perf_counter() - start) * 1000
                    latencies.append(latency_ms)

            except asyncio.TimeoutError:
                # Timeout counts as error, don't record latency
                pass

            except Exception as e:
                # Other errors
                pass

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)

    def save_report(self, report: LoadTestReport, output_path: str):
        """Save report to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        report_dict = asdict(report)

        # Save JSON
        output_file.write_text(json.dumps(report_dict, indent=2))

        print(f"\n✓ Report saved to: {output_file}")

    def print_report(self, report: LoadTestReport):
        """Print formatted report"""
        print("\n" + "=" * 80)
        print("LOAD TEST REPORT")
        print("=" * 80)
        print(f"Duration: {report.duration_seconds:.1f}s")
        print(f"Concurrency: {report.concurrency}")
        print(f"Total Requests: {report.total_requests}")
        print(f"Total Errors: {report.total_errors}")
        print(f"Overall RPS: {report.overall_rps:.1f}")
        print(f"\nEndpoint Results:")
        print("-" * 80)

        for endpoint in report.endpoints:
            print(f"\n{endpoint.method} {endpoint.endpoint}")
            print(f"  Requests: {endpoint.total_requests} "
                  f"(Success: {endpoint.successful_requests}, "
                  f"Failed: {endpoint.failed_requests})")
            print(f"  Error Rate: {endpoint.error_rate:.1f}%")
            print(f"  Throughput: {endpoint.requests_per_second:.1f} req/s")
            print(f"  Latency:")
            print(f"    p50: {endpoint.latency_p50:.1f}ms")
            print(f"    p95: {endpoint.latency_p95:.1f}ms")
            print(f"    p99: {endpoint.latency_p99:.1f}ms")
            print(f"    mean: {endpoint.latency_mean:.1f}ms")
            print(f"    range: {endpoint.latency_min:.1f}ms - {endpoint.latency_max:.1f}ms")

        print("=" * 80)


async def main():
    parser = argparse.ArgumentParser(description="Performance Load Harness")
    parser.add_argument(
        '--base-url',
        type=str,
        default='http://localhost:8000',
        help="Base URL of API (default: http://localhost:8000)"
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=120,
        help="Test duration in seconds (default: 120)"
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)"
    )
    parser.add_argument(
        '--endpoints',
        type=str,
        help="Comma-separated list of endpoints to test (default: all)"
    )
    parser.add_argument(
        '--output',
        type=str,
        default='artifacts/perf/load_test.json',
        help="Output path for JSON report"
    )

    args = parser.parse_args()

    # Parse endpoints
    endpoint_names = None
    if args.endpoints:
        endpoint_names = [e.strip() for e in args.endpoints.split(',')]

    # Run load test
    harness = LoadHarness(
        base_url=args.base_url,
        concurrency=args.concurrency,
        duration_seconds=args.duration
    )

    report = await harness.run_test(endpoint_names=endpoint_names)

    # Print and save report
    harness.print_report(report)
    harness.save_report(report, args.output)


if __name__ == "__main__":
    asyncio.run(main())
