#!/usr/bin/env python3
"""
Distributed Tracing Demo

Simulates a distributed trace across multiple services:
User → CRM Frontend → CRM API → Task Queue → Background Task → OPS API

Demonstrates:
- W3C traceparent propagation
- Parent-child span relationships
- Trace context in logs
- Cross-service tracing

Usage:
    python scripts/observability/trace_demo.py
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability.logger import get_logger
from observability.tracing import TraceContext, propagate_trace, extract_trace
from observability.metrics import http_requests_total, http_request_duration_ms, task_processing_duration_ms


class ServiceSimulator:
    """Simulate a microservice"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger(service_name, service_name=service_name)

    def handle_request(self, method: str, path: str, trace: TraceContext, user_id: str = None):
        """Simulate handling an HTTP request"""

        # Create child span for this service
        span = trace.create_child_span()

        # Log request received
        self.logger.info(
            f"Received {method} {path}",
            http_method=method,
            http_path=path,
            trace_id=span.trace_id,
            span_id=span.span_id,
            user_id=user_id,
            event_action="http.request",
            event_category="web"
        )

        # Simulate processing time
        start = time.time()
        time.sleep(0.05 + (hash(path) % 50) / 1000)  # 50-100ms
        duration_ms = (time.time() - start) * 1000

        # Record metrics
        http_requests_total.inc(method=method, path=path, status="200")
        http_request_duration_ms.observe(duration_ms, method=method, path=path)

        # Log response
        self.logger.info(
            f"Responded {method} {path} - 200 OK",
            http_method=method,
            http_path=path,
            http_status=200,
            trace_id=span.trace_id,
            span_id=span.span_id,
            event_duration=duration_ms,
            event_action="http.response",
            event_outcome="success"
        )

        return span

    def call_downstream(self, downstream_service: "ServiceSimulator", method: str, path: str, trace: TraceContext):
        """Call downstream service"""

        # Create child span for outgoing request
        span = trace.create_child_span()

        # Log outgoing request
        self.logger.info(
            f"Calling downstream {downstream_service.service_name} {method} {path}",
            http_method=method,
            http_path=path,
            trace_id=span.trace_id,
            span_id=span.span_id,
            downstream_service=downstream_service.service_name,
            event_action="http.client.request"
        )

        # Simulate network latency
        time.sleep(0.01)

        # Call downstream (propagate trace)
        downstream_span = downstream_service.handle_request(method, path, span)

        return downstream_span


class TaskQueueSimulator:
    """Simulate a task queue (Celery-like)"""

    def __init__(self, queue_name: str = "default"):
        self.queue_name = queue_name
        self.logger = get_logger(f"task_queue.{queue_name}", service_name="task_queue")

    def enqueue(self, task_type: str, trace: TraceContext, **kwargs):
        """Enqueue a task"""

        # Create child span for enqueue operation
        span = trace.create_child_span()

        self.logger.info(
            f"Task enqueued: {task_type}",
            queue=self.queue_name,
            task_type=task_type,
            trace_id=span.trace_id,
            span_id=span.span_id,
            event_action="task.enqueue"
        )

        return span

    def process(self, task_type: str, trace: TraceContext, ops_service: ServiceSimulator):
        """Process a task"""

        # Create child span for task processing
        span = trace.create_child_span()

        self.logger.info(
            f"Task processing started: {task_type}",
            queue=self.queue_name,
            task_type=task_type,
            trace_id=span.trace_id,
            span_id=span.span_id,
            event_action="task.process.start"
        )

        # Simulate task work
        start = time.time()
        time.sleep(0.1)  # 100ms task

        # Task calls ops API
        if ops_service:
            ops_service.handle_request("POST", "/api/v1/sync", span)

        duration_ms = (time.time() - start) * 1000

        # Record metrics
        task_processing_duration_ms.observe(duration_ms, queue=self.queue_name, task_type=task_type)

        self.logger.info(
            f"Task processing completed: {task_type}",
            queue=self.queue_name,
            task_type=task_type,
            trace_id=span.trace_id,
            span_id=span.span_id,
            event_duration=duration_ms,
            event_action="task.process.complete",
            event_outcome="success"
        )

        return span


def demo_simple_trace():
    """Demo 1: Simple HTTP request trace"""
    print(f"\n{'='*70}")
    print(f"Demo 1: Simple HTTP Request Trace")
    print(f"{'='*70}\n")

    # Create CRM API service
    crm_api = ServiceSimulator("crm_api")

    # Start trace
    trace = TraceContext.create()

    print(f"🔍 Trace ID: {trace.trace_id}")
    print(f"🔍 Root Span ID: {trace.span_id}\n")

    # Simulate user login request
    crm_api.handle_request("POST", "/api/v1/auth/login", trace, user_id="user123")

    print(f"\n✅ Simple trace complete\n")


