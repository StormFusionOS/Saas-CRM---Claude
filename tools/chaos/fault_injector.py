#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Chaos Engineering - Fault Injector

Simulates failures to test system resilience:
- Network timeouts
- Service exceptions
- Database slowdowns
- Partial failures
- Resource exhaustion

Usage:
    from tools.chaos.fault_injector import FaultInjector, inject_fault

    # Decorator for fault injection
    @inject_fault(failure_rate=0.1, fault_type="timeout")
    def my_function():
        return "success"

    # Context manager
    with FaultInjector().inject("timeout", rate=0.2):
        # Code that may timeout
        response = requests.get(url)
"""

import time
import random
import functools
from typing import Callable, Optional, Literal
from contextlib import contextmanager

FaultType = Literal["timeout", "exception", "slowdown", "partial_failure", "network_error"]


class FaultInjector:
    """
    Chaos fault injection system

    Injects controlled failures for resilience testing.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize fault injector

        Args:
            enabled: Enable/disable fault injection (global kill switch)
        """
        self.enabled = enabled

    @contextmanager
    def inject(
        self,
        fault_type: FaultType,
        rate: float = 0.1,
        delay_ms: Optional[int] = None
    ):
        """
        Inject fault within context

        Args:
            fault_type: Type of fault to inject
            rate: Probability of fault (0.0 to 1.0)
            delay_ms: Delay in milliseconds (for slowdown)

        Yields:
            None

        Raises:
            Various exceptions based on fault_type
        """
        if not self.enabled or random.random() > rate:
            yield
            return

        # Inject fault
        if fault_type == "timeout":
            raise TimeoutError("Chaos: Simulated timeout")

        elif fault_type == "exception":
            raise RuntimeError("Chaos: Simulated exception")

        elif fault_type == "slowdown":
            delay = delay_ms or random.randint(1000, 5000)
            print(f"⚠️  Chaos: Injecting {delay}ms delay")
            time.sleep(delay / 1000)
            yield

        elif fault_type == "partial_failure":
            # Return None/empty instead of raising
            print(f"⚠️  Chaos: Injecting partial failure (degraded response)")
            yield

        elif fault_type == "network_error":
            raise ConnectionError("Chaos: Simulated network error")

        else:
            yield


def inject_fault(
    failure_rate: float = 0.1,
    fault_type: FaultType = "exception",
    delay_ms: Optional[int] = None
):
    """
    Decorator to inject faults into functions

    Args:
        failure_rate: Probability of fault (0.0 to 1.0)
        fault_type: Type of fault to inject
        delay_ms: Delay in milliseconds (for slowdown)

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            injector = FaultInjector()

            with injector.inject(fault_type, rate=failure_rate, delay_ms=delay_ms):
                return func(*args, **kwargs)

        return wrapper
    return decorator


# Example fault-prone functions for testing
class ResilientService:
    """Example service with retry/fallback logic"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    @inject_fault(failure_rate=0.3, fault_type="timeout")
    def unreliable_api_call(self, endpoint: str) -> dict:
        """Simulates an unreliable external API"""
        # Stub: Would make actual HTTP request
        return {"status": "success", "endpoint": endpoint}

    def api_call_with_retry(self, endpoint: str) -> dict:
        """API call with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                result = self.unreliable_api_call(endpoint)
                return result

            except TimeoutError as e:
                if attempt < self.max_retries - 1:
                    delay = (2 ** attempt) * 0.1  # Exponential backoff
                    print(f"  Retry {attempt + 1}/{self.max_retries} after {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"  ❌ All retries exhausted")
                    raise

    @inject_fault(failure_rate=0.2, fault_type="partial_failure")
    def get_user_data(self, user_id: str) -> dict:
        """Gets user data with fallback to cached data"""
        # Stub: Would query database
        return {
            "user_id": user_id,
            "name": "John Doe",
            "email": "john@example.com"
        }

    def get_user_with_fallback(self, user_id: str) -> dict:
        """Get user data with cache fallback"""
        try:
            return self.get_user_data(user_id)
        except Exception as e:
            print(f"  ⚠️  Primary failed, using cache: {e}")
            # Fallback to cache
            return self._get_cached_user(user_id)

    def _get_cached_user(self, user_id: str) -> dict:
        """Fallback cached user data (degraded response)"""
        return {
            "user_id": user_id,
            "name": "Cached User",
            "email": None,  # Degraded: missing email
            "cached": True
        }


if __name__ == "__main__":
    print("=== Chaos Fault Injector Demo ===\n")

    service = ResilientService(max_retries=3)

    # Test 1: Retry logic
    print("1. Testing retry logic (30% timeout rate):")
    for i in range(5):
        try:
            result = service.api_call_with_retry(f"/api/v1/data/{i}")
            print(f"  ✓ Call {i}: {result}")
        except TimeoutError:
            print(f"  ❌ Call {i}: Failed after retries")
    print()

    # Test 2: Fallback logic
    print("2. Testing fallback logic (20% partial failure rate):")
    for i in range(5):
        result = service.get_user_with_fallback(f"user_{i}")
        cached = result.get("cached", False)
        print(f"  {'⚠️  Cached' if cached else '✓ Fresh'}: {result}")
    print()

    print("=== Demo complete ===")
