"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Tests for Nginx configuration hardening.

Verifies that the Nginx config includes proper security headers and policies.
"""

import pytest
from pathlib import Path


def test_nginx_config_exists():
    """Test that Nginx config file exists."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"

    assert nginx_config.exists(), "Nginx config file should exist"


def test_nginx_has_csp_headers():
    """Test that Nginx config includes Content-Security-Policy headers."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    assert "Content-Security-Policy" in content, "CSP headers should be configured"
    assert "default-src" in content, "CSP should include default-src directive"


def test_nginx_has_hsts():
    """Test that Nginx config includes HSTS (Strict-Transport-Security)."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    assert "Strict-Transport-Security" in content, "HSTS header should be configured"
    assert "max-age" in content, "HSTS should include max-age directive"


def test_nginx_has_xframe_options():
    """Test that Nginx config includes X-Frame-Options header."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    assert "X-Frame-Options" in content, "X-Frame-Options header should be configured"
    assert "SAMEORIGIN" in content or "DENY" in content, "X-Frame-Options should be set to SAMEORIGIN or DENY"


def test_nginx_has_content_type_options():
    """Test that Nginx config includes X-Content-Type-Options header."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    assert "X-Content-Type-Options" in content, "X-Content-Type-Options header should be configured"
    assert "nosniff" in content, "X-Content-Type-Options should be set to nosniff"


def test_nginx_has_rate_limiting():
    """Test that Nginx config includes rate limiting."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    assert "limit_req_zone" in content, "Rate limiting should be configured"
    assert "limit_req" in content, "Rate limiting should be applied"


def test_nginx_has_origin_enforcement():
    """Test that Nginx config enforces origin checking."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    # Check for origin validation logic
    assert "cors_origin" in content or "http_origin" in content, "Origin checking should be implemented"
    assert "Access-Control-Allow-Origin" in content, "CORS headers should be configured"


def test_nginx_has_separate_server_blocks():
    """Test that CRM and Ops have separate server blocks."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    # Count server blocks
    server_count = content.count("server {")

    assert server_count >= 2, "Should have at least 2 separate server blocks (CRM and Ops)"


def test_nginx_comment_shows_expected_headers():
    """Test that Nginx config has comments about expected headers."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    # Check for helpful comments
    assert "#" in content, "Config should include comments for maintainability"

    # Check for specific important terms in comments or config
    lower_content = content.lower()
    assert "security" in lower_content or "hardened" in lower_content, "Should mention security/hardening"


def test_nginx_has_gzip_compression():
    """Test that Nginx config includes gzip compression."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    assert "gzip" in content, "Gzip compression should be configured"


def test_nginx_blocks_cross_origin_api_calls():
    """Test that Nginx config blocks cross-origin API calls."""
    nginx_config = Path(__file__).parent.parent.parent / "deploy" / "nginx" / "nginx.conf"
    content = nginx_config.read_text()

    # Should have logic to check and potentially reject based on origin
    assert "return 403" in content or "Forbidden" in content, "Should have logic to block unauthorized origins"