def demo_cross_service_trace():
    """Demo 2: Cross-service trace (Frontend → API)"""
    print(f"\n{'='*70}")
    print(f"Demo 2: Cross-Service Trace (Frontend → API)")
    print(f"{'='*70}\n")

    # Create services
    crm_frontend = ServiceSimulator("crm_frontend")
    crm_api = ServiceSimulator("crm_api")

    # Start trace at frontend
    trace = TraceContext.create()

    print(f"🔍 Trace ID: {trace.trace_id}\n")

    # Frontend handles user request
    frontend_span = crm_frontend.handle_request("GET", "/dashboard", trace, user_id="user456")

    # Frontend calls CRM API
    crm_frontend.call_downstream(crm_api, "GET", "/api/v1/leads", frontend_span)

    print(f"\n✅ Cross-service trace complete\n")


def demo_full_distributed_trace():
    """Demo 3: Full distributed trace with task queue"""
    print(f"\n{'='*70}")
    print(f"Demo 3: Full Distributed Trace")
    print(f"User → CRM Frontend → CRM API → Task Queue → Worker → Ops API")
    print(f"{'='*70}\n")

    # Create all services
    crm_frontend = ServiceSimulator("crm_frontend")
    crm_api = ServiceSimulator("crm_api")
    ops_api = ServiceSimulator("ops_api")
    task_queue = TaskQueueSimulator("celery")

    # Start trace
    trace = TraceContext.create()

    print(f"🔍 Trace ID: {trace.trace_id}")
    print(f"📊 Following this trace through the system...\n")

    # 1. User interacts with frontend
    print("1️⃣  User submits form in CRM Frontend")
    frontend_span = crm_frontend.handle_request("POST", "/leads/create", trace, user_id="user789")

    time.sleep(0.02)

    # 2. Frontend calls CRM API
    print("\n2️⃣  Frontend calls CRM API")
    api_span = crm_frontend.call_downstream(crm_api, "POST", "/api/v1/leads", frontend_span)

    time.sleep(0.02)

    # 3. CRM API enqueues background task
    print("\n3️⃣  CRM API enqueues background task")
    task_span = task_queue.enqueue("sync_to_ops", api_span, lead_id="lead-123")

    time.sleep(0.05)

    # 4. Worker processes task
    print("\n4️⃣  Background worker processes task")
    worker_span = task_queue.process("sync_to_ops", task_span, ops_api)

    print(f"\n✅ Full distributed trace complete")
    print(f"📊 Total spans: 8 (frontend, frontend→api, api, api→task, task, task→worker, worker→ops, ops)")
    print(f"🔍 All spans share trace ID: {trace.trace_id}\n")


def demo_trace_sampling():
    """Demo 4: Trace sampling (sampled vs unsampled)"""
    print(f"\n{'='*70}")
    print(f"Demo 4: Trace Sampling")
    print(f"{'='*70}\n")

    crm_api = ServiceSimulator("crm_api")

    # Sampled trace (default)
    sampled_trace = TraceContext.create(sampled=True)
    print(f"🔍 Sampled trace (flags=01): {sampled_trace.trace_id}")
    crm_api.handle_request("GET", "/api/v1/health", sampled_trace)

    print()

    # Unsampled trace
    unsampled_trace = TraceContext.create(sampled=False)
    print(f"🔍 Unsampled trace (flags=00): {unsampled_trace.trace_id}")
    crm_api.handle_request("GET", "/api/v1/health", unsampled_trace)

    print(f"\n✅ Sampling demo complete\n")


def demo_trace_propagation_headers():
    """Demo 5: W3C traceparent header propagation"""
    print(f"\n{'='*70}")
    print(f"Demo 5: W3C Traceparent Header Propagation")
    print(f"{'='*70}\n")

    # Create trace
    trace = TraceContext.create()

    # Generate traceparent header
    traceparent = trace.to_traceparent()

    print(f"📤 Outgoing Request Headers:")
    print(f"   traceparent: {traceparent}")
    print()

    # Simulate receiving request at downstream service
    headers = {"traceparent": traceparent}

    # Extract trace at downstream
    downstream_trace = extract_trace(headers)

    print(f"📥 Incoming Request - Extracted Trace:")
    print(f"   Trace ID: {downstream_trace.trace_id}")
    print(f"   Parent Span ID: {downstream_trace.span_id}")
    print()

    # Create child span
    child_span = downstream_trace.create_child_span()

    print(f"👶 Created Child Span:")
    print(f"   Trace ID: {child_span.trace_id} (same as parent)")
    print(f"   Span ID: {child_span.span_id} (new)")
    print()

    print(f"✅ Trace propagation verified\n")


def main():
    """Run all demos"""
    print(f"\n{'='*70}")
    print(f"🔬 Distributed Tracing Demo")
    print(f"{'='*70}")

    # Run demos
    demo_simple_trace()
    time.sleep(0.5)

    demo_cross_service_trace()
    time.sleep(0.5)

    demo_full_distributed_trace()
    time.sleep(0.5)

    demo_trace_sampling()
    time.sleep(0.5)

    demo_trace_propagation_headers()

    print(f"{'='*70}")
    print(f"✅ All Demos Complete!")
    print(f"{'='*70}")
    print()
    print(f"📋 Check logs/ directory for JSON Lines logs with trace IDs")
    print(f"🔍 Look for 'trace_id' and 'span_id' fields in log entries")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
