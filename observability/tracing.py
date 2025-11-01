"""
Distributed Tracing Module

Implements W3C Trace Context (traceparent/tracestate) propagation.

Features:
- W3C traceparent header generation and parsing
- Trace ID and span ID generation
- Context propagation across services
- Parent-child span relationships

W3C Traceparent Format:
    traceparent: 00-{trace-id}-{parent-id}-{trace-flags}
    Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

Usage:
    from observability.tracing import TraceContext, propagate_trace

    # Start new trace
    trace = TraceContext.create()

    # Propagate to downstream service
    headers = {"traceparent": trace.to_traceparent()}

    # Parse from upstream
    trace = TraceContext.from_traceparent(headers.get("traceparent"))

    # Create child span
    child_trace = trace.create_child_span()
"""

import random
import re
from dataclasses import dataclass
from typing import Optional, Dict


# W3C Traceparent regex
TRACEPARENT_PATTERN = re.compile(
    r'^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$'
)


@dataclass
class TraceContext:
    """W3C Trace Context"""

    trace_id: str  # 32 hex chars
    span_id: str   # 16 hex chars
    version: str = "00"
    trace_flags: str = "01"  # 01 = sampled

    @classmethod
    def create(cls, sampled: bool = True) -> "TraceContext":
        """
        Create new trace context.

        Args:
            sampled: Whether trace should be sampled (default True)

        Returns:
            TraceContext with new trace ID and span ID
        """
        trace_id = cls._generate_trace_id()
        span_id = cls._generate_span_id()
        trace_flags = "01" if sampled else "00"

        return cls(
            trace_id=trace_id,
            span_id=span_id,
            version="00",
            trace_flags=trace_flags
        )

    @classmethod
    def from_traceparent(cls, traceparent: Optional[str]) -> Optional["TraceContext"]:
        """
        Parse W3C traceparent header.

        Args:
            traceparent: Traceparent header value

        Returns:
            TraceContext if valid, None otherwise
        """
        if not traceparent:
            return None

        match = TRACEPARENT_PATTERN.match(traceparent.strip())
        if not match:
            return None

        version, trace_id, span_id, trace_flags = match.groups()

        # Validate trace ID (cannot be all zeros)
        if trace_id == "00000000000000000000000000000000":
            return None

        # Validate span ID (cannot be all zeros)
        if span_id == "0000000000000000":
            return None

        return cls(
            trace_id=trace_id,
            span_id=span_id,
            version=version,
            trace_flags=trace_flags
        )

    def to_traceparent(self) -> str:
        """
        Generate W3C traceparent header.

        Returns:
            Traceparent header value
        """
        return f"{self.version}-{self.trace_id}-{self.span_id}-{self.trace_flags}"

    def create_child_span(self) -> "TraceContext":
        """
        Create child span with same trace ID.

        Returns:
            New TraceContext with same trace_id but new span_id
        """
        return TraceContext(
            trace_id=self.trace_id,
            span_id=self._generate_span_id(),
            version=self.version,
            trace_flags=self.trace_flags
        )

    def is_sampled(self) -> bool:
        """Check if trace is sampled"""
        return self.trace_flags == "01"

    @staticmethod
    def _generate_trace_id() -> str:
        """Generate random 32-char hex trace ID"""
        return ''.join(f'{random.randint(0, 255):02x}' for _ in range(16))

    @staticmethod
    def _generate_span_id() -> str:
        """Generate random 16-char hex span ID"""
        return ''.join(f'{random.randint(0, 255):02x}' for _ in range(8))

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for logging"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "version": self.version,
            "trace_flags": self.trace_flags,
        }


def propagate_trace(trace: Optional[TraceContext]) -> Dict[str, str]:
    """
    Create headers for trace propagation.

    Args:
        trace: TraceContext or None

    Returns:
        Dictionary of headers to propagate
    """
    if not trace:
        trace = TraceContext.create()

    return {
        "traceparent": trace.to_traceparent()
    }


def extract_trace(headers: Dict[str, str]) -> TraceContext:
    """
    Extract trace context from headers.

    Args:
        headers: Request headers (case-insensitive)

    Returns:
        TraceContext (creates new if not found)
    """
    # Try to find traceparent header (case-insensitive)
    traceparent = None
    for key, value in headers.items():
        if key.lower() == "traceparent":
            traceparent = value
            break

    trace = TraceContext.from_traceparent(traceparent)

    # Create new trace if not found
    if not trace:
        trace = TraceContext.create()

    return trace


# Thread-local trace context storage
import threading

_trace_context = threading.local()


def set_current_trace(trace: TraceContext) -> None:
    """Set current trace context for this thread"""
    _trace_context.trace = trace


def get_current_trace() -> Optional[TraceContext]:
    """Get current trace context for this thread"""
    return getattr(_trace_context, 'trace', None)


def clear_current_trace() -> None:
    """Clear current trace context"""
    if hasattr(_trace_context, 'trace'):
        del _trace_context.trace
