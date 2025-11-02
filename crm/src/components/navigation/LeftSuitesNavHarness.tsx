/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import { LeftSuitesNav } from './LeftSuitesNav';
import './LeftSuitesNav.css';

/**
 * Test Harness for LeftSuitesNav Component
 *
 * This component demonstrates all features of the LeftSuitesNav:
 * - Role-based filtering
 * - Badge counts
 * - Navigation
 * - Theme switching
 * - State management
 */
export const LeftSuitesNavHarness: React.FC = () => {
  const [activeRoute, setActiveRoute] = useState('/ai/prompt-runner');
  const [userRoles, setUserRoles] = useState<string[]>(['ADMIN', 'SALES']);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Simulated badge counts
  const [badges] = useState<Record<string, number>>({
    reviewQueue: 12,
    anomalyCount: 3,
    pendingChanges: 5,
    auditIssues: 8,
    unread: 24,
    healthAlerts: 2,
  });

  const handleNavigate = (route: string) => {
    console.log('Navigating to:', route);
    setActiveRoute(route);
  };

  const toggleRole = (role: string) => {
    setUserRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
    );
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div
      className="harness-container"
      data-theme={theme}
      style={{
        display: 'flex',
        height: '100vh',
        backgroundColor: theme === 'dark' ? '#0a0e14' : '#f3f4f6',
      }}
    >
      {/* Left Sidebar - Navigation */}
      <div
        style={{
          width: '280px',
          height: '100%',
          borderRight: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
          overflow: 'hidden',
        }}
      >
        <LeftSuitesNav
          activeRoute={activeRoute}
          userRoles={userRoles}
          onNavigate={handleNavigate}
          badges={badges}
          userId="test-user"
        />
      </div>

      {/* Main Content - Test Controls */}
      <div
        style={{
          flex: 1,
          padding: '2rem',
          overflowY: 'auto',
          color: theme === 'dark' ? '#e6edf3' : '#1f2937',
        }}
      >
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          LeftSuitesNav Test Harness
        </h1>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Current State */}
          <section>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>
              Current State
            </h2>
            <div
              style={{
                padding: '1rem',
                backgroundColor: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                borderRadius: '0.5rem',
                border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
              }}
            >
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Active Route:</strong> <code>{activeRoute}</code>
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>User Roles:</strong> <code>{userRoles.join(', ') || 'None'}</code>
              </div>
              <div>
                <strong>Theme:</strong> <code>{theme}</code>
              </div>
            </div>
          </section>

          {/* Theme Toggle */}
          <section>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>
              Theme
            </h2>
            <button
              onClick={toggleTheme}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: theme === 'dark' ? '#00d9ff' : '#007bff',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontWeight: '500',
              }}
            >
              Toggle Theme (Current: {theme})
            </button>
          </section>

          {/* Role Management */}
          <section>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>
              User Roles (affects visibility)
            </h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {['ADMIN', 'SALES', 'OPERATIONS', 'MARKETING', 'DEVELOPER'].map((role) => (
                <button
                  key={role}
                  onClick={() => toggleRole(role)}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: userRoles.includes(role)
                      ? theme === 'dark'
                        ? '#10b981'
                        : '#059669'
                      : theme === 'dark'
                      ? 'rgba(255,255,255,0.1)'
                      : 'rgba(0,0,0,0.1)',
                    color: userRoles.includes(role)
                      ? '#ffffff'
                      : theme === 'dark'
                      ? '#7d8590'
                      : '#6b7280',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontWeight: '500',
                  }}
                >
                  {role}
                </button>
              ))}
            </div>
          </section>

          {/* Badge Counts */}
          <section>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>
              Badge Counts
            </h2>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: '0.75rem',
              }}
            >
              {Object.entries(badges).map(([key, count]) => (
                <div
                  key={key}
                  style={{
                    padding: '0.75rem',
                    backgroundColor: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                    borderRadius: '0.375rem',
                    border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: theme === 'dark' ? '#7d8590' : '#6b7280' }}>
                    {key}
                  </div>
                  <div
                    style={{
                      fontSize: '1.5rem',
                      fontWeight: 'bold',
                      color: theme === 'dark' ? '#00d9ff' : '#007bff',
                    }}
                  >
                    {count}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Features Checklist */}
          <section>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>
              Features Implemented ✅
            </h2>
            <ul style={{ lineHeight: '1.75' }}>
              <li>✅ ARIA tree pattern (role="tree", role="treeitem")</li>
              <li>✅ Full keyboard navigation (↑ ↓ → ← Home End Enter Space)</li>
              <li>✅ LocalStorage persistence per user</li>
              <li>✅ Badge counts with visibility control</li>
              <li>✅ Role-based filtering (try toggling roles above)</li>
              <li>✅ Fuzzy search with auto-expand and highlighting</li>
              <li>✅ Abstract CSS variables for theming</li>
              <li>✅ Dark/Light theme support</li>
              <li>✅ Active route highlighting (aria-current="page")</li>
              <li>✅ Collapsible suites with state persistence</li>
            </ul>
          </section>

          {/* Usage Instructions */}
          <section>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>
              Keyboard Navigation
            </h2>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: '0.875rem',
              }}
            >
              <thead>
                <tr
                  style={{
                    backgroundColor: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                  }}
                >
                  <th
                    style={{
                      padding: '0.75rem',
                      textAlign: 'left',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Key
                  </th>
                  <th
                    style={{
                      padding: '0.75rem',
                      textAlign: 'left',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    <code>↑</code>
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Move focus to previous item
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    <code>↓</code>
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Move focus to next item
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    <code>→</code>
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Expand suite (if collapsed)
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    <code>←</code>
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Collapse suite (if expanded) or move to parent suite
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    <code>Home</code>
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Move to first item
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    <code>End</code>
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    }}
                  >
                    Move to last item
                  </td>
                </tr>
                <tr>
                  <td style={{ padding: '0.75rem' }}>
                    <code>Enter</code> or <code>Space</code>
                  </td>
                  <td style={{ padding: '0.75rem' }}>Activate item (navigate to tool or toggle suite)</td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
      </div>
    </div>
  );
};

export default LeftSuitesNavHarness;
