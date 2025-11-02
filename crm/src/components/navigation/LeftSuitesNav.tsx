/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { SUITES, Suite, ToolItem, filterSuitesByRoles } from './suites.config';

/**
 * Props for the LeftSuitesNav component
 */
export interface LeftSuitesNavProps {
  /** Current active route path */
  activeRoute: string;

  /** User's roles for filtering available tools */
  userRoles: string[];

  /** Callback when navigation item is clicked */
  onNavigate: (route: string) => void;

  /** Optional badge counts (key: badgeKey from tool, value: count) */
  badges?: Record<string, number>;

  /** Optional icon mapping function */
  renderIcon?: (iconName: string) => React.ReactNode;

  /** Optional CSS class name for styling */
  className?: string;

  /** LocalStorage key for persisting state (defaults to 'suites-nav-state') */
  storageKey?: string;

  /** User ID for user-specific state (defaults to 'default') */
  userId?: string;
}

/**
 * Accessible, single-suite dropdown navigation
 *
 * Features:
 * - Single suite selector dropdown
 * - Tools list updates based on selected suite
 * - Full keyboard navigation
 * - LocalStorage persistence per user
 * - Badge counts for pending items
 * - Role-based filtering
 * - Abstract styling via CSS variables
 */
export const LeftSuitesNav: React.FC<LeftSuitesNavProps> = ({
  activeRoute,
  userRoles,
  onNavigate,
  badges = {},
  renderIcon,
  className = '',
  storageKey = 'suites-nav-state',
  userId = 'default',
}) => {
  const navRef = useRef<HTMLElement>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter suites based on user roles
  const visibleSuites = useMemo(() => filterSuitesByRoles(SUITES, userRoles), [userRoles]);

  // Get initially selected suite from localStorage or default to first suite with defaultOpen
  const getInitialSelectedSuite = useCallback((): string => {
    try {
      const stored = localStorage.getItem(`${storageKey}-selected-${userId}`);
      if (stored && visibleSuites.some((s) => s.id === stored)) {
        return stored;
      }
    } catch (error) {
      console.warn('Failed to load selected suite from localStorage:', error);
    }

    // Default to first suite with defaultOpen, or first suite
    const defaultSuite = visibleSuites.find((s) => s.defaultOpen);
    return defaultSuite ? defaultSuite.id : visibleSuites[0]?.id || 'ai';
  }, [storageKey, userId, visibleSuites]);

  const [selectedSuiteId, setSelectedSuiteId] = useState<string>(getInitialSelectedSuite);

  // Persist selected suite to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(`${storageKey}-selected-${userId}`, selectedSuiteId);
    } catch (error) {
      console.warn('Failed to save selected suite to localStorage:', error);
    }
  }, [selectedSuiteId, storageKey, userId]);

  // Get current suite
  const selectedSuite = visibleSuites.find((s) => s.id === selectedSuiteId) || visibleSuites[0];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isDropdownOpen]);

  // Handle suite selection
  const handleSuiteSelect = (suiteId: string) => {
    setSelectedSuiteId(suiteId);
    setIsDropdownOpen(false);

    // Navigate to suite dashboard if available
    const suite = visibleSuites.find((s) => s.id === suiteId);
    if (suite?.dashboardRoute) {
      onNavigate(suite.dashboardRoute);
    }
  };

  // Default icon renderer
  const defaultRenderIcon = (iconName: string) => {
    const iconMap: Record<string, string> = {
      sparkle: '✨',
      bolt: '⚡',
      target: '🎯',
      'chat-bubble': '💬',
      beaker: '🧪',
      network: '🕸️',
      link: '🔗',
      branches: '🌿',
      funnel: '🔽',
      pulse: '💓',
      braces: '{ }',
      seo: '🔍',
      history: '📜',
      checklist: '✅',
      'link-2': '🔗',
      refresh: '🔄',
      gauge: '⏱️',
      chart: '📊',
      spider: '🕷️',
      search: '🔍',
      compare: '⚖️',
      'map-pin': '📍',
      speed: '⚡',
      wrench: '🔧',
      calendar: '📅',
      terminal: '💻',
      handshake: '🤝',
      inbox: '📥',
      kanban: '📋',
      receipt: '🧾',
      template: '📝',
      user: '👤',
      settings: '⚙️',
      'check-circle': '✅',
      plug: '🔌',
      clock: '⏰',
      'heart-pulse': '💓',
      shield: '🛡️',
      users: '👥',
      database: '🗄️',
      'settings-gear': '⚙️',
    };

    return <span className="suite-nav-icon">{iconMap[iconName] || '•'}</span>;
  };

  const iconRenderer = renderIcon || defaultRenderIcon;

  if (!selectedSuite) {
    return (
      <nav className={`suite-nav ${className}`} aria-label="Main navigation">
        <div className="suite-nav-empty">
          <p>No suites available</p>
        </div>
      </nav>
    );
  }

  return (
    <nav ref={navRef} className={`suite-nav ${className}`} aria-label="Main navigation">
      {/* Suite Selector Dropdown */}
      <div className="suite-nav-dropdown-container" ref={dropdownRef}>
        <button
          className="suite-nav-dropdown-trigger"
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          aria-expanded={isDropdownOpen}
          aria-haspopup="listbox"
          aria-label="Select suite"
        >
          <span className="suite-nav-dropdown-icon">{iconRenderer(selectedSuite.icon || '')}</span>
          <span className="suite-nav-dropdown-label">{selectedSuite.label}</span>
          <span className={`suite-nav-dropdown-arrow ${isDropdownOpen ? 'suite-nav-dropdown-arrow-open' : ''}`}>
            ▼
          </span>
        </button>

        {isDropdownOpen && (
          <div className="suite-nav-dropdown-menu" role="listbox">
            {visibleSuites.map((suite) => (
              <button
                key={suite.id}
                className={`suite-nav-dropdown-option ${suite.id === selectedSuiteId ? 'suite-nav-dropdown-option-selected' : ''}`}
                role="option"
                aria-selected={suite.id === selectedSuiteId}
                onClick={() => handleSuiteSelect(suite.id)}
              >
                <span className="suite-nav-dropdown-option-icon">{iconRenderer(suite.icon || '')}</span>
                <span className="suite-nav-dropdown-option-label">{suite.label}</span>
                {suite.id === selectedSuiteId && (
                  <span className="suite-nav-dropdown-option-check">✓</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Tools List */}
      <ul className="suite-nav-tools-list" role="list">
        {selectedSuite.items.map((tool) => {
          const isActive = activeRoute === tool.route;
          const badgeCount = tool.badgeKey ? badges[tool.badgeKey] || 0 : 0;

          return (
            <li key={tool.id} className="suite-nav-tool-item" role="listitem">
              <button
                className={`suite-nav-tool ${isActive ? 'suite-nav-tool-active' : ''}`}
                onClick={() => onNavigate(tool.route)}
                aria-current={isActive ? 'page' : undefined}
                title={tool.description}
              >
                <span className="suite-nav-tool-icon">{iconRenderer(tool.icon || '')}</span>
                <span className="suite-nav-tool-label">{tool.label}</span>
                {badgeCount > 0 && (
                  <span className="suite-nav-badge" aria-label={`${badgeCount} pending`}>
                    {badgeCount}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default LeftSuitesNav;
