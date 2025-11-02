/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Feature Flag System.
 *
 * Provides environment-based and localStorage-based feature flag management.
 * Flags can be set via build-time environment variables or overridden at runtime
 * via localStorage for testing and debugging.
 */

/**
 * Defined feature flags.
 */
export enum FeatureFlag {
  // UI Features
  ENABLE_NEW_DASHBOARD = "enableNewDashboard",

  // Security/Validation
  STRICT_WEBHOOK_WINDOW = "strictWebhookWindow",

  // Infrastructure
  ENABLE_RATE_LIMITING = "enableRateLimiting",
  ENABLE_EMAIL_NOTIFICATIONS = "enableEmailNotifications",
}

/**
 * Feature flag configuration from environment variables.
 *
 * Set at build time via VITE_FEATURE_FLAG_* environment variables.
 */
const ENV_FLAGS: Record<string, boolean> = {
  [FeatureFlag.ENABLE_NEW_DASHBOARD]:
    import.meta.env.VITE_FEATURE_FLAG_ENABLE_NEW_DASHBOARD === "true",
  [FeatureFlag.STRICT_WEBHOOK_WINDOW]:
    import.meta.env.VITE_FEATURE_FLAG_STRICT_WEBHOOK_WINDOW === "true",
  [FeatureFlag.ENABLE_RATE_LIMITING]:
    import.meta.env.VITE_FEATURE_FLAG_ENABLE_RATE_LIMITING === "true",
  [FeatureFlag.ENABLE_EMAIL_NOTIFICATIONS]:
    import.meta.env.VITE_FEATURE_FLAG_ENABLE_EMAIL_NOTIFICATIONS === "true",
};

/**
 * localStorage key prefix for feature flags.
 */
const STORAGE_PREFIX = "ff_";

/**
 * Check if a feature flag is enabled.
 *
 * Priority order:
 * 1. localStorage override (ff_<flagName>)
 * 2. Environment variable (VITE_FEATURE_FLAG_*)
 * 3. Default value (false)
 *
 * @param flag - Feature flag to check
 * @returns True if flag is enabled, False otherwise
 *
 * @example
 * if (isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)) {
 *   return <NewDashboard />;
 * }
 */
export function isEnabled(flag: FeatureFlag): boolean {
  // Check localStorage override first (for testing/debugging)
  const storageKey = `${STORAGE_PREFIX}${flag}`;
  const storageValue = localStorage.getItem(storageKey);

  if (storageValue !== null) {
    return storageValue.toLowerCase() === "true";
  }

  // Check environment variable
  return ENV_FLAGS[flag] ?? false;
}

/**
 * Set a feature flag override in localStorage.
 *
 * This is useful for:
 * - Testing (enable/disable flags in browser console)
 * - QA (test features before deployment)
 * - Debugging (isolate feature-specific issues)
 *
 * @param flag - Feature flag to set
 * @param enabled - Whether to enable (true) or disable (false) the flag
 *
 * @example
 * // In browser console
 * setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true)
 * // Reload page to see changes
 */
export function setFlag(flag: FeatureFlag, enabled: boolean): void {
  const storageKey = `${STORAGE_PREFIX}${flag}`;
  localStorage.setItem(storageKey, enabled.toString());
}

/**
 * Clear a feature flag override from localStorage.
 *
 * After clearing, the flag will fall back to environment variable or default.
 *
 * @param flag - Feature flag to clear
 *
 * @example
 * clearFlag(FeatureFlag.ENABLE_NEW_DASHBOARD)
 */
export function clearFlag(flag: FeatureFlag): void {
  const storageKey = `${STORAGE_PREFIX}${flag}`;
  localStorage.removeItem(storageKey);
}

/**
 * Clear all feature flag overrides from localStorage.
 *
 * Useful for returning to default configuration.
 */
export function clearAllFlags(): void {
  // Iterate through all localStorage keys
  const keysToRemove: string[] = [];

  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(STORAGE_PREFIX)) {
      keysToRemove.push(key);
    }
  }

  // Remove all flag keys
  keysToRemove.forEach((key) => {
    localStorage.removeItem(key);
  });
}

/**
 * Get current state of all feature flags.
 *
 * @returns Object mapping flag names to their enabled state
 */
export function getAllFlags(): Record<string, boolean> {
  const flags: Record<string, boolean> = {};

  Object.values(FeatureFlag).forEach((flag) => {
    flags[flag] = isEnabled(flag);
  });

  return flags;
}

/**
 * Get the source of a flag's value (for debugging).
 *
 * @param flag - Feature flag to check
 * @returns "localStorage" if overridden, "environment" if set via env, "default" otherwise
 *
 * @example
 * getFlagSource(FeatureFlag.ENABLE_NEW_DASHBOARD) // "localStorage"
 */
export function getFlagSource(flag: FeatureFlag): "localStorage" | "environment" | "default" {
  const storageKey = `${STORAGE_PREFIX}${flag}`;
  const storageValue = localStorage.getItem(storageKey);

  if (storageValue !== null) {
    return "localStorage";
  }

  // Check if environment variable was actually set (truthy value means it was set to "true")
  const envKey = `VITE_FEATURE_FLAG_${flag.replace(/([A-Z])/g, "_$1").toUpperCase().substring(1)}`;
  const envValue = (import.meta.env as any)[envKey];

  if (envValue === "true") {
    return "environment";
  }

  return "default";
}

/**
 * Feature flag descriptions for documentation/debugging.
 */
export const FLAG_DESCRIPTIONS: Record<FeatureFlag, string> = {
  [FeatureFlag.ENABLE_NEW_DASHBOARD]:
    "Enable new dashboard UI with improved analytics and visualizations. Gradual rollout feature.",
  [FeatureFlag.STRICT_WEBHOOK_WINDOW]:
    "Enforce strict 5-minute timestamp window for webhook signature validation. Prevents replay attacks.",
  [FeatureFlag.ENABLE_RATE_LIMITING]:
    "Enable API rate limiting to prevent abuse. Recommended for staging and production.",
  [FeatureFlag.ENABLE_EMAIL_NOTIFICATIONS]:
    "Send email notifications for lead assignments, status changes, etc.",
};

/**
 * Get human-readable description of a feature flag.
 */
export function getFlagDescription(flag: FeatureFlag): string {
  return FLAG_DESCRIPTIONS[flag] || "No description available";
}

/**
 * Debug helper: Log all flags and their sources.
 *
 * Useful for troubleshooting flag configuration.
 *
 * @example
 * // In browser console
 * logAllFlags()
 * // Output:
 * // enableNewDashboard: true (localStorage)
 * // strictWebhookWindow: false (default)
 */
export function logAllFlags(): void {
  console.group("🚩 Feature Flags");

  Object.values(FeatureFlag).forEach((flag) => {
    const enabled = isEnabled(flag);
    const source = getFlagSource(flag);
    const icon = enabled ? "✅" : "❌";

    console.log(`${icon} ${flag}: ${enabled} (${source})`);
  });

  console.groupEnd();
}

// Make flags available in browser console for debugging
if (typeof window !== "undefined") {
  (window as any).featureFlags = {
    isEnabled,
    setFlag,
    clearFlag,
    clearAllFlags,
    getAllFlags,
    getFlagSource,
    logAllFlags,
    FeatureFlag,
  };
}
