/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Navigation Components - Public API
 */

// Main component
export { LeftSuitesNav, type LeftSuitesNavProps } from './LeftSuitesNav';

// Configuration and types
export {
  SUITES,
  type Suite,
  type ToolItem,
  type UserRole,
  filterSuitesByRoles,
  getAllRoutes,
  findToolByRoute,
} from './suites.config';

// Test harness (for development/testing)
export { LeftSuitesNavHarness } from './LeftSuitesNavHarness';
