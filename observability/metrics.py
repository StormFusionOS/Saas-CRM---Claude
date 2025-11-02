"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Metrics Module

Provides Prometheus-style metrics collection and exposition.

Features:
- Counter, Gauge, Histogram metrics
- Prometheus text exposition format
- HTTP metrics (requests, duration, bytes)
- Task queue metrics
- /metrics endpoint

Usage:
    from observability.metrics import metrics_registry, http_requests_total

    # Increment counter
    http_requests_total.inc(method="GET", path="/api/users", status="200")

    # Record histogram
    with http_request_duration_ms.time(method="GET", path="/api/users"):
        # ... handle request ...
        pass

    # Get metrics output
    output = metrics_registry.generate()
"""

import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple


class Metric:
    """Base metric class"""

    def __init__(self, name: str, help_text: str, labels: Optional[List[str]] = None):
        self.name = name
        self.help = help_text
        self.labels = labels or []
        self._lock = threading.Lock()


class Counter(Metric):
    """Counter metric - monotonically increasing value"""

    def __init__(self, name: str, help_text: str, labels: Optional[List[str]] = None):
        super().__init__(name, help_text, labels)
        self._values: Dict[Tuple, float] = defaultdict(float)

    def inc(self, value: float = 1.0, **label_values) -> None:
        """Increment counter"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            self._values[label_key] += value

    def get(self, **label_values) -> float:
        """Get counter value"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            return self._values[label_key]

    def _make_label_key(self, label_values: Dict[str, str]) -> Tuple:
        """Create hashable label key"""
        return tuple(sorted(label_values.items()))

    def samples(self) -> List[Tuple[Dict[str, str], float]]:
        """Get all samples"""
        with self._lock:
            return [
                (dict(labels), value)
                for labels, value in self._values.items()
            ]


class Gauge(Metric):
    """Gauge metric - can go up and down"""

    def __init__(self, name: str, help_text: str, labels: Optional[List[str]] = None):
        super().__init__(name, help_text, labels)
        self._values: Dict[Tuple, float] = defaultdict(float)

    def set(self, value: float, **label_values) -> None:
        """Set gauge value"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            self._values[label_key] = value

    def inc(self, value: float = 1.0, **label_values) -> None:
        """Increment gauge"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            self._values[label_key] += value

    def dec(self, value: float = 1.0, **label_values) -> None:
        """Decrement gauge"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            self._values[label_key] -= value

    def get(self, **label_values) -> float:
        """Get gauge value"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            return self._values[label_key]

    def _make_label_key(self, label_values: Dict[str, str]) -> Tuple:
        """Create hashable label key"""
        return tuple(sorted(label_values.items()))

    def samples(self) -> List[Tuple[Dict[str, str], float]]:
        """Get all samples"""
        with self._lock:
            return [
                (dict(labels), value)
                for labels, value in self._values.items()
            ]


class Histogram(Metric):
    """Histogram metric - track distribution of values"""

    # Default buckets (in milliseconds for duration)
    DEFAULT_BUCKETS = [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]

    def __init__(self, name: str, help_text: str, labels: Optional[List[str]] = None,
                 buckets: Optional[List[float]] = None):
        super().__init__(name, help_text, labels)
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self._counts: Dict[Tuple, Dict[float, int]] = defaultdict(lambda: defaultdict(int))
        self._sums: Dict[Tuple, float] = defaultdict(float)
        self._total_counts: Dict[Tuple, int] = defaultdict(int)

    def observe(self, value: float, **label_values) -> None:
        """Observe a value"""
        label_key = self._make_label_key(label_values)

        with self._lock:
            # Update buckets
            for bucket in self.buckets:
                if value <= bucket:
                    self._counts[label_key][bucket] += 1

            # Update sum and count
            self._sums[label_key] += value
            self._total_counts[label_key] += 1

    @contextmanager
    def time(self, **label_values):
        """Time a code block (in milliseconds)"""
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000
            self.observe(duration_ms, **label_values)

    def get_sum(self, **label_values) -> float:
        """Get sum of observed values"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            return self._sums[label_key]

    def get_count(self, **label_values) -> int:
        """Get count of observations"""
        label_key = self._make_label_key(label_values)
        with self._lock:
            return self._total_counts[label_key]

    def _make_label_key(self, label_values: Dict[str, str]) -> Tuple:
        """Create hashable label key"""
        return tuple(sorted(label_values.items()))

    def samples(self) -> List[Tuple[Dict[str, str], str, float]]:
        """Get all samples (labels, suffix, value)"""
        samples = []

        with self._lock:
            for label_key, counts in self._counts.items():
                labels = dict(label_key)

                # Bucket samples
                cumulative = 0
                for bucket in sorted(self.buckets):
                    cumulative += counts.get(bucket, 0)
                    bucket_labels = {**labels, "le": str(bucket)}
                    samples.append((bucket_labels, "_bucket", cumulative))

                # +Inf bucket
                inf_labels = {**labels, "le": "+Inf"}
                samples.append((inf_labels, "_bucket", self._total_counts[label_key]))

                # Sum and count
                samples.append((labels, "_sum", self._sums[label_key]))
                samples.append((labels, "_count", self._total_counts[label_key]))

        return samples


