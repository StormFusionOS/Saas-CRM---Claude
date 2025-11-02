"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Tests for feature flag system.

Verifies that flags behave deterministically with environment variables,
runtime overrides, and default values.
"""

import os
import pytest
from app.core.feature_flags import (
    FeatureFlag,
    is_enabled,
    set_flag,
    clear_flag,
    clear_all_flags,
    get_all_flags,
    get_flag_source,
    get_flag_description,
)


@pytest.fixture(autouse=True)
def clean_flags():
    """Clear all runtime flags before each test."""
    clear_all_flags()
    yield
    clear_all_flags()


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Clear flag-related environment variables before each test."""
    for flag in FeatureFlag:
        monkeypatch.delenv(flag.value, raising=False)


class TestFeatureFlagDefaults:
    """Test default flag behavior (no env, no runtime override)."""

    def test_all_flags_disabled_by_default(self):
        """All flags should be disabled by default."""
        for flag in FeatureFlag:
            assert is_enabled(flag) is False, f"{flag.value} should be disabled by default"

    def test_default_source(self):
        """Flag source should be 'default' when not set."""
        assert get_flag_source(FeatureFlag.ENABLE_NEW_DASHBOARD) == "default"
        assert get_flag_source(FeatureFlag.STRICT_WEBHOOK_WINDOW) == "default"


class TestEnvironmentVariables:
    """Test flag behavior with environment variables."""

    def test_enable_via_env_true(self, monkeypatch):
        """Flag enabled when env variable is 'true'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_enable_via_env_1(self, monkeypatch):
        """Flag enabled when env variable is '1'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "1")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_enable_via_env_yes(self, monkeypatch):
        """Flag enabled when env variable is 'yes'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "yes")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_enable_via_env_on(self, monkeypatch):
        """Flag enabled when env variable is 'on'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "on")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_disable_via_env_false(self, monkeypatch):
        """Flag disabled when env variable is 'false'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "false")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_disable_via_env_0(self, monkeypatch):
        """Flag disabled when env variable is '0'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "0")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_disable_via_env_no(self, monkeypatch):
        """Flag disabled when env variable is 'no'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "no")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_disable_via_env_off(self, monkeypatch):
        """Flag disabled when env variable is 'off'."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "off")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_case_insensitive(self, monkeypatch):
        """Env variable values should be case-insensitive."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "TRUE")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "FALSE")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_environment_source(self, monkeypatch):
        """Flag source should be 'environment' when set via env."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")
        assert get_flag_source(FeatureFlag.ENABLE_NEW_DASHBOARD) == "environment"

    def test_multiple_flags_independent(self, monkeypatch):
        """Multiple flags can be set independently."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")
        monkeypatch.setenv("STRICT_WEBHOOK_WINDOW", "false")

        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True
        assert is_enabled(FeatureFlag.STRICT_WEBHOOK_WINDOW) is False


class TestRuntimeOverrides:
    """Test runtime flag overrides."""

    def test_enable_via_runtime(self):
        """Flag can be enabled at runtime."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_disable_via_runtime(self):
        """Flag can be disabled at runtime."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, False)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_runtime_overrides_env(self, monkeypatch):
        """Runtime override takes precedence over environment variable."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "false")
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)

        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_runtime_source(self):
        """Flag source should be 'runtime' when set via set_flag()."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        assert get_flag_source(FeatureFlag.ENABLE_NEW_DASHBOARD) == "runtime"

    def test_clear_flag_returns_to_env(self, monkeypatch):
        """Clearing a runtime flag returns to environment value."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, False)

        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

        clear_flag(FeatureFlag.ENABLE_NEW_DASHBOARD)

        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_clear_flag_returns_to_default(self):
        """Clearing a runtime flag with no env returns to default."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

        clear_flag(FeatureFlag.ENABLE_NEW_DASHBOARD)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_clear_all_flags(self):
        """clear_all_flags() clears all runtime overrides."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        set_flag(FeatureFlag.STRICT_WEBHOOK_WINDOW, True)

        clear_all_flags()

        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False
        assert is_enabled(FeatureFlag.STRICT_WEBHOOK_WINDOW) is False


class TestDeterministicBehavior:
    """Test that flags behave deterministically."""

    def test_same_input_same_output(self, monkeypatch):
        """Same configuration always produces same result."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")

        for _ in range(10):
            assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_toggle_behavior_deterministic(self):
        """Toggling flags produces deterministic results."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, False)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True


class TestGetAllFlags:
    """Test getting all flags at once."""

    def test_get_all_flags_default(self):
        """get_all_flags() returns all flags disabled by default."""
        flags = get_all_flags()

        assert len(flags) == len(FeatureFlag)
        for flag_value in flags.values():
            assert flag_value is False

    def test_get_all_flags_with_some_enabled(self, monkeypatch):
        """get_all_flags() returns correct state for mixed flags."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")
        set_flag(FeatureFlag.STRICT_WEBHOOK_WINDOW, True)

        flags = get_all_flags()

        assert flags["ENABLE_NEW_DASHBOARD"] is True
        assert flags["STRICT_WEBHOOK_WINDOW"] is True
        assert flags["ENABLE_RATE_LIMITING"] is False


class TestFlagDescriptions:
    """Test flag descriptions."""

    def test_all_flags_have_descriptions(self):
        """All defined flags should have descriptions."""
        for flag in FeatureFlag:
            description = get_flag_description(flag)
            assert description is not None
            assert len(description) > 0
            assert description != "No description available"


class TestWebhookBehavior:
    """Test that STRICT_WEBHOOK_WINDOW flag affects webhook validation behavior."""

    def test_strict_webhook_disabled_by_default(self):
        """Strict webhook validation should be disabled by default."""
        assert is_enabled(FeatureFlag.STRICT_WEBHOOK_WINDOW) is False

    def test_enable_strict_webhook_at_runtime(self):
        """Strict webhook validation can be enabled at runtime."""
        set_flag(FeatureFlag.STRICT_WEBHOOK_WINDOW, True)
        assert is_enabled(FeatureFlag.STRICT_WEBHOOK_WINDOW) is True

    def test_strict_webhook_via_env(self, monkeypatch):
        """Strict webhook validation can be set via environment."""
        monkeypatch.setenv("STRICT_WEBHOOK_WINDOW", "true")
        assert is_enabled(FeatureFlag.STRICT_WEBHOOK_WINDOW) is True


class TestDashboardBehavior:
    """Test that ENABLE_NEW_DASHBOARD flag determines dashboard behavior."""

    def test_new_dashboard_disabled_by_default(self):
        """New dashboard should be disabled by default."""
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is False

    def test_enable_new_dashboard_at_runtime(self):
        """New dashboard can be enabled at runtime."""
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True

    def test_new_dashboard_via_env(self, monkeypatch):
        """New dashboard can be enabled via environment."""
        monkeypatch.setenv("ENABLE_NEW_DASHBOARD", "true")
        assert is_enabled(FeatureFlag.ENABLE_NEW_DASHBOARD) is True
