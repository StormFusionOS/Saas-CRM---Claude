/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Navigation Suites Configuration
 *
 * This config drives the left sidebar navigation with collapsible suites.
 * Each suite contains tools/pages organized by functional area.
 */

export type UserRole = 'ADMIN' | 'SALES' | 'OPERATIONS' | 'MARKETING' | 'DEVELOPER';

export type ToolItem = {
  id: string;
  label: string;
  route: string;
  icon?: string;
  roles?: string[];
  description?: string;
  badgeKey?: string; // key in badges map
};

export type Suite = {
  id: string;
  label: string;
  icon?: string;
  defaultOpen?: boolean;
  dashboardRoute?: string; // Route to suite dashboard
  items: ToolItem[];
};

export const SUITES: Suite[] = [
  {
    id: 'ai',
    label: 'AI',
    icon: 'sparkle',
    defaultOpen: false,
    dashboardRoute: '/ai/dashboard',
    items: [
      {
        id: 'ai-dashboard',
        label: 'Dashboard',
        route: '/ai/dashboard',
        icon: 'gauge',
        description: 'AI suite overview',
      },
      {
        id: 'prompt-runner',
        label: 'Prompt Runner',
        route: '/ai/prompt-runner',
        icon: 'bolt',
        badgeKey: 'reviewQueue',
      },
      {
        id: 'snippet-optimizer',
        label: 'Featured Snippet Optimizer',
        route: '/ai/snippet-optimizer',
        icon: 'target',
      },
      {
        id: 'faq-paa',
        label: 'FAQ & PAA Generator',
        route: '/ai/faq-paa',
        icon: 'chat-bubble',
      },
      {
        id: 'meta-ctr',
        label: 'Meta Rewrite & CTR Tests',
        route: '/ai/meta-ctr',
        icon: 'beaker',
      },
      {
        id: 'clusters',
        label: 'Content Cluster Planner',
        route: '/ai/clusters',
        icon: 'network',
      },
      {
        id: 'internal-linking',
        label: 'Internal Linking Assistant',
        route: '/ai/internal-linking',
        icon: 'link',
      },
      {
        id: 'backlink-gap',
        label: 'Backlink Gap Finder',
        route: '/ai/backlink-gap',
        icon: 'branches',
      },
      {
        id: 'keywords',
        label: 'Keyword Funnel & Prioritize',
        route: '/ai/keywords',
        icon: 'funnel',
      },
      {
        id: 'anomalies',
        label: 'Rank/Traffic Anomaly Explainer',
        route: '/ai/anomalies',
        icon: 'pulse',
        badgeKey: 'anomalyCount',
      },
      {
        id: 'schema-gen',
        label: 'Schema (JSON‑LD) Generator',
        route: '/ai/schema-generator',
        icon: 'braces',
      },
    ],
  },
  {
    id: 'seo',
    label: 'SEO',
    icon: 'seo',
    dashboardRoute: '/seo/dashboard',
    items: [
      {
        id: 'seo-dashboard',
        label: 'Dashboard',
        route: '/seo/dashboard',
        icon: 'gauge',
        description: 'SEO suite overview',
      },
      {
        id: 'seo-tools',
        label: 'SEO Tools',
        route: '/seo',
        icon: 'seo',
        description: 'Search engine optimization tools',
      },
      {
        id: 'change-log',
        label: 'Change Log & Approvals',
        route: '/seo/change-log',
        icon: 'history',
        badgeKey: 'pendingChanges',
      },
      {
        id: 'schema-workflow',
        label: 'Schema Workflow & Validator',
        route: '/seo/schema',
        icon: 'checklist',
      },
      {
        id: 'linking',
        label: 'Internal Linking Manager',
        route: '/seo/linking',
        icon: 'link-2',
      },
      {
        id: 'content-refresh',
        label: 'Content Refresh & Snippets',
        route: '/seo/content-refresh',
        icon: 'refresh',
      },
      {
        id: 'seo-reports',
        label: 'SEO Reports',
        route: '/seo/reports',
        icon: 'chart',
      },
    ],
  },
  {
    id: 'scrape',
    label: 'Scrape',
    icon: 'spider',
    dashboardRoute: '/scrape/dashboard',
    items: [
      {
        id: 'scrape-dashboard',
        label: 'Scrape Dashboard',
        route: '/scrape/dashboard',
        icon: 'gauge',
        description: 'Scrape suite overview',
      },
      {
        id: 'competitor-audit',
        label: 'Competitor Site Audit',
        route: '/scrape/competitor-audit',
        icon: 'binoculars',
        badgeKey: 'auditIssues',
      },
      {
        id: 'serp-scraper',
        label: 'SERP Position Scraper',
        route: '/scrape/serp',
        icon: 'search',
      },
      {
        id: 'backlink-finder',
        label: 'Backlink Discovery',
        route: '/scrape/backlinks',
        icon: 'link-chain',
        badgeKey: 'newBacklinks',
      },
      {
        id: 'content-extraction',
        label: 'Content Extraction',
        route: '/scrape/content',
        icon: 'document',
      },
      {
        id: 'price-monitor',
        label: 'Price & Change Monitor',
        route: '/scrape/monitor',
        icon: 'eye',
      },
      {
        id: 'scrape-scheduler',
        label: 'Scrape Scheduler',
        route: '/scrape/scheduler',
        icon: 'clock',
      },
      {
        id: 'scrape-api',
        label: 'API & Exports',
        route: '/scrape/api',
        icon: 'code',
      },
    ],
  },
  {
    id: 'sales',
    label: 'Sales',
    icon: 'handshake',
    defaultOpen: true,
    dashboardRoute: '/sales/dashboard',
    items: [
      {
        id: 'sales-dashboard',
        label: 'Sales Dashboard',
        route: '/sales/dashboard',
        icon: 'gauge',
        description: 'Sales suite overview',
      },
      {
        id: 'general-dashboard',
        label: 'Overview Dashboard',
        route: '/dashboard',
        icon: 'chart',
        description: 'General business overview',
      },
      {
        id: 'inbox',
        label: 'Unified Inbox',
        route: '/inbox',
        icon: 'inbox',
        badgeKey: 'unread',
      },
      {
        id: 'leads',
        label: 'Leads & Pipeline',
        route: '/leads',
        icon: 'kanban',
      },
      {
        id: 'estimator',
        label: 'Estimator',
        route: '/estimator',
        icon: 'receipt',
      },
      {
        id: 'services',
        label: 'Service Catalog',
        route: '/sales/services',
        icon: 'package',
        description: 'Manage service offerings and pricing',
      },
      {
        id: 'quotes',
        label: 'Quotes & Invoices',
        route: '/quotes',
        icon: 'receipt',
      },
      {
        id: 'calendar',
        label: 'Calendar & Scheduling',
        route: '/calendar',
        icon: 'calendar',
      },
      {
        id: 'client-portal',
        label: 'Client Portal',
        route: '/client-portal',
        icon: 'user',
      },
      {
        id: 'sales-reports',
        label: 'Reports',
        route: '/reports',
        icon: 'chart',
      },
    ],
  },
  {
    id: 'admin',
    label: 'Admin',
    icon: 'settings',
    dashboardRoute: '/admin/dashboard',
    items: [
      {
        id: 'admin-dashboard',
        label: 'Dashboard',
        route: '/admin/dashboard',
        icon: 'gauge',
        description: 'Admin suite overview',
      },
      {
        id: 'system-health',
        label: 'System Health & Alerts',
        route: '/health',
        icon: 'heart-pulse',
        badgeKey: 'healthAlerts',
      },
      {
        id: 'settings',
        label: 'Settings',
        route: '/settings',
        icon: 'settings-gear',
      },
      {
        id: 'user-management',
        label: 'User Management',
        route: '/admin/users',
        icon: 'users',
        description: 'Manage users and permissions',
      },
      {
        id: 'audit-logs',
        label: 'Audit Logs',
        route: '/admin/audit',
        icon: 'history',
        description: 'System activity audit trail',
      },
      {
        id: 'integrations',
        label: 'Integrations',
        route: '/admin/integrations',
        icon: 'puzzle',
        description: 'Third-party integrations',
      },
      {
        id: 'billing',
        label: 'Billing & Subscriptions',
        route: '/admin/billing',
        icon: 'credit-card',
        description: 'Manage billing and plans',
      },
      {
        id: 'pwa',
        label: 'Tech PWA',
        route: '/pwa',
        icon: 'plug',
        description: 'Technician mobile app',
      },
      {
        id: 'api-keys',
        label: 'API Keys & Webhooks',
        route: '/admin/api',
        icon: 'key',
        description: 'API access management',
      },
      {
        id: 'visual-check',
        label: 'Visual Check',
        route: '/visual-check',
        icon: 'check-circle',
        description: 'UI component preview',
      },
    ],
  },
];

/**
 * Helper function to filter suites and tools based on user roles
 */
export function filterSuitesByRoles(suites: Suite[], userRoles: string[]): Suite[] {
  return suites
    .map((suite) => ({
      ...suite,
      items: suite.items.filter((item) => {
        // If item has required roles, check if user has at least one
        if (item.roles && item.roles.length > 0) {
          return item.roles.some((role) => userRoles.includes(role));
        }
        return true;
      }),
    }))
    .filter((suite) => suite.items.length > 0); // Remove empty suites
}

/**
 * Get all navigable paths from suites
 */
export function getAllRoutes(suites: Suite[]): string[] {
  return suites.flatMap((suite) => suite.items.map((item) => item.route));
}

/**
 * Find tool by route
 */
export function findToolByRoute(suites: Suite[], route: string): ToolItem | undefined {
  for (const suite of suites) {
    const tool = suite.items.find((t) => t.route === route);
    if (tool) return tool;
  }
  return undefined;
}
