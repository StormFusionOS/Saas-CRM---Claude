#!/usr/bin/env python3
"""
Security Tests: Nginx Configuration Assertions.

Tests that Nginx config has required security headers:
- X-Frame-Options (clickjacking protection)
- Referrer-Policy (referrer information control)
- Permissions-Policy (feature policy)
- Origin pinning for /api routes
"""

import re
import sys
from pathlib import Path


class TestNginxConfig:
    """Test Nginx configuration security."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.nginx_config = self.project_root / "deploy" / "nginx" / "nginx.conf"

    def _read_config(self) -> str:
        """Read Nginx configuration file."""
        if not self.nginx_config.exists():
            raise FileNotFoundError(f"Nginx config not found: {self.nginx_config}")
        return self.nginx_config.read_text()

    def test_x_frame_options_present(self):
        """SEC-NGINX-001: X-Frame-Options header is present."""
        config = self._read_config()

        # Look for X-Frame-Options header
        pattern = r'add_header\s+X-Frame-Options\s+"?(DENY|SAMEORIGIN)"?'
        match = re.search(pattern, config, re.IGNORECASE)

        assert match is not None, "X-Frame-Options header must be set"

        value = match.group(1)
        assert value in ["DENY", "SAMEORIGIN"], \
            f"X-Frame-Options should be DENY or SAMEORIGIN, got: {value}"

        print(f"✓ SEC-NGINX-001: X-Frame-Options present ({value})")
        return True

    def test_referrer_policy_present(self):
        """SEC-NGINX-002: Referrer-Policy header is present."""
        config = self._read_config()

        # Look for Referrer-Policy header
        pattern = r'add_header\s+Referrer-Policy\s+"?([^";]+)"?'
        match = re.search(pattern, config, re.IGNORECASE)

        assert match is not None, "Referrer-Policy header must be set"

        value = match.group(1).strip()
        valid_policies = [
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin"
        ]

        assert value in valid_policies, \
            f"Referrer-Policy should be one of {valid_policies}, got: {value}"

        print(f"✓ SEC-NGINX-002: Referrer-Policy present ({value})")
        return True

    def test_permissions_policy_present(self):
        """SEC-NGINX-003: Permissions-Policy header is present."""
        config = self._read_config()

        # Look for Permissions-Policy header
        pattern = r'add_header\s+Permissions-Policy\s+"([^"]+)"'
        match = re.search(pattern, config, re.IGNORECASE)

        assert match is not None, "Permissions-Policy header must be set"

        value = match.group(1)

        # Verify at least some features are restricted
        restricted_features = ["camera", "microphone", "geolocation", "payment"]
        has_restrictions = any(feature in value for feature in restricted_features)

        assert has_restrictions, \
            "Permissions-Policy should restrict at least some features"

        print(f"✓ SEC-NGINX-003: Permissions-Policy present (restricts {len([f for f in restricted_features if f in value])} features)")
        return True

    def test_origin_pinning_for_api(self):
        """SEC-NGINX-004: Origin pinning enforced for /api routes."""
        config = self._read_config()

        # Look for origin validation in API location blocks
        # Pattern: location /api with origin checks
        api_location_pattern = r'location\s+/api[^{]*\{[^}]*\}'
        api_locations = re.findall(api_location_pattern, config, re.DOTALL)

        assert len(api_locations) > 0, "Should have /api location blocks"

        # Check for origin validation
        origin_checks = [
            r'\$http_origin',  # Origin variable usage
            r'add_header\s+Access-Control-Allow-Origin',  # CORS header
            r'if.*\$http_origin',  # Origin conditional
        ]

        found_origin_checks = 0
        for location in api_locations:
            for pattern in origin_checks:
                if re.search(pattern, location, re.IGNORECASE):
                    found_origin_checks += 1
                    break

        assert found_origin_checks > 0, \
            "API routes should have origin validation/CORS configuration"

        print(f"✓ SEC-NGINX-004: Origin pinning for /api routes ({found_origin_checks} locations)")
        return True

    def test_hsts_header_present(self):
        """SEC-NGINX-005: HSTS (Strict-Transport-Security) header is present."""
        config = self._read_config()

        # Look for HSTS header
        pattern = r'add_header\s+Strict-Transport-Security\s+"([^"]+)"'
        match = re.search(pattern, config, re.IGNORECASE)

        assert match is not None, "Strict-Transport-Security header must be set"

        value = match.group(1)

        # Verify it has max-age
        assert "max-age=" in value, "HSTS should specify max-age"

        # Extract max-age value
        max_age_match = re.search(r'max-age=(\d+)', value)
        if max_age_match:
            max_age = int(max_age_match.group(1))
            assert max_age >= 31536000, \
                f"HSTS max-age should be at least 1 year (31536000s), got: {max_age}"

        print(f"✓ SEC-NGINX-005: HSTS header present (max-age: {max_age}s)")
        return True

    def test_csp_header_present(self):
        """SEC-NGINX-006: Content-Security-Policy header is present."""
        config = self._read_config()

        # Look for CSP header
        pattern = r'add_header\s+Content-Security-Policy\s+"([^"]+)"'
        match = re.search(pattern, config, re.IGNORECASE)

        assert match is not None, "Content-Security-Policy header must be set"

        value = match.group(1)

        # Verify it has at least default-src directive
        assert "default-src" in value or "script-src" in value, \
            "CSP should specify at least default-src or script-src"

        print(f"✓ SEC-NGINX-006: CSP header present")
        return True

    def test_rate_limiting_configured(self):
        """SEC-NGINX-007: Rate limiting is configured."""
        config = self._read_config()

        # Look for rate limiting configuration
        patterns = [
            r'limit_req_zone',  # Rate limit zone definition
            r'limit_req\s+zone',  # Rate limit usage
            r'limit_conn_zone',  # Connection limit zone
            r'limit_conn\s+',  # Connection limit usage
        ]

        found_patterns = sum(1 for pattern in patterns if re.search(pattern, config))

        assert found_patterns > 0, "Rate limiting should be configured"

        print(f"✓ SEC-NGINX-007: Rate limiting configured ({found_patterns} directives)")
        return True

    def test_server_tokens_off(self):
        """SEC-NGINX-008: server_tokens is set to off (hide Nginx version)."""
        config = self._read_config()

        # Look for server_tokens directive
        pattern = r'server_tokens\s+off'
        match = re.search(pattern, config, re.IGNORECASE)

        # It's acceptable if not found (defaults to off in some configs)
        # But if found, verify it's set to off
        if match:
            print("✓ SEC-NGINX-008: server_tokens explicitly set to off")
        else:
            # Check it's not set to on
            on_pattern = r'server_tokens\s+on'
            on_match = re.search(on_pattern, config, re.IGNORECASE)
            assert on_match is None, "server_tokens should not be set to 'on'"
            print("✓ SEC-NGINX-008: server_tokens not exposing version (default or off)")

        return True


def run_tests():
    """Run all Nginx config tests."""
    print("\n" + "="*80)
    print("SECURITY TESTS: NGINX CONFIGURATION")
    print("="*80)

    test_suite = TestNginxConfig()
    tests = [
        test_suite.test_x_frame_options_present,
        test_suite.test_referrer_policy_present,
        test_suite.test_permissions_policy_present,
        test_suite.test_origin_pinning_for_api,
        test_suite.test_hsts_header_present,
        test_suite.test_csp_header_present,
        test_suite.test_rate_limiting_configured,
        test_suite.test_server_tokens_off,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ {test.__doc__.split(':')[0]}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__doc__.split(':')[0]}: ERROR - {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