class MetricsRegistry:
    """Registry for all metrics"""

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._lock = threading.Lock()

    def register(self, metric: Metric) -> Metric:
        """Register a metric"""
        with self._lock:
            if metric.name in self._metrics:
                return self._metrics[metric.name]
            self._metrics[metric.name] = metric
            return metric

    def generate(self) -> str:
        """Generate Prometheus text format output"""
        lines = []

        with self._lock:
            for name, metric in sorted(self._metrics.items()):
                # TYPE and HELP
                metric_type = self._get_metric_type(metric)
                lines.append(f"# HELP {name} {metric.help}")
                lines.append(f"# TYPE {name} {metric_type}")

                # Samples
                if isinstance(metric, Histogram):
                    for labels, suffix, value in metric.samples():
                        label_str = self._format_labels(labels)
                        lines.append(f"{name}{suffix}{label_str} {value}")
                else:
                    for labels, value in metric.samples():
                        label_str = self._format_labels(labels)
                        lines.append(f"{name}{label_str} {value}")

                lines.append("")  # Blank line between metrics

        return "\n".join(lines)

    @staticmethod
    def _get_metric_type(metric: Metric) -> str:
        """Get Prometheus metric type"""
        if isinstance(metric, Counter):
            return "counter"
        elif isinstance(metric, Gauge):
            return "gauge"
        elif isinstance(metric, Histogram):
            return "histogram"
        else:
            return "untyped"

    @staticmethod
    def _format_labels(labels: Dict[str, str]) -> str:
        """Format labels for Prometheus"""
        if not labels:
            return ""

        label_parts = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(label_parts) + "}"


# Global metrics registry
metrics_registry = MetricsRegistry()


# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = metrics_registry.register(Counter(
    name="http_requests_total",
    help_text="Total number of HTTP requests",
    labels=["method", "path", "status"]
))

http_request_duration_ms = metrics_registry.register(Histogram(
    name="http_request_duration_ms",
    help_text="HTTP request duration in milliseconds",
    labels=["method", "path"],
    buckets=[5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
))

http_request_bytes = metrics_registry.register(Histogram(
    name="http_request_bytes",
    help_text="HTTP request body size in bytes",
    labels=["method", "path"],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
))

http_response_bytes = metrics_registry.register(Histogram(
    name="http_response_bytes",
    help_text="HTTP response body size in bytes",
    labels=["method", "path"],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
))

http_requests_in_progress = metrics_registry.register(Gauge(
    name="http_requests_in_progress",
    help_text="Number of HTTP requests currently being processed",
    labels=["method", "path"]
))


# ============================================================================
# Task Queue Metrics
# ============================================================================

task_queue_length = metrics_registry.register(Gauge(
    name="task_queue_length",
    help_text="Number of tasks waiting in queue",
    labels=["queue"]
))

task_processing_duration_ms = metrics_registry.register(Histogram(
    name="task_processing_duration_ms",
    help_text="Task processing duration in milliseconds",
    labels=["queue", "task_type"],
    buckets=[100, 500, 1000, 5000, 10000, 30000, 60000]
))

task_total = metrics_registry.register(Counter(
    name="task_total",
    help_text="Total number of tasks processed",
    labels=["queue", "task_type", "status"]
))

task_retries_total = metrics_registry.register(Counter(
    name="task_retries_total",
    help_text="Total number of task retries",
    labels=["queue", "task_type"]
))


# ============================================================================
# Database Metrics
# ============================================================================

db_connections_total = metrics_registry.register(Gauge(
    name="db_connections_total",
    help_text="Number of active database connections",
    labels=["database"]
))

db_query_duration_ms = metrics_registry.register(Histogram(
    name="db_query_duration_ms",
    help_text="Database query duration in milliseconds",
    labels=["database", "operation"],
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 5000]
))


# ============================================================================
# Application Metrics
# ============================================================================

app_info = metrics_registry.register(Gauge(
    name="app_info",
    help_text="Application information",
    labels=["version", "service"]
))

# Set app info (always 1, used for labels)
app_info.set(1, version="1.0.0", service="rivercityclean")
