#!/usr/bin/env python3
"""
Stub API Server for Load Testing

Simple HTTP server that simulates API endpoints for testing the load harness.

Usage:
    python tools/perf/stub_server.py
"""

import asyncio
import json
import random
from aiohttp import web


async def handle_login(request):
    """Simulate login endpoint"""
    await asyncio.sleep(random.uniform(0.05, 0.15))  # 50-150ms
    return web.json_response({
        "status": "success",
        "token": "fake_token_12345"
    })


async def handle_leads(request):
    """Simulate leads list endpoint"""
    await asyncio.sleep(random.uniform(0.1, 0.3))  # 100-300ms
    return web.json_response({
        "leads": [
            {"id": i, "name": f"Lead {i}", "status": "active"}
            for i in range(20)
        ],
        "total": 100
    })


async def handle_enqueue(request):
    """Simulate task enqueue endpoint"""
    await asyncio.sleep(random.uniform(0.02, 0.08))  # 20-80ms
    return web.json_response({
        "status": "enqueued",
        "task_id": f"task_{random.randint(1000, 9999)}"
    })


async def handle_health(request):
    """Health check"""
    return web.json_response({"status": "healthy"})


async def init_app():
    """Initialize app"""
    app = web.Application()

    # Add routes
    app.router.add_post('/api/v1/auth/login', handle_login)
    app.router.add_get('/api/v1/leads', handle_leads)
    app.router.add_post('/api/v1/tasks/enqueue', handle_enqueue)
    app.router.add_get('/health', handle_health)

    return app


if __name__ == "__main__":
    print("Starting stub API server on http://localhost:8000")
    web.run_app(init_app(), host='localhost', port=8000)
