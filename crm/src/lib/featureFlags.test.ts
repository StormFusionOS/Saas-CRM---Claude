/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Tests for feature flag system.
 *
 * Verifies that flags behave deterministically with environment variables,
 * localStorage overrides, and default values.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  FeatureFlag,
  isEnabled,
  setFlag,
  clearFlag,
  clearAllFlags,
  getAllFlags,
  getFlagSource,
  getFlagDescription,
} from "./featureFlags";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    // Add keys() method for iteration
    key: (index: number) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    },
    get length() {
      return Object.keys(store).length;
    },
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
  configurable: true,
});

describe("Feature Flags", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorageMock.clear();
  });

  afterEach(() => {
    // Clean up after each test
    clearAllFlags();
  });

  describe("Default Behavior", () => {
    it("should return false for all flags by default", () => {
      Object.values(FeatureFlag).forEach((flag) => {
        expect(isEnabled(flag)).toBe(false);
      });
    });

    it("should return 'default' as source when no override", () => {
      expect(getFlagSource(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe("default");
      expect(getFlagSource(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe("default");
    });
  });

  describe("localStorage Overrides", () => {
    it("should enable flag via localStorage", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
    });

    it("should disable flag via localStorage", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, false);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
    });

    it("should return 'localStorage' as source when overridden", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(getFlagSource(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe("localStorage");
    });

    it("should handle string 'true' in localStorage", () => {
      localStorageMock.setItem("ff_enableNewDashboard", "true");
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
    });

    it("should handle string 'false' in localStorage", () => {
      localStorageMock.setItem("ff_enableNewDashboard", "false");
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
    });

    it("should be case-insensitive for localStorage values", () => {
      localStorageMock.setItem("ff_enableNewDashboard", "TRUE");
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);

      localStorageMock.setItem("ff_enableNewDashboard", "FALSE");
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
    });
  });

  describe("Clear Flag", () => {
    it("should clear individual flag from localStorage", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);

      clearFlag(FeatureFlag.ENABLE_NEW_DASHBOARD);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
    });

    it("should return to default after clearing flag", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      clearFlag(FeatureFlag.ENABLE_NEW_DASHBOARD);

      expect(getFlagSource(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe("default");
    });
  });

  describe("Clear All Flags", () => {
    it("should clear all flags from localStorage", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      setFlag(FeatureFlag.STRICT_WEBHOOK_WINDOW, true);

      clearAllFlags();

      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
      expect(isEnabled(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe(false);
    });

    it("should only clear ff_ prefixed items", () => {
      localStorageMock.setItem("ff_enableNewDashboard", "true");
      localStorageMock.setItem("other_key", "value");

      clearAllFlags();

      expect(localStorageMock.getItem("ff_enableNewDashboard")).toBe(null);
      expect(localStorageMock.getItem("other_key")).toBe("value");
    });
  });

  describe("Get All Flags", () => {
    it("should return all flags disabled by default", () => {
      const flags = getAllFlags();

      Object.values(flags).forEach((enabled) => {
        expect(enabled).toBe(false);
      });
    });

    it("should return correct state for mixed flags", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      setFlag(FeatureFlag.STRICT_WEBHOOK_WINDOW, false);

      const flags = getAllFlags();

      expect(flags[FeatureFlag.ENABLE_NEW_DASHBOARD]).toBe(true);
      expect(flags[FeatureFlag.STRICT_WEBHOOK_WINDOW]).toBe(false);
      expect(flags[FeatureFlag.ENABLE_RATE_LIMITING]).toBe(false);
    });

    it("should return all defined flags", () => {
      const flags = getAllFlags();
      const flagCount = Object.values(FeatureFlag).length;

      expect(Object.keys(flags).length).toBe(flagCount);
    });
  });

  describe("Flag Descriptions", () => {
    it("should have descriptions for all flags", () => {
      Object.values(FeatureFlag).forEach((flag) => {
        const description = getFlagDescription(flag);

        expect(description).toBeDefined();
        expect(description.length).toBeGreaterThan(0);
        expect(description).not.toBe("No description available");
      });
    });

    it("should return descriptive text for ENABLE_NEW_DASHBOARD", () => {
      const description = getFlagDescription(FeatureFlag.ENABLE_NEW_DASHBOARD);

      expect(description).toContain("dashboard");
      expect(description.length).toBeGreaterThan(20);
    });

    it("should return descriptive text for STRICT_WEBHOOK_WINDOW", () => {
      const description = getFlagDescription(FeatureFlag.STRICT_WEBHOOK_WINDOW);

      expect(description).toContain("webhook");
      expect(description.length).toBeGreaterThan(20);
    });
  });

  describe("Deterministic Behavior", () => {
    it("should return same result for same input", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);

      for (let i = 0; i < 10; i++) {
        expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
      }
    });

    it("should toggle deterministically", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);

      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, false);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);

      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
    });

    it("should maintain independent state for different flags", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      setFlag(FeatureFlag.STRICT_WEBHOOK_WINDOW, false);

      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
      expect(isEnabled(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe(false);

      // Change one flag
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, false);

      // Other flag unchanged
      expect(isEnabled(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe(false);
    });
  });

  describe("Dashboard Feature Flag", () => {
    it("should be disabled by default", () => {
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
    });

    it("should enable new dashboard when flag is true", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
    });

    it("should use old dashboard when flag is false", () => {
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, false);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);
    });
  });

  describe("Webhook Validation Feature Flag", () => {
    it("should be disabled by default", () => {
      expect(isEnabled(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe(false);
    });

    it("should enable strict validation when flag is true", () => {
      setFlag(FeatureFlag.STRICT_WEBHOOK_WINDOW, true);
      expect(isEnabled(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe(true);
    });

    it("should use relaxed validation when flag is false", () => {
      setFlag(FeatureFlag.STRICT_WEBHOOK_WINDOW, false);
      expect(isEnabled(FeatureFlag.STRICT_WEBHOOK_WINDOW)).toBe(false);
    });
  });

  describe("Integration Tests", () => {
    it("should allow toggling flags during runtime", () => {
      // Simulate testing new dashboard
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);

      // Simulate disabling after finding bug
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, false);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(false);

      // Simulate re-enabling after fix
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      expect(isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD)).toBe(true);
    });

    it("should support A/B testing scenarios", () => {
      // Group A: Old dashboard
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, false);
      const groupADashboard = isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD);

      // Group B: New dashboard
      setFlag(FeatureFlag.ENABLE_NEW_DASHBOARD, true);
      const groupBDashboard = isEnabled(FeatureFlag.ENABLE_NEW_DASHBOARD);

      expect(groupADashboard).toBe(false);
      expect(groupBDashboard).toBe(true);
    });
  });
});
