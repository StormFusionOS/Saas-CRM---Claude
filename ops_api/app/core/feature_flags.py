"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Feature Flag System.

Provides environment-based and runtime feature flag management.
Flags can be set via environment variables or programmatically at runtime.
"""

import os
from typing import Dict, Any, Optional
from enum import Enum


class FeatureFlag(str, Enum):
    """
    Defined feature flags.

    Add new flags here to ensure type safety and documentation.
    """
    # UI Features
    ENABLE_NEW_DASHBOARD = "ENABLE_NEW_DASHBOARD"

    # Security/Validation
    STRICT_WEBHOOK_WINDOW = "STRICT_WEBHOOK_WINDOW"

    # Infrastructure
    ENABLE_RATE_LIMITING = "ENABLE_RATE_LIMITING"
    ENABLE_EMAIL_NOTIFICATIONS = "ENABLE_EMAIL_NOTIFICATIONS"


# Runtime flag overrides (for testing and dynamic configuration)
_runtime_flags: Dict[str, bool] = {}


def is_enabled(flag: FeatureFlag) -> bool:
    """
    Check if a feature flag is enabled.

    Priority order:
    1. Runtime override (set via set_flag())
    2. Environment variable
    3. Default value (False)

    Args:
        flag: Feature flag to check

    Returns:
        True if flag is enabled, False otherwise

    Example:
        if is_enabled(FeatureFlag.STRICT_WEBHOOK_WINDOW):
            validate_webhook_timestamp()
    """
    flag_name = flag.value

    # Check runtime override first
    if flag_name in _runtime_flags:
        return _runtime_flags[flag_name]

    # Check environment variable
    env_value = os.getenv(flag_name, "").lower()
    if env_value in ("1", "true", "yes", "on"):
        return True
    elif env_value in ("0", "false", "no", "off"):
        return False

    # Default to False
    return False


def set_flag(flag: FeatureFlag, enabled: bool) -> None:
    """
    Set a feature flag at runtime.

    This is useful for:
    - Testing (enable/disable flags in tests)
    - Dynamic configuration (enable flags based on user, A/B testing)
    - Admin controls (toggle flags without redeploying)

    Args:
        flag: Feature flag to set
        enabled: Whether to enable (True) or disable (False) the flag

    Example:
        # In tests
        set_flag(FeatureFlag.STRICT_WEBHOOK_WINDOW, False)

        # In admin endpoint
        set_flag(FeatureFlag.ENABLE_NEW_DASHBOARD, True)
    """
    _runtime_flags[flag.value] = enabled


def clear_flag(flag: FeatureFlag) -> None:
    """
    Clear runtime override for a feature flag.

    After clearing, the flag will fall back to environment variable or default.

    Args:
        flag: Feature flag to clear
    """
    _runtime_flags.pop(flag.value, None)


def clear_all_flags() -> None:
    """
    Clear all runtime flag overrides.

    Useful for test cleanup to ensure a clean slate.
    """
    _runtime_flags.clear()


def get_all_flags() -> Dict[str, bool]:
    """
    Get current state of all feature flags.

    Returns:
        Dictionary mapping flag names to their enabled state
    """
    return {
        flag.value: is_enabled(flag)
        for flag in FeatureFlag
    }


def get_flag_source(flag: FeatureFlag) -> str:
    """
    Get the source of a flag's value (for debugging).

    Returns:
        "runtime" if set via set_flag()
        "environment" if set via env variable
        "default" if using default value

    Example:
        >>> get_flag_source(FeatureFlag.STRICT_WEBHOOK_WINDOW)
        "environment"
    """
    flag_name = flag.value

    if flag_name in _runtime_flags:
        return "runtime"

    env_value = os.getenv(flag_name, "")
    if env_value:
        return "environment"

    return "default"


# Feature flag descriptions for documentation/admin UI
FLAG_DESCRIPTIONS: Dict[FeatureFlag, str] = {
    FeatureFlag.ENABLE_NEW_DASHBOARD: (
        "Enable new dashboard UI with improved analytics and visualizations. "
        "Gradual rollout feature."
    ),
    FeatureFlag.STRICT_WEBHOOK_WINDOW: (
        "Enforce strict 5-minute timestamp window for webhook signature validation. "
        "Prevents replay attacks but requires accurate server time synchronization."
    ),
    FeatureFlag.ENABLE_RATE_LIMITING: (
        "Enable API rate limiting to prevent abuse. "
        "Recommended for staging and production."
    ),
    FeatureFlag.ENABLE_EMAIL_NOTIFICATIONS: (
        "Send email notifications for lead assignments, status changes, etc. "
        "Requires SMTP configuration."
    ),
}


def get_flag_description(flag: FeatureFlag) -> str:
    """Get human-readable description of a feature flag."""
    return FLAG_DESCRIPTIONS.get(flag, "No description available")


__all__ = [
    "FeatureFlag",
    "is_enabled",
    "set_flag",
    "clear_flag",
    "clear_all_flags",
    "get_all_flags",
    "get_flag_source",
    "get_flag_description",
]
